"""Pure odds, expected-value, posterior, and relation calculations."""

import math

from scipy.stats import beta

from probability_calibration_tool.domain.dto import (
    HistoricalEstimate,
    HistoricalOddsAnalysis,
    HistoricalSideAnalysis,
    SubjectiveEstimate,
    SubjectiveOddsAnalysis,
    SubjectiveSideAnalysis,
)
from probability_calibration_tool.domain.enums import (
    EvState,
    HistoryModelStatus,
    ModelRelation,
    OddsCombinationStatus,
)

from .model_specs import (
    FLOAT_EPSILON,
    JEFFREYS_ALPHA,
    JEFFREYS_BETA,
    ODDS_ANALYSIS_VERSION,
)
from .validation import validate_odds


def classify_ev_state(ev_min: float, ev_max: float) -> EvState:
    """Classify an EV interval using the frozen business epsilon."""
    if ev_min > FLOAT_EPSILON:
        return EvState.ROBUST_POSITIVE
    if ev_max < -FLOAT_EPSILON:
        return EvState.ROBUST_NEGATIVE
    return EvState.CROSSES_THRESHOLD


def classify_odds_combination(win_odds: float, lose_odds: float) -> OddsCombinationStatus:
    """Classify the two-sided gross-return odds geometry."""
    win_odds = validate_odds(win_odds)
    lose_odds = validate_odds(lose_odds)
    total_inverse_odds = 1.0 / win_odds + 1.0 / lose_odds
    if abs(total_inverse_odds - 1.0) <= FLOAT_EPSILON:
        return OddsCombinationStatus.CRITICAL
    if total_inverse_odds > 1.0 + FLOAT_EPSILON:
        return OddsCombinationStatus.NORMAL_OVERLAP
    return OddsCombinationStatus.DOUBLE_POSITIVE_WINDOW


def _logit(probability: float) -> float:
    return math.log(probability / (1.0 - probability))


def _subjective_win_analysis(subjective: SubjectiveEstimate, odds: float) -> SubjectiveSideAnalysis:
    ev_center = subjective.probability * odds - 1.0
    ev_min = subjective.p_min * odds - 1.0
    ev_max = subjective.p_max * odds - 1.0
    margin = (
        None
        if odds == 1.0
        else (_logit(subjective.probability) - _logit(1.0 / odds)) / subjective.logit_half_width
    )
    return SubjectiveSideAnalysis(
        ev_center, ev_min, ev_max, classify_ev_state(ev_min, ev_max), margin
    )


def _subjective_lose_analysis(
    subjective: SubjectiveEstimate, odds: float
) -> SubjectiveSideAnalysis:
    ev_center = (1.0 - subjective.probability) * odds - 1.0
    ev_min = (1.0 - subjective.p_max) * odds - 1.0
    ev_max = (1.0 - subjective.p_min) * odds - 1.0
    margin = (
        None
        if odds == 1.0
        else (_logit(1.0 - subjective.probability) - _logit(1.0 / odds))
        / subjective.logit_half_width
    )
    return SubjectiveSideAnalysis(
        ev_center, ev_min, ev_max, classify_ev_state(ev_min, ev_max), margin
    )


def analyze_subjective_odds(
    subjective: SubjectiveEstimate, win_odds: float, lose_odds: float
) -> SubjectiveOddsAnalysis:
    """Analyze independent subjective EVs and robust-margin indices."""
    if not isinstance(subjective, SubjectiveEstimate):
        raise TypeError("subjective must be a SubjectiveEstimate.")
    win_odds = validate_odds(win_odds)
    lose_odds = validate_odds(lose_odds)
    return SubjectiveOddsAnalysis(
        analysis_version=ODDS_ANALYSIS_VERSION,
        break_even_win=1.0 / win_odds,
        break_even_lose_event=1.0 / lose_odds,
        break_even_lose_as_win_probability=1.0 - 1.0 / lose_odds,
        odds_combination_status=classify_odds_combination(win_odds, lose_odds),
        win=_subjective_win_analysis(subjective, win_odds),
        lose=_subjective_lose_analysis(subjective, lose_odds),
    )


def _clamp_probability(value: float) -> float:
    return min(1.0, max(0.0, value))


def _historical_win_analysis(history: HistoricalEstimate, odds: float) -> HistoricalSideAnalysis:
    assert (
        history.probability is not None and history.lower is not None and history.upper is not None
    )
    ev_center = history.probability * odds - 1.0
    ev_min = history.lower * odds - 1.0
    ev_max = history.upper * odds - 1.0
    posterior = 1.0 - float(
        beta.cdf(1.0 / odds, history.wins + JEFFREYS_ALPHA, history.losses + JEFFREYS_BETA)
    )
    return HistoricalSideAnalysis(
        ev_center, ev_min, ev_max, classify_ev_state(ev_min, ev_max), _clamp_probability(posterior)
    )


def _historical_lose_analysis(history: HistoricalEstimate, odds: float) -> HistoricalSideAnalysis:
    assert (
        history.probability is not None and history.lower is not None and history.upper is not None
    )
    ev_center = (1.0 - history.probability) * odds - 1.0
    ev_min = (1.0 - history.upper) * odds - 1.0
    ev_max = (1.0 - history.lower) * odds - 1.0
    posterior = float(
        beta.cdf(1.0 - 1.0 / odds, history.wins + JEFFREYS_ALPHA, history.losses + JEFFREYS_BETA)
    )
    return HistoricalSideAnalysis(
        ev_center, ev_min, ev_max, classify_ev_state(ev_min, ev_max), _clamp_probability(posterior)
    )


def analyze_historical_odds(
    history: HistoricalEstimate, win_odds: float, lose_odds: float
) -> HistoricalOddsAnalysis | None:
    """Analyze historical EV only when the historical model passes the frozen gate."""
    if not isinstance(history, HistoricalEstimate):
        raise TypeError("history must be a HistoricalEstimate.")
    if history.status is not HistoryModelStatus.VALID:
        return None
    win_odds = validate_odds(win_odds)
    lose_odds = validate_odds(lose_odds)
    return HistoricalOddsAnalysis(
        win=_historical_win_analysis(history, win_odds),
        lose=_historical_lose_analysis(history, lose_odds),
    )


def classify_model_relation(
    subjective_state: EvState, historical_state: EvState | None
) -> ModelRelation:
    """Classify independent subjective and valid historical EV states without fusing them."""
    if not isinstance(subjective_state, EvState):
        raise TypeError("subjective_state must be an EvState.")
    if historical_state is None:
        return ModelRelation.HISTORY_UNAVAILABLE
    if not isinstance(historical_state, EvState):
        raise TypeError("historical_state must be an EvState or None.")
    if EvState.CROSSES_THRESHOLD in (subjective_state, historical_state):
        return ModelRelation.UNCERTAIN
    if subjective_state is historical_state is EvState.ROBUST_POSITIVE:
        return ModelRelation.AGREEMENT_POSITIVE
    if subjective_state is historical_state is EvState.ROBUST_NEGATIVE:
        return ModelRelation.AGREEMENT_NEGATIVE
    return ModelRelation.CONFLICT
