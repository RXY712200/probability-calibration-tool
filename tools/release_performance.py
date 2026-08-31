"""Release-only deterministic bulk fixture and real 50k/100k production-path smoke."""

import argparse
import ctypes
import gc
import json
import sqlite3
import sys
import tempfile
from contextlib import closing
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import perf_counter
from uuid import UUID

STAMP = datetime(2026, 1, 1, tzinfo=UTC)


def memory_sample():
    """Windows process metrics include native SciPy/SQLite memory, not just Python objects."""
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            *[
                (name, ctypes.c_size_t)
                for name in (
                    "PeakWorkingSetSize",
                    "WorkingSetSize",
                    "QuotaPeakPagedPoolUsage",
                    "QuotaPagedPoolUsage",
                    "QuotaPeakNonPagedPoolUsage",
                    "QuotaNonPagedPoolUsage",
                    "PagefileUsage",
                    "PeakPagefileUsage",
                    "PrivateUsage",
                )
            ],
        ]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(Counters),
        wintypes.DWORD,
    ]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    if not psapi.GetProcessMemoryInfo(
        kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    return {
        "working_set_bytes": counters.WorkingSetSize,
        "peak_working_set_bytes": counters.PeakWorkingSetSize,
        "private_bytes": counters.PrivateUsage,
    }


def round_id(index):
    # IDs run in reverse order deliberately: chronological meaning comes from timestamps.
    return str(UUID(int=(1 << 120) - index, version=4))


def build_fixture(path, count):
    from probability_calibration_tool import core
    from probability_calibration_tool.application.analysis_builder import (
        build_snapshot,
        validate_prediction,
    )
    from probability_calibration_tool.application.commands import CalculateCommand
    from probability_calibration_tool.persistence.database import create_connection, serialize_utc
    from probability_calibration_tool.persistence.schema import initialize_v1

    assert count > 0 and count % 10 == 0
    command = CalculateCommand(1, False, 70, "2.00", "3.00")
    prediction = validate_prediction(command)
    template = asdict(build_snapshot(prediction, [], STAMP))
    subject_odds = core.analyze_subjective_odds(prediction.subjective, 2.0, 3.0)
    regime = "regime-1-1"
    wins = losses = 0
    round_columns = (
        "round_id",
        "created_at",
        "calculated_at",
        "last_updated_at",
        "completed_at",
        "character_id",
        "history_regime_id",
        "reference_history",
        "p_h_raw",
        "win_odds_raw",
        "lose_odds_raw",
        "win_odds",
        "lose_odds",
        "status",
        "revision_count",
        "result",
        "include_character_history",
        "history_exposed",
        "subjective_independence_compromised",
    )
    with closing(create_connection(path)) as db:
        initialize_v1(db)
        db.execute("BEGIN IMMEDIATE")
        # Test-only seed timestamps precede the deterministic synthetic history.
        db.execute(
            "UPDATE history_regimes SET started_at=?", (serialize_utc(STAMP - timedelta(days=1)),)
        )
        db.execute("UPDATE character_stats SET updated_at=?", (serialize_utc(STAMP),))
        db.execute("UPDATE meta SET updated_at=?", (serialize_utc(STAMP),))
        round_batch, snapshot_batch = [], []
        insert_round = f"INSERT INTO rounds ({', '.join(round_columns)}) VALUES ({', '.join('?' for _ in round_columns)})"
        insert_snapshot = f"INSERT INTO round_analysis_snapshots ({', '.join(template)}) VALUES ({', '.join('?' for _ in template)})"
        for index in range(count):
            stamp = serialize_utc(STAMP + timedelta(seconds=index * 2))
            completed = serialize_utc(STAMP + timedelta(seconds=index * 2 + 1))
            identity = round_id(index)
            result = index % 10 < 7
            round_batch.append(
                (
                    identity,
                    stamp,
                    stamp,
                    completed,
                    completed,
                    1,
                    regime,
                    0,
                    70,
                    "2.00",
                    "3.00",
                    2.0,
                    3.0,
                    "completed",
                    0,
                    int(result),
                    1,
                    0,
                    0,
                )
            )
            # Use accepted Core functions for EVERY prior-history snapshot. No fake repeated snapshot.
            history = core.compute_historical_estimate(wins, losses)
            odds = core.analyze_historical_odds(history, 2.0, 3.0)
            snapshot = dict(
                template,
                round_id=identity,
                history_model_status=history.status,
                history_statistically_ready=int(history.statistically_ready),
                history_wins=wins,
                history_losses=losses,
                history_sample_size=index,
                history_probability=history.probability,
                history_lower=history.lower,
                history_upper=history.upper,
                history_data_through_at=stamp,
                last_included_historical_round_id=None if index == 0 else round_id(index - 1),
            )
            for side in ("win", "lose"):
                historical = None if odds is None else getattr(odds, side)
                for field in (
                    "ev_center",
                    "ev_min",
                    "ev_max",
                    "ev_state",
                    "threshold_posterior_probability",
                ):
                    snapshot[f"historical_{side}_{field}"] = (
                        None if historical is None else getattr(historical, field)
                    )
                snapshot[f"{side}_model_relation"] = core.classify_model_relation(
                    getattr(subject_odds, side).ev_state,
                    None if historical is None else historical.ev_state,
                )
            snapshot_batch.append(tuple(snapshot.values()))
            wins += result
            losses += not result
            if len(round_batch) == 1000 or index == count - 1:
                db.executemany(insert_round, round_batch)
                db.executemany(insert_snapshot, snapshot_batch)
                round_batch.clear()
                snapshot_batch.clear()
        db.execute(
            "UPDATE character_stats SET included_games=?, wins=?, losses=?, last_included_round_id=?, updated_at=? WHERE character_id=1",
            (count, wins, losses, round_id(count - 1), completed),
        )
        db.commit()
    return {
        "rounds": count,
        "snapshots": count,
        "wins": wins,
        "losses": losses,
        "character_id": 1,
        "regime_id": regime,
        "last_included_round_id": round_id(count - 1),
    }


@dataclass
class FixedClock:
    value: datetime

    def now(self):
        return self.value


def exercise(root, count):
    from probability_calibration_tool.application.commands import CalculateCommand
    from probability_calibration_tool.application.invariant_service import InvariantService
    from probability_calibration_tool.application.maintenance_service import MaintenanceService
    from probability_calibration_tool.application.ports import UUIDGenerator
    from probability_calibration_tool.application.reliability_views import StartupDisposition
    from probability_calibration_tool.application.round_service import RoundService
    from probability_calibration_tool.application.startup_service import StartupService
    from probability_calibration_tool.application.stats_validation_service import (
        StatsValidationService,
    )
    from probability_calibration_tool.infrastructure.backup import BackupCategory, BackupService
    from probability_calibration_tool.infrastructure.paths import AppPaths
    from tools.release_verify import verify_database

    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=False)
    paths = AppPaths.from_root(root)
    paths.create_directories()
    evidence = {"root": str(root), "timings_seconds": {}, "memory": {"before": memory_sample()}}
    timings = evidence["timings_seconds"]
    start = perf_counter()
    evidence["fixture"] = build_fixture(paths.database, count)
    timings["fixture"] = perf_counter() - start
    evidence["initial_integrity"] = verify_database(paths.database)
    start = perf_counter()
    invariants = InvariantService().inspect(paths.database)
    assert not invariants.issues and invariants.pending_count == 0
    timings["invariant_inspection"] = perf_counter() - start
    evidence["memory"]["after_invariants"] = memory_sample()
    # Damage ONLY this generated cache; the real StartupService must rebuild it.
    with closing(sqlite3.connect(paths.database)) as db:
        db.execute("UPDATE character_stats SET stats_version=99 WHERE character_id=1")
        db.commit()

    class TimedStatsValidation(StatsValidationService):
        def validate(self, *args, **kwargs):
            started = perf_counter()
            result = super().validate(*args, **kwargs)
            timings["stats_validation_and_rebuild"] = perf_counter() - started
            return result

    start = perf_counter()
    with StartupService(paths, stats=TimedStatsValidation()).start() as runtime:
        timings["startup_including_repair_and_daily"] = perf_counter() - start
        assert runtime.result.disposition == StartupDisposition.READY_DRAFT, runtime.result
        assert any("rebuilt" in warning for warning in runtime.result.warnings)
        factory = runtime.uow_factory()
        with factory() as uow:
            stats = uow.stats.get(1, "regime-1-1")
            assert (stats.included_games, stats.wins, stats.losses, stats.stats_version) == (
                count,
                count * 7 // 10,
                count * 3 // 10,
                1,
            )
            assert stats.last_included_round_id == round_id(count - 1)
            assert len(uow.rounds.eligible_history(1, "regime-1-1")) == count
        evidence["stats_rebuilt"] = asdict(stats)
        start = perf_counter()
        maintenance = MaintenanceService(factory).list_characters()
        assert len(maintenance) == 34 and maintenance[0].included_sample_count == count
        timings["maintenance"] = perf_counter() - start
        evidence["memory"]["before_calculate"] = memory_sample()
        clock = FixedClock(STAMP + timedelta(seconds=count * 2 + 10))
        service = RoundService(factory, clock, UUIDGenerator())
        start = perf_counter()
        view = service.calculate(CalculateCommand(1, True, 70, "2.00", "3.00"))
        timings["calculate"] = perf_counter() - start
        assert view.history.sample_size == count and view.history_exposed
        with factory() as uow:
            snapshot = uow.snapshots.get(view.round_id)
            assert snapshot.history_sample_size == count
            assert snapshot.last_included_historical_round_id == round_id(count - 1)
        clock.value += timedelta(seconds=1)
        start = perf_counter()
        service.complete_pending(view.round_id, True, True)
        timings["complete"] = perf_counter() - start
        with factory() as uow:
            assert uow.snapshots.get(view.round_id) == snapshot
            assert len(uow.rounds.eligible_history(1, "regime-1-1")) == count + 1
        evidence["prediction_sample_size"] = count
        evidence["eligible_after_completion"] = count + 1
        evidence["frozen_snapshot_unchanged"] = True
        start = perf_counter()
        backup = BackupService(paths, logger=runtime.logger).create(BackupCategory.RECENT)
        timings["large_online_backup"] = perf_counter() - start
        evidence["backup_integrity"] = verify_database(backup.path)
        assert evidence["backup_integrity"]["completed"] == count + 1
        # Repeated real source-inventory inspections: record retained memory, do not impose an MB gate.
        repeat_memory, repeat_timings = [], []
        for _ in range(3):
            start = perf_counter()
            assert not InvariantService().inspect(paths.database).issues
            repeat_timings.append(perf_counter() - start)
            gc.collect()
            repeat_memory.append(memory_sample())
        evidence["repeated_invariant_seconds"] = repeat_timings
        evidence["memory"]["repeated_invariants_after_gc"] = repeat_memory
    evidence["final_integrity"] = verify_database(paths.database, final_manual=True)
    evidence["memory"]["final"] = memory_sample()
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, choices=(50000, 100000), default=100000)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    root = args.root or Path(tempfile.mkdtemp(prefix="pct-release-performance-")) / "app"
    evidence = exercise(root, args.rounds)
    serialized = json.dumps(evidence, indent=2, default=str)
    if args.evidence:
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    main()
