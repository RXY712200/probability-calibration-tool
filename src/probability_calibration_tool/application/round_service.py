"""Atomic prediction revisions and post-run transitions."""

from dataclasses import replace

from probability_calibration_tool.domain.enums import HistoryModelStatus, RoundStatus
from probability_calibration_tool.domain.records import RoundRecord

from . import _view_builder
from ._checks import (
    active_regime,
    pending_rounds,
    require_bool,
    require_round,
    require_snapshot,
    utc_now,
    validate_reason,
)
from .analysis_builder import build_snapshot, validate_prediction
from .commands import CalculateCommand
from .errors import PendingRoundExistsError
from .ports import Clock, IdGenerator, UowFactory
from .views import CompletionResult, LockedAnalysisView, VoidResult


class RoundService:
    def __init__(self, uow_factory: UowFactory, clock: Clock, ids: IdGenerator) -> None:
        self._uow_factory = uow_factory
        self._clock = clock
        self._ids = ids

    def calculate(self, command: CalculateCommand) -> LockedAnalysisView:
        prediction = validate_prediction(command)
        # Read history and write its prediction in the SAME consistent transaction.
        with self._uow_factory() as uow:
            if pending_rounds(uow):
                raise PendingRoundExistsError("Finish or void the existing pending round first.")
            regime = active_regime(uow, command.character_id)
            now = utc_now(self._clock)
            snapshot = build_snapshot(
                prediction, uow.rounds.eligible_history(command.character_id, regime.regime_id), now
            )
            round_id = self._ids.new_id()
            snapshot = replace(snapshot, round_id=round_id)
            exposed = (
                command.reference_history
                and snapshot.history_model_status == HistoryModelStatus.VALID
            )
            record = RoundRecord(
                round_id=round_id,
                created_at=now,
                calculated_at=now,
                last_updated_at=now,
                completed_at=None,
                voided_at=None,
                void_reason=None,
                character_id=command.character_id,
                history_regime_id=regime.regime_id,
                reference_history=command.reference_history,
                p_h_raw=command.p_h_raw,
                win_odds_raw=command.win_odds_raw,
                lose_odds_raw=command.lose_odds_raw,
                win_odds=prediction.win_odds,
                lose_odds=prediction.lose_odds,
                status=RoundStatus.PENDING,
                revision_count=0,
                result=None,
                include_character_history=None,
                history_exposed=exposed,
                history_exposed_at=now if exposed else None,
                subjective_independence_compromised=False,
                supersedes_round_id=None,
            )
            uow.rounds.insert(record)
            uow.snapshots.insert(snapshot)
            uow.commit()
        return _view_builder.locked_view(record, snapshot)

    def recalculate(self, round_id: str, command: CalculateCommand) -> LockedAnalysisView:
        prediction = validate_prediction(command)
        with self._uow_factory() as uow:
            pending_rounds(uow)
            old = require_round(uow, round_id, RoundStatus.PENDING)
            require_snapshot(uow, round_id)
            regime = active_regime(uow, command.character_id)
            now = utc_now(self._clock)
            snapshot = replace(
                build_snapshot(
                    prediction,
                    uow.rounds.eligible_history(command.character_id, regime.regime_id),
                    now,
                ),
                round_id=round_id,
            )
            exposed = old.history_exposed or (
                command.reference_history
                and snapshot.history_model_status == HistoryModelStatus.VALID
            )
            compromised = old.subjective_independence_compromised or (
                old.history_exposed
                and (old.character_id != command.character_id or old.p_h_raw != command.p_h_raw)
            )
            record = replace(
                old,
                calculated_at=now,
                last_updated_at=now,
                revision_count=old.revision_count + 1,
                character_id=command.character_id,
                history_regime_id=regime.regime_id,
                reference_history=command.reference_history,
                p_h_raw=command.p_h_raw,
                win_odds_raw=command.win_odds_raw,
                lose_odds_raw=command.lose_odds_raw,
                win_odds=prediction.win_odds,
                lose_odds=prediction.lose_odds,
                history_exposed=exposed,
                history_exposed_at=old.history_exposed_at
                if old.history_exposed
                else (now if exposed else None),
                subjective_independence_compromised=compromised,
            )
            uow.rounds.update(record)
            uow.snapshots.update(snapshot)
            uow.commit()
        return _view_builder.locked_view(record, snapshot)

    def complete_pending(
        self, round_id: str, result: bool, include_character_history: bool
    ) -> CompletionResult:
        require_bool(result, "result")
        require_bool(include_character_history, "include_character_history")
        with self._uow_factory() as uow:
            pending_rounds(uow)
            old = require_round(uow, round_id, RoundStatus.PENDING)
            require_snapshot(uow, round_id)
            now = utc_now(self._clock)
            record = replace(
                old,
                status=RoundStatus.COMPLETED,
                result=result,
                include_character_history=include_character_history,
                completed_at=now,
                last_updated_at=now,
            )
            uow.rounds.update(record)
            if include_character_history:
                uow.stats.rebuild_stats(record.character_id, record.history_regime_id)
            uow.commit()
        return CompletionResult(round_id, record.status, result, include_character_history, now)

    def void_pending(self, round_id: str, reason: str | None = None) -> VoidResult:
        validate_reason(reason)
        with self._uow_factory() as uow:
            pending_rounds(uow)
            old = require_round(uow, round_id, RoundStatus.PENDING)
            require_snapshot(uow, round_id)
            now = utc_now(self._clock)
            uow.rounds.update(
                replace(
                    old,
                    status=RoundStatus.VOIDED,
                    voided_at=now,
                    void_reason=reason,
                    last_updated_at=now,
                    result=None,
                    include_character_history=None,
                    completed_at=None,
                )
            )
            uow.commit()
        return VoidResult(round_id, RoundStatus.VOIDED, now, reason)
