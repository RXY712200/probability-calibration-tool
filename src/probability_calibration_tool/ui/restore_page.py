from PySide6.QtCore import QCoreApplication

from .startup_pages import EmergencyRecoveryPage
from .widgets import button, label


class RestorePage(EmergencyRecoveryPage):
    def __init__(self, *, emergency=False):
        super().__init__()
        self.layout().itemAt(0).widget().setText(
            QCoreApplication.translate("Restore", "Emergency Restore")
            if emergency
            else QCoreApplication.translate("Restore", "Normal Restore")
        )
        self.refresh = button(QCoreApplication.translate("Restore", "Reload verified backups"))
        self.confirmation = label(
            QCoreApplication.translate(
                "Restore", "Replace the live database with the selected verified backup?"
            )
        )
        self.confirm, self.back = (
            button(QCoreApplication.translate("Restore", "Confirm Restore")),
            button(QCoreApplication.translate("Restore", "Back")),
        )
        for widget in (self.refresh, self.confirmation, self.confirm, self.back):
            self.layout().addWidget(widget)
        self.close_button.setVisible(emergency)
        self.render_confirmation(allowed=False, confirming=False, busy=False)

    def render_confirmation(self, *, allowed, confirming, busy):
        super().render(connected=allowed, active=busy)
        self.candidates.setEnabled(not busy and not confirming)
        self.restore.setVisible(not confirming)
        self.refresh.setEnabled(not busy and not confirming)
        for widget in (self.confirmation, self.confirm, self.back):
            widget.setVisible(confirming)
        self.confirm.setEnabled(allowed and confirming and not busy and self.selected() is not None)
        self.back.setEnabled(not busy)
        self.close_button.setEnabled(not busy)
