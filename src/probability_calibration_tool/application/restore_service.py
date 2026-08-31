import sqlite3

from probability_calibration_tool.infrastructure.backup import (
    BackupService,
    SQLiteSafetyBackupAdapter,
)
from probability_calibration_tool.infrastructure.error_reporting import report_error
from probability_calibration_tool.infrastructure.restore_engine import (
    RestoreEngine,
    cleanup_temporary,
)
from probability_calibration_tool.infrastructure.sqlite_health import (
    DatabaseHealthError,
    SQLiteHealth,
)

from .errors import ApplicationInvariantError
from .invariant_service import InvariantService
from .migration_service import MigrationService
from .reliability_views import ReliabilityResult, StartupDisposition, ready_disposition
from .stats_validation_service import StatsValidationService


class RestoreService:
    def __init__(
        self,
        runtime,
        *,
        health=None,
        invariants=None,
        stats=None,
        migrations=None,
        engine=None,
        safety=None,
    ):
        self.runtime = runtime
        self.health = health if health is not None else SQLiteHealth()
        self.invariants = invariants if invariants is not None else InvariantService()
        self.stats = stats if stats is not None else StatsValidationService(runtime.logger)
        self.migrations = (
            migrations if migrations is not None else MigrationService(health=self.health)
        )
        self.engine = engine if engine is not None else RestoreEngine(self.health, runtime.logger)
        self.safety = (
            safety
            if safety is not None
            else SQLiteSafetyBackupAdapter(
                BackupService(runtime.paths, health=self.health, logger=runtime.logger)
            )
        )

    def normal_restore(self, candidate) -> ReliabilityResult:
        return self._restore(candidate, emergency=False)

    def emergency_restore(self, candidate) -> ReliabilityResult:
        return self._restore(candidate, emergency=True)

    def _validate(self, path, *, repair):
        self.health.verify(path, expected_version=self.migrations.target_version)
        report = self.invariants.inspect(path)
        if report.issues:
            raise ApplicationInvariantError("; ".join(report.issues))
        self.stats.validate(path, repair=repair)
        self.health.verify(path, expected_version=self.migrations.target_version)
        return report

    def _restore(self, candidate, *, emergency):
        live = self.runtime.paths.database
        temporary = None
        replaced = False
        warnings = ()
        try:
            with self.runtime.quiescent():
                if emergency:
                    unsafe = self.runtime.unsafe_database
                    if not unsafe:
                        try:
                            self.health.verify(live, readonly=False)
                        except (sqlite3.DatabaseError, DatabaseHealthError, OSError):
                            unsafe = True
                    if not unsafe:
                        raise RuntimeError("Healthy runtime must use Normal Restore.")
                else:
                    self.health.verify(
                        live, expected_version=self.migrations.target_version, readonly=False
                    )
                    report = self.invariants.inspect(live)
                    if report.pending_count:
                        raise RuntimeError("Pending rounds block Normal Restore.")
                    if report.issues:
                        raise ApplicationInvariantError(
                            "Unsafe live source requires emergency recovery."
                        )
                temporary = self.engine.prepare_copy(candidate, live)
                self.migrations.migrate_restore_copy(temporary, candidate)
                self._validate(temporary, repair=True)
                if emergency:
                    warnings = self.engine.quarantine(live, self.runtime.paths.safety)
                    self.engine.replace(temporary, live)
                else:
                    self.safety.create_verified_safety_backup("pre_restore")
                    self.engine.replace_normal(temporary, live)
                replaced = True
                report = self._validate(live, repair=False)
                result = ReliabilityResult(ready_disposition(report.pending_count), warnings)
                self.runtime.unsafe_database = report.pending_count > 1
        except Exception as exc:  # noqa: BLE001 - report full traceback; never silently undo replacement
            if replaced:
                self.runtime.unsafe_database = True
            result = ReliabilityResult(
                StartupDisposition.EMERGENCY_RECOVERY
                if replaced
                else StartupDisposition.DATA_SAFETY_ERROR,
                warnings,
                report_error(
                    self.runtime.logger,
                    exc,
                    "Replacement requires emergency recovery."
                    if replaced
                    else "Restore did not replace the live database.",
                ),
            )
        finally:
            if temporary is not None:
                cleanup_temporary(temporary, self.runtime.logger)
        # A rejected operation does not change the health of the unchanged live runtime.
        if replaced:
            self.runtime.result = result
        return result
