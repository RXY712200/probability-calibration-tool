import pytest
from infrastructure.helpers import InjectedFailure, make_rig, query

from probability_calibration_tool.application import migration_service as migration_module
from probability_calibration_tool.application.migration_service import (
    MigrationService,
    PostCommitMigrationError,
)
from probability_calibration_tool.application.reliability_views import StartupDisposition
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.infrastructure.backup import (
    BackupCategory,
    InventoryKind,
    SQLiteSafetyBackupAdapter,
)
from probability_calibration_tool.infrastructure.sqlite_health import SQLiteHealth
from probability_calibration_tool.persistence.errors import UnsupportedNewerSchemaError
from probability_calibration_tool.persistence.migration_engine import (
    Migration,
    MigrationRegistry,
    UnsupportedMigrationError,
)


@pytest.fixture
def rig(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "test-localappdata"))
    return make_rig(tmp_path / "app")


def safety_files(rig):
    return [
        entry.path
        for entry in rig.backup.inventory(BackupCategory.SAFETY)
        if entry.kind == InventoryKind.VALID
    ]


def test_ordered_synthetic_migrations_verify_safety_and_update_version_after_body(rig):
    rig.h.seed_history(1, 0)

    def one(connection):
        assert len(safety_files(rig)) == 1
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        connection.execute("CREATE TABLE synthetic_only (value TEXT)")
        connection.execute("INSERT INTO synthetic_only VALUES ('preserved')")
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1

    def two(connection):
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2
        connection.execute("ALTER TABLE synthetic_only ADD COLUMN extra INTEGER")

    service = MigrationService(MigrationRegistry((Migration(1, 2, one), Migration(2, 3, two))), 3)
    service.migrate_live(rig.paths.database, SQLiteSafetyBackupAdapter(rig.backup))
    assert query(rig.paths.database, "PRAGMA user_version") == [(3,)]
    assert query(rig.paths.database, "SELECT value FROM synthetic_only") == [("preserved",)]
    assert query(rig.paths.database, "SELECT count(*) FROM rounds") == [(1,)]
    assert query(safety_files(rig)[0], "PRAGMA user_version") == [(1,)]


@pytest.mark.parametrize("fault", ["body", "precommit"])
def test_precommit_failure_rolls_back_schema_data_version_preserving_safety(
    rig, monkeypatch, fault
):
    before = rig.h.capture()

    def one(connection):
        connection.execute("CREATE TABLE synthetic_only (value)")

    def two(connection):
        connection.execute("UPDATE meta SET value='changed'")
        if fault == "body":
            raise InjectedFailure("migration body")

    def fail(*args):
        raise InjectedFailure("precommit check")

    if fault == "precommit":
        monkeypatch.setattr(migration_module, "integrity_check", fail)
    service = MigrationService(MigrationRegistry((Migration(1, 2, one), Migration(2, 3, two))), 3)
    with pytest.raises(InjectedFailure):
        service.migrate_live(rig.paths.database, SQLiteSafetyBackupAdapter(rig.backup))
    assert rig.h.capture() == before
    assert query(rig.paths.database, "PRAGMA user_version") == [(1,)]
    assert (
        query(rig.paths.database, "SELECT name FROM sqlite_master WHERE name='synthetic_only'")
        == []
    )
    assert len(safety_files(rig)) == 1


def test_required_safety_failure_never_starts_migration_body(rig, monkeypatch):
    before = rig.paths.database.read_bytes()

    def fail(*args):
        raise InjectedFailure("Safety failed")

    monkeypatch.setattr(rig.backup, "_copy_online", fail)
    service = MigrationService(
        MigrationRegistry((Migration(1, 2, lambda c: pytest.fail("No mutation allowed")),)), 2
    )
    with pytest.raises(InjectedFailure):
        service.migrate_live(rig.paths.database, SQLiteSafetyBackupAdapter(rig.backup))
    assert rig.paths.database.read_bytes() == before


def test_postcommit_failure_is_not_fake_rollback_and_startup_routes_emergency(rig):
    class BadPostHealth(SQLiteHealth):
        def verify(self, *args, **kwargs):
            raise InjectedFailure("postcommit integrity failure")

    def body(connection):
        connection.execute("CREATE TABLE synthetic_only (value)")

    migration = MigrationService(MigrationRegistry((Migration(1, 2, body),)), 2, BadPostHealth())
    with StartupService(
        rig.paths, migrations=migration, backup_factory=lambda *args: rig.backup
    ).start() as runtime:
        assert runtime.result.disposition == StartupDisposition.EMERGENCY_RECOVERY
    assert query(rig.paths.database, "PRAGMA user_version") == [(2,)]
    assert query(
        rig.paths.database, "SELECT name FROM sqlite_master WHERE name='synthetic_only'"
    ) == [("synthetic_only",)]
    assert len(safety_files(rig)) == 1
    assert list(rig.paths.daily.iterdir()) == []


def test_direct_postcommit_failure_type(rig):
    class BadPostHealth(SQLiteHealth):
        def verify(self, *args, **kwargs):
            raise InjectedFailure("postcommit")

    service = MigrationService(
        MigrationRegistry((Migration(1, 2, lambda c: None),)), 2, BadPostHealth()
    )
    with pytest.raises(PostCommitMigrationError):
        service.migrate_live(rig.paths.database, SQLiteSafetyBackupAdapter(rig.backup))
    assert query(rig.paths.database, "PRAGMA user_version") == [(2,)]


def test_newer_schema_remains_unchanged_and_real_registry_has_no_product_v2(rig):
    from infrastructure.helpers import mutate

    mutate(rig.paths.database, "PRAGMA user_version=2")
    before = rig.paths.database.read_bytes()
    with pytest.raises(UnsupportedNewerSchemaError):
        MigrationService().migrate_live(rig.paths.database, SQLiteSafetyBackupAdapter(rig.backup))
    assert rig.paths.database.read_bytes() == before
    assert safety_files(rig) == []
    with pytest.raises(UnsupportedMigrationError):
        MigrationRegistry().plan(1, 2)
    with pytest.raises(UnsupportedMigrationError):
        MigrationRegistry().plan(0, 1)
