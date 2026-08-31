import sqlite3

from probability_calibration_tool.domain.records import HistoryRegimeRecord
from probability_calibration_tool.persistence.database import (
    deserialize_utc,
    ensure_write_transaction,
    serialize_utc,
)


def _record(row: sqlite3.Row) -> HistoryRegimeRecord:
    return HistoryRegimeRecord(
        row["regime_id"],
        row["character_id"],
        row["regime_number"],
        deserialize_utc(row["started_at"]),
        None if row["ended_at"] is None else deserialize_utc(row["ended_at"]),
        bool(row["active"]),
        row["reason"],
    )


class HistoryRegimeRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get(self, regime_id: str) -> HistoryRegimeRecord | None:
        row = self._connection.execute(
            "SELECT * FROM history_regimes WHERE regime_id = ?", (regime_id,)
        ).fetchone()
        return None if row is None else _record(row)

    def list_all(self) -> list[HistoryRegimeRecord]:
        """Include inactive regimes for complete cache validation."""
        return [_record(row) for row in self._connection.execute("SELECT * FROM history_regimes")]

    def get_active(self, character_id: int) -> HistoryRegimeRecord | None:
        row = self._connection.execute(
            "SELECT * FROM history_regimes WHERE character_id = ? AND active = 1", (character_id,)
        ).fetchone()
        return None if row is None else _record(row)

    def insert(self, record: HistoryRegimeRecord) -> None:
        ensure_write_transaction(self._connection)
        self._connection.execute(
            "INSERT INTO history_regimes VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                record.regime_id,
                record.character_id,
                record.regime_number,
                serialize_utc(record.started_at),
                None if record.ended_at is None else serialize_utc(record.ended_at),
                int(record.active),
                record.reason,
            ),
        )

    def update(self, record: HistoryRegimeRecord) -> None:
        """Update data by regime identity without deciding switching permissions."""
        parameters = (
            record.character_id,
            record.regime_number,
            serialize_utc(record.started_at),
            None if record.ended_at is None else serialize_utc(record.ended_at),
            int(record.active),
            record.reason,
            record.regime_id,
        )
        ensure_write_transaction(self._connection)
        self._connection.execute(
            "UPDATE history_regimes SET character_id = ?, regime_number = ?, started_at = ?, "
            "ended_at = ?, active = ?, reason = ? WHERE regime_id = ?",
            parameters,
        )
