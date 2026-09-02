"""Semantic validation errors for the pure math core."""

from enum import StrEnum


class CoreValidationCode(StrEnum):
    UNKNOWN = "unknown"
    ODDS_NUMERIC = "odds_numeric"
    ODDS_BINARY64 = "odds_binary64"
    ODDS_RANGE = "odds_range"
    ODDS_SYNTAX = "odds_syntax"
    RAW_PROBABILITY = "raw_probability"


class CoreValidationError(ValueError):
    """Base error for invalid mathematical-core input."""

    def __init__(self, message, *, code=CoreValidationCode.UNKNOWN):
        self.code = code
        super().__init__(message)


class InvalidSubjectiveProbabilityError(CoreValidationError):
    """Raised when a raw subjective probability is invalid."""


class InvalidHistoryCountsError(CoreValidationError):
    """Raised when historical win/loss counts are invalid."""


class InvalidOddsError(CoreValidationError):
    """Raised when an odds value or odds string is invalid."""
