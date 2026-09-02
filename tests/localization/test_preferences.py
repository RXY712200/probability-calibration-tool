import gc

import pytest
from PySide6.QtCore import QSettings

from probability_calibration_tool.localization import (
    PREFERENCE_KEY,
    FallbackReason,
    Language,
    initialize_localization,
    read_preference,
)
from probability_calibration_tool.localization import (
    PreferenceSaveFailure as Failure,
)
from probability_calibration_tool.localization import (
    PreferenceState as State,
)

from .helpers import App, SettingsPlan, Translator, dummy_pack, write_preference


@pytest.mark.parametrize(
    "raw,state,preferred",
    [
        ("en", State.SAVED_VALID, Language.EN),
        ("zh_CN", State.SAVED_VALID, Language.ZH_CN),
        ("banana", State.SAVED_INVALID, Language.EN),
        ("zh", State.SAVED_INVALID, Language.EN),
        ("zh_TW", State.SAVED_INVALID, Language.EN),
        ("zh-CN", State.SAVED_INVALID, Language.EN),
        (" en ", State.SAVED_INVALID, Language.EN),
        ("", State.SAVED_INVALID, Language.EN),
        (42, State.SAVED_INVALID, Language.EN),
        (["en", "zh_CN"], State.SAVED_INVALID, Language.EN),
    ],
)
def test_real_read_exact_values_never_rewrites(tmp_path, raw, state, preferred):
    write_preference(tmp_path, raw)
    path = tmp_path / "settings.ini"
    before = path.read_bytes()
    result = read_preference(path)
    assert (result.state, result.preferred_language) == (state, preferred)
    assert result.key_existed and result.raw_value == raw
    gc.collect()
    assert path.read_bytes() == before


def test_real_missing_file_and_missing_key_are_readonly(tmp_path):
    root = tmp_path / "never-created"
    assert read_preference(root / "settings.ini").state == State.DEFAULT
    gc.collect()
    assert not root.exists()
    path = tmp_path / "settings.ini"
    path.write_text("[unrelated]\nvalue=keep\n", encoding="utf-8")
    before = path.read_bytes()
    result = read_preference(path)
    assert result.state == State.DEFAULT and not result.key_existed
    assert result.preferred_language == Language.EN
    assert path.read_bytes() == before


def test_real_malformed_ini_reports_format_error_without_repair(tmp_path):
    path = tmp_path / "settings.ini"
    path.write_bytes(b"[malformed\nvalue=test\n")
    before = path.read_bytes()
    result = read_preference(path)
    assert result.status == QSettings.Status.FormatError
    assert result.state == State.READ_ERROR
    assert result.preferred_language == Language.EN
    gc.collect()
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "config",
    [
        {"status": QSettings.Status.AccessError},
        {"status": QSettings.Status.FormatError},
        {"read_error": OSError("injected read failure")},
    ],
)
def test_read_failure_fresh_exact_atomic_settings_never_write(tmp_path, config):
    factory = SettingsPlan(config)
    result = read_preference(tmp_path / "settings.ini", settings_factory=factory)
    assert result.state == State.READ_ERROR and result.preferred_language == Language.EN
    assert all(call not in ("remove", "sync", "clear") for call in factory.records[0]["calls"])
    assert not any(isinstance(call, tuple) for call in factory.records[0]["calls"])
    assert not factory.plans


def test_default_en_confirm_persists_but_saved_same_is_noop(tmp_path):
    context = initialize_localization(App(), tmp_path)
    assert context.preference_state == State.DEFAULT
    assert not context.settings_path.exists()
    result = context.save_preference(Language.EN)
    assert result.success and not result.restart_required
    assert context.preference_state == State.SAVED_VALID
    assert read_preference(context.settings_path).raw_value == "en"
    before = context.settings_path.read_bytes()
    factory = SettingsPlan()  # No QSettings operation is permitted for a saved no-op.
    context._settings_factory = factory
    assert context.save_preference(Language.EN).success
    assert not factory.records
    assert context.settings_path.read_bytes() == before


@pytest.mark.parametrize("initial", ["banana", "zh_CN"])
def test_explicit_en_repairs_preference_preserves_keys_and_startup_notice(tmp_path, initial):
    write_preference(tmp_path, initial)
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    settings.setValue("other/number", 17)
    settings.setValue("other/string", "preserved")
    settings.sync()
    del settings
    context = initialize_localization(App(), tmp_path)
    notice = context.startup_notice_kind
    assert notice != FallbackReason.NONE
    result = context.save_preference(Language.EN)
    assert result.success and not result.restart_required
    assert context.preferred_language == context.effective_language == Language.EN
    assert context.fallback_reason == FallbackReason.NONE
    assert context.startup_notice_kind == notice
    assert read_preference(context.settings_path).raw_value == "en"
    checked = QSettings(str(context.settings_path), QSettings.Format.IniFormat)
    assert checked.value("other/number", type=int) == 17
    assert checked.value("other/string") == "preserved"


