from dataclasses import asdict, replace

import pytest

from probability_calibration_tool import core
from probability_calibration_tool.application.enums import (
    HistoricalDisplayState,
    RecoveryState,
    WorkflowState,
)
from probability_calibration_tool.application.errors import (
    ApplicationInvariantError,
    InvalidWorkflowTransitionError,
    MultiplePendingRoundsError,
    RoundNotPendingError,
)
from probability_calibration_tool.persistence.repositories import RoundRepository
from probability_calibration_tool.persistence.unit_of_work import UnitOfWork

from .helpers import COMMAND


def test_recovery_zero_pending_has_no_analysis(h):
    before = h.capture()
    inspection = h.recovery.inspect()
    assert asdict(inspection) == {"state": RecoveryState.NONE, "round_id": None}
    workflow = h.workflow()
    assert workflow.inspect_recovery() == inspection
    assert workflow.state == WorkflowState.DRAFT
    with pytest.raises(RoundNotPendingError):
        h.recovery.continue_pending()
    assert h.capture() == before


@pytest.mark.parametrize(
    "reference,counts,display",
    [
        (False, (19, 1), HistoricalDisplayState.HIDDEN),
        (True, (0, 0), HistoricalDisplayState.NO_HISTORY),
        (True, (1, 0), HistoricalDisplayState.INSUFFICIENT),
        (True, (19, 1), HistoricalDisplayState.VISIBLE),
    ],
)
def test_recovery_same_round_same_snapshot_without_math_writes_or_new_id(
    h, monkeypatch, reference, counts, display
):
    h.seed_history(*counts)
    locked = h.rounds.calculate(replace(COMMAND, reference_history=reference))
    before = h.capture()
    h.clock.advance()

    def forbidden(*args):
        pytest.fail("Recovery must not recompute or write")

    for function in (
        "compute_historical_estimate",
        "compute_subjective_estimate",
        "analyze_historical_odds",
        "analyze_subjective_odds",
    ):
        monkeypatch.setattr(core, function, forbidden)
    monkeypatch.setattr(UnitOfWork, "commit", forbidden)
    monkeypatch.setattr(h.ids, "new_id", forbidden)
    monkeypatch.setattr(h.clock, "now", forbidden)
    inspection = h.recovery.inspect()
    assert asdict(inspection) == {"state": RecoveryState.RECOVERABLE, "round_id": locked.round_id}
    assert h.recovery.continue_pending() == locked
    assert locked.history.state == display
    workflow = h.workflow()
    workflow.inspect_recovery()
    assert workflow.state == WorkflowState.RECOVERY
    assert workflow.analysis is None
    assert workflow.continue_recovery() == locked
    assert workflow.state == WorkflowState.PENDING_LOCKED
    assert workflow.post_run_choices == (None, None)
    assert h.capture() == before


def test_multiple_pending_is_semantic_recovery_error_never_selects_one(h, monkeypatch):
    locked = h.rounds.calculate(COMMAND)
    record = h.record(locked.round_id)
    before = h.capture()
    monkeypatch.setattr(
        RoundRepository, "list_pending", lambda self: [record, replace(record, round_id="second")]
    )
    for action in (h.recovery.inspect, h.recovery.continue_pending):
        with pytest.raises(MultiplePendingRoundsError):
            action()
    workflow = h.workflow()
    with pytest.raises(MultiplePendingRoundsError):
        workflow.inspect_recovery()
    assert workflow.state == WorkflowState.RECOVERY_ERROR
    assert workflow.analysis is None
    with pytest.raises(InvalidWorkflowTransitionError):
        workflow.continue_recovery()
    assert h.capture() == before


def test_multiple_pending_detected_again_on_continue(h, monkeypatch):
    locked = h.rounds.calculate(COMMAND)
    workflow = h.workflow()
    workflow.inspect_recovery()
    record = h.record(locked.round_id)
    monkeypatch.setattr(RoundRepository, "list_pending", lambda self: [record, record])
    with pytest.raises(MultiplePendingRoundsError):
        workflow.continue_recovery()
    assert workflow.state == WorkflowState.RECOVERY_ERROR


def test_recovery_exposure_contradiction_fails_closed_without_history_release(h, monkeypatch):
    h.seed_history()
    locked = h.rounds.calculate(COMMAND)
    with h.factory() as uow:
        uow.rounds.update(replace(uow.rounds.get(locked.round_id), reference_history=True))
        uow.commit()
    before = h.capture()
    from probability_calibration_tool.application import _view_builder

    def forbidden(*args, **kwargs):
        pytest.fail("Unauthorized numeric history view must never be constructed")

    monkeypatch.setattr(_view_builder, "VisibleHistoryView", forbidden)
    workflow = h.workflow()
    workflow.inspect_recovery()
    with pytest.raises(ApplicationInvariantError):
        workflow.continue_recovery()
    assert workflow.analysis is None
    assert workflow.state == WorkflowState.RECOVERY
    assert h.capture() == before


def test_pending_edit_crash_restores_old_inputs_and_snapshot(h):
    workflow = h.workflow()
    workflow.set_inputs(COMMAND)
    locked = workflow.calculate()
    before = h.capture()
    workflow.modify()
    edited = replace(COMMAND, character_id=2, p_h_raw=30, win_odds_raw="5")
    workflow.set_inputs(edited)
    assert workflow.inputs == edited and workflow.state == WorkflowState.PENDING_EDIT
    assert h.capture() == before
    del workflow
    recovered = h.workflow()
    recovered.inspect_recovery()
    assert recovered.continue_recovery() == locked
    assert recovered.inputs == COMMAND
    assert h.capture() == before


def test_postrun_choices_lost_on_crash_without_persisting_result(h):
    workflow = h.workflow()
    workflow.set_inputs(COMMAND)
    locked = workflow.calculate()
    before = h.capture()
    workflow.choose_result(False)
    workflow.choose_include(False)
    assert workflow.state == WorkflowState.CONFIRM_SAVE
    assert h.capture() == before
    recovered = h.workflow()
    recovered.inspect_recovery()
    assert recovered.continue_recovery() == locked
    assert recovered.post_run_choices == (None, None)


def test_missing_snapshot_fails_closed(h, monkeypatch):
    from probability_calibration_tool.persistence.repositories import SnapshotRepository

    h.rounds.calculate(COMMAND)
    monkeypatch.setattr(SnapshotRepository, "get", lambda *args: None)
    with pytest.raises(ApplicationInvariantError):
        h.recovery.continue_pending()
