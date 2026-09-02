"""Permanent Step 4 ownership/source boundaries, not a future-UI translation ban."""

import ast
from pathlib import Path

import pytest

SOURCE = Path(__file__).parents[2] / "src" / "probability_calibration_tool"
ORDINARY = (
    "analysis_panel",
    "pre_run_panel",
    "post_run_panel",
    "round_page",
    "maintenance_page",
    "correction_page",
    "restore_page",
    "recovery_page",
    "character_matrix",
)


@pytest.mark.parametrize("module", ORDINARY)
def test_ordinary_widgets_have_no_infrastructure_context_dependency(module):
    tree = ast.parse((SOURCE / "ui" / f"{module}.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            assert node.id not in {"LocalizationContext", "QSettings", "QTranslator"}
        if isinstance(node, ast.arg):
            assert node.arg not in {"context", "localization", "localization_context"}
        if isinstance(node, ast.ImportFrom):
            assert "persistence" not in (node.module or "").split(".")
            assert node.module != "probability_calibration_tool.localization"


def test_static_sources_no_live_translation_or_display_text_business_protocol():
    paths = [SOURCE / "desktop_host.py", SOURCE / "bootstrap.py", *(SOURCE / "ui").glob("*.py")]
    delayed_mapping_modules = {"localization.py", "startup_pages.py", "language_dialog.py"}
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = (
                    node.func.attr
                    if isinstance(node.func, ast.Attribute)
                    else getattr(node.func, "id", "")
                )
                assert name not in {"retranslateUi", "changeEvent"}, (
                    path,
                    node.lineno,
                )
                if name == "setDefault" and isinstance(node.func, ast.Attribute):
                    assert not ast.unparse(node.func.value).endswith("QLocale"), (path, node.lineno)
                if name in {"translate", "QT_TRANSLATE_NOOP", "template"}:
                    assert not any(
                        isinstance(arg, (ast.JoinedStr, ast.BinOp)) for arg in node.args[:2]
                    ), (path, node.lineno)
                    if name == "QT_TRANSLATE_NOOP":
                        assert all(isinstance(arg, ast.Constant) for arg in node.args[:2])
                    elif name == "translate" and not all(
                        isinstance(arg, ast.Constant) for arg in node.args[:2]
                    ):
                        assert path.name in delayed_mapping_modules, (path, node.lineno)
                if name == "str" and node.args and isinstance(node.args[0], ast.Name):
                    assert node.args[0].id not in {"exc", "error", "failure"}, (path, node.lineno)
            if isinstance(node, (ast.If, ast.IfExp, ast.While, ast.Assert)):
                # Reading editable user input is legitimate. Never branch on a
                # translated label/button; the sole condition reads a reason field.
                for call in ast.walk(node.test):
                    if (
                        isinstance(call, ast.Call)
                        and isinstance(call.func, ast.Attribute)
                        and call.func.attr == "text"
                    ):
                        assert path.name == "correction_page.py"
                        assert ast.unparse(call.func.value) == "self.reason"
            if isinstance(node, ast.Attribute):
                assert node.attr != "LanguageChange", (path, node.lineno)


def test_error_reporting_and_session_stay_language_agnostic():
    for relative in ("infrastructure/error_reporting.py", "application/desktop_session.py"):
        source = (SOURCE / relative).read_text(encoding="utf-8")
        assert "PySide6" not in source and "localization" not in source
        assert "Error ID:" not in source
