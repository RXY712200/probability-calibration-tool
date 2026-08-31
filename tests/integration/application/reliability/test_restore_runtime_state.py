"""Restore operation failures must not overwrite unchanged live-runtime health."""

from dataclasses import replace

import pytest
from infrastructure.helpers import InjectedFailure, mutate, query

from application.helpers import COMMAND
from probability_calibration_tool.application.invariant_service import InvariantService
from probability_calibration_tool.application.reliability_views import StartupDisposition as D
from probability_calibration_tool.application.restore_service import RestoreService
from probability_calibration_tool.application.runtime_context import RuntimeBusyError
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.infrastructure.backup import BackupCategory, InventoryKind
from probability_calibration_tool.infrastructure.sqlite_health import sidecars


def candidate_with_changed_live(rig):
    rig.h.seed_history(1, 0)
    candidate = rig.backup.create(BackupCategory.RECENT).path
    rig.h.seed_history(0, 1)
    return candidate


def verified_safety(rig):
    return [
        entry.path
        for entry in rig.backup.inventory(BackupCategory.SAFETY)
        if entry.kind == InventoryKind.VALID
    ]


def assert_ready_preserved(runtime, previous):
    assert runtime.result is previous
    assert runtime.unsafe_database is False
    with runtime.uow_factory()() as uow:
        assert len(uow.characters.list_all()) == 34


@pytest.mark.parametrize("bad_candidate", ["corrupt", "newer"])
def test_normal_invalid_candidate_preserves_ready_runtime(rig, bad_candidate):
    candidate = candidate_with_changed_live(rig)
    if bad_candidate == "corrupt":
        candidate.write_bytes(b"corrupt candidate")
    else:
        mutate(candidate, "PRAGMA user_version=99")
    original = candidate.read_bytes()
    with StartupService(rig.paths).start() as runtime:
        previous = runtime.result
        assert previous.disposition == D.READY_DRAFT
        before = rig.paths.database.read_bytes()
        result = RestoreService(runtime).normal_restore(candidate)
        assert result.disposition == D.DATA_SAFETY_ERROR and result.error is not None
        assert rig.paths.database.read_bytes() == before
        assert candidate.read_bytes() == original
        assert verified_safety(rig) == []
        assert_ready_preserved(runtime, previous)


def test_pending_rejection_preserves_recovery_runtime_and_pending(rig):
    candidate = rig.backup.create(BackupCategory.RECENT).path
    pending = rig.h.rounds.calculate(COMMAND)
    with StartupService(rig.paths).start() as runtime:
        previous = runtime.result
        assert previous.disposition == D.READY_RECOVERY
        before = rig.paths.database.read_bytes()
        result = RestoreService(runtime).normal_restore(candidate)
        assert result.disposition == D.DATA_SAFETY_ERROR
        assert rig.paths.database.read_bytes() == before
        assert verified_safety(rig) == []
        assert_ready_preserved(runtime, previous)
        with runtime.uow_factory()() as uow:
            assert [row.round_id for row in uow.rounds.list_pending()] == [pending.round_id]


def test_busy_rejection_preserves_current_and_subsequent_managed_uow(rig):
    candidate = candidate_with_changed_live(rig)
    with StartupService(rig.paths).start() as runtime:
        previous = runtime.result
        before = rig.paths.database.read_bytes()
        with runtime.uow_factory()() as uow:
            result = RestoreService(runtime).normal_restore(candidate)
            assert result.disposition == D.DATA_SAFETY_ERROR
            assert len(uow.characters.list_all()) == 34
            assert runtime.result is previous
            assert runtime.unsafe_database is False
        assert rig.paths.database.read_bytes() == before
        assert verified_safety(rig) == []
        assert_ready_preserved(runtime, previous)


@pytest.mark.parametrize("fault", ["temp_prepare", "temp_validation", "safety", "replace"])
def test_pre_replacement_fault_preserves_ready_runtime_and_allows_retry(rig, monkeypatch, fault):
    candidate = candidate_with_changed_live(rig)
    original = candidate.read_bytes()
    with StartupService(rig.paths).start() as runtime:
        previous = runtime.result
        before = rig.paths.database.read_bytes()
        service = RestoreService(runtime)

        def fail(*args, **kwargs):
            raise InjectedFailure(fault)

        target, name = {
            "temp_prepare": (service.engine, "prepare_copy"),
            "temp_validation": (service, "_validate"),
            "safety": (service.safety, "create_verified_safety_backup"),
            "replace": (service.engine, "replace"),
        }[fault]
        with monkeypatch.context() as patch:
            patch.setattr(target, name, fail)
            result = service.normal_restore(candidate)
        assert result.disposition == D.DATA_SAFETY_ERROR
        assert rig.paths.database.read_bytes() == before
        assert candidate.read_bytes() == original
        assert not list(rig.paths.database.parent.glob(".restore_*"))
        assert_ready_preserved(runtime, previous)
        retained = verified_safety(rig)
        assert len(retained) == (1 if fault == "replace" else 0)
        retained_bytes = {path: path.read_bytes() for path in retained}
        retry = service.normal_restore(candidate)
        assert runtime.result is retry and retry.disposition == D.READY_DRAFT
        assert runtime.unsafe_database is False
        assert query(rig.paths.database, "SELECT count(*) FROM rounds") == [(1,)]
        assert {path: path.read_bytes() for path in retained} == retained_bytes


