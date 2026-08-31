"""Startup/restore safety presentation without a business Workflow."""

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from .banners import BannerHost
from .desktop_boundary import DesktopBoundary
from .restore_page import RestorePage
from .startup_pages import StartupSafetyPage


class SafetyWindow(DesktopBoundary, QMainWindow):
    def __init__(self, session, result, *, emergency=False):
        super().__init__()
        self.session, self.result = session, result
        self._disposed = self._operation_active = False
        self._restore_ticket = None
        self.setWindowTitle("Probability Calibration Tool 1.0 — Data Safety")
        self.resize(900, 650)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self.banner = BannerHost()
        layout.addWidget(self.banner)
        self.restore_page = RestorePage(emergency=True) if emergency else None
        self.page = self.restore_page or StartupSafetyPage()
        layout.addWidget(self.page)
        self.page.close_button.clicked.connect(self.close)
        if emergency:
            self._connect_restore()
            self._load_backups()
            self.page.close_button.setFocus()
        else:
            self.page.render(result)
        self.render_from_workflow()

    def _clear_errors(self):
        self.banner.clear()

    def _input_error(self, exc):
        self.banner.show_message(str(exc), "error")

    def _render(self):
        if self.restore_page is not None:
            self.restore_page.render_confirmation(
                allowed=True,
                confirming=self._restore_ticket is not None,
                busy=self._operation_active or self.session.busy,
            )

    def closeEvent(self, event):
        if self._operation_active or self.session.busy:
            event.ignore()
        else:
            event.accept()
