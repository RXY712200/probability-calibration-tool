"""Inspection connections do not configure journal_mode or initialize existing files."""

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

CORE_TABLES = frozenset(
    {
        "characters",
        "history_regimes",
        "rounds",
        "round_analysis_snapshots",
        "character_stats",
        "meta",
    }
)


class DatabaseHealthError(RuntimeError):
    pass


@dataclass(frozen=True)
class DatabaseMetadata:
    version: int
    tables: frozenset[str]


def open_existing(path: Path, *, readonly: bool = False) -> sqlite3.Connection:
    # mode=rw prevents accidental creation while permitting native hot-journal recovery.
    connection = sqlite3.connect(
        path.resolve().as_uri() + ("?mode=ro" if readonly else "?mode=rw"),
        uri=True,
        isolation_level=None,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def integrity_check(connection: sqlite3.Connection) -> None:
    rows = [tuple(row) for row in connection.execute("PRAGMA integrity_check")]
    if rows != [("ok",)]:
        raise DatabaseHealthError("Full SQLite integrity check failed.")


def inspect_connection(connection: sqlite3.Connection) -> DatabaseMetadata:
    integrity_check(connection)
    version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    tables = frozenset(
        row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    )
    return DatabaseMetadata(version, tables)


class SQLiteHealth:
    def inspect(self, path: Path, *, readonly: bool = False) -> DatabaseMetadata:
        with closing(open_existing(path, readonly=readonly)) as connection:
            return inspect_connection(connection)

    def verify(
        self, path: Path, *, expected_version: int | None = None, readonly: bool = True
    ) -> DatabaseMetadata:
        metadata = self.inspect(path, readonly=readonly)
        if expected_version is not None and metadata.version != expected_version:
            raise DatabaseHealthError("Backup schema version differs from its source.")
        if metadata.version < 1 or not CORE_TABLES <= metadata.tables:
            raise DatabaseHealthError("Expected product database tables/version are missing.")
        return metadata


def sidecars(path: Path) -> tuple[Path, ...]:
    return tuple(Path(str(path) + suffix) for suffix in ("-journal", "-wal", "-shm"))
