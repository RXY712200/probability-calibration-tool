"""Public views: non-visible history structurally contains no numeric payload."""

from dataclasses import dataclass
from datetime import datetime

from probability_calibration_tool.domain.dto import (
    HistoricalOddsAnalysis,
    SubjectiveEstimate,
    SubjectiveOddsAnalysis,
)
from probability_calibration_tool.domain.enums import ModelRelation, RoundStatus

from .commands import CalculateCommand
from .enums import HistoricalDisplayState, RecoveryState


@dataclass(frozen=True)
class NonnumericHistoryView:
    state: HistoricalDisplayState


@dataclass(frozen=True)
class VisibleHistoryView:
    state: HistoricalDisplayState
    wins: int
    losses: int
    sample_size: int
    probability: float
    lower: float
    upper: float
    model_version: int
    gate_version: int
    data_through_at: datetime
    last_included_round_id: str | None
    odds: HistoricalOddsAnalysis
    win_model_relation: ModelRelation
    lose_model_relation: ModelRelation


@dataclass(frozen=True)
class LockedAnalysisView:
    round_id: str
    inputs: CalculateCommand
    regime_id: str
    created_at: datetime
    calculated_at: datetime
    revision_count: int
    history_exposed: bool
    history_exposed_at: datetime | None
    subjective_independence_compromised: bool
    subjective: SubjectiveEstimate
    subjective_odds: SubjectiveOddsAnalysis
    history: NonnumericHistoryView | VisibleHistoryView


@dataclass(frozen=True)
class RecoveryView:
    state: RecoveryState
    round_id: str | None


@dataclass(frozen=True)
class CompletionResult:
    round_id: str
    status: RoundStatus
    result: bool
    include_character_history: bool
    completed_at: datetime


@dataclass(frozen=True)
class VoidResult:
    round_id: str
    status: RoundStatus
    voided_at: datetime
    reason: str | None


@dataclass(frozen=True)
class RegimeSummaryView:
    character_id: int
    regime_id: str
    regime_number: int
    started_at: datetime
    reason: str | None
    included_sample_count: int


@dataclass(frozen=True)
class MaintenanceCharacterView:
    character_id: int
    display_name: str
    active_regime_number: int
    regime_started_at: datetime
    regime_reason: str | None
    included_sample_count: int


@dataclass(frozen=True)
class CorrectionResult:
    original_round_id: str
    replacement_round_id: str
    corrected_at: datetime
    result: bool
    include_character_history: bool
