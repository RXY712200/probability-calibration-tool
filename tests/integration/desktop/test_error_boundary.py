import re

import pytest

from probability_calibration_tool.application.desktop_session import DisposedSessionError
from probability_calibration_tool.application.enums import WorkflowState as S

from .helpers import COMMAND, calculate, click, complete, fail_recent, scalar


def test_unexpected_error_id_safe_ui_and_matching_full_traceback_log(desk, monkeypatch):
    def fail(*args):
        raise RuntimeError("SELECT secret FROM rounds at C:/private/database.db")

    monkeypatch.setattr(desk.session.workflow._target._rounds._rounds, "calculate", fail)
    calculate(desk.window)
    content = desk.window.banner.message.text()
    assert "The operation could not be completed" in content
    error_id = re.search(r"Error ID: (\S+)", content)[1]
    assert all(
        secret not in content for secret in ("SELECT", "private", "Traceback", "RuntimeError")
    )
    log = desk.runtime.paths.log_file.read_text()
    assert error_id in log and "Traceback" in log and "SELECT secret" in log
    assert desk.session.workflow.state == S.DRAFT
    assert scalar(desk.path, "SELECT count(*) FROM rounds") == 0


def test_committed_calculate_render_failure_does_not_retry(desk, monkeypatch):
    original = desk.window.round.analysis.render
    failed_renders = []

    def render(view, **kwargs):
        if view is not None:
            failed_renders.append(view.round_id)
            raise RuntimeError("injected analysis presentation failure")
        return original(view, **kwargs)

    monkeypatch.setattr(desk.window.round.analysis, "render", render)
    view = calculate(desk.window)
    assert failed_renders == [view.round_id]
    assert scalar(desk.path, "SELECT count(*) FROM rounds") == 1
    assert desk.session.workflow.state == S.PENDING_LOCKED
    assert "Error ID" in desk.window.banner.message.text()
    assert not desk.backups()


def test_committed_complete_render_failure_does_not_retry(desk, monkeypatch):
    render = desk.window._render
    calls = []

    def fail_completed():
        if desk.session.workflow.state == S.COMPLETED_NOTICE:
            calls.append("failed-render")
            raise RuntimeError("injected completed render failure")
        return render()

    monkeypatch.setattr(desk.window, "_render", fail_completed)
    complete(desk.window)
    desk.window._save()  # queued duplicate is consumed, even after presentation failure
    assert calls == ["failed-render"]
    assert scalar(desk.path, "SELECT status FROM rounds") == "completed"
    assert len(desk.backups()) == 1


def test_regime_refresh_failure_does_not_repeat_successful_business_commit(desk, monkeypatch):
    desk.window.show_maintenance()
    desk.window.maintenance.table.selectRow(0)
    click(desk.window.maintenance.start)

    def fail():
        raise RuntimeError("injected maintenance refresh failure")

    monkeypatch.setattr(desk.session, "maintenance_rows", fail)
    desk.window._start_regime()
    desk.window._start_regime()
    assert scalar(desk.path, "SELECT count(*) FROM history_regimes WHERE character_id=1") == 2
    assert len(desk.backups()) == 1
    assert "Error ID" in desk.window.banner.message.text()


def test_warning_presentation_failure_does_not_retry_commit(desk, monkeypatch):
    fail_recent(desk, monkeypatch)
    show = desk.window.banner.show_message

    def fail_warning(text, severity="information"):
        if severity == "warning":
            raise RuntimeError("injected warning rendering failure")
        return show(text, severity)

    monkeypatch.setattr(desk.window.banner, "show_message", fail_warning)
    complete(desk.window)
    desk.window._save()
    assert scalar(desk.path, "SELECT count(*) FROM rounds") == 1
    assert scalar(desk.path, "SELECT status FROM rounds") == "completed"
    assert desk.session.workflow.state == S.COMPLETED_NOTICE
    assert "Error ID" in desk.window.banner.message.text()


def test_input_errors_inline_and_rejected_checkable_signal_resyncs_authoritative_choices(desk):
    calculate(desk.window)
    click(desk.window.round.post.result.buttons[True])
    click(desk.window.round.post.include.buttons[True])
    pair = desk.window.round.post.result
    pair.sync(False)  # widget changed before the rejected queued signal
    pair.chosen.emit(False)
    assert desk.session.workflow.post_run_choices == (True, True)
    assert pair.value() is True
    assert desk.window.banner.property("severity") == "error"


@pytest.mark.parametrize(
    "operation",
    [
        "inputs",
        "calculate",
        "modify",
        "result",
        "include",
        "save",
        "void",
        "back",
        "dismiss",
        "inspect",
        "continue",
        "maintenance",
        "candidates",
        "regime",
        "correction",
        "restore",
        "catalog",
        "warnings",
        "admin",
    ],
)
def test_disposed_session_revokes_all_integration_workflow_actions(desk, operation):
    session, workflow = desk.session, desk.session.workflow
    callbacks = {
        "inputs": lambda: workflow.set_inputs(COMMAND),
        "calculate": workflow.calculate,
        "modify": workflow.modify,
        "result": lambda: workflow.choose_result(True),
        "include": lambda: workflow.choose_include(True),
        "save": workflow.confirm_save,
        "void": workflow.void_pending,
        "back": workflow.back,
        "dismiss": workflow.dismiss_completed,
        "inspect": workflow.inspect_recovery,
        "continue": workflow.continue_recovery,
        "maintenance": session.maintenance_rows,
        "candidates": session.correction_candidates,
        "regime": lambda: session.start_regime(object(), None),
        "correction": lambda: session.correct(object(), False, True, "reason"),
        "restore": lambda: session.restore(object()),
        "catalog": session.catalog.refresh,
        "warnings": session.take_warnings,
        "admin": session.can_admin,
    }
    callback = callbacks[operation]
    desk.host.dispose()
    with pytest.raises(DisposedSessionError):
        callback()
