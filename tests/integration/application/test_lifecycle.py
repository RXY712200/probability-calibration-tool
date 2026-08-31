from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone

import pytest

from probability_calibration_tool.application.errors import (
    ApplicationInvariantError,
    InputValidationError,
    RoundNotFoundError,
    RoundNotPendingError,
)
from probability_calibration_tool.domain.enums import RoundStatus
from probability_calibration_tool.persistence.repositories import CharacterStatsRepository
from probability_calibration_tool.persistence.unit_of_work import UnitOfWork

from .helpers import COMMAND, InjectedFailure


@pytest.mark.parametrize("result", [False, True])
def test_complete_included_atomically_updates_facts_and_stats_not_snapshot(h, result):
    h.seed_history(1, 1)
    view = h.rounds.calculate(COMMAND)
    old = h.record(view.round_id)
    snapshot = h.snapshot(view.round_id)
    now = h.clock.advance()
    completed = h.rounds.complete_pending(view.round_id, result, True)
    record = h.record(view.round_id)
    assert record == replace(
        old,
        status=RoundStatus.COMPLETED,
        result=result,
        include_character_history=True,
        completed_at=now,
        last_updated_at=now,
    )
    assert completed.round_id == view.round_id
    assert completed.status == RoundStatus.COMPLETED
    assert completed.result is result and completed.include_character_history
    assert completed.completed_at == now
    stats = h.stats()
    assert (stats.included_games, stats.wins, stats.losses) == (3, 1 + result, 2 - result)
    assert stats.last_included_round_id == view.round_id
    assert h.snapshot(view.round_id) == snapshot
    with h.factory() as uow:
        assert uow.rounds.list_pending() == []
    before = h.capture()
    with pytest.raises(RoundNotPendingError):
        h.rounds.complete_pending(view.round_id, not result, True)
    with pytest.raises(RoundNotPendingError):
        h.rounds.void_pending(view.round_id)
    assert h.capture() == before


@pytest.mark.parametrize("result", [False, True])
def test_excluded_completion_preserves_audit_without_stats_or_future_history(
    h, monkeypatch, result
):
    h.seed_history(1, 0)
    stats = h.stats()
    view = h.rounds.calculate(COMMAND)
    snapshot = h.snapshot(view.round_id)
    with monkeypatch.context() as patch:

        def forbidden(*args):
            pytest.fail("Excluded completion must not rebuild normal stats")

        patch.setattr(CharacterStatsRepository, "rebuild_stats", forbidden)
        h.rounds.complete_pending(view.round_id, result, False)
    record = h.record(view.round_id)
    assert record.result is result
    assert record.include_character_history is False
    assert record.status == RoundStatus.COMPLETED
    assert h.stats() == stats
    assert h.snapshot(view.round_id) == snapshot
    next_view = h.rounds.calculate(COMMAND)
    assert h.snapshot(next_view.round_id).history_sample_size == 1


@pytest.mark.parametrize("failure", ["before_stats", "after_stats", "commit"])
def test_complete_rollback_restores_pending_postrun_nulls_and_stats(h, monkeypatch, failure):
    h.seed_history(1, 1)
    view = h.rounds.calculate(COMMAND)
    before = h.capture()
    h.clock.advance()
    original = CharacterStatsRepository.rebuild_stats

    def fail_stats(self, *args):
        if failure == "after_stats":
            original(self, *args)
        raise InjectedFailure(failure)

    def fail_commit(self):
        raise InjectedFailure("commit")

    if failure == "commit":
        monkeypatch.setattr(UnitOfWork, "commit", fail_commit)
    else:
        monkeypatch.setattr(CharacterStatsRepository, "rebuild_stats", fail_stats)
    with pytest.raises(InjectedFailure):
        h.rounds.complete_pending(view.round_id, True, True)
    assert h.capture() == before
    record = h.record(view.round_id)
    assert record.status == RoundStatus.PENDING
    assert record.result is record.include_character_history is record.completed_at is None


@pytest.mark.parametrize("reason", [None, "Abandoned before the outcome"])
def test_pending_void_is_terminal_and_preserves_snapshot(h, reason):
    view = h.rounds.calculate(COMMAND)
    old = h.record(view.round_id)
    snapshot, stats = h.snapshot(view.round_id), h.stats()
    now = h.clock.advance()
    result = h.rounds.void_pending(view.round_id, reason)
    assert h.record(view.round_id) == replace(
        old, status=RoundStatus.VOIDED, voided_at=now, void_reason=reason, last_updated_at=now
    )
    assert result.voided_at == now and result.reason == reason
    assert h.snapshot(view.round_id) == snapshot
    assert h.stats() == stats
    before = h.capture()
    for operation in (
        lambda: h.rounds.complete_pending(view.round_id, True, True),
        lambda: h.rounds.recalculate(view.round_id, COMMAND),
        lambda: h.rounds.void_pending(view.round_id),
    ):
        with pytest.raises(RoundNotPendingError):
            operation()
    assert h.capture() == before


def test_void_commit_failure_preserves_pending(h, monkeypatch):
    view = h.rounds.calculate(COMMAND)
    before = h.capture()

    def fail(self):
        raise InjectedFailure("void commit")

    monkeypatch.setattr(UnitOfWork, "commit", fail)
    with pytest.raises(InjectedFailure):
        h.rounds.void_pending(view.round_id, "mistake")
    assert h.capture() == before


@pytest.mark.parametrize(
    "result,include,field",
    [
        (1, True, "result"),
        (None, True, "result"),
        ("win", True, "result"),
        (True, 0, "include_character_history"),
        (True, None, "include_character_history"),
    ],
)
def test_completion_requires_explicit_boolean_facts(h, result, include, field):
    view = h.rounds.calculate(COMMAND)
    before = h.capture()
    with pytest.raises(InputValidationError) as caught:
        h.rounds.complete_pending(view.round_id, result, include)
    assert caught.value.field == field
    assert h.capture() == before


@pytest.mark.parametrize("operation", ["complete", "void", "recalculate"])
def test_missing_round_is_semantic_error(h, operation):
    before = h.capture()
    with pytest.raises(RoundNotFoundError):
        if operation == "complete":
            h.rounds.complete_pending("missing", True, True)
        elif operation == "void":
            h.rounds.void_pending("missing")
        else:
            h.rounds.recalculate("missing", COMMAND)
    assert h.capture() == before


def test_naive_clock_is_rejected_and_aware_offsets_are_normalized(h):
    before = h.capture()
    h.clock.value = datetime(2026, 9, 1)  # noqa: DTZ001 - intentionally exercise rejection
    with pytest.raises(ApplicationInvariantError):
        h.rounds.calculate(COMMAND)
    assert h.capture() == before
    h.clock.value = datetime(2026, 9, 1, 8, tzinfo=timezone(timedelta(hours=8)))
    view = h.rounds.calculate(COMMAND)
    record = h.record(view.round_id)
    assert record.calculated_at == datetime(2026, 9, 1, tzinfo=UTC)
    assert record.calculated_at.tzinfo is UTC
    assert view.calculated_at.tzinfo is UTC
