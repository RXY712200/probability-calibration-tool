from __future__ import annotations

import ast
import hashlib
import shutil
import subprocess
import sys
from contextlib import closing
from dataclasses import fields
from pathlib import Path

import pytest

from probability_calibration_tool.application.correction_query_service import (
    CorrectionCandidate,
)
from probability_calibration_tool.application.enums import WorkflowState
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.desktop_host import DesktopHost
from probability_calibration_tool.domain.enums import (
    EvState,
    HistoryModelStatus,
    ModelRelation,
    OddsCombinationStatus,
)
from probability_calibration_tool.infrastructure.paths import AppPaths
from probability_calibration_tool.localization import APP_QM_NAME, Language, preflight_app_pack
from probability_calibration_tool.persistence.database import create_connection
from probability_calibration_tool.persistence.migrations import ensure_schema
from probability_calibration_tool.ui.localization import (
    CHARACTER_SOURCES,
    DOMAIN_SOURCES,
    unavailable_label,
)
from probability_calibration_tool.ui.presentation import CharacterOption

from .qa_helpers import (
    ParityHarness,
    activated_track,
    build_official_qm,
    canonical_database,
)
from .step5_support import CONTEXTS, ROOT, TS_PATH, load_catalog

EXPECTED_TS_SHA256 = "2b0085143a972d0c954629959bae405dcf2bd1cd02725cf191a14494a9e86ebd"
SOURCE_ROOT = ROOT / "src" / "probability_calibration_tool"


@pytest.fixture(scope="module")
def step6_guardrail_qm(tmp_path_factory):
    return build_official_qm(tmp_path_factory.mktemp("step6-guardrail-official-qm"))


def test_source_and_context_drift_guard_uses_fresh_production_extraction(tmp_path):
    candidate = tmp_path / "fresh-production.ts"
    executable = Path(sys.executable).parent / "pyside6-lupdate.exe"
    process = subprocess.run(
        [str(executable), "-extensions", "py", "src", "-ts", str(candidate)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    official_units = load_catalog()[1]
    extracted_units = load_catalog(candidate)[1]
    official_keys = {(unit.context, unit.source, unit.numerus) for unit in official_units}
    extracted_keys = {(unit.context, unit.source, unit.numerus) for unit in extracted_units}
    assert extracted_keys == official_keys
    assert len(extracted_keys) == 225
    assert {context for context, _, _ in extracted_keys} == CONTEXTS
    assert hashlib.sha256(TS_PATH.read_bytes()).hexdigest() == EXPECTED_TS_SHA256


def test_runtime_pack_and_single_external_locale_boundaries(tmp_path):
    assert APP_QM_NAME == "probability_calibration_tool_zh_CN.qm"
    assert preflight_app_pack(tmp_path).path == tmp_path.absolute() / APP_QM_NAME
    assert list((ROOT / "translations").glob("*.ts")) == [TS_PATH]
    assert not list((ROOT / "translations").glob("*.qm"))
    assert not list(SOURCE_ROOT.rglob("*.ts")) and not list(SOURCE_ROOT.rglob("*.qm"))

    tree = ast.parse((SOURCE_ROOT / "localization.py").read_text(encoding="utf-8"))
    calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    constants = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)}
    assert not calls.intersection({"glob", "rglob"})
    assert ".ts" not in constants
    assert "translations" not in constants and "build" not in constants


def test_identity_domain_mapping_and_schema_guardrails(tmp_path):
    assert {field.name for field in fields(CharacterOption)} == {"character_id"}
    assert {field.name for field in fields(CorrectionCandidate)} == {
        "round_id",
        "character_id",
        "completed_at",
    }
    assert set(CHARACTER_SOURCES) == set(range(1, 35))
    assert "Tainted Esau" not in CHARACTER_SOURCES.values()
    assert set(DOMAIN_SOURCES) == {
        EvState,
        OddsCombinationStatus,
        ModelRelation,
        HistoryModelStatus,
    }
    for enum, mapping in DOMAIN_SOURCES.items():
        assert set(mapping) == set(enum)
    assert unavailable_label()

    database = tmp_path / "schema.db"
    with closing(create_connection(database)) as connection:
        ensure_schema(connection)
        for table in (
            "characters",
            "history_regimes",
            "rounds",
            "round_analysis_snapshots",
            "character_stats",
            "meta",
        ):
            columns = {row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')}
            assert not columns.intersection({"language", "locale", "translation", "localized"})


@pytest.mark.parametrize("language", [Language.EN, Language.ZH_CN], ids=["en", "zh_CN"])
def test_real_official_qm_anti_anchoring_before_calculate(
    language, tmp_path, localization_app, step6_guardrail_qm
):
    seed = tmp_path / "shared-seed.db"
    if not seed.exists():
        ParityHarness(seed).seed_history(19, 1)
    root = tmp_path / language.value
    paths = AppPaths.from_root(root / "business")
    paths.database.parent.mkdir(parents=True)
    shutil.copyfile(seed, paths.database)
    before = canonical_database(paths.database)

    with (
        activated_track(
            localization_app, root / "localization", language, step6_guardrail_qm
        ) as context,
        StartupService(paths).start() as runtime,
    ):
        host = DesktopHost(runtime)
        host.bind_localization(context)
        try:
            host.show_initial_state()
            window = host.window
            assert window.workflow.state == WorkflowState.DRAFT
            assert window.round.analysis.isHidden()
            history = window.round.analysis.historical
            assert all(
                not widget.text() and widget.isHidden() for widget in history.values.values()
            )
            assert all(
                not widget.text() and widget.isHidden() for widget in history.captions.values()
            )
            assert not history.message.text() and history.message.isHidden()
            assert window.maintenance.table.columnCount() == 5
        finally:
            host.dispose()
    assert canonical_database(paths.database) == before
