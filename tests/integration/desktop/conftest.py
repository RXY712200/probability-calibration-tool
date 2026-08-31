import os
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.desktop_host import DesktopHost
from probability_calibration_tool.infrastructure.paths import AppPaths

from .helpers import DesktopRig


@pytest.fixture(scope="session")
def desktop_app():
    previous = os.environ.get("QT_QPA_PLATFORM")
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication.instance() or QApplication([])
    font = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "segoeui.ttf"
    assert QFontDatabase.addApplicationFont(str(font)) >= 0
    app.setFont(QFont("Segoe UI", 9))
    yield app
    if previous is None:
        os.environ.pop("QT_QPA_PLATFORM", None)
    else:
        os.environ["QT_QPA_PLATFORM"] = previous


@pytest.fixture(autouse=True)
def isolated_localappdata(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "fake-localappdata"))


@pytest.fixture
def paths(tmp_path):
    return AppPaths.from_root(tmp_path / "desktop")


@pytest.fixture
def desk(paths, desktop_app):
    runtime = StartupService(paths).start()
    host = DesktopHost(runtime)
    try:
        host.show_initial_state()
        assert host.session is not None
        yield DesktopRig(runtime, host)
    finally:
        host.dispose()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        runtime.close()
