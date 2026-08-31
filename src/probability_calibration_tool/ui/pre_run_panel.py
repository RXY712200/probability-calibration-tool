from PySide6.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QLineEdit

from .widgets import ChoicePair, button, label


class PreRunPanel(QGroupBox):
    def __init__(self):
        super().__init__("Pre-run inputs")
        layout = QGridLayout(self)
        self.reference = ChoicePair("Use history", "Do not use history")
        self.reference_error = label()
        layout.addWidget(self.reference, 0, 0, 1, 3)
        layout.addWidget(self.reference_error, 1, 0, 1, 3)
        self.probability = QLineEdit()
        self.win_odds = QLineEdit()
        self.lose_odds = QLineEdit()
        self.errors = {"reference_history": self.reference_error}
        for column, (field, title, widget) in enumerate(
            (
                ("subjective_probability", "Subjective probability", self.probability),
                ("win_odds", "Win odds", self.win_odds),
                ("lose_odds", "Lose odds", self.lose_odds),
            )
        ):
            widget.setObjectName(field)
            layout.addWidget(label(title), 2, column)
            if column == 0:
                row = QHBoxLayout()
                row.addWidget(widget)
                row.addWidget(label("%"))
                layout.addLayout(row, 3, column)
            else:
                layout.addWidget(widget, 3, column)
            error = label()
            self.errors[field] = error
            layout.addWidget(error, 4, column)
        self.primary = button("Calculate")
        self.modify = button("Modify")
        layout.addWidget(self.primary, 5, 1)
        layout.addWidget(self.modify, 5, 2)
        self.clear_errors()

    def clear_errors(self):
        for error in self.errors.values():
            error.clear()
            error.hide()

    def show_error(self, field, message):
        if field in self.errors:
            self.errors[field].setText(message)
            self.errors[field].show()

    def set_editable(self, editable):
        self.reference.setEnabled(editable)
        for widget in (self.probability, self.win_odds, self.lose_odds):
            widget.setReadOnly(not editable)

    def load(self, command):
        self.reference.sync(command.reference_history)
        # Preserve exact text already in the input when it denotes this command's integer.
        from .presentation import calculate_command

        current = calculate_command(None, None, self.probability.text(), "", "").p_h_raw
        if current != command.p_h_raw:
            self.probability.setText(str(command.p_h_raw))
        self.win_odds.setText(command.win_odds_raw)
        self.lose_odds.setText(command.lose_odds_raw)

    def clear_raw(self):
        for widget in (self.probability, self.win_odds, self.lose_odds):
            widget.clear()
        self.clear_errors()
