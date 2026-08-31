"""Explicit commit-or-rollback Unit of Work."""

from collections.abc import Callable
from pathlib import Path
from typing import Self

from .database import create_connection
from .repositories import (
    CharacterRepository,
    CharacterStatsRepository,
    HistoryRegimeRepository,
    MetaRepository,
    RoundRepository,
    SnapshotRepository,
)


class UnitOfWork:
    """Each commit ends one transaction and starts the next uncommitted one."""

    def __init__(self, path: Path | str) -> None:
        self._path = path
        self._connection = None

    def __enter__(self) -> Self:
        self._connection = create_connection(self._path)
        self._connection.execute("BEGIN")
        self.characters = CharacterRepository(self._connection)
        self.regimes = HistoryRegimeRepository(self._connection)
        self.rounds = RoundRepository(self._connection)
        self.snapshots = SnapshotRepository(self._connection)
        self.stats = CharacterStatsRepository(self._connection)
        self.meta = MetaRepository(self._connection)
        return self

    def commit(self) -> None:
        assert self._connection is not None
        self._connection.commit()
        self._connection.execute("BEGIN")

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        assert self._connection is not None
        try:
            self._connection.rollback()
        finally:
            self._connection.close()
            self._connection = None


def create_uow_factory(path: Path | str) -> Callable[[], UnitOfWork]:
    return lambda: UnitOfWork(path)
