import pytest

from probability_calibration_tool.application.enums import WorkflowState
from probability_calibration_tool.application.errors import BusinessRuleError, InputValidationError
from probability_calibration_tool.infrastructure.backup import BackupCategory

from .helpers import begin_correction, click, complete, scalar


def capture_errors_and_recent(desk, monkeypatch, *, recent_failure=True):
    errors, attempts = [], []
    report = desk.session.report_unexpected
    create = desk.host.backup.create

    def recorded_report(exc):
        error = report(exc)
        errors.append(error)
        return error

    def recorded_create(category, reason=None):
        attempts.append(category)
        if category == BackupCategory.RECENT and recent_failure:
            raise OSError("injected Recent failure")
        return create(category, reason)

    monkeypatch.setattr(desk.session, "report_unexpected", recorded_report)
    monkeypatch.setattr(desk.host.backup, "create", recorded_create)
    return errors, attempts


def fail_refresh():
    raise RuntimeError("private SELECT details: injected refresh failure")


def assert_error_priority(desk, errors, *, warning=True):
    assert len(errors) == 1
    error = errors[0]
    banner = desk.window.banner
    assert banner.isVisible()
    assert banner.property("severity") == "error"
    text = banner.message.text()
    assert error.message in text and error.error_id in text
    assert ("Recent backup failed" in text) is warning
    assert "private SELECT" not in text and "Traceback" not in text
    log = desk.runtime.paths.log_file.read_text()
    assert error.error_id in log and "Traceback" in log
    assert not desk.session.take_warnings()


def prepare_regime(desk):
    desk.window.show_maintenance()
    desk.window.maintenance.table.selectRow(0)
    click(desk.window.maintenance.start)


def test_regime_commit_recent_failure_refresh_failure_retains_unexpected_id(desk, monkeypatch):
    prepare_regime(desk)
    errors, attempts = capture_errors_and_recent(desk, monkeypatch)
    monkeypatch.setattr(desk.session, "maintenance_rows", fail_refresh)
    desk.window._start_regime()
    desk.window._start_regime()
    assert scalar(desk.path, "SELECT count(*) FROM history_regimes WHERE character_id=1") == 2
    assert attempts == [BackupCategory.RECENT]
    assert not desk.backups()
    assert_error_priority(desk, errors)


@pytest.mark.parametrize("refresh", ["correction_candidates", "maintenance_rows"])
def test_correction_commit_recent_failure_refresh_failure_retains_unexpected_id(
    desk, monkeypatch, refresh
):
    original = complete(desk.window)
    click(desk.window.round.new_round)
    begin_correction(desk.window)
    errors, attempts = capture_errors_and_recent(desk, monkeypatch)
    monkeypatch.setattr(desk.session, refresh, fail_refresh)
    desk.window._confirm_correction()
    desk.window._confirm_correction()
    assert scalar(desk.path, "SELECT count(*) FROM rounds") == 2
    assert scalar(desk.path, "SELECT status FROM rounds WHERE round_id=?", (original,)) == "voided"
    assert (
        scalar(
            desk.path,
            "SELECT count(*) FROM rounds WHERE supersedes_round_id=? AND status='completed'",
            (original,),
        )
        == 1
    )
    assert scalar(desk.path, "SELECT losses FROM character_stats WHERE character_id=1") == 1
    assert attempts == [BackupCategory.SAFETY, BackupCategory.RECENT]
    assert len(desk.backups(BackupCategory.SAFETY)) == 1
    assert len(desk.backups()) == 1  # the original completion's backup is unchanged
    assert_error_priority(desk, errors)


@pytest.mark.parametrize("mode", ["warning_only", "error_only"])
def test_single_failure_presentation_remains_warning_or_error(desk, monkeypatch, mode):
    prepare_regime(desk)
    errors, attempts = capture_errors_and_recent(
        desk, monkeypatch, recent_failure=mode == "warning_only"
    )
    if mode == "error_only":
        monkeypatch.setattr(desk.session, "maintenance_rows", fail_refresh)
    desk.window._start_regime()
    assert attempts == [BackupCategory.RECENT]
    assert scalar(desk.path, "SELECT count(*) FROM history_regimes WHERE character_id=1") == 2
    if mode == "error_only":
        assert_error_priority(desk, errors, warning=False)
    else:
        assert errors == []
        assert desk.window.banner.property("severity") == "warning"
        assert "Recent backup failed" in desk.window.banner.message.text()
        assert desk.window.maintenance.rows[0].active_regime_number == 2


def test_combined_presentation_failure_logs_once_without_recursive_render_or_retry(
    desk, monkeypatch
):
    prepare_regime(desk)
    errors, attempts = capture_errors_and_recent(desk, monkeypatch)
    monkeypatch.setattr(desk.session, "maintenance_rows", fail_refresh)
    rendered = []

    def fail_presentation(text, severity="information"):
        rendered.append((text, severity))
        raise OSError("injected combined presentation failure")

    monkeypatch.setattr(desk.window.banner, "show_message", fail_presentation)
    desk.window._start_regime()
    desk.window._start_regime()
    assert len(rendered) == len(errors) == 1
    assert errors[0].error_id in rendered[0][0]
    assert "Recent backup failed" in rendered[0][0]
    assert rendered[0][1] == "error"
    assert attempts == [BackupCategory.RECENT]
    assert scalar(desk.path, "SELECT count(*) FROM history_regimes WHERE character_id=1") == 2
    log = desk.runtime.paths.log_file.read_text()
    assert log.count("Error presentation failed:") == 1
    assert "injected combined presentation failure" in log
    assert errors[0].error_id in log


def test_post_commit_render_failure_also_keeps_recent_warning_below_error(desk, monkeypatch):
    errors, attempts = capture_errors_and_recent(desk, monkeypatch)
    render = desk.window._render
    failed_renders = []

    def fail_completed():
        if desk.session.workflow.state == WorkflowState.COMPLETED_NOTICE:
            failed_renders.append("completed")
            raise RuntimeError("injected completed rendering failure")
        return render()

    monkeypatch.setattr(desk.window, "_render", fail_completed)
    complete(desk.window)
    desk.window._save()
    assert failed_renders == ["completed"]
    assert attempts == [BackupCategory.RECENT]
    assert scalar(desk.path, "SELECT count(*) FROM rounds WHERE status='completed'") == 1
    assert_error_priority(desk, errors)


@pytest.mark.parametrize(
    "error",
    [
        BusinessRuleError("Refresh unavailable."),
        InputValidationError("reason", "Refresh input unavailable."),
    ],
)
def test_expected_error_also_outranks_operational_warning(desk, monkeypatch, error):
    prepare_regime(desk)
    errors, attempts = capture_errors_and_recent(desk, monkeypatch)

    def fail_expected():
        raise error

    monkeypatch.setattr(desk.session, "maintenance_rows", fail_expected)
    desk.window._start_regime()
    assert attempts == [BackupCategory.RECENT]
    assert errors == []
    assert desk.window.banner.property("severity") == "error"
    assert str(error) in desk.window.banner.message.text()
    assert "Recent backup failed" in desk.window.banner.message.text()
    assert scalar(desk.path, "SELECT count(*) FROM history_regimes WHERE character_id=1") == 2
