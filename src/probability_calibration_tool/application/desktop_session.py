"""Production orchestration and revocable lifetime, never a second Workflow."""

from contextlib import contextmanager
from functools import wraps

from probability_calibration_tool.infrastructure.backup import (
    BackupCoordinator,
    SQLiteSafetyBackupAdapter,
)
from probability_calibration_tool.infrastructure.error_reporting import report_error

from .backup_catalog_service import BackupCatalogService
from .correction_query_service import CorrectionQueryService
from .correction_service import CorrectionService
from .enums import WorkflowState
from .errors import BusinessRuleError, ErrorCode
from .integrated_round_actions import IntegratedRoundActions
from .maintenance_service import MaintenanceService
from .ports import SystemClock, UUIDGenerator
from .recovery_service import RecoveryService
from .regime_service import RegimeService
from .reliability_views import StartupDisposition as D
from .round_service import RoundService
from .workflow import Workflow


class DisposedSessionError(RuntimeError):
    code = ErrorCode.SESSION_DISPOSED


class GuardedWorkflow:
    """Revokes even previously captured bound callbacks; delegates all semantics."""

    __slots__ = ("_guard", "_target")

    def __init__(self, target, guard):
        self._target, self._guard = target, guard

    def __getattr__(self, name):
        self._guard()
        if name.startswith("_"):
            raise AttributeError(name)
        value = getattr(self._target, name)
        if not callable(value):
            return value

        @wraps(value)
        def guarded(*args, **kwargs):
            self._guard()
            return value(*args, **kwargs)

        return guarded


class RestoreSession:
    """Safety presentation lifetime: deliberately has no UoW or Workflow."""

    def __init__(self, runtime, backup, restore):
        self.runtime = runtime
        self.disposed = False
        self.busy = False
        self._restore = restore
        self._tickets = {}
        self._warnings = []
        self.catalog = BackupCatalogService(backup, self.require_active)

    def require_active(self):
        if self.disposed or not self.runtime.lock.held:
            raise DisposedSessionError("Desktop session has been disposed.")

    def dispose(self):
        self.disposed = True
        self._tickets.clear()
        self._warnings.clear()

    @contextmanager
    def _operation(self):
        self.require_active()
        if self.busy:
            raise BusinessRuleError("Another operation is in progress.", code=ErrorCode.BUSY)
        self.busy = True
        try:
            yield
        finally:
            self.busy = False

    def _issue(self, kind, identity):
        self.require_active()
        if self.busy:
            raise BusinessRuleError("Another operation is in progress.", code=ErrorCode.BUSY)
        ticket = object()
        self._tickets[kind] = (ticket, identity)
        return ticket

    def _consume(self, kind, ticket):
        self.require_active()
        existing = self._tickets.get(kind)
        if existing is None or existing[0] is not ticket:
            raise BusinessRuleError(
                "Confirmation expired. Confirm the operation again.",
                code=ErrorCode.CONFIRMATION_EXPIRED,
            )
        del self._tickets[kind]
        return existing[1]

    def _revoke(self, kind, ticket):
        """Cancel only this interaction; late cancellation cannot revoke a newer one."""
        self.require_active()
        existing = self._tickets.get(kind)
        if existing is not None and existing[0] is ticket:
            del self._tickets[kind]

    def cancel_restore(self, ticket):
        self._revoke("restore", ticket)

    def begin_restore(self, candidate_id):
        self.require_active()
        self.catalog.resolve(candidate_id)
        return self._issue("restore", candidate_id)

    def restore(self, ticket):
        self.require_active()
        candidate_id = self._consume("restore", ticket)
        with self._operation():
            return self._restore(self, self.catalog.resolve(candidate_id))

    def report_unexpected(self, exc):
        self.require_active()
        return report_error(self.runtime.logger, exc, "The operation could not be completed.")

    def take_warnings(self):
        self.require_active()
        warnings = tuple(self._warnings)
        self._warnings.clear()
        return warnings


class DesktopSession(RestoreSession):
    def __init__(self, runtime, backup, restore, *, clock=None, ids=None):
        super().__init__(runtime, backup, restore)
        self._require_healthy()
        factory = runtime.uow_factory()
        clock, ids = clock or SystemClock(), ids or UUIDGenerator()
        self._backups = BackupCoordinator(backup)
        rounds = IntegratedRoundActions(RoundService(factory, clock, ids), self._recent)
        self._recovery = RecoveryService(factory)
        self.workflow = GuardedWorkflow(Workflow(rounds, self._recovery), self._require_healthy)
        self._maintenance = MaintenanceService(factory)
        self._regimes = RegimeService(factory, clock, ids)
        self._corrections = CorrectionService(
            factory, clock, ids, SQLiteSafetyBackupAdapter(backup)
        )
        self._candidates = CorrectionQueryService(factory)

    def _require_healthy(self):
        self.require_active()
        if self.runtime.unsafe_database or self.runtime.result.disposition not in (
            D.READY_DRAFT,
            D.READY_RECOVERY,
        ):
            raise BusinessRuleError(
                "Normal operation is not available.", code=ErrorCode.NORMAL_UNAVAILABLE
            )

    def can_admin(self):
        self._require_healthy()
        return not self.busy and self.workflow.state == WorkflowState.DRAFT

    def _require_admin(self):
        if not self.can_admin():
            raise BusinessRuleError(
                "Return to a healthy Draft before changing administrative data.",
                code=ErrorCode.HEALTHY_DRAFT_REQUIRED,
            )

    def _recent(self):
        # Coordinator contains backup faults; this cannot undo a committed business operation.
        outcome = self._backups.recent()
        if outcome.warning is not None:
            self._warnings.append(outcome.warning)
        if outcome.backup is not None:
            self._warnings.extend(outcome.backup.warnings)

    def maintenance_rows(self):
        self._require_healthy()
        return self._maintenance.list_characters()

    def correction_candidates(self):
        self._require_healthy()
        return self._candidates.list_candidates()

    def recovery_preview(self):
        self._require_healthy()
        return self._recovery.continue_pending()

    def begin_regime(self, character_id):
        self._require_admin()
        return self._issue("regime", character_id)

    def cancel_regime(self, ticket):
        self._revoke("regime", ticket)

    def start_regime(self, ticket, reason):
        self._require_admin()
        character_id = self._consume("regime", ticket)
        with self._operation():
            result = self._regimes.start_new_regime(character_id, reason)
            self._recent()
            return result

    def begin_correction(self, round_id):
        self._require_admin()
        return self._issue("correction", round_id)

    def cancel_correction(self, ticket):
        self._revoke("correction", ticket)

    def correct(self, ticket, result, include, reason):
        self._require_admin()
        round_id = self._consume("correction", ticket)
        with self._operation():
            outcome = self._corrections.correct_post_run(round_id, result, include, reason)
            self._recent()
            return outcome

    def begin_restore(self, candidate_id):
        self._require_admin()
        return super().begin_restore(candidate_id)

    def restore(self, ticket):
        self._require_admin()
        return super().restore(ticket)
