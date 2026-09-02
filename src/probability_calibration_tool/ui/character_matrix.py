from PySide6.QtCore import QCoreApplication, Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QGridLayout, QSizePolicy, QVBoxLayout, QWidget

from .localization import character_name
from .widgets import button, label


class CharacterMatrix(QWidget):
    selected = Signal(int)

    def __init__(self, characters):
        super().__init__()
        by_id = {row.character_id: row for row in characters}
        if set(by_id) != set(range(1, 35)) or len(characters) != 34:
            raise ValueError("The character matrix requires the 34 frozen character identities.")
        self.group = QButtonGroup(self)
        self.buttons = {}
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.grid = QGridLayout()
        self.grid.setVerticalSpacing(2)
        self.grid.addWidget(label(QCoreApplication.translate("Characters", "Normal")), 0, 0)
        self.grid.addWidget(label(QCoreApplication.translate("Characters", "Tainted")), 0, 1)
        for character_id in range(1, 35):
            name = character_name(character_id)
            widget = button(name.replace("&", "&&"))
            widget.setAccessibleName(name)
            widget.setCheckable(True)
            self.group.addButton(widget, character_id)
            self.buttons[character_id] = widget
            row = (character_id - 1) % 17 + 1
            column = (character_id - 1) // 17
            self.grid.addWidget(widget, row, column)
        layout.addLayout(self.grid)
        self.error = label()
        layout.addWidget(self.error)
        layout.addStretch()
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.group.idClicked.connect(self.selected)

    def value(self):
        value = self.group.checkedId()
        return None if value == -1 else value

    def sync(self, character_id, enabled):
        self.group.setExclusive(False)
        for key, widget in self.buttons.items():
            widget.setChecked(key == character_id)
            widget.setEnabled(enabled)
        self.group.setExclusive(True)
