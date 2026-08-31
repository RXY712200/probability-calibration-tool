import os
import sqlite3
from contextlib import closing

from probability_calibration_tool.infrastructure.backup import (
    BackupCoordinator,
    BackupService,
    SQLiteSafetyBackupAdapter,
)
from probability_calibration_tool.infrastructure.error_reporting import report_error
from probability_calibration_tool.infrastructure.logging_setup import (
    bootstrap_logger,
    close_logger,
    full_logger,
)
from probability_calibration_tool.infrastructure.restore_engine import (
    cleanup_temporary,
    temporary_database,
)
from probability_calibration_tool.infrastructure.runtime_lock import RuntimeLock
from probability_calibration_tool.infrastructure.sqlite_health import (
    DatabaseHealthError,
    SQLiteHealth,
)
from probability_calibration_tool.persistence.database import create_connection
from probability_calibration_tool.persistence.errors import UnsupportedNewerSchemaError
from probability_calibration_tool.persistence.schema import initialize_v1

from .errors import ApplicationInvariantError
from .invariant_service import InvariantService
from .migration_service import MigrationService, PostCommitMigrationError
from .reliability_views import ReliabilityResult, StartupDisposition, ready_disposition
from .runtime_context import RuntimeContext
from .stats_validation_service import StatsValidationService


class StartupService:
    def __init__(
        self,
        paths,
        *,
        health=None,
        invariants=None,
        stats=None,
        migrations=None,
        backup_factory=None,
        lock_factory=RuntimeLock,
        initializer=initialize_v1,
    ):
        self.paths = paths
        self.health = health if health is not None else SQLiteHealth()
        self.invariants = invariants if invariants is not None else InvariantService()
        self.stats = stats if stats is not None else StatsValidationService()
        self.migrations = (
            migrations if migrations is not None else MigrationService(health=self.health)
        )
        self.backup_factory = (
            backup_factory
            if backup_factory is not None
            else (lambda paths, logger: BackupService(paths, health=self.health, logger=logger))
        )
        self.lock_factory, self.initializer = lock_factory, initializer

    def _initialize_fresh(self, logger):
        temporary = temporary_database(self.paths.database.parent, ".initialize_")
        try:
            with closing(create_connection(temporary)) as connection:
                self.initializer(connection)
            self.health.verify(temporary, expected_version=self.migrations.target_version)
            self.invariants.require_valid(temporary)
            self.stats.validate(temporary, repair=False)
            if os.path.lexists(self.paths.database):
                raise FileExistsError(
                    "Live database appeared during initialization; not overwriting."
                )
            with temporary.open("r+b") as stream:
                os.fsync(stream.fileno())
            os.replace(temporary, self.paths.database)
        finally:
            cleanup_temporary(temporary, logger)

    def start(self) -> RuntimeContext:
        try:
            self.paths.create_directories()
        except Exception as exc:  # noqa: BLE001 - directory failure still needs a safe bootstrap result
            logger = bootstrap_logger()
            runtime = RuntimeContext(self.paths, self.lock_factory(self.paths.lock_file), logger)
            runtime.result = ReliabilityResult(
                StartupDisposition.DATA_SAFETY_ERROR,
                error=report_error(logger, exc, "Application directories could not be prepared."),
            )
            return runtime
        bootstrap = bootstrap_logger()
        runtime = RuntimeContext(self.paths, self.lock_factory(self.paths.lock_file), bootstrap)
        database_phase = False
        try:
            if not runtime.lock.acquire():
                runtime.result = ReliabilityResult(StartupDisposition.ALREADY_RUNNING)
                return runtime
            runtime.logger = full_logger(self.paths.log_file)
            close_logger(bootstrap)
            self.stats.logger = runtime.logger
            backup = self.backup_factory(self.paths, runtime.logger)
            database_phase = True
            existed = os.path.lexists(self.paths.database)
            if not existed:
                self._initialize_fresh(runtime.logger)
            try:
                metadata = self.health.inspect(self.paths.database)
            except (sqlite3.DatabaseError, DatabaseHealthError, OSError) as exc:
                runtime.unsafe_database = True
                runtime.result = ReliabilityResult(
                    StartupDisposition.EMERGENCY_RECOVERY,
                    error=report_error(
                        runtime.logger, exc, "Database integrity could not be established."
                    ),
                )
                return runtime
            if metadata.version > self.migrations.target_version:
                raise UnsupportedNewerSchemaError("A newer application is required.")
            if metadata.version < self.migrations.target_version:
                self.migrations.migrate_live(self.paths.database, SQLiteSafetyBackupAdapter(backup))
            report = self.invariants.inspect(self.paths.database)
            if report.pending_count > 1:
                runtime.unsafe_database = True
                runtime.logger.warning("Multiple pending records; Daily backup suppressed.")
                runtime.result = ReliabilityResult(StartupDisposition.RECOVERY_ERROR, report.issues)
                return runtime
            if report.issues:
                raise ApplicationInvariantError("; ".join(report.issues))
            repairs = self.stats.validate(self.paths.database)
            self.health.verify(self.paths.database, expected_version=self.migrations.target_version)
            daily = BackupCoordinator(backup).daily()
            warnings = []
            if repairs.repaired_regime_ids:
                warnings.append("Derived statistics were rebuilt from source records.")
            if daily.warning is not None:
                warnings.append(f"{daily.warning.message} Error ID: {daily.warning.error_id}")
            elif daily.backup is not None:
                warnings.extend(daily.backup.warnings)
            runtime.result = ReliabilityResult(
                ready_disposition(report.pending_count), tuple(warnings)
            )
        except UnsupportedNewerSchemaError:
            runtime.result = ReliabilityResult(StartupDisposition.UNSUPPORTED_NEWER_SCHEMA)
        except PostCommitMigrationError as exc:
            runtime.unsafe_database = True
            runtime.result = ReliabilityResult(
                StartupDisposition.EMERGENCY_RECOVERY,
                error=report_error(
                    runtime.logger, exc, "Committed migration requires emergency recovery."
                ),
            )
        except Exception as exc:  # noqa: BLE001 - boundary logs traceback and returns safe disposition
            runtime.unsafe_database = database_phase
            runtime.result = ReliabilityResult(
                StartupDisposition.DATA_SAFETY_ERROR,
                error=report_error(runtime.logger, exc, "Startup could not safely continue."),
            )
        return runtime
