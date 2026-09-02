from enum import Enum

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMessageBox

from probability_calibration_tool.application.enums import WorkflowState as S


class CloseDecision(Enum):
    ACCEPT = "accept"
    CONFIRM_EDITS = "confirm_edits"
    CONFIRM_CHOICES = "confirm_choices"
    IGNORE = "ignore"


def close_decision(state, choices, *, operation_active=False):
    if operation_active or state in (S.CALCULATING, S.COMPLETING):
        return CloseDecision.IGNORE
    if state == S.PENDING_EDIT:
        return CloseDecision.CONFIRM_EDITS
    if state == S.CONFIRM_SAVE or (
        state == S.PENDING_LOCKED and any(value is not None for value in choices)
    ):
        return CloseDecision.CONFIRM_CHOICES
    return CloseDecision.ACCEPT


def confirm_close(parent, decision):
    message = (
        QCoreApplication.translate(
            "Round",
            "Candidate edits will be lost. The previously committed pending prediction remains safe.",
        )
        if decision == CloseDecision.CONFIRM_EDITS
        else QCoreApplication.translate(
            "Round",
            "Post-run choices are not persisted. The pending prediction remains recoverable.",
        )
    )
    box = QMessageBox(parent)
    box.setWindowTitle(QCoreApplication.translate("Round", "Close pending round"))
    box.setText(message)
    cancel = box.addButton(
        QCoreApplication.translate("Round", "Cancel"), QMessageBox.ButtonRole.RejectRole
    )
    close = box.addButton(
        QCoreApplication.translate("Round", "Close Anyway"), QMessageBox.ButtonRole.AcceptRole
    )
    box.setDefaultButton(cancel)
    box.exec()
    return box.clickedButton() is close
