"""Prepare isolated Localization Step 7 manual-QA scenarios; never judge the UI."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
from dataclasses import asdict, dataclass, replace
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree as ET

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
RUNTIME_ROOT = PROJECT_ROOT / "outputs" / "localization_step7_runtime"
OFFICIAL_TS = PROJECT_ROOT / "translations" / "probability_calibration_tool_zh_CN.ts"
QA_ARTIFACTS = RUNTIME_ROOT / "_qa_artifacts"
QA_QM = QA_ARTIFACTS / "step7_qa_probability_calibration_tool_zh_CN.qm"
LEGACY_QA_QM = QA_ARTIFACTS / "probability_calibration_tool_zh_CN.qm"
APP_QM_NAME = "probability_calibration_tool_zh_CN.qm"
CHECKLIST = PROJECT_ROOT / "qa" / "localization" / "manual_checklist.md"
EXECUTION_GUIDE = PROJECT_ROOT / "qa" / "localization" / "execution_guide.md"
SCENARIO_MANIFEST = PROJECT_ROOT / "qa" / "localization" / "scenario_manifest.md"
FROZEN_TS_SHA256 = "82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257"
FORMAL_MANUAL_SCALING = "150%"
DELETED_DPI_IDS = frozenset(
    {
        "EN-DPI-150-01",
        "EN-DPI-150-02",
        "EN-DPI-150-03",
        "EN-DPI-150-04",
        "EN-DPI-150-05",
        "ZH-DPI125-01",
        "ZH-DPI125-02",
        "ZH-DPI125-03",
        "ZH-DPI125-04",
        "ZH-DPI125-05",
        "ZH-DPI125-06",
        "ZH-DPI125-07",
        "ZH-DPI150-01",
        "ZH-DPI150-02",
        "ZH-DPI150-03",
        "ZH-DPI150-04",
        "ZH-DPI150-05",
        "ZH-DPI150-06",
        "ZH-DPI150-07",
        "CR-DPI150-01",
        "CR-DPI150-02",
        "CR-DPI150-03",
        "CR-DPI150-04",
    }
)


def _discover_real_default_user_root() -> Path | None:
    if os.name == "nt":
        try:
            import winreg

            key_name = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_name) as key:
                raw = winreg.QueryValueEx(key, "Local AppData")[0]
            return Path(os.path.expandvars(raw)).resolve() / "ProbabilityCalibrationTool"
        except OSError:
            profile = os.environ.get("USERPROFILE")
            if profile:
                return Path(profile).resolve() / "AppData" / "Local" / "ProbabilityCalibrationTool"
    localappdata = os.environ.get("LOCALAPPDATA")
    return None if not localappdata else Path(localappdata).resolve() / "ProbabilityCalibrationTool"


_REAL_DEFAULT_USER_ROOT = _discover_real_default_user_root()


@dataclass(frozen=True)
class Scenario:
    purpose: str
    preference: str
    effective: str
    pack: str = "valid"
    database: str = "empty"
    backup: str = "none"
    fault: str | None = None


SCENARIOS = {
    "healthy_en": Scenario(
        "English healthy UI with valid and insufficient history", "en", "en", database="rich"
    ),
    "healthy_zh": Scenario(
        "Simplified Chinese healthy UI with official QA pack and history",
        "zh_CN",
        "zh_CN",
        database="rich",
    ),
    "lifecycle": Scenario("Restart-only language preference lifecycle", "en", "en"),
    "missing_pack": Scenario(
        "Preferred zh_CN with canonical pack absent", "zh_CN", "en", pack="missing"
    ),
    "corrupt_pack": Scenario(
        "Preferred zh_CN with corrupt canonical pack", "zh_CN", "en", pack="corrupt"
    ),
    "wrong_filename": Scenario(
        "Valid QM under a noncanonical filename", "zh_CN", "en", pack="wrong_filename"
    ),
    "wrong_location": Scenario(
        "Valid canonical-named QM outside the languages directory",
        "zh_CN",
        "en",
        pack="wrong_location",
    ),
    "invalid_preference": Scenario(
        "Unsupported saved preference with an otherwise valid pack", "INVALID_qa", "en"
    ),
    "confirm_pack_loss": Scenario(
        "Remove the pack after the Language dialog opens but before Confirm", "en", "en"
    ),
    "save_failure": Scenario(
        "Real Language dialog with deterministic isolated QSettings writer failure",
        "en",
        "en",
        fault="settings-save",
    ),
    "recovery": Scenario(
        "Exactly one valid pending round and snapshot", "en", "en", database="pending"
    ),
    "recovery_zh": Scenario(
        "Exactly one valid pending round and snapshot in Simplified Chinese",
        "zh_CN",
        "zh_CN",
        database="pending",
    ),
    "recovery_no_pending": Scenario(
        "Remove the isolated pending record after Recovery is displayed",
        "en",
        "en",
        database="pending",
    ),
    "recovery_no_pending_zh": Scenario(
        "Remove the isolated pending record after Chinese Recovery is displayed",
        "zh_CN",
        "zh_CN",
        database="pending",
    ),
    "recovery_stale_en": Scenario(
        "English Recovery with snapshot removable after presentation",
        "en",
        "en",
        database="pending",
    ),
    "recovery_stale_zh": Scenario(
        "Simplified Chinese Recovery with snapshot removable after presentation",
        "zh_CN",
        "zh_CN",
        database="pending",
    ),
    "recovery_localization_fallback": Scenario(
        "Pending Recovery plus preferred zh_CN and missing pack",
        "zh_CN",
        "en",
        pack="missing",
        database="pending",
    ),
    "multiple_pending": Scenario(
        "Deliberate test-only two-pending invariant violation",
        "en",
        "en",
        database="multiple_pending",
    ),
    "multiple_pending_zh": Scenario(
        "Deliberate test-only two-pending invariant violation in Simplified Chinese",
        "zh_CN",
        "zh_CN",
        database="multiple_pending",
    ),
    "data_safety_en": Scenario(
        "English Data Safety with a deliberately missing required snapshot",
        "en",
        "en",
        database="data_safety",
    ),
    "data_safety": Scenario(
        "Recognized DB with a deliberately missing required snapshot",
        "zh_CN",
        "zh_CN",
        database="data_safety",
    ),
    "data_safety_fallback": Scenario(
        "Data Safety plus preferred zh_CN missing-pack fallback notice condition",
        "zh_CN",
        "en",
        pack="missing",
        database="data_safety",
    ),
    "data_safety_warning_en": Scenario(
        "English Data Safety plus an ordinary startup warning",
        "en",
        "en",
        database="data_safety",
        fault="data-safety-warning",
    ),
    "data_safety_warning_zh": Scenario(
        "Simplified Chinese Data Safety plus an ordinary startup warning",
        "zh_CN",
        "zh_CN",
        database="data_safety",
        fault="data-safety-warning",
    ),
    "already_running": Scenario(
        "Two real processes sharing one isolated root; localization fallback is secondary",
        "zh_CN",
        "en",
        pack="missing",
    ),
    "correction": Scenario(
        "One completed correction candidate and no pending round",
        "zh_CN",
        "zh_CN",
        database="correction",
    ),
    "correction_en": Scenario(
        "English completed correction candidate and no pending round",
        "en",
        "en",
        database="correction",
    ),
    "correction_warning_en": Scenario(
        "English Correction commit plus isolated Recent-backup warning",
        "en",
        "en",
        database="correction",
        fault="recent-backup",
    ),
    "correction_warning_zh": Scenario(
        "Simplified Chinese Correction commit plus isolated Recent-backup warning",
        "zh_CN",
        "zh_CN",
        database="correction",
        fault="recent-backup",
    ),
    "restore_normal": Scenario(
        "Healthy live state A and verified, visibly distinguishable candidate B",
        "zh_CN",
        "zh_CN",
        database="restore_normal",
        backup="valid B",
    ),
    "restore_normal_en": Scenario(
        "English healthy live state A and verified, visibly distinguishable candidate B",
        "en",
        "en",
        database="restore_normal",
        backup="valid B",
    ),
    "restore_invalid": Scenario(
        "Healthy live DB with candidate that can be expired after selection",
        "en",
        "en",
        database="restore_normal",
        backup="valid then expired",
    ),
    "restore_corrupt": Scenario(
        "Healthy live DB and recognized corrupt backup excluded from verified candidates",
        "en",
        "en",
        database="restore_corrupt",
        backup="corrupt",
    ),
    "emergency_restore": Scenario(
        "Damaged live DB and verified healthy emergency candidate",
        "zh_CN",
        "zh_CN",
        database="emergency",
        backup="valid",
    ),
    "emergency_invalid": Scenario(
        "Damaged live DB with candidate that can be expired after selection",
        "en",
        "en",
        database="emergency",
        backup="valid then expired",
    ),
    "emergency_missing_pack": Scenario(
        "Damaged live DB, valid emergency candidate, preferred zh_CN, pack missing",
        "zh_CN",
        "en",
        pack="missing",
        database="emergency",
        backup="valid",
    ),
    "unexpected_en": Scenario(
        "Production unexpected-error presentation in English",
        "en",
        "en",
        fault="unexpected",
    ),
    "unexpected_zh": Scenario(
        "Production unexpected-error presentation in zh_CN",
        "zh_CN",
        "zh_CN",
        fault="unexpected",
    ),
    "unexpected_warning_en": Scenario(
        "English unexpected error while an ordinary startup warning is present",
        "en",
        "en",
        fault="unexpected-with-warning",
    ),
    "unexpected_warning_zh": Scenario(
        "Simplified Chinese unexpected error while an ordinary startup warning is present",
        "zh_CN",
        "zh_CN",
        fault="unexpected-with-warning",
    ),
    "backup_warning": Scenario(
        "Committed main operation plus injected nonfatal Recent-backup failure",
        "zh_CN",
        "zh_CN",
        fault="recent-backup",
    ),
    "over_retention_en": Scenario(
        "English real presentation of the over-retention warning code",
        "en",
        "en",
        fault="over-retention-warning",
    ),
    "over_retention_zh": Scenario(
        "Simplified Chinese real presentation of the over-retention warning code",
        "zh_CN",
        "zh_CN",
        fault="over-retention-warning",
    ),
    "quarantine_warning_en": Scenario(
        "English real presentation of the quarantine-copy warning code",
        "en",
        "en",
        fault="quarantine-warning",
    ),
    "quarantine_warning_zh": Scenario(
        "Simplified Chinese real presentation of the quarantine-copy warning code",
        "zh_CN",
        "zh_CN",
        fault="quarantine-warning",
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_link_or_junction(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    try:
        return bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (AttributeError, FileNotFoundError):
        return False


def _default_user_root() -> Path | None:
    return _REAL_DEFAULT_USER_ROOT


def _lexical(path: Path) -> Path:
    return Path(os.path.abspath(path))


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _reject_reparse_components(path: Path, *, anchor: Path) -> None:
    path = _lexical(path)
    anchor = _lexical(anchor)
    if not _is_within(path, anchor):
        raise RuntimeError(f"Safety guard rejected path outside approved anchor: {path}")
    current = anchor
    if current.exists() and _is_link_or_junction(current):
        raise RuntimeError(f"Safety guard rejected reparse point: {current}")
    for part in path.relative_to(anchor).parts:
        current /= part
        if os.path.lexists(current) and _is_link_or_junction(current):
            raise RuntimeError(f"Safety guard rejected reparse point: {current}")


def _validate_runtime_root(root: Path = RUNTIME_ROOT, *, self_test: bool = False) -> Path:
    root = _lexical(root)
    canonical = _lexical(RUNTIME_ROOT)
    if self_test:
        if not _is_within(root, canonical / "_safety_selftest"):
            raise RuntimeError(
                "Safety self-test root is outside its disposable controlled subtree."
            )
    elif root != canonical:
        raise RuntimeError("Safety guard rejected a noncanonical runtime root.")
    expected_parent = _lexical(PROJECT_ROOT / "outputs")
    if not _is_within(root, expected_parent) or root == expected_parent:
        raise RuntimeError("Safety guard rejected a runtime root outside project outputs.")
    _reject_reparse_components(root, anchor=_lexical(PROJECT_ROOT))
    resolved = root.resolve(strict=False)
    resolved_project = _lexical(PROJECT_ROOT).resolve(strict=True)
    if not _is_within(resolved, resolved_project / "outputs"):
        raise RuntimeError("Safety guard rejected a resolved runtime escape.")
    return root


def _scenario_dir_for(
    name: str,
    *,
    root: Path = RUNTIME_ROOT,
    allowlist=None,
    self_test: bool = False,
) -> Path:
    allowed = SCENARIOS if allowlist is None else allowlist
    if name not in allowed:
        raise ValueError(f"Unknown scenario: {name!r}")
    approved_root = _validate_runtime_root(root, self_test=self_test)
    target = _lexical(approved_root / name)
    if target.parent != approved_root or target == approved_root:
        raise RuntimeError("Safety guard rejected a path outside the approved runtime root.")
    _reject_reparse_components(target, anchor=_lexical(PROJECT_ROOT))
    resolved = target.resolve(strict=False)
    if not _is_within(resolved, approved_root.resolve(strict=False)) or resolved == approved_root:
        raise RuntimeError("Safety guard rejected a resolved scenario escape.")
    default = _default_user_root()
    app_root = target / "localappdata" / "ProbabilityCalibrationTool"
    if default is not None and app_root.resolve() == default.resolve():
        raise RuntimeError("Safety guard rejected the real default user application root.")
    return target


def _scenario_dir(name: str) -> Path:
    return _scenario_dir_for(name)


def _scenario_target_for(
    name: str,
    *parts: str,
    root: Path = RUNTIME_ROOT,
    allowlist=None,
    self_test: bool = False,
) -> Path:
    scenario = _scenario_dir_for(name, root=root, allowlist=allowlist, self_test=self_test)
    if any(not part or Path(part).is_absolute() or part in {".", ".."} for part in parts):
        raise RuntimeError("Safety guard rejected invalid mutation path components.")
    target = _lexical(scenario.joinpath(*parts))
    if not _is_within(target, scenario) or target == scenario:
        raise RuntimeError("Safety guard rejected mutation outside the scenario subtree.")
    _reject_reparse_components(target, anchor=scenario)
    if not _is_within(target.resolve(strict=False), scenario.resolve(strict=False)):
        raise RuntimeError("Safety guard rejected resolved mutation escape.")
    default = _default_user_root()
    if default is not None and target.resolve(strict=False) == default.resolve(strict=False):
        raise RuntimeError("Safety guard rejected the real default user application root.")
    return target


def _scenario_target(name: str, *parts: str) -> Path:
    return _scenario_target_for(name, *parts)


def _qa_target(filename: str) -> Path:
    root = _validate_runtime_root()
    qa_dir = _lexical(root / "_qa_artifacts")
    target = _lexical(qa_dir / filename)
    if target.parent != qa_dir:
        raise RuntimeError("Safety guard rejected QA artifact outside the approved directory.")
    _reject_reparse_components(target, anchor=root)
    if not _is_within(target.resolve(strict=False), qa_dir.resolve(strict=False)):
        raise RuntimeError("Safety guard rejected resolved QA artifact escape.")
    return target


def _qa_target_for_self_test(root: Path, filename: str) -> Path:
    root = _validate_runtime_root(root, self_test=True)
    qa_dir = _lexical(root / "_qa_artifacts")
    target = _lexical(qa_dir / filename)
    if target.parent != qa_dir:
        raise RuntimeError("Safety guard rejected QA artifact outside the approved directory.")
    _reject_reparse_components(target, anchor=root)
    if not _is_within(target.resolve(strict=False), qa_dir.resolve(strict=False)):
        raise RuntimeError("Safety guard rejected resolved QA artifact escape.")
    return target


def _reject_tree_reparse(path: Path) -> None:
    _reject_reparse_components(path, anchor=_lexical(PROJECT_ROOT))
    if not path.exists():
        return
    for current, directories, files in os.walk(path, followlinks=False):
        for name in [*directories, *files]:
            candidate = Path(current) / name
            if _is_link_or_junction(candidate):
                raise RuntimeError(f"Safety guard rejected nested reparse point: {candidate}")


def _safe_reset(name: str) -> None:
    target = _scenario_dir(name)
    if target.exists():
        _reject_tree_reparse(target)
        shutil.rmtree(target)


def _active_catalog_units() -> list[tuple[str, str, str | None, str]]:
    root = ET.parse(OFFICIAL_TS).getroot()
    units = []
    for context in root.findall("context"):
        context_name = context.findtext("name") or ""
        for message in context.findall("message"):
            translation = message.find("translation")
            if translation is None or translation.get("type") in {"obsolete", "vanished"}:
                continue
            if message.get("numerus") == "yes":
                raise RuntimeError("Step 7 QA helper does not accept unreviewed numerus units.")
            source = message.findtext("source") or ""
            disambiguation = message.findtext("comment")
            translated = "".join(translation.itertext())
            if translation.get("type") == "unfinished" or not translated.strip():
                raise RuntimeError(f"Unfinished/empty translation: {context_name} / {source}")
            units.append((context_name, source, disambiguation, translated))
    return units


def compile_qm() -> dict[str, object]:
    if _sha256(OFFICIAL_TS) != FROZEN_TS_SHA256:
        raise RuntimeError("Official TS hash differs from the frozen Step 6 value.")
    units = _active_catalog_units()
    if len(units) != 225:
        raise RuntimeError(f"Expected 225 active translations; found {len(units)}.")
    qa_qm = _qa_target(QA_QM.name)
    identity = _qa_target("qa_qm_identity.json")
    legacy = _qa_target(LEGACY_QA_QM.name)
    qa_qm.parent.mkdir(parents=True, exist_ok=True)
    legacy.unlink(missing_ok=True)
    executable = Path(sys.executable).parent / "pyside6-lrelease.exe"
    result = subprocess.run(
        [
            str(executable),
            str(OFFICIAL_TS),
            "-qm",
            str(qa_qm),
            "-fail-on-unfinished",
            "-fail-on-invalid",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    from PySide6.QtCore import QTranslator

    translator = QTranslator()
    loaded = translator.load(str(qa_qm), "", "", "")
    matched = sum(
        translator.translate(context, source, disambiguation) == translated
        for context, source, disambiguation, translated in units
    )
    if not loaded or translator.isEmpty() or matched != 225:
        raise RuntimeError(f"QTranslator audit failed: loaded={loaded}, matched={matched}/225")
    evidence = {
        "ts_sha256": _sha256(OFFICIAL_TS),
        "active": len(units),
        "finished": len(units),
        "unfinished": 0,
        "qtranslator_loaded": loaded,
        "qtranslator_matches": matched,
        "qm_size": qa_qm.stat().st_size,
        "qm_sha256": _sha256(qa_qm),
        "compiler_stdout": result.stdout.strip(),
    }
    identity.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return evidence


class FixedClock:
    def __init__(self, start: datetime = datetime(2026, 9, 1, 1, 0, tzinfo=UTC)):
        self.value = start

    def now(self) -> datetime:
        current = self.value
        self.value += timedelta(minutes=1)
        return current


class FixedIds:
    def __init__(self, prefix: str):
        self.prefix = prefix
        self.index = 0

    def new_id(self) -> str:
        self.index += 1
        return f"{self.prefix}-{self.index:04d}"


class FixedCalendar:
    def today(self) -> date:
        return date(2026, 9, 1)


def _write_preference(app_root: Path, raw: str) -> None:
    from PySide6.QtCore import QSettings

    settings = QSettings(str(app_root / "settings.ini"), QSettings.Format.IniFormat)
    settings.setFallbacksEnabled(False)
    settings.setValue("localization/preferred_language", raw)
    settings.sync()
    if settings.status() != QSettings.Status.NoError:
        raise RuntimeError("Could not write isolated manual-QA preference.")
    del settings


def _new_database(app_root: Path):
    from probability_calibration_tool.infrastructure.paths import AppPaths
    from probability_calibration_tool.persistence.database import create_connection
    from probability_calibration_tool.persistence.migrations import ensure_schema

    paths = AppPaths.from_root(app_root)
    paths.create_directories()
    with create_connection(paths.database) as connection:
        ensure_schema(connection)
    return paths


def _round_builder(paths):
    from probability_calibration_tool.application.round_service import RoundService
    from probability_calibration_tool.persistence.unit_of_work import create_uow_factory

    return RoundService(create_uow_factory(paths.database), FixedClock(), FixedIds("step7-round"))


def _complete(service, character: int, result: bool, include: bool = True) -> str:
    from probability_calibration_tool.application.commands import CalculateCommand

    view = service.calculate(CalculateCommand(character, False, 70, "2.00", "3.00"))
    service.complete_pending(view.round_id, result, include)
    return view.round_id


def _pending(service, character: int = 1) -> str:
    from probability_calibration_tool.application.commands import CalculateCommand

    return service.calculate(CalculateCommand(character, True, 70, "2.00", "3.00")).round_id


def _valid_backup(paths, token: str = "candidate") -> Path:
    from probability_calibration_tool.infrastructure.backup import BackupCategory, BackupService

    service = BackupService(
        paths,
        clock=FixedClock(datetime(2026, 9, 1, 12, 0, tzinfo=UTC)),
        ids=FixedIds(token),
        calendar=FixedCalendar(),
    )
    return service.create(BackupCategory.RECENT).path


def _clone_second_pending(database: Path, source_id: str) -> None:
    second = "step7-round-abnormal-0002"
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("DROP INDEX ux_rounds_pending")
        round_columns = [row[1] for row in connection.execute("PRAGMA table_info(rounds)")]
        select = ["?" if name == "round_id" else name for name in round_columns]
        connection.execute(
            f"INSERT INTO rounds ({','.join(round_columns)}) "
            f"SELECT {','.join(select)} FROM rounds WHERE round_id=?",
            (second, source_id),
        )
        snapshot_columns = [
            row[1] for row in connection.execute("PRAGMA table_info(round_analysis_snapshots)")
        ]
        select = ["?" if name == "round_id" else name for name in snapshot_columns]
        connection.execute(
            f"INSERT INTO round_analysis_snapshots ({','.join(snapshot_columns)}) "
            f"SELECT {','.join(select)} FROM round_analysis_snapshots WHERE round_id=?",
            (second, source_id),
        )
        connection.commit()


def _seed_database(paths, kind: str) -> dict[str, object]:
    service = _round_builder(paths)
    details: dict[str, object] = {}
    if kind == "rich":
        for index in range(100):
            _complete(service, 1, index < 50)
        _complete(service, 2, True)
        details.update(completed=101, history="character 1: 50W/50L; character 2: 1W/0L")
    elif kind == "pending":
        details["pending_round_id"] = _pending(service)
    elif kind == "multiple_pending":
        first = _pending(service)
        _clone_second_pending(paths.database, first)
        details.update(pending_round_ids=[first, "step7-round-abnormal-0002"])
    elif kind == "data_safety":
        completed = _complete(service, 1, True)
        with sqlite3.connect(paths.database) as connection:
            connection.execute("PRAGMA foreign_keys=OFF")
            connection.execute(
                "DELETE FROM round_analysis_snapshots WHERE round_id=?", (completed,)
            )
            connection.commit()
        details.update(deliberate_fault="required completed-round snapshot removed")
    elif kind == "correction":
        details["correction_candidate_round_id"] = _complete(service, 1, True)
    elif kind == "restore_normal":
        state_b_round = _complete(service, 1, True)
        candidate = _valid_backup(paths, "state-b")
        state_a_round = _complete(service, 2, False)
        details.update(
            live_state_a="2 completed rounds (characters 1 and 2)",
            candidate_state_b="1 completed round (character 1 only)",
            state_a_round_id=state_a_round,
            state_b_round_id=state_b_round,
            candidate=str(candidate),
        )
    elif kind == "restore_corrupt":
        _complete(service, 1, True)
        corrupt = paths.recent / "recent_20260901T120000.000000Z_corrupt-0001.db"
        corrupt.write_bytes(b"STEP7 deliberate corrupt backup candidate")
        details.update(corrupt_candidate=str(corrupt))
    elif kind == "emergency":
        _complete(service, 1, True)
        candidate = _valid_backup(paths, "emergency-good")
        paths.database.write_bytes(b"STEP7 deliberately damaged isolated live database")
        details.update(candidate=str(candidate), live_database="deliberately damaged")
    elif kind != "empty":
        raise ValueError(f"Unsupported database fixture: {kind}")
    return details


def _install_pack(name: str, app_root: Path, state: str) -> dict[str, str]:
    languages = _scenario_target(name, "localappdata", "ProbabilityCalibrationTool", "languages")
    languages.mkdir(parents=True, exist_ok=True)
    canonical = _scenario_target(
        name, "localappdata", "ProbabilityCalibrationTool", "languages", APP_QM_NAME
    )
    qa_qm = _qa_target(QA_QM.name)
    if state == "valid":
        shutil.copyfile(qa_qm, canonical)
        return {"canonical": str(canonical), "sha256": _sha256(canonical)}
    if state == "corrupt":
        canonical.write_bytes(b"STEP7 deliberate corrupt QM")
        return {"corrupt": str(canonical)}
    if state == "wrong_filename":
        wrong = languages / "probability_calibration_tool_zh_CN.WRONG.qm"
        shutil.copyfile(qa_qm, wrong)
        return {"wrong_filename": str(wrong)}
    if state == "wrong_location":
        wrong = app_root / APP_QM_NAME
        shutil.copyfile(qa_qm, wrong)
        return {"wrong_location": str(wrong)}
    if state == "missing":
        return {"canonical": "absent"}
    raise ValueError(f"Unsupported pack fixture: {state}")


def _database_counts(database: Path) -> dict[str, int | str]:
    try:
        with sqlite3.connect(database) as connection:
            return {
                "user_version": connection.execute("PRAGMA user_version").fetchone()[0],
                "rounds": connection.execute("SELECT count(*) FROM rounds").fetchone()[0],
                "pending": connection.execute(
                    "SELECT count(*) FROM rounds WHERE status='pending'"
                ).fetchone()[0],
                "completed": connection.execute(
                    "SELECT count(*) FROM rounds WHERE status='completed'"
                ).fetchone()[0],
                "snapshots": connection.execute(
                    "SELECT count(*) FROM round_analysis_snapshots"
                ).fetchone()[0],
            }
    except sqlite3.DatabaseError:
        return {"database": "damaged"}


def _assert_rich_history_fixture(paths) -> dict[str, dict[str, object]]:
    """Observe rich history through production validation, query, and snapshot assembly."""
    from probability_calibration_tool.application.analysis_builder import (
        build_snapshot,
        validate_prediction,
    )
    from probability_calibration_tool.application.commands import CalculateCommand
    from probability_calibration_tool.domain.enums import HistoryModelStatus
    from probability_calibration_tool.persistence.unit_of_work import create_uow_factory

    expected = {
        1: (HistoryModelStatus.VALID, True, 50, 50),
        2: (HistoryModelStatus.INSUFFICIENT, False, 1, 0),
        3: (HistoryModelStatus.NO_HISTORY, False, 0, 0),
    }
    observed: dict[str, dict[str, object]] = {}
    with create_uow_factory(paths.database)() as uow:
        for character_id, required in expected.items():
            regime = uow.regimes.get_active(character_id)
            if regime is None:
                raise RuntimeError(f"rich fixture: character {character_id} has no active regime")
            prediction = validate_prediction(
                CalculateCommand(character_id, True, 70, "2.00", "3.00")
            )
            snapshot = build_snapshot(
                prediction,
                uow.rounds.eligible_history(character_id, regime.regime_id),
                datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
            )
            actual = (
                snapshot.history_model_status,
                snapshot.history_statistically_ready,
                snapshot.history_wins,
                snapshot.history_losses,
            )
            if actual != required:
                raise RuntimeError(
                    f"rich fixture character {character_id}: actual={actual}, expected={required}"
                )
            observed[str(character_id)] = {
                "status": snapshot.history_model_status.value,
                "statistically_ready": snapshot.history_statistically_ready,
                "wins": snapshot.history_wins,
                "losses": snapshot.history_losses,
            }
    return observed


def prepare(name: str) -> dict[str, object]:
    qa_qm = _qa_target(QA_QM.name)
    if not qa_qm.is_file():
        compile_qm()
    spec = SCENARIOS[name]
    target = _scenario_dir(name)
    _safe_reset(name)
    localappdata = _scenario_target(name, "localappdata")
    app_root = _scenario_target(name, "localappdata", "ProbabilityCalibrationTool")
    app_root.mkdir(parents=True)
    _scenario_target(name, "localappdata", "ProbabilityCalibrationTool", "data")
    _scenario_target(name, "localappdata", "ProbabilityCalibrationTool", "backups")
    paths = _new_database(app_root)
    fixture = _seed_database(paths, spec.database)
    if spec.database == "rich":
        fixture["production_history_readiness"] = _assert_rich_history_fixture(paths)
    pack = _install_pack(name, app_root, spec.pack)
    _scenario_target(name, "localappdata", "ProbabilityCalibrationTool", "settings.ini")
    _write_preference(app_root, spec.preference)
    evidence = {
        "status": "PREPARED_ONLY_MANUAL_ACCEPTANCE_NOT_STARTED",
        "scenario": name,
        "spec": asdict(spec),
        "runtime_root": str(target),
        "localappdata": str(localappdata),
        "production_app_root": str(app_root),
        "database": str(paths.database),
        "database_counts": _database_counts(paths.database),
        "pack": pack,
        "fixture": fixture,
        "real_entrypoint": "python -m probability_calibration_tool",
        "launch_command": launch_command(name),
        "reset_command": f"uv run python tools/localization_step7_prepare.py reset {name}",
    }
    _scenario_target(name, "scenario.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return evidence


def launch_command(name: str) -> str:
    localappdata = _scenario_target(name, "localappdata")
    relative = localappdata.relative_to(PROJECT_ROOT)
    return (
        "$env:PYTHONPATH='src'; "
        f"$env:LOCALAPPDATA=(Resolve-Path '{relative}').Path; "
        "uv run python -m probability_calibration_tool"
    )


def mutate(name: str, action: str) -> dict[str, str]:
    _scenario_target(name, "localappdata", "ProbabilityCalibrationTool")
    if action == "remove-pack" and name == "confirm_pack_loss":
        path = _scenario_target(
            name, "localappdata", "ProbabilityCalibrationTool", "languages", APP_QM_NAME
        )
        path.unlink(missing_ok=False)
        return {"action": action, "removed": str(path), "recovery": f"prepare {name}"}
    if action == "restore-pack" and name == "missing_pack":
        path = _scenario_target(
            name, "localappdata", "ProbabilityCalibrationTool", "languages", APP_QM_NAME
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(_qa_target(QA_QM.name), path)
        return {
            "action": action,
            "installed": str(path),
            "sha256": _sha256(path),
            "recovery": f"prepare {name}",
        }
    if action == "expire-candidate" and name in {"restore_invalid", "emergency_invalid"}:
        recent = _scenario_target(
            name, "localappdata", "ProbabilityCalibrationTool", "backups", "recent"
        )
        candidates = sorted(recent.glob("recent_*.db"))
        if len(candidates) != 1:
            raise RuntimeError(f"Expected exactly one Recent candidate; found {len(candidates)}.")
        candidates[0].unlink()
        return {
            "action": action,
            "removed": str(candidates[0]),
            "recovery": f"prepare {name}",
        }
    if action == "remove-pending" and name in {
        "recovery_no_pending",
        "recovery_no_pending_zh",
    }:
        database = _scenario_target(
            name, "localappdata", "ProbabilityCalibrationTool", "data", "probability.db"
        )
        with sqlite3.connect(database) as connection:
            connection.execute("PRAGMA foreign_keys=ON")
            pending = connection.execute(
                "SELECT round_id FROM rounds WHERE status='pending'"
            ).fetchall()
            if len(pending) != 1:
                raise RuntimeError(f"Expected one pending round; found {len(pending)}.")
            round_id = pending[0][0]
            connection.execute("DELETE FROM round_analysis_snapshots WHERE round_id=?", (round_id,))
            connection.execute("DELETE FROM rounds WHERE round_id=?", (round_id,))
            connection.commit()
        return {
            "action": action,
            "removed": round_id,
            "recovery": f"prepare {name}",
        }
    if action == "remove-recovery-snapshot" and name in {
        "recovery_stale_en",
        "recovery_stale_zh",
    }:
        database = _scenario_target(
            name, "localappdata", "ProbabilityCalibrationTool", "data", "probability.db"
        )
        with sqlite3.connect(database) as connection:
            pending = connection.execute(
                "SELECT round_id FROM rounds WHERE status='pending'"
            ).fetchall()
            if len(pending) != 1:
                raise RuntimeError(f"Expected one pending round; found {len(pending)}.")
            round_id = pending[0][0]
            deleted = connection.execute(
                "DELETE FROM round_analysis_snapshots WHERE round_id=?", (round_id,)
            ).rowcount
            connection.commit()
        if deleted != 1:
            raise RuntimeError(f"Expected one Recovery snapshot; deleted {deleted}.")
        return {
            "action": action,
            "removed": round_id,
            "recovery": f"prepare {name}",
        }
    raise ValueError(f"Mutation {action!r} is not allowed for scenario {name!r}.")


def _set_launch_environment(name: str, *, offscreen: bool = False) -> None:
    target = _scenario_dir(name)
    localappdata = target / "localappdata"
    if not localappdata.is_dir():
        raise RuntimeError(f"Scenario is not prepared: {name}")
    os.environ["LOCALAPPDATA"] = str(localappdata)
    os.environ["PYTHONPATH"] = str(SOURCE_ROOT)
    if offscreen:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"


class _FailingWriter:
    def setFallbacksEnabled(self, _enabled):
        return None

    def setAtomicSyncRequired(self, _required):
        return None

    def setValue(self, _key, _value):
        return None

    def remove(self, _key):
        return None

    def sync(self):
        return None

    def status(self):
        from PySide6.QtCore import QSettings

        return QSettings.Status.AccessError


class _SaveFailureFactory:
    """Odd calls are real reads; even calls are deterministic no-write failures."""

    def __init__(self):
        self.calls = 0

    def __call__(self, path, format_):
        from PySide6.QtCore import QSettings

        self.calls += 1
        return QSettings(path, format_) if self.calls % 2 else _FailingWriter()


def _fault_main(name: str, *, auto_exit_ms: int | None = None) -> int:
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    from probability_calibration_tool.application.startup_service import StartupService
    from probability_calibration_tool.bootstrap import main
    from probability_calibration_tool.desktop_host import DesktopHost
    from probability_calibration_tool.infrastructure.backup import BackupCategory
    from probability_calibration_tool.infrastructure.error_reporting import WarningCode
    from probability_calibration_tool.localization import initialize_localization

    spec = SCENARIOS[name]
    print("TEST-ONLY MANUAL QA FAULT INJECTION", flush=True)
    print(f"scenario={name}; seam={spec.fault}", flush=True)

    class FaultHost(DesktopHost):
        def show_initial_state(self):
            super().show_initial_state()
            if spec.fault in {"unexpected", "unexpected-with-warning"}:
                rounds = self.session.workflow._target._rounds._rounds

                def fail(_command):
                    raise RuntimeError("PRIVATE STEP7 DIAGNOSTIC: SQL=C:/private/manual-fixture.db")

                rounds.calculate = fail
                print("injected seam=RoundService.calculate", flush=True)
            elif spec.fault == "recent-backup":
                original = self.backup.create

                def fail_backup(category, reason=None):
                    if category == BackupCategory.RECENT:
                        raise OSError("PRIVATE STEP7 DIAGNOSTIC: injected Recent backup failure")
                    return original(category, reason)

                self.backup.create = fail_backup
                print("injected seam=BackupService.create(RECENT)", flush=True)

    localization_factory = initialize_localization
    startup_factory = StartupService
    if spec.fault == "settings-save":

        def localization_factory(app, root):
            context = initialize_localization(app, root)
            context._settings_factory = _SaveFailureFactory()
            print("injected seam=LocalizationContext._settings_factory writer", flush=True)
            return context

    warning_faults = {
        "data-safety-warning": WarningCode.BACKUP_OVER_RETENTION,
        "unexpected-with-warning": WarningCode.BACKUP_OVER_RETENTION,
        "over-retention-warning": WarningCode.BACKUP_OVER_RETENTION,
        "quarantine-warning": WarningCode.QUARANTINE_COPY_FAILED,
    }
    if spec.fault in warning_faults:

        class WarningStartup(StartupService):
            def start(self):
                runtime = super().start()
                runtime.result = replace(
                    runtime.result,
                    warnings=(*runtime.result.warnings, warning_faults[spec.fault]),
                )
                print(
                    "injected seam=RuntimeContext.result.warnings"
                    f"+WarningCode.{warning_faults[spec.fault].name}",
                    flush=True,
                )
                return runtime

        startup_factory = WarningStartup

    event_loop = None
    if auto_exit_ms is not None:

        def event_loop(app: QApplication, _host: DesktopHost) -> int:
            QTimer.singleShot(auto_exit_ms, app.quit)
            return app.exec()

    return main(
        [],
        host_factory=FaultHost,
        startup_factory=startup_factory,
        localization_factory=localization_factory,
        event_loop=event_loop,
    )


def launch(name: str) -> int:
    _set_launch_environment(name)
    spec = SCENARIOS[name]
    print(f"isolated_LOCALAPPDATA={os.environ['LOCALAPPDATA']}", flush=True)
    print(f"production_root={Path(os.environ['LOCALAPPDATA']) / 'ProbabilityCalibrationTool'}")
    if spec.fault:
        return _fault_main(name)
    return subprocess.call(
        [sys.executable, "-m", "probability_calibration_tool"],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONPATH": str(SOURCE_ROOT)},
    )


def smoke_launch(name: str) -> int:
    _set_launch_environment(name, offscreen=True)
    spec = SCENARIOS[name]
    if spec.fault:
        return _fault_main(name, auto_exit_ms=150)
    script = (
        "import runpy; "
        "from PySide6.QtWidgets import QApplication; "
        "from PySide6.QtCore import QTimer; "
        "app=QApplication([]); QTimer.singleShot(150, app.quit); "
        "runpy.run_module('probability_calibration_tool', run_name='__main__')"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONPATH": str(SOURCE_ROOT), "QT_QPA_PLATFORM": "offscreen"},
        check=False,
    )
    return result.returncode


def probe_save_failure() -> dict[str, object]:
    """Exercise the real dialog/save presentation offscreen; this is not visual acceptance."""
    from PySide6.QtWidgets import QApplication

    from probability_calibration_tool.localization import (
        Language,
        initialize_localization,
        read_preference,
    )
    from probability_calibration_tool.ui.language_dialog import LanguageDialog

    name = "save_failure"
    _set_launch_environment(name, offscreen=True)
    app_root = _scenario_dir(name) / "localappdata" / "ProbabilityCalibrationTool"
    app = QApplication.instance() or QApplication([])
    context = initialize_localization(app, app_root)
    context._settings_factory = _SaveFailureFactory()
    before = read_preference(context.settings_path).raw_value
    dialog = LanguageDialog(context)
    dialog.choices[Language.ZH_CN].setChecked(True)
    dialog._confirm()
    after = read_preference(context.settings_path).raw_value
    result = {
        "scenario": name,
        "production_dialog": type(dialog).__name__,
        "message": dialog.message.text(),
        "preference_before": before,
        "preference_after": after,
        "dialog_still_open": dialog.result() == 0,
    }
    dialog.close()
    if (
        before != "en"
        or after != "en"
        or not result["dialog_still_open"]
        or "could not be saved" not in str(result["message"])
    ):
        raise RuntimeError(f"Save-failure presentation probe failed: {result}")
    return result


EXPECTED_DISPOSITIONS = {
    "pending": "ready_recovery",
    "multiple_pending": "recovery_error",
    "data_safety": "data_safety_error",
    "emergency": "emergency_recovery",
}


def probe(name: str) -> dict[str, object]:
    from probability_calibration_tool.application.startup_service import StartupService
    from probability_calibration_tool.infrastructure.paths import AppPaths
    from probability_calibration_tool.localization import (
        PackPreflightStatus,
        PreferenceState,
        preflight_app_pack,
        read_preference,
    )

    target = _scenario_dir(name)
    app_root = target / "localappdata" / "ProbabilityCalibrationTool"
    paths = AppPaths.from_root(app_root)
    with StartupService(paths).start() as runtime:
        disposition = runtime.result.disposition.value
    expected = EXPECTED_DISPOSITIONS.get(SCENARIOS[name].database, "ready_draft")
    preference = read_preference(app_root / "settings.ini")
    pack = preflight_app_pack(app_root / "languages")
    if disposition != expected:
        raise RuntimeError(f"{name}: expected {expected}, got {disposition}")
    if SCENARIOS[name].pack == "valid" and pack.status != PackPreflightStatus.VALID:
        raise RuntimeError(f"{name}: valid pack failed preflight: {pack.status}")
    if (
        SCENARIOS[name].preference == "INVALID_qa"
        and preference.state != PreferenceState.SAVED_INVALID
    ):
        raise RuntimeError(f"{name}: invalid preference was not preserved")
    rich_history = None
    if SCENARIOS[name].database == "rich":
        rich_history = _assert_rich_history_fixture(paths)
    return {
        "scenario": name,
        "disposition": disposition,
        "expected_disposition": expected,
        "preference_state": preference.state.value,
        "preferred": preference.preferred_language.value,
        "pack_preflight": pack.status.value,
        "database_counts": _database_counts(paths.database),
        "production_history_readiness": rich_history,
    }


def safety_guard_self_check() -> dict[str, bool | str]:
    results: dict[str, bool | str] = {}
    try:
        _scenario_dir("..")
    except ValueError:
        results["unknown_name_rejected"] = True
    else:
        results["unknown_name_rejected"] = False
    try:
        mutate("healthy_en", "expire-candidate")
    except ValueError:
        results["unauthorized_mutation_rejected"] = True
    else:
        results["unauthorized_mutation_rejected"] = False

    runtime = _validate_runtime_root()
    results["runtime_is_project_controlled"] = runtime.parent == _lexical(PROJECT_ROOT / "outputs")
    safety_base = _lexical(runtime / "_safety_selftest")
    test_root = safety_base / "controlled_root"
    outside = safety_base / "outside_targets"

    if safety_base.exists():
        _reject_tree_reparse(safety_base)
        shutil.rmtree(safety_base)
    test_root.mkdir(parents=True)
    outside.mkdir(parents=True)

    def make_reparse(link: Path, target: Path) -> str:
        target.mkdir(parents=True, exist_ok=True)
        try:
            os.symlink(target, link, target_is_directory=True)
            return "symlink"
        except OSError:
            completed = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode:
                raise RuntimeError(
                    "Could not create disposable safety-test symlink or junction: "
                    + completed.stderr
                )
            return "junction"

    def remove_reparse(link: Path) -> None:
        if link.is_symlink():
            link.unlink()
        else:
            os.rmdir(link)

    def expect_rejected(key: str, operation) -> None:
        try:
            operation()
        except RuntimeError:
            results[key] = True
        else:
            results[key] = False

    allowlist = {"probe"}
    methods = set()
    scenario_link = test_root / "probe"
    methods.add(make_reparse(scenario_link, outside / "scenario"))
    expect_rejected(
        "scenario_reparse_escape_rejected",
        lambda: _scenario_dir_for("probe", root=test_root, allowlist=allowlist, self_test=True),
    )
    remove_reparse(scenario_link)

    for component, parts in (
        (
            "languages",
            ("localappdata", "ProbabilityCalibrationTool", "languages", APP_QM_NAME),
        ),
        (
            "backup",
            (
                "localappdata",
                "ProbabilityCalibrationTool",
                "backups",
                "recent",
                "recent_candidate.db",
            ),
        ),
        (
            "data",
            ("localappdata", "ProbabilityCalibrationTool", "data", "probability.db"),
        ),
    ):
        scenario = test_root / "probe"
        if scenario.exists():
            shutil.rmtree(scenario)
        reparse_parent = scenario.joinpath(*parts[:-2])
        reparse_parent.mkdir(parents=True)
        link = reparse_parent / parts[-2]
        methods.add(make_reparse(link, outside / component))
        expect_rejected(
            f"nested_{component}_reparse_rejected",
            lambda parts=parts: _scenario_target_for(
                "probe",
                *parts,
                root=test_root,
                allowlist=allowlist,
                self_test=True,
            ),
        )
        remove_reparse(link)
        shutil.rmtree(scenario)

    qa_link = test_root / "_qa_artifacts"
    methods.add(make_reparse(qa_link, outside / "qa"))
    expect_rejected(
        "qa_artifact_reparse_escape_rejected",
        lambda: _qa_target_for_self_test(test_root, "candidate.qm"),
    )
    remove_reparse(qa_link)
    results["reparse_mechanism"] = "+".join(sorted(methods))

    _reject_tree_reparse(safety_base)
    shutil.rmtree(safety_base)
    boolean_results = {key: value for key, value in results.items() if isinstance(value, bool)}
    if not all(boolean_results.values()):
        raise RuntimeError(f"Safety guard self-check failed: {results}")
    return results


def _markdown_rows(text: str, start: str, end: str) -> list[list[str]]:
    section = text.split(start, 1)[1].split(end, 1)[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0] != "ID":
            rows.append(cells)
    return rows


def _manifest_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] in SCENARIOS:
            rows[cells[0]] = cells
    return rows


def traceability_check() -> dict[str, object]:
    checklist_text = CHECKLIST.read_text(encoding="utf-8")
    checklist_rows = []
    for line in checklist_text.splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and re.fullmatch(r"(?:A-ENV|B-EN|C-ZH|D-LC|E-SP|F-EV)-\d{2}", cells[0]):
            checklist_rows.append(cells)
    ids = [row[0] for row in checklist_rows]
    requirements = {row[0]: row[5] for row in checklist_rows}
    results = {row[0]: row[6] for row in checklist_rows}
    expected_gate_totals = {
        "A": (7, 7, 0, 7),
        "B": (15, 15, 0, 15),
        "C": (15, 15, 0, 15),
        "D": (16, 14, 2, 16),
        "E": (8, 8, 0, 8),
        "F": (2, 2, 0, 2),
    }
    if len(ids) != 63 or len(set(ids)) != 63:
        raise RuntimeError(
            f"Checklist identity gate failed: rows={len(ids)}, unique={len(set(ids))}"
        )
    deleted_present = sorted(DELETED_DPI_IDS & set(ids))
    if deleted_present:
        raise RuntimeError(f"Deleted DPI checklist IDs remain: {deleted_present}")
    if set(results.values()) != {"NOT_RUN"}:
        raise RuntimeError("Every preparation checklist result must remain NOT_RUN.")
    requirement_counts = {
        requirement: sum(value == requirement for value in requirements.values())
        for requirement in sorted(set(requirements.values()))
    }
    if requirement_counts != {"MANDATORY": 61, "N/A_ALLOWED": 2}:
        raise RuntimeError(f"Checklist requirement counts changed: {requirement_counts}")
    na_allowed_ids = {item for item in ids if requirements[item] == "N/A_ALLOWED"}
    if na_allowed_ids != {"D-LC-11", "D-LC-14"}:
        raise RuntimeError(
            "N/A_ALLOWED identity changed: "
            f"actual={sorted(na_allowed_ids)}, expected=['D-LC-11', 'D-LC-14']"
        )
    if any(results[item] != "NOT_RUN" for item in na_allowed_ids):
        raise RuntimeError("N/A_ALLOWED rows must remain NOT_RUN after preparation.")
    totals_section = checklist_text.split("## Preparation totals", 1)[1]
    expected_preparation_totals = {
        "A — Environment & Localization Identity": (7, 7, 0, 7),
        "B — English Built-in Regression": (15, 15, 0, 15),
        "C — Official zh_CN Presentation": (15, 15, 0, 15),
        "D — Language Lifecycle / Fallback": (16, 14, 2, 16),
        "E — Localization-Sensitive Safety / Priority Presentation": (8, 8, 0, 8),
        "F — Evidence / Defect Closure": (2, 2, 0, 2),
        "Total": (63, 61, 2, 63),
    }
    preparation_totals: dict[str, tuple[int, int, int, int]] = {}
    for line in totals_section.splitlines():
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0] == "Gate":
            continue
        if len(cells) != 5:
            raise RuntimeError(f"Malformed preparation total row: {line}")
        try:
            preparation_totals[cells[0]] = tuple(int(value) for value in cells[1:])
        except ValueError as error:
            raise RuntimeError(f"Non-numeric preparation total row: {line}") from error
    if preparation_totals != expected_preparation_totals:
        raise RuntimeError(
            "Checklist preparation totals changed: "
            f"actual={preparation_totals}, expected={expected_preparation_totals}"
        )
    checklist_by_id = {row[0]: row for row in checklist_rows}
    manual_ids = {item for item in ids if item[0] in {"B", "C", "D", "E", "F"}}
    legacy_scaling = {
        item: checklist_by_id[item][3]
        for item in manual_ids
        if checklist_by_id[item][3] != FORMAL_MANUAL_SCALING
    }
    if legacy_scaling:
        raise RuntimeError(
            f"Formal manual route does not use {FORMAL_MANUAL_SCALING}: {legacy_scaling}"
        )
    env03 = checklist_by_id["A-ENV-03"]
    if (
        env03[3] != FORMAL_MANUAL_SCALING
        or "2560×1600 @ 150%" not in env03[4]
        or "minimum practical" not in env03[4]
        or "maximized" not in env03[4]
    ):
        raise RuntimeError("A-ENV-03 does not state the frozen 150% certification baseline.")

    actual_gate_totals = {}
    for gate, expected in expected_gate_totals.items():
        gate_ids = [item for item in ids if item.startswith(f"{gate}-")]
        actual_gate_totals[gate] = (
            len(gate_ids),
            sum(requirements[item] == "MANDATORY" for item in gate_ids),
            sum(requirements[item] == "N/A_ALLOWED" for item in gate_ids),
            sum(results[item] == "NOT_RUN" for item in gate_ids),
        )
        if actual_gate_totals[gate] != expected:
            raise RuntimeError(
                f"Gate {gate} totals changed: actual={actual_gate_totals[gate]}, expected={expected}"
            )

    guide = EXECUTION_GUIDE.read_text(encoding="utf-8")
    trace_rows = _markdown_rows(
        guide,
        "## Appendix A - Formal checklist traceability",
        "## Final human handoff rule",
    )
    traces = {row[0]: row for row in trace_rows}
    mandatory = {item for item in ids if requirements[item] == "MANDATORY"}
    if set(traces) != set(ids):
        raise RuntimeError(
            "Guide traceability must contain exactly all checklist IDs: "
            f"missing={sorted(set(ids) - set(traces))}, extra={sorted(set(traces) - set(ids))}"
        )
    if "localization_step7_manual\\trace\\" in guide or "+## Appendix A" in guide:
        raise RuntimeError("Guide contains a phantom trace path or malformed Appendix A heading.")
    if "100%" in checklist_text or "125%" in checklist_text:
        raise RuntimeError("Checklist retains a non-150% formal route.")
    deleted_references = {
        item for item in DELETED_DPI_IDS if item in guide or item in checklist_text
    }
    if deleted_references:
        raise RuntimeError(
            f"Deleted DPI IDs remain in checklist or guide: {sorted(deleted_references)}"
        )

    expected_contexts = {
        "AppShell",
        "Round",
        "Analysis",
        "Maintenance",
        "Correction",
        "Restore",
        "Recovery",
        "StartupSafety",
        "Errors",
        "Characters",
        "DomainLabels",
        "Localization",
    }
    observed_contexts: set[str] = set()
    for item, row in traces.items():
        if len(row) != 4:
            raise RuntimeError(f"Malformed traceability row: {item}")
        route = row[1]
        for route_name in route.split(" + "):
            if route_name != "ENVIRONMENT" and route_name not in SCENARIOS:
                raise RuntimeError(f"{item}: route is not a prepared scenario: {route_name!r}")
        observed_contexts.update(
            context.strip() for context in row[3].split(";") if context.strip() != "—"
        )
    if observed_contexts != expected_contexts:
        raise RuntimeError(
            f"Human localization-context coverage changed: actual={observed_contexts}, "
            f"expected={expected_contexts}"
        )

    characters = (
        "以撒",
        "抹大拉",
        "该隐",
        "犹大",
        "???",
        "夏娃",
        "参孙",
        "阿撒泻勒",
        "拉撒路",
        "伊甸",
        "游魂",
        "莉莉丝",
        "店主",
        "亚玻伦",
        "遗骸",
        "伯大尼",
        "雅各和以扫",
        "堕化以撒",
        "堕化抹大拉",
        "堕化该隐",
        "堕化犹大",
        "堕化???",
        "堕化夏娃",
        "堕化参孙",
        "堕化阿撒泻勒",
        "堕化拉撒路",
        "堕化伊甸",
        "堕化游魂",
        "堕化莉莉丝",
        "堕化店主",
        "堕化亚玻伦",
        "堕化遗骸",
        "堕化伯大尼",
        "堕化雅各",
    )
    character_description = checklist_by_id["C-ZH-02"][4]
    character_prefix = "All 34 mappings: "
    if not character_description.startswith(character_prefix):
        raise RuntimeError("C-ZH-02 does not begin with the required 34-mapping delimiter.")
    actual_characters = tuple(character_description.removeprefix(character_prefix).split("、"))
    if actual_characters != characters:
        raise RuntimeError(
            f"C-ZH-02 character sequence changed: actual={actual_characters}, expected={characters}"
        )
    if len(actual_characters) != 34 or len(set(actual_characters)) != 34:
        raise RuntimeError("C-ZH-02 must contain exactly 34 unique character mappings.")

    context_row = traces["C-ZH-14"]
    expected_context_sequence = (
        "AppShell",
        "Round",
        "Analysis",
        "Maintenance",
        "Correction",
        "Restore",
        "Recovery",
        "StartupSafety",
        "Errors",
        "Characters",
        "DomainLabels",
        "Localization",
    )
    actual_context_sequence = tuple(context.strip() for context in context_row[3].split(";"))
    if actual_context_sequence != expected_context_sequence:
        raise RuntimeError(
            "C-ZH-14 must declare the exact 12-context sequence: "
            f"actual={actual_context_sequence}, expected={expected_context_sequence}"
        )

    lifecycle_mandatory = {f"D-LC-{number:02}" for number in range(1, 17)} - {"D-LC-11", "D-LC-14"}
    if any(requirements[item] != "MANDATORY" for item in lifecycle_mandatory):
        raise RuntimeError("Mandatory lifecycle core coverage is incomplete.")
    safety_ids = {item for item in ids if item.startswith("E-SP-")}
    if len(safety_ids) != 8 or any(requirements[item] != "MANDATORY" for item in safety_ids):
        raise RuntimeError(
            "Mandatory localization-sensitive safety/priority coverage is incomplete."
        )
    if any(
        phrase in (checklist_text + guide)
        for phrase in (
            "perform the real Correction",
            "real Correction transaction",
            "real Normal Restore transaction",
            "real Emergency Restore transaction",
        )
    ):
        raise RuntimeError(
            "Formal localization contract reintroduces a destructive business transaction."
        )

    manifest = _manifest_rows(SCENARIO_MANIFEST.read_text(encoding="utf-8"))
    if set(manifest) != set(SCENARIOS):
        raise RuntimeError("Scenario manifest keys do not exactly match the preparer scenarios.")
    manifest_text = SCENARIO_MANIFEST.read_text(encoding="utf-8")
    manifest_deleted_references = sorted(item for item in DELETED_DPI_IDS if item in manifest_text)
    if manifest_deleted_references:
        raise RuntimeError(
            f"Scenario manifest retains deleted DPI IDs: {manifest_deleted_references}"
        )
    expected_data_safety_route = (
        "data_safety_en",
        "data_safety",
        "data_safety_fallback",
        "data_safety_warning_en",
        "data_safety_warning_zh",
    )
    data_safety_route = tuple(traces["E-SP-02"][1].split(" + "))
    if data_safety_route != expected_data_safety_route:
        raise RuntimeError(
            "E-SP-02 route must include the exact competing-condition scenarios: "
            f"actual={data_safety_route}, expected={expected_data_safety_route}"
        )
    fallback_spec = SCENARIOS["data_safety_fallback"]
    if not (
        fallback_spec.database == "data_safety"
        and fallback_spec.preference == "zh_CN"
        and fallback_spec.effective == "en"
        and fallback_spec.pack == "missing"
    ):
        raise RuntimeError(
            "E-SP-02 fallback route is not Data Safety versus a localization notice."
        )
    for scenario_name, language in (
        ("data_safety_warning_en", "en"),
        ("data_safety_warning_zh", "zh_CN"),
    ):
        spec = SCENARIOS[scenario_name]
        if (
            spec.database != "data_safety"
            or spec.fault != "data-safety-warning"
            or spec.effective != language
        ):
            raise RuntimeError(
                f"E-SP-02 {scenario_name} is not the required warning-priority route."
            )
    for scenario_name in traces["E-SP-07"][1].split(" + "):
        spec = SCENARIOS[scenario_name]
        if spec.fault != "unexpected-with-warning":
            raise RuntimeError("E-SP-07 is not an error-over-warning presentation route.")

    return {
        "checklist_rows": len(ids),
        "unique_ids": len(set(ids)),
        "result_counts": {"NOT_RUN": len(results), "PASS": 0, "FAIL": 0, "N/A": 0},
        "requirement_counts": requirement_counts,
        "preparation_totals": preparation_totals,
        "mandatory_traceability": f"{len(mandatory)}/{len(mandatory)}",
        "gate_totals": actual_gate_totals,
        "localization_contexts": len(observed_contexts),
        "zh_character_mappings": len(characters),
        "na_allowed_ids": sorted(na_allowed_ids),
        "B-EN-12_route": traces["B-EN-12"][1],
        "E-SP-02_route": traces["E-SP-02"][1],
        "C-ZH-14_contexts": len(actual_context_sequence),
        "formal_scaling": FORMAL_MANUAL_SCALING,
        "legacy_100_routes": 0,
        "legacy_125_routes": 0,
        "deleted_dpi_ids_present": 0,
        "fallback_counted_as_zh_CN": 0,
        "manual_scope": "localization_delta_only",
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("compile-qm", help="strictly compile and audit the frozen official TS")
    prepare_parser = sub.add_parser("prepare", help="reset then prepare one/all scenarios")
    prepare_parser.add_argument("scenario", choices=[*SCENARIOS, "all"])
    reset_parser = sub.add_parser("reset", help="safely remove one/all controlled scenarios")
    reset_parser.add_argument("scenario", choices=[*SCENARIOS, "all"])
    show_parser = sub.add_parser("show", help="print paths and exact launch command")
    show_parser.add_argument("scenario", choices=SCENARIOS)
    launch_parser = sub.add_parser("launch", help="launch the real production GUI")
    launch_parser.add_argument("scenario", choices=SCENARIOS)
    probe_parser = sub.add_parser("probe", help="nonvisual isolated startup/fixture smoke")
    probe_parser.add_argument("scenario", choices=SCENARIOS)
    smoke_parser = sub.add_parser("smoke-launch", help="offscreen real-entrypoint smoke only")
    smoke_parser.add_argument("scenario", choices=SCENARIOS)
    mutate_parser = sub.add_parser("mutate", help="apply one whitelisted in-session mutation")
    mutate_parser.add_argument("scenario", choices=SCENARIOS)
    mutate_parser.add_argument(
        "action",
        choices=[
            "remove-pack",
            "restore-pack",
            "expire-candidate",
            "remove-pending",
            "remove-recovery-snapshot",
        ],
    )
    sub.add_parser("safety-check", help="exercise refusal guards without changing scenarios")
    sub.add_parser("traceability-check", help="validate checklist/guide count and route contracts")
    sub.add_parser(
        "probe-save-failure",
        help="offscreen exercise of the real Language dialog failure path",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.command == "compile-qm":
        result = compile_qm()
    elif args.command == "prepare":
        names = SCENARIOS if args.scenario == "all" else (args.scenario,)
        result = {name: prepare(name) for name in names}
    elif args.command == "reset":
        names = SCENARIOS if args.scenario == "all" else (args.scenario,)
        for name in names:
            _safe_reset(name)
        result = {"reset": list(names), "approved_root": str(RUNTIME_ROOT)}
    elif args.command == "show":
        target = _scenario_dir(args.scenario)
        result = {
            "scenario": args.scenario,
            "runtime_root": str(target),
            "localappdata": str(target / "localappdata"),
            "production_root": str(target / "localappdata" / "ProbabilityCalibrationTool"),
            "launch": launch_command(args.scenario),
        }
    elif args.command == "launch":
        return launch(args.scenario)
    elif args.command == "probe":
        result = probe(args.scenario)
    elif args.command == "smoke-launch":
        return smoke_launch(args.scenario)
    elif args.command == "mutate":
        result = mutate(args.scenario, args.action)
    elif args.command == "safety-check":
        result = safety_guard_self_check()
    elif args.command == "traceability-check":
        result = traceability_check()
    elif args.command == "probe-save-failure":
        result = probe_save_failure()
    else:
        raise AssertionError(args.command)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(SOURCE_ROOT))
    raise SystemExit(main())
