import sqlite3

from probability_calibration_tool.domain.enums import RoundStatus
from probability_calibration_tool.domain.records import RoundRecord
from probability_calibration_tool.persistence.database import (
    deserialize_utc,
    ensure_write_transaction,
    serialize_utc,
)


def _record(row: sqlite3.Row) -> RoundRecord:
    values = dict(row)
    for key in (
        "created_at",
        "calculated_at",
        "last_updated_at",
        "completed_at",
        "voided_at",
        "history_exposed_at",
    ):
        if values[key] is not None:
            values[key] = deserialize_utc(values[key])
    for key in (
        "reference_history",
        "result",
        "include_character_history",
        "history_exposed",
        "subjective_independence_compromised",
    ):
        if values[key] is not None:
            values[key] = bool(values[key])
    values["status"] = RoundStatus(values["status"])
    return RoundRecord(**values)


def _values(record: RoundRecord) -> dict[str, object]:
    values = record.__dict__.copy()
    for key in (
        "created_at",
        "calculated_at",
        "last_updated_at",
        "completed_at",
        "voided_at",
        "history_exposed_at",
    ):
        if values[key] is not None:
            values[key] = serialize_utc(values[key])
    for key in (
        "reference_history",
        "result",
        "include_character_history",
        "history_exposed",
        "subjective_independence_compromised",
    ):
        if values[key] is not None:
            values[key] = int(values[key])
    values["status"] = values["status"].value
    return values


class RoundRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def insert(self, record: RoundRecord) -> None:
        values = _values(record)
        columns = ", ".join(values)
        ensure_write_transaction(self._connection)
        self._connection.execute(
            f"INSERT INTO rounds ({columns}) VALUES ({', '.join('?' for _ in values)})",
            tuple(values.values()),
        )

    def update(self, record: RoundRecord) -> None:
        """Update the identified row; transition permission belongs to Application."""
        values = _values(record)
        round_id = values.pop("round_id")
        assignments = ", ".join(f"{column} = ?" for column in values)
        ensure_write_transaction(self._connection)
        self._connection.execute(
            f"UPDATE rounds SET {assignments} WHERE round_id = ?",
            (*values.values(), round_id),
        )

    def get(self, round_id: str) -> RoundRecord | None:
        row = self._connection.execute(
            "SELECT * FROM rounds WHERE round_id = ?", (round_id,)
        ).fetchone()
        return None if row is None else _record(row)

    def list_pending(self) -> list[RoundRecord]:
        """Read every pending row; Application decides how to handle cardinality."""
        rows = self._connection.execute("SELECT * FROM rounds WHERE status = 'pending'")
        return [_record(row) for row in rows]

    def correction_identifiers(self) -> tuple[tuple[str, str, str], ...]:
        """Eager, non-directional audit metadata only; never load prediction/results."""
        rows = self._connection.execute(
            "SELECT r.round_id, c.display_name, r.completed_at "
            "FROM rounds r JOIN characters c ON c.character_id = r.character_id "
            "WHERE r.status = 'completed' ORDER BY r.completed_at DESC, r.round_id"
        ).fetchall()
        return tuple(tuple(row) for row in rows)

    def eligible_history(self, character_id: int, regime_id: str) -> list[RoundRecord]:
        rows = self._connection.execute(
            "SELECT * FROM rounds WHERE character_id = ? AND history_regime_id = ? AND status = 'completed' AND include_character_history = 1 ORDER BY calculated_at, round_id",
            (character_id, regime_id),
        )
        return [_record(row) for row in rows]
