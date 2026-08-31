import sqlite3
from datetime import UTC, datetime

import pytest

from probability_calibration_tool.domain.enums import RoundStatus
from probability_calibration_tool.domain.records import RoundRecord
from probability_calibration_tool.persistence.database import (
    create_connection,
    deserialize_utc,
    serialize_utc,
)
from probability_calibration_tool.persistence.errors import UnsupportedNewerSchemaError
from probability_calibration_tool.persistence.migrations import ensure_schema
from probability_calibration_tool.persistence.schema import SCHEMA_VERSION, initialize_v1
from probability_calibration_tool.persistence.seed import CHARACTERS
from probability_calibration_tool.persistence.unit_of_work import create_uow_factory


def initialized_database(tmp_path: object) -> object:
    path = tmp_path / "test.db"
    connection = create_connection(path)
    ensure_schema(connection)
    connection.close()
    return path


def pending(round_id: str, character_id: int = 1, regime_id: str = "regime-1-1") -> RoundRecord:
    now = datetime.now(UTC)
    return RoundRecord(
        round_id,
        now,
        now,
        now,
        None,
        None,
        None,
        character_id,
        regime_id,
        False,
        50,
        "2",
        "2",
        2.0,
        2.0,
        RoundStatus.PENDING,
        0,
        None,
        None,
        False,
        None,
        False,
        None,
    )


def test_connection_pragmas_and_exact_seed(tmp_path: object) -> None:
    path = initialized_database(tmp_path)
    connection = create_connection(path)
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert connection.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
    assert connection.execute("PRAGMA synchronous").fetchone()[0] == 3
    assert connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    rows = connection.execute(
        "SELECT character_id, internal_code, display_name, tainted, pair_row FROM characters ORDER BY character_id"
    ).fetchall()
    assert [tuple(row) for row in rows] == sorted(CHARACTERS)
    assert (
        connection.execute(
            "SELECT COUNT(*) FROM history_regimes WHERE active = 1 AND regime_number = 1"
        ).fetchone()[0]
        == 34
    )
    assert (
        connection.execute(
            "SELECT COUNT(*) FROM character_stats WHERE included_games = 0"
        ).fetchone()[0]
        == 34
    )
    assert {
        r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    } == {
        "characters",
        "history_regimes",
        "rounds",
        "round_analysis_snapshots",
        "character_stats",
        "meta",
    }


def test_timestamp_round_trip_rejects_naive() -> None:
    value = datetime(2026, 8, 30, 11, 23, 45, 123456, tzinfo=UTC)
    assert deserialize_utc(serialize_utc(value)) == value
    with pytest.raises(ValueError):
        serialize_utc(datetime.fromisoformat("2026-08-30T00:00:00"))


def test_initialization_rollback_fault(tmp_path: object) -> None:
    path = tmp_path / "fault.db"
    connection = create_connection(path)
    with pytest.raises(RuntimeError):
        initialize_v1(connection, lambda: (_ for _ in ()).throw(RuntimeError("fault")))
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 0
    assert (
        connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table'").fetchone()[0]
        == 0
    )


def test_newer_schema_is_rejected_without_writes(tmp_path: object) -> None:
    path = tmp_path / "newer.db"
    connection = create_connection(path)
    connection.execute("PRAGMA user_version = 999")
    with pytest.raises(UnsupportedNewerSchemaError):
        ensure_schema(connection)
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 999


def test_round_constraints_and_pending_uniqueness(tmp_path: object) -> None:
    path = initialized_database(tmp_path)
    factory = create_uow_factory(path)
    with factory() as uow:
        uow.rounds.insert(pending("a"))
        uow.commit()
    with factory() as uow, pytest.raises(sqlite3.IntegrityError):
        uow.rounds.insert(pending("b"))
    connection = create_connection(path)
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO rounds(round_id, created_at, calculated_at, last_updated_at, character_id, history_regime_id, reference_history, p_h_raw, win_odds_raw, lose_odds_raw, win_odds, lose_odds, status) VALUES ('bad', 'x', 'x', 'x', 1, 'regime-1-1', 0, 101, '2', '2', 2, 2, 'voided')"
        )


def test_composite_fk_and_repository_does_not_commit(tmp_path: object) -> None:
    path = initialized_database(tmp_path)
    factory = create_uow_factory(path)
    with factory() as uow, pytest.raises(sqlite3.IntegrityError):
        uow.rounds.insert(pending("wrong", 1, "regime-1-2"))
    with factory() as uow:
        uow.rounds.insert(pending("hidden"))
        other = create_connection(path)
        assert (
            other.execute("SELECT COUNT(*) FROM rounds WHERE round_id = 'hidden'").fetchone()[0]
            == 0
        )
        other.close()
        uow.commit()
    assert (
        create_connection(path)
        .execute("SELECT COUNT(*) FROM rounds WHERE round_id = 'hidden'")
        .fetchone()[0]
        == 1
    )


def test_uow_rolls_back_and_eligible_history_and_stats_rebuild(tmp_path: object) -> None:
    path = initialized_database(tmp_path)
    factory = create_uow_factory(path)
    with factory() as uow:
        uow.rounds.insert(pending("rollback"))
    assert create_connection(path).execute("SELECT COUNT(*) FROM rounds").fetchone()[0] == 0
    now = datetime.now(UTC)
    with factory() as uow:
        for number in range(20):
            record = RoundRecord(
                f"r{number}",
                now,
                now,
                now,
                now,
                None,
                None,
                1,
                "regime-1-1",
                False,
                50,
                "2",
                "2",
                2.0,
                2.0,
                RoundStatus.COMPLETED,
                0,
                number < 16,
                True,
                False,
                None,
                False,
                None,
            )
            uow.rounds.insert(record)
        uow.rounds.insert(
            RoundRecord(
                "excluded",
                now,
                now,
                now,
                now,
                None,
                None,
                1,
                "regime-1-1",
                False,
                50,
                "2",
                "2",
                2.0,
                2.0,
                RoundStatus.COMPLETED,
                0,
                True,
                False,
                False,
                None,
                False,
                None,
            )
        )
        assert len(uow.rounds.eligible_history(1, "regime-1-1")) == 20
        stats = uow.stats.rebuild_stats(1, "regime-1-1")
        assert (stats.included_games, stats.wins, stats.losses, stats.stats_version) == (
            20,
            16,
            4,
            1,
        )
        uow.commit()
