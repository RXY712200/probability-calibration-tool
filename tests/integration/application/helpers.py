from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

from probability_calibration_tool.application import (
    CalculateCommand,
    CorrectionService,
    MaintenanceService,
    RecoveryService,
    RegimeService,
    RoundService,
    Workflow,
)
from probability_calibration_tool.persistence.database import create_connection
from probability_calibration_tool.persistence.migrations import ensure_schema
from probability_calibration_tool.persistence.unit_of_work import create_uow_factory

STAMP = datetime(2026, 9, 1, 10, 0, 0, 123456, UTC)
COMMAND = CalculateCommand(1, False, 70, "2.00", "3.00")


@dataclass
class FakeClock:
    value: datetime = STAMP

    def now(self) -> datetime:
        return self.value

    def advance(self) -> datetime:
        self.value += timedelta(minutes=1)
        return self.value


@dataclass
class FakeIdGenerator:
    count: int = 0

    def new_id(self) -> str:
        self.count += 1
        return str(UUID(int=self.count))


class InjectedFailure(RuntimeError):
    pass


class FakeSafetyBackupPort:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.fail = False
        self.on_backup = lambda: None

    def create_verified_safety_backup(self, reason: str) -> None:
        self.calls.append(reason)
        self.on_backup()
        if self.fail:
            raise InjectedFailure("Safety verification failed.")


class Harness:
    def __init__(self, path: Path) -> None:
        self.path = path
        with closing(create_connection(path)) as connection:
            ensure_schema(connection)
        self.clock = FakeClock()
        self.ids = FakeIdGenerator()
        self.backup = FakeSafetyBackupPort()
        self.factory = create_uow_factory(path)
        self.rounds = RoundService(self.factory, self.clock, self.ids)
        self.regimes = RegimeService(self.factory, self.clock, self.ids)
        self.recovery = RecoveryService(self.factory)
        self.maintenance = MaintenanceService(self.factory)
        self.corrections = CorrectionService(self.factory, self.clock, self.ids, self.backup)

    def workflow(self) -> Workflow:
        return Workflow(self.rounds, self.recovery)

    def record(self, round_id):
        with self.factory() as uow:
            return uow.rounds.get(round_id)

    def snapshot(self, round_id):
        with self.factory() as uow:
            return uow.snapshots.get(round_id)

    def stats(self, character_id=1, regime_id=None):
        with self.factory() as uow:
            if regime_id is None:
                regime_id = uow.regimes.get_active(character_id).regime_id
            return uow.stats.get(character_id, regime_id)

    def capture(self):
        """All logical database content from a fresh connection, not an open writer."""
        with closing(create_connection(self.path)) as connection:
            return {
                table: tuple(
                    tuple(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY 1, 2")
                )
                for table in (
                    "characters",
                    "history_regimes",
                    "rounds",
                    "round_analysis_snapshots",
                    "character_stats",
                    "meta",
                )
            }

    def seed_history(self, wins=19, losses=1, character_id=1, include=True):
        ids = []
        for result in [True] * wins + [False] * losses:
            command = CalculateCommand(character_id, False, 60, "2", "2")
            view = self.rounds.calculate(command)
            ids.append(view.round_id)
            self.clock.advance()
            self.rounds.complete_pending(view.round_id, result, include)
            self.clock.advance()
        return ids
