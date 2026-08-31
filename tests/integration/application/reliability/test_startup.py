import sqlite3
from contextlib import closing
from types import SimpleNamespace

import pytest
from infrastructure.helpers import InjectedFailure, mutate

from application.helpers import COMMAND
from probability_calibration_tool.application import startup_service as startup_module
from probability_calibration_tool.application.invariant_service import InvariantService
from probability_calibration_tool.application.reliability_views import InvariantReport
from probability_calibration_tool.application.reliability_views import StartupDisposition as D
from probability_calibration_tool.application.runtime_context import RuntimeBusyError
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.infrastructure.backup import BackupCategory
from probability_calibration_tool.infrastructure.paths import AppPaths
from probability_calibration_tool.infrastructure.sqlite_health import SQLiteHealth


def test_fresh_temporary_initialization_then_daily_and_long_lived_context(tmp_path, monkeypatch):
    paths = AppPaths.from_root(tmp_path / "fresh")
    original = startup_module.os.replace
    installs = []

    def install(source, target):
        if target == paths.database:
            assert not target.exists()
            assert source.parent == target.parent and source.name.startswith(".initialize_")
            assert SQLiteHealth().verify(source).version == 1
            assert not InvariantService().inspect(source).issues
            installs.append(source)
        return original(source, target)

    monkeypatch.setattr(startup_module.os, "replace", install)
    with StartupService(paths).start() as runtime:
        assert runtime.result.disposition == D.READY_DRAFT
        assert runtime.lock.held
        assert len(installs) == 1 and not installs[0].exists()
        assert len(list(paths.daily.glob("daily_*.db"))) == 1
        with runtime.uow_factory()() as uow:
            assert len(uow.characters.list_all()) == 34
            with pytest.raises(RuntimeBusyError), runtime.quiescent():
                pytest.fail("Open UoW must prevent quiescence")
        with runtime.quiescent(), pytest.raises(RuntimeBusyError), runtime.uow_factory()():
            pytest.fail("Paused runtime must prevent a new UoW")
    assert not runtime.lock.held


@pytest.mark.parametrize("fault", ["initializer", "integrity", "invariant", "install"])
def test_fresh_failure_never_installs_live_database(tmp_path, monkeypatch, fault):
    paths = AppPaths.from_root(tmp_path / "fresh")
    service = StartupService(paths)

    def fail(*args, **kwargs):
        raise InjectedFailure(fault)

    if fault == "initializer":
        service.initializer = fail
    elif fault == "integrity":
        monkeypatch.setattr(service.health, "verify", fail)
    elif fault == "invariant":
        monkeypatch.setattr(service.invariants, "require_valid", fail)
    else:
        monkeypatch.setattr(startup_module.os, "replace", fail)
    with service.start() as runtime:
        assert runtime.result.disposition == D.DATA_SAFETY_ERROR
        assert not paths.database.exists()
        assert list(paths.database.parent.glob(".initialize_*")) == []


@pytest.mark.parametrize(
    "existing", ["zero_bytes", "empty_sqlite", "version_zero_table", "corrupt"]
)
def test_preexisting_empty_or_corrupt_is_never_fresh(tmp_path, existing):
    paths = AppPaths.from_root(tmp_path / "existing")
    paths.create_directories()
    if existing == "zero_bytes":
        paths.database.touch()
    elif existing == "corrupt":
        paths.database.write_bytes(b"broken SQLite")
    else:
        with closing(sqlite3.connect(paths.database)) as connection:
            if existing == "version_zero_table":
                connection.execute("CREATE TABLE unrelated (value)")
    before = paths.database.read_bytes()
    with StartupService(paths).start() as runtime:
        assert runtime.result.disposition in (D.DATA_SAFETY_ERROR, D.EMERGENCY_RECOVERY)
        assert paths.database.read_bytes() == before
        assert list(paths.daily.iterdir()) == []


def test_newer_schema_rejected_before_seeding_stats_or_backup(rig, monkeypatch):
    mutate(rig.paths.database, "PRAGMA user_version=99")
    before = rig.paths.database.read_bytes()
    service = StartupService(rig.paths)

    def forbidden(*args):
        pytest.fail("Newer schema must not run application writes or source inspection")

    monkeypatch.setattr(service.invariants, "inspect", forbidden)
    monkeypatch.setattr(service.stats, "validate", forbidden)
    with service.start() as runtime:
        assert runtime.result.disposition == D.UNSUPPORTED_NEWER_SCHEMA
    assert rig.paths.database.read_bytes() == before
    assert list(rig.paths.daily.iterdir()) == []


