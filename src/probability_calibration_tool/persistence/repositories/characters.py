import sqlite3

from probability_calibration_tool.domain.records import CharacterRecord


class CharacterRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def list_all(self) -> list[CharacterRecord]:
        return [
            CharacterRecord(
                r["character_id"],
                r["internal_code"],
                r["display_name"],
                bool(r["tainted"]),
                r["pair_row"],
                bool(r["active"]),
            )
            for r in self._connection.execute("SELECT * FROM characters ORDER BY character_id")
        ]

    def get(self, character_id: int) -> CharacterRecord | None:
        row = self._connection.execute(
            "SELECT * FROM characters WHERE character_id = ?", (character_id,)
        ).fetchone()
        return (
            None
            if row is None
            else CharacterRecord(
                row["character_id"],
                row["internal_code"],
                row["display_name"],
                bool(row["tainted"]),
                row["pair_row"],
                bool(row["active"]),
            )
        )
