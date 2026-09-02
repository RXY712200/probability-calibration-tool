"""Unpackaged production composition root; no business decisions or transactions."""

import logging
import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QMessageBox

from .application.reliability_views import StartupDisposition
from .application.startup_service import StartupService
from .desktop_host import DesktopHost
from .infrastructure.paths import AppPaths
from .localization import english_context, initialize_localization


def main(
    argv=None,
    *,
    paths=None,
    startup_factory=StartupService,
    host_factory=DesktopHost,
    event_loop=None,
    notify_running=None,
    localization_factory=initialize_localization,
):
    app = QApplication.instance() or QApplication(sys.argv if argv is None else argv)
    resolved_paths = paths if paths is not None else AppPaths.from_local_appdata()
    try:
        localization = localization_factory(app, resolved_paths.root)
    except Exception:  # Only localization initialization is allowed to fail open.
        logging.getLogger(__name__).exception("Localization initialization failed; using English.")
        localization = english_context(resolved_paths.root)
    with startup_factory(resolved_paths).start() as runtime:
        if runtime.result.disposition == StartupDisposition.ALREADY_RUNNING:
            notify = notify_running or (
                lambda: QMessageBox.information(
                    None,
                    "Probability Calibration Tool",
                    QCoreApplication.translate(
                        "StartupSafety", "Probability Calibration Tool is already running."
                    ),
                )
            )
            try:
                notify()
                return 0
            finally:
                del localization
        host = host_factory(runtime)
        try:
            if isinstance(host, DesktopHost):
                host.bind_localization(localization)
            host.show_initial_state()
            return app.exec() if event_loop is None else event_loop(app, host)
        finally:
            host.dispose()
            # Process-level ownership outlives all host/session/window disposal.
            del localization
