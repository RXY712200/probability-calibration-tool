import sqlite3
from contextlib import closing
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import pytest

from probability_calibration_tool.domain.enums import RoundStatus
from probability_calibration_tool.domain.records import CharacterStatsRecord, HistoryRegimeRecord
from probability_calibration_tool.persistence.database import create_connection
from probability_calibration_tool.persistence.repositories import (
    CharacterStatsRepository,
    HistoryRegimeRepository,
    MetaRepository,
    RoundRepository,
    SnapshotRepository,
)
from probability_calibration_tool.persistence.unit_of_work import UnitOfWork

from .helpers import STAMP, STAMP_TEXT, insert_row, make_round, make_snapshot, sql_values
from .test_repositories import assert_record_round_trip


def insert_test_regime(connection: sqlite3.Connection) -> None:
    insert_row(
        connection,
        "history_regimes",
        {
            "regime_id": "extra-regime",
            "character_id": 1,
            "regime_number": 2,
            "started_at": STAMP_TEXT,
            "ended_at": STAMP_TEXT,
            "active": 0,
            "reason": None,
        },
    )


@pytest.mark.parametrize("kind", ["pending", "completed", "voided-pending", "voided-completed"])
def test_round_update_round_trip_preserves_identity_and_other_rows(
    connection: sqlite3.Connection, kind: str
) -> None:
    repo = RoundRepository(connection)
    original = make_round()
    other = make_round("unrelated", RoundStatus.COMPLETED)
    repo.insert(original)
    repo.insert(other)
    status = {"pending": RoundStatus.PENDING, "completed": RoundStatus.COMPLETED}.get(
        kind, RoundStatus.VOIDED
    )
    updated = make_round(
        status=status,
        p_h_raw=61,
        win_odds_raw="2.125",
        win_odds=2.125,
        lose_odds_raw="3.5",
        lose_odds=3.5,
        revision_count=3,
        last_updated_at=STAMP + timedelta(minutes=2),
        reference_history=True,
        history_exposed=True,
        history_exposed_at=STAMP,
        subjective_independence_compromised=True,
    )
    if kind == "voided-completed":
        updated = replace(
            updated, result=False, include_character_history=False, completed_at=STAMP
        )
    repo.update(updated)
    assert_record_round_trip(repo.get(original.round_id), updated)
    assert_record_round_trip(repo.get(other.round_id), other)
    assert connection.execute("SELECT COUNT(*) FROM rounds").fetchone()[0] == 2


def test_round_update_relies_on_sqlite_constraints(connection: sqlite3.Connection) -> None:
    repo = RoundRepository(connection)
    original = make_round()
    repo.insert(original)
    with pytest.raises(sqlite3.IntegrityError):
        repo.update(replace(original, p_h_raw=-1))
    assert_record_round_trip(repo.get(original.round_id), original)


@pytest.mark.parametrize("closed", [False, True])
def test_regime_update_round_trip_preserves_identity_and_other_rows(
    connection: sqlite3.Connection, closed: bool
) -> None:
    repo = HistoryRegimeRepository(connection)
    original = repo.get("regime-1-1")
    other = repo.get("regime-1-2")
    assert original is not None
    updated = replace(
        original,
        started_at=STAMP,
        ended_at=STAMP + timedelta(days=1) if closed else None,
        active=not closed,
        reason="updated '原因'",
    )
    repo.update(updated)
    assert_record_round_trip(repo.get(original.regime_id), updated)
    assert_record_round_trip(repo.get(other.regime_id), other)
    assert connection.execute("SELECT COUNT(*) FROM history_regimes").fetchone()[0] == 34


def test_regime_update_relies_on_sqlite_constraints(connection: sqlite3.Connection) -> None:
    repo = HistoryRegimeRepository(connection)
    original = repo.get("regime-1-1")
    assert original is not None
    with pytest.raises(sqlite3.IntegrityError):
        repo.update(replace(original, active=False, ended_at=None))
    assert_record_round_trip(repo.get(original.regime_id), original)


@pytest.mark.parametrize("positive", [False, True])
def test_stats_insert_round_trip(connection: sqlite3.Connection, positive: bool) -> None:
    insert_test_regime(connection)
    insert_row(connection, "rounds", sql_values(make_round("prior", RoundStatus.COMPLETED)))
    record = CharacterStatsRecord(
        1, "extra-regime", int(positive), int(positive), 0, "prior" if positive else None, STAMP, 1
    )
    repo = CharacterStatsRepository(connection)
    repo.insert(record)
    assert_record_round_trip(repo.get(1, "extra-regime"), record)


def test_stats_insert_relies_on_sqlite_constraints(connection: sqlite3.Connection) -> None:
    insert_test_regime(connection)
    repo = CharacterStatsRepository(connection)
    with pytest.raises(sqlite3.IntegrityError):
        repo.insert(CharacterStatsRecord(1, "extra-regime", 0, 1, 0, None, STAMP, 1))
    assert repo.get(1, "extra-regime") is None


