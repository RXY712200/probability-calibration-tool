import pytest

from probability_calibration_tool.core.errors import InvalidOddsError
from probability_calibration_tool.core.validation import parse_odds_text, validate_odds


@pytest.mark.parametrize(
    ("text", "expected"),
    [("1", 1.0), ("16", 16.0), ("1.01", 1.01), ("2.500", 2.5), ("0002.50", 2.5)],
)
def test_parse_odds_text_accepts_frozen_decimal_syntax(text: str, expected: float) -> None:
    assert parse_odds_text(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "1e3",
        "1E3",
        "NaN",
        "nan",
        "inf",
        "Infinity",
        "-infinity",
        "-2",
        "+2",
        "1,5",
        "abc",
        "1..2",
        "1.",
        ".5",
        "",
        " ",
        " 2",
        "2 ",
        "１２",
        "0",
        "0.99",
    ],
)
def test_parse_odds_text_rejects_invalid_syntax_or_values(text: str) -> None:
    with pytest.raises(InvalidOddsError):
        parse_odds_text(text)


@pytest.mark.parametrize(
    "odds",
    [
        True,
        False,
        pytest.param(10**10000, id="oversized-int"),
        float("nan"),
        float("inf"),
        -float("inf"),
        0,
        0.99,
        "2",
        None,
    ],
)
def test_numeric_odds_validation_rejects_invalid_values(odds: object) -> None:
    with pytest.raises(InvalidOddsError):
        validate_odds(odds)  # type: ignore[arg-type]


@pytest.mark.parametrize("odds", [1, 2, 1.01, 2.5])
def test_numeric_odds_validation_accepts_ordinary_ints_and_floats(odds: float) -> None:
    assert validate_odds(odds) == float(odds)
