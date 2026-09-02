import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from probability_calibration_tool.application.reliability_views import ReliabilityResult
from probability_calibration_tool.application.reliability_views import StartupDisposition as D
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.bootstrap import main
from probability_calibration_tool.desktop_host import DesktopHost
from probability_calibration_tool.infrastructure.error_reporting import ErrorPresentation
from probability_calibration_tool.infrastructure.paths import AppPaths
from probability_calibration_tool.localization import (
    FallbackReason,
    PreferenceSaveFailure,
    PreferenceState,
    initialize_localization,
)
from probability_calibration_tool.localization import (
    Language as L,
)
from probability_calibration_tool.ui.language_dialog import (
    PROVENANCE_SOURCES,
    QT_DEGRADED_SOURCE,
    SAVE_FAILURE_SOURCES,
    SAVE_SUCCESS_SOURCES,
    STARTUP_SOURCES,
    LanguageDialog,
    startup_notice,
)

from . import test_presentation
from .helpers import App, SettingsPlan, Translator, dummy_pack, write_preference

marker = test_presentation.marker


def test_frozen_step46_sources_and_language_provenance_exact():
    assert STARTUP_SOURCES[FallbackReason.PREFERRED_PACK_MISSING] == (
        'The preferred interface language is "简体中文", but its language pack was not found. '
        "English will be used for this launch. The preferred language setting will not be changed."
    )
    assert STARTUP_SOURCES[FallbackReason.PREFERRED_PACK_INVALID] == (
        'The "简体中文" language pack could not be loaded. English will be used for this launch. '
        "The preferred language setting will not be changed."
    )
    assert STARTUP_SOURCES[FallbackReason.INVALID_PREFERENCE] == (
        "The saved interface language preference is invalid. English will be used for this launch. "
        "The settings file will not be changed automatically."
    )
    assert STARTUP_SOURCES[FallbackReason.SETTINGS_READ_ERROR] == (
        "The interface language preference could not be read. English will be used for this launch. "
        "The existing settings file will not be modified."
    )
    assert (
        STARTUP_SOURCES[FallbackReason.APP_INSTALL_FAILED]
        == STARTUP_SOURCES[FallbackReason.PREFERRED_PACK_INVALID]
    )
    assert (
        STARTUP_SOURCES[FallbackReason.INITIALIZATION_ERROR]
        == STARTUP_SOURCES[FallbackReason.SETTINGS_READ_ERROR]
    )
    assert QT_DEGRADED_SOURCE == (
        "Simplified Chinese is active, but Qt's standard translations could not be loaded. "
        "Some Qt-owned text may remain in English."
    )
    assert SAVE_FAILURE_SOURCES[PreferenceSaveFailure.PACK_INVALID] == (
        'The "简体中文" language pack could not be verified, so the new interface language setting '
        "was not saved. Make sure the language pack still exists and can be loaded."
    )
    generic_failure = (
        "The interface language preference could not be saved. The existing preference remains "
        "unchanged."
    )
    assert {
        SAVE_FAILURE_SOURCES[code]
        for code in (
            PreferenceSaveFailure.SETTINGS_ACCESS_ERROR,
            PreferenceSaveFailure.SETTINGS_FORMAT_ERROR,
            PreferenceSaveFailure.VERIFY_MISMATCH,
        )
    } == {generic_failure}
    assert SAVE_SUCCESS_SOURCES == {
        L.EN: "The interface language preference was saved. English will take effect the next time the application starts.",
        L.ZH_CN: "The interface language preference was saved. The new interface language will take effect the next time the application starts.",
    }
    assert PROVENANCE_SOURCES == {L.EN: "Built-in", L.ZH_CN: "External language pack"}


def test_provenance_is_localized_but_language_self_names_are_stable(tmp_path, marker):
    marker()
    context = initialize_localization(App(), tmp_path)
    dialog = LanguageDialog(context)
    assert dialog.choices[L.EN].text() == "English"
    assert dialog.choices[L.ZH_CN].text() == "简体中文"
    assert dialog.provenance[L.EN].text() == "⟦Localization⟧ Built-in"
    assert dialog.provenance[L.ZH_CN].text() == "⟦Localization⟧ External language pack"


