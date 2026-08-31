import sqlite3
from contextlib import closing
from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QAbstractButton, QLabel, QLineEdit, QListWidget, QTableWidget

from probability_calibration_tool.application.commands import CalculateCommand
from probability_calibration_tool.infrastructure.backup import BackupCategory, InventoryKind

COMMAND = CalculateCommand(1, False, 70, "2.00", "3.00")


def click(widget):
    QTest.mouseClick(widget, Qt.MouseButton.LeftButton)


def calculate(window, *, reference=False):
    click(window.characters.buttons[1])
    click(window.round.pre.reference.buttons[reference])
    window.round.pre.probability.setText("70")
    window.round.pre.win_odds.setText("2.00")
    window.round.pre.lose_odds.setText("3.00")
    click(window.round.pre.primary)
    return window.workflow.analysis


def complete(window, *, result=True, include=True):
    view = calculate(window)
    click(window.round.post.result.buttons[result])
    click(window.round.post.include.buttons[include])
    click(window.round.post.save)
    return view.round_id


def scalar(path, query, params=()):
    with closing(sqlite3.connect(path)) as db:
        return db.execute(query, params).fetchone()[0]


def rows(path, table):
    with closing(sqlite3.connect(path)) as db:
        return db.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()


def text_tree(root):
    values = []
    for widget in [
        root,
        *root.findChildren(QLabel),
        *root.findChildren(QLineEdit),
        *root.findChildren(QAbstractButton),
        *root.findChildren(QListWidget),
        *root.findChildren(QTableWidget),
    ]:
        if isinstance(widget, (QLabel, QLineEdit, QAbstractButton)):
            values.append(widget.text())
        if isinstance(widget, QListWidget):
            values.extend(widget.item(i).text() for i in range(widget.count()))
            values.extend(
                str(widget.item(i).data(Qt.ItemDataRole.UserRole)) for i in range(widget.count())
            )
        if isinstance(widget, QTableWidget):
            values.extend(
                widget.item(r, c).text()
                for r in range(widget.rowCount())
                for c in range(widget.columnCount())
                if widget.item(r, c)
            )
        values.extend((widget.toolTip(), widget.accessibleName(), widget.accessibleDescription()))
    return "\n".join(values)


def fail_recent(desk, monkeypatch):
    original = desk.host.backup.create

    def create(category, reason=None):
        if category == BackupCategory.RECENT:
            raise OSError("injected backup disk failure")
        return original(category, reason)

    monkeypatch.setattr(desk.host.backup, "create", create)


def begin_correction(window, *, reason="Correct recorded post-run facts"):
    window.show_correction()
    window.correction.candidates.setCurrentRow(0)
    click(window.correction.start)
    click(window.correction.result.buttons[False])
    click(window.correction.include.buttons[True])
    window.correction.reason.setText(reason)


@dataclass
class DesktopRig:
    runtime: object
    host: object

    @property
    def window(self):
        return self.host.window

    @property
    def session(self):
        return self.host.session

    @property
    def path(self):
        return self.runtime.paths.database

    def backups(self, category=BackupCategory.RECENT):
        return tuple(
            e for e in self.host.backup.inventory(category) if e.kind == InventoryKind.VALID
        )
