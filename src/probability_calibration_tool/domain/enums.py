"""Enums used by the deterministic mathematical core."""

from enum import Enum


class HistoryModelStatus(str, Enum):
    NO_HISTORY = "no_history"
    INSUFFICIENT = "insufficient"
    VALID = "valid"


class EvState(str, Enum):
    ROBUST_POSITIVE = "robust_positive"
    ROBUST_NEGATIVE = "robust_negative"
    CROSSES_THRESHOLD = "crosses_threshold"


class OddsCombinationStatus(str, Enum):
    NORMAL_OVERLAP = "normal_overlap"
    CRITICAL = "critical"
    DOUBLE_POSITIVE_WINDOW = "double_positive_window"


class ModelRelation(str, Enum):
    AGREEMENT_POSITIVE = "agreement_positive"
    AGREEMENT_NEGATIVE = "agreement_negative"
    CONFLICT = "conflict"
    UNCERTAIN = "uncertain"
    HISTORY_UNAVAILABLE = "history_unavailable"


class RoundStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    VOIDED = "voided"
