import re
from dataclasses import replace

import pytest

from probability_calibration_tool.application.commands import CalculateCommand
from probability_calibration_tool.application.enums import HistoricalDisplayState as H
from probability_calibration_tool.application.views import NonnumericHistoryView

from .helpers import calculate, click, widget_text


@pytest.fixture
def visible(h):
    h.seed_history(19, 1)
    return h.rounds.calculate(CalculateCommand(1, True, 70, "2.00", "3.00"))


@pytest.mark.parametrize("state", [H.HIDDEN, H.NO_HISTORY, H.INSUFFICIENT])
def test_stale_history_is_cleared_not_just_hidden(window, visible, state):
    panel = window.round.analysis
    panel.render(visible)
    assert panel.historical.values["probability"].text()
    panel.render(replace(visible, history=NonnumericHistoryView(state)))
    assert all(value.text() == "" for value in panel.historical.values.values())
    assert not re.search(r"\d", widget_text(panel.historical))
    assert panel.historical.message.text()


@pytest.mark.parametrize("history_case", ["hidden_valid", "no_history", "insufficient"])
def test_real_safe_view_leaks_no_history_numbers(window, h, history_case):
    if history_case == "hidden_valid":
        h.seed_history(19, 1)
    elif history_case == "insufficient":
        h.seed_history(1, 0)
    view = calculate(window, reference=history_case != "hidden_valid")
    expected = {
        "hidden_valid": H.HIDDEN,
        "no_history": H.NO_HISTORY,
        "insufficient": H.INSUFFICIENT,
    }
    assert view.history.state == expected[history_case]
    if history_case == "hidden_valid":
        assert h.snapshot(view.round_id).history_model_status.value == "valid"
    assert not re.search(r"\d", widget_text(window.round.analysis.historical))
    assert not re.search(r"\d", widget_text(window.recovery.analysis.historical))


@pytest.mark.parametrize("reset", ["complete", "void"])
def test_new_draft_clears_all_analysis_including_hidden_widgets(window, h, reset):
    h.seed_history(19, 1)
    calculate(window, reference=True)
    assert window.round.analysis.historical.values["probability"].text()
    if reset == "complete":
        click(window.round.post.result.buttons[True])
        click(window.round.post.include.buttons[True])
        click(window.round.post.save)
        click(window.round.new_round)
    else:
        click(window.round.post.void)
        click(window.round.post.confirm_void)
    for panel in (window.round.analysis, window.recovery.analysis):
        assert all(not v.text() for v in panel.historical.values.values())
        assert all(not v.text() for v in panel.subjective.values.values())
        assert not re.search(r"\d", widget_text(panel))
    assert window.round.pre.probability.text() == ""
    assert window.round.pre.win_odds.text() == window.round.pre.lose_odds.text() == ""
    assert window.round.post.result.value() is window.round.post.include.value() is None
    assert window.characters.value() == 1 and window.round.pre.reference.value() is True


def test_visible_subjective_and_history_are_separate_safe_cards(window, h):
    h.seed_history(19, 1)
    view = calculate(window, reference=True)
    assert view.history.state == H.VISIBLE
    panel = window.round.analysis
    assert panel.subjective is not panel.historical
    assert panel.layout().indexOf(panel.subjective) < panel.layout().indexOf(panel.historical)
    assert "Wins 19" in panel.historical.values["samples"].text()
    assert panel.subjective.values["probability"].text() == "70.0%"
    assert panel.historical.values["probability"].text()
    assert "Recommend" not in widget_text(window)


def test_presenting_safety_page_clears_off_page_analysis(window, h):
    from probability_calibration_tool.application.reliability_views import (
        ReliabilityResult,
        StartupDisposition,
    )

    h.seed_history(19, 1)
    calculate(window, reference=True)
    window.present_startup(ReliabilityResult(StartupDisposition.DATA_SAFETY_ERROR))
    assert all(not v.text() for v in window.round.analysis.historical.values.values())
    assert all(not v.text() for v in window.recovery.analysis.historical.values.values())
