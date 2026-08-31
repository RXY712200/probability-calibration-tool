from typing import ClassVar

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from probability_calibration_tool.application.reliability_views import StartupDisposition as D

from .formatting import format_timestamp
from .widgets import button, label


class StartupSafetyPage(QWidget):
    MESSAGES: ClassVar = {
        D.RECOVERY_ERROR: (
            "Multiple pending rounds require recovery attention. "
            "Normal workflow is unavailable; no record has been selected."
        ),
        D.UNSUPPORTED_NEWER_SCHEMA: (
            "This database was created by a newer version of the application. "
            "This version will not write to it."
        ),
        D.ALREADY_RUNNING: "Probability Calibration Tool is already running.",
        D.DATA_SAFETY_ERROR: "Normal operation cannot safely continue.",
    }

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.message, self.error = label(), label()
        self.close_button = button("Close")
        layout.addWidget(self.message)
        layout.addWidget(self.error)
        layout.addWidget(self.close_button)
        layout.addStretch()

    def render(self, result):
        self.message.setText(self.MESSAGES[result.disposition])
        self.error.clear()
        if result.error is not None:
            self.error.setText(f"{result.error.message} Error ID: {result.error.error_id}")


class EmergencyRecoveryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(label("Emergency Recovery"))
        self.message = label("Select a verified backup explicitly before requesting Restore.")
        layout.addWidget(self.message)
        self.candidates = QListWidget()
        layout.addWidget(self.candidates)
        self.restore = button("Restore selected backup")
        self.close_button = button("Close")
        layout.addWidget(self.restore)
        layout.addWidget(self.close_button)
        self.rows = ()
        self.restore.setEnabled(False)

    def populate(self, candidates):
        self.rows = tuple(candidates)
        self.candidates.clear()
        for candidate in self.rows:
            item = QListWidgetItem(
                f"{candidate.category} · {format_timestamp(candidate.created_at)}"
                + (f" · {candidate.reason}" if candidate.reason else "")
                + ("" if candidate.valid else " · Unavailable")
            )
            if not candidate.valid:
                item.setFlags(
                    item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled
                )
            self.candidates.addItem(item)
        self.candidates.setCurrentRow(-1)
        self.candidates.clearSelection()

    def selected(self):
        index = self.candidates.currentRow()
        if index < 0 or not self.candidates.item(index).isSelected() or not self.rows[index].valid:
            return None
        return self.rows[index]

    def render(self, *, connected, active):
        self.candidates.setEnabled(not active)
        self.restore.setEnabled(connected and not active and self.selected() is not None)
