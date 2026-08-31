"""Unpackaged production composition root; no business decisions or transactions."""

import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from .application.reliability_views import StartupDisposition
from .application.startup_service import StartupService
from .desktop_host import DesktopHost
from .infrastructure.paths import AppPaths


def main(
    argv=None,
    *,
    paths=None,
    startup_factory=StartupService,
    host_factory=DesktopHost,
    event_loop=None,
    notify_running=None,
):
    app = QApplication.instance() or QApplication(sys.argv if argv is None else argv)
    resolved_paths = paths if paths is not None else AppPaths.from_local_appdata()
    with startup_factory(resolved_paths).start() as runtime:
        if runtime.result.disposition == StartupDisposition.ALREADY_RUNNING:
            notify = notify_running or (
                lambda: QMessageBox.information(
                    None,
                    "Probability Calibration Tool",
                    "Probability Calibration Tool is already running.",
                )
            )
            notify()
            return 0
        host = host_factory(runtime)
        try:
            host.show_initial_state()
            return app.exec() if event_loop is None else event_loop(app, host)
        finally:
            host.dispose()
