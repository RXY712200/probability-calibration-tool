import sqlite3
from datetime import UTC, datetime

from probability_calibration_tool.core.model_specs import STATS_VERSION
from probability_calibration_tool.domain.records import CharacterStatsRecord
from probability_calibration_tool.persistence.database import (
    deserialize_utc,
    ensure_write_transaction,
    serialize_utc,
)


class CharacterStatsRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def insert(self, record: CharacterStatsRecord) -> None:
        """Insert a cache record into the caller's uncommitted transaction."""
        parameters = (
            record.character_id,
            record.regime_id,
            record.included_games,
            record.wins,
            record.losses,
            record.last_included_round_id,
            serialize_utc(record.updated_at),
            record.stats_version,
        )
        ensure_write_transaction(self._connection)
        self._connection.execute(
            "INSERT INTO character_stats (character_id, regime_id, included_games, wins, losses, "
            "last_included_round_id, updated_at, stats_version) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            parameters,
        )

    def get(self, character_id: int, regime_id: str) -> CharacterStatsRecord | None:
        row = self._connection.execute(
            "SELECT * FROM character_stats WHERE character_id = ? AND regime_id = ?",
            (character_id, regime_id),
        ).fetchone()
        return (
            None
            if row is None
            else CharacterStatsRecord(
                row["character_id"],
                row["regime_id"],
                row["included_games"],
                row["wins"],
                row["losses"],
                row["last_included_round_id"],
                deserialize_utc(row["updated_at"]),
                row["stats_version"],
            )
        )

    def rebuild_stats(self, character_id: int, regime_id: str) -> CharacterStatsRecord:
        ensure_write_transaction(self._connection)
        row = self._connection.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM(result), 0) AS wins FROM rounds WHERE character_id = ? AND history_regime_id = ? AND status = 'completed' AND include_character_history = 1",
            (character_id, regime_id),
        ).fetchone()
        last = self._connection.execute(
            "SELECT round_id FROM rounds WHERE character_id = ? AND history_regime_id = ? AND status = 'completed' AND include_character_history = 1 ORDER BY calculated_at DESC, round_id DESC LIMIT 1",
            (character_id, regime_id),
        ).fetchone()
        now = serialize_utc(datetime.now(UTC))
        n = int(row["n"])
        wins = int(row["wins"])
        self._connection.execute(
            "UPDATE character_stats SET included_games = ?, wins = ?, losses = ?, last_included_round_id = ?, updated_at = ?, stats_version = ? WHERE character_id = ? AND regime_id = ?",
            (
                n,
                wins,
                n - wins,
                None if last is None else last["round_id"],
                now,
                STATS_VERSION,
                character_id,
                regime_id,
            ),
        )
        result = self.get(character_id, regime_id)
        assert result is not None
        return result
