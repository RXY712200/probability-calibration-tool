import sqlite3

import pytest

from probability_calibration_tool.domain.enums import RoundStatus

from .helpers import STAMP_TEXT, insert_row, make_round, sql_values


@pytest.mark.parametrize(
    ("status", "field", "value"),
    [
        (RoundStatus.PENDING, "p_h_raw", -1),
        (RoundStatus.PENDING, "p_h_raw", 101),
        (RoundStatus.PENDING, "reference_history", 2),
        (RoundStatus.PENDING, "history_exposed", 2),
        (RoundStatus.PENDING, "subjective_independence_compromised", 2),
        (RoundStatus.PENDING, "status", "unknown"),
        (RoundStatus.PENDING, "win_odds", 0.99),
        (RoundStatus.PENDING, "lose_odds", 0.99),
        (RoundStatus.PENDING, "win_odds", float("inf")),
        (RoundStatus.PENDING, "lose_odds", float("inf")),
        (RoundStatus.PENDING, "revision_count", -1),
        (RoundStatus.PENDING, "result", 1),
        (RoundStatus.PENDING, "include_character_history", 1),
        (RoundStatus.PENDING, "completed_at", STAMP_TEXT),
        (RoundStatus.PENDING, "voided_at", STAMP_TEXT),
        (RoundStatus.PENDING, "void_reason", "illegal"),
        (RoundStatus.COMPLETED, "result", None),
        (RoundStatus.COMPLETED, "result", 2),
        (RoundStatus.COMPLETED, "include_character_history", None),
        (RoundStatus.COMPLETED, "include_character_history", 2),
        (RoundStatus.COMPLETED, "completed_at", None),
        (RoundStatus.COMPLETED, "voided_at", STAMP_TEXT),
        (RoundStatus.COMPLETED, "void_reason", "illegal"),
        (RoundStatus.PENDING, "history_exposed_at", STAMP_TEXT),
        (RoundStatus.PENDING, "history_exposed", 1),
        (RoundStatus.PENDING, "supersedes_round_id", "current"),
        (RoundStatus.VOIDED, "voided_at", None),
    ],
)
def test_round_check_matrix(
    connection: sqlite3.Connection, status: RoundStatus, field: str, value: object
) -> None:
    values = sql_values(make_round(status=status))
    values[field] = value
    with pytest.raises(sqlite3.IntegrityError) as caught:
        insert_row(connection, "rounds", values)
    assert caught.value.sqlite_errorname == "SQLITE_CONSTRAINT_CHECK"
    assert connection.execute("SELECT COUNT(*) FROM rounds").fetchone()[0] == 0


@pytest.mark.parametrize("kind", ["pending", "completed", "voided-pending", "voided-completed"])
def test_legal_round_states(connection: sqlite3.Connection, kind: str) -> None:
    status = {"pending": RoundStatus.PENDING, "completed": RoundStatus.COMPLETED}.get(
        kind, RoundStatus.VOIDED
    )
    values = sql_values(make_round(status=status))
    if kind == "voided-completed":
        values.update(result=1, include_character_history=0, completed_at=STAMP_TEXT)
    insert_row(connection, "rounds", values)
    assert dict(connection.execute("SELECT * FROM rounds").fetchone()) == values


@pytest.mark.parametrize(
    "field,value",
    [("history_regime_id", "regime-1-2"), ("character_id", 99), ("supersedes_round_id", "missing")],
)
def test_round_foreign_keys(connection: sqlite3.Connection, field: str, value: object) -> None:
    values = sql_values(make_round())
    values[field] = value
    with pytest.raises(sqlite3.IntegrityError) as caught:
        insert_row(connection, "rounds", values)
    assert caught.value.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY"


def test_second_pending_is_globally_rejected(connection: sqlite3.Connection) -> None:
    insert_row(connection, "rounds", sql_values(make_round("first")))
    with pytest.raises(sqlite3.IntegrityError) as caught:
        insert_row(
            connection,
            "rounds",
            sql_values(make_round("second", character_id=2, history_regime_id="regime-1-2")),
        )
    assert caught.value.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE"
    assert connection.execute("SELECT COUNT(*) FROM rounds").fetchone()[0] == 1


def test_supersede_branch_rejected_but_chain_allowed(connection: sqlite3.Connection) -> None:
    insert_row(connection, "rounds", sql_values(make_round("A", RoundStatus.COMPLETED)))
    insert_row(
        connection,
        "rounds",
        sql_values(make_round("B", RoundStatus.COMPLETED, supersedes_round_id="A")),
    )
    with pytest.raises(sqlite3.IntegrityError) as caught:
        insert_row(
            connection,
            "rounds",
            sql_values(make_round("branch", RoundStatus.COMPLETED, supersedes_round_id="A")),
        )
    assert caught.value.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE"
    insert_row(
        connection,
        "rounds",
        sql_values(make_round("C", RoundStatus.COMPLETED, supersedes_round_id="B")),
    )
    assert [
        tuple(row)
        for row in connection.execute(
            "SELECT round_id, supersedes_round_id FROM rounds ORDER BY round_id"
        )
    ] == [("A", None), ("B", "A"), ("C", "B")]


def test_duplicate_round_identity_is_rejected(connection: sqlite3.Connection) -> None:
    values = sql_values(make_round("same", RoundStatus.COMPLETED))
    insert_row(connection, "rounds", values)
    with pytest.raises(sqlite3.IntegrityError):
        insert_row(connection, "rounds", values)


@pytest.mark.parametrize(
    ("result", "include", "completed_at"),
    [
        (1, None, None),
        (None, 1, None),
        (None, None, STAMP_TEXT),
        (1, 1, None),
        (1, None, STAMP_TEXT),
        (None, 1, STAMP_TEXT),
    ],
)
def test_voided_hybrid_post_run_fields_rejected(
    connection: sqlite3.Connection,
    result: int | None,
    include: int | None,
    completed_at: str | None,
) -> None:
    values = sql_values(make_round(status=RoundStatus.VOIDED))
    values.update(result=result, include_character_history=include, completed_at=completed_at)
    with pytest.raises(sqlite3.IntegrityError) as caught:
        insert_row(connection, "rounds", values)
    assert caught.value.sqlite_errorname == "SQLITE_CONSTRAINT_CHECK"
    assert connection.execute("SELECT COUNT(*) FROM rounds").fetchone()[0] == 0


@pytest.mark.parametrize("completed_derived", [False, True])
@pytest.mark.parametrize("reason", [None, "explicit reason"])
def test_voided_all_null_or_all_present_remain_valid(
    connection: sqlite3.Connection, completed_derived: bool, reason: str | None
) -> None:
    values = sql_values(make_round(status=RoundStatus.VOIDED, void_reason=reason))
    if completed_derived:
        values.update(result=0, include_character_history=0, completed_at=STAMP_TEXT)
    insert_row(connection, "rounds", values)
    assert dict(connection.execute("SELECT * FROM rounds").fetchone()) == values
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
