import pytest

from probability_calibration_tool.core.errors import InvalidHistoryCountsError
from probability_calibration_tool.core.historical import compute_historical_estimate
from probability_calibration_tool.domain.enums import HistoryModelStatus


def test_no_history_golden_case() -> None:
    estimate = compute_historical_estimate(0, 0)
    assert estimate.status is HistoryModelStatus.NO_HISTORY
    assert estimate.probability is None
    assert estimate.lower is None
    assert estimate.upper is None
    assert not estimate.statistically_ready


@pytest.mark.parametrize(
    ("wins", "losses", "probability", "width", "ready"),
    [
        (1, 0, 0.75, 0.8528681027, False),
        (18, 2, 0.8809523810, 0.2624807693, False),
        (19, 1, 0.9285714286, 0.2053696037, True),
        (20, 0, 0.9761904762, 0.1166147364, True),
        (50, 50, 0.5, 0.1936520982, True),
    ],
)
def test_historical_golden_probability_width_and_gate(
    wins: int, losses: int, probability: float, width: float, ready: bool
) -> None:
    estimate = compute_historical_estimate(wins, losses)
    assert estimate.probability == pytest.approx(probability, abs=1e-10)
    assert estimate.lower is not None
    assert estimate.upper is not None
    assert estimate.upper - estimate.lower == pytest.approx(width, abs=1e-10)
    assert estimate.statistically_ready is ready
    assert estimate.status is (
        HistoryModelStatus.VALID if ready else HistoryModelStatus.INSUFFICIENT
    )


def test_one_zero_historical_interval_golden_case() -> None:
    estimate = compute_historical_estimate(1, 0)
    assert estimate.lower == pytest.approx(0.1467463163, abs=1e-10)
    assert estimate.upper == pytest.approx(0.9996144190, abs=1e-10)


def test_fifty_fifty_interval_is_symmetric() -> None:
    estimate = compute_historical_estimate(50, 50)
    assert estimate.probability == pytest.approx(0.5, abs=1e-15)
    assert estimate.lower is not None
    assert estimate.upper is not None
    assert estimate.lower == pytest.approx(0.4031739509, abs=1e-10)
    assert estimate.upper == pytest.approx(0.5968260491, abs=1e-10)
    assert estimate.lower + estimate.upper == pytest.approx(1.0, abs=1e-12)


def test_zero_one_is_valid_input_but_insufficient_history() -> None:
    estimate = compute_historical_estimate(0, 1)
    assert estimate.probability == pytest.approx(0.25, abs=1e-15)
    assert estimate.status is HistoryModelStatus.INSUFFICIENT


def test_gate_requires_minimum_sample_size_even_for_extreme_history() -> None:
    estimate = compute_historical_estimate(19, 0)
    assert estimate.sample_size == 19
    assert not estimate.statistically_ready


def test_gate_requires_interval_width_condition() -> None:
    estimate = compute_historical_estimate(18, 2)
    assert estimate.sample_size == 20
    assert not estimate.statistically_ready


def test_gate_accepts_when_both_conditions_hold() -> None:
    estimate = compute_historical_estimate(19, 1)
    assert estimate.statistically_ready


@pytest.mark.parametrize(
    ("wins", "losses"),
    [
        (True, 0),
        (0, False),
        (-1, 0),
        (0, -1),
        (1.0, 0),
        (0, "1"),
        (None, 0),
    ],
)
def test_invalid_history_counts_are_rejected(wins: object, losses: object) -> None:
    with pytest.raises(InvalidHistoryCountsError):
        compute_historical_estimate(wins, losses)  # type: ignore[arg-type]
