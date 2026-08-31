import shutil
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from probability_calibration_tool.application import CorrectionService
from probability_calibration_tool.infrastructure import backup as backup_module
from probability_calibration_tool.infrastructure.backup import (
    BackupCategory,
    BackupCoordinator,
    InventoryKind,
    SQLiteSafetyBackupAdapter,
)
from probability_calibration_tool.infrastructure.sqlite_health import (
    DatabaseHealthError,
    SQLiteHealth,
)

from .helpers import InjectedFailure, query


def valid(rig, category):
    return [entry for entry in rig.backup.inventory(category) if entry.kind == InventoryKind.VALID]


def test_online_backup_verified_version_and_representative_source_data(rig, monkeypatch):
    ids = rig.h.seed_history(2, 1)
    source_before = rig.h.capture()
    calls = []
    original_open = backup_module.open_existing

    class SpyConnection:
        def __init__(self, connection):
            self.connection = connection

        def __getattr__(self, name):
            return getattr(self.connection, name)

        def backup(self, destination):
            calls.append("online")
            self.connection.backup(destination)

    monkeypatch.setattr(
        backup_module, "open_existing", lambda path: SpyConnection(original_open(path))
    )
    monkeypatch.setattr(
        shutil, "copyfile", lambda *args: pytest.fail("Live DB must not use file copy")
    )
    original_verify = rig.backup.health.verify

    def verify(path, **kwargs):
        if "expected_version" in kwargs:
            calls.append(("verified", kwargs["expected_version"]))
        return original_verify(path, **kwargs)

    monkeypatch.setattr(rig.backup.health, "verify", verify)
    result = rig.backup.create(BackupCategory.RECENT)
    assert calls[:2] == ["online", ("verified", 1)]
    assert SQLiteHealth().verify(result.path).version == 1
    assert {row[0] for row in query(result.path, "SELECT round_id FROM rounds")} == set(ids)
    assert query(result.path, "SELECT count(*) FROM round_analysis_snapshots") == [(3,)]
    assert rig.h.capture() == source_before


@pytest.mark.parametrize(
    "category,limit", [(BackupCategory.RECENT, 5), (BackupCategory.SAFETY, 10)]
)
def test_independent_retention_keeps_newest_valid(rig, category, limit):
    other = BackupCategory.SAFETY if category == BackupCategory.RECENT else BackupCategory.RECENT
    other_path = rig.backup.create(other, "pre_restore").path
    created = []
    for _ in range(limit + 2):
        created.append(rig.backup.create(category, "pre_migration").path)
        rig.advance()
    assert {entry.path for entry in valid(rig, category)} == set(created[-limit:])
    assert not any(path.exists() for path in created[:-limit])
    assert other_path.exists()


@pytest.mark.parametrize("failure", ["creation", "integrity", "version"])
def test_failed_candidate_preserves_previous_five_byte_for_byte(rig, monkeypatch, failure):
    paths = [rig.backup.create(BackupCategory.RECENT).path for _ in range(5)]
    before = {path: path.read_bytes() for path in paths}
    if failure == "creation":

        def fail(*args):
            raise InjectedFailure("online failure")

        monkeypatch.setattr(rig.backup, "_copy_online", fail)
    elif failure == "integrity":
        original = rig.backup.health.verify

        def fail(path, **kwargs):
            if "expected_version" in kwargs:
                raise DatabaseHealthError("candidate integrity")
            return original(path, **kwargs)

        monkeypatch.setattr(rig.backup.health, "verify", fail)
    else:
        original = rig.backup._copy_online

        def wrong_version(path):
            return original(path) + 1

        monkeypatch.setattr(rig.backup, "_copy_online", wrong_version)
    with pytest.raises((InjectedFailure, DatabaseHealthError)):
        rig.backup.create(BackupCategory.RECENT)
    assert {path: path.read_bytes() for path in paths} == before
    assert set(rig.paths.recent.iterdir()) == set(paths)


