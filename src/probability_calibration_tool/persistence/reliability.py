"""Read-only source inventory for reliability inspection; no repair or business policy."""

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceInventory:
    characters: tuple[dict, ...]
    regimes: tuple[dict, ...]
    rounds: tuple[dict, ...]
    snapshots: tuple[dict, ...]
    source_fk_violations: tuple[tuple, ...]


def read_source_inventory(connection: sqlite3.Connection) -> SourceInventory:
    def rows(table):
        return tuple(dict(row) for row in connection.execute(f"SELECT * FROM {table}"))

    return SourceInventory(
        rows("characters"),
        rows("history_regimes"),
        rows("rounds"),
        rows("round_analysis_snapshots"),
        tuple(
            tuple(row)
            for row in connection.execute("PRAGMA foreign_key_check")
            if row[0] != "character_stats"
        ),
    )
