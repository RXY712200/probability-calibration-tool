import gc
import weakref
from types import SimpleNamespace

import pytest
from PySide6.QtCore import QSettings

from probability_calibration_tool import bootstrap
from probability_calibration_tool.application.reliability_views import StartupDisposition as D
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.infrastructure.paths import AppPaths
from probability_calibration_tool.localization import (
    APP_QM_NAME,
    Language,
    initialize_localization,
)

from .helpers import App, SettingsPlan, Translator, dummy_pack, write_preference


@pytest.mark.parametrize("disposition", list(D))
def test_qapplication_localization_startup_ui_order_and_teardown(
    tmp_path, monkeypatch, disposition
):
    events, refs = [], {}
    paths = AppPaths.from_root(tmp_path)

    class Application:
        @staticmethod
        def instance():
            return None

        def __init__(self, argv):
            assert argv == []
            events.append("QApplication")

    class Context:
        def __del__(self):
            events.append("localization-release")

    def localization_factory(app, root):
        assert isinstance(app, Application) and root == paths.root
        events.append("localization")
        context = Context()
        refs["context"] = weakref.ref(context)
        return context

    class Runtime:
        result = SimpleNamespace(disposition=disposition)

        def __enter__(self):
            events.append("runtime-enter")
            assert refs["context"]() is not None
            return self

        def __exit__(self, *args):
            gc.collect()
            assert refs["context"]() is None
            events.append("runtime-release")

    class Startup:
        def __init__(self, resolved_paths):
            assert resolved_paths == paths and refs["context"]() is not None
            events.append("StartupService")

        def start(self):
            events.append("startup")
            return Runtime()

    class Host:
        def __init__(self, runtime):
            assert disposition != D.ALREADY_RUNNING
            assert runtime.result.disposition == disposition and refs["context"]() is not None
            events.append("host")

        def show_initial_state(self):
            events.append("UI")

        def dispose(self):
            assert refs["context"]() is not None
            events.append("dispose-UI")

    def notify():
        assert refs["context"]() is not None
        events.append("notify-only")

    def loop(app, host):
        assert refs["context"]() is not None
        events.append("event-loop")
        return 13

    monkeypatch.setattr(bootstrap, "QApplication", Application)
    code = bootstrap.main(
        [],
        paths=paths,
        localization_factory=localization_factory,
        startup_factory=Startup,
        host_factory=Host,
        event_loop=loop,
        notify_running=notify,
    )
    prefix = ["QApplication", "localization", "StartupService", "startup", "runtime-enter"]
    middle = (
        ["notify-only"]
        if disposition == D.ALREADY_RUNNING
        else ["host", "UI", "event-loop", "dispose-UI"]
    )
    assert events == prefix + middle + ["localization-release", "runtime-release"]
    assert code == (0 if disposition == D.ALREADY_RUNNING else 13)


@pytest.mark.parametrize(
    "failure",
    [
        "missing_pack",
        "invalid_pack",
        "invalid_preference",
        "access_error",
        "format_error",
        "unexpected",
    ],
)
def test_localization_failure_does_not_change_real_healthy_business_startup(
    tmp_path, localization_app, failure, caplog
):
    paths = AppPaths.from_root(tmp_path / "product")
    with StartupService(paths).start() as baseline:
        assert baseline.result.disposition == D.READY_DRAFT
    if failure in ("missing_pack", "invalid_pack"):
        write_preference(paths.root, "zh_CN")
        if failure == "invalid_pack":
            dummy_pack(paths.root)  # Invalid for the real QTranslator.
    elif failure == "invalid_preference":
        write_preference(paths.root, "banana")
    contexts, results = [], []

    def localization_factory(app, root):
        assert app is localization_app
        if failure == "unexpected":
            raise RuntimeError("injected localization programming failure")
        config = {}
        if failure in ("access_error", "format_error"):
            status = (
                QSettings.Status.AccessError
                if failure == "access_error"
                else QSettings.Status.FormatError
            )
            config["settings_factory"] = SettingsPlan({"status": status})
        context = initialize_localization(app, root, **config)
        contexts.append(context)
        assert context.effective_language == Language.EN
        return context

    class Host:
        def __init__(self, runtime):
            self.runtime = runtime
            results.append(runtime.result.disposition)
            assert runtime.lock.held

        def show_initial_state(self):
            assert self.runtime.result.disposition == D.READY_DRAFT

        def dispose(self):
            assert self.runtime.lock.held

    assert (
        bootstrap.main(
            [],
            paths=paths,
            localization_factory=localization_factory,
            host_factory=Host,
            event_loop=lambda app, host: 0,
        )
        == 0
    )
    assert results == [D.READY_DRAFT]
    if failure == "unexpected":
        assert "Localization initialization failed; using English." in caplog.text
        assert "injected localization programming failure" in caplog.text
    else:
        assert len(contexts) == 1


def test_unexpected_partial_translation_activation_fails_open_cleanly(
    tmp_path, monkeypatch, caplog
):
    from probability_calibration_tool import localization as loc

    dummy_pack(tmp_path)
    write_preference(tmp_path, "zh_CN")
    qt_directory = tmp_path / "qt"
    qt_directory.mkdir()
    (qt_directory / "qtbase_zh_CN.qm").write_bytes(b"Qt test")
    monkeypatch.setattr(loc.QLibraryInfo, "path", lambda kind: str(qt_directory))
    app = App(fail=APP_QM_NAME, error=RuntimeError("partial app activation"))
    monkeypatch.setattr(bootstrap, "QApplication", SimpleNamespace(instance=lambda: app))
    seen = []

    class Host:
        def __init__(self, runtime):
            assert not app.active  # No Qt-only Chinese state reaches user UI.
            seen.append(runtime.result.disposition)

        def show_initial_state(self):
            pass

        def dispose(self):
            pass

    assert (
        bootstrap.main(
            [],
            paths=AppPaths.from_root(tmp_path),
            localization_factory=lambda app, root: initialize_localization(
                app, root, translator_factory=Translator
            ),
            host_factory=Host,
            event_loop=lambda app, host: 0,
        )
        == 0
    )
    assert seen == [D.READY_DRAFT] and not app.active
    assert "partial app activation" in caplog.text


@pytest.mark.parametrize("stage", ["startup", "host", "loop"])
def test_localization_fail_open_does_not_swallow_business_exceptions(tmp_path, stage):
    paths = AppPaths.from_root(tmp_path)
    disposed = []

    def bug(*args):
        raise RuntimeError(f"business {stage} failure")

    class Host:
        def __init__(self, runtime):
            self.runtime = runtime

        def show_initial_state(self):
            pass

        def dispose(self):
            assert self.runtime.lock.held
            disposed.append(True)

    options = (
        {"startup_factory": bug}
        if stage == "startup"
        else {
            "host_factory": bug if stage == "host" else Host,
            "event_loop": bug,
        }
    )
    with pytest.raises(RuntimeError, match=f"business {stage} failure"):
        bootstrap.main([], paths=paths, **options)
    assert disposed == ([True] if stage == "loop" else [])
