"""Presentation-only sources and mappings; no translator or settings ownership."""

import re
from collections import Counter

from PySide6.QtCore import QT_TRANSLATE_NOOP, QCoreApplication

from probability_calibration_tool.application.errors import ErrorCode
from probability_calibration_tool.domain.enums import (
    EvState,
    HistoryModelStatus,
    ModelRelation,
    OddsCombinationStatus,
)
from probability_calibration_tool.infrastructure.error_reporting import (
    ErrorPresentation,
    SafeErrorCode,
    WarningCode,
)

PLACEHOLDER = re.compile(r"%[1-9][0-9]*")


def template(context, source, *values):
    """Fixed NOOP-declared source; malformed pack messages fall back independently."""
    translated = QCoreApplication.translate(context, source)
    signature = Counter(PLACEHOLDER.findall(source))
    if not isinstance(translated, str) or Counter(PLACEHOLDER.findall(translated)) != signature:
        translated = source
    if any(int(token[1:]) > len(values) for token in signature):
        raise ValueError("Missing presentation template argument.")
    return PLACEHOLDER.sub(lambda match: str(values[int(match[0][1:]) - 1]), translated)


EV_SOURCES = {
    EvState.ROBUST_POSITIVE: QT_TRANSLATE_NOOP("DomainLabels", "Robust positive"),
    EvState.ROBUST_NEGATIVE: QT_TRANSLATE_NOOP("DomainLabels", "Robust negative"),
    EvState.CROSSES_THRESHOLD: QT_TRANSLATE_NOOP("DomainLabels", "Crosses threshold"),
}
ODDS_SOURCES = {
    OddsCombinationStatus.NORMAL_OVERLAP: QT_TRANSLATE_NOOP("DomainLabels", "Normal overlap"),
    OddsCombinationStatus.CRITICAL: QT_TRANSLATE_NOOP("DomainLabels", "Critical"),
    OddsCombinationStatus.DOUBLE_POSITIVE_WINDOW: QT_TRANSLATE_NOOP(
        "DomainLabels", "Double positive window"
    ),
}
RELATION_SOURCES = {
    ModelRelation.AGREEMENT_POSITIVE: QT_TRANSLATE_NOOP("DomainLabels", "Agreement positive"),
    ModelRelation.AGREEMENT_NEGATIVE: QT_TRANSLATE_NOOP("DomainLabels", "Agreement negative"),
    ModelRelation.CONFLICT: QT_TRANSLATE_NOOP("DomainLabels", "Conflict"),
    ModelRelation.UNCERTAIN: QT_TRANSLATE_NOOP("DomainLabels", "Uncertain"),
    ModelRelation.HISTORY_UNAVAILABLE: QT_TRANSLATE_NOOP("DomainLabels", "History unavailable"),
}
HISTORY_SOURCES = {
    HistoryModelStatus.NO_HISTORY: QT_TRANSLATE_NOOP("DomainLabels", "No history"),
    HistoryModelStatus.INSUFFICIENT: QT_TRANSLATE_NOOP("DomainLabels", "Insufficient"),
    HistoryModelStatus.VALID: QT_TRANSLATE_NOOP("DomainLabels", "Valid"),
}
DOMAIN_SOURCES = {
    EvState: EV_SOURCES,
    OddsCombinationStatus: ODDS_SOURCES,
    ModelRelation: RELATION_SOURCES,
    HistoryModelStatus: HISTORY_SOURCES,
}


def domain_label(value):
    return QCoreApplication.translate("DomainLabels", DOMAIN_SOURCES[type(value)][value])


def unavailable_label():
    return QCoreApplication.translate("DomainLabels", "N/A")


def result_label(result):
    if type(result) is not bool:
        raise TypeError("A result requires an explicit boolean.")
    return (
        QCoreApplication.translate("DomainLabels", "Win")
        if result
        else QCoreApplication.translate("DomainLabels", "Loss")
    )


def inclusion_label(include_character_history):
    if type(include_character_history) is not bool:
        raise TypeError("History inclusion requires an explicit boolean.")
    return (
        QCoreApplication.translate("DomainLabels", "Include")
        if include_character_history
        else QCoreApplication.translate("DomainLabels", "Exclude")
    )


