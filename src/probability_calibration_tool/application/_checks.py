"""Private, shared business guards. These never return records to service callers."""

from datetime import UTC, datetime

from probability_calibration_tool.domain.enums import RoundStatus
from probability_calibration_tool.domain.records import (
    HistoryRegimeRecord,
    RoundAnalysisSnapshotRecord,
    RoundRecord,
)
from probability_calibration_tool.persistence.unit_of_work import UnitOfWork

from .errors import (
    ApplicationInvariantError,
    InputValidationError,
    MultiplePendingRoundsError,
    RoundNotCompletedError,
    RoundNotFoundError,
    RoundNotPendingError,
)
from .ports import Clock


def utc_now(clock: Clock) -> datetime:
    value = clock.now()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ApplicationInvariantError("Clock must return an aware datetime.")
    return value.astimezone(UTC)


def require_bool(value: bool, field: str) -> None:
    if type(value) is not bool:
        raise InputValidationError(field, "An explicit boolean choice is required.")


def validate_reason(reason: str | None, *, required: bool = False) -> None:
    if reason is not None and not isinstance(reason, str):
        raise InputValidationError("reason", "Reason must be text.")
    if required and (reason is None or not reason.strip()):
        raise InputValidationError("reason", "A nonempty correction reason is required.")


def active_regime(uow: UnitOfWork, character_id: int) -> HistoryRegimeRecord:
    if type(character_id) is not int:
        raise InputValidationError("character_id", "Character ID must be an integer.")
    character = uow.characters.get(character_id)
    if character is None or not character.active:
        raise InputValidationError("character_id", "Choose an active character.")
    regime = uow.regimes.get_active(character_id)
    if regime is None:
        raise ApplicationInvariantError("Active character has no active history regime.")
    return regime


def pending_rounds(uow: UnitOfWork) -> list[RoundRecord]:
    rows = uow.rounds.list_pending()
    if len(rows) > 1:
        raise MultiplePendingRoundsError("Multiple pending rounds require recovery attention.")
    return rows


def require_round(uow: UnitOfWork, round_id: str, status: RoundStatus) -> RoundRecord:
    record = uow.rounds.get(round_id)
    if record is None:
        raise RoundNotFoundError("Round does not exist.")
    if record.status != status:
        error = RoundNotPendingError if status == RoundStatus.PENDING else RoundNotCompletedError
        raise error(f"Round must be {status.value}.")
    return record


def require_snapshot(uow: UnitOfWork, round_id: str) -> RoundAnalysisSnapshotRecord:
    snapshot = uow.snapshots.get(round_id)
    if snapshot is None:
        raise ApplicationInvariantError("Round has no committed analysis snapshot.")
    return snapshot
