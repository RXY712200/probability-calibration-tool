"""Typed persistence records with no SQL or workflow behavior."""

from dataclasses import dataclass
from datetime import datetime

from .enums import EvState, HistoryModelStatus, ModelRelation, OddsCombinationStatus, RoundStatus


@dataclass(frozen=True)
class CharacterRecord:
    character_id: int
    internal_code: str
    display_name: str
    tainted: bool
    pair_row: int
    active: bool


@dataclass(frozen=True)
class HistoryRegimeRecord:
    regime_id: str
    character_id: int
    regime_number: int
    started_at: datetime
    ended_at: datetime | None
    active: bool
    reason: str | None


@dataclass(frozen=True)
class RoundRecord:
    round_id: str
    created_at: datetime
    calculated_at: datetime
    last_updated_at: datetime
    completed_at: datetime | None
    voided_at: datetime | None
    void_reason: str | None
    character_id: int
    history_regime_id: str
    reference_history: bool
    p_h_raw: int
    win_odds_raw: str
    lose_odds_raw: str
    win_odds: float
    lose_odds: float
    status: RoundStatus
    revision_count: int
    result: bool | None
    include_character_history: bool | None
    history_exposed: bool
    history_exposed_at: datetime | None
    subjective_independence_compromised: bool
    supersedes_round_id: str | None


@dataclass(frozen=True)
class RoundAnalysisSnapshotRecord:
    round_id: str
    p_h_used: int
    subjective_probability: float
    subjective_p_min: float
    subjective_p_max: float
    subjective_logit_half_width: float
    subjective_model_version: int
    odds_analysis_version: int
    break_even_win: float
    break_even_lose_event: float
    break_even_lose_as_win_probability: float
    subjective_win_ev_center: float
    subjective_win_ev_min: float
    subjective_win_ev_max: float
    subjective_win_margin_index: float | None
    subjective_win_ev_state: EvState
    subjective_lose_ev_center: float
    subjective_lose_ev_min: float
    subjective_lose_ev_max: float
    subjective_lose_margin_index: float | None
    subjective_lose_ev_state: EvState
    odds_combination_status: OddsCombinationStatus
    history_model_status: HistoryModelStatus
    history_statistically_ready: bool
    history_wins: int
    history_losses: int
    history_sample_size: int
    history_model_version: int
    history_gate_version: int
    history_probability: float | None
    history_lower: float | None
    history_upper: float | None
    history_data_through_at: datetime
    last_included_historical_round_id: str | None
    historical_win_ev_center: float | None
    historical_win_ev_min: float | None
    historical_win_ev_max: float | None
    historical_win_ev_state: EvState | None
    historical_win_threshold_posterior_probability: float | None
    historical_lose_ev_center: float | None
    historical_lose_ev_min: float | None
    historical_lose_ev_max: float | None
    historical_lose_ev_state: EvState | None
    historical_lose_threshold_posterior_probability: float | None
    win_model_relation: ModelRelation
    lose_model_relation: ModelRelation


@dataclass(frozen=True)
class CharacterStatsRecord:
    character_id: int
    regime_id: str
    included_games: int
    wins: int
    losses: int
    last_included_round_id: str | None
    updated_at: datetime
    stats_version: int


@dataclass(frozen=True)
class MetaRecord:
    key: str
    value: str
    updated_at: datetime
