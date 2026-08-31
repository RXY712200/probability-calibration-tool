import shutil
from contextlib import closing
from dataclasses import replace
from types import SimpleNamespace

import pytest
from infrastructure.helpers import InjectedFailure, mutate, query

from application.helpers import COMMAND
from probability_calibration_tool.application.invariant_service import InvariantService
from probability_calibration_tool.application.migration_service import MigrationService
from probability_calibration_tool.application.reliability_views import StartupDisposition as D
from probability_calibration_tool.application.restore_service import RestoreService
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.infrastructure.backup import BackupCategory, InventoryKind
from probability_calibration_tool.infrastructure.sqlite_health import (
    SQLiteHealth,
    open_existing,
    sidecars,
)
from probability_calibration_tool.persistence.migration_engine import Migration, MigrationRegistry


def candidate_and_changed_live(rig):
    rig.h.seed_history(1, 0)
    candidate = rig.backup.create(BackupCategory.RECENT).path
    rig.h.seed_history(0, 1)
    return candidate


def safety_files(rig):
    return [
        entry.path
        for entry in rig.backup.inventory(BackupCategory.SAFETY)
        if entry.kind == InventoryKind.VALID
    ]


def test_normal_restore_atomic_success_original_immutable_and_pre_restore_preserved(rig):
    candidate = candidate_and_changed_live(rig)
    candidate_bytes = candidate.read_bytes()
    with StartupService(rig.paths).start() as runtime:
        assert runtime.result.disposition == D.READY_DRAFT
        result = RestoreService(runtime).normal_restore(candidate)
        assert result.disposition == D.READY_DRAFT
        with runtime.uow_factory()() as uow:
            assert len(uow.rounds.eligible_history(1, rig.h.stats().regime_id)) == 1
    assert candidate.read_bytes() == candidate_bytes
    backups = safety_files(rig)
    assert len(backups) == 1 and "pre_restore" in backups[0].name
    assert query(backups[0], "SELECT count(*) FROM rounds") == [(2,)]
    assert query(rig.paths.database, "SELECT count(*) FROM rounds") == [(1,)]
    assert not list(rig.paths.database.parent.glob(".restore_*"))


@pytest.mark.parametrize(
    "fault", ["corrupt", "newer", "copy", "temp_validation", "safety", "replace"]
)
def test_normal_restore_pre_replacement_failures_preserve_live_and_candidate(
    rig, monkeypatch, fault
):
    candidate = candidate_and_changed_live(rig)
    if fault == "corrupt":
        candidate.write_bytes(b"corrupt candidate")
    elif fault == "newer":
        mutate(candidate, "PRAGMA user_version=99")
    candidate_bytes = candidate.read_bytes()
    with StartupService(rig.paths).start() as runtime:
        service = RestoreService(runtime)
        before = rig.paths.database.read_bytes()

        def fail(*args, **kwargs):
            raise InjectedFailure(fault)

        if fault == "copy":
            monkeypatch.setattr(shutil, "copyfile", fail)
        elif fault == "temp_validation":
            monkeypatch.setattr(service, "_validate", fail)
        elif fault == "safety":
            monkeypatch.setattr(service.safety, "create_verified_safety_backup", fail)
        elif fault == "replace":
            monkeypatch.setattr(service.engine, "replace", fail)
        result = service.normal_restore(candidate)
        assert result.disposition == D.DATA_SAFETY_ERROR
        assert not runtime.unsafe_database  # Operation failure is not proof that old DB is corrupt.
        assert rig.paths.database.read_bytes() == before
        assert candidate.read_bytes() == candidate_bytes
        assert list(rig.paths.database.parent.glob(".restore_*")) == []


