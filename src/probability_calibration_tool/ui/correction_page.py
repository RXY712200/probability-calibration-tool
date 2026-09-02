"""Audit identifiers plus explicitly new post-run facts. No previous results."""

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QLineEdit, QListWidget, QVBoxLayout, QWidget

from .formatting import format_timestamp
from .localization import character_name
from .widgets import ChoicePair, button, label


class CorrectionPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(
            label(
                QCoreApplication.translate(
                    "Correction", "Historical Correction — post-run facts only"
                )
            )
        )
        layout.addWidget(
            label(
                QCoreApplication.translate(
                    "Correction", "Identify a completed record by character, time and round ID."
                )
            )
        )
        self.candidates = QListWidget()
        layout.addWidget(self.candidates)
        self.start = button(QCoreApplication.translate("Correction", "Correct selected record"))
        layout.addWidget(self.start)
        self.form = QWidget()
        fields = QVBoxLayout(self.form)
        self.result = ChoicePair(
            QCoreApplication.translate("Correction", "Corrected result: Win"),
            QCoreApplication.translate("Correction", "Corrected result: Loss"),
        )
        self.include = ChoicePair(
            QCoreApplication.translate("Correction", "Corrected: Include"),
            QCoreApplication.translate("Correction", "Corrected: Exclude"),
        )
        self.reason = QLineEdit()
        self.reason.setPlaceholderText(
            QCoreApplication.translate("Correction", "Required correction reason")
        )
        self.error = label()
        self.confirm, self.back = (
            button(QCoreApplication.translate("Correction", "Confirm Correction")),
            button(QCoreApplication.translate("Correction", "Back")),
        )
        for widget in (self.result, self.include, self.reason, self.confirm, self.back):
            fields.addWidget(widget)
        layout.addWidget(self.form)
        layout.addWidget(self.error)
        self.notice = label()
        layout.addWidget(self.notice)
        self.rows = ()
        self.render(allowed=False, confirming=False, busy=False)

    def populate(self, rows):
        self.rows = tuple(rows)
        self.candidates.clear()
        for row in self.rows:
            self.candidates.addItem(
                f"{character_name(row.character_id)} · {format_timestamp(row.completed_at)} · {row.round_id}"
            )
        self.candidates.setCurrentRow(-1)
        self.candidates.clearSelection()
        self.reset_form()

    def reset_form(self):
        self.result.sync(None)
        self.include.sync(None)
        self.reason.clear()
        self.error.clear()

    def selected(self):
        index = self.candidates.currentRow()
        if index < 0 or not self.candidates.item(index).isSelected():
            return None
        return self.rows[index]

    def render(self, *, allowed, confirming, busy):
        self.candidates.setEnabled(not busy and not confirming)
        self.start.setVisible(not confirming)
        self.start.setEnabled(allowed and not busy and self.selected() is not None)
        self.form.setVisible(confirming)
        self.form.setEnabled(allowed and not busy)
        self.confirm.setEnabled(
            allowed
            and not busy
            and confirming
            and self.result.value() is not None
            and self.include.value() is not None
            and bool(self.reason.text().strip())
        )
