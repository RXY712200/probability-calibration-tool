import sqlite3

import pytest

from probability_calibration_tool.domain.enums import RoundStatus

from .helpers import insert_row, make_round, sql_values, update_row


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        pytest.param({"included_games": -1}, "SQLITE_CONSTRAINT_CHECK", id="negative-included"),
        pytest.param({"wins": -1}, "SQLITE_CONSTRAINT_CHECK", id="negative-wins"),
        pytest.param({"losses": -1}, "SQLITE_CONSTRAINT_CHECK", id="negative-losses"),
        pytest.param({"wins": 1}, "SQLITE_CONSTRAINT_CHECK", id="count-arithmetic"),
        pytest.param(
            {"last_included_round_id": "prior"}, "SQLITE_CONSTRAINT_CHECK", id="zero-with-last"
        ),
        pytest.param(
            {"included_games": 1, "wins": 1}, "SQLITE_CONSTRAINT_CHECK", id="positive-without-last"
        ),
        pytest.param({"stats_version": 0}, "SQLITE_CONSTRAINT_CHECK", id="invalid-version"),
        pytest.param(
            {"regime_id": "regime-1-2"}, "SQLITE_CONSTRAINT_FOREIGNKEY", id="mismatched-regime"
        ),
        pytest.param(
            {"included_games": 1, "wins": 1, "last_included_round_id": "missing"},
            "SQLITE_CONSTRAINT_FOREIGNKEY",
            id="nonexistent-last",
        ),
    ],
)
def test_stats_constraint_matrix(
    connection: sqlite3.Connection, changes: dict[str, object], error: str
) -> None:
    insert_row(connection, "rounds", sql_values(make_round("prior", RoundStatus.COMPLETED)))
    with pytest.raises(sqlite3.IntegrityError) as caught:
        update_row(
            connection,
            "character_stats",
            changes,
            "character_id = ? AND regime_id = ?",
            (1, "regime-1-1"),
        )
    assert caught.value.sqlite_errorname == error


@pytest.mark.parametrize("positive", [False, True])
def test_valid_zero_and_positive_stats(connection: sqlite3.Connection, positive: bool) -> None:
    insert_row(connection, "rounds", sql_values(make_round("prior", RoundStatus.COMPLETED)))
    count = int(positive)
    update_row(
        connection,
        "character_stats",
        {
            "included_games": count,
            "wins": count,
            "losses": 0,
            "last_included_round_id": "prior" if positive else None,
        },
        "character_id = ? AND regime_id = ?",
        (1, "regime-1-1"),
    )
    row = connection.execute(
        "SELECT included_games, wins, losses, last_included_round_id FROM character_stats WHERE character_id = 1"
    ).fetchone()
    assert tuple(row) == (count, count, 0, "prior" if positive else None)
