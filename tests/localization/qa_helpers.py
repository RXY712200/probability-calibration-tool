"""Tests-only bilingual QA harness with isolated mutable state per language track."""

from __future__ import annotations

import shutil
import sqlite3
import subprocess
import sys
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

from PySide6.QtCore import QCoreApplication, QSettings

from probability_calibration_tool.application import (
    CorrectionService,
    MaintenanceService,
    RecoveryService,
    RegimeService,
    RoundService,
    Workflow,
)
from probability_calibration_tool.localization import (
    APP_QM_NAME,
    PREFERENCE_KEY,
    FallbackReason,
    Language,
    initialize_localization,
)
from probability_calibration_tool.persistence.database import create_connection
from probability_calibration_tool.persistence.migrations import ensure_schema
from probability_calibration_tool.persistence.unit_of_work import create_uow_factory

from .step5_support import ROOT, TS_PATH

STAMP = datetime(2026, 9, 1, 10, 0, 0, 123456, UTC)
TABLE_ORDER = (
    "characters",
    "history_regimes",
    "rounds",
    "round_analysis_snapshots",
    "character_stats",
    "meta",
)
TABLE_ORDER_BY = {
    "characters": "character_id",
    "history_regimes": "character_id, regime_number, regime_id",
    "rounds": "created_at, round_id",
    "round_analysis_snapshots": "round_id",
    "character_stats": "character_id, regime_id",
    "meta": "key",
}


@dataclass
class FakeClock:
    value: datetime = STAMP

    def now(self) -> datetime:
        return self.value

    def advance(self) -> datetime:
        self.value += timedelta(minutes=1)
        return self.value


@dataclass
class FakeIds:
    count: int = 0

    def new_id(self) -> str:
        self.count += 1
        return str(UUID(int=self.count))


class FakeSafetyBackup:
    def __init__(self) -> None:
        self.calls = []

    def create_verified_safety_backup(self, reason: str) -> None:
        self.calls.append(reason)


class ParityHarness:
    def __init__(self, path: Path) -> None:
        self.path = path
        with closing(create_connection(path)) as connection:
            ensure_schema(connection)
        self.clock = FakeClock()
        self.ids = FakeIds()
        self.backup = FakeSafetyBackup()
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
            target = regime_id or uow.regimes.get_active(character_id).regime_id
            return uow.stats.get(character_id, target)

    def seed_history(self, wins=19, losses=1, character_id=1, include=True):
        from probability_calibration_tool.application.commands import CalculateCommand

        ids = []
        for result in [True] * wins + [False] * losses:
            view = self.rounds.calculate(CalculateCommand(character_id, False, 60, "2", "2"))
            ids.append(view.round_id)
            self.clock.advance()
            self.rounds.complete_pending(view.round_id, result, include)
            self.clock.advance()
        return ids


def create_seed_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(create_connection(path)) as connection:
        ensure_schema(connection)


def canonical_database(path: Path) -> dict[str, tuple[tuple[str, ...], tuple[tuple, ...]]]:
    """Compare every column with explicit SELECT lists and stable semantic ordering.

    The sole normalization allowlist entry is ``character_stats.updated_at``. Its
    repository update uses the wall clock (there is no clock injection point), so
    two intentionally sequential language tracks cannot produce the same instant.
    No IDs, states, reasons, links, math, odds, results, or other values are changed.
    """
    result = {}
    with closing(sqlite3.connect(path)) as connection:
        for table in TABLE_ORDER:
            columns = tuple(row[1] for row in connection.execute(f'PRAGMA table_info("{table}")'))
            select_list = ", ".join(f'"{column}"' for column in columns)
            raw_rows = tuple(
                connection.execute(
                    f'SELECT {select_list} FROM "{table}" ORDER BY {TABLE_ORDER_BY[table]}'
                ).fetchall()
            )
            rows = tuple(
                tuple(
                    "<wall-clock>"
                    if table == "character_stats" and column == "updated_at"
                    else value
                    for column, value in zip(columns, row, strict=True)
                )
                for row in raw_rows
            )
            result[table] = columns, rows
    return result


def build_official_qm(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    candidate = directory / APP_QM_NAME
    executable = Path(sys.executable).parent / "pyside6-lrelease.exe"
    assert executable.is_file() and executable.resolve().is_relative_to((ROOT / ".venv").resolve())
    process = subprocess.run(
        [
            str(executable),
            str(TS_PATH),
            "-qm",
            str(candidate),
            "-fail-on-unfinished",
            "-fail-on-invalid",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    assert candidate.is_file() and candidate.stat().st_size > 0
    return candidate


@contextmanager
def activated_track(app: QCoreApplication, root: Path, language: Language, candidate: Path):
    root.mkdir(parents=True, exist_ok=True)
    if language == Language.ZH_CN:
        directory = root / "languages"
        directory.mkdir()
        shutil.copyfile(candidate, directory / APP_QM_NAME)
        settings = QSettings(str(root / "settings.ini"), QSettings.Format.IniFormat)
        settings.setFallbacksEnabled(False)
        settings.setValue(PREFERENCE_KEY, Language.ZH_CN.value)
        settings.sync()
    context = initialize_localization(app, root)
    if language == Language.EN:
        assert context.effective_language == Language.EN
        assert context.app_translator is None
    else:
        assert context.preferred_language == Language.ZH_CN
        assert context.effective_language == Language.ZH_CN
        assert context.fallback_reason == FallbackReason.NONE
        assert context.app_translator is not None
    try:
        yield context
    finally:
        for translator in (context.app_translator, context.qt_translator):
            if translator is not None:
                app.removeTranslator(translator)


def run_bilingual_pair(tmp_path, app, candidate, scenario):
    """Compare isolated tracks, allowing only the documented wall-clock sentinel."""
    seed = tmp_path / "seed" / "initial.db"
    create_seed_database(seed)
    outputs = {}
    for language in (Language.EN, Language.ZH_CN):
        track = tmp_path / language.value
        database = track / "business.db"
        database.parent.mkdir(parents=True)
        shutil.copyfile(seed, database)
        with activated_track(app, track / "app", language, candidate) as context:
            outputs[language] = {
                "identity": (
                    context.preferred_language,
                    context.effective_language,
                    context.app_translator is not None,
                ),
                "scenario": scenario(ParityHarness(database)),
            }
    assert outputs[Language.EN]["identity"] == (Language.EN, Language.EN, False)
    assert outputs[Language.ZH_CN]["identity"] == (
        Language.ZH_CN,
        Language.ZH_CN,
        True,
    )
    left = outputs[Language.EN]["scenario"]
    right = outputs[Language.ZH_CN]["scenario"]
    assert left == right, _first_difference(left, right)
    return outputs


def _first_difference(left, right, path="scenario"):
    if type(left) is not type(right):
        return f"{path}: type {type(left)!r} != {type(right)!r}"
    if isinstance(left, dict):
        if left.keys() != right.keys():
            return f"{path}: keys {left.keys()!r} != {right.keys()!r}"
        for key in left:
            if left[key] != right[key]:
                return _first_difference(left[key], right[key], f"{path}.{key}")
    elif isinstance(left, (tuple, list)):
        if len(left) != len(right):
            return f"{path}: length {len(left)} != {len(right)}"
        for index, (left_item, right_item) in enumerate(zip(left, right, strict=True)):
            if left_item != right_item:
                return _first_difference(left_item, right_item, f"{path}[{index}]")
    return f"{path}: {left!r} != {right!r}"
