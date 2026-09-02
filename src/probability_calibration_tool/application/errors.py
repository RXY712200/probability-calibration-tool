"""Semantic application failures; unexpected persistence failures are not translated."""

from enum import StrEnum


class ErrorCode(StrEnum):
    UNKNOWN = "unknown"
    ODDS_NUMERIC = "odds_numeric"
    ODDS_BINARY64 = "odds_binary64"
    ODDS_RANGE = "odds_range"
    ODDS_SYNTAX = "odds_syntax"
    RAW_PROBABILITY = "raw_probability"
    BOOLEAN_REQUIRED = "boolean_required"
    REASON_TEXT = "reason_text"
    CORRECTION_REASON_REQUIRED = "correction_reason_required"
    CHARACTER_INTEGER = "character_integer"
    CHARACTER_ACTIVE = "character_active"
    CURRENT_STATE = "current_state"
    INPUTS_MISSING = "inputs_missing"
    REVISION_CLOSED = "revision_closed"
    BUSY = "busy"
    CONFIRMATION_EXPIRED = "confirmation_expired"
    SESSION_DISPOSED = "session_disposed"
    NORMAL_UNAVAILABLE = "normal_unavailable"
    HEALTHY_DRAFT_REQUIRED = "healthy_draft_required"
    PENDING_CORRECTION = "pending_correction"
    BACKUP_EXPIRED = "backup_expired"
    NO_PENDING_RECOVERY = "no_pending_recovery"
    PENDING_EXISTS = "pending_exists"
    PENDING_REGIME = "pending_regime"
    ROUND_NOT_FOUND = "round_not_found"
    ROUND_NOT_PENDING = "round_not_pending"
    ROUND_NOT_COMPLETED = "round_not_completed"
    MULTIPLE_PENDING = "multiple_pending"


class ApplicationError(Exception):
    default_code = ErrorCode.UNKNOWN

    def __init__(self, message, *, code=None):
        self.code = self.default_code if code is None else code
        super().__init__(message)


class BusinessRuleError(ApplicationError):
    pass


class InputValidationError(ApplicationError):
    def __init__(self, field: str, message: str, *, code=ErrorCode.UNKNOWN) -> None:
        self.field = field
        super().__init__(message, code=code)


class InvalidWorkflowTransitionError(BusinessRuleError):
    default_code = ErrorCode.CURRENT_STATE


class PendingRoundExistsError(BusinessRuleError):
    default_code = ErrorCode.PENDING_EXISTS


class RoundNotFoundError(BusinessRuleError):
    default_code = ErrorCode.ROUND_NOT_FOUND


class RoundNotPendingError(BusinessRuleError):
    default_code = ErrorCode.ROUND_NOT_PENDING


class RoundNotCompletedError(BusinessRuleError):
    default_code = ErrorCode.ROUND_NOT_COMPLETED


class MultiplePendingRoundsError(BusinessRuleError):
    default_code = ErrorCode.MULTIPLE_PENDING


class RegimeSwitchBlockedError(BusinessRuleError):
    default_code = ErrorCode.PENDING_REGIME


class CorrectionBlockedError(BusinessRuleError):
    default_code = ErrorCode.PENDING_CORRECTION


class ApplicationInvariantError(ApplicationError):
    pass
