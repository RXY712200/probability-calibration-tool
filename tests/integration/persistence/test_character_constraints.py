import sqlite3

import pytest

from .helpers import update_row


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        pytest.param({"character_id": 0}, "SQLITE_CONSTRAINT_CHECK", id="id-below-one"),
        pytest.param({"character_id": 35}, "SQLITE_CONSTRAINT_CHECK", id="id-above-34"),
        pytest.param(
            {"internal_code": "magdalene"}, "SQLITE_CONSTRAINT_UNIQUE", id="duplicate-code"
        ),
        pytest.param({"pair_row": 2}, "SQLITE_CONSTRAINT_UNIQUE", id="duplicate-pair-slot"),
        pytest.param({"pair_row": 0}, "SQLITE_CONSTRAINT_CHECK", id="row-below-one"),
        pytest.param({"pair_row": 18}, "SQLITE_CONSTRAINT_CHECK", id="row-above-17"),
        pytest.param({"tainted": 2}, "SQLITE_CONSTRAINT_CHECK", id="invalid-tainted"),
        pytest.param({"active": -1}, "SQLITE_CONSTRAINT_CHECK", id="invalid-active"),
    ],
)
def test_character_constraint(
    connection: sqlite3.Connection, changes: dict[str, object], error: str
) -> None:
    before = tuple(connection.execute("SELECT * FROM characters WHERE character_id = 1").fetchone())
    with pytest.raises(sqlite3.IntegrityError) as caught:
        update_row(connection, "characters", changes, "character_id = ?", (1,))
    assert caught.value.sqlite_errorname == error
    assert (
        tuple(connection.execute("SELECT * FROM characters WHERE character_id = 1").fetchone())
        == before
    )
