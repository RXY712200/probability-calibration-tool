"""SQLite connection and explicit UTC timestamp conversion."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path


def serialize_utc(value: datetime) -> str:
    """Serialize an aware UTC datetime without accepting naive timestamps."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Naive datetime values are not accepted.")
    return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def deserialize_utc(value: str) -> datetime:
    """Deserialize canonical UTC ISO-8601 text into an aware UTC datetime."""
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Persisted timestamp must include a UTC offset.")
    return parsed.astimezone(UTC)


def create_connection(path: Path | str) -> sqlite3.Connection:
    """Create the only allowed SQLite connection shape for this application."""
    connection = sqlite3.connect(str(path), isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = DELETE")
    connection.execute("PRAGMA synchronous = EXTRA")
    return connection


def ensure_write_transaction(connection: sqlite3.Connection) -> None:
    """Keep repository writes uncommitted until their caller explicitly commits.

    A Unit of Work already owns a transaction. Standalone repository callers
    must commit or roll back the transaction started here themselves.
    """
    if not connection.in_transaction:
        connection.execute("BEGIN")
