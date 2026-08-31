"""Small injectable boundaries; no backup/filesystem implementation lives here."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from probability_calibration_tool.persistence.unit_of_work import UnitOfWork

UowFactory = Callable[[], UnitOfWork]


class Clock(Protocol):
    def now(self) -> datetime:
        """Return an aware UTC datetime."""
        ...


class IdGenerator(Protocol):
    def new_id(self) -> str: ...


class SafetyBackupPort(Protocol):
    def create_verified_safety_backup(self, reason: str) -> None:
        """Return only after verification succeeds; raise on any failure."""
        ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class UUIDGenerator:
    def new_id(self) -> str:
        return str(uuid4())
