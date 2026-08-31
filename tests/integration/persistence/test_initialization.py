import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from probability_calibration_tool.domain.enums import RoundStatus
from probability_calibration_tool.persistence import schema
from probability_calibration_tool.persistence.database import create_connection
from probability_calibration_tool.persistence.errors import UnsupportedNewerSchemaError
from probability_calibration_tool.persistence.migrations import ensure_schema

from .helpers import STAMP_TEXT, insert_row, make_round, sql_values

# Independent frozen expected identities. Do not import production seed constants here.
EXPECTED_SEEDS = [
    (1, "isaac", "Isaac", 0, 1),
    (2, "magdalene", "Magdalene", 0, 2),
    (3, "cain", "Cain", 0, 3),
    (4, "judas", "Judas", 0, 4),
    (5, "blue_baby", "???", 0, 5),
    (6, "eve", "Eve", 0, 6),
    (7, "samson", "Samson", 0, 7),
    (8, "azazel", "Azazel", 0, 8),
    (9, "lazarus", "Lazarus", 0, 9),
    (10, "eden", "Eden", 0, 10),
    (11, "the_lost", "The Lost", 0, 11),
    (12, "lilith", "Lilith", 0, 12),
    (13, "keeper", "Keeper", 0, 13),
    (14, "apollyon", "Apollyon", 0, 14),
    (15, "the_forgotten", "The Forgotten", 0, 15),
    (16, "bethany", "Bethany", 0, 16),
    (17, "jacob_and_esau", "Jacob & Esau", 0, 17),
    (18, "tainted_isaac", "Tainted Isaac", 1, 1),
    (19, "tainted_magdalene", "Tainted Magdalene", 1, 2),
    (20, "tainted_cain", "Tainted Cain", 1, 3),
    (21, "tainted_judas", "Tainted Judas", 1, 4),
    (22, "tainted_blue_baby", "Tainted ???", 1, 5),
    (23, "tainted_eve", "Tainted Eve", 1, 6),
    (24, "tainted_samson", "Tainted Samson", 1, 7),
    (25, "tainted_azazel", "Tainted Azazel", 1, 8),
    (26, "tainted_lazarus", "Tainted Lazarus", 1, 9),
    (27, "tainted_eden", "Tainted Eden", 1, 10),
    (28, "tainted_lost", "Tainted Lost", 1, 11),
    (29, "tainted_lilith", "Tainted Lilith", 1, 12),
    (30, "tainted_keeper", "Tainted Keeper", 1, 13),
    (31, "tainted_apollyon", "Tainted Apollyon", 1, 14),
    (32, "tainted_forgotten", "Tainted Forgotten", 1, 15),
    (33, "tainted_bethany", "Tainted Bethany", 1, 16),
    (34, "tainted_jacob", "Tainted Jacob", 1, 17),
]
TABLES = (
    "characters",
    "history_regimes",
    "rounds",
    "round_analysis_snapshots",
    "character_stats",
    "meta",
)


def test_exact_34_seed_identities_and_initial_regime_stats(connection: sqlite3.Connection) -> None:
    actual = connection.execute(
        "SELECT character_id, internal_code, display_name, tainted, pair_row FROM characters ORDER BY character_id"
    ).fetchall()
    assert [tuple(row) for row in actual] == EXPECTED_SEEDS
    assert (
        connection.execute("SELECT COUNT(*) FROM characters WHERE active = 1").fetchone()[0] == 34
    )
    regimes = connection.execute(
        "SELECT character_id, regime_number, active, ended_at FROM history_regimes ORDER BY character_id"
    ).fetchall()
    assert [tuple(row) for row in regimes] == [(number, 1, 1, None) for number in range(1, 35)]
    stats = connection.execute(
        "SELECT character_id, included_games, wins, losses, last_included_round_id, stats_version FROM character_stats ORDER BY character_id"
    ).fetchall()
    assert [tuple(row) for row in stats] == [(number, 0, 0, 0, None, 1) for number in range(1, 35)]
    assert (
        connection.execute(
            "SELECT COUNT(*) FROM character_stats s JOIN history_regimes r ON s.character_id = r.character_id AND s.regime_id = r.regime_id"
        ).fetchone()[0]
        == 34
    )
    assert (
        connection.execute("SELECT value FROM meta WHERE key = 'schema_initialized'").fetchone()[0]
        == "1"
    )