def test_failed_normal_restore_does_not_grant_emergency_backup_bypass(rig):
    candidate = candidate_and_changed_live(rig)
    with StartupService(rig.paths).start() as runtime:
        service = RestoreService(runtime)
        bad = rig.paths.recent / "bad.db"
        bad.write_bytes(b"bad")
        before = rig.paths.database.read_bytes()
        assert service.normal_restore(bad).disposition == D.DATA_SAFETY_ERROR
        assert service.emergency_restore(candidate).disposition == D.DATA_SAFETY_ERROR
        assert rig.paths.database.read_bytes() == before


def test_live_pending_blocks_normal_restore(rig):
    candidate = rig.backup.create(BackupCategory.RECENT).path
    rig.h.rounds.calculate(COMMAND)
    before = rig.h.capture()
    with StartupService(rig.paths).start() as runtime:
        assert RestoreService(runtime).normal_restore(candidate).disposition == D.DATA_SAFETY_ERROR
    assert rig.h.capture() == before and safety_files(rig) == []


def test_open_managed_uow_blocks_restore_without_forcing_transaction_closed(rig):
    candidate = candidate_and_changed_live(rig)
    with StartupService(rig.paths).start() as runtime:
        before = rig.paths.database.read_bytes()
        with runtime.uow_factory()() as uow:
            result = RestoreService(runtime).normal_restore(candidate)
            assert result.disposition == D.DATA_SAFETY_ERROR
            assert len(uow.characters.list_all()) == 34
        assert rig.paths.database.read_bytes() == before
        assert safety_files(rig) == []


@pytest.mark.parametrize("suffix", ["-journal", "-wal", "-shm"])
def test_unexplained_sidecar_blocks_normal_replacement_and_is_not_deleted(rig, suffix):
    candidate = candidate_and_changed_live(rig)
    with StartupService(rig.paths).start() as runtime:
        service = RestoreService(runtime)
        original = service.safety.create_verified_safety_backup
        sidecar = next(path for path in sidecars(rig.paths.database) if str(path).endswith(suffix))

        def add_sidecar(reason):
            original(reason)
            sidecar.write_bytes(b"unexplained sidecar")

        service.safety = SimpleNamespace(create_verified_safety_backup=add_sidecar)
        before = rig.paths.database.read_bytes()
        assert service.normal_restore(candidate).disposition == D.DATA_SAFETY_ERROR
        assert rig.paths.database.read_bytes() == before
        assert sidecar.read_bytes() == b"unexplained sidecar"


def test_post_replacement_failure_keeps_new_main_and_safety_without_auto_restore(rig, monkeypatch):
    candidate = candidate_and_changed_live(rig)
    with StartupService(rig.paths).start() as runtime:
        service = RestoreService(runtime)
        original = service._validate

        def validate(path, **kwargs):
            if path == rig.paths.database:
                raise InjectedFailure("post replacement")
            return original(path, **kwargs)

        monkeypatch.setattr(service, "_validate", validate)
        result = service.normal_restore(candidate)
        assert result.disposition == D.EMERGENCY_RECOVERY and runtime.unsafe_database
        assert query(rig.paths.database, "SELECT count(*) FROM rounds") == [(1,)]
        assert query(safety_files(rig)[0], "SELECT count(*) FROM rounds") == [(2,)]


def test_restore_supported_older_candidate_migrates_only_temp_copy(rig):
    candidate = candidate_and_changed_live(rig)
    original_bytes = candidate.read_bytes()
    mutate(rig.paths.database, "PRAGMA user_version=2")

    def migrate(connection):
        connection.execute("CREATE TABLE synthetic_restore_only (value)")

    migration = MigrationService(MigrationRegistry((Migration(1, 2, migrate),)), 2)
    with StartupService(rig.paths, migrations=migration).start() as runtime:
        result = RestoreService(runtime, migrations=migration).normal_restore(candidate)
        assert result.disposition == D.READY_DRAFT
    assert candidate.read_bytes() == original_bytes
    assert query(rig.paths.database, "PRAGMA user_version") == [(2,)]
    assert query(
        rig.paths.database, "SELECT name FROM sqlite_master WHERE name='synthetic_restore_only'"
    ) == [("synthetic_restore_only",)]
    assert len(safety_files(rig)) == 1 and "pre_restore" in safety_files(rig)[0].name