CHARACTER_SOURCES = {
    1: QT_TRANSLATE_NOOP("Characters", "Isaac"),
    2: QT_TRANSLATE_NOOP("Characters", "Magdalene"),
    3: QT_TRANSLATE_NOOP("Characters", "Cain"),
    4: QT_TRANSLATE_NOOP("Characters", "Judas"),
    5: QT_TRANSLATE_NOOP("Characters", "???"),
    6: QT_TRANSLATE_NOOP("Characters", "Eve"),
    7: QT_TRANSLATE_NOOP("Characters", "Samson"),
    8: QT_TRANSLATE_NOOP("Characters", "Azazel"),
    9: QT_TRANSLATE_NOOP("Characters", "Lazarus"),
    10: QT_TRANSLATE_NOOP("Characters", "Eden"),
    11: QT_TRANSLATE_NOOP("Characters", "The Lost"),
    12: QT_TRANSLATE_NOOP("Characters", "Lilith"),
    13: QT_TRANSLATE_NOOP("Characters", "Keeper"),
    14: QT_TRANSLATE_NOOP("Characters", "Apollyon"),
    15: QT_TRANSLATE_NOOP("Characters", "The Forgotten"),
    16: QT_TRANSLATE_NOOP("Characters", "Bethany"),
    17: QT_TRANSLATE_NOOP("Characters", "Jacob & Esau"),
    18: QT_TRANSLATE_NOOP("Characters", "Tainted Isaac"),
    19: QT_TRANSLATE_NOOP("Characters", "Tainted Magdalene"),
    20: QT_TRANSLATE_NOOP("Characters", "Tainted Cain"),
    21: QT_TRANSLATE_NOOP("Characters", "Tainted Judas"),
    22: QT_TRANSLATE_NOOP("Characters", "Tainted ???"),
    23: QT_TRANSLATE_NOOP("Characters", "Tainted Eve"),
    24: QT_TRANSLATE_NOOP("Characters", "Tainted Samson"),
    25: QT_TRANSLATE_NOOP("Characters", "Tainted Azazel"),
    26: QT_TRANSLATE_NOOP("Characters", "Tainted Lazarus"),
    27: QT_TRANSLATE_NOOP("Characters", "Tainted Eden"),
    28: QT_TRANSLATE_NOOP("Characters", "Tainted Lost"),
    29: QT_TRANSLATE_NOOP("Characters", "Tainted Lilith"),
    30: QT_TRANSLATE_NOOP("Characters", "Tainted Keeper"),
    31: QT_TRANSLATE_NOOP("Characters", "Tainted Apollyon"),
    32: QT_TRANSLATE_NOOP("Characters", "Tainted Forgotten"),
    33: QT_TRANSLATE_NOOP("Characters", "Tainted Bethany"),
    34: QT_TRANSLATE_NOOP("Characters", "Tainted Jacob"),
}


def character_name(character_id):
    if type(character_id) is not int:
        raise TypeError("Character presentation requires an integer identity.")
    return QCoreApplication.translate("Characters", CHARACTER_SOURCES[character_id])


