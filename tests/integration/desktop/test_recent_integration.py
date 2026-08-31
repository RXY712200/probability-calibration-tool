from probability_calibration_tool.application.enums import WorkflowState as S

from .helpers import COMMAND, calculate, click, complete, fail_recent, scalar


def test_all_nontrigger_interactions_leave_recent_empty(desk):
    window = desk.window
    window.show_maintenance()
    window.show_correction()
    window.show_restore()
    window.show_round()
    calculate(window)
    click(window.round.pre.modify)
    window.round.pre.probability.setText("71")
    click(window.round.pre.primary)
    click(window.round.post.result.buttons[True])
    click(window.round.post.include.buttons[False])
    click(window.round.post.back)
    window.show_maintenance()
    assert not desk.backups()


def test_recovery_inspection_continue_do_not_create_recent(desk):
    from probability_calibration_tool.application.reliability_views import (
        ReliabilityResult,
        StartupDisposition,
    )

    desk.session.workflow.set_inputs(COMMAND)
    desk.session.workflow.calculate()
    desk.runtime.result = ReliabilityResult(StartupDisposition.READY_RECOVERY)
    desk.host.show_initial_state()
    assert not desk.backups()
    click(desk.window.recovery.continue_button)
    assert not desk.backups()


def test_complete_recent_failure_keeps_success_and_warning_after_render(desk, monkeypatch):
    fail_recent(desk, monkeypatch)
    round_id = complete(desk.window)
    assert desk.window.workflow.state == S.COMPLETED_NOTICE
    assert desk.window.round.completed.isVisible()
    assert (
        scalar(desk.path, "SELECT status FROM rounds WHERE round_id=?", (round_id,)) == "completed"
    )
    assert scalar(desk.path, "SELECT wins FROM character_stats WHERE character_id=1") == 1
    assert "Recent backup failed" in desk.window.banner.message.text()
    assert desk.window.banner.isVisible()
    assert not desk.backups()


def test_void_recent_failure_keeps_fresh_draft_and_warning(desk, monkeypatch):
    fail_recent(desk, monkeypatch)
    view = calculate(desk.window)
    click(desk.window.round.post.void)
    click(desk.window.round.post.confirm_void)
    assert desk.window.workflow.state == S.DRAFT
    assert desk.window.round.pre.probability.text() == ""
    assert (
        scalar(desk.path, "SELECT status FROM rounds WHERE round_id=?", (view.round_id,))
        == "voided"
    )
    assert "Recent backup failed" in desk.window.banner.message.text()
    assert desk.window.banner.isVisible()


def test_void_success_creates_one_real_recent_and_consumes_confirmation(desk):
    calculate(desk.window)
    desk.window._show_void(True)
    desk.window._void()
    desk.window._void()
    assert len(desk.backups()) == 1
    assert scalar(desk.backups()[0].path, "SELECT status FROM rounds") == "voided"


def test_complete_double_callback_does_not_retry_business_or_recent(desk, monkeypatch):
    calculate(desk.window)
    click(desk.window.round.post.result.buttons[True])
    click(desk.window.round.post.include.buttons[True])
    original = desk.session.workflow._target.confirm_save
    calls = []

    def confirm():
        calls.append("save")
        return original()

    monkeypatch.setattr(desk.session.workflow._target, "confirm_save", confirm)
    desk.window._save()
    desk.window._save()
    assert calls == ["save"]
    assert len(desk.backups()) == 1
