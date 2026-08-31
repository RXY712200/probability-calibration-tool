import sqlite3
from contextlib import closing
from dataclasses import fields, is_dataclass, replace
from datetime import UTC, datetime, timedelta, timezone
from enum import Enum
from pathlib import Path

import pytest

from probability_calibration_tool.domain.enums import HistoryModelStatus, RoundStatus
from probability_calibration_tool.domain.records import (
    CharacterRecord,
    CharacterStatsRecord,
    HistoryRegimeRecord,
    MetaRecord,
)
from probability_calibration_tool.persistence.database import (
    create_connection,
    deserialize_utc,
    serialize_utc,
)
from probability_calibration_tool.persistence.repositories import (
    CharacterRepository,
    CharacterStatsRepository,
    HistoryRegimeRepository,
    MetaRepository,
    RoundRepository,
    SnapshotRepository,
)
from probability_calibration_tool.persistence.unit_of_work import UnitOfWork

from .helpers import STAMP, STAMP_TEXT, insert_row, make_round, make_snapshot, sql_values


def assert_record_round_trip(actual: object, expected: object) -> None:
    assert type(actual) is type(expected)
    assert is_dataclass(actual)
    for field in fields(expected):
        value = getattr(actual, field.name)
        reference = getattr(expected, field.name)
        assert value == reference, field.name
        if isinstance(reference, Enum):
            assert type(value) is type(reference), field.name
        elif isinstance(reference, datetime):
            assert isinstance(value, datetime)
            assert value.tzinfo is UTC, field.name
        else:
            assert type(value) is type(reference), field.name


def test_character_repository_returns_typed_records(connection: sqlite3.Connection) -> None:
    repo = CharacterRepository(connection)
    records = repo.list_all()
    assert len(records) == 34
    assert [record.character_id for record in records] == list(range(1, 35))
    for record in records:
        assert isinstance(record, CharacterRecord)
        assert type(record.tainted) is bool
        assert type(record.active) is bool
        assert_record_round_trip(repo.get(record.character_id), record)
    assert_record_round_trip(repo.get(1), CharacterRecord(1, "isaac", "Isaac", False, 1, True))
    assert repo.get(99) is None


@pytest.mark.parametrize("active", [False, True])
def test_regime_repository_round_trip(connection: sqlite3.Connection, active: bool) -> None:
    if active:
        connection.execute(
            "UPDATE history_regimes SET active = 0, ended_at = ? WHERE regime_id = 'regime-1-1'",
            (STAMP_TEXT,),
        )
    record = HistoryRegimeRecord(
        "test-regime",
        1,
        2,
        STAMP,
        None if active else STAMP + timedelta(days=1),
        active,
        "原因 'quoted'" if active else None,
    )
    repo = HistoryRegimeRepository(connection)
    repo.insert(record)
    assert_record_round_trip(repo.get(record.regime_id), record)
    current = repo.get_active(1)
    assert isinstance(current, HistoryRegimeRecord)
    assert current.regime_id == ("test-regime" if active else "regime-1-1")
    assert repo.get("missing") is None
    assert repo.get_active(99) is None


@pytest.mark.parametrize("kind", ["pending", "completed", "voided-pending", "voided-completed"])
def test_round_repository_round_trip(connection: sqlite3.Connection, kind: str) -> None:
    repo = RoundRepository(connection)
    repo.insert(make_round("prior", RoundStatus.COMPLETED))
    status = {"pending": RoundStatus.PENDING, "completed": RoundStatus.COMPLETED}.get(
        kind, RoundStatus.VOIDED
    )
    record = make_round(
        status=status,
        reference_history=True,
        p_h_raw=99,
        win_odds_raw="0002.125",
        lose_odds_raw="3.500",
        win_odds=2.125,
        lose_odds=3.5,
        revision_count=3,
        history_exposed=True,
        history_exposed_at=STAMP,
        subjective_independence_compromised=True,
        supersedes_round_id="prior",
    )
    if kind == "voided-completed":
        record = replace(record, result=False, include_character_history=False, completed_at=STAMP)
    repo.insert(record)
    assert_record_round_trip(repo.get(record.round_id), record)
    assert repo.get("missing") is None


@pytest.mark.parametrize("status", list(HistoryModelStatus))
def test_snapshot_repository_every_field_round_trip(
    snapshot_connection: sqlite3.Connection, status: HistoryModelStatus
) -> None:
    record = make_snapshot(status)
    repo = SnapshotRepository(snapshot_connection)
    repo.insert(record)
    assert_record_round_trip(repo.get(record.round_id), record)
    assert repo.get("missing") is None


@pytest.mark.parametrize("before", list(HistoryModelStatus))
@pytest.mark.parametrize("after", list(HistoryModelStatus))
def test_snapshot_repository_update_round_trip(
    snapshot_connection: sqlite3.Connection, before: HistoryModelStatus, after: HistoryModelStatus
) -> None:
    repo = SnapshotRepository(snapshot_connection)
    repo.insert(make_snapshot(before))
    insert_row(
        snapshot_connection, "rounds", sql_values(make_round("unrelated", RoundStatus.COMPLETED))
    )
    other = make_snapshot(round_id="unrelated")
    repo.insert(other)
    updated = replace(
        make_snapshot(after),
        p_h_used=51,
        subjective_probability=0.51,
        subjective_win_margin_index=0.125,
        history_data_through_at=STAMP + timedelta(seconds=7),
    )
    repo.update(updated)
    assert_record_round_trip(repo.get("current"), updated)
    assert_record_round_trip(repo.get("unrelated"), other)
    assert (
        snapshot_connection.execute("SELECT COUNT(*) FROM round_analysis_snapshots").fetchone()[0]
        == 2
    )


