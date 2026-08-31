from enum import StrEnum


class WorkflowState(StrEnum):
    DRAFT = "draft"
    CALCULATING = "calculating"
    PENDING_LOCKED = "pending_locked"
    PENDING_EDIT = "pending_edit"
    CONFIRM_SAVE = "confirm_save"
    COMPLETING = "completing"
    RECOVERY = "recovery"
    RECOVERY_ERROR = "recovery_error"
    COMPLETED_NOTICE = "completed_notice"


class HistoricalDisplayState(StrEnum):
    HIDDEN = "hidden"
    NO_HISTORY = "no_history"
    INSUFFICIENT = "insufficient"
    VISIBLE = "visible"


class RecoveryState(StrEnum):
    NONE = "none"
    RECOVERABLE = "recoverable"
