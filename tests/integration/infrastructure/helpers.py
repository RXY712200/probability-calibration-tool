from contextlib import closing
from datetime import date, timedelta
from types import SimpleNamespace

from application.helpers import FakeClock, FakeIdGenerator, Harness, InjectedFailure

from probability_calibration_tool.infrastructure.backup import BackupService
from probability_calibration_tool.infrastructure.paths import AppPaths
from probability_calibration_tool.infrastructure.sqlite_health import open_existing

__all__ = [
    "FakeClock",
    "FakeIdGenerator",
    "Harness",
    "InjectedFailure",
    "make_rig",
    "mutate",
    "query",
]


def make_rig(root):
    paths = AppPaths.from_root(root)
    paths.create_directories()
    h = Harness(paths.database)
    calendar = SimpleNamespace(value=date(2026, 9, 1))
    calendar.today = lambda: calendar.value
    backup = BackupService(paths, clock=h.clock, ids=h.ids, calendar=calendar)

    def advance():
        h.clock.advance()
        calendar.value += timedelta(days=1)

    return SimpleNamespace(paths=paths, h=h, backup=backup, calendar=calendar, advance=advance)


def query(path, sql):
    with closing(open_existing(path)) as connection:
        return [tuple(row) for row in connection.execute(sql)]


def mutate(path, sql, parameters=()):
    with closing(open_existing(path)) as connection:
        connection.execute(sql, parameters)