@pytest.mark.parametrize("sidecar_index", [0, 1, 2])
def test_sidecar_rejection_preserves_runtime_state(rig, monkeypatch, sidecar_index):
    candidate = candidate_with_changed_live(rig)
    with StartupService(rig.paths).start() as runtime:
        previous = runtime.result
        before = rig.paths.database.read_bytes()
        service = RestoreService(runtime)
        original_safety = service.safety.create_verified_safety_backup
        sidecar = sidecars(rig.paths.database)[sidecar_index]

        def safety_with_sidecar(reason):
            original_safety(reason)
            sidecar.write_bytes(b"unexplained sidecar")

        monkeypatch.setattr(service.safety, "create_verified_safety_backup", safety_with_sidecar)
        result = service.normal_restore(candidate)
        assert result.disposition == D.DATA_SAFETY_ERROR
        assert runtime.result is previous and runtime.unsafe_database is False
        assert rig.paths.database.read_bytes() == before
        assert sidecar.read_bytes() == b"unexplained sidecar"
        assert len(verified_safety(rig)) == 1
        # Remove only this test-injected obstruction before reopening SQLite.
        sidecar.unlink()
        assert_ready_preserved(runtime, previous)


@pytest.mark.parametrize("bad_candidate", ["corrupt", "newer"])
def test_invalid_emergency_candidate_preserves_emergency_runtime(rig, bad_candidate):
    candidate = candidate_with_changed_live(rig)
    if bad_candidate == "corrupt":
        candidate.write_bytes(b"corrupt candidate")
    else:
        mutate(candidate, "PRAGMA user_version=99")
    original = candidate.read_bytes()
    rig.paths.database.write_bytes(b"damaged live database")
    with StartupService(rig.paths).start() as runtime:
        previous = runtime.result
        assert previous.disposition == D.EMERGENCY_RECOVERY
        assert runtime.unsafe_database is True
        for path in sidecars(rig.paths.database):
            path.write_bytes(b"damaged sidecar")
        before = {p: p.read_bytes() for p in (rig.paths.database, *sidecars(rig.paths.database))}
        result = RestoreService(runtime).emergency_restore(candidate)
        assert result.disposition == D.DATA_SAFETY_ERROR and result.error is not None
        assert runtime.result is previous
        assert runtime.unsafe_database is True
        assert {p: p.read_bytes() for p in before} == before
        assert candidate.read_bytes() == original
        assert list(rig.paths.safety.iterdir()) == []


@pytest.mark.parametrize("pending", [False, True])
@pytest.mark.parametrize("emergency", [False, True])
def test_successful_restore_commits_new_runtime_state(rig, pending, emergency):
    if pending:
        view = rig.h.rounds.calculate(COMMAND)
    candidate = rig.backup.create(BackupCategory.RECENT).path
    if pending:
        rig.h.rounds.complete_pending(view.round_id, True, True)
    if emergency:
        rig.paths.database.write_bytes(b"damaged live database")
    with StartupService(rig.paths).start() as runtime:
        previous = runtime.result
        assert previous.disposition == (D.EMERGENCY_RECOVERY if emergency else D.READY_DRAFT)
        assert runtime.unsafe_database is emergency
        service = RestoreService(runtime)
        result = (
            service.emergency_restore(candidate) if emergency else service.normal_restore(candidate)
        )
        assert result.disposition == (D.READY_RECOVERY if pending else D.READY_DRAFT)
        assert runtime.result is result and runtime.result is not previous
        assert_ready_preserved(runtime, result)
        with runtime.uow_factory()() as uow:
            assert len(uow.rounds.list_pending()) == int(pending)


def test_successful_replacement_with_multiple_pending_marks_runtime_unsafe(rig):
    candidate = candidate_with_changed_live(rig)

    class MultipleAfterReplacement(InvariantService):
        live_calls = 0

        def inspect(self, path):
            report = super().inspect(path)
            if path == rig.paths.database:
                self.live_calls += 1
                if self.live_calls == 1:
                    return report
            return replace(report, pending_count=2)

    with StartupService(rig.paths).start() as runtime:
        result = RestoreService(runtime, invariants=MultipleAfterReplacement()).normal_restore(
            candidate
        )
        assert result.disposition == D.RECOVERY_ERROR
        assert runtime.result is result and runtime.unsafe_database is True
        with pytest.raises(RuntimeBusyError), runtime.uow_factory()():
            pytest.fail("Unsafe runtime unexpectedly admitted a managed UoW")


def test_post_replacement_failure_commits_emergency_runtime_and_retains_safety(rig, monkeypatch):
    candidate = candidate_with_changed_live(rig)
    with StartupService(rig.paths).start() as runtime:
        previous = runtime.result
        service = RestoreService(runtime)
        original = service._validate

        def validate(path, **kwargs):
            if path == rig.paths.database:
                raise InjectedFailure("post-replacement validation")
            return original(path, **kwargs)

        monkeypatch.setattr(service, "_validate", validate)
        result = service.normal_restore(candidate)
        assert result.disposition == D.EMERGENCY_RECOVERY
        assert runtime.result is result and runtime.result is not previous
        assert runtime.unsafe_database is True
        assert query(rig.paths.database, "SELECT count(*) FROM rounds") == [(1,)]
        backups = verified_safety(rig)
        assert len(backups) == 1
        assert query(backups[0], "SELECT count(*) FROM rounds") == [(2,)]
        with pytest.raises(RuntimeBusyError), runtime.uow_factory()():
            pytest.fail("Unsafe runtime unexpectedly admitted a managed UoW")