@pytest.mark.parametrize(
    "raw,pack,selected",
    [
        ("en", False, L.EN),
        ("en", True, L.EN),
        ("zh_CN", True, L.ZH_CN),
        ("zh_CN", False, None),
        ("banana", False, None),
        ("read_error", False, None),
    ],
)
def test_chooser_initial_state_does_not_overwrite_unavailable_preference(
    tmp_path, raw, pack, selected
):
    from PySide6.QtCore import QSettings

    if pack:
        dummy_pack(tmp_path)
    write_preference(tmp_path, raw)
    kwargs = (
        {"settings_factory": SettingsPlan({"status": QSettings.Status.AccessError})}
        if raw == "read_error"
        else {}
    )
    context = initialize_localization(App(), tmp_path, translator_factory=Translator, **kwargs)
    before = context.settings_path.read_bytes()
    dialog = LanguageDialog(context)
    assert dialog._selected() == selected
    assert not dialog.confirm.isEnabled()
    assert dialog.choices[L.ZH_CN].isEnabled() is pack
    assert dialog.available_rows[L.ZH_CN].isHidden() is (not pack)
    assert not dialog.available_rows[L.EN].isHidden()
    assert dialog.choices[L.EN].text() == "English" and dialog.choices[L.ZH_CN].text() == "简体中文"
    assert dialog.provenance[L.EN].text() == "Built-in"
    assert dialog.provenance[L.ZH_CN].text() == "External language pack"
    assert "banana" not in dialog.preferred.text() and "read_error" not in dialog.preferred.text()
    dialog.reject()
    assert context.settings_path.read_bytes() == before


@pytest.mark.parametrize("close", ["cancel", "escape", "x", "reject"])
def test_cancel_escape_close_never_save_or_preflight(tmp_path, monkeypatch, close):
    from probability_calibration_tool import localization as loc

    context = initialize_localization(App(), tmp_path)
    calls = []
    monkeypatch.setattr(context, "save_preference", lambda *args: calls.append("save"))
    monkeypatch.setattr(
        loc, "preflight_app_pack", lambda *args, **kwargs: calls.append("preflight")
    )
    dialog = LanguageDialog(context)
    dialog.show()
    if close == "cancel":
        QTest.mouseClick(dialog.cancel, Qt.MouseButton.LeftButton)
    elif close == "escape":
        QTest.keyClick(dialog, Qt.Key.Key_Escape)
    elif close == "x":
        dialog.close()
    else:
        dialog.reject()
    assert not calls
    assert not context.settings_path.exists()
    assert context.preference_state == PreferenceState.DEFAULT


def test_confirm_once_restart_only_and_current_language_notice(tmp_path, monkeypatch, marker):
    marker()
    dummy_pack(tmp_path)
    context = initialize_localization(App(), tmp_path, translator_factory=Translator)
    original = context.save_preference
    calls, notices = [], []

    def save(language):
        calls.append(language)
        return original(language)

    monkeypatch.setattr(context, "save_preference", save)
    dialog = LanguageDialog(context)
    dialog.saved.connect(notices.append)
    dialog.show()
    dialog.choices[L.ZH_CN].click()
    current = dialog.current.text()
    QTest.mouseClick(dialog.confirm, Qt.MouseButton.LeftButton)
    dialog._confirm()  # A queued duplicate must not issue another save.
    assert calls == [L.ZH_CN]
    assert context.preferred_language == L.ZH_CN and context.effective_language == L.EN
    assert context.app_translator is context.qt_translator is None
    assert notices == [
        "⟦Localization⟧ The interface language preference was saved. The new interface language will take effect the next time the application starts."
    ]
    assert dialog.current.text() == current and "English" in current


