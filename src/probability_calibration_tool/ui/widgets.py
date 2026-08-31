from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QWidget,
)


def label(text=""):
    widget = QLabel(text)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    widget.setWordWrap(True)
    return widget


def button(text):
    widget = QPushButton(text)
    widget.setDefault(False)
    widget.setAutoDefault(False)
    return widget


class ChoicePair(QWidget):
    chosen = Signal(bool)

    def __init__(self, yes, no):
        super().__init__()
        self.group = QButtonGroup(self)
        self.buttons = {True: QRadioButton(yes), False: QRadioButton(no)}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        for value, widget in self.buttons.items():
            self.group.addButton(widget, int(value))
            layout.addWidget(widget)
            widget.clicked.connect(lambda checked, v=value: self.chosen.emit(v))
        layout.addStretch()

    def value(self):
        selected = self.group.checkedButton()
        return None if selected is None else bool(self.group.id(selected))

    def sync(self, value):
        self.group.setExclusive(False)
        for key, widget in self.buttons.items():
            widget.setChecked(value is key)
        self.group.setExclusive(True)
