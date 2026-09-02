from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication, QTranslator

from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.desktop_host import DesktopHost
from probability_calibration_tool.infrastructure.paths import AppPaths
from probability_calibration_tool.localization import (
    APP_QM_NAME,
    FallbackReason,
    Language,
    PackPreflightStatus,
    initialize_localization,
    preflight_app_pack,
)

from .helpers import write_preference
from .step5_support import CONTEXTS, ROOT, TS_PATH, catalog_map, load_catalog


@pytest.fixture(scope="module")
def official_qm(tmp_path_factory):
    directory = tmp_path_factory.mktemp("step5-qm")
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
    return candidate, process


def _install_candidate(root, candidate):
    directory = root / "languages"
    directory.mkdir(parents=True)
    shutil.copyfile(candidate, directory / APP_QM_NAME)
    return directory


def test_strict_lrelease_and_direct_qtranslator_equivalence_225_of_225(official_qm):
    candidate, process = official_qm
    assert "225 translation(s) (225 finished and 0 unfinished)" in process.stdout
    translator = QTranslator()
    assert translator.load(str(candidate), "", "", "") is True
    assert not translator.isEmpty() and translator.language() == "zh_CN"
    units = load_catalog()[1]
    assert len(units) == 225
    assert all(
        translator.translate(unit.context, unit.source) == unit.translation for unit in units
    )
    assert translator.translate("Characters", "???") == "???"
    assert translator.translate("Localization", "Language") == "界面语言"


def test_real_step3_preflight_and_zh_cn_initialization(
    tmp_path, localization_app, real_contexts, official_qm
):
    root = tmp_path / "app"
    directory = _install_candidate(root, official_qm[0])
    preflight = preflight_app_pack(directory)
    assert preflight.status == PackPreflightStatus.VALID
    assert preflight.translator is not None and not preflight.translator.isEmpty()
    write_preference(root, Language.ZH_CN.value)
    context = initialize_localization(localization_app, root)
    real_contexts.append(context)
    assert context.preferred_language == Language.ZH_CN
    assert context.effective_language == Language.ZH_CN
    assert context.available_languages == frozenset({Language.EN, Language.ZH_CN})
    assert context.fallback_reason == FallbackReason.NONE
    assert context.app_translator is not None and not context.app_translator.isEmpty()


def test_installed_real_translator_smoke_covers_all_12_contexts(
    tmp_path, localization_app, real_contexts, official_qm
):
    root = tmp_path / "app"
    _install_candidate(root, official_qm[0])
    write_preference(root, Language.ZH_CN.value)
    context = initialize_localization(localization_app, root)
    real_contexts.append(context)
    catalog = catalog_map()
    samples = {}
    for (name, source), translation in catalog.items():
        samples.setdefault(name, (source, translation))
    assert set(samples) == CONTEXTS
    assert all(
        QCoreApplication.translate(name, source) == target
        for name, (source, target) in samples.items()
    )


def test_real_widget_smoke_uses_compiled_official_pack(
    tmp_path, localization_app, real_contexts, official_qm
):
    app_root = tmp_path / "localized-app"
    _install_candidate(app_root, official_qm[0])
    write_preference(app_root, Language.ZH_CN.value)
    context = initialize_localization(localization_app, app_root)
    real_contexts.append(context)
    with StartupService(AppPaths.from_root(tmp_path / "business")).start() as runtime:
        host = DesktopHost(runtime)
        try:
            host.show_initial_state()
            window = host.window
            assert window.round_button.text() == "单局"
            assert window.maintenance_button.text() == "维护"
            assert window.round.pre.primary.text() == "计算"
            assert window.characters.buttons[1].accessibleName() == "以撒"
            assert window.round.analysis.subjective.title() == "主观概率分析"
        finally:
            host.dispose()


def test_english_and_missing_pack_fallback_remain_unchanged(
    tmp_path, localization_app, real_contexts
):
    assert QCoreApplication.translate("Round", "Calculate") == "Calculate"
    root = tmp_path / "missing-pack"
    write_preference(root, Language.ZH_CN.value)
    context = initialize_localization(localization_app, root)
    real_contexts.append(context)
    assert context.preferred_language == Language.ZH_CN
    assert context.effective_language == Language.EN
    assert context.available_languages == frozenset({Language.EN})
    assert context.fallback_reason == FallbackReason.PREFERRED_PACK_MISSING
    assert context.app_translator is None
    assert QCoreApplication.translate("Round", "Calculate") == "Calculate"