def test_restored_pending_routes_recovery_without_recalculation(rig):
    view = rig.h.rounds.calculate(COMMAND)
    saved = rig.h.record(view.round_id), rig.h.snapshot(view.round_id)
    candidate = rig.backup.create(BackupCategory.RECENT).path
    rig.h.rounds.complete_pending(view.round_id, True, True)
    with StartupService(rig.paths).start() as runtime:
        result = RestoreService(runtime).normal_restore(candidate)
        assert result.disposition == D.READY_RECOVERY
    assert (rig.h.record(view.round_id), rig.h.snapshot(view.round_id)) == saved


def test_restored_multiple_pending_uses_special_route_with_inspection_double(rig):
    candidate = candidate_and_changed_live(rig)

    class MultipleAfterRestore(InvariantService):
        live_calls = 0

        def inspect(self, path):
            report = super().inspect(path)
            if path == rig.paths.database:
                self.live_calls += 1
                return report if self.live_calls == 1 else replace(report, pending_count=2)
            return replace(report, pending_count=2)

    with StartupService(rig.paths).start() as runtime:
        result = RestoreService(runtime, invariants=MultipleAfterRestore()).normal_restore(
            candidate
        )
        assert result.disposition == D.RECOVERY_ERROR


@pytest.mark.parametrize("quarantine_failure", [False, True])
def test_emergency_restore_quarantines_damage_isolates_sidecars_without_verified_pre_restore(
    rig, monkeypatch, quarantine_failure
):
    candidate = candidate_and_changed_live(rig)
    original_candidate = candidate.read_bytes()
    rig.paths.database.write_bytes(b"damaged main")
    with StartupService(rig.paths).start() as runtime:
        assert runtime.result.disposition == D.EMERGENCY_RECOVERY
        # Isolate Restore's handling from SQLite's own startup journal recovery/cleanup.
        for file in sidecars(rig.paths.database):
            file.write_bytes(b"damaged sidecar")
        if quarantine_failure:
            original_copy = shutil.copyfile

            def copy(source, target):
                if source == rig.paths.database or source in sidecars(rig.paths.database):
                    raise PermissionError("quarantine unavailable")
                return original_copy(source, target)

            monkeypatch.setattr(shutil, "copyfile", copy)
        result = RestoreService(runtime).emergency_restore(candidate)
        assert result.disposition == D.READY_DRAFT
        assert bool(result.warnings) is quarantine_failure
    assert candidate.read_bytes() == original_candidate
    assert SQLiteHealth().verify(rig.paths.database).version == 1
    assert query(rig.paths.database, "SELECT count(*) FROM rounds") == [(1,)]
    assert not any(file.exists() for file in sidecars(rig.paths.database))
    assert len(list(rig.paths.database.parent.glob("UNVERIFIED_CORRUPT_*"))) == 3
    assert safety_files(rig) == []
    if not quarantine_failure:
        entries = rig.backup.inventory(BackupCategory.SAFETY)
        assert len(entries) == 4 and all(
            entry.kind == InventoryKind.QUARANTINE for entry in entries
        )


@pytest.mark.parametrize("bad_candidate", ["corrupt", "newer"])
def test_invalid_emergency_candidate_preserves_all_damaged_files(rig, bad_candidate):
    candidate = candidate_and_changed_live(rig)
    if bad_candidate == "corrupt":
        candidate.write_bytes(b"bad candidate")
    else:
        mutate(candidate, "PRAGMA user_version=99")
    rig.paths.database.write_bytes(b"damaged main")
    with StartupService(rig.paths).start() as runtime:
        for file in sidecars(rig.paths.database):
            file.write_bytes(b"damaged sidecar")
        before = {
            file: file.read_bytes() for file in (rig.paths.database, *sidecars(rig.paths.database))
        }
        assert (
            RestoreService(runtime).emergency_restore(candidate).disposition == D.DATA_SAFETY_ERROR
        )
    assert {file: file.read_bytes() for file in before} == before
    assert list(rig.paths.safety.iterdir()) == []


