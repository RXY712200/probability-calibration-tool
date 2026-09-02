"""Validation and parsing for mathematical core inputs."""

import math
import re
from typing import Never

from .errors import CoreValidationCode, InvalidOddsError

_ODDS_DECIMAL_PATTERN = re.compile(r"[0-9]+(?:\.[0-9]+)?\Z")


def _raise_invalid_odds(message: str, code: CoreValidationCode) -> Never:
    raise InvalidOddsError(message, code=code)


def validate_odds(odds: float) -> float:
    """Return a valid binary64 gross-return multiplier, or raise InvalidOddsError."""
    if isinstance(odds, bool) or not isinstance(odds, (int, float)):
        _raise_invalid_odds(
            "Odds must be a finite numeric multiplier.", CoreValidationCode.ODDS_NUMERIC
        )
    try:
        value = float(odds)
    except OverflowError:
        _raise_invalid_odds(
            "Odds must be representable as a finite binary64 value.",
            CoreValidationCode.ODDS_BINARY64,
        )
    if not math.isfinite(value) or value < 1.0:
        _raise_invalid_odds("Odds must be finite and at least 1.", CoreValidationCode.ODDS_RANGE)
    return value


def parse_odds_text(text: str) -> float:
    """Parse the final Calculate-level unsigned decimal odds syntax."""
    if not isinstance(text, str) or _ODDS_DECIMAL_PATTERN.fullmatch(text) is None:
        _raise_invalid_odds(
            "Odds must use unsigned decimal notation.", CoreValidationCode.ODDS_SYNTAX
        )
    return validate_odds(float(text))
