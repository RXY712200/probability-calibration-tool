import sqlite3
from contextlib import closing

import pytest
from PySide6.QtCore import QTimer

from probability_calibration_tool.application.desktop_session import DisposedSessionError
from probability_calibration_tool.application.enums import WorkflowState as S
from probability_calibration_tool.application.reliability_views import StartupDisposition as D
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.desktop_host import DesktopHost
from probability_calibration_tool.infrastructure.backup import BackupCategory
from probability_calibration_tool.ui.safety_window import SafetyWindow

from .helpers import COMMAND, calculate, click, rows, scalar


def prepare_restore(desk):
    candidate = desk.backups(BackupCategory.DAILY)[0].path
    ticket = desk.session.begin_regime(1)
    desk.session.start_regime(ticket, "change live")
    handles = desk.session.catalog.refresh()
    handle = next(
        row.candidate_id
        for row in handles
        if desk.session.catalog.resolve(row.candidate_id) == candidate
    )
    return candidate, desk.session.begin_restore(handle)


def test_real_normal_restore_replaces_session_workflow_and_all_page_caches(desk):
    _, ticket = prepare_restore(desk)
    old, old_window = desk.session, desk.window
    old_workflow = old.workflow
    captured_calculate = old_workflow.calculate
    previous = desk.runtime.result
    result = old.restore(ticket)
    assert desk.runtime.result is result and result is not previous
    assert result.disposition == D.READY_DRAFT
    assert old.disposed and old_window._disposed
    assert desk.session is not old and desk.session.workflow is not old_workflow
    assert desk.session.maintenance_rows()[0].active_regime_number == 1
    assert not desk.window.maintenance.rows and not desk.window.correction.rows
    assert not desk.window.restore_page.rows
    for action in (
        captured_calculate,
        lambda: old_workflow.state,
        old.maintenance_rows,
        old.correction_candidates,
        old.catalog.refresh,
        lambda: old.restore(ticket),
    ):
        with pytest.raises(DisposedSessionError):
            action()
    assert len(desk.backups(BackupCategory.SAFETY)) == 1
    assert scalar(desk.path, "PRAGMA integrity_check") == "ok"


@pytest.mark.parametrize(
    "fault", ["corrupt", "newer", "safety", "replace", "candidate_sidecar", "active_uow"]
)
def test_pre_replacement_failure_preserves_identical_runtime_session_and_calculate(
    desk, monkeypatch, fault
):
    candidate, ticket = prepare_restore(desk)
    old, old_workflow, previous = desk.session, desk.session.workflow, desk.runtime.result
    before = rows(desk.path, "history_regimes")

    def fail(*args):
        raise OSError("injected pre-replacement failure")

    if fault == "corrupt":
        candidate.write_bytes(b"invalid candidate")
    elif fault == "newer":
        with closing(sqlite3.connect(candidate)) as db:
            db.execute("PRAGMA user_version=999")
    elif fault == "safety":
        monkeypatch.setattr(desk.host.restore_service.safety, "create_verified_safety_backup", fail)
    elif fault == "replace":
        monkeypatch.setattr(desk.host.restore_service.engine, "replace", fail)
    elif fault == "candidate_sidecar":
        candidate.with_name(candidate.name + "-wal").write_bytes(b"unexplained sidecar")
    if fault == "active_uow":
        with desk.runtime.uow_factory()() as uow:
            result = desk.window._invoke(lambda: old.restore(ticket))
            assert len(uow.characters.list_all()) == 34
    else:
        result = desk.window._invoke(lambda: old.restore(ticket))
    assert result.disposition == D.DATA_SAFETY_ERROR
    assert desk.runtime.result is previous
    assert desk.session is old and desk.session.workflow is old_workflow and not old.disposed
    assert rows(desk.path, "history_regimes") == before
    assert "did not replace" in desk.window.banner.message.text()
    assert calculate(desk.window) is not None


def test_restore_pending_builds_new_workflow_inspects_without_auto_continue(desk):
    original = calculate(desk.window)
    pending_backup = desk.host.backup.create(BackupCategory.DAILY)
    # Daily is once per day, so use a real dedicated Safety candidate for pending content.
    assert pending_backup.created is False
    pending_backup = desk.host.backup.create(BackupCategory.SAFETY, "pre_restore")
    click(desk.window.round.post.result.buttons[True])
    click(desk.window.round.post.include.buttons[True])
    click(desk.window.round.post.save)
    click(desk.window.round.new_round)
    old = desk.session
    candidates = old.catalog.refresh()
    handle = next(
        c.candidate_id
        for c in candidates
        if old.catalog.resolve(c.candidate_id) == pending_backup.path
    )
    result = old.restore(old.begin_restore(handle))
    assert result.disposition == D.READY_RECOVERY
    assert desk.session is not old and old.disposed
    assert desk.session.workflow.state == S.RECOVERY
    assert desk.session.workflow.analysis is None
    assert desk.window.stack.currentWidget() is desk.window.recovery
    click(desk.window.recovery.continue_button)
    assert desk.session.workflow.analysis == original
    assert not desk.session.workflow.can_modify_prediction


