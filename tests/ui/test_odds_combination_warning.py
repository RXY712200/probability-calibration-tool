"""Presentation-only odds warning, driven by the committed Application enum."""

import re
from dataclasses import replace

import pytest

from probability_calibration_tool.application.enums import WorkflowState as S
from probability_calibration_tool.application.reliability_views import ReliabilityResult
from probability_calibration_tool.application.reliability_views import StartupDisposition as D
from probability_calibration_tool.domain.enums import OddsCombinationStatus as O

from .helpers import calculate, click, widget_text


def test_double_positive_window_has_explicit_timing_warning(window):
    view = calculate(window, win="2.00", lose="3.00")
    assert view.subjective_odds.odds_combination_status == O.DOUBLE_POSITIVE_WINDOW
    panel = window.round.analysis
    warning = panel.combination_warning
    assert warning.isVisible()
    text = warning.text().lower()
    assert "warning" in text
    assert "input" in text and "multiplier" in text and "timing" in text
    assert panel.subjective.values["combination"].text() == "Double positive window"
    assert re.search(r"\b(win|loss|bet|stake|recommended|participate)\b", text) is None
    assert window.workflow.post_run_choices == (None, None)


@pytest.mark.parametrize("odds,status", [("1.50", O.NORMAL_OVERLAP), ("2.00", O.CRITICAL)])
def test_other_odds_status_has_no_double_positive_warning(window, odds, status):
    view = calculate(window, win=odds, lose=odds)
    assert view.subjective_odds.odds_combination_status == status
    warning = window.round.analysis.combination_warning
    assert warning.text() == "" and warning.isHidden()
    assert "input/multiplier timing" not in widget_text(window)
    assert window.round.analysis.subjective.values["combination"].text()


@pytest.mark.parametrize("raw,used", [("0", "1"), ("100", "99")])
def test_endpoint_note_and_odds_warning_coexist(window, raw, used):
    calculate(window, probability=raw, win="2.00", lose="3.00")
    panel = window.round.analysis
    assert panel.subjective.message is not panel.combination_warning
    assert panel.subjective.message.isVisible() and panel.combination_warning.isVisible()
    assert f"{raw}% entered" in panel.subjective.message.text()
    assert f"{used}% used" in panel.subjective.message.text()
    assert "input/multiplier timing" in panel.combination_warning.text()
    assert window.round.pre.probability.text() == raw


@pytest.mark.parametrize(
    "transition", ["no_analysis", "completed_new_draft", "void_new_draft", "safety"]
)
def test_stale_odds_warning_is_cleared_from_hidden_and_visible_widgets(window, transition):
    calculate(window, win="2.00", lose="3.00")
    old_warning = window.round.analysis.combination_warning.text()
    assert old_warning
    if transition == "no_analysis":
        window.round.analysis.render(None)
    elif transition == "completed_new_draft":
        click(window.round.post.result.buttons[True])
        click(window.round.post.include.buttons[False])
        click(window.round.post.save)
        click(window.round.new_round)
        assert window.workflow.state == S.DRAFT
    elif transition == "void_new_draft":
        click(window.round.post.void)
        click(window.round.post.confirm_void)
        assert window.workflow.state == S.DRAFT
    else:
        window.present_startup(ReliabilityResult(D.DATA_SAFETY_ERROR))
    assert window.round.analysis.combination_warning.text() == ""
    assert window.round.analysis.combination_warning.isHidden()
    assert old_warning not in widget_text(window)


@pytest.mark.parametrize("odds,status", [("1.50", O.NORMAL_OVERLAP), ("2.00", O.CRITICAL)])
def test_modify_warning_uses_committed_odds_until_recalculate(window, h, odds, status):
    committed = calculate(window, win="2.00", lose="3.00")
    panel = window.round.analysis
    committed_warning = panel.combination_warning.text()
    before = h.capture()
    click(window.round.pre.modify)
    window.round.pre.win_odds.setText(odds)
    window.round.pre.lose_odds.setText(odds)
    window.render_from_workflow()
    assert window.workflow.state == S.PENDING_EDIT
    assert window.workflow.analysis is committed
    assert panel.combination_warning.text() == committed_warning
    assert panel.combination_warning.isVisible()
    assert "Pending edits are not reflected until Recalculate succeeds" in panel.edit_note.text()
    assert h.capture() == before
    click(window.round.pre.primary)
    assert window.workflow.state == S.PENDING_LOCKED
    assert window.workflow.analysis.subjective_odds.odds_combination_status == status
    assert panel.combination_warning.text() == "" and panel.combination_warning.isHidden()
    assert committed_warning not in widget_text(window)


def test_warning_mapping_uses_authoritative_enum_not_input_odds(window):
    view = calculate(window, win="2.00", lose="3.00")
    # Controlled safe DTO: identical raw odds, different supplied authoritative status.
    # The presentation must map the enum, never reclassify the inputs.
    presentation = replace(
        view,
        subjective_odds=replace(view.subjective_odds, odds_combination_status=O.NORMAL_OVERLAP),
    )
    window.round.analysis.render(presentation)
    assert window.round.analysis.combination_warning.text() == ""
    assert "input/multiplier timing" not in widget_text(window)
