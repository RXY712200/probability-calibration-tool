from probability_calibration_tool.application.enums import WorkflowState as S
from probability_calibration_tool.application.errors import InvalidWorkflowTransitionError

from .helpers import calculate, click, fill


def test_real_workflow_calculate_modify_recalculate(window, h):
    calculate(window)
    old = window.workflow.analysis
    snapshot = h.snapshot(old.round_id)
    click(window.round.pre.modify)
    assert window.workflow.state == S.PENDING_EDIT
    assert window.round.analysis.edit_note.text()
    old_text = window.round.analysis.subjective.values["probability"].text()
    window.round.pre.probability.setText("80")
    assert window.round.analysis.subjective.values["probability"].text() == old_text
    assert h.snapshot(old.round_id) == snapshot
    click(window.round.pre.primary)
    assert window.workflow.state == S.PENDING_LOCKED
    assert window.workflow.analysis.round_id == old.round_id
    assert window.workflow.analysis.revision_count == old.revision_count + 1
    assert h.record(old.round_id).p_h_raw == 80


def test_failed_recalculate_preserves_candidate_and_committed_analysis(window, h):
    calculate(window)
    old = window.workflow.analysis
    before = h.capture()
    click(window.round.pre.modify)
    window.round.pre.probability.setText("invalid candidate")
    click(window.round.pre.primary)
    assert window.workflow.state == S.PENDING_EDIT
    assert window.workflow.analysis is old
    assert window.round.pre.probability.text() == "invalid candidate"
    assert window.round.analysis.edit_note.text()
    assert window.round.pre.errors["subjective_probability"].text()
    assert h.capture() == before


def test_audit_lock_post_choices_back_and_rejected_widget_signal(window, monkeypatch):
    calculate(window)
    post = window.round.post
    assert window.round.pre.modify.isVisible()
    assert post.result.value() is post.include.value() is None
    click(post.result.buttons[True])
    assert not window.round.pre.modify.isVisible()
    click(post.include.buttons[True])
    assert window.workflow.state == S.CONFIRM_SAVE
    assert post.confirmation.isVisible()
    click(post.back)
    assert window.workflow.state == S.PENDING_LOCKED
    assert post.result.value() is True and post.include.value() is True
    assert not window.round.pre.modify.isVisible()
    click(post.result.buttons[False])
    assert window.workflow.state == S.CONFIRM_SAVE
    click(post.back)

    def reject(value):
        raise InvalidWorkflowTransitionError("Rejected choice")

    monkeypatch.setattr(window.workflow, "choose_result", reject)
    click(post.result.buttons[True])
    assert post.result.value() is False
    assert "Rejected choice" in window.banner.message.text()


def test_completed_reset_and_session_only_retention(window, make_window):
    calculate(window)
    click(window.round.post.result.buttons[True])
    click(window.round.post.include.buttons[False])
    click(window.round.post.save)
    assert window.workflow.state == S.COMPLETED_NOTICE
    assert window.round.completed.isVisible()
    click(window.round.new_round)
    assert window.workflow.state == S.DRAFT
    assert window.round.pre.probability.text() == ""
    assert window.round.pre.win_odds.text() == window.round.pre.lose_odds.text() == ""
    assert window.characters.value() == 1
    assert window.round.pre.reference.value() is False
    assert window.round.post.result.value() is window.round.post.include.value() is None
    restarted = make_window()
    assert restarted.characters.value() is None
    assert restarted.round.pre.reference.value() is None


def test_void_in_page_confirmation_does_not_delete(window, h):
    view = calculate(window)
    click(window.round.post.void)
    assert window.round.post.void_confirmation.isVisible()
    click(window.round.post.cancel_void)
    assert h.record(view.round_id).status.value == "pending"
    click(window.round.post.void)
    window.round.post.reason.setText("Optional reason")
    click(window.round.post.confirm_void)
    assert window.workflow.state == S.DRAFT
    assert h.record(view.round_id).status.value == "voided"
    assert h.snapshot(view.round_id) is not None
    assert window.round.analysis.isHidden()


def test_official_analysis_not_shown_until_calculate_returns(window, h, monkeypatch):
    original = h.rounds.calculate

    def observe(command):
        assert window.workflow.state == S.CALCULATING
        window.render_from_workflow()
        assert window.workflow.analysis is None
        assert window.round.analysis.isHidden()
        assert window.round.pre.probability.isReadOnly()
        return original(command)

    monkeypatch.setattr(h.rounds, "calculate", observe)
    fill(window)
    click(window.round.pre.primary)
    assert window.workflow.state == S.PENDING_LOCKED
    assert window.round.analysis.isVisible()


def test_unexpected_error_uses_safe_phase4_dto(window, h, monkeypatch, caplog):
    def fail(command):
        raise RuntimeError("PRIVATE_PATH SQL SECRET")

    monkeypatch.setattr(h.rounds, "calculate", fail)
    calculate(window)
    message = window.banner.message.text()
    assert "Error ID:" in message
    assert "PRIVATE_PATH" not in message and "Traceback" not in message
    error_id = message.split("Error ID: ")[1]
    assert error_id in caplog.text and "PRIVATE_PATH SQL SECRET" in caplog.text
    assert "Traceback" in caplog.text


def test_completing_disables_conflicting_controls_and_rejects_close(window, h, monkeypatch):
    from PySide6.QtGui import QCloseEvent

    calculate(window)
    click(window.round.post.result.buttons[True])
    click(window.round.post.include.buttons[True])
    original = h.rounds.complete_pending

    def observe(*args):
        assert window.workflow.state == S.COMPLETING
        window.render_from_workflow()
        assert not window.round.post.save.isEnabled()
        assert not window.round.post.result.isEnabled()
        assert not window.round.post.include.isEnabled()
        assert not window.maintenance_button.isEnabled()
        event = QCloseEvent()
        window.closeEvent(event)
        assert not event.isAccepted()
        return original(*args)

    monkeypatch.setattr(h.rounds, "complete_pending", observe)
    click(window.round.post.save)
    assert window.workflow.state == S.COMPLETED_NOTICE
