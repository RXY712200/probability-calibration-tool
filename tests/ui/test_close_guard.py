from types import SimpleNamespace

import pytest
from PySide6.QtGui import QCloseEvent

from probability_calibration_tool.application.enums import WorkflowState as S
from probability_calibration_tool.ui.close_guard import CloseDecision as C
from probability_calibration_tool.ui.close_guard import close_decision

from .helpers import calculate, click


@pytest.mark.parametrize(
    "state,choices,expected",
    [
        (S.DRAFT, (None, None), C.ACCEPT),
        (S.PENDING_LOCKED, (None, None), C.ACCEPT),
        (S.PENDING_EDIT, (None, None), C.CONFIRM_EDITS),
        (S.PENDING_LOCKED, (True, None), C.CONFIRM_CHOICES),
        (S.PENDING_LOCKED, (None, False), C.CONFIRM_CHOICES),
        (S.CONFIRM_SAVE, (False, True), C.CONFIRM_CHOICES),
        (S.CALCULATING, (None, None), C.IGNORE),
        (S.COMPLETING, (True, True), C.IGNORE),
        (S.RECOVERY, (None, None), C.ACCEPT),
        (S.RECOVERY_ERROR, (None, None), C.ACCEPT),
        (S.COMPLETED_NOTICE, (True, True), C.ACCEPT),
    ],
)
def test_close_policy(state, choices, expected):
    assert close_decision(state, choices) == expected


@pytest.mark.parametrize("mode", ["draft", "locked", "edit", "choices", "confirm"])
@pytest.mark.parametrize("answer", [False, True])
def test_real_close_event_never_mutates_database(h, make_window, mode, answer):
    prompts = []
    window = make_window(close_confirmation=lambda _, decision: prompts.append(decision) or answer)
    if mode != "draft":
        calculate(window)
    if mode == "edit":
        click(window.round.pre.modify)
        window.round.pre.probability.setText("88")
    elif mode in ("choices", "confirm"):
        click(window.round.post.result.buttons[True])
        if mode == "confirm":
            click(window.round.post.include.buttons[False])
    before = h.capture()
    event = QCloseEvent()
    window.closeEvent(event)
    assert event.isAccepted() == (answer or mode in ("draft", "locked"))
    assert bool(prompts) == (mode in ("edit", "choices", "confirm"))
    assert h.capture() == before


@pytest.mark.parametrize("state", [S.CALCULATING, S.COMPLETING])
def test_busy_close_is_ignored_without_mutation(window, state):
    # Controlled public-state spy, no duplicate transition logic.
    original = window.workflow
    window.workflow = SimpleNamespace(state=state, post_run_choices=(None, None))
    try:
        event = QCloseEvent()
        window.closeEvent(event)
        assert not event.isAccepted()
    finally:
        window.workflow = original
