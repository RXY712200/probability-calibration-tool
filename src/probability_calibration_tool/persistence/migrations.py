"""Schema inspection and the deliberately small v0/v1 migration registry."""

import sqlite3

from .errors import UnsupportedNewerSchemaError
from .schema import SCHEMA_VERSION, initialize_v1


def ensure_schema(connection: sqlite3.Connection) -> None:
    """Initialize v0 or recognize v1; never downgrade or modify a newer schema."""
    version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if version > SCHEMA_VERSION:
        raise UnsupportedNewerSchemaError(
            f"Database schema {version} is newer than supported schema {SCHEMA_VERSION}."
        )
    if version == 0:
        initialize_v1(connection)
