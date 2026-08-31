from dataclasses import replace

import pytest

from probability_calibration_tool.application.enums import WorkflowState
from probability_calibration_tool.application.errors import (
    InputValidationError,
    InvalidWorkflowTransitionError,
)
from probability_calibration_tool.domain.enums import RoundStatus
from probability_calibration_tool.persistence.repositories import (
    CharacterStatsRepository,
    SnapshotRepository,
)

from .helpers import COMMAND, InjectedFailure


def test_states_are_memory_only_and_persistent_status_vocabulary_unchanged():
    assert {state.name for state in WorkflowState} == {
        "DRAFT",
        "CALCULATING",
        "PENDING_LOCKED",
        "PENDING_EDIT",
        "CONFIRM_SAVE",
        "COMPLETING",
        "RECOVERY",
        "RECOVERY_ERROR",
        "COMPLETED_NOTICE",
    }
    assert {state.value for state in RoundStatus} == {"pending", "completed", "voided"}


@pytest.mark.parametrize(
    "operation,allowed",
    [
        ("set_inputs", {WorkflowState.DRAFT, WorkflowState.PENDING_EDIT}),
        ("calculate", {WorkflowState.DRAFT, WorkflowState.PENDING_EDIT}),
        ("modify", {WorkflowState.PENDING_LOCKED}),
        ("choose_result", {WorkflowState.PENDING_LOCKED}),
        ("choose_include", {WorkflowState.PENDING_LOCKED}),
        ("back", {WorkflowState.CONFIRM_SAVE}),
        ("confirm_save", {WorkflowState.CONFIRM_SAVE}),
        ("void_pending", {WorkflowState.PENDING_LOCKED}),
        ("inspect_recovery", {WorkflowState.DRAFT}),
        ("continue_recovery", {WorkflowState.RECOVERY}),
        ("dismiss_completed", {WorkflowState.COMPLETED_NOTICE}),
    ],
)
def test_transition_matrix_rejects_every_disallowed_origin(h, operation, allowed):
    before = h.capture()
    for state in set(WorkflowState) - allowed:
        workflow = h.workflow()
        workflow._state = state  # Exercise every guard independently, including transient states.
        args = {"set_inputs": (COMMAND,), "choose_result": (True,), "choose_include": (True,)}.get(
            operation, ()
        )
        with pytest.raises(InvalidWorkflowTransitionError):
            getattr(workflow, operation)(*args)
        assert workflow.state == state
    assert h.capture() == before


@pytest.mark.parametrize("include_first", [False, True])
def test_successful_workflow_including_transient_states_and_back(h, monkeypatch, include_first):
    workflow = h.workflow()
    before = h.capture()
    workflow.set_inputs(COMMAND)
    assert workflow.state == WorkflowState.DRAFT and workflow.analysis is None
    assert h.capture() == before
    original_insert = SnapshotRepository.insert
    observed = []

    def insert(self, snapshot):
        observed.append(workflow.state)
        assert workflow.state == WorkflowState.CALCULATING
        original_insert(self, snapshot)

    monkeypatch.setattr(SnapshotRepository, "insert", insert)
    locked = workflow.calculate()
    assert workflow.state == WorkflowState.PENDING_LOCKED
    workflow.modify()
    assert workflow.state == WorkflowState.PENDING_EDIT
    workflow.set_inputs(replace(COMMAND, p_h_raw=60))
    original_update = SnapshotRepository.update

    def update(self, snapshot):
        observed.append(workflow.state)
        assert workflow.state == WorkflowState.CALCULATING
        original_update(self, snapshot)

    monkeypatch.setattr(SnapshotRepository, "update", update)
    revised = workflow.calculate()
    assert revised.round_id == locked.round_id and revised.revision_count == 1
    assert workflow.state == WorkflowState.PENDING_LOCKED
    choices = [lambda: workflow.choose_result(False), lambda: workflow.choose_include(True)]
    if include_first:
        choices.reverse()
    before_choices = h.capture()
    choices[0]()
    assert workflow.state == WorkflowState.PENDING_LOCKED
    choices[1]()
    assert workflow.state == WorkflowState.CONFIRM_SAVE
    assert workflow.post_run_choices == (False, True)
    assert h.capture() == before_choices
    workflow.back()
    assert workflow.state == WorkflowState.PENDING_LOCKED
    workflow.choose_result(True)
    assert workflow.state == WorkflowState.CONFIRM_SAVE
    original_rebuild = CharacterStatsRepository.rebuild_stats

    def rebuild(self, *args):
        observed.append(workflow.state)
        assert workflow.state == WorkflowState.COMPLETING
        return original_rebuild(self, *args)

    monkeypatch.setattr(CharacterStatsRepository, "rebuild_stats", rebuild)
    completed = workflow.confirm_save()
    assert completed.status == RoundStatus.COMPLETED
    assert workflow.state == WorkflowState.COMPLETED_NOTICE
    assert observed == [
        WorkflowState.CALCULATING,
        WorkflowState.CALCULATING,
        WorkflowState.COMPLETING,
    ]
    workflow.dismiss_completed()
    assert workflow.state == WorkflowState.DRAFT
    assert workflow.analysis is workflow.inputs is None
    assert workflow.post_run_choices == (None, None)


