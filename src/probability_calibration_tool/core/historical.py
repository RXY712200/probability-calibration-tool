"""Jeffreys historical estimate and deterministic readiness gate."""

from scipy.stats import beta

from probability_calibration_tool.domain.dto import HistoricalEstimate
from probability_calibration_tool.domain.enums import HistoryModelStatus

from .errors import InvalidHistoryCountsError
from .model_specs import (
    HISTORY_CREDIBLE_LEVEL,
    HISTORY_GATE_VERSION,
    HISTORY_MAX_INTERVAL_WIDTH,
    HISTORY_MIN_SAMPLE_SIZE,
    HISTORY_MODEL_VERSION,
    JEFFREYS_ALPHA,
    JEFFREYS_BETA,
)


def _validate_count(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InvalidHistoryCountsError(f"{name} must be a non-negative integer.")


def compute_historical_estimate(wins: int, losses: int) -> HistoricalEstimate:
    """Compute a Jeffreys posterior estimate without any external state."""
    _validate_count(wins, "wins")
    _validate_count(losses, "losses")
    sample_size = wins + losses
    if sample_size == 0:
        return HistoricalEstimate(
            wins=wins,
            losses=losses,
            sample_size=0,
            status=HistoryModelStatus.NO_HISTORY,
            statistically_ready=False,
            probability=None,
            lower=None,
            upper=None,
            model_version=HISTORY_MODEL_VERSION,
            gate_version=HISTORY_GATE_VERSION,
        )
    alpha = wins + JEFFREYS_ALPHA
    beta_parameter = losses + JEFFREYS_BETA
    tail_probability = (1.0 - HISTORY_CREDIBLE_LEVEL) / 2.0
    lower = float(beta.ppf(tail_probability, alpha, beta_parameter))
    upper = float(beta.ppf(1.0 - tail_probability, alpha, beta_parameter))
    ready = sample_size >= HISTORY_MIN_SAMPLE_SIZE and upper - lower <= HISTORY_MAX_INTERVAL_WIDTH
    return HistoricalEstimate(
        wins=wins,
        losses=losses,
        sample_size=sample_size,
        status=HistoryModelStatus.VALID if ready else HistoryModelStatus.INSUFFICIENT,
        statistically_ready=ready,
        probability=(wins + JEFFREYS_ALPHA) / (sample_size + JEFFREYS_ALPHA + JEFFREYS_BETA),
        lower=lower,
        upper=upper,
        model_version=HISTORY_MODEL_VERSION,
        gate_version=HISTORY_GATE_VERSION,
    )
