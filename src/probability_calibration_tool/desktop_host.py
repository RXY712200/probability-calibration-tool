"""Qt/runtime composition and authoritative restore routing."""

from .application.desktop_session import DesktopSession, RestoreSession
from .application.enums import RecoveryState
from .application.errors import ApplicationInvariantError
from .application.reliability_views import ReliabilityResult
from .application.reliability_views import StartupDisposition as D
from .application.restore_service import RestoreService
from .infrastructure.backup import BackupService
from .infrastructure.error_reporting import report_error
from .ui.desktop_window import DesktopWindow
from .ui.presentation import RecoveryPresentation
from .ui.safety_window import SafetyWindow


class DesktopHost:
    def __init__(self, runtime, *, backup=None, restore=None, session_factory=DesktopSession):
        self.runtime = runtime
        self.backup = (
            backup if backup is not None else BackupService(runtime.paths, logger=runtime.logger)
        )
        self.restore_service = restore if restore is not None else RestoreService(runtime)
        self._session_factory = session_factory
        self.session = self.lease = self.window = None
        self.disposed = False

    def _detach(self):
        if self.lease is not None:
            self.lease.dispose()
        if self.window is not None:
            self.window.close_for_session_replacement()
        self.session = self.lease = self.window = None

    def dispose(self):
        self._detach()
        self.disposed = True

    def show_initial_state(self):
        if self.disposed:
            raise RuntimeError("Desktop host has been disposed.")
        if self.runtime.result.disposition == D.ALREADY_RUNNING:
            raise RuntimeError(
                "Already-running notification belongs to bootstrap, without an event loop."
            )
        self._route()

    def _route(self):
        self._detach()
        result = self.runtime.result
        if result.disposition in (D.READY_DRAFT, D.READY_RECOVERY):
            try:
                self.session = self.lease = self._session_factory(
                    self.runtime, self.backup, self._restore
                )
                recovery = None
                if result.disposition == D.READY_RECOVERY:
                    view = self.session.workflow.inspect_recovery()
                    if view.state != RecoveryState.RECOVERABLE:
                        raise ApplicationInvariantError(
                            "Startup recovery inspection was inconsistent."
                        )
                    recovery = RecoveryPresentation(view, self.session.recovery_preview())
                self.window = DesktopWindow(self.session)
                if recovery is not None:
                    self.window.present_recovery(recovery)
            except Exception as exc:  # noqa: BLE001 - fail-closed startup presentation boundary
                self._detach()
                result = ReliabilityResult(
                    D.DATA_SAFETY_ERROR,
                    result.warnings,
                    report_error(
                        self.runtime.logger, exc, "Desktop startup could not safely continue."
                    ),
                )
        if self.window is None:
            self.lease = RestoreSession(self.runtime, self.backup, self._restore)
            emergency = result.disposition == D.EMERGENCY_RECOVERY or (
                result.disposition == D.DATA_SAFETY_ERROR and self.runtime.unsafe_database
            )
            self.window = SafetyWindow(self.lease, result, emergency=emergency)
        self.window.show()
        # Rendering new Draft may clear banners. Apply startup/restore outcome LAST.
        if result.error is not None:
            self.window.banner.show_error(result.error)
        if result.warnings:
            prefix = (
                ""
                if result.error is None
                else f"{result.error.message} Error ID: {result.error.error_id}\n"
            )
            self.window.banner.show_message(prefix + "\n".join(result.warnings), "warning")

    def _restore(self, lease, path):
        lease.require_active()
        if self.disposed or lease is not self.lease:
            raise RuntimeError("Obsolete desktop session cannot restore.")
        previous = self.runtime.result
        if self.session is lease:
            operation_result = self.restore_service.normal_restore(path)
        elif previous.disposition == D.EMERGENCY_RECOVERY or (
            previous.disposition == D.DATA_SAFETY_ERROR and self.runtime.unsafe_database
        ):
            operation_result = self.restore_service.emergency_restore(path)
        else:
            raise RuntimeError("Emergency restore is not available in this safety state.")
        # Operation failure does not necessarily mean that live runtime health changed.
        if self.runtime.result is not previous:
            self._route()
        return operation_result
