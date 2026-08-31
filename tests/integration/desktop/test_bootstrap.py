import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest
from PySide6.QtCore import QTimer

from probability_calibration_tool.application.reliability_views import StartupDisposition as D
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.bootstrap import main
from probability_calibration_tool.desktop_host import DesktopHost
from probability_calibration_tool.infrastructure.runtime_lock import RuntimeLock

from .helpers import calculate


def test_runtime_spans_real_qt_event_loop_then_disposes_before_lock_release(paths, desktop_app):
    observed = []

    class Host(DesktopHost):
        def dispose(self):
            observed.append(("dispose", self.runtime.lock.held))
            super().dispose()

    def loop(app, host):
        assert host.runtime.lock.held
        lock = RuntimeLock(paths.lock_file)
        assert not lock.acquire()
        calculate(host.window)
        QTimer.singleShot(0, lambda: app.exit(7))
        return app.exec()

    assert main([], paths=paths, host_factory=Host, event_loop=loop) == 7
    assert observed == [("dispose", True)]
    with StartupService(paths).start() as restarted:
        assert restarted.result.disposition == D.READY_RECOVERY
        assert restarted.lock.held


def test_bootstrap_exception_still_disposes_before_runtime_close(paths, desktop_app):
    hosts = []

    def factory(runtime):
        host = DesktopHost(runtime)
        hosts.append(host)
        return host

    def loop(app, host):
        raise ValueError("injected loop failure")

    with pytest.raises(ValueError, match="loop failure"):
        main([], paths=paths, host_factory=factory, event_loop=loop)
    assert hosts[0].disposed
    assert not hosts[0].runtime.lock.held


def test_already_running_notifies_without_constructing_host_or_entering_loop(desk, desktop_app):
    notifications = []

    def forbidden(*args):
        pytest.fail("Already-running path must not construct host or enter normal loop")

    assert (
        main(
            [],
            paths=desk.runtime.paths,
            host_factory=forbidden,
            event_loop=forbidden,
            notify_running=lambda: notifications.append("notified"),
        )
        == 0
    )
    assert notifications == ["notified"]
    assert desk.runtime.lock.held


def test_main_module_is_only_import_and_system_exit():
    path = Path(__file__).parents[3] / "src" / "probability_calibration_tool" / "__main__.py"
    # tests/integration/desktop -> repository is parents[3].
    tree = ast.parse(path.read_text(encoding="utf-8"))
    assert len(tree.body) == 2
    assert isinstance(tree.body[0], ast.ImportFrom)
    assert isinstance(tree.body[1], ast.Raise)


def test_actual_unpacked_module_entry_subprocess_initializes_and_exits_cleanly(tmp_path):
    source = Path(__file__).parents[3] / "src"
    environment = dict(
        os.environ, LOCALAPPDATA=str(tmp_path / "isolated"), QT_QPA_PLATFORM="offscreen"
    )
    script = (
        "import runpy; "
        "from PySide6.QtWidgets import QApplication; "
        "from PySide6.QtCore import QTimer; "
        "from PySide6.QtGui import QFontDatabase; "
        "app = QApplication([]); "
        "QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf'); "
        "QTimer.singleShot(0, app.quit); "
        "runpy.run_module('probability_calibration_tool', run_name='__main__')"
    )
    process = subprocess.run(
        [sys.executable, "-c", script],
        cwd=source,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert process.returncode == 0, process.stderr
    from probability_calibration_tool.infrastructure.paths import AppPaths

    paths = AppPaths.from_root(tmp_path / "isolated" / "ProbabilityCalibrationTool")
    assert paths.database.exists()
    with StartupService(paths).start() as runtime:
        assert runtime.result.disposition == D.READY_DRAFT
