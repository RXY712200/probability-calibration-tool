import pytest

from probability_calibration_tool.core.errors import InvalidOddsError
from probability_calibration_tool.core.ev import (
    analyze_historical_odds,
    analyze_subjective_odds,
    classify_ev_state,
    classify_model_relation,
    classify_odds_combination,
)
from probability_calibration_tool.core.historical import compute_historical_estimate
from probability_calibration_tool.core.model_specs import FLOAT_EPSILON
from probability_calibration_tool.core.subjective import compute_subjective_estimate
from probability_calibration_tool.domain.enums import (
    EvState,
    ModelRelation,
    OddsCombinationStatus,
)


def test_subjective_win_margin_matches_interval_boundaries() -> None:
    subjective = compute_subjective_estimate(60)
    at_lower = analyze_subjective_odds(subjective, 1.0 / subjective.p_min, 2.0)
    at_upper = analyze_subjective_odds(subjective, 1.0 / subjective.p_max, 2.0)
    assert at_lower.win.robust_margin_index == pytest.approx(1.0, abs=1e-12)
    assert at_upper.win.robust_margin_index == pytest.approx(-1.0, abs=1e-12)


def test_subjective_lose_margin_matches_interval_boundaries() -> None:
    subjective = compute_subjective_estimate(60)
    at_lower = analyze_subjective_odds(subjective, 2.0, 1.0 / (1.0 - subjective.p_max))
    at_upper = analyze_subjective_odds(subjective, 2.0, 1.0 / (1.0 - subjective.p_min))
    assert at_lower.lose.robust_margin_index == pytest.approx(1.0, abs=1e-12)
    assert at_upper.lose.robust_margin_index == pytest.approx(-1.0, abs=1e-12)


@pytest.mark.parametrize(
    ("ev_min", "ev_max", "expected"),
    [
        (0.0, 0.1, EvState.CROSSES_THRESHOLD),
        (0.5 * FLOAT_EPSILON, 0.1, EvState.CROSSES_THRESHOLD),
        (2.0 * FLOAT_EPSILON, 0.1, EvState.ROBUST_POSITIVE),
        (-0.1, 0.0, EvState.CROSSES_THRESHOLD),
        (-0.1, -0.5 * FLOAT_EPSILON, EvState.CROSSES_THRESHOLD),
        (-0.1, -2.0 * FLOAT_EPSILON, EvState.ROBUST_NEGATIVE),
    ],
)
def test_ev_epsilon_boundaries(ev_min: float, ev_max: float, expected: EvState) -> None:
    assert classify_ev_state(ev_min, ev_max) is expected


@pytest.mark.parametrize(
    ("win_odds", "lose_odds", "expected"),
    [
        (2.0, 2.0, OddsCombinationStatus.CRITICAL),
        (1.8, 1.8, OddsCombinationStatus.NORMAL_OVERLAP),
        (2.2, 2.2, OddsCombinationStatus.DOUBLE_POSITIVE_WINDOW),
        (2.0, 1.0 / (0.5 + 0.5 * FLOAT_EPSILON), OddsCombinationStatus.CRITICAL),
    ],
)
def test_odds_combination_classification(
    win_odds: float, lose_odds: float, expected: OddsCombinationStatus
) -> None:
    assert classify_odds_combination(win_odds, lose_odds) is expected


def test_one_odds_keeps_ev_and_sets_margin_to_none() -> None:
    analysis = analyze_subjective_odds(compute_subjective_estimate(50), 1.0, 1.0)
    assert analysis.win.robust_margin_index is None
    assert analysis.lose.robust_margin_index is None
    assert analysis.break_even_win == 1.0
    assert analysis.break_even_lose_event == 1.0


def test_invalid_history_returns_no_historical_odds_analysis() -> None:
    assert analyze_historical_odds(compute_historical_estimate(1, 0), 2.0, 2.0) is None


@pytest.mark.parametrize(
    "history",
    [
        compute_historical_estimate(0, 0),
        compute_historical_estimate(1, 0),
    ],
)
def test_non_valid_history_returns_none_before_odds_validation(history: object) -> None:
    assert analyze_historical_odds(history, float("nan"), 0.5) is None  # type: ignore[arg-type]


def test_valid_history_rejects_invalid_odds() -> None:
    with pytest.raises(InvalidOddsError):
        analyze_historical_odds(compute_historical_estimate(19, 1), float("nan"), 2.0)


def test_valid_history_with_valid_odds_performs_analysis() -> None:
    assert analyze_historical_odds(compute_historical_estimate(19, 1), 2.0, 2.0) is not None


def test_historical_posterior_symmetry_direction() -> None:
    analysis = analyze_historical_odds(compute_historical_estimate(50, 50), 2.0, 2.0)
    assert analysis is not None
    assert analysis.win.threshold_posterior_probability == pytest.approx(0.5, abs=1e-12)
    assert analysis.lose.threshold_posterior_probability == pytest.approx(0.5, abs=1e-12)


@pytest.mark.parametrize(
    ("subjective_state", "historical_state", "expected"),
    [
        (EvState.ROBUST_POSITIVE, EvState.ROBUST_POSITIVE, ModelRelation.AGREEMENT_POSITIVE),
        (EvState.ROBUST_NEGATIVE, EvState.ROBUST_NEGATIVE, ModelRelation.AGREEMENT_NEGATIVE),
        (EvState.ROBUST_POSITIVE, EvState.ROBUST_NEGATIVE, ModelRelation.CONFLICT),
        (EvState.ROBUST_NEGATIVE, EvState.ROBUST_POSITIVE, ModelRelation.CONFLICT),
        (EvState.CROSSES_THRESHOLD, EvState.ROBUST_POSITIVE, ModelRelation.UNCERTAIN),
        (EvState.ROBUST_POSITIVE, EvState.CROSSES_THRESHOLD, ModelRelation.UNCERTAIN),
        (EvState.CROSSES_THRESHOLD, EvState.ROBUST_NEGATIVE, ModelRelation.UNCERTAIN),
        (EvState.ROBUST_NEGATIVE, EvState.CROSSES_THRESHOLD, ModelRelation.UNCERTAIN),
        (EvState.CROSSES_THRESHOLD, EvState.CROSSES_THRESHOLD, ModelRelation.UNCERTAIN),
        (EvState.ROBUST_POSITIVE, None, ModelRelation.HISTORY_UNAVAILABLE),
    ],
)
def test_model_relation_classification(
    subjective_state: EvState, historical_state: EvState | None, expected: ModelRelation
) -> None:
    assert classify_model_relation(subjective_state, historical_state) is expected