def test_en_to_zh_real_save_requires_restart_and_does_not_install(tmp_path):
    dummy_pack(tmp_path)
    app = App()
    context = initialize_localization(app, tmp_path, translator_factory=Translator)
    assert context.save_preference(Language.ZH_CN).success
    assert context.preferred_language == Language.ZH_CN
    assert context.effective_language == Language.EN and context.restart_required
    assert read_preference(context.settings_path).raw_value == "zh_CN"
    assert app.events == []


def test_preferred_changes_only_after_fresh_readback_exact_match(tmp_path):
    dummy_pack(tmp_path)
    factory = SettingsPlan({}, {}, {}, {"values": {PREFERENCE_KEY: "zh_CN"}})
    context = initialize_localization(
        App(), tmp_path, settings_factory=factory, translator_factory=Translator
    )
    seen = []

    def during_readback():
        seen.append(context.preferred_language)
        assert context.preference_state == State.DEFAULT

    factory.hook = during_readback
    assert context.save_preference(Language.ZH_CN).success
    assert seen == [Language.EN]
    assert context.preferred_language == Language.ZH_CN
    assert context.effective_language == Language.EN
    assert len(factory.records) == 4 and not factory.plans
    assert factory.records[2]["calls"][:5] == [
        "fallbacks_off",
        "atomic_on",
        ("set", "zh_CN"),
        "sync",
        "status",
    ]


@pytest.mark.parametrize("old", [None, "en", "banana"])
@pytest.mark.parametrize(
    "writer_config,check_config,failure",
    [
        ({"status": QSettings.Status.AccessError}, None, Failure.SETTINGS_ACCESS_ERROR),
        ({"status": QSettings.Status.FormatError}, None, Failure.SETTINGS_FORMAT_ERROR),
        ({"sync_error": OSError("sync failed")}, None, Failure.SETTINGS_ACCESS_ERROR),
        ({"set_error": OSError("set failed")}, None, Failure.SETTINGS_ACCESS_ERROR),
        ({}, {"values": {PREFERENCE_KEY: "en"}}, Failure.VERIFY_MISMATCH),
        ({}, {}, Failure.VERIFY_MISMATCH),
        ({}, {"status": QSettings.Status.AccessError}, Failure.SETTINGS_ACCESS_ERROR),
        ({}, {"status": QSettings.Status.FormatError}, Failure.SETTINGS_FORMAT_ERROR),
    ],
)
def test_failed_save_restores_raw_or_removes_before_writer_teardown(
    tmp_path, old, writer_config, check_config, failure
):
    dummy_pack(tmp_path)
    values = {"unrelated/key": "keep"}
    if old is not None:
        values[PREFERENCE_KEY] = old
    plans = [{"values": values}, {"values": values}, {**writer_config, "values": values}]
    if check_config is not None:
        plans.append(check_config)
    factory = SettingsPlan(*plans)
    app = App()
    context = initialize_localization(
        app, tmp_path, settings_factory=factory, translator_factory=Translator
    )
    original = (context.preferred_language, context.preference_state, context.fallback_reason)
    result = context.save_preference(Language.ZH_CN)
    assert not result.success and result.failure == failure
    assert (
        context.preferred_language,
        context.preference_state,
        context.fallback_reason,
    ) == original
    assert context.effective_language == Language.EN and not context.restart_required
    assert app.events == []
    gc.collect()
    writer = factory.records[2]
    assert writer["teardown_values"] == values
    restore = "remove" if old is None else ("set", old)
    assert writer["calls"][-2:] == [restore, "teardown"]
    assert not factory.plans


@pytest.mark.parametrize(
    "status,failure",
    [
        (QSettings.Status.AccessError, Failure.SETTINGS_ACCESS_ERROR),
        (QSettings.Status.FormatError, Failure.SETTINGS_FORMAT_ERROR),
    ],
)
def test_failed_capture_of_old_value_cannot_write(tmp_path, status, failure):
    factory = SettingsPlan({}, {"status": status})
    context = initialize_localization(App(), tmp_path, settings_factory=factory)
    assert context.save_preference(Language.EN).failure == failure
    assert context.preference_state == State.DEFAULT
    assert len(factory.records) == 2 and not factory.plans


@pytest.mark.parametrize("unsupported", ["en", "zh_CN", "ja_JP", None, 7])
def test_unsupported_internal_language_is_programmer_error(tmp_path, unsupported):
    context = initialize_localization(App(), tmp_path)
    with pytest.raises(TypeError, match="Language enum"):
        context.save_preference(unsupported)
    assert not context.settings_path.exists()


def test_unexpected_save_bug_not_silently_converted_to_settings_error(tmp_path):
    factory = SettingsPlan({}, {}, {"sync_error": RuntimeError("programming bug")})
    context = initialize_localization(App(), tmp_path, settings_factory=factory)
    with pytest.raises(RuntimeError, match="programming bug"):
        context.save_preference(Language.EN)
    assert context.preference_state == State.DEFAULT
    gc.collect()
    assert factory.records[2]["teardown_values"] == {}
