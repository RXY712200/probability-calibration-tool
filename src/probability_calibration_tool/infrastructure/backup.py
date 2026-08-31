"""Verified Online Backup candidates and independently rotated backup pools."""

import logging
import os
import re
import sqlite3
import tempfile
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, date, datetime
from enum import StrEnum
from pathlib import Path
from uuid import uuid4

from probability_calibration_tool.persistence.database import create_connection

from .error_reporting import ErrorPresentation, report_error
from .paths import AppPaths
from .sqlite_health import (
    CORE_TABLES,
    DatabaseHealthError,
    SQLiteHealth,
    inspect_connection,
    open_existing,
)


class BackupCategory(StrEnum):
    RECENT = "recent"
    DAILY = "daily"
    SAFETY = "safety"


class InventoryKind(StrEnum):
    VALID = "valid"
    CORRUPT = "corrupt"
    TEMPORARY = "temporary"
    QUARANTINE = "quarantine"
    UNRELATED = "unrelated"


@dataclass(frozen=True)
class BackupEntry:
    path: Path
    kind: InventoryKind
    created_at: datetime | None = None
    local_date: date | None = None


@dataclass(frozen=True)
class BackupResult:
    path: Path
    warnings: tuple[str, ...] = ()
    created: bool = True


@dataclass(frozen=True)
class BackupOutcome:
    backup: BackupResult | None
    warning: ErrorPresentation | None = None


class SystemClock:
    def now(self):
        return datetime.now(UTC)


class UUIDGenerator:
    def new_id(self):
        return str(uuid4())


class LocalCalendar:
    def today(self):
        return datetime.now().astimezone().date()


REASONS = {"pre_migration", "pre_restore", "pre_history_correction"}
_STAMP = r"(?P<stamp>\d{8}T\d{6}\.\d{6}Z)"
_ID = r"[A-Za-z0-9-]{1,64}"
_PATTERNS = {
    BackupCategory.RECENT: re.compile(r"recent_" + _STAMP + "_" + _ID + r"\.db\Z"),
    BackupCategory.DAILY: re.compile(
        r"daily_(?P<day>\d{4}-\d{2}-\d{2})_" + _STAMP + "_" + _ID + r"\.db\Z"
    ),
    BackupCategory.SAFETY: re.compile(
        r"safety_(?:pre_migration|pre_restore|pre_history_correction)_"
        + _STAMP
        + "_"
        + _ID
        + r"\.db\Z"
    ),
}