def test_snapshot_update_constraint_failure_preserves_saved_row(
    snapshot_connection: sqlite3.Connection,
) -> None:
    repo = SnapshotRepository(snapshot_connection)
    original = make_snapshot()
    repo.insert(original)
    with pytest.raises(sqlite3.IntegrityError):
        repo.update(replace(original, p_h_used=0))
    assert_record_round_trip(repo.get("current"), original)


def test_stats_repository_returns_typed_zero_record(connection: sqlite3.Connection) -> None:
    repo = CharacterStatsRepository(connection)
    record = repo.get(1, "regime-1-1")
    assert isinstance(record, CharacterStatsRecord)
    assert (
        record.included_games,
        record.wins,
        record.losses,
        record.last_included_round_id,
        record.stats_version,
    ) == (0, 0, 0, None, 1)
    assert record.updated_at.tzinfo is UTC
    rebuilt = repo.rebuild_stats(1, "regime-1-1")
    assert_record_round_trip(repo.get(1, "regime-1-1"), rebuilt)
    assert repo.get(99, "missing") is None


def test_meta_repository_insert_and_update(connection: sqlite3.Connection) -> None:
    repo = MetaRepository(connection)
    assert repo.get("missing") is None
    repo.set("test'key", "中文 'value' 3.5")
    first = repo.get("test'key")
    assert isinstance(first, MetaRecord)
    assert (first.key, first.value) == ("test'key", "中文 'value' 3.5")
    assert first.updated_at.tzinfo is UTC
    repo.set("test'key", "replacement")
    updated = repo.get("test'key")
    assert isinstance(updated, MetaRecord)
    assert updated.value == "replacement"
    assert (
        connection.execute("SELECT COUNT(*) FROM meta WHERE key = ?", ("test'key",)).fetchone()[0]
        == 1
    )


def test_utc_canonical_serialization_and_offset_round_trip(connection: sqlite3.Connection) -> None:
    offset_time = STAMP.astimezone(timezone(timedelta(hours=8)))
    assert serialize_utc(offset_time) == STAMP_TEXT
    assert deserialize_utc(STAMP_TEXT) == STAMP
    assert deserialize_utc(STAMP_TEXT).tzinfo is UTC
    record = make_round(
        created_at=offset_time, calculated_at=offset_time, last_updated_at=offset_time
    )
    repo = RoundRepository(connection)
    repo.insert(record)
    assert_record_round_trip(repo.get(record.round_id), record)
    assert connection.execute("SELECT created_at FROM rounds").fetchone()[0] == STAMP_TEXT


def test_naive_timestamp_is_rejected_by_serialization_and_repository(
    connection: sqlite3.Connection,
) -> None:
    naive = datetime.fromisoformat("2026-08-30T11:23:45")
    with pytest.raises(ValueError):
        serialize_utc(naive)
    with pytest.raises(ValueError):
        deserialize_utc("2026-08-30T11:23:45")
    with pytest.raises(ValueError):
        RoundRepository(connection).insert(make_round(created_at=naive))
    assert connection.execute("SELECT COUNT(*) FROM rounds").fetchone()[0] == 0


@pytest.mark.parametrize(
    "operation", ["round", "snapshot-insert", "snapshot-update", "regime", "stats", "meta"]
)
def test_repositories_do_not_commit_independently(db_path: Path, operation: str) -> None:
    with closing(create_connection(db_path)) as setup:
        insert_row(setup, "rounds", sql_values(make_round("prior", RoundStatus.COMPLETED)))
        if operation.startswith("snapshot"):
            insert_row(setup, "rounds", sql_values(make_round()))
        if operation == "snapshot-update":
            SnapshotRepository(setup).insert(make_snapshot())
            setup.commit()
    queries = {
        "round": ("SELECT COUNT(*) FROM rounds WHERE round_id = 'current'", 0, 1),
        "snapshot-insert": ("SELECT COUNT(*) FROM round_analysis_snapshots", 0, 1),
        "snapshot-update": (
            "SELECT p_h_used FROM round_analysis_snapshots WHERE round_id = 'current'",
            50,
            51,
        ),
        "regime": ("SELECT COUNT(*) FROM history_regimes WHERE regime_id = 'extra'", 0, 1),
        "stats": ("SELECT included_games FROM character_stats WHERE character_id = 1", 0, 1),
        "meta": ("SELECT COUNT(*) FROM meta WHERE key = 'transaction-test'", 0, 1),
    }
    query, before, after = queries[operation]
    with closing(create_connection(db_path)) as observer, UnitOfWork(db_path) as uow:
        if operation == "round":
            uow.rounds.insert(make_round())
        elif operation == "snapshot-insert":
            uow.snapshots.insert(make_snapshot())
        elif operation == "snapshot-update":
            uow.snapshots.update(replace(make_snapshot(), p_h_used=51))
        elif operation == "regime":
            uow.regimes.insert(HistoryRegimeRecord("extra", 1, 2, STAMP, STAMP, False, None))
        elif operation == "stats":
            uow.stats.rebuild_stats(1, "regime-1-1")
        else:
            uow.meta.set("transaction-test", "inserted")
        assert observer.execute(query).fetchone()[0] == before
        uow.commit()
        assert observer.execute(query).fetchone()[0] == after
