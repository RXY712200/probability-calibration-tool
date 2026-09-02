"""Post-run facts only: verified safety port, then atomic audit-preserving replacement."""

from dataclasses import replace

from probability_calibration_tool.domain.enums import RoundStatus
from probability_calibration_tool.domain.records import RoundAnalysisSnapshotRecord, RoundRecord
from probability_calibration_tool.persistence.unit_of_work import UnitOfWork

from ._checks import (
    pending_rounds,
    require_bool,
    require_round,
    require_snapshot,
    utc_now,
    validate_reason,
)
from .errors import CorrectionBlockedError, ErrorCode
from .ports import Clock, IdGenerator, SafetyBackupPort, UowFactory
from .views import CorrectionResult


def _correction_source(
    uow: UnitOfWork, round_id: str
) -> tuple[RoundRecord, RoundAnalysisSnapshotRecord]:
    if pending_rounds(uow):
        raise CorrectionBlockedError("A pending round blocks historical correction.")
    return (
        require_round(uow, round_id, RoundStatus.COMPLETED),
        require_snapshot(uow, round_id),
    )


class CorrectionService:
    def __init__(
        self, uow_factory: UowFactory, clock: Clock, ids: IdGenerator, backup: SafetyBackupPort
    ) -> None:
        self._uow_factory = uow_factory
        self._clock = clock
        self._ids = ids
        self._backup = backup

    def correct_post_run(
        self, round_id: str, result: bool, include_character_history: bool, reason: str
    ) -> CorrectionResult:
        require_bool(result, "result")
        require_bool(include_character_history, "include_character_history")
        validate_reason(reason, required=True)
        # Read-only preflight closes before backup; no correction write transaction yet.
        with self._uow_factory() as uow:
            original, snapshot = _correction_source(uow, round_id)
        self._backup.create_verified_safety_backup("pre_history_correction")
        now = utc_now(self._clock)
        replacement_id = self._ids.new_id()
        with self._uow_factory() as uow:
            current, current_snapshot = _correction_source(uow, round_id)
            if current != original or current_snapshot != snapshot:
                raise CorrectionBlockedError(
                    "Correction source changed during safety verification.",
                    code=ErrorCode.CONFIRMATION_EXPIRED,
                )
            uow.rounds.update(
                replace(
                    original,
                    status=RoundStatus.VOIDED,
                    voided_at=now,
                    void_reason=reason,
                    last_updated_at=now,
                )
            )
            replacement = replace(
                original,
                round_id=replacement_id,
                supersedes_round_id=round_id,
                status=RoundStatus.COMPLETED,
                created_at=now,
                last_updated_at=now,
                completed_at=now,
                voided_at=None,
                void_reason=None,
                result=result,
                include_character_history=include_character_history,
            )
            uow.rounds.insert(replacement)
            uow.snapshots.insert(replace(snapshot, round_id=replacement_id))
            uow.stats.rebuild_stats(original.character_id, original.history_regime_id)
            uow.commit()
        return CorrectionResult(round_id, replacement_id, now, result, include_character_history)
