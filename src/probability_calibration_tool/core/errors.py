"""Semantic validation errors for the pure math core."""


class CoreValidationError(ValueError):
    """Base error for invalid mathematical-core input."""


class InvalidSubjectiveProbabilityError(CoreValidationError):
    """Raised when a raw subjective probability is invalid."""


class InvalidHistoryCountsError(CoreValidationError):
    """Raised when historical win/loss counts are invalid."""


class InvalidOddsError(CoreValidationError):
    """Raised when an odds value or odds string is invalid."""
