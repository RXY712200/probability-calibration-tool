"""Internal Core composition and complete snapshot assembly, never a public service view."""

from dataclasses import dataclass
from datetime import datetime

from probability_calibration_tool import core
from probability_calibration_tool.core.errors import CoreValidationCode, CoreValidationError
from probability_calibration_tool.domain.dto import SubjectiveEstimate
from probability_calibration_tool.domain.records import RoundAnalysisSnapshotRecord, RoundRecord

from ._checks import require_bool
from .commands import CalculateCommand
from .errors import ApplicationInvariantError, ErrorCode, InputValidationError

CORE_INPUT_ERRORS = {
    CoreValidationCode.ODDS_NUMERIC: (
        ErrorCode.ODDS_NUMERIC,
        "Odds must be a finite numeric multiplier.",
    ),
    CoreValidationCode.ODDS_BINARY64: (
        ErrorCode.ODDS_BINARY64,
        "Odds must be representable as a finite binary64 value.",
    ),
    CoreValidationCode.ODDS_RANGE: (ErrorCode.ODDS_RANGE, "Odds must be finite and at least 1."),
    CoreValidationCode.ODDS_SYNTAX: (
        ErrorCode.ODDS_SYNTAX,
        "Odds must use unsigned decimal notation.",
    ),
    CoreValidationCode.RAW_PROBABILITY: (
        ErrorCode.RAW_PROBABILITY,
        "Raw subjective probability must be an integer from 0 to 100.",
    ),
}


def _input_failure(field, exc):
    if exc.code not in CORE_INPUT_ERRORS:
        raise ApplicationInvariantError("Unclassified core validation failure.") from exc
    code, diagnostic = CORE_INPUT_ERRORS[exc.code]
    return InputValidationError(field, diagnostic, code=code)


@dataclass(frozen=True)
class ValidatedPrediction:
    subjective: SubjectiveEstimate
    win_odds: float
    lose_odds: float


def validate_prediction(command: CalculateCommand) -> ValidatedPrediction:
    require_bool(command.reference_history, "reference_history")
    if type(command.character_id) is not int:
        raise InputValidationError(
            "character_id", "Character ID must be an integer.", code=ErrorCode.CHARACTER_INTEGER
        )
    odds = []
    for field, text in (("win_odds", command.win_odds_raw), ("lose_odds", command.lose_odds_raw)):
        try:
            odds.append(core.parse_odds_text(text))
        except CoreValidationError as exc:
            raise _input_failure(field, exc) from exc
    try:
        subjective = core.compute_subjective_estimate(command.p_h_raw)
    except CoreValidationError as exc:
        raise _input_failure("subjective_probability", exc) from exc
    return ValidatedPrediction(subjective, *odds)


def build_snapshot(
    prediction: ValidatedPrediction, history_rows: list[RoundRecord], cutoff: datetime
) -> RoundAnalysisSnapshotRecord:
    """History rows come from the accepted eligible-history query, not the stats cache."""
    subject = prediction.subjective
    wins = sum(row.result is True for row in history_rows)
    history = core.compute_historical_estimate(wins, len(history_rows) - wins)
    subjective_odds = core.analyze_subjective_odds(
        subject, prediction.win_odds, prediction.lose_odds
    )
    historical_odds = core.analyze_historical_odds(
        history, prediction.win_odds, prediction.lose_odds
    )
    sides = {}
    for name in ("win", "lose"):
        subjective_side = getattr(subjective_odds, name)
        historical_side = None if historical_odds is None else getattr(historical_odds, name)
        for field in ("ev_center", "ev_min", "ev_max", "ev_state"):
            sides[f"subjective_{name}_{field}"] = getattr(subjective_side, field)
            sides[f"historical_{name}_{field}"] = (
                None if historical_side is None else getattr(historical_side, field)
            )
        sides[f"subjective_{name}_margin_index"] = subjective_side.robust_margin_index
        sides[f"historical_{name}_threshold_posterior_probability"] = (
            None if historical_side is None else historical_side.threshold_posterior_probability
        )
        sides[f"{name}_model_relation"] = core.classify_model_relation(
            subjective_side.ev_state,
            None if historical_side is None else historical_side.ev_state,
        )
    return RoundAnalysisSnapshotRecord(
        round_id="",  # Bound to the generated/existing ID only after the analysis is assembled.
        p_h_used=subject.p_h_used,
        subjective_probability=subject.probability,
        subjective_p_min=subject.p_min,
        subjective_p_max=subject.p_max,
        subjective_logit_half_width=subject.logit_half_width,
        subjective_model_version=subject.model_version,
        odds_analysis_version=subjective_odds.analysis_version,
        break_even_win=subjective_odds.break_even_win,
        break_even_lose_event=subjective_odds.break_even_lose_event,
        break_even_lose_as_win_probability=subjective_odds.break_even_lose_as_win_probability,
        odds_combination_status=subjective_odds.odds_combination_status,
        history_model_status=history.status,
        history_statistically_ready=history.statistically_ready,
        history_wins=history.wins,
        history_losses=history.losses,
        history_sample_size=history.sample_size,
        history_model_version=history.model_version,
        history_gate_version=history.gate_version,
        history_probability=history.probability,
        history_lower=history.lower,
        history_upper=history.upper,
        history_data_through_at=cutoff,
        last_included_historical_round_id=history_rows[-1].round_id if history_rows else None,
        **sides,
    )
