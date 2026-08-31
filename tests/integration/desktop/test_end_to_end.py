from probability_calibration_tool.application.enums import WorkflowState as S
from probability_calibration_tool.application.reliability_views import StartupDisposition as D
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.desktop_host import DesktopHost
from probability_calibration_tool.infrastructure.backup import BackupCategory, InventoryKind

from .helpers import calculate, click, complete, scalar, text_tree


def test_real_start_close_restart_continue_complete_backup_new_draft(paths, desktop_app):
    with StartupService(paths).start() as runtime_a:
        host_a = DesktopHost(runtime_a)
        try:
            host_a.show_initial_state()
            assert runtime_a.result.disposition == D.READY_DRAFT
            first = calculate(host_a.window)
            with runtime_a.uow_factory()() as uow:
                saved_snapshot = uow.snapshots.get(first.round_id)
            assert host_a.window.close()
            assert runtime_a.lock.held
        finally:
            host_a.dispose()
    assert not runtime_a.lock.held
    with StartupService(paths).start() as runtime_b:
        host_b = DesktopHost(runtime_b)
        try:
            host_b.show_initial_state()
            window = host_b.window
            assert runtime_b is not runtime_a
            assert runtime_b.result.disposition == D.READY_RECOVERY
            assert window.workflow.state == S.RECOVERY
            assert window.workflow.analysis is None
            assert window.stack.currentWidget() is window.recovery
            click(window.recovery.continue_button)
            assert window.workflow.analysis == first
            assert not window.workflow.can_modify_prediction
            with runtime_b.uow_factory()() as uow:
                assert uow.snapshots.get(first.round_id) == saved_snapshot
            click(window.round.post.result.buttons[True])
            click(window.round.post.include.buttons[True])
            click(window.round.post.save)
            assert window.workflow.state == S.COMPLETED_NOTICE
            assert window.round.new_round.isVisible()
            entries = host_b.backup.inventory(BackupCategory.RECENT)
            assert len(entries) == 1 and entries[0].kind == InventoryKind.VALID
            assert (
                scalar(
                    entries[0].path, "SELECT status FROM rounds WHERE round_id=?", (first.round_id,)
                )
                == "completed"
            )
            assert scalar(entries[0].path, "PRAGMA integrity_check") == "ok"
            click(window.round.new_round)
            assert window.workflow.state == S.DRAFT
            assert scalar(paths.database, "PRAGMA integrity_check") == "ok"
        finally:
            host_b.dispose()


def test_full_integration_valid_history_is_committed_before_render_and_snapshot_stays_frozen(
    desk, monkeypatch
):
    for index in range(20):
        complete(desk.window, result=index < 19)
        click(desk.window.round.new_round)
    assert desk.window.workflow.state == S.DRAFT
    assert "92.9%" not in text_tree(desk.window)
    render = desk.window.round.analysis.render
    exposed = []

    def check_commit(view, **kwargs):
        if view is not None and view.history_exposed:
            assert (
                scalar(
                    desk.path,
                    "SELECT history_exposed FROM rounds WHERE round_id=?",
                    (view.round_id,),
                )
                == 1
            )
            exposed.append(view.round_id)
        return render(view, **kwargs)

    monkeypatch.setattr(desk.window.round.analysis, "render", check_commit)
    prediction = calculate(desk.window, reference=True)
    assert prediction.round_id in exposed
    assert prediction.history.sample_size == 20
    with desk.runtime.uow_factory()() as uow:
        before = uow.snapshots.get(prediction.round_id)
    click(desk.window.round.post.result.buttons[True])
    click(desk.window.round.post.include.buttons[True])
    click(desk.window.round.post.save)
    with desk.runtime.uow_factory()() as uow:
        assert uow.snapshots.get(prediction.round_id) == before
    assert (
        scalar(desk.path, "SELECT included_games FROM character_stats WHERE character_id=1") == 21
    )
    assert scalar(desk.path, "PRAGMA integrity_check") == "ok"
    assert len(desk.backups()) == 5