def test_exact_six_tables_and_required_indexes(connection: sqlite3.Connection) -> None:
    assert {
        row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    } == set(TABLES)
    indexes = {
        row[0]: row[1]
        for row in connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE type = 'index' AND sql IS NOT NULL"
        )
    }
    expected = {
        "ux_history_regimes_active",
        "ux_rounds_pending",
        "ux_rounds_supersedes",
        "ix_rounds_calculated_at",
        "ix_rounds_eligible_history",
    }
    assert expected <= indexes.keys()
    for name in ("ux_history_regimes_active", "ux_rounds_pending", "ux_rounds_supersedes"):
        assert "CREATE UNIQUE INDEX" in indexes[name]
        assert "WHERE" in indexes[name]
    assert "character_id, history_regime_id, calculated_at" in indexes["ix_rounds_eligible_history"]
    unique_keys = []
    for index in connection.execute("PRAGMA index_list(characters)"):
        if index["unique"]:
            unique_keys.append(
                tuple(
                    row["name"]
                    for row in connection.execute(f"PRAGMA index_info('{index['name']}')")
                )
            )
    assert ("pair_row", "tainted") in unique_keys
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
    assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


def test_every_factory_connection_has_required_pragmas(db_path: Path) -> None:
    for _ in range(3):
        with closing(create_connection(db_path)) as connection:
            assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
            assert connection.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
            assert connection.execute("PRAGMA synchronous").fetchone()[0] == 3


def test_reopen_preserves_all_existing_rows_and_does_not_reseed(db_path: Path) -> None:
    with closing(create_connection(db_path)) as connection:
        insert_row(connection, "rounds", sql_values(make_round("saved", RoundStatus.COMPLETED)))
        connection.execute(
            "INSERT INTO meta VALUES ('sentinel', 'do not overwrite', ?)", (STAMP_TEXT,)
        )
        before = {
            table: [
                tuple(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY 1, 2")
            ]
            for table in TABLES
        }
    for _ in range(2):
        with closing(create_connection(db_path)) as connection:
            ensure_schema(connection)
            after = {
                table: [
                    tuple(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY 1, 2")
                ]
                for table in TABLES
            }
            assert after == before
            assert connection.execute("PRAGMA user_version").fetchone()[0] == 1


@pytest.mark.parametrize("failure_point", ["during-seed", "after-all-seeds"])
def test_initialization_failure_rolls_back_schema_seed_and_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure_point: str
) -> None:
    path = tmp_path / "fault.db"
    with closing(create_connection(path)) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 0
        if failure_point == "during-seed":
            with monkeypatch.context() as patcher:
                patcher.setattr(schema, "CHARACTERS", schema.CHARACTERS[:2] + schema.CHARACTERS[:1])
                with pytest.raises(sqlite3.IntegrityError):
                    ensure_schema(connection)
        else:

            def fail_after_seed() -> None:
                assert connection.execute("SELECT COUNT(*) FROM characters").fetchone()[0] == 34
                assert (
                    connection.execute("SELECT COUNT(*) FROM character_stats").fetchone()[0] == 34
                )
                raise RuntimeError("injected initialization failure")

            with pytest.raises(RuntimeError, match="injected"):
                schema.initialize_v1(connection, fail_after_seed)
        assert not connection.in_transaction
    with closing(create_connection(path)) as reopened:
        assert reopened.execute("PRAGMA user_version").fetchone()[0] == 0
        assert (
            reopened.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'index')"
            ).fetchall()
            == []
        )
        ensure_schema(reopened)
        assert reopened.execute("PRAGMA user_version").fetchone()[0] == 1
        assert reopened.execute("SELECT COUNT(*) FROM characters").fetchone()[0] == 34


def test_newer_schema_rejection_preserves_file_and_user_data(tmp_path: Path) -> None:
    path = tmp_path / "future.db"
    with closing(create_connection(path)) as connection:
        connection.execute(
            "CREATE TABLE future_payload (id INTEGER PRIMARY KEY, content TEXT, payload BLOB)"
        )
        connection.execute(
            "INSERT INTO future_payload VALUES (1, ?, ?)", ("不可改写 'future'", b"\x00\x01\xff")
        )
        connection.execute("PRAGMA user_version = 999")
    before = path.read_bytes()
    with closing(create_connection(path)) as connection:
        with pytest.raises(UnsupportedNewerSchemaError):
            ensure_schema(connection)
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 999
        assert tuple(connection.execute("SELECT * FROM future_payload").fetchone()) == (
            1,
            "不可改写 'future'",
            b"\x00\x01\xff",
        )
        assert [
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        ] == ["future_payload"]
    assert path.read_bytes() == before