class BackupService:
    def __init__(
        self,
        paths: AppPaths,
        source: Path | None = None,
        *,
        clock=None,
        ids=None,
        calendar=None,
        health=None,
        logger=None,
    ):
        self.paths = paths
        self.source = source if source is not None else paths.database
        self.clock = clock if clock is not None else SystemClock()
        self.ids = ids if ids is not None else UUIDGenerator()
        self.calendar = calendar if calendar is not None else LocalCalendar()
        self.health = health if health is not None else SQLiteHealth()
        self.logger = logger if logger is not None else logging.getLogger(__name__)

    def _directory(self, category):
        return {
            BackupCategory.RECENT: self.paths.recent,
            BackupCategory.DAILY: self.paths.daily,
            BackupCategory.SAFETY: self.paths.safety,
        }[category]

    def inventory(self, category: BackupCategory) -> tuple[BackupEntry, ...]:
        entries = []
        for path in sorted(self._directory(category).iterdir()):
            if not path.is_file() or path.is_symlink():
                entries.append(BackupEntry(path, InventoryKind.UNRELATED))
                continue
            if "UNVERIFIED_CORRUPT" in path.name:
                entries.append(BackupEntry(path, InventoryKind.QUARANTINE))
                continue
            if path.name.startswith(".candidate_") or path.name.endswith(".tmp"):
                entries.append(BackupEntry(path, InventoryKind.TEMPORARY))
                continue
            match = _PATTERNS[category].fullmatch(path.name)
            if match is None:
                entries.append(BackupEntry(path, InventoryKind.UNRELATED))
                continue
            try:
                created = datetime.strptime(match["stamp"], "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=UTC)
                day = date.fromisoformat(match["day"]) if category == BackupCategory.DAILY else None
            except ValueError:
                entries.append(BackupEntry(path, InventoryKind.UNRELATED))
                continue
            try:
                self.health.verify(path)
            except (OSError, ValueError, RuntimeError, sqlite3.DatabaseError):
                self.logger.warning("Preserving invalid recognized backup: %s", path.name)
                entries.append(BackupEntry(path, InventoryKind.CORRUPT, created, day))
            else:
                entries.append(BackupEntry(path, InventoryKind.VALID, created, day))
        return tuple(entries)

    def _copy_online(self, candidate: Path) -> int:
        with closing(open_existing(self.source)) as source:
            source.execute("BEGIN")
            metadata = inspect_connection(source)
            if metadata.version < 1 or not CORE_TABLES <= metadata.tables:
                raise DatabaseHealthError("Source is not a recognized product database.")
            with closing(create_connection(candidate)) as target:
                source.backup(target)
            return metadata.version

    def create(self, category: BackupCategory, reason: str | None = None) -> BackupResult:
        if category == BackupCategory.SAFETY and reason not in REASONS:
            raise ValueError("A recognized safety reason is required.")
        directory = self._directory(category)
        day = self.calendar.today() if category == BackupCategory.DAILY else None
        if day is not None:
            existing = [
                entry
                for entry in self.inventory(category)
                if entry.kind == InventoryKind.VALID and entry.local_date == day
            ]
            if existing:
                return BackupResult(
                    max(existing, key=lambda entry: entry.created_at).path, created=False
                )
        now = self.clock.now()
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("Backup clock must be aware.")
        stamp = now.astimezone(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
        unique = self.ids.new_id()
        if not re.fullmatch(_ID, unique):
            raise ValueError("Unsafe backup ID.")
        prefix = category.value
        if day is not None:
            prefix += "_" + day.isoformat()
        if category == BackupCategory.SAFETY:
            prefix += "_" + reason
        final = directory / f"{prefix}_{stamp}_{unique}.db"
        if final.exists():
            raise FileExistsError("Refusing to overwrite an existing backup.")
        fd, name = tempfile.mkstemp(prefix=".candidate_", suffix=".tmp", dir=directory)
        os.close(fd)
        candidate = Path(name)
        try:
            version = self._copy_online(candidate)
            self.health.verify(candidate, expected_version=version)
            with candidate.open("r+b") as stream:
                os.fsync(stream.fileno())
            os.replace(candidate, final)
        finally:
            if candidate.exists():
                try:
                    candidate.unlink()
                except OSError:
                    self.logger.warning("Could not remove failed backup candidate: %s", candidate)
        return BackupResult(final, self._rotate(category))

    def _rotate(self, category) -> tuple[str, ...]:
        try:
            valid = [
                entry for entry in self.inventory(category) if entry.kind == InventoryKind.VALID
            ]
            valid.sort(
                key=lambda entry: (entry.local_date or date.min, entry.created_at, entry.path.name)
            )
            if category == BackupCategory.DAILY:
                newest_by_date = {entry.local_date: entry for entry in valid}
                keep = {entry.path for entry in list(newest_by_date.values())[-7:]}
                obsolete = [entry for entry in valid if entry.path not in keep]
            else:
                limit = 5 if category == BackupCategory.RECENT else 10
                obsolete = valid[:-limit]
            for entry in obsolete:
                entry.path.unlink()  # First deletion failure stops the entire loop.
        except OSError:
            message = "Backup accepted; rotation stopped safely with possible over-retention."
            self.logger.warning(message, exc_info=True)
            return (message,)
        return ()


class BackupCoordinator:
    """Nonfatal capability boundary, not a callback attached to Phase 3 transactions."""

    def __init__(self, service: BackupService):
        self.service = service

    def _attempt(self, category):
        try:
            return BackupOutcome(self.service.create(category))
        except Exception as exc:  # noqa: BLE001 - nonfatal boundary logs the full traceback
            message = (
                f"{category.value.capitalize()} backup failed; saved main data was not reverted."
            )
            presentation = report_error(self.service.logger, exc, message)
            self.service.logger.warning("error_id=%s %s", presentation.error_id, message)
            return BackupOutcome(None, presentation)

    def recent(self) -> BackupOutcome:
        return self._attempt(BackupCategory.RECENT)

    def daily(self) -> BackupOutcome:
        return self._attempt(BackupCategory.DAILY)


class SQLiteSafetyBackupAdapter:
    def __init__(self, service: BackupService):
        self.service = service

    def create_verified_safety_backup(self, reason: str) -> None:
        self.service.create(BackupCategory.SAFETY, reason)
