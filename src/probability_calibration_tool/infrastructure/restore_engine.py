"""Filesystem replacement primitives; policy and validations belong to Application."""

import logging
import os
import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

from .sqlite_health import SQLiteHealth, sidecars


def temporary_database(directory: Path, prefix: str) -> Path:
    fd, name = tempfile.mkstemp(dir=directory, prefix=prefix, suffix=".tmp")
    os.close(fd)
    return Path(name)


def cleanup_temporary(path: Path, logger) -> None:
    for file in (path, *sidecars(path)):
        try:
            file.unlink(missing_ok=True)
        except OSError:
            logger.warning("Could not clean temporary file: %s", file)


class RestoreEngine:
    def __init__(self, health=None, logger=None):
        self.health = health if health is not None else SQLiteHealth()
        self.logger = logger if logger is not None else logging.getLogger(__name__)

    def prepare_copy(self, candidate: Path, live: Path) -> Path:
        if candidate.resolve() == live.resolve():
            raise ValueError("Restore requires a separate backup candidate.")
        if any(path.exists() for path in sidecars(candidate)):
            raise RuntimeError(
                "Restore candidate must be a standalone immutable backup, without sidecars."
            )
        self.health.verify(candidate, readonly=True)
        temporary = temporary_database(live.parent, ".restore_")
        try:
            shutil.copyfile(candidate, temporary)  # Immutable offline candidate, NEVER live backup.
            return temporary
        except BaseException:
            cleanup_temporary(temporary, self.logger)
            raise

    def replace_normal(self, temporary: Path, live: Path) -> None:
        if any(path.exists() for path in sidecars(live)):
            raise RuntimeError("Unexplained SQLite sidecars block Normal Restore.")
        self.replace(temporary, live)

    def replace(self, temporary: Path, live: Path) -> None:
        if temporary.parent.resolve() != live.parent.resolve():
            raise ValueError("Restore replacement must be staged in the live data directory.")
        with temporary.open("r+b") as stream:
            os.fsync(stream.fileno())
        os.replace(temporary, live)

    def quarantine(self, live: Path, directory: Path) -> tuple[str, ...]:
        warnings = []
        token = str(uuid4())
        for source in (live, *sidecars(live)):
            if not source.exists():
                continue
            target = directory / f"UNVERIFIED_CORRUPT_{token}_{source.name}"
            try:
                shutil.copyfile(source, target)
            except OSError:
                warnings.append(
                    "Damaged-file quarantine copy failed; replacement may still proceed."
                )
                self.logger.warning("Quarantine copy failed: %s", source, exc_info=True)
        # Isolation is mandatory even if the best-effort diagnostic copies failed.
        for source in sidecars(live):
            if source.exists():
                os.replace(source, live.parent / f"UNVERIFIED_CORRUPT_{token}_{source.name}")
        return tuple(warnings)
