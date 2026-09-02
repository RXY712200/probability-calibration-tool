import gc
import weakref
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QSettings, QTranslator

from probability_calibration_tool import localization as loc
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.desktop_host import DesktopHost
from probability_calibration_tool.infrastructure.paths import AppPaths
from probability_calibration_tool.localization import (
    APP_QM_NAME,
    PREFERENCE_KEY,
    initialize_localization,
)
from probability_calibration_tool.localization import (
    FallbackReason as Reason,
)
from probability_calibration_tool.localization import (
    Language as L,
)
from probability_calibration_tool.localization import (
    PreferenceSaveFailure as Failure,
)
from probability_calibration_tool.localization import (
    PreferenceState as State,
)
from probability_calibration_tool.localization import (
    QtTranslationStatus as QtStatus,
)

from .helpers import App, SettingsPlan, Translator, dummy_pack, write_preference


@pytest.fixture
def qt_directory(tmp_path, monkeypatch):
    directory = tmp_path / "qt-framework"
    directory.mkdir()

    def qt_path(kind):
        assert kind == loc.QLibraryInfo.LibraryPath.TranslationsPath
        return str(directory)

    monkeypatch.setattr(loc.QLibraryInfo, "path", qt_path)
    return directory


@pytest.mark.parametrize("pack", ["missing", "invalid", "valid"])
@pytest.mark.parametrize(
    "preference,state,preferred",
    [
        (None, State.DEFAULT, L.EN),
        ("en", State.SAVED_VALID, L.EN),
        ("zh_CN", State.SAVED_VALID, L.ZH_CN),
        ("banana", State.SAVED_INVALID, L.EN),
        ("read_error", State.READ_ERROR, L.EN),
    ],
)
def test_preferred_available_effective_golden_matrix(
    tmp_path, qt_directory, pack, preference, state, preferred
):
    if pack != "missing":
        dummy_pack(tmp_path)
    plan = {"values": {PREFERENCE_KEY: preference}} if preference is not None else {}
    if preference == "read_error":
        plan = {"status": QSettings.Status.AccessError}
    factory = SettingsPlan(plan)
    app = App()
    context = initialize_localization(
        app,
        tmp_path,
        settings_factory=factory,
        translator_factory=lambda: Translator(load_ok=pack == "valid"),
    )
    expected_reason = Reason.NONE
    if state == State.SAVED_INVALID:
        expected_reason = Reason.INVALID_PREFERENCE
    elif state == State.READ_ERROR:
        expected_reason = Reason.SETTINGS_READ_ERROR
    elif preferred == L.ZH_CN and pack != "valid":
        expected_reason = (
            Reason.PREFERRED_PACK_MISSING if pack == "missing" else Reason.PREFERRED_PACK_INVALID
        )
    effective = L.ZH_CN if preferred == L.ZH_CN and pack == "valid" else L.EN
    assert context.preferred_language == preferred
    assert context.preference_state == state
    assert context.effective_language == effective
    assert context.available_languages == ({L.EN, L.ZH_CN} if pack == "valid" else {L.EN})
    assert context.fallback_reason == context.startup_notice_kind == expected_reason
    assert context.settings_path == tmp_path / "settings.ini"
    assert context.languages_directory == tmp_path / "languages"
    if effective == L.EN:
        assert context.app_translator is context.qt_translator is None
        assert context.qt_translation_status == QtStatus.NOT_REQUIRED
        assert app.events == []
    else:
        assert context.app_translator is not None and context.qt_translator is None
        assert context.qt_translation_status == QtStatus.UNAVAILABLE
        assert app.events == [("install", APP_QM_NAME)]
    assert not context.settings_path.exists()


@pytest.mark.parametrize(
    "qt_case,status",
    [
        ("valid", QtStatus.LOADED),
        ("missing", QtStatus.UNAVAILABLE),
        ("load_failed", QtStatus.LOAD_FAILED),
        ("empty", QtStatus.LOAD_FAILED),
        ("install_false", QtStatus.LOAD_FAILED),
        ("install_oserror", QtStatus.LOAD_FAILED),
        ("install_runtime_error", QtStatus.LOAD_FAILED),
    ],
)
def test_qt_failure_only_degrades_framework_app_still_chinese(
    tmp_path, qt_directory, qt_case, status
):
    dummy_pack(tmp_path)
    write_preference(tmp_path, "zh_CN")
    if qt_case != "missing":
        (qt_directory / "qtbase_zh_CN.qm").write_bytes(b"injected framework pack")

    class SelectiveTranslator(Translator):
        def load(self, path, *options):
            if Path(path).name == "qtbase_zh_CN.qm":
                self.load_ok, self.empty = qt_case != "load_failed", qt_case == "empty"
            return super().load(path, *options)

    app = App(
        fail="qtbase_zh_CN.qm" if qt_case.startswith("install") else None,
        error=(
            OSError("partial Qt install")
            if qt_case == "install_oserror"
            else RuntimeError("partial Qt framework install")
            if qt_case == "install_runtime_error"
            else None
        ),
    )
    context = initialize_localization(app, tmp_path, translator_factory=SelectiveTranslator)
    assert context.effective_language == L.ZH_CN and context.fallback_reason == Reason.NONE
    assert context.qt_translation_status == status and context.app_translator is not None
    assert (context.qt_translator is not None) == (status == QtStatus.LOADED)
    assert app.events[-1] == ("install", APP_QM_NAME)
    if qt_case == "valid":
        assert app.events == [("install", "qtbase_zh_CN.qm"), ("install", APP_QM_NAME)]
        assert len(app.active) == 2
    else:
        assert list(app.active) == [id(context.app_translator)]