ERROR_SOURCES = {
    ErrorCode.ODDS_NUMERIC: QT_TRANSLATE_NOOP(
        "Errors", "Odds must be a finite numeric multiplier."
    ),
    ErrorCode.ODDS_BINARY64: QT_TRANSLATE_NOOP(
        "Errors", "Odds must be representable as a finite binary64 value."
    ),
    ErrorCode.ODDS_RANGE: QT_TRANSLATE_NOOP("Errors", "Odds must be finite and at least 1."),
    ErrorCode.ODDS_SYNTAX: QT_TRANSLATE_NOOP("Errors", "Odds must use unsigned decimal notation."),
    ErrorCode.RAW_PROBABILITY: QT_TRANSLATE_NOOP(
        "Errors", "Raw subjective probability must be an integer from 0 to 100."
    ),
    ErrorCode.BOOLEAN_REQUIRED: QT_TRANSLATE_NOOP(
        "Errors", "An explicit boolean choice is required."
    ),
    ErrorCode.REASON_TEXT: QT_TRANSLATE_NOOP("Errors", "Reason must be text."),
    ErrorCode.CORRECTION_REASON_REQUIRED: QT_TRANSLATE_NOOP(
        "Errors", "A nonempty correction reason is required."
    ),
    ErrorCode.CHARACTER_INTEGER: QT_TRANSLATE_NOOP("Errors", "Character ID must be an integer."),
    ErrorCode.CHARACTER_ACTIVE: QT_TRANSLATE_NOOP("Errors", "Choose an active character."),
    ErrorCode.CURRENT_STATE: QT_TRANSLATE_NOOP(
        "Errors", "Operation is not allowed in the current state."
    ),
    ErrorCode.INPUTS_MISSING: QT_TRANSLATE_NOOP(
        "Errors", "Prediction inputs have not been provided."
    ),
    ErrorCode.REVISION_CLOSED: QT_TRANSLATE_NOOP(
        "Errors", "Prediction revision is closed after result selection or recovery."
    ),
    ErrorCode.BUSY: QT_TRANSLATE_NOOP("Errors", "Another operation is in progress."),
    ErrorCode.CONFIRMATION_EXPIRED: QT_TRANSLATE_NOOP(
        "Errors", "Confirmation expired. Confirm the operation again."
    ),
    ErrorCode.SESSION_DISPOSED: QT_TRANSLATE_NOOP("Errors", "Desktop session has been disposed."),
    ErrorCode.NORMAL_UNAVAILABLE: QT_TRANSLATE_NOOP("Errors", "Normal operation is not available."),
    ErrorCode.HEALTHY_DRAFT_REQUIRED: QT_TRANSLATE_NOOP(
        "Errors", "Return to a healthy Draft before changing administrative data."
    ),
    ErrorCode.PENDING_CORRECTION: QT_TRANSLATE_NOOP(
        "Errors", "A pending round blocks historical correction."
    ),
    ErrorCode.BACKUP_EXPIRED: QT_TRANSLATE_NOOP(
        "Errors", "Backup selection expired. Reload and select again."
    ),
    ErrorCode.NO_PENDING_RECOVERY: QT_TRANSLATE_NOOP(
        "Errors", "No pending round is available for recovery."
    ),
    ErrorCode.PENDING_EXISTS: QT_TRANSLATE_NOOP(
        "Errors", "Finish or void the existing pending round first."
    ),
    ErrorCode.PENDING_REGIME: QT_TRANSLATE_NOOP(
        "Errors", "A pending round blocks all regime switching."
    ),
    ErrorCode.MULTIPLE_PENDING: QT_TRANSLATE_NOOP(
        "Errors", "Multiple pending rounds require recovery attention."
    ),
}
SAFE_ERROR_SOURCES = {
    SafeErrorCode.OPERATION_FAILED: QT_TRANSLATE_NOOP(
        "Errors", "The operation could not be completed."
    ),
    SafeErrorCode.RESTORE_RECOVERY_REQUIRED: QT_TRANSLATE_NOOP(
        "Errors", "Replacement requires emergency recovery."
    ),
    SafeErrorCode.RESTORE_NOT_REPLACED: QT_TRANSLATE_NOOP(
        "Errors", "Restore did not replace the live database."
    ),
    SafeErrorCode.RECENT_BACKUP_FAILED: QT_TRANSLATE_NOOP(
        "Errors", "Recent backup failed; saved main data was not reverted."
    ),
    SafeErrorCode.DAILY_BACKUP_FAILED: QT_TRANSLATE_NOOP(
        "Errors", "Daily backup failed; saved main data was not reverted."
    ),
}
WARNING_SOURCES = {
    WarningCode.STATS_REBUILT: QT_TRANSLATE_NOOP(
        "Errors", "Derived statistics were rebuilt from source records."
    ),
    WarningCode.BACKUP_OVER_RETENTION: QT_TRANSLATE_NOOP(
        "Errors", "Backup accepted; rotation stopped safely with possible over-retention."
    ),
    WarningCode.QUARANTINE_COPY_FAILED: QT_TRANSLATE_NOOP(
        "Errors", "Damaged-file quarantine copy failed; replacement may still proceed."
    ),
    WarningCode.MULTIPLE_PENDING: QT_TRANSLATE_NOOP(
        "Errors", "Multiple pending rounds require recovery attention."
    ),
}
BACKUP_CATEGORY_SOURCES = {
    "recent": QT_TRANSLATE_NOOP("Restore", "recent"),
    "daily": QT_TRANSLATE_NOOP("Restore", "daily"),
    "safety": QT_TRANSLATE_NOOP("Restore", "safety"),
}
BACKUP_REASON_SOURCES = {
    "pre_migration": QT_TRANSLATE_NOOP("Restore", "pre_migration"),
    "pre_restore": QT_TRANSLATE_NOOP("Restore", "pre_restore"),
    "pre_history_correction": QT_TRANSLATE_NOOP("Restore", "pre_history_correction"),
}
SEVERITY_SOURCES = {
    "information": QT_TRANSLATE_NOOP("AppShell", "Information"),
    "warning": QT_TRANSLATE_NOOP("AppShell", "Warning"),
    "error": QT_TRANSLATE_NOOP("AppShell", "Error"),
}


def expected_error(exc):
    """Render only explicitly public expected errors; internal codes are never a fallback."""
    return QCoreApplication.translate("Errors", ERROR_SOURCES[exc.code])


def is_public_expected_error(exc):
    try:
        return getattr(exc, "code", None) in ERROR_SOURCES
    except TypeError:
        return False


def error_with_id(message, error_id):
    return template("Errors", QT_TRANSLATE_NOOP("Errors", "%1 Error ID: %2"), message, error_id)


def safe_error(presentation):
    source = SAFE_ERROR_SOURCES.get(
        presentation.code, SAFE_ERROR_SOURCES[SafeErrorCode.OPERATION_FAILED]
    )
    return error_with_id(QCoreApplication.translate("Errors", source), presentation.error_id)


def severity_label(severity):
    return QCoreApplication.translate("AppShell", SEVERITY_SOURCES[severity])


def warning_text(warning):
    if isinstance(warning, ErrorPresentation):
        return safe_error(warning)
    source = WARNING_SOURCES.get(warning, SAFE_ERROR_SOURCES[SafeErrorCode.OPERATION_FAILED])
    return QCoreApplication.translate("Errors", source)


def warning_list(warnings):
    return "\n".join(warning_text(warning) for warning in warnings)


def backup_category(category):
    return QCoreApplication.translate("Restore", BACKUP_CATEGORY_SOURCES[category])


def backup_reason(reason):
    return QCoreApplication.translate("Restore", BACKUP_REASON_SOURCES[reason])
