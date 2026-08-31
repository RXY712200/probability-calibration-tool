import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from probability_calibration_tool.application.enums import WorkflowState as S

from .helpers import calculate, click, fill


def test_first_run_defaults(window):
    pre, post = window.round.pre, window.round.post
    assert len(window.characters.buttons) == 34
    assert window.characters.value() is None and pre.reference.value() is None
    assert pre.probability.text() == pre.win_odds.text() == pre.lose_odds.text() == ""
    assert post.result.value() is post.include.value() is None
    assert window.workflow.analysis is None
    assert all(not v.text() for v in window.round.analysis.historical.values.values())
    assert window.round.analysis.isHidden()


def test_exact_matrix_mapping_and_exclusive_choices(window, h):
    expected = {r.character_id: r.display_name for r in h.maintenance.list_characters()}
    for key, widget in window.characters.buttons.items():
        assert widget.text().replace("&&", "&") == expected[key]
        assert widget.accessibleName() == expected[key]
        index = window.characters.grid.indexOf(widget)
        row, col, height, width = window.characters.grid.getItemPosition(index)
        assert (row, col, height, width) == ((key - 1) % 17 + 1, (key - 1) // 17, 1, 1)
        click(widget)
        assert sum(w.isChecked() for w in window.characters.buttons.values()) == 1
    assert window.characters.buttons[34].text() == "Tainted Jacob"
    for choice in (True, False, True):
        click(window.round.pre.reference.buttons[choice])
        assert window.round.pre.reference.value() is choice
        assert sum(b.isChecked() for b in window.round.pre.reference.buttons.values()) == 1


@pytest.mark.parametrize("field", ["probability", "win_odds", "lose_odds"])
@pytest.mark.parametrize("key", [Qt.Key.Key_Return, Qt.Key.Key_Enter])
@pytest.mark.parametrize("editing", [False, True])
def test_enter_never_calculates(window, monkeypatch, field, key, editing):
    fill(window)
    if editing:
        click(window.round.pre.primary)
        click(window.round.pre.modify)
    calls = []
    monkeypatch.setattr(window.workflow, "calculate", lambda: calls.append("calculate"))
    widget = getattr(window.round.pre, field)
    widget.setFocus()
    QTest.keyClick(widget, key)
    assert calls == []
    assert not window.round.pre.primary.isDefault()
    assert not window.round.pre.primary.autoDefault()


@pytest.mark.parametrize(
    "field,text,error",
    [
        ("probability", "105", "subjective_probability"),
        ("probability", "garbage", "subjective_probability"),
        ("probability", "1.5", "subjective_probability"),
        ("win_odds", "2,00", "win_odds"),
        ("win_odds", "1e2", "win_odds"),
        ("lose_odds", "NaN", "lose_odds"),
        ("lose_odds", "0.9", "lose_odds"),
    ],
)
def test_inline_errors_preserve_raw_text(window, field, text, error):
    fill(window)
    widget = getattr(window.round.pre, field)
    assert widget.validator() is None
    widget.setText(text)
    click(window.round.pre.primary)
    assert window.workflow.state == S.DRAFT
    assert widget.text() == text
    assert window.round.pre.errors[error].text()
    assert window.banner.isHidden()
    assert window.workflow.analysis is None


@pytest.mark.parametrize("raw,used", [("0", "1"), ("100", "99")])
def test_endpoint_note_preserves_raw_input(window, raw, used):
    calculate(window, probability=raw)
    assert window.round.pre.probability.text() == raw
    note = window.round.analysis.subjective.message.text()
    assert f"{raw}% entered" in note and f"{used}% used" in note


def test_valid_calculate_locks_fields_and_preserves_odds(window):
    calculate(window)
    assert window.workflow.state == S.PENDING_LOCKED
    assert window.round.pre.probability.isReadOnly()
    assert window.round.pre.win_odds.isReadOnly()
    assert window.round.pre.lose_odds.isReadOnly()
    assert not window.characters.buttons[1].isEnabled()
    assert not window.round.pre.reference.isEnabled()
    assert window.round.pre.win_odds.text() == "2.00"
    assert window.round.pre.lose_odds.text() == "3.00"
    assert window.round.pre.modify.isVisible()
    assert window.round.post.isVisible()