@pytest.mark.parametrize("pending", [False, True])
def test_healthy_existing_routes_and_daily_failure_is_nonfatal(rig, monkeypatch, pending):
    if pending:
        rig.h.rounds.calculate(COMMAND)
    before = rig.h.capture()

    def fail(*args):
        raise InjectedFailure("Daily unavailable")

    monkeypatch.setattr(rig.backup, "_copy_online", fail)
    with StartupService(rig.paths, backup_factory=lambda *args: rig.backup).start() as runtime:
        assert runtime.result.disposition == (D.READY_RECOVERY if pending else D.READY_DRAFT)
        assert runtime.result.warnings
        assert runtime.result.error is None
    assert rig.h.capture() == before


def test_second_instance_does_not_open_full_log(rig, monkeypatch):
    with StartupService(rig.paths).start() as first:
        assert first.result.disposition == D.READY_DRAFT

        def forbidden(*args):
            pytest.fail("Second instance must not open shared rotating log")

        monkeypatch.setattr(startup_module, "full_logger", forbidden)
        with StartupService(rig.paths).start() as second:
            assert second.result.disposition == D.ALREADY_RUNNING
        assert first.lock.held


def test_multiple_pending_precedes_generic_invariant_and_suppresses_daily(rig):
    fake = SimpleNamespace(inspect=lambda path: InvariantReport(("additional source issue",), 2))
    with StartupService(rig.paths, invariants=fake).start() as runtime:
        assert runtime.result.disposition == D.RECOVERY_ERROR
        assert list(rig.paths.daily.iterdir()) == []


def test_source_invariant_failure_is_not_repaired_or_backed_up(rig):
    mutate(rig.paths.database, "UPDATE characters SET display_name='wrong' WHERE character_id=1")
    before = rig.h.capture()
    with StartupService(rig.paths).start() as runtime:
        assert runtime.result.disposition == D.DATA_SAFETY_ERROR
        assert runtime.result.error.error_id
    assert rig.h.capture() == before
    assert list(rig.paths.daily.iterdir()) == []


def test_startup_repairs_cache_before_backup(rig, monkeypatch):
    rig.h.seed_history(1, 0)
    mutate(rig.paths.database, "UPDATE character_stats SET stats_version=9 WHERE character_id=1")
    original = rig.backup.create
    events = []

    def create(category, *args):
        assert category == BackupCategory.DAILY
        assert rig.h.stats().stats_version == 1
        events.append("daily_after_repair")
        return original(category, *args)

    monkeypatch.setattr(rig.backup, "create", create)
    with StartupService(rig.paths, backup_factory=lambda *args: rig.backup).start() as runtime:
        assert runtime.result.disposition == D.READY_DRAFT
        assert runtime.result.warnings
    assert events == ["daily_after_repair"]


def test_startup_stats_failure_is_safety_error_without_daily(rig, monkeypatch):
    service = StartupService(rig.paths)

    def fail(*args):
        raise InjectedFailure("stats batch")

    monkeypatch.setattr(service.stats, "validate", fail)
    before = rig.h.capture()
    with service.start() as runtime:
        assert runtime.result.disposition == D.DATA_SAFETY_ERROR
    assert rig.h.capture() == before
    assert list(rig.paths.daily.iterdir()) == []


def test_startup_strict_order_with_real_components_and_spies(rig, monkeypatch):
    events = []
    service = StartupService(rig.paths, backup_factory=lambda *args: rig.backup)
    original_directories = AppPaths.create_directories

    def directories(paths):
        events.append("directories")
        original_directories(paths)

    monkeypatch.setattr(AppPaths, "create_directories", directories)
    for name in ("bootstrap_logger", "full_logger"):
        original = getattr(startup_module, name)

        def logger(*args, _original=original, _name=name):
            events.append(_name)
            return _original(*args)

        monkeypatch.setattr(startup_module, name, logger)
    real_lock = service.lock_factory

    class LockSpy(real_lock):
        def acquire(self):
            events.append("lock")
            return super().acquire()

    service.lock_factory = LockSpy
    for component, method, label in (
        (service.health, "inspect", "probe"),
        (service.invariants, "inspect", "invariants"),
        (service.stats, "validate", "stats"),
        (rig.backup, "create", "daily"),
    ):
        original = getattr(component, method)

        def wrapped(*args, _original=original, _label=label, **kwargs):
            events.append(_label)
            return _original(*args, **kwargs)

        monkeypatch.setattr(component, method, wrapped)
    with service.start() as runtime:
        assert runtime.result.disposition == D.READY_DRAFT
    assert events[:4] == ["directories", "bootstrap_logger", "lock", "full_logger"]
    assert (
        events.index("probe")
        < events.index("invariants")
        < events.index("stats")
        < events.index("daily")
    )


def test_unsafe_runtime_cannot_create_business_uow(rig):
    rig.paths.database.write_bytes(b"broken")
    with StartupService(rig.paths).start() as runtime:
        assert runtime.result.disposition == D.EMERGENCY_RECOVERY
        with pytest.raises(RuntimeBusyError), runtime.uow_factory()():
            pytest.fail("Unsafe source must not reopen normal business writes")