OPERATIONS = [
    "round-insert",
    "round-update",
    "regime-insert",
    "regime-update",
    "snapshot-insert",
    "snapshot-update",
    "stats-insert",
    "stats-rebuild",
    "meta-set",
]


def prepare_mutation(path: Path) -> None:
    with closing(create_connection(path)) as setup:
        insert_row(setup, "rounds", sql_values(make_round("prior", RoundStatus.COMPLETED)))
        insert_row(setup, "rounds", sql_values(make_round("existing", RoundStatus.COMPLETED)))
        insert_row(
            setup, "round_analysis_snapshots", sql_values(make_snapshot(round_id="existing"))
        )
        insert_test_regime(setup)


def mutate(
    rounds: RoundRepository,
    regimes: HistoryRegimeRepository,
    snapshots: SnapshotRepository,
    stats: CharacterStatsRepository,
    meta: MetaRepository,
    operation: str,
) -> None:
    if operation == "round-insert":
        rounds.insert(make_round())
    elif operation == "round-update":
        rounds.update(replace(rounds.get("existing"), p_h_raw=51))
    elif operation == "regime-insert":
        regimes.insert(HistoryRegimeRecord("inserted", 1, 3, STAMP, STAMP, False, None))
    elif operation == "regime-update":
        regimes.update(replace(regimes.get("extra-regime"), reason="changed"))
    elif operation == "snapshot-insert":
        snapshots.insert(make_snapshot(round_id="prior"))
    elif operation == "snapshot-update":
        snapshots.update(replace(make_snapshot(round_id="existing"), p_h_used=51))
    elif operation == "stats-insert":
        stats.insert(CharacterStatsRecord(1, "extra-regime", 0, 0, 0, None, STAMP, 1))
    elif operation == "stats-rebuild":
        stats.rebuild_stats(1, "regime-1-1")
    else:
        meta.set("transaction-probe", "changed")


PROBES = {
    "round-insert": ("SELECT COUNT(*) FROM rounds WHERE round_id = 'current'", 0, 1),
    "round-update": ("SELECT p_h_raw FROM rounds WHERE round_id = 'existing'", 50, 51),
    "regime-insert": ("SELECT COUNT(*) FROM history_regimes WHERE regime_id = 'inserted'", 0, 1),
    "regime-update": (
        "SELECT reason FROM history_regimes WHERE regime_id = 'extra-regime'",
        None,
        "changed",
    ),
    "snapshot-insert": (
        "SELECT COUNT(*) FROM round_analysis_snapshots WHERE round_id = 'prior'",
        0,
        1,
    ),
    "snapshot-update": (
        "SELECT p_h_used FROM round_analysis_snapshots WHERE round_id = 'existing'",
        50,
        51,
    ),
    "stats-insert": ("SELECT COUNT(*) FROM character_stats WHERE regime_id = 'extra-regime'", 0, 1),
    "stats-rebuild": (
        "SELECT included_games FROM character_stats WHERE character_id = 1 AND regime_id = 'regime-1-1'",
        0,
        2,
    ),
    "meta-set": ("SELECT COUNT(*) FROM meta WHERE key = 'transaction-probe'", 0, 1),
}


@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("commit", [False, True])
def test_direct_repository_writes_require_explicit_commit(
    db_path: Path, operation: str, commit: bool
) -> None:
    prepare_mutation(db_path)
    query, before, after = PROBES[operation]
    with (
        closing(create_connection(db_path)) as observer,
        closing(create_connection(db_path)) as writer,
    ):
        mutate(
            RoundRepository(writer),
            HistoryRegimeRepository(writer),
            SnapshotRepository(writer),
            CharacterStatsRepository(writer),
            MetaRepository(writer),
            operation,
        )
        assert writer.in_transaction
        assert observer.execute(query).fetchone()[0] == before
        if commit:
            writer.commit()
            assert observer.execute(query).fetchone()[0] == after
    with closing(create_connection(db_path)) as reopened:
        assert reopened.execute(query).fetchone()[0] == (after if commit else before)


@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("commit", [False, True])
def test_repository_write_after_uow_commit_requires_next_commit(
    db_path: Path, operation: str, commit: bool
) -> None:
    prepare_mutation(db_path)
    query, before, after = PROBES[operation]
    with closing(create_connection(db_path)) as observer, UnitOfWork(db_path) as uow:
        uow.meta.set("first-transaction", "committed")
        uow.commit()
        mutate(uow.rounds, uow.regimes, uow.snapshots, uow.stats, uow.meta, operation)
        assert observer.execute(query).fetchone()[0] == before
        if commit:
            uow.commit()
            assert observer.execute(query).fetchone()[0] == after
    with closing(create_connection(db_path)) as reopened:
        assert reopened.execute(query).fetchone()[0] == (after if commit else before)
        assert (
            reopened.execute("SELECT value FROM meta WHERE key = 'first-transaction'").fetchone()[0]
            == "committed"
        )
