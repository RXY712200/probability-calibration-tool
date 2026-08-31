import sqlite3

import pytest

from .helpers import STAMP_TEXT, insert_row


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        pytest.param({"regime_number": 0}, "SQLITE_CONSTRAINT_CHECK", id="number-below-one"),
        pytest.param({"regime_number": 1}, "SQLITE_CONSTRAINT_UNIQUE", id="duplicate-number"),
        pytest.param(
            {"active": 1, "ended_at": None}, "SQLITE_CONSTRAINT_UNIQUE", id="second-active"
        ),
        pytest.param({"active": 1}, "SQLITE_CONSTRAINT_CHECK", id="active-has-end"),
        pytest.param({"ended_at": None}, "SQLITE_CONSTRAINT_CHECK", id="closed-missing-end"),
        pytest.param({"active": 2}, "SQLITE_CONSTRAINT_CHECK", id="invalid-active"),
        pytest.param({"character_id": 99}, "SQLITE_CONSTRAINT_FOREIGNKEY", id="missing-character"),
    ],
)
def test_regime_constraint(
    connection: sqlite3.Connection, changes: dict[str, object], error: str
) -> None:
    values = {
        "regime_id": "closed",
        "character_id": 1,
        "regime_number": 2,
        "started_at": STAMP_TEXT,
        "ended_at": STAMP_TEXT,
        "active": 0,
        "reason": "closed test regime",
    }
    values.update(changes)
    with pytest.raises(sqlite3.IntegrityError) as caught:
        insert_row(connection, "history_regimes", values)
    assert caught.value.sqlite_errorname == error


def test_valid_closed_and_active_regimes(connection: sqlite3.Connection) -> None:
    connection.execute(
        "UPDATE history_regimes SET active = 0, ended_at = ? WHERE regime_id = 'regime-1-1'",
        (STAMP_TEXT,),
    )
    insert_row(
        connection,
        "history_regimes",
        {
            "regime_id": "new-active",
            "character_id": 1,
            "regime_number": 2,
            "started_at": STAMP_TEXT,
            "ended_at": None,
            "active": 1,
            "reason": "new regime",
        },
    )
    rows = connection.execute(
        "SELECT active, ended_at FROM history_regimes WHERE character_id = 1 ORDER BY regime_number"
    ).fetchall()
    assert [tuple(row) for row in rows] == [(0, STAMP_TEXT), (1, None)]
