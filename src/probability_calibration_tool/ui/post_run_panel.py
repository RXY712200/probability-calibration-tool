from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

from .widgets import ChoicePair, button, label


class PostRunPanel(QGroupBox):
    def __init__(self):
        super().__init__("Post-run")
        layout = QVBoxLayout(self)
        self.result = ChoicePair("Win", "Loss")
        self.include = ChoicePair("Include", "Exclude")
        choices = QHBoxLayout()
        choices.addWidget(self.result)
        choices.addWidget(self.include)
        layout.addLayout(choices)
        self.confirmation = QWidget()
        row = QHBoxLayout(self.confirmation)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(label("Save the selected result and history inclusion?"), 1)
        self.back, self.save = button("Back"), button("Confirm Save")
        row.addWidget(self.back)
        row.addWidget(self.save)
        layout.addWidget(self.confirmation)
        self.void = button("Void Pending")
        layout.addWidget(self.void)
        self.void_confirmation = QWidget()
        void_layout = QVBoxLayout(self.void_confirmation)
        void_layout.addWidget(label("Void this pending round? Its audit record will be preserved."))
        self.reason = QLineEdit()
        self.reason.setPlaceholderText("Optional reason")
        void_layout.addWidget(self.reason)
        actions = QHBoxLayout()
        self.cancel_void, self.confirm_void = button("Cancel"), button("Confirm Void")
        actions.addWidget(self.cancel_void)
        actions.addWidget(self.confirm_void)
        void_layout.addLayout(actions)
        layout.addWidget(self.void_confirmation)
        self.void_confirmation.hide()
