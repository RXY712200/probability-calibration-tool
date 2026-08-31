import sqlite3
from datetime import UTC, datetime

from probability_calibration_tool.domain.records import MetaRecord
from probability_calibration_tool.persistence.database import (
    deserialize_utc,
    ensure_write_transaction,
    serialize_utc,
)


class MetaRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get(self, key: str) -> MetaRecord | None:
        row = self._connection.execute("SELECT * FROM meta WHERE key = ?", (key,)).fetchone()
        return (
            None
            if row is None
            else MetaRecord(row["key"], row["value"], deserialize_utc(row["updated_at"]))
        )

    def set(self, key: str, value: str) -> None:
        ensure_write_transaction(self._connection)
        self._connection.execute(
            "INSERT INTO meta(key, value, updated_at) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
            (key, value, serialize_utc(datetime.now(UTC))),
        )
