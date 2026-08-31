"""Private projection of COMMITTED records; never recalculate during projection/recovery."""

from probability_calibration_tool.domain.dto import (
    HistoricalOddsAnalysis,
    HistoricalSideAnalysis,
    SubjectiveEstimate,
    SubjectiveOddsAnalysis,
    SubjectiveSideAnalysis,
)
from probability_calibration_tool.domain.enums import HistoryModelStatus
from probability_calibration_tool.domain.records import RoundAnalysisSnapshotRecord, RoundRecord

from .commands import CalculateCommand
from .enums import HistoricalDisplayState
from .errors import ApplicationInvariantError
from .views import LockedAnalysisView, NonnumericHistoryView, VisibleHistoryView


def locked_view(round: RoundRecord, snapshot: RoundAnalysisSnapshotRecord) -> LockedAnalysisView:
    if round.round_id != snapshot.round_id:
        raise ApplicationInvariantError("Snapshot identity does not match its round.")
    if round.history_exposed != (round.history_exposed_at is not None):
        raise ApplicationInvariantError("First exposure timestamp contradicts exposure flag.")
    if not round.reference_history:
        history = NonnumericHistoryView(HistoricalDisplayState.HIDDEN)
    elif snapshot.history_model_status != HistoryModelStatus.VALID:
        state = {
            HistoryModelStatus.NO_HISTORY: HistoricalDisplayState.NO_HISTORY,
            HistoryModelStatus.INSUFFICIENT: HistoricalDisplayState.INSUFFICIENT,
        }.get(snapshot.history_model_status)
        if state is None:
            raise ApplicationInvariantError("Unknown historical model state.")
        history = NonnumericHistoryView(state)
    else:
        if not round.history_exposed:
            raise ApplicationInvariantError(
                "Numerical history has no committed exposure authority."
            )
        required = [snapshot.history_probability, snapshot.history_lower, snapshot.history_upper]
        historical_sides = []
        for side in ("win", "lose"):
            values = [
                getattr(snapshot, f"historical_{side}_{field}")
                for field in (
                    "ev_center",
                    "ev_min",
                    "ev_max",
                    "ev_state",
                    "threshold_posterior_probability",
                )
            ]
            required.extend(values)
            historical_sides.append(HistoricalSideAnalysis(*values))
        if any(value is None for value in required) or not snapshot.history_statistically_ready:
            raise ApplicationInvariantError("Valid historical snapshot is incomplete.")
        history = VisibleHistoryView(
            state=HistoricalDisplayState.VISIBLE,
            wins=snapshot.history_wins,
            losses=snapshot.history_losses,
            sample_size=snapshot.history_sample_size,
            probability=snapshot.history_probability,
            lower=snapshot.history_lower,
            upper=snapshot.history_upper,
            model_version=snapshot.history_model_version,
            gate_version=snapshot.history_gate_version,
            data_through_at=snapshot.history_data_through_at,
            last_included_round_id=snapshot.last_included_historical_round_id,
            odds=HistoricalOddsAnalysis(*historical_sides),
            win_model_relation=snapshot.win_model_relation,
            lose_model_relation=snapshot.lose_model_relation,
        )
    subjective_sides = [
        SubjectiveSideAnalysis(
            *(
                getattr(snapshot, f"subjective_{side}_{field}")
                for field in ("ev_center", "ev_min", "ev_max", "ev_state", "margin_index")
            )
        )
        for side in ("win", "lose")
    ]
    return LockedAnalysisView(
        round_id=round.round_id,
        inputs=CalculateCommand(
            round.character_id,
            round.reference_history,
            round.p_h_raw,
            round.win_odds_raw,
            round.lose_odds_raw,
        ),
        regime_id=round.history_regime_id,
        created_at=round.created_at,
        calculated_at=round.calculated_at,
        revision_count=round.revision_count,
        history_exposed=round.history_exposed,
        history_exposed_at=round.history_exposed_at,
        subjective_independence_compromised=round.subjective_independence_compromised,
        subjective=SubjectiveEstimate(
            round.p_h_raw,
            snapshot.p_h_used,
            snapshot.subjective_probability,
            snapshot.subjective_p_min,
            snapshot.subjective_p_max,
            snapshot.subjective_logit_half_width,
            snapshot.subjective_model_version,
        ),
        subjective_odds=SubjectiveOddsAnalysis(
            snapshot.odds_analysis_version,
            snapshot.break_even_win,
            snapshot.break_even_lose_event,
            snapshot.break_even_lose_as_win_probability,
            snapshot.odds_combination_status,
            *subjective_sides,
        ),
        history=history,
    )