def test_invalid_app_pack_never_activates_valid_qt(tmp_path, qt_directory):
    dummy_pack(tmp_path)
    write_preference(tmp_path, "zh_CN")
    (qt_directory / "qtbase_zh_CN.qm").write_bytes(b"Qt would load")
    app = App()
    context = initialize_localization(
        app, tmp_path, translator_factory=lambda: Translator(empty=True)
    )
    assert context.effective_language == L.EN
    assert context.fallback_reason == Reason.PREFERRED_PACK_INVALID
    assert app.events == [] and not app.active


@pytest.mark.parametrize("error", [None, RuntimeError("unexpected app install failure")])
def test_app_install_failure_removes_app_and_already_installed_qt(tmp_path, qt_directory, error):
    dummy_pack(tmp_path)
    write_preference(tmp_path, "zh_CN")
    (qt_directory / "qtbase_zh_CN.qm").write_bytes(b"injected Qt")
    app = App(fail=APP_QM_NAME, error=error)
    if error is not None:
        with pytest.raises(RuntimeError, match="unexpected app install"):
            initialize_localization(app, tmp_path, translator_factory=Translator)
    else:
        context = initialize_localization(app, tmp_path, translator_factory=Translator)
        assert context.preferred_language == L.ZH_CN and context.effective_language == L.EN
        assert context.fallback_reason == Reason.APP_INSTALL_FAILED
        assert context.app_translator is context.qt_translator is None
        assert context.qt_translation_status == QtStatus.NOT_REQUIRED
    assert app.events == [
        ("install", "qtbase_zh_CN.qm"),
        ("install", APP_QM_NAME),
        ("remove", APP_QM_NAME),
        ("remove", "qtbase_zh_CN.qm"),
    ]
    assert not app.active


def test_new_pack_is_not_promoted_until_new_startup(tmp_path):
    app = App()
    context = initialize_localization(app, tmp_path, translator_factory=Translator)
    dummy_pack(tmp_path)
    assert context.save_preference(L.ZH_CN).failure == Failure.PACK_INVALID
    assert context.available_languages == {L.EN} and not context.settings_path.exists()
    assert not app.events
    restarted = initialize_localization(app, tmp_path, translator_factory=Translator)
    assert restarted.available_languages == {L.EN, L.ZH_CN}
    assert restarted.save_preference(L.ZH_CN).success
    assert restarted.effective_language == L.EN and restarted.restart_required


@pytest.mark.parametrize("change", ["delete", "corrupt"])
@pytest.mark.parametrize("preferred", ["en", "zh_CN"])
def test_confirm_can_demote_but_never_replace_active_language(
    tmp_path, qt_directory, preferred, change
):
    path = dummy_pack(tmp_path)
    write_preference(tmp_path, preferred)
    app = App()
    valid = True
    context = initialize_localization(
        app, tmp_path, translator_factory=lambda: Translator(load_ok=valid)
    )
    runtime = (context.effective_language, context.app_translator, context.qt_translator)
    events, before = list(app.events), context.settings_path.read_bytes()
    if change == "delete":
        path.unlink()
    else:
        valid = False
    assert context.save_preference(L.ZH_CN).failure == Failure.PACK_INVALID
    assert context.available_languages == {L.EN}
    assert context.preferred_language == preferred
    assert (context.effective_language, context.app_translator, context.qt_translator) == runtime
    assert app.events == events and context.settings_path.read_bytes() == before
    dummy_pack(tmp_path)
    valid = True
    assert context.save_preference(L.ZH_CN).failure == Failure.PACK_INVALID
    assert context.available_languages == {L.EN}


def test_real_translators_held_across_gc_preference_save_and_business_window_rebuild(
    tmp_path, qt_directory, compile_qm, localization_app, real_contexts
):
    root = tmp_path / "product"
    compile_qm(root / "languages", translation="app wins")
    compile_qm(qt_directory, name="qtbase_zh_CN.qm", translation="framework lower priority")
    write_preference(root, "zh_CN")
    context = initialize_localization(localization_app, root)
    real_contexts.append(context)
    assert isinstance(context.app_translator, QTranslator)
    assert isinstance(context.qt_translator, QTranslator)
    assert context.qt_translation_status == QtStatus.LOADED
    app_ref, qt_ref = weakref.ref(context.app_translator), weakref.ref(context.qt_translator)
    assert localization_app.translate("Localization", "Language") == "app wins"
    with StartupService(AppPaths.from_root(root)).start() as runtime:
        host = DesktopHost(runtime)
        try:
            host.show_initial_state()
            first_session, first_window = host.session, host.window
            assert first_session is not None
            host.show_initial_state()  # Existing host routing rebuilds business session/window.
            assert host.session is not first_session and host.window is not first_window
            QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
            gc.collect()
            assert app_ref() is context.app_translator and qt_ref() is context.qt_translator
            assert localization_app.translate("Localization", "Language") == "app wins"
            result = context.save_preference(L.EN)
            assert result.success and result.restart_required
            assert context.preferred_language == L.EN and context.effective_language == L.ZH_CN
            assert context.app_translator is app_ref() and context.qt_translator is qt_ref()
            assert localization_app.translate("Localization", "Language") == "app wins"
        finally:
            host.dispose()
            QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    gc.collect()
    assert app_ref() is context.app_translator and qt_ref() is context.qt_translator


@pytest.mark.parametrize(
    "attribute,value",
    [
        ("effective_language", L.ZH_CN),
        ("app_translator", object()),
        ("qt_translator", object()),
        ("startup_notice_kind", Reason.NONE),
        ("available_languages", frozenset({L.ZH_CN})),
    ],
)
def test_public_runtime_state_cannot_be_reassigned(tmp_path, attribute, value):
    context = initialize_localization(App(), tmp_path)
    with pytest.raises(AttributeError):
        setattr(context, attribute, value)