def test_confirm_pack_disappearance_demotes_keeps_dialog_open_and_no_repromotion(tmp_path):
    path = dummy_pack(tmp_path)
    write_preference(tmp_path, "en")
    context = initialize_localization(App(), tmp_path, translator_factory=Translator)
    before = context.settings_path.read_bytes()
    dialog = LanguageDialog(context)
    dialog.show()
    dialog.choices[L.ZH_CN].setChecked(True)
    path.unlink()
    dialog._confirm()
    assert dialog.isVisible() and dialog.message.text()
    assert (
        dialog.message.text()
        == 'The "简体中文" language pack could not be verified, so the new interface language setting was not saved. Make sure the language pack still exists and can be loaded.'
    )
    assert context.preferred_language == context.effective_language == L.EN
    assert context.available_languages == {L.EN}
    assert dialog._selected() is None and not dialog.confirm.isEnabled()
    assert dialog.available_rows[L.ZH_CN].isHidden()
    assert context.settings_path.read_bytes() == before
    dummy_pack(tmp_path)
    dialog._refresh_available()
    assert not dialog.choices[L.ZH_CN].isEnabled()
    assert dialog.available_rows[L.ZH_CN].isHidden()
    dialog.reject()


def test_invalid_preference_explicit_english_repair(tmp_path):
    write_preference(tmp_path, "invalid secret preference")
    context = initialize_localization(App(), tmp_path)
    dialog = LanguageDialog(context)
    notices = []
    dialog.saved.connect(notices.append)
    assert not dialog.confirm.isEnabled()
    dialog.choices[L.EN].setChecked(True)
    dialog._confirm()
    assert context.preference_state == PreferenceState.SAVED_VALID
    assert context.preferred_language == context.effective_language == L.EN
    assert notices == [SAVE_SUCCESS_SOURCES[L.EN]]


def test_default_english_explicit_save_uses_frozen_restart_notice(tmp_path):
    context = initialize_localization(App(), tmp_path)
    dialog = LanguageDialog(context)
    notices = []
    dialog.saved.connect(notices.append)
    assert dialog._selected() == L.EN and dialog.confirm.isEnabled()
    dialog._confirm()
    assert notices == [SAVE_SUCCESS_SOURCES[L.EN]]
    assert context.preferred_language == context.effective_language == L.EN


def test_dialog_healthy_saved_same_selection_has_no_confirm_and_never_calls_api(
    tmp_path, monkeypatch
):
    write_preference(tmp_path, "en")
    context = initialize_localization(App(), tmp_path)
    before = context.settings_path.read_bytes()
    no_settings_operations = SettingsPlan()
    context._settings_factory = no_settings_operations
    monkeypatch.setattr(
        context,
        "save_preference",
        lambda *args: pytest.fail("Healthy saved selection must not call save_preference"),
    )
    dialog = LanguageDialog(context)
    assert dialog._selected() == L.EN and not dialog.confirm.isEnabled()
    dialog._confirm()
    assert dialog.result() == dialog.DialogCode.Rejected
    assert not no_settings_operations.records
    assert context.settings_path.read_bytes() == before


def test_dialog_explicit_english_repairs_resolved_read_error(tmp_path):
    from PySide6.QtCore import QSettings

    from probability_calibration_tool.localization import PREFERENCE_KEY

    settings = SettingsPlan(
        {"status": QSettings.Status.AccessError}, {}, {}, {"values": {PREFERENCE_KEY: "en"}}
    )
    context = initialize_localization(App(), tmp_path, settings_factory=settings)
    dialog = LanguageDialog(context)
    assert context.preference_state == PreferenceState.READ_ERROR
    assert dialog._selected() is None
    dialog.choices[L.EN].click()
    dialog._confirm()
    assert dialog.result() == dialog.DialogCode.Accepted
    assert context.preference_state == PreferenceState.SAVED_VALID
    assert context.preferred_language == context.effective_language == L.EN
    assert sum(record["calls"].count(("set", "en")) for record in settings.records) == 1


