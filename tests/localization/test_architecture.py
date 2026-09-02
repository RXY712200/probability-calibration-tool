import ast
import hashlib
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest
from PySide6.QtCore import QSettings

from probability_calibration_tool import localization as loc
from probability_calibration_tool.application import CalculateCommand, RoundService
from probability_calibration_tool.application.ports import SystemClock, UUIDGenerator
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.infrastructure.backup import BackupCategory, BackupService
from probability_calibration_tool.infrastructure.paths import AppPaths
from probability_calibration_tool.persistence.schema import SCHEMA_VERSION

from .helpers import App, SettingsPlan, Translator, dummy_pack, write_preference

SOURCE = Path(__file__).parents[2] / "src" / "probability_calibration_tool"


def test_localization_has_only_stdlib_qtcore_dependencies():
    tree = ast.parse((SOURCE / "localization.py").read_text(encoding="utf-8"))
    allowed = {"logging", "collections.abc", "dataclasses", "enum", "pathlib", "PySide6.QtCore"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            imported.add(node.module)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in {"clear", "isWritable", "mkdir", "glob", "rglob"}
    assert imported <= allowed


@pytest.mark.parametrize("layer", ["core", "domain", "application", "persistence"])
def test_business_layers_have_no_localization_dependencies_or_calls(layer):
    files = list((SOURCE / layer).rglob("*.py"))
    assert files
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.name for alias in node.names]
                if isinstance(node, ast.ImportFrom):
                    names.append(node.module or "")
                assert not any(
                    name.startswith("PySide6")
                    or "localization" in name.split(".")
                    or name in {"QTranslator", "QCoreApplication"}
                    for name in names
                ), (path, node.lineno)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"translate", "tr"}, (path, node.lineno)


