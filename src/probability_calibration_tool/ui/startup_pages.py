from typing import ClassVar

from PySide6.QtCore import QT_TRANSLATE_NOOP, QCoreApplication, Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from probability_calibration_tool.application.reliability_views import StartupDisposition as D

from .formatting import format_timestamp
from .localization import backup_category, backup_reason, safe_error
from .widgets import button, label


class StartupSafetyPage(QWidget):
    MESSAGES: ClassVar = {
        D.RECOVERY_ERROR: QT_TRANSLATE_NOOP(
            "StartupSafety",
            "Multiple pending rounds require recovery attention. Normal workflow is unavailable; no record has been selected.",
        ),
        D.UNSUPPORTED_NEWER_SCHEMA: QT_TRANSLATE_NOOP(
            "StartupSafety",
            "This database was created by a newer version of the application. This version will not write to it.",
        ),
        D.ALREADY_RUNNING: QT_TRANSLATE_NOOP(
            "StartupSafety", "Probability Calibration Tool is already running."
        ),
        D.DATA_SAFETY_ERROR: QT_TRANSLATE_NOOP(
            "StartupSafety", "Normal operation cannot safely continue."
        ),
    }

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.message, self.error = label(), label()
        self.close_button = button(QCoreApplication.translate("StartupSafety", "Close"))
        layout.addWidget(self.message)
        layout.addWidget(self.error)
        layout.addWidget(self.close_button)
        layout.addStretch()

    def render(self, result):
        self.message.setText(
            QCoreApplication.translate("StartupSafety", self.MESSAGES[result.disposition])
        )
        self.error.clear()
        if result.error is not None:
            self.error.setText(safe_error(result.error))


class EmergencyRecoveryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(label(QCoreApplication.translate("Restore", "Emergency Recovery")))
        self.message = label(
            QCoreApplication.translate(
                "Restore", "Select a verified backup explicitly before requesting Restore."
            )
        )
        layout.addWidget(self.message)
        self.candidates = QListWidget()
        layout.addWidget(self.candidates)
        self.restore = button(QCoreApplication.translate("Restore", "Restore selected backup"))
        self.close_button = button(QCoreApplication.translate("Restore", "Close"))
        layout.addWidget(self.restore)
        layout.addWidget(self.close_button)
        self.rows = ()
        self.restore.setEnabled(False)

    def populate(self, candidates):
        self.rows = tuple(candidates)
        self.candidates.clear()
        for candidate in self.rows:
            item = QListWidgetItem(
                f"{backup_category(candidate.category)} · {format_timestamp(candidate.created_at)}"
                + (f" · {backup_reason(candidate.reason)}" if candidate.reason else "")
                + (
                    ""
                    if candidate.valid
                    else " · " + QCoreApplication.translate("Restore", "Unavailable")
                )
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