@pytest.mark.parametrize("editing", [False, True])
def test_calculation_failure_returns_to_correct_origin_and_keeps_committed_view(
    h, monkeypatch, editing
):
    workflow = h.workflow()
    workflow.set_inputs(COMMAND)
    locked = None
    if editing:
        locked = workflow.calculate()
        workflow.modify()
        workflow.set_inputs(replace(COMMAND, p_h_raw=80))
    before = h.capture()

    def fail(*args):
        assert workflow.state == WorkflowState.CALCULATING
        raise InjectedFailure("calculation persistence")

    monkeypatch.setattr(SnapshotRepository, "update" if editing else "insert", fail)
    with pytest.raises(InjectedFailure):
        workflow.calculate()
    assert workflow.state == (WorkflowState.PENDING_EDIT if editing else WorkflowState.DRAFT)
    assert workflow.analysis == locked
    assert h.capture() == before


def test_completion_failure_returns_to_confirmation_and_allows_retry(h, monkeypatch):
    workflow = h.workflow()
    workflow.set_inputs(COMMAND)
    workflow.calculate()
    workflow.choose_result(False)
    workflow.choose_include(True)
    before = h.capture()
    with monkeypatch.context() as patch:

        def fail(*args):
            assert workflow.state == WorkflowState.COMPLETING
            raise InjectedFailure("stats")

        patch.setattr(CharacterStatsRepository, "rebuild_stats", fail)
        with pytest.raises(InjectedFailure):
            workflow.confirm_save()
    assert workflow.state == WorkflowState.CONFIRM_SAVE
    assert workflow.post_run_choices == (False, True)
    assert h.capture() == before
    workflow.confirm_save()
    assert workflow.state == WorkflowState.COMPLETED_NOTICE


def test_void_workflow_returns_to_empty_draft(h):
    workflow = h.workflow()
    workflow.set_inputs(COMMAND)
    locked = workflow.calculate()
    result = workflow.void_pending("cancel")
    assert result.round_id == locked.round_id and result.status == RoundStatus.VOIDED
    assert workflow.state == WorkflowState.DRAFT
    assert workflow.analysis is workflow.inputs is None


def test_missing_inputs_and_invalid_choices_do_not_transition(h):
    workflow = h.workflow()
    with pytest.raises(InvalidWorkflowTransitionError):
        workflow.calculate()
    assert workflow.state == WorkflowState.DRAFT
    workflow.set_inputs(COMMAND)
    workflow.calculate()
    for action in (lambda: workflow.choose_result(1), lambda: workflow.choose_include(None)):
        with pytest.raises(InputValidationError):
            action()
        assert workflow.state == WorkflowState.PENDING_LOCKED
        assert workflow.post_run_choices == (None, None)
