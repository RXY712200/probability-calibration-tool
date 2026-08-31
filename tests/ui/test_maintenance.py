import re

from .helpers import calculate, click, widget_text


def test_maintenance_safe_columns_and_in_page_regime_confirmation(window, h):
    h.seed_history(19, 1)
    click(window.maintenance_button)
    page = window.maintenance
    assert window.stack.currentWidget() is page
    assert page.table.rowCount() == 34 and page.table.columnCount() == 5
    assert not page.table.isSortingEnabled()
    assert [page.table.horizontalHeaderItem(i).text() for i in range(5)] == [
        "Character",
        "Current regime",
        "Started locally",
        "Reason",
        "Included samples",
    ]
    text = widget_text(page).lower()
    for prohibited in (
        "win rate",
        "wins",
        "losses",
        "jeffreys",
        "probability",
        "interval",
        "ev",
        "12/20",
    ):
        assert re.search(r"\b" + re.escape(prohibited) + r"\b", text) is None
    assert not page.start.isEnabled()
    page.table.selectRow(0)
    click(page.start)
    assert page.confirmation.isVisible()
    assert "Isaac" in page.summary.text()
    page.reason.setText("Changed conditions")
    click(page.confirm)
    assert h.maintenance.list_characters()[0].active_regime_number == 2
    assert page.table.item(0, 4).text() == "0"


def test_pending_disables_regime_ui_and_service_still_guards(window, h):
    import pytest

    from probability_calibration_tool.application.errors import RegimeSwitchBlockedError

    calculate(window)
    click(window.maintenance_button)
    page = window.maintenance
    page.table.selectRow(0)
    assert not page.start.isEnabled()
    assert "pending" in page.unavailable.text()
    with pytest.raises(RegimeSwitchBlockedError):
        h.regimes.start_new_regime(1)
