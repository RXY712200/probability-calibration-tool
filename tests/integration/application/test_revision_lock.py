"""Outcome knowledge closes prediction revision without persisting post-run choices."""

from dataclasses import replace

import pytest

from probability_calibration_tool.application.enums import WorkflowState
from probability_calibration_tool.application.errors import (
    InputValidationError,
    InvalidWorkflowTransitionError,
)
from probability_calibration_tool.domain.enums import RoundStatus

from .helpers import COMMAND, InjectedFailure


def _locked_workflow(h):
    workflow = h.workflow()
    workflow.set_inputs(COMMAND)
    workflow.calculate()
    return workflow


def _assert_revision_rejected(h, workflow):
    before = h.capture()
    state = workflow.state
    inputs, analysis, choices = workflow.inputs, workflow.analysis, workflow.post_run_choices
    for action in (
        workflow.modify,
        lambda: workflow.set_inputs(replace(COMMAND, p_h_raw=30)),
        workflow.calculate,
    ):
        with pytest.raises(InvalidWorkflowTransitionError):
            action()
        assert workflow.state == state
        assert (workflow.inputs, workflow.analysis, workflow.post_run_choices) == (
            inputs,
            analysis,
            choices,
        )
    assert h.capture() == before


@pytest.mark.parametrize("include_only", [False, True])
def test_a_pre_result_modify_recalculate_remains_allowed(h, include_only):
    workflow = _locked_workflow(h)
    original = workflow.analysis
    if include_only:
        workflow.choose_include(True)
    before = h.capture()
    workflow.modify()
    revised_inputs = replace(COMMAND, p_h_raw=60)
    workflow.set_inputs(revised_inputs)
    assert workflow.state == WorkflowState.PENDING_EDIT
    assert h.capture() == before
    h.clock.advance()
    revised = workflow.calculate()
    assert workflow.state == WorkflowState.PENDING_LOCKED
    assert revised.round_id == original.round_id
    assert revised.created_at == original.created_at
    assert revised.revision_count == original.revision_count + 1
    assert revised.inputs == revised_inputs
    assert h.snapshot(revised.round_id).subjective_probability == 0.6
    workflow.modify()  # Successful pre-result revision does not itself introduce a lock.
    assert workflow.state == WorkflowState.PENDING_EDIT


@pytest.mark.parametrize("result", [True, False], ids=["B_win", "C_loss"])
def test_b_c_result_selection_locks_revision_without_persisting_choices(h, result):
    workflow = _locked_workflow(h)
    before = h.capture()
    workflow.choose_result(result)
    assert workflow.state == WorkflowState.PENDING_LOCKED
    assert workflow.post_run_choices == (result, None)
    _assert_revision_rejected(h, workflow)
    assert h.capture() == before


def test_d_e_back_and_changed_postrun_choices_never_reopen_prediction(h):
    workflow = _locked_workflow(h)
    before = h.capture()
    workflow.choose_result(True)
    workflow.choose_include(True)
    assert workflow.state == WorkflowState.CONFIRM_SAVE
    workflow.back()
    _assert_revision_rejected(h, workflow)
    workflow.choose_result(False)
    assert workflow.state == WorkflowState.CONFIRM_SAVE
    assert workflow.post_run_choices == (False, True)
    workflow.back()
    _assert_revision_rejected(h, workflow)
    workflow.choose_include(False)
    assert workflow.state == WorkflowState.CONFIRM_SAVE
    assert workflow.post_run_choices == (False, False)
    workflow.back()
    _assert_revision_rejected(h, workflow)
    assert h.capture() == before


def test_e_result_change_before_include_does_not_reopen_revision(h):
    workflow = _locked_workflow(h)
    for result in (True, False, True):
        workflow.choose_result(result)
        assert workflow.post_run_choices == (result, None)
        _assert_revision_rejected(h, workflow)


@pytest.mark.parametrize("previous_result", [None, True, False])
def test_f_recovery_conservatively_locks_with_or_without_previous_result(h, previous_result):
    workflow = _locked_workflow(h)
    original = workflow.analysis
    if previous_result is not None:
        workflow.choose_result(previous_result)
    before = h.capture()
    del workflow
    recovered = h.workflow()
    recovered.inspect_recovery()
    assert recovered.continue_recovery() == original
    assert recovered.state == WorkflowState.PENDING_LOCKED
    assert recovered.post_run_choices == (None, None)
    _assert_revision_rejected(h, recovered)
    assert h.capture() == before