def test_dialog_save_access_failure_preserves_preference_and_stays_open(tmp_path, marker):
    from PySide6.QtCore import QSettings

    marker()
    settings = SettingsPlan({}, {"status": QSettings.Status.AccessError})
    context = initialize_localization(App(), tmp_path, settings_factory=settings)
    dialog = LanguageDialog(context)
    dialog.show()
    dialog._confirm()
    assert dialog.isVisible()
    assert "⟦Localization⟧" in dialog.message.text()
    assert (
        dialog.message.text()
        == "⟦Localization⟧ " + SAVE_FAILURE_SOURCES[PreferenceSaveFailure.SETTINGS_ACCESS_ERROR]
    )
    assert context.preference_state == PreferenceState.DEFAULT
    assert context.preferred_language == context.effective_language == L.EN
    assert not any(
        isinstance(call, tuple) for record in settings.records for call in record["calls"]
    )
    dialog.reject()


@pytest.mark.parametrize(
    "state",
    ["missing", "invalid_pack", "invalid_preference", "read_error", "qt_degraded", "healthy"],
)
def test_startup_notice_semantic_states_and_english_missing_pack(tmp_path, monkeypatch, state):
    from PySide6.QtCore import QSettings

    from probability_calibration_tool import localization as loc

    kwargs = {}
    if state in ("missing", "invalid_pack", "qt_degraded"):
        write_preference(tmp_path, "zh_CN")
    if state == "invalid_preference":
        write_preference(tmp_path, "secret invalid preference")
    if state in ("invalid_pack", "qt_degraded"):
        dummy_pack(tmp_path)
    if state == "qt_degraded":
        kwargs["translator_factory"] = Translator
        monkeypatch.setattr(loc.QLibraryInfo, "path", lambda kind: str(tmp_path / "absent-qt"))
    if state == "read_error":
        kwargs["settings_factory"] = SettingsPlan({"status": QSettings.Status.AccessError})
    context = initialize_localization(App(), tmp_path, **kwargs)
    before = context.settings_path.read_bytes() if context.settings_path.exists() else None
    notice = startup_notice(context)
    assert (notice is None) is (state == "healthy")
    expected = {
        "missing": STARTUP_SOURCES[FallbackReason.PREFERRED_PACK_MISSING],
        "invalid_pack": STARTUP_SOURCES[FallbackReason.PREFERRED_PACK_INVALID],
        "invalid_preference": STARTUP_SOURCES[FallbackReason.INVALID_PREFERENCE],
        "read_error": STARTUP_SOURCES[FallbackReason.SETTINGS_READ_ERROR],
        "qt_degraded": QT_DEGRADED_SOURCE,
        "healthy": None,
    }
    assert notice == expected[state]
    if state == "missing":
        assert context.preferred_language == L.ZH_CN and context.effective_language == L.EN
    if state == "qt_degraded":
        assert context.effective_language == L.ZH_CN
        assert "Qt's standard" in notice
    assert "secret" not in (notice or "")
    assert (
        context.settings_path.read_bytes() if context.settings_path.exists() else None
    ) == before


def test_process_notice_once_across_host_session_rebuild_and_language_entry(
    tmp_path, localization_app
):
    paths = AppPaths.from_root(tmp_path)
    write_preference(tmp_path, "zh_CN")
    context = initialize_localization(localization_app, tmp_path)
    before = context.settings_path.read_bytes()
    with StartupService(paths).start() as runtime:
        host = DesktopHost(runtime)
        host.bind_localization(context)
        try:
            host.show_initial_state()
            assert startup_notice(context) in host.window.banner.message.text()
            assert host.window.localization is context
            assert host.window.language_button.isEnabled()
            navigation = (
                host.window.round_button.parentWidget()
                .layout()
                .itemAt(1)
                .layout()
                .itemAt(0)
                .layout()
            )
            assert navigation.itemAt(navigation.count() - 1).widget() is host.window.language_button
            assert navigation.itemAt(navigation.count() - 2).spacerItem() is not None
            session = host.session
            host.show_initial_state()
            assert host.session is not session and host.window.localization is context
            assert not host.window.banner.message.text()
        finally:
            host.dispose()
    assert context.settings_path.read_bytes() == before


