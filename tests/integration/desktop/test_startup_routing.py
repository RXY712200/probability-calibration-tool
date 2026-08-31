import sqlite3
from contextlib import closing

import pytest

from probability_calibration_tool.application.enums import RecoveryState, WorkflowState
from probability_calibration_tool.application.errors import MultiplePendingRoundsError
from probability_calibration_tool.application.recovery_service import RecoveryService
from probability_calibration_tool.application.reliability_views import ReliabilityResult
from probability_calibration_tool.application.reliability_views import StartupDisposition as D
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.application.views import RecoveryView
from probability_calibration_tool.desktop_host import DesktopHost
from probability_calibration_tool.infrastructure.backup import BackupService
from probability_calibration_tool.ui.safety_window import SafetyWindow

from .helpers import COMMAND, calculate


@pytest.mark.parametrize(
    "disposition",
    [D.RECOVERY_ERROR, D.EMERGENCY_RECOVERY, D.UNSUPPORTED_NEWER_SCHEMA, D.DATA_SAFETY_ERROR],
)
def test_unsafe_route_never_constructs_normal_session_or_uow(
    paths, desktop_app, monkeypatch, disposition
):
    with StartupService(paths).start() as runtime:
        runtime.result = ReliabilityResult(disposition)
        runtime.unsafe_database = disposition == D.EMERGENCY_RECOVERY

        def forbidden(*args):
            pytest.fail("Unsafe presentation must not construct normal Workflow/UoW")

        monkeypatch.setattr(runtime, "uow_factory", forbidden)
        host = DesktopHost(runtime, session_factory=forbidden)
        try:
            host.show_initial_state()
            assert host.session is None
            assert isinstance(host.window, SafetyWindow)
            assert not hasattr(host.lease, "workflow")
            if disposition == D.EMERGENCY_RECOVERY:
                assert host.window.restore_page.selected() is None
            else:
                assert host.window.restore_page is None
        finally:
            host.dispose()


@pytest.mark.parametrize("inconsistent", ["none", "multiple"])
def test_ready_recovery_inconsistent_inspection_fails_closed(desk, monkeypatch, inconsistent):
    calculate(desk.window)
    desk.runtime.result = ReliabilityResult(D.READY_RECOVERY)

    def inspect(self):
        if inconsistent == "multiple":
            raise MultiplePendingRoundsError("injected multiple")
        return RecoveryView(RecoveryState.NONE, None)

    monkeypatch.setattr(RecoveryService, "inspect", inspect)
    desk.host.show_initial_state()
    assert desk.host.session is None
    assert isinstance(desk.window, SafetyWindow)
    assert "Error ID" in desk.window.banner.message.text()
    assert "Traceback" in desk.runtime.paths.log_file.read_text()


@pytest.mark.parametrize("pending", [False, True])
def test_daily_failure_warning_is_last_and_healthy_work_remains_available(
    paths, desktop_app, pending
):
    if pending:
        from probability_calibration_tool.application.ports import SystemClock, UUIDGenerator
        from probability_calibration_tool.application.round_service import RoundService

        with StartupService(paths).start() as seed:
            RoundService(seed.uow_factory(), SystemClock(), UUIDGenerator()).calculate(COMMAND)

    class FailedDaily(BackupService):
        def create(self, category, reason=None):
            raise OSError("injected Daily failure")

    with StartupService(
        paths, backup_factory=lambda p, logger: FailedDaily(p, logger=logger)
    ).start() as runtime:
        host = DesktopHost(runtime)
        try:
            host.show_initial_state()
            window = host.window
            assert window.workflow.state == (
                WorkflowState.RECOVERY if pending else WorkflowState.DRAFT
            )
            assert "Daily backup failed" in window.banner.message.text()
            assert window.banner.isVisible()
            if not pending:
                assert calculate(window) is not None
        finally:
            host.dispose()


def test_actual_newer_database_routes_safety_without_business_access(paths, desktop_app):
    with StartupService(paths).start():
        pass
    with closing(sqlite3.connect(paths.database)) as db:
        db.execute("PRAGMA user_version=999")
    with StartupService(paths).start() as runtime:
        assert runtime.result.disposition == D.UNSUPPORTED_NEWER_SCHEMA

        def forbidden(*args):
            pytest.fail("No normal session for newer schema")

        host = DesktopHost(runtime, session_factory=forbidden)
        try:
            host.show_initial_state()
            assert host.session is None
            assert host.window.restore_page is None
            with closing(sqlite3.connect(paths.database)) as db:
                assert db.execute("PRAGMA user_version").fetchone()[0] == 999
        finally:
            host.dispose()
