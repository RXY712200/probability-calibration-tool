import sqlite3
from contextlib import closing
from dataclasses import replace
from pathlib import Path

import pytest

from probability_calibration_tool.persistence.database import create_connection
from probability_calibration_tool.persistence.unit_of_work import UnitOfWork, create_uow_factory

from .helpers import make_round, make_snapshot


def assert_joint_counts(path: Path, expected: int) -> None:
    with closing(create_connection(path)) as observer:
        assert (
            observer.execute("SELECT COUNT(*) FROM rounds WHERE round_id = 'current'").fetchone()[0]
            == expected
        )
        assert (
            observer.execute(
                "SELECT COUNT(*) FROM round_analysis_snapshots WHERE round_id = 'current'"
            ).fetchone()[0]
            == expected
        )


def test_snapshot_insertion_failure_rolls_back_round_and_snapshot(db_path: Path) -> None:
    with pytest.raises(sqlite3.IntegrityError), UnitOfWork(db_path) as uow:
        uow.rounds.insert(make_round())
        uow.snapshots.insert(replace(make_snapshot(), p_h_used=0))
    assert_joint_counts(db_path, 0)


def test_round_and_snapshot_commit_together(db_path: Path) -> None:
    factory = create_uow_factory(db_path)
    with factory() as uow:
        uow.rounds.insert(make_round())
        uow.snapshots.insert(make_snapshot())
        uow.commit()
    assert_joint_counts(db_path, 1)


def test_scope_exit_without_commit_rolls_back_both(db_path: Path) -> None:
    with UnitOfWork(db_path) as uow:
        uow.rounds.insert(make_round())
        uow.snapshots.insert(make_snapshot())
    assert_joint_counts(db_path, 0)


def test_exception_after_both_inserts_rolls_back_both(db_path: Path) -> None:
    with pytest.raises(RuntimeError, match="injected"), UnitOfWork(db_path) as uow:
        uow.rounds.insert(make_round())
        uow.snapshots.insert(make_snapshot())
        raise RuntimeError("injected failure after both inserts")
    assert_joint_counts(db_path, 0)


def test_post_commit_write_starts_an_uncommitted_transaction(db_path: Path) -> None:
    with closing(create_connection(db_path)) as observer, UnitOfWork(db_path) as uow:
        uow.meta.set("first", "1")
        uow.commit()
        assert observer.execute("SELECT value FROM meta WHERE key = 'first'").fetchone()[0] == "1"
        uow.meta.set("second", "2")
        assert uow.meta.get("second").value == "2"
        assert observer.execute("SELECT value FROM meta WHERE key = 'second'").fetchone() is None
    with closing(create_connection(db_path)) as reopened:
        assert reopened.execute("SELECT value FROM meta WHERE key = 'first'").fetchone()[0] == "1"
        assert reopened.execute("SELECT value FROM meta WHERE key = 'second'").fetchone() is None


def test_second_explicit_commit_persists_only_its_transaction(db_path: Path) -> None:
    with UnitOfWork(db_path) as uow:
        uow.meta.set("first", "1")
        uow.commit()
        uow.meta.set("second", "2")
        uow.commit()
        uow.meta.set("third", "3")
    with closing(create_connection(db_path)) as reopened:
        rows = reopened.execute(
            "SELECT key, value FROM meta WHERE key IN ('first', 'second', 'third') ORDER BY key"
        ).fetchall()
        assert [tuple(row) for row in rows] == [("first", "1"), ("second", "2")]


def test_exception_after_commit_rolls_back_only_later_writes(db_path: Path) -> None:
    with pytest.raises(RuntimeError, match="second transaction"), UnitOfWork(db_path) as uow:
        uow.meta.set("first", "1")
        uow.commit()
        uow.meta.set("second", "2")
        raise RuntimeError("second transaction failure")
    with closing(create_connection(db_path)) as reopened:
        assert reopened.execute("SELECT value FROM meta WHERE key = 'first'").fetchone()[0] == "1"
        assert reopened.execute("SELECT value FROM meta WHERE key = 'second'").fetchone() is None
