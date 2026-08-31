from contextlib import closing

from probability_calibration_tool.infrastructure.sqlite_health import (
    SQLiteHealth,
    integrity_check,
    open_existing,
)
from probability_calibration_tool.persistence.errors import UnsupportedNewerSchemaError
from probability_calibration_tool.persistence.migration_engine import (
    MigrationRegistry,
    apply_migrations,
)
from probability_calibration_tool.persistence.schema import SCHEMA_VERSION


class PostCommitMigrationError(RuntimeError):
    """Commit already happened. Safety backup remains; automatic rollback is impossible."""


class MigrationService:
    def __init__(self, registry=None, target_version=SCHEMA_VERSION, health=None):
        self.registry = registry if registry is not None else MigrationRegistry()
        self.target_version = target_version
        self.health = health if health is not None else SQLiteHealth()

    def _plan(self, path):
        metadata = self.health.inspect(path)
        if metadata.version > self.target_version:
            raise UnsupportedNewerSchemaError("A newer application is required.")
        return self.registry.plan(metadata.version, self.target_version)

    def migrate_live(self, path, safety) -> None:
        steps = self._plan(path)
        if not steps:
            return
        safety.create_verified_safety_backup("pre_migration")
        self._apply(path, steps)

    def migrate_restore_copy(self, path, original) -> None:
        if path.resolve() == original.resolve() or not original.is_file():
            raise ValueError("Restore migration requires a separate preserved original.")
        self._apply(path, self._plan(path))

    def _apply(self, path, steps):
        if not steps:
            return
        with closing(open_existing(path)) as connection:
            apply_migrations(connection, steps, integrity_check)
        try:
            self.health.verify(path, expected_version=self.target_version)
        except Exception as exc:
            raise PostCommitMigrationError(
                "Migration committed but post-commit verification failed."
            ) from exc
