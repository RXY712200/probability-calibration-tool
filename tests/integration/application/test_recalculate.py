from dataclasses import replace

import pytest

from probability_calibration_tool.application import _view_builder
from probability_calibration_tool.application.enums import HistoricalDisplayState
from probability_calibration_tool.application.errors import RoundNotPendingError
from probability_calibration_tool.domain.enums import HistoryModelStatus
from probability_calibration_tool.persistence.repositories import SnapshotRepository
from probability_calibration_tool.persistence.unit_of_work import UnitOfWork

from .helpers import COMMAND, InjectedFailure


def test_recalculate_preserves_identity_created_at_and_replaces_full_snapshot(h):
    view = h.rounds.calculate(COMMAND)
    old = h.record(view.round_id)
    old_snapshot = h.snapshot(view.round_id)
    now = h.clock.advance()
    new_command = replace(COMMAND, p_h_raw=40, win_odds_raw="4.00", lose_odds_raw="1.5")
    revised = h.rounds.recalculate(view.round_id, new_command)
    record = h.record(view.round_id)
    snapshot = h.snapshot(view.round_id)
    assert revised.round_id == record.round_id == old.round_id
    assert record.created_at == old.created_at
    assert record.calculated_at == record.last_updated_at == now
    assert record.revision_count == old.revision_count + 1
    assert revised.inputs == new_command
    assert snapshot.round_id == old_snapshot.round_id
    assert snapshot.history_data_through_at == now
    assert snapshot.subjective_probability == 0.4
    assert snapshot.subjective_win_ev_center != old_snapshot.subjective_win_ev_center
    assert len(h.capture()["rounds"]) == len(h.capture()["round_analysis_snapshots"]) == 1


@pytest.mark.parametrize("old_exposed", [False, True])
@pytest.mark.parametrize("failure", ["snapshot_update", "commit"])
def test_recalculate_rollback_then_retry_all_fields(h, monkeypatch, old_exposed, failure):
    h.seed_history()
    command = replace(COMMAND, reference_history=old_exposed)
    view = h.rounds.calculate(command)
    before = h.capture()
    old = h.record(view.round_id)
    now = h.clock.advance()
    changed = replace(COMMAND, reference_history=True, p_h_raw=80)
    calls = []
    with monkeypatch.context() as patch:
        patch.setattr(_view_builder, "locked_view", lambda *args: calls.append(args))
        original = SnapshotRepository.update

        def fail_snapshot(self, snapshot):
            original(self, snapshot)
            raise InjectedFailure("After snapshot and round mutation")

        def fail_commit(self):
            raise InjectedFailure("Before commit")

        if failure == "snapshot_update":
            patch.setattr(SnapshotRepository, "update", fail_snapshot)
        else:
            patch.setattr(UnitOfWork, "commit", fail_commit)
        with pytest.raises(InjectedFailure):
            h.rounds.recalculate(view.round_id, changed)
    assert calls == []
    assert h.capture() == before
    assert h.record(view.round_id) == old
    revised = h.rounds.recalculate(view.round_id, changed)
    assert revised.revision_count == old.revision_count + 1
    assert revised.history_exposed
    assert revised.history_exposed_at == (old.history_exposed_at if old_exposed else now)
    assert revised.subjective_independence_compromised is old_exposed


def test_golden_d_odds_only_and_reference_only_do_not_compromise(h):
    h.seed_history()
    command = replace(COMMAND, reference_history=True)
    view = h.rounds.calculate(command)
    for changes in (
        {"win_odds_raw": "4"},
        {"reference_history": False},
        {"reference_history": True},
    ):
        h.clock.advance()
        command = replace(command, **changes)
        revised = h.rounds.recalculate(view.round_id, command)
        assert not revised.subjective_independence_compromised
        assert revised.history_exposed_at == view.history_exposed_at