def test_inventory_preserves_corrupt_temp_quarantine_unrelated(rig):
    corrupt = rig.backup.create(BackupCategory.RECENT).path
    corrupt.write_bytes(b"corrupt")
    names = {
        ".candidate_abandoned.tmp": InventoryKind.TEMPORARY,
        "UNVERIFIED_CORRUPT_saved.db": InventoryKind.QUARANTINE,
        "unrelated.db": InventoryKind.UNRELATED,
    }
    for name in names:
        (rig.paths.recent / name).write_bytes(b"preserve")
    for _ in range(7):
        rig.backup.create(BackupCategory.RECENT)
        rig.advance()
    inventory = {
        entry.path.name: entry.kind for entry in rig.backup.inventory(BackupCategory.RECENT)
    }
    assert inventory[corrupt.name] == InventoryKind.CORRUPT
    assert all(inventory[name] == kind for name, kind in names.items())
    assert len(valid(rig, BackupCategory.RECENT)) == 5
    assert corrupt.read_bytes() == b"corrupt"


def test_rotation_delete_failure_stops_immediately_and_overretains(rig, monkeypatch):
    with monkeypatch.context() as patch:
        patch.setattr(rig.backup, "_rotate", lambda category: ())
        old = []
        for _ in range(7):
            old.append(rig.backup.create(BackupCategory.RECENT).path)
            rig.advance()
    original = Path.unlink
    calls = []

    def unlink(path, *args, **kwargs):
        if path in old:
            calls.append(path)
            if path == old[0]:
                raise PermissionError("oldest locked")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", unlink)
    result = rig.backup.create(BackupCategory.RECENT)
    assert result.path.exists() and result.warnings
    assert calls == [old[0]]
    assert all(path.exists() for path in old)
    assert len(valid(rig, BackupCategory.RECENT)) == 8


def test_daily_local_date_once_corrupt_replacement_and_seven_distinct_days(rig):
    first = rig.backup.create(BackupCategory.DAILY)
    duplicate = rig.backup.create(BackupCategory.DAILY)
    assert not duplicate.created and duplicate.path == first.path
    first.path.write_bytes(b"corrupt daily")
    replacement = rig.backup.create(BackupCategory.DAILY)
    assert replacement.created and replacement.path != first.path and first.path.exists()
    dates = [rig.calendar.value]
    for _ in range(8):
        rig.advance()
        dates.append(rig.calendar.value)
        rig.backup.create(BackupCategory.DAILY)
    retained = valid(rig, BackupCategory.DAILY)
    assert len(retained) == 7 and {entry.local_date for entry in retained} == set(dates[-7:])
    assert first.path.exists()


def test_daily_uses_injected_local_calendar_not_utc_date(rig):
    rig.h.clock.value = datetime(2026, 12, 31, 16, 30, tzinfo=UTC)
    rig.calendar.today = lambda: rig.h.clock.now().astimezone(timezone(timedelta(hours=8))).date()
    first = rig.backup.create(BackupCategory.DAILY)
    assert first.path.name.startswith("daily_2027-01-01_20261231T163000")
    rig.h.clock.value += timedelta(hours=10)  # Different UTC date, same local calendar date.
    assert not rig.backup.create(BackupCategory.DAILY).created
    rig.h.clock.value += timedelta(days=1)
    assert rig.backup.create(BackupCategory.DAILY).created


@pytest.mark.parametrize("category", ["recent", "daily"])
def test_nonfatal_backup_warning_does_not_revert_committed_main_data(rig, monkeypatch, category):
    rig.h.seed_history(1, 0)
    before = rig.h.capture()

    def fail(*args):
        raise InjectedFailure("backup unavailable")

    monkeypatch.setattr(rig.backup, "_copy_online", fail)
    result = getattr(BackupCoordinator(rig.backup), category)()
    assert result.backup is None and result.warning.error_id
    assert rig.h.capture() == before


def test_safety_adapter_satisfies_existing_correction_port_without_wiring_changes(rig, monkeypatch):
    round_id = rig.h.seed_history(1, 0)[0]
    adapter = SQLiteSafetyBackupAdapter(rig.backup)
    service = CorrectionService(rig.h.factory, rig.h.clock, rig.h.ids, adapter)
    before = rig.h.capture()
    with monkeypatch.context() as patch:

        def fail(*args):
            raise InjectedFailure("required backup")

        patch.setattr(rig.backup, "_copy_online", fail)
        with pytest.raises(InjectedFailure):
            service.correct_post_run(round_id, False, True, "correction")
    assert rig.h.capture() == before
    service.correct_post_run(round_id, False, True, "correction")
    assert len(valid(rig, BackupCategory.SAFETY)) == 1
    assert "pre_history_correction" in valid(rig, BackupCategory.SAFETY)[0].path.name
    assert list(rig.paths.recent.iterdir()) == []  # No Phase 6 callbacks attached.
