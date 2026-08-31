from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QAbstractButton,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QTableWidget,
)


def click(widget):
    QTest.mouseClick(widget, Qt.MouseButton.LeftButton)


def fill(window, *, reference=False, probability="70", win="2.00", lose="3.00"):
    click(window.characters.buttons[1])
    click(window.round.pre.reference.buttons[reference])
    for widget, text in (
        (window.round.pre.probability, probability),
        (window.round.pre.win_odds, win),
        (window.round.pre.lose_odds, lose),
    ):
        widget.setText(text)


def calculate(window, **kwargs):
    fill(window, **kwargs)
    click(window.round.pre.primary)
    return window.workflow.analysis


def widget_text(root):
    # Include hidden descendants, non-label item text, tooltips and accessibility strings.
    values = []
    for widget in [
        root,
        *root.findChildren(QLabel),
        *root.findChildren(QLineEdit),
        *root.findChildren(QAbstractButton),
        *root.findChildren(QGroupBox),
        *root.findChildren(QTableWidget),
        *root.findChildren(QListWidget),
    ]:
        if isinstance(widget, (QLabel, QLineEdit, QAbstractButton)):
            values.append(widget.text())
        if isinstance(widget, QGroupBox):
            values.append(widget.title())
        if isinstance(widget, QTableWidget):
            for row in range(widget.rowCount()):
                for col in range(widget.columnCount()):
                    item = widget.item(row, col)
                    if item is not None:
                        values.append(item.text())
        if isinstance(widget, QListWidget):
            values.extend(widget.item(i).text() for i in range(widget.count()))
        values.extend([widget.toolTip(), widget.accessibleName(), widget.accessibleDescription()])
    return "\n".join(values)