def test_bootstrap_same_context_real_language_entry_saves_without_rebuilding(
    tmp_path, localization_app
):
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    dummy_pack(tmp_path)
    context = initialize_localization(App(), tmp_path, translator_factory=Translator)
    observed = []

    def event_loop(app, host):
        assert app is localization_app
        assert host.localization is host.window.localization is context
        session, window = host.session, host.window
        caption = window.round.pre.primary.text()

        def confirm():
            dialog = QApplication.activeModalWidget()
            assert isinstance(dialog, LanguageDialog) and dialog.context is context
            dialog.choices[L.ZH_CN].click()
            dialog.confirm.click()

        QTimer.singleShot(0, confirm)
        window.language_button.click()
        assert host.window is window and host.session is session
        assert window.round.pre.primary.text() == caption
        assert context.preferred_language == L.ZH_CN and context.effective_language == L.EN
        assert context.app_translator is None
        assert window.banner.property("severity") == "information"
        assert SAVE_SUCCESS_SOURCES[L.ZH_CN] in window.banner.message.text()
        observed.append(True)
        return 0

    assert (
        main(
            [],
            paths=AppPaths.from_root(tmp_path),
            localization_factory=lambda *args: context,
            event_loop=event_loop,
        )
        == 0
    )
    assert observed == [True]


@pytest.mark.parametrize(
    "disposition", [D.DATA_SAFETY_ERROR, D.EMERGENCY_RECOVERY, D.RECOVERY_ERROR]
)
def test_safety_startup_suppresses_localization_notice_and_has_no_chooser(
    tmp_path, disposition, localization_app
):
    write_preference(tmp_path, "zh_CN")
    context = initialize_localization(localization_app, tmp_path)
    with StartupService(AppPaths.from_root(tmp_path)).start() as runtime:
        runtime.result = ReliabilityResult(
            disposition, error=ErrorPresentation("private diagnostic", "safety-id")
        )
        host = DesktopHost(runtime)
        host.bind_localization(context)
        try:
            host.show_initial_state()
            assert "safety-id" in host.window.banner.message.text()
            assert "language pack" not in host.window.banner.message.text()
            assert not hasattr(host.window, "language_button")
        finally:
            host.dispose()


def test_error_and_operational_warning_priority_never_becomes_language_notice(
    tmp_path, localization_app
):
    from probability_calibration_tool.infrastructure.error_reporting import WarningCode

    write_preference(tmp_path, "zh_CN")
    context = initialize_localization(localization_app, tmp_path)
    with StartupService(AppPaths.from_root(tmp_path)).start() as runtime:
        runtime.result = ReliabilityResult(
            D.DATA_SAFETY_ERROR,
            (WarningCode.QUARANTINE_COPY_FAILED,),
            ErrorPresentation("PRIVATE SQL", "priority-id"),
        )
        host = DesktopHost(runtime)
        host.bind_localization(context)
        try:
            host.show_initial_state()
            text = host.window.banner.message.text()
            assert host.window.banner.property("severity") == "error"
            assert "priority-id" in text and "quarantine" in text
            assert "language pack" not in text and "PRIVATE" not in text
        finally:
            host.dispose()


def test_already_running_has_no_additional_localization_popup(
    tmp_path, monkeypatch, localization_app
):
    from probability_calibration_tool import desktop_host

    write_preference(tmp_path, "zh_CN")
    paths = AppPaths.from_root(tmp_path)
    calls = []
    monkeypatch.setattr(
        desktop_host, "startup_notice", lambda *args: pytest.fail("Extra startup warning")
    )
    with StartupService(paths).start():
        assert main([], paths=paths, notify_running=lambda: calls.append("already")) == 0
    assert calls == ["already"]
