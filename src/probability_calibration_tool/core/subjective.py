"""Frozen subjective-probability model from SPEC 1.0."""

from math import exp, log

from probability_calibration_tool.domain.dto import SubjectiveEstimate

from .errors import InvalidSubjectiveProbabilityError
from .model_specs import (
    LOG_FACTOR_HIGH,
    LOG_FACTOR_LOW,
    LOG_FACTOR_MAX,
    LOG_FACTOR_MID,
    SUBJECTIVE_HIGH_BREAKPOINT,
    SUBJECTIVE_LOW_BREAKPOINT,
    SUBJECTIVE_MAX_PROBABILITY,
    SUBJECTIVE_MID_HIGH_BREAKPOINT,
    SUBJECTIVE_MIN_PROBABILITY,
    SUBJECTIVE_MODEL_VERSION,
    SUBJECTIVE_VERY_HIGH_BREAKPOINT,
)


def subjective_logit_half_width(probability: float) -> float:
    """Return frozen d(p) for a valid mathematical subjective probability."""
    if not SUBJECTIVE_MIN_PROBABILITY <= probability <= SUBJECTIVE_MAX_PROBABILITY:
        raise InvalidSubjectiveProbabilityError("Mathematical probability must be in [0.01, 0.99].")
    if probability <= SUBJECTIVE_LOW_BREAKPOINT:
        return LOG_FACTOR_LOW
    if probability < SUBJECTIVE_MID_HIGH_BREAKPOINT:
        fraction = (probability - SUBJECTIVE_LOW_BREAKPOINT) / (
            SUBJECTIVE_MID_HIGH_BREAKPOINT - SUBJECTIVE_LOW_BREAKPOINT
        )
        return LOG_FACTOR_LOW + fraction * (LOG_FACTOR_MID - LOG_FACTOR_LOW)
    if probability <= SUBJECTIVE_HIGH_BREAKPOINT:
        return LOG_FACTOR_MID
    if probability < SUBJECTIVE_VERY_HIGH_BREAKPOINT:
        fraction = (probability - SUBJECTIVE_HIGH_BREAKPOINT) / (
            SUBJECTIVE_VERY_HIGH_BREAKPOINT - SUBJECTIVE_HIGH_BREAKPOINT
        )
        return LOG_FACTOR_MID - fraction * (LOG_FACTOR_MID - LOG_FACTOR_HIGH)
    fraction = (probability - SUBJECTIVE_VERY_HIGH_BREAKPOINT) / (
        SUBJECTIVE_MAX_PROBABILITY - SUBJECTIVE_VERY_HIGH_BREAKPOINT
    )
    return LOG_FACTOR_HIGH - fraction * (LOG_FACTOR_HIGH - LOG_FACTOR_MAX)


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + exp(-value))


def compute_subjective_estimate(p_h_raw: int) -> SubjectiveEstimate:
    """Compute the independent subjective estimate and uncertainty interval."""
    if isinstance(p_h_raw, bool) or not isinstance(p_h_raw, int) or not 0 <= p_h_raw <= 100:
        raise InvalidSubjectiveProbabilityError(
            "Raw subjective probability must be an integer from 0 to 100."
        )
    p_h_used = min(max(p_h_raw, 1), 99)
    probability = p_h_used / 100.0
    half_width = subjective_logit_half_width(probability)
    logit = log(probability / (1.0 - probability))
    return SubjectiveEstimate(
        p_h_raw=p_h_raw,
        p_h_used=p_h_used,
        probability=probability,
        p_min=_sigmoid(logit - half_width),
        p_max=_sigmoid(logit + half_width),
        logit_half_width=half_width,
        model_version=SUBJECTIVE_MODEL_VERSION,
    )
