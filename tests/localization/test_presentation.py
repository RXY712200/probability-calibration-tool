import ast
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import fields, replace
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication, QTranslator

from probability_calibration_tool.application.correction_query_service import CorrectionCandidate
from probability_calibration_tool.application.enums import HistoricalDisplayState as H
from probability_calibration_tool.application.errors import ErrorCode, InputValidationError
from probability_calibration_tool.application.views import NonnumericHistoryView
from probability_calibration_tool.domain.enums import (
    EvState,
    HistoryModelStatus,
    ModelRelation,
    OddsCombinationStatus,
)
from probability_calibration_tool.infrastructure.error_reporting import (
    ErrorPresentation,
    SafeErrorCode,
    WarningCode,
)
from probability_calibration_tool.persistence.seed import CHARACTERS
from probability_calibration_tool.ui import localization as display
from probability_calibration_tool.ui.analysis_panel import AnalysisPanel
from probability_calibration_tool.ui.character_matrix import CharacterMatrix
from probability_calibration_tool.ui.correction_page import CorrectionPage
from probability_calibration_tool.ui.maintenance_page import MaintenancePage
from probability_calibration_tool.ui.presentation import CharacterOption, RecoveryPresentation
from probability_calibration_tool.ui.recovery_page import RecoveryPage


class MarkerTranslator(QTranslator):
    def __init__(self, overrides=None):
        super().__init__()
        self.overrides = overrides or {}
        self.calls = []

    def isEmpty(self):
        return False

    def translate(self, context, source, disambiguation=None, n=-1):
        self.calls.append((context, source))
        return self.overrides.get((context, source), f"⟦{context}⟧ {source}")


@pytest.fixture
def marker(localization_app):
    installed = []

    def install(overrides=None):
        translator = MarkerTranslator(overrides)
        assert localization_app.installTranslator(translator)
        installed.append(translator)
        return translator

    yield install
    for translator in reversed(installed):
        localization_app.removeTranslator(translator)


@pytest.fixture
def presentation_harness(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).parents[1] / "integration"))
    from application.helpers import Harness

    return Harness(tmp_path / "presentation.db")


@pytest.mark.parametrize("translated", [False, True])
@pytest.mark.parametrize(
    "enum,mapping",
    [
        (EvState, display.EV_SOURCES),
        (OddsCombinationStatus, display.ODDS_SOURCES),
        (ModelRelation, display.RELATION_SOURCES),
        (HistoryModelStatus, display.HISTORY_SOURCES),
    ],
)
def test_semantic_mapping_exact_and_exhaustive(marker, translated, enum, mapping):
    assert set(mapping) == set(enum)
    if translated:
        marker()
    for value in enum:
        text = display.domain_label(value)
        assert text == ("⟦DomainLabels⟧ " if translated else "") + mapping[value]
    with pytest.raises(KeyError):
        display.domain_label("not-a-semantic-enum")


def test_legacy_double_positive_na_and_explicit_boolean_semantics(marker):
    assert (
        display.domain_label(OddsCombinationStatus.DOUBLE_POSITIVE_WINDOW)
        == "Double positive window"
    )
    marker()
    assert display.unavailable_label() == "⟦DomainLabels⟧ N/A"
    assert display.result_label(True) == "⟦DomainLabels⟧ Win"
    assert display.result_label(False) == "⟦DomainLabels⟧ Loss"
    assert display.inclusion_label(True) == "⟦DomainLabels⟧ Include"
    assert display.inclusion_label(False) == "⟦DomainLabels⟧ Exclude"


@pytest.mark.parametrize(
    "translation,expected",
    [
        ("%2 before %1", "two before one"),
        ("missing %1", "one / two"),
        ("%1 %1 %2", "one / two"),
        ("%1 %2 %3", "one / two"),
        ("no placeholders", "one / two"),
    ],
)
def test_placeholder_reordering_and_per_message_safe_fallback(marker, translation, expected):
    marker({("Analysis", "%1 / %2"): translation})
    assert display.template("Analysis", "%1 / %2", "one", "two") == expected
    assert QCoreApplication.translate("Round", "Calculate") == "⟦Round⟧ Calculate"