def _assert_no_presentation_translator_lifecycle(tree, path):
    # UI translation and read-only injected context references are legitimate.
    # Only process translator/context construction and activation belong elsewhere.
    aliases = {
        alias.asname: alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
        if alias.asname
    }
    lifecycle_calls = {
        "QTranslator",
        "LocalizationContext",
        "initialize_localization",
        "english_context",
        "installTranslator",
        "removeTranslator",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                name = aliases.get(node.func.id, node.func.id)
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            else:
                continue
            assert name not in lifecycle_calls, (path, node.lineno, name)


def test_ui_and_desktop_host_do_not_own_translator_lifecycle():
    # G20 is a Step 3 diff/hash audit, not a permanent ban on UI localization.
    paths = [SOURCE / "desktop_host.py", *list((SOURCE / "ui").rglob("*.py"))]
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        _assert_no_presentation_translator_lifecycle(tree, path)


def test_presentation_contract_allows_translation_and_readonly_context_dependency():
    # Parsed examples only: no Step 4 production code or UI is implemented here.
    tree = ast.parse("""
from PySide6.QtCore import QCoreApplication, QTranslator
from probability_calibration_tool.localization import LocalizationContext
from probability_calibration_tool.ui.localization import format_label

class Presentation:
    def __init__(self, localization: LocalizationContext):
        self.localization = localization

    def labels(self):
        return (
            QCoreApplication.translate("Presentation", "Language"),
            self.tr("Language"),
            format_label(self.localization.effective_language),
        )
""")
    _assert_no_presentation_translator_lifecycle(tree, "read-only presentation example")


@pytest.mark.parametrize(
    "source",
    [
        "from PySide6.QtCore import QTranslator; translator = QTranslator()",
        "from PySide6 import QtCore; translator = QtCore.QTranslator()",
        "from PySide6.QtCore import QTranslator as Translator; translator = Translator()",
        "app.installTranslator(translator)",
        "app.removeTranslator(translator)",
        "from probability_calibration_tool import localization; localization.initialize_localization(app, root)",
        "from probability_calibration_tool.localization import initialize_localization as init; init(app, root)",
        "from probability_calibration_tool.localization import english_context; english_context(root)",
        "from probability_calibration_tool.localization import LocalizationContext as Context; self.localization = Context()",
    ],
)
def test_presentation_contract_rejects_translator_or_context_lifecycle(source):
    with pytest.raises(AssertionError):
        _assert_no_presentation_translator_lifecycle(ast.parse(source), "ownership violation")


@pytest.mark.parametrize("failure", ["default", "missing", "invalid", "read_error"])
def test_initialization_creates_no_business_files_or_settings(tmp_path, failure):
    root = tmp_path / "fresh-product"
    if failure in ("missing", "invalid"):
        write_preference(root, "zh_CN")
        if failure == "invalid":
            dummy_pack(root)
    before = {
        path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()
    }
    kwargs = (
        {"settings_factory": SettingsPlan({"status": QSettings.Status.AccessError})}
        if failure == "read_error"
        else {}
    )
    context = loc.initialize_localization(App(), root, **kwargs)
    assert context.effective_language == loc.Language.EN
    after = {
        path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()
    }
    assert after == before
    paths = AppPaths.from_root(root)
    assert not paths.database.exists() and not (root / "backups").exists()
    if failure in ("default", "read_error"):
        assert not root.exists()


@pytest.fixture
def populated_database(tmp_path):
    paths = AppPaths.from_root(tmp_path / "business")
    with StartupService(paths).start() as runtime:
        rounds = RoundService(runtime.uow_factory(), SystemClock(), UUIDGenerator())
        view = rounds.calculate(CalculateCommand(1, False, 70, "2.00", "3.00"))
        rounds.complete_pending(view.round_id, True, True)
        backup = BackupService(paths, logger=runtime.logger)
        backup.create(BackupCategory.RECENT)
        backup.create(BackupCategory.SAFETY, reason="pre_history_correction")
    return paths


@pytest.mark.parametrize(
    "state",
    [
        "default",
        "en",
        "zh_missing",
        "zh_invalid",
        "zh_valid",
        "invalid_preference",
        "access_error",
        "format_error",
    ],
)
def test_existing_database_and_all_backups_byte_identical_after_localization(
    populated_database, tmp_path, monkeypatch, state
):
    paths = populated_database
    if state in {"en", "zh_missing", "zh_invalid", "zh_valid", "invalid_preference"}:
        raw = "banana" if state == "invalid_preference" else "en" if state == "en" else "zh_CN"
        write_preference(paths.root, raw)
    if state in {"zh_invalid", "zh_valid"}:
        dummy_pack(paths.root)
    kwargs = {}
    if state in {"access_error", "format_error"}:
        status = (
            QSettings.Status.AccessError
            if state == "access_error"
            else QSettings.Status.FormatError
        )
        kwargs["settings_factory"] = SettingsPlan({"status": status})
    if state == "zh_valid":
        kwargs["translator_factory"] = Translator
    monkeypatch.setattr(loc.QLibraryInfo, "path", lambda kind: str(tmp_path / "missing-qt"))

    def hashes():
        return {
            p.relative_to(paths.root): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths.root.rglob("*")
            if p.is_file()
        }

    def database_content():
        with closing(sqlite3.connect(paths.database)) as connection:
            assert connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION == 1
            content = {
                table: connection.execute(f"SELECT * FROM {table} ORDER BY 1, 2").fetchall()
                for table in (
                    "rounds",
                    "round_analysis_snapshots",
                    "history_regimes",
                    "character_stats",
                )
            }
            assert all(content.values())
            return content

    content_before = database_content()
    before = hashes()
    assert (
        any(paths.recent.iterdir()) and any(paths.daily.iterdir()) and any(paths.safety.iterdir())
    )
    context = loc.initialize_localization(App(), paths.root, **kwargs)
    assert context.effective_language == (
        loc.Language.ZH_CN if state == "zh_valid" else loc.Language.EN
    )
    assert hashes() == before
    assert database_content() == content_before
    assert hashes() == before
