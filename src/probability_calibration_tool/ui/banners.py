from PySide6.QtWidgets import QHBoxLayout, QWidget

from .widgets import button, label


class BannerHost(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        self.message = label()
        self.dismiss = button("Dismiss")
        layout.addWidget(self.message, 1)
        layout.addWidget(self.dismiss)
        self.dismiss.clicked.connect(self.clear)
        self.clear()

    def clear(self):
        self.message.clear()
        self.hide()

    def show_message(self, text, severity="information"):
        self.message.setText(f"{severity.capitalize()}: {text}")
        self.setProperty("severity", severity)
        self.show()

    def show_error(self, presentation):
        self.show_message(f"{presentation.message} Error ID: {presentation.error_id}", "error")
