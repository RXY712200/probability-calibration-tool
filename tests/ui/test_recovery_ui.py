import re

import pytest

from probability_calibration_tool.application.commands import CalculateCommand
from probability_calibration_tool.application.enums import HistoricalDisplayState as H
from probability_calibration_tool.application.enums import WorkflowState as S

from .helpers import click, widget_text


@pytest.mark.parametrize("history_case", ["hidden", "no_history", "insufficient", "visible"])
def test_real_recovery_safe_render_and_continue_without_recalculate(
    h, make_window, monkeypatch, history_case
):
    if history_case in ("hidden", "visible"):
        h.seed_history(19, 1)
    elif history_case == "insufficient":
        h.seed_history(1, 0)
    view = h.rounds.calculate(CalculateCommand(1, history_case != "hidden", 70, "2.00", "3.00"))
    before = h.capture()
    window = make_window()

    def forbidden(*args):
        pytest.fail("Recovery must not calculate/recalculate")

    monkeypatch.setattr(h.rounds, "calculate", forbidden)
    monkeypatch.setattr(h.rounds, "recalculate", forbidden)
    window.inspect_recovery()
    assert window.workflow.state == S.RECOVERY
    assert window.stack.currentWidget() is window.recovery
    assert window.workflow.analysis is None  # Inspection never continues Workflow.
    assert "2.00" in window.recovery.facts.text()
    if view.history.state != H.VISIBLE:
        assert not re.search(r"\d", widget_text(window.recovery.analysis.historical))
    else:
        assert window.recovery.analysis.historical.values["probability"].text()
    click(window.recovery.continue_button)
    assert window.workflow.state == S.PENDING_LOCKED
    assert window.workflow.analysis.round_id == view.round_id
    assert not window.round.pre.modify.isVisible()
    assert window.round.post.result.value() is window.round.post.include.value() is None
    assert all(not v.text() for v in window.recovery.analysis.historical.values.values())
    assert h.capture() == before


def test_recovery_does_not_create_persisted_session_preferences(h, make_window):
    h.rounds.calculate(CalculateCommand(18, False, 70, "2.00", "3.00"))
    window = make_window()
    window.inspect_recovery()
    click(window.recovery.continue_button)
    assert window.characters.value() == 18
    click(window.round.post.result.buttons[False])
    click(window.round.post.include.buttons[False])
    click(window.round.post.save)
    click(window.round.new_round)
    assert window.characters.value() is None
    assert window.round.pre.reference.value() is None


def test_no_pending_inspection_stays_draft_without_error(window):
    window.inspect_recovery()
    assert window.workflow.state == S.DRAFT
    assert window.stack.currentWidget() is window.round
    assert window.banner.message.text() == ""
