import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path

import pytest

from probability_calibration_tool.infrastructure.sqlite_health import (
    DatabaseHealthError,
    SQLiteHealth,
    integrity_check,
    open_existing,
)

from .helpers import mutate, query


def test_full_check_requires_exact_ok_result():
    class FakeConnection:
        def __init__(self, rows):
            self.rows = rows

        def execute(self, sql):
            assert sql == "PRAGMA integrity_check"
            return self.rows

    integrity_check(FakeConnection([("ok",)]))
    for rows in ([], [("ok",), ("error",)], [("OK",)], [("quick ok",)]):
        with pytest.raises(DatabaseHealthError):
            integrity_check(FakeConnection(rows))


def test_existing_probe_does_not_force_readonly_or_change_journal_mode(rig):
    mutate(rig.paths.database, "PRAGMA journal_mode=WAL")
    with closing(open_existing(rig.paths.database)) as connection:
        trace = []
        connection.set_trace_callback(trace.append)
        integrity_check(connection)
        assert query(rig.paths.database, "PRAGMA journal_mode") == [("wal",)]
        connection.execute("BEGIN")
        connection.execute("UPDATE meta SET value=value")  # mode=rw can recover/write; rolled back.
        connection.rollback()
        assert "PRAGMA quick_check" not in trace


def test_empty_unrelated_sqlite_is_not_verified_backup(tmp_path):
    path = tmp_path / "empty.db"
    with closing(sqlite3.connect(path)):
        pass
    with pytest.raises(DatabaseHealthError):
        SQLiteHealth().verify(path)
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("CREATE TABLE unrelated (value)")
        connection.execute("PRAGMA user_version=1")
    with pytest.raises(DatabaseHealthError):
        SQLiteHealth().verify(path)


def test_native_hot_rollback_journal_is_recovered(rig):
    # A real SQLite write transaction spills dirty pages before os._exit, leaving a hot journal.
    mutate(rig.paths.database, "CREATE TABLE crash_payload (id INTEGER PRIMARY KEY, data BLOB)")
    with closing(open_existing(rig.paths.database)) as connection:
        connection.execute("BEGIN")
        connection.executemany(
            "INSERT INTO crash_payload VALUES (?, ?)", [(i, b"old" * 2000) for i in range(200)]
        )
        connection.commit()
    script = """
import os, sqlite3, sys
c=sqlite3.connect(sys.argv[1], isolation_level=None)
c.execute('PRAGMA journal_mode=DELETE')
c.execute('PRAGMA cache_size=5')
c.execute('PRAGMA cache_spill=ON')
c.execute('BEGIN IMMEDIATE')
c.execute('UPDATE crash_payload SET data=?', (b'new'*2000,))
os._exit(0)
"""
    subprocess.run([sys.executable, "-c", script, str(rig.paths.database)], check=True, timeout=15)
    journal = Path(str(rig.paths.database) + "-journal")
    assert journal.exists() and journal.stat().st_size > 512
    SQLiteHealth().verify(rig.paths.database, readonly=False)
    assert query(
        rig.paths.database,
        "SELECT count(*) FROM crash_payload WHERE data=x'" + (b"old" * 2000).hex() + "'",
    ) == [(200,)]
    assert not journal.exists()
