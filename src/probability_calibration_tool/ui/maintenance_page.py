from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .formatting import format_timestamp
from .widgets import button, label


class MaintenancePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(label("Maintenance / Regimes"))
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Character", "Current regime", "Started locally", "Reason", "Included samples"]
        )
        self.table.setSortingEnabled(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.unavailable = label()
        layout.addWidget(self.unavailable)
        self.start = button("Start New Regime")
        layout.addWidget(self.start)
        self.confirmation = QWidget()
        form = QVBoxLayout(self.confirmation)
        self.summary = label()
        form.addWidget(self.summary)
        self.reason = QLineEdit()
        self.reason.setPlaceholderText("Optional reason")
        form.addWidget(self.reason)
        self.reason_error = label()
        form.addWidget(self.reason_error)
        actions = QHBoxLayout()
        self.back, self.confirm = button("Back"), button("Confirm")
        actions.addWidget(self.back)
        actions.addWidget(self.confirm)
        form.addLayout(actions)
        layout.addWidget(self.confirmation)
        self.confirmation.hide()
        self.rows = ()

    def populate(self, rows):
        self.rows = tuple(rows)
        self.table.clearContents()
        self.table.setRowCount(len(self.rows))
        for index, row in enumerate(self.rows):
            values = (
                row.display_name,
                str(row.active_regime_number),
                format_timestamp(row.regime_started_at),
                row.regime_reason or "",
                str(row.included_sample_count),
            )
            for column, value in enumerate(values):
                self.table.setItem(index, column, QTableWidgetItem(value))
        self.table.clearSelection()
        self.table.setCurrentCell(-1, -1)

    def selected(self):
        row = self.table.currentRow()
        return None if row < 0 else self.rows[row]

    def render(self, *, can_start, confirmation, connected):
        selected = self.selected()
        self.start.setEnabled(can_start and selected is not None and connected)
        self.confirm.setEnabled(can_start and selected is not None and connected)
        self.confirmation.setVisible(confirmation and selected is not None)
        self.table.setEnabled(not confirmation)
        self.start.setVisible(not confirmation)
        self.unavailable.setText(
            "A pending round prevents starting a new regime."
            if not can_start
            else ""
            if connected
            else "Regime service is not connected."
        )
        self.summary.setText(
            ""
            if selected is None
            else f"{selected.display_name} · Current regime {selected.active_regime_number}"
        )