def test_post_replacement_validation_failure_revokes_normal_session_and_keeps_safety(
    desk, monkeypatch
):
    _, ticket = prepare_restore(desk)
    old = desk.session
    validate = desk.host.restore_service._validate

    def fail_post(path, *, repair):
        if not repair:
            raise RuntimeError("injected live post-check failure")
        return validate(path, repair=repair)

    monkeypatch.setattr(desk.host.restore_service, "_validate", fail_post)
    result = old.restore(ticket)
    assert result.disposition == D.EMERGENCY_RECOVERY
    assert desk.runtime.result is result and desk.runtime.unsafe_database
    assert old.disposed
    assert desk.session is None
    assert isinstance(desk.window, SafetyWindow)
    assert desk.window.restore_page is not None
    assert len(desk.backups(BackupCategory.SAFETY)) == 1
    # Replacement remains in place: no automatic restoration of pre_restore Safety.
    assert (
        scalar(
            desk.path, "SELECT regime_number FROM history_regimes WHERE character_id=1 AND active=1"
        )
        == 1
    )


def test_actual_qt_queued_callbacks_old_session_rejected_before_db_backup_or_second_restore(
    desk, desktop_app, monkeypatch
):
    _, ticket = prepare_restore(desk)
    old = desk.session
    callback = old.workflow.set_inputs
    observed = []

    def first():
        old.restore(ticket)
        observed.append("restored")

    def second():
        def forbidden(*args, **kwargs):
            pytest.fail("stale callback reached a dependency")

        monkeypatch.setattr(desk.host.restore_service, "normal_restore", forbidden)
        monkeypatch.setattr(desk.host.backup, "create", forbidden)
        monkeypatch.setattr(old.workflow._target, "set_inputs", forbidden)
        monkeypatch.setattr(old._maintenance, "list_characters", forbidden)
        for action in (
            lambda: callback(COMMAND),
            old.maintenance_rows,
            old.catalog.refresh,
            lambda: old.restore(ticket),
        ):
            with pytest.raises(DisposedSessionError):
                action()
        observed.append("rejected")

    QTimer.singleShot(0, first)
    QTimer.singleShot(0, second)
    desktop_app.processEvents()
    assert observed == ["restored", "rejected"]


def test_programmatic_teardown_bypasses_close_guard_even_with_unsaved_edits(desk):
    calculate(desk.window)
    click(desk.window.round.pre.modify)
    before = rows(desk.path, "rounds")
    prompts = []
    desk.window.close_confirmation = lambda *args: prompts.append("prompt") or False
    assert not desk.window.close()
    assert prompts == ["prompt"]
    prompts.clear()
    desk.host.dispose()
    assert prompts == []
    assert rows(desk.path, "rounds") == before
    assert desk.runtime.lock.held


@pytest.mark.parametrize("failure", [False, True])
def test_real_corrupt_startup_emergency_restore_creates_normal_session_only_after_replacement(
    paths, desktop_app, failure
):
    with StartupService(paths).start():
        pass
    paths.database.write_bytes(b"corrupt live database")
    with StartupService(paths).start() as runtime:
        assert runtime.result.disposition == D.EMERGENCY_RECOVERY
        host = DesktopHost(runtime)
        try:
            host.show_initial_state()
            assert host.session is None and not hasattr(host.lease, "workflow")
            old_lease, old_window, previous = host.lease, host.window, runtime.result
            assert old_window.restore_page.selected() is None
            assert not old_window.restore_page.restore.isEnabled()
            page = old_window.restore_page
            page.candidates.setCurrentRow(0)
            click(page.restore)
            if failure:
                path = old_lease.catalog.resolve(page.selected().candidate_id)
                path.write_bytes(b"candidate now corrupt")
            click(page.confirm)
            if failure:
                assert runtime.result is previous and host.lease is old_lease
                assert host.session is None and not old_lease.disposed
                assert "did not replace" in old_window.banner.message.text()
            else:
                assert runtime.result is not previous
                assert runtime.result.disposition == D.READY_DRAFT
                assert old_lease.disposed and old_window._disposed
                assert host.session is not None
                assert calculate(host.window) is not None
                assert scalar(paths.database, "PRAGMA integrity_check") == "ok"
                assert list(paths.safety.glob("UNVERIFIED_CORRUPT*"))
        finally:
            host.dispose()


def test_normal_restore_ui_explicit_selection_confirmation_busy_and_close_ignore(desk, monkeypatch):
    window = desk.window
    window.show_restore()
    page = window.restore_page
    assert page.selected() is None and not page.restore.isEnabled()
    page.candidates.setCurrentRow(0)
    click(page.restore)
    assert not page.candidates.isEnabled()
    original = desk.host.restore_service.normal_restore
    observations = []

    def restoring(path):
        observations.extend(
            (
                not page.confirm.isEnabled(),
                not page.candidates.isEnabled(),
                not window.round_button.isEnabled(),
                not window.close(),
            )
        )
        return original(path)

    monkeypatch.setattr(desk.host.restore_service, "normal_restore", restoring)
    click(page.confirm)
    assert observations == [True, True, True, True]
    assert window._disposed
    assert desk.window is not window