@pytest.mark.parametrize(
    "changes", [{"p_h_raw": 80}, {"character_id": 2}], ids=["golden_E", "golden_F"]
)
def test_golden_e_f_old_exposure_compromise_is_irreversible(h, changes):
    h.seed_history()
    command = replace(COMMAND, reference_history=True)
    view = h.rounds.calculate(command)
    h.clock.advance()
    revised = h.rounds.recalculate(view.round_id, replace(command, **changes))
    assert revised.subjective_independence_compromised
    # Restoring original facts, then changing only odds or display, must not clear the audit.
    for later in (
        command,
        replace(command, win_odds_raw="4"),
        replace(command, reference_history=False),
    ):
        h.clock.advance()
        restored = h.rounds.recalculate(view.round_id, later)
        assert restored.subjective_independence_compromised
        assert restored.history_exposed_at == view.history_exposed_at


def test_golden_g_first_exposure_same_recalc_uses_old_flag(h, monkeypatch):
    h.seed_history()
    view = h.rounds.calculate(COMMAND)
    assert not view.history_exposed
    now = h.clock.advance()
    original = _view_builder.locked_view
    calls = []

    def project(record, snapshot):
        persisted = h.record(record.round_id)
        assert persisted == record
        assert persisted.history_exposed and persisted.history_exposed_at == now
        assert not persisted.subjective_independence_compromised
        assert h.snapshot(record.round_id) == snapshot
        calls.append(record.round_id)
        return original(record, snapshot)

    monkeypatch.setattr(_view_builder, "locked_view", project)
    revised = h.rounds.recalculate(
        view.round_id, replace(COMMAND, p_h_raw=80, reference_history=True)
    )
    assert revised.history.state == HistoricalDisplayState.VISIBLE
    assert revised.history_exposed
    assert not revised.subjective_independence_compromised
    assert calls == [view.round_id]


def test_golden_h_first_timestamp_survives_off_on_and_history_status_change(h):
    h.seed_history()
    h.seed_history(1, 0, character_id=2)
    command = replace(COMMAND, reference_history=True)
    first = h.rounds.calculate(command)
    cases = [
        (replace(command, reference_history=False), HistoricalDisplayState.HIDDEN),
        (command, HistoricalDisplayState.VISIBLE),
        (replace(command, character_id=2), HistoricalDisplayState.INSUFFICIENT),
        (replace(command, character_id=3), HistoricalDisplayState.NO_HISTORY),
        (command, HistoricalDisplayState.VISIBLE),
    ]
    for changed, state in cases:
        h.clock.advance()
        revised = h.rounds.recalculate(first.round_id, changed)
        assert revised.history_exposed
        assert revised.history_exposed_at == first.history_exposed_at
        assert revised.history.state == state


def test_changed_character_uses_new_characters_active_regime_only(h):
    h.seed_history()
    h.seed_history(2, 0, character_id=2)
    regime = h.regimes.start_new_regime(2, "new character rules")
    target_ids = h.seed_history(0, 1, character_id=2)
    view = h.rounds.calculate(COMMAND)
    revised = h.rounds.recalculate(
        view.round_id, replace(COMMAND, character_id=2, reference_history=True)
    )
    record, snapshot = h.record(view.round_id), h.snapshot(view.round_id)
    assert record.history_regime_id == revised.regime_id == regime.regime_id
    assert (snapshot.history_wins, snapshot.history_losses) == (0, 1)
    assert snapshot.history_model_status == HistoryModelStatus.INSUFFICIENT
    assert snapshot.last_included_historical_round_id == target_ids[-1]
    assert not record.history_exposed
    assert not record.subjective_independence_compromised


def test_actual_raw_change_not_clamped_probability_controls_compromise(h):
    h.seed_history()
    command = replace(COMMAND, reference_history=True, p_h_raw=0)
    view = h.rounds.calculate(command)
    revised = h.rounds.recalculate(view.round_id, replace(command, p_h_raw=1))
    assert revised.subjective.probability == view.subjective.probability
    assert revised.subjective_independence_compromised


@pytest.mark.parametrize("terminal", ["completed", "voided"])
def test_terminal_snapshots_cannot_be_recalculated(h, terminal):
    view = h.rounds.calculate(COMMAND)
    if terminal == "completed":
        h.rounds.complete_pending(view.round_id, True, True)
    else:
        h.rounds.void_pending(view.round_id)
    before = h.capture()
    with pytest.raises(RoundNotPendingError):
        h.rounds.recalculate(view.round_id, replace(COMMAND, p_h_raw=50))
    assert h.capture() == before
