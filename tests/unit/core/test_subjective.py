import math

import pytest

from probability_calibration_tool.core.errors import InvalidSubjectiveProbabilityError
from probability_calibration_tool.core.subjective import (
    compute_subjective_estimate,
    subjective_logit_half_width,
)


@pytest.mark.parametrize(
    ("raw", "used", "lower", "upper"),
    [
        (0, 1, 0.0066889632, 0.0149253731),
        (1, 1, 0.0066889632, 0.0149253731),
        (40, 40, 0.3076923077, 0.5000000000),
        (45, 45, 0.3529411765, 0.5510204082),
        (50, 50, 0.3660254038, 0.6339745962),
        (55, 55, 0.3793103448, 0.7096774194),
        (75, 75, 0.6000000000, 0.8571428571),
        (85, 85, 0.7391304348, 0.9189189189),
        (90, 90, 0.8432240348, 0.9377330360),
        (95, 95, 0.9313725490, 0.9637681159),
        (99, 99, 0.9880239521, 0.9916527546),
        (100, 99, 0.9880239521, 0.9916527546),
    ],
)
def test_subjective_golden_estimates(raw: int, used: int, lower: float, upper: float) -> None:
    estimate = compute_subjective_estimate(raw)
    assert estimate.p_h_raw == raw
    assert estimate.p_h_used == used
    assert estimate.p_min == pytest.approx(lower, abs=1e-10)
    assert estimate.p_max == pytest.approx(upper, abs=1e-10)


def test_zero_and_one_preserve_distinct_raw_values() -> None:
    zero = compute_subjective_estimate(0)
    one = compute_subjective_estimate(1)
    assert zero.p_h_raw == 0
    assert one.p_h_raw == 1
    assert (zero.probability, zero.p_min, zero.p_max) == (
        one.probability,
        one.p_min,
        one.p_max,
    )


def test_ninety_nine_and_one_hundred_preserve_distinct_raw_values() -> None:
    ninety_nine = compute_subjective_estimate(99)
    one_hundred = compute_subjective_estimate(100)
    assert ninety_nine.p_h_raw == 99
    assert one_hundred.p_h_raw == 100
    assert (ninety_nine.probability, ninety_nine.p_min, ninety_nine.p_max) == (
        one_hundred.probability,
        one_hundred.p_min,
        one_hundred.p_max,
    )


@pytest.mark.parametrize("raw", range(1, 100))
def test_subjective_interval_strictly_contains_probability(raw: int) -> None:
    estimate = compute_subjective_estimate(raw)
    assert 0.0 < estimate.p_min < estimate.probability < estimate.p_max < 1.0


@pytest.mark.parametrize("boundary", [0.45, 0.55, 0.85, 0.95])
def test_piecewise_half_width_is_continuous_at_boundaries(boundary: float) -> None:
    delta = 1e-10
    left = subjective_logit_half_width(boundary - delta)
    right = subjective_logit_half_width(boundary + delta)
    at_boundary = subjective_logit_half_width(boundary)
    assert left == pytest.approx(at_boundary, abs=1e-9)
    assert right == pytest.approx(at_boundary, abs=1e-9)


def test_half_width_at_ninety_nine_is_log_one_point_two() -> None:
    assert subjective_logit_half_width(0.99) == pytest.approx(math.log(1.2), abs=1e-15)


@pytest.mark.parametrize("raw", [True, False, 50.0, "50", None, -1, 101])
def test_invalid_subjective_raw_values_are_rejected(raw: object) -> None:
    with pytest.raises(InvalidSubjectiveProbabilityError):
        compute_subjective_estimate(raw)  # type: ignore[arg-type]
