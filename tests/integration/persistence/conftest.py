import sqlite3
from collections.abc import Iterator
from contextlib import closing
from pathlib import Path

import pytest

from probability_calibration_tool.domain.enums import RoundStatus
from probability_calibration_tool.persistence.database import create_connection
from probability_calibration_tool.persistence.migrations import ensure_schema

from .helpers import insert_row, make_round, sql_values


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "test.db"
    with closing(create_connection(path)) as connection:
        ensure_schema(connection)
    return path


@pytest.fixture
def connection(db_path: Path) -> Iterator[sqlite3.Connection]:
    with closing(create_connection(db_path)) as db:
        yield db


@pytest.fixture
def snapshot_connection(connection: sqlite3.Connection) -> sqlite3.Connection:
    insert_row(connection, "rounds", sql_values(make_round("prior", RoundStatus.COMPLETED)))
    insert_row(connection, "rounds", sql_values(make_round()))
    return connection
