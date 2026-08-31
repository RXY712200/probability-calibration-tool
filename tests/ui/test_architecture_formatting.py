import ast
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from probability_calibration_tool.ui import formatting


def test_ui_has_no_persistence_math_private_workflow_or_event_pumping():
    root = Path(formatting.__file__).parent
    forbidden = {
        "sqlite3",
        "scipy",
        "math",
        "probability_calibration_tool.core",
        "probability_calibration_tool.persistence",
    }
    for file in root.glob("*.py"):
        tree = ast.parse(file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not any(
                    any(a.name.startswith(prefix) for prefix in forbidden) for a in node.names
                )
            if isinstance(node, ast.ImportFrom):
                assert not any((node.module or "").startswith(prefix) for prefix in forbidden)
            if isinstance(node, ast.Attribute):
                assert node.attr not in ("processEvents", "setGeometry", "setValidator")
                if isinstance(node.value, ast.Attribute) and node.value.attr == "workflow":
                    assert not node.attr.startswith("_")
    assert not list(root.glob("*.ui")) and not list(root.glob("*.qml"))


def test_local_timestamp_and_readable_formatting_do_not_mutate_values():
    stamp = datetime(2026, 8, 31, 18, 30, tzinfo=UTC)
    assert formatting.format_timestamp(stamp, timezone(timedelta(hours=8))) == "2026-09-01 02:30:00"
    assert stamp.hour == 18 and stamp.tzinfo == UTC
    assert formatting.format_probability(0.7123456789) == "71.2%"
    assert formatting.format_ev(-0.1234567) == "-0.123"
    assert formatting.format_odds(2.0) == "2"


@pytest.mark.parametrize("p", ["", "garbage", "1.1", "1000"])
def test_command_conversion_defers_validity_to_application(p):
    from probability_calibration_tool.ui.presentation import calculate_command

    command = calculate_command(None, None, p, "2,00", "1e5")
    assert command.p_h_raw == (1000 if p == "1000" else p)
    assert command.win_odds_raw == "2,00" and command.lose_odds_raw == "1e5"
