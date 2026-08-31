"""Semantic application failures; unexpected persistence failures are not translated."""


class ApplicationError(Exception):
    pass


class BusinessRuleError(ApplicationError):
    pass


class InputValidationError(ApplicationError):
    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(message)


class InvalidWorkflowTransitionError(BusinessRuleError):
    pass


class PendingRoundExistsError(BusinessRuleError):
    pass


class RoundNotFoundError(BusinessRuleError):
    pass


class RoundNotPendingError(BusinessRuleError):
    pass


class RoundNotCompletedError(BusinessRuleError):
    pass


class MultiplePendingRoundsError(BusinessRuleError):
    pass


class RegimeSwitchBlockedError(BusinessRuleError):
    pass


class CorrectionBlockedError(BusinessRuleError):
    pass


class ApplicationInvariantError(ApplicationError):
    pass
