from dataclasses import asdict, fields, replace

import pytest

from probability_calibration_tool.application.enums import HistoricalDisplayState
from probability_calibration_tool.application.errors import (
    ApplicationInvariantError,
    InputValidationError,
    RegimeSwitchBlockedError,
)
from probability_calibration_tool.core.model_specs import STATS_VERSION
from probability_calibration_tool.persistence.repositories import (
    CharacterStatsRepository,
    HistoryRegimeRepository,
)
from probability_calibration_tool.persistence.unit_of_work import UnitOfWork

from .helpers import COMMAND, InjectedFailure


def test_regime_switch_preserves_old_history_reason_and_initializes_zero_cache(h):
    first = h.regimes.start_new_regime(1, "first reason")
    ids = h.seed_history(2, 1)
    old_stats = h.stats()
    old_snapshots = [h.snapshot(round_id) for round_id in ids]
    with h.factory() as uow:
        old = uow.regimes.get_active(1)
    now = h.clock.advance()
    view = h.regimes.start_new_regime(1, "new rules")
    assert view.character_id == 1 and view.regime_number == first.regime_number + 1
    assert view.regime_id != old.regime_id
    assert view.reason == "new rules" and view.started_at == now
    assert view.included_sample_count == 0
    with h.factory() as uow:
        assert uow.regimes.get(old.regime_id) == replace(old, active=False, ended_at=now)
        assert uow.regimes.get(old.regime_id).reason == "first reason"
        new = uow.regimes.get_active(1)
        assert new.regime_id == view.regime_id and new.ended_at is None
        assert new.reason == "new rules" and new.started_at == now
        assert uow.stats.get(1, old.regime_id) == old_stats
    stats = h.stats()
    assert (stats.included_games, stats.wins, stats.losses) == (0, 0, 0)
    assert stats.updated_at == now and stats.stats_version == STATS_VERSION
    assert stats.last_included_round_id is None
    assert [h.snapshot(round_id) for round_id in ids] == old_snapshots
    pending = h.rounds.calculate(replace(COMMAND, reference_history=True))
    assert pending.history.state == HistoricalDisplayState.NO_HISTORY
    assert h.snapshot(pending.round_id).history_sample_size == 0


@pytest.mark.parametrize("character_id", [1, 2])
def test_pending_blocks_regime_switch_for_every_character(h, character_id):
    h.rounds.calculate(COMMAND)
    before = h.capture()
    with pytest.raises(RegimeSwitchBlockedError):
        h.regimes.start_new_regime(character_id, "not allowed")
    assert h.capture() == before


@pytest.mark.parametrize("failure", ["new_regime", "zero_stats", "commit"])
def test_regime_switch_rollback(h, monkeypatch, failure):
    h.seed_history(1, 1)
    before = h.capture()
    h.clock.advance()

    def fail(*args):
        raise InjectedFailure(failure)

    if failure == "new_regime":
        monkeypatch.setattr(HistoryRegimeRepository, "insert", fail)
    elif failure == "zero_stats":
        monkeypatch.setattr(CharacterStatsRepository, "insert", fail)
    else:
        monkeypatch.setattr(UnitOfWork, "commit", fail)
    with pytest.raises(InjectedFailure):
        h.regimes.start_new_regime(1, "new")
    assert h.capture() == before
    with h.factory() as uow:
        assert uow.regimes.get_active(1).regime_number == 1


def test_maintenance_dto_is_structurally_nondirectional_before_lock(h):
    h.seed_history()
    before = h.capture()
    views = h.maintenance.list_characters()
    assert len(views) == 34
    expected_fields = {
        "character_id",
        "display_name",
        "active_regime_number",
        "regime_started_at",
        "regime_reason",
        "included_sample_count",
    }
    for view in views:
        assert {field.name for field in fields(view)} == expected_fields
        assert set(asdict(view)) == expected_fields
        assert not any(isinstance(value, (dict, list)) for value in asdict(view).values())
    first = next(view for view in views if view.character_id == 1)
    assert first.included_sample_count == 20
    assert first.active_regime_number == 1
    assert h.capture() == before


@pytest.mark.parametrize("operation", ["calculate", "regime", "maintenance"])
def test_missing_active_regime_fails_as_application_invariant(h, monkeypatch, operation):
    before = h.capture()
    monkeypatch.setattr(HistoryRegimeRepository, "get_active", lambda *args: None)
    with pytest.raises(ApplicationInvariantError):
        if operation == "calculate":
            h.rounds.calculate(COMMAND)
        elif operation == "regime":
            h.regimes.start_new_regime(1)
        else:
            h.maintenance.list_characters()
    assert h.capture() == before


@pytest.mark.parametrize("operation", ["void", "regime"])
def test_optional_reason_rejects_nontext(h, operation):
    before = h.capture()
    with pytest.raises(InputValidationError) as caught:
        if operation == "void":
            h.rounds.void_pending("unused", 123)
        else:
            h.regimes.start_new_regime(1, 123)
    assert caught.value.field == "reason"
    assert h.capture() == before