def test_placeholder_substitution_is_not_recursive_and_handles_percent_and_ten(marker):
    marker({("Analysis", "%1% %10"): "%10 %1%"})
    assert display.template("Analysis", "%1% %10", "%2", *range(2, 11)) == "10 %2%"


@pytest.mark.parametrize("translated", [False, True])
@pytest.mark.parametrize("character_id", [1, 5, 22, 17, 34])
def test_character_identity_across_matrix_maintenance_recovery_correction(
    marker, translated, character_id, presentation_harness
):
    from probability_calibration_tool.application import CalculateCommand

    h = presentation_harness
    seed = {row[0]: row[2] for row in CHARACTERS}
    assert display.CHARACTER_SOURCES == seed and set(seed) == set(range(1, 35))
    assert {field.name for field in fields(CharacterOption)} == {"character_id"}
    if translated:
        marker()
    name = ("⟦Characters⟧ " if translated else "") + seed[character_id]
    matrix = CharacterMatrix(tuple(CharacterOption(key) for key in sorted(seed)))
    assert matrix.buttons[character_id].text() == name.replace("&", "&&")
    assert matrix.buttons[character_id].accessibleName() == name
    page = MaintenancePage()
    rows = h.maintenance.list_characters()
    page.populate(rows)
    index = next(i for i, row in enumerate(rows) if row.character_id == character_id)
    assert page.table.item(index, 0).text() == name
    page.table.selectRow(index)
    page.render(can_start=True, confirmation=True, connected=True)
    assert name in page.summary.text()
    view = h.rounds.calculate(CalculateCommand(character_id, False, 70, "2.00", "3.00"))
    recovery = RecoveryPage()
    recovery.render(RecoveryPresentation(h.recovery.inspect(), h.recovery.continue_pending()))
    assert name in recovery.facts.text()
    assert h.recovery.continue_pending().round_id == view.round_id
    correction = CorrectionPage()
    candidate = CorrectionCandidate(view.round_id, character_id, view.calculated_at)
    correction.populate([candidate])
    assert name in correction.candidates.item(0).text()
    correction.candidates.setCurrentRow(0)
    assert correction.selected().round_id == view.round_id
    with h.factory() as uow:
        assert {c.character_id: c.display_name for c in uow.characters.list_all()} == seed


@pytest.mark.parametrize("translated", [False, True])
@pytest.mark.parametrize("state", [H.HIDDEN, H.NO_HISTORY, H.INSUFFICIENT])
def test_translated_anti_anchoring_stale_history_cleared(
    marker, translated, state, presentation_harness
):
    from probability_calibration_tool.application import CalculateCommand

    if translated:
        marker()
    h = presentation_harness
    h.seed_history(19, 1)
    view = h.rounds.calculate(CalculateCommand(1, True, 70, "2", "3"))
    panel = AnalysisPanel()
    panel.render(view)
    assert panel.historical.values["probability"].text()
    panel.render(replace(view, history=NonnumericHistoryView(state)))
    assert all(not widget.text() for widget in panel.historical.values.values())
    assert all(not widget.text() for widget in panel.historical.captions.values())
    assert not any(character.isdigit() for character in panel.historical.message.text())
    assert panel.historical.message.text().startswith("⟦Analysis⟧ ") is translated
    maintenance = MaintenancePage()
    maintenance.populate(h.maintenance.list_characters())
    assert maintenance.table.columnCount() == 5
    assert "wins" not in maintenance.table.horizontalHeaderItem(4).text().lower()
    assert "losses" not in maintenance.table.horizontalHeaderItem(4).text().lower()


