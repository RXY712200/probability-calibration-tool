"""Explicit ordered migrations; the production registry intentionally contains no v2."""

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass


class UnsupportedMigrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Migration:
    source_version: int
    target_version: int
    apply: Callable[[sqlite3.Connection], None]


class MigrationRegistry:
    def __init__(self, migrations: tuple[Migration, ...] = ()):
        self._steps = {step.source_version: step for step in migrations}
        if len(self._steps) != len(migrations) or any(
            type(step.source_version) is not int
            or type(step.target_version) is not int
            or step.source_version < 0
            or step.target_version <= step.source_version
            for step in migrations
        ):
            raise ValueError("Migrations must have unique, strictly increasing integer versions.")

    def plan(self, source: int, target: int) -> tuple[Migration, ...]:
        steps = []
        while source < target:
            step = self._steps.get(source)
            if step is None or step.target_version > target:
                raise UnsupportedMigrationError("No supported migration path exists.")
            steps.append(step)
            source = step.target_version
        if source != target:
            raise UnsupportedMigrationError("Downgrades are prohibited.")
        return tuple(steps)


def apply_migrations(
    connection: sqlite3.Connection, steps: tuple[Migration, ...], validate
) -> None:
    connection.execute("BEGIN IMMEDIATE")
    try:
        for step in steps:
            actual = int(connection.execute("PRAGMA user_version").fetchone()[0])
            if actual != step.source_version:
                raise UnsupportedMigrationError("Source version changed before migration.")
            step.apply(connection)
            connection.execute(f"PRAGMA user_version={step.target_version}")
        validate(connection)
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
