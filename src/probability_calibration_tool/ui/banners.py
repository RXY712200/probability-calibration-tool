from PySide6.QtCore import QT_TRANSLATE_NOOP, QCoreApplication
from PySide6.QtWidgets import QHBoxLayout, QWidget

from .localization import safe_error, severity_label, template
from .widgets import button, label


class BannerHost(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        self.message = label()
        self.dismiss = button(QCoreApplication.translate("AppShell", "Dismiss"))
        layout.addWidget(self.message, 1)
        layout.addWidget(self.dismiss)
        self.dismiss.clicked.connect(self.clear)
        self.clear()

    def clear(self):
        self.message.clear()
        self.hide()

    def show_message(self, text, severity="information"):
        self.message.setText(
            template(
                "AppShell", QT_TRANSLATE_NOOP("AppShell", "%1: %2"), severity_label(severity), text
            )
        )
        self.setProperty("severity", severity)
        self.show()

    def show_error(self, presentation):
        self.show_message(safe_error(presentation), "error")