def test_expected_and_safe_error_mapping_exhaustive_and_not_message_protocol(marker):
    internal = {
        ErrorCode.UNKNOWN,
        ErrorCode.ROUND_NOT_FOUND,
        ErrorCode.ROUND_NOT_PENDING,
        ErrorCode.ROUND_NOT_COMPLETED,
    }
    assert set(display.ERROR_SOURCES) == set(ErrorCode) - internal
    assert set(display.SAFE_ERROR_SOURCES) == set(SafeErrorCode)
    marker()
    for code in display.ERROR_SOURCES:
        error = InputValidationError("win_odds", "PRIVATE SELECT diagnostic", code=code)
        assert display.is_public_expected_error(error)
        assert display.expected_error(error) == "⟦Errors⟧ " + display.ERROR_SOURCES[code]
        assert error.field == "win_odds"
    for code in (*internal, "unrecognized", []):
        error = InputValidationError("reason", "SECRET pending_edit", code=code)
        assert not display.is_public_expected_error(error)
        with pytest.raises((KeyError, TypeError)):
            display.expected_error(error)
    safe = display.safe_error(ErrorPresentation("SECRET SQL C:/private", "error-id"))
    assert "error-id" in safe and "SECRET" not in safe and "⟦Errors⟧" in safe


def test_operational_warning_and_backup_metadata_mapping_exhaustive(marker):
    from probability_calibration_tool.infrastructure.backup import REASONS, BackupCategory
    from probability_calibration_tool.ui.banners import BannerHost

    assert set(display.WARNING_SOURCES) == set(WarningCode)
    assert set(display.BACKUP_CATEGORY_SOURCES) == set(BackupCategory)
    assert set(display.BACKUP_REASON_SOURCES) == REASONS
    marker()
    for code in WarningCode:
        assert display.warning_text(code) == "⟦Errors⟧ " + display.WARNING_SOURCES[code]
    for code in SafeErrorCode:
        error = ErrorPresentation("PRIVATE SQL/path diagnostic", "id", code)
        assert display.SAFE_ERROR_SOURCES[code] in display.warning_text(error)
        assert "PRIVATE" not in display.warning_text(error)
    assert (
        display.warning_text("PRIVATE unknown warning")
        == "⟦Errors⟧ The operation could not be completed."
    )
    banner = BannerHost()
    for severity, source in display.SEVERITY_SOURCES.items():
        banner.show_message("payload", severity)
        assert banner.property("severity") == severity
        assert "⟦AppShell⟧ " + source in banner.message.text()


def test_real_extraction_exact_contexts_sources_and_placeholder_signatures(tmp_path):
    root = Path(__file__).parents[2]
    tool = Path(sys.executable).parent / "pyside6-lupdate.exe"
    assert tool.is_file() and tool.resolve().is_relative_to((root / ".venv").resolve())
    output = tmp_path / "step4-extraction.ts"
    process = subprocess.run(
        [str(tool), "-extensions", "py", str(root / "src"), "-ts", str(output)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    tree = ET.parse(output)
    contexts = {context.findtext("name") for context in tree.findall("context")}
    assert contexts == {
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
    extracted = {
        context.findtext("name"): {
            message.findtext("source") for message in context.findall("message")
        }
        for context in tree.findall("context")
    }
    assert set(display.CHARACTER_SOURCES.values()) <= extracted["Characters"]
    assert set(display.ERROR_SOURCES.values()) <= extracted["Errors"]
    assert {
        "Round does not exist.",
        "Round must be pending.",
        "Round must be completed.",
    }.isdisjoint(extracted["Errors"])
    assert "Language" in extracted["Localization"]
    assert "Double positive window" in extracted["DomainLabels"]
    for source, tokens in {
        "Win %1; loss event %2; loss as win-probability %3": ["%1", "%2", "%3"],
        "%1% entered; %2% used for mathematical calculation.": ["%1", "%2"],
        "Wins %1; losses %2; samples %3": ["%1", "%2", "%3"],
        "Win: %1; Loss: %2": ["%1", "%2"],
    }.items():
        assert source in extracted["Analysis"]
        assert display.PLACEHOLDER.findall(source) == tokens


def test_no_lookup_at_import_or_generic_widget_auto_translation():
    root = Path(display.__file__).parent
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        class Visitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                pass

            def visit_Call(self, node, path=path):
                assert not (
                    isinstance(node.func, ast.Attribute) and node.func.attr in {"translate", "tr"}
                ), (path, node.lineno)
                self.generic_visit(node)

        Visitor().visit(tree)
    widgets = ast.parse((root / "widgets.py").read_text(encoding="utf-8"))
    assert not any(
        isinstance(n, ast.Attribute) and n.attr in {"translate", "tr"} for n in ast.walk(widgets)
    )
