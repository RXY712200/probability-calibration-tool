"""Immutable result types for pure probability calculations."""

from dataclasses import dataclass

from .enums import EvState, HistoryModelStatus, OddsCombinationStatus


@dataclass(frozen=True)
class SubjectiveEstimate:
    p_h_raw: int
    p_h_used: int
    probability: float
    p_min: float
    p_max: float
    logit_half_width: float
    model_version: int


@dataclass(frozen=True)
class HistoricalEstimate:
    wins: int
    losses: int
    sample_size: int
    status: HistoryModelStatus
    statistically_ready: bool
    probability: float | None
    lower: float | None
    upper: float | None
    model_version: int
    gate_version: int


@dataclass(frozen=True)
class SubjectiveSideAnalysis:
    ev_center: float
    ev_min: float
    ev_max: float
    ev_state: EvState
    robust_margin_index: float | None


@dataclass(frozen=True)
class SubjectiveOddsAnalysis:
    analysis_version: int
    break_even_win: float
    break_even_lose_event: float
    break_even_lose_as_win_probability: float
    odds_combination_status: OddsCombinationStatus
    win: SubjectiveSideAnalysis
    lose: SubjectiveSideAnalysis


@dataclass(frozen=True)
class HistoricalSideAnalysis:
    ev_center: float
    ev_min: float
    ev_max: float
    ev_state: EvState
    threshold_posterior_probability: float


@dataclass(frozen=True)
class HistoricalOddsAnalysis:
    win: HistoricalSideAnalysis
    lose: HistoricalSideAnalysis