def test_candidate_stats_repaired_only_in_temp_original_backup_unchanged(rig):
    candidate = candidate_and_changed_live(rig)
    mutate(candidate, "DELETE FROM character_stats WHERE character_id=1")
    original = candidate.read_bytes()
    with StartupService(rig.paths).start() as runtime:
        result = RestoreService(runtime).normal_restore(candidate)
        assert result.disposition == D.READY_DRAFT
    assert rig.h.stats().included_games == 1
    assert candidate.read_bytes() == original
    assert query(candidate, "SELECT count(*) FROM character_stats WHERE character_id=1") == [(0,)]


def test_candidate_source_invariant_failure_leaves_live_unchanged(rig):
    candidate = candidate_and_changed_live(rig)
    mutate(candidate, "UPDATE characters SET display_name='wrong' WHERE character_id=1")
    with StartupService(rig.paths).start() as runtime:
        before = rig.paths.database.read_bytes()
        assert RestoreService(runtime).normal_restore(candidate).disposition == D.DATA_SAFETY_ERROR
        assert rig.paths.database.read_bytes() == before
        assert safety_files(rig) == []


def test_candidate_sidecars_rejected_without_touching_original_or_live(rig):
    candidate = candidate_and_changed_live(rig)
    candidate_sidecar = sidecars(candidate)[1]
    candidate_sidecar.write_bytes(b"unexplained WAL")
    with StartupService(rig.paths).start() as runtime:
        before = rig.paths.database.read_bytes()
        original = candidate.read_bytes()
        assert RestoreService(runtime).normal_restore(candidate).disposition == D.DATA_SAFETY_ERROR
        assert rig.paths.database.read_bytes() == before
        assert candidate.read_bytes() == original
        assert candidate_sidecar.read_bytes() == b"unexplained WAL"


def test_windows_unmanaged_open_connection_prevents_replacement_without_data_loss(rig):
    candidate = candidate_and_changed_live(rig)
    with StartupService(rig.paths).start() as runtime:
        before = rig.paths.database.read_bytes()
        with closing(open_existing(rig.paths.database)) as unmanaged:
            assert unmanaged.execute("SELECT count(*) FROM rounds").fetchone()[0] == 2
            result = RestoreService(runtime).normal_restore(candidate)
            assert result.disposition == D.DATA_SAFETY_ERROR
            assert rig.paths.database.read_bytes() == before
            assert unmanaged.execute("SELECT count(*) FROM rounds").fetchone()[0] == 2


def test_emergency_sidecar_isolation_failure_blocks_main_replacement(rig, monkeypatch):
    from probability_calibration_tool.infrastructure import restore_engine

    candidate = candidate_and_changed_live(rig)
    rig.paths.database.write_bytes(b"damaged main")
    with StartupService(rig.paths).start() as runtime:
        for file in sidecars(rig.paths.database):
            file.write_bytes(b"damaged sidecar")
        before = {
            file: file.read_bytes() for file in (rig.paths.database, *sidecars(rig.paths.database))
        }
        original = restore_engine.os.replace

        def fail(source, target):
            if source in sidecars(rig.paths.database):
                raise PermissionError("Cannot isolate old SQLite sidecar")
            return original(source, target)

        monkeypatch.setattr(restore_engine.os, "replace", fail)
        result = RestoreService(runtime).emergency_restore(candidate)
        assert result.disposition == D.DATA_SAFETY_ERROR
        assert {file: file.read_bytes() for file in before} == before
        assert safety_files(rig) == []
