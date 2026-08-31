import os
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from probability_calibration_tool.ui.main_window import MainWindow
from probability_calibration_tool.ui.presentation import (
    CharacterOption,
    PresentationPorts,
    RecoveryPresentation,
)


@pytest.fixture(scope="session")
def qapp():
    previous = os.environ.get("QT_QPA_PLATFORM")
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication.instance() or QApplication([])
    # Windows offscreen QPA has no system font discovery; load a real UI font for layout tests.
    font_path = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "segoeui.ttf"
    assert QFontDatabase.addApplicationFont(str(font_path)) >= 0
    app.setFont(QFont("Segoe UI", 9))
    yield app
    if previous is None:
        os.environ.pop("QT_QPA_PLATFORM", None)
    else:
        os.environ["QT_QPA_PLATFORM"] = previous


@pytest.fixture
def h(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "fake-localappdata"))
    monkeypatch.syspath_prepend(str(Path(__file__).parents[1] / "integration"))
    from application.helpers import Harness

    return Harness(tmp_path / "ui.db")


@pytest.fixture
def make_window(qapp, h):
    windows = []

    def make(workflow=None, **kwargs):
        characters = tuple(
            CharacterOption(v.character_id, v.display_name) for v in h.maintenance.list_characters()
        )
        ports = kwargs.pop(
            "ports",
            PresentationPorts(
                maintenance_rows=h.maintenance.list_characters,
                start_regime=h.regimes.start_new_regime,
                recovery_preview=lambda: RecoveryPresentation(
                    h.recovery.inspect(), h.recovery.continue_pending()
                ),
            ),
        )
        window = MainWindow(
            h.workflow() if workflow is None else workflow,
            characters,
            ports=ports,
            close_confirmation=kwargs.pop("close_confirmation", lambda *_: False),
            **kwargs,
        )
        windows.append(window)
        window.show()
        qapp.processEvents()
        return window

    yield make
    for window in windows:
        window.hide()
        window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


@pytest.fixture
def window(make_window):
    return make_window()