def test_g_pending_edit_crash_restores_old_prediction_but_locks_further_revision(h):
    workflow = _locked_workflow(h)
    original = workflow.analysis
    snapshot = h.snapshot(original.round_id)
    before = h.capture()
    workflow.modify()
    workflow.set_inputs(replace(COMMAND, character_id=2, p_h_raw=30, win_odds_raw="5"))
    assert workflow.state == WorkflowState.PENDING_EDIT
    assert h.capture() == before
    del workflow
    recovered = h.workflow()
    recovered.inspect_recovery()
    assert recovered.continue_recovery() == original
    assert recovered.inputs == COMMAND
    _assert_revision_rejected(h, recovered)
    assert h.snapshot(original.round_id) == snapshot
    assert h.capture() == before


@pytest.mark.parametrize("recovered", [False, True], ids=["live", "recovered"])
def test_h_completion_after_lock_and_next_round_revision_reset(h, recovered):
    workflow = _locked_workflow(h)
    original_id = workflow.analysis.round_id
    if recovered:
        workflow = h.workflow()
        workflow.inspect_recovery()
        workflow.continue_recovery()
    workflow.choose_result(False)
    _assert_revision_rejected(h, workflow)
    workflow.choose_include(True)
    completed = workflow.confirm_save()
    assert completed.status == RoundStatus.COMPLETED
    assert completed.round_id == original_id
    assert completed.result is False and completed.include_character_history is True
    assert workflow.state == WorkflowState.COMPLETED_NOTICE
    workflow.dismiss_completed()
    assert workflow.state == WorkflowState.DRAFT
    workflow.set_inputs(COMMAND)
    fresh = workflow.calculate()
    assert fresh.round_id != original_id
    workflow.modify()
    assert workflow.state == WorkflowState.PENDING_EDIT


@pytest.mark.parametrize("recovered", [False, True], ids=["live", "recovered"])
def test_i_void_after_lock_preserves_semantics_and_resets_next_round(h, recovered):
    workflow = _locked_workflow(h)
    original_id = workflow.analysis.round_id
    original, snapshot, stats = h.record(original_id), h.snapshot(original_id), h.stats()
    if recovered:
        workflow = h.workflow()
        workflow.inspect_recovery()
        workflow.continue_recovery()
    workflow.choose_result(True)
    _assert_revision_rejected(h, workflow)
    now = h.clock.advance()
    voided = workflow.void_pending("abandoned")
    assert voided.status == RoundStatus.VOIDED
    assert h.record(original_id) == replace(
        original,
        status=RoundStatus.VOIDED,
        voided_at=now,
        last_updated_at=now,
        void_reason="abandoned",
    )
    assert h.snapshot(original_id) == snapshot and h.stats() == stats
    assert workflow.state == WorkflowState.DRAFT
    workflow.set_inputs(COMMAND)
    assert workflow.calculate().round_id != original_id
    workflow.modify()
    assert workflow.state == WorkflowState.PENDING_EDIT


@pytest.mark.parametrize("invalid", [None, 1, "win"])
def test_rejected_nonboolean_result_does_not_lock_prediction(h, invalid):
    workflow = _locked_workflow(h)
    before = h.capture()
    with pytest.raises(InputValidationError):
        workflow.choose_result(invalid)
    assert workflow.post_run_choices == (None, None)
    workflow.modify()
    assert workflow.state == WorkflowState.PENDING_EDIT
    assert h.capture() == before


@pytest.mark.parametrize("operation", ["complete", "void"])
def test_failed_terminal_operation_does_not_clear_revision_lock(h, monkeypatch, operation):
    workflow = _locked_workflow(h)
    workflow.choose_result(True)
    before = h.capture()

    def fail(*args):
        raise InjectedFailure("terminal operation")

    if operation == "complete":
        workflow.choose_include(True)
        monkeypatch.setattr(h.rounds, "complete_pending", fail)
        with pytest.raises(InjectedFailure):
            workflow.confirm_save()
        assert workflow.state == WorkflowState.CONFIRM_SAVE
        workflow.back()
    else:
        monkeypatch.setattr(h.rounds, "void_pending", fail)
        with pytest.raises(InjectedFailure):
            workflow.void_pending()
    _assert_revision_rejected(h, workflow)
    assert h.capture() == before
