import pytest

from probability_calibration_tool.application.errors import BusinessRuleError

from .helpers import calculate, click, complete, fail_recent, scalar


@pytest.mark.parametrize("backup_failure", [False, True])
def test_regime_one_shot_commit_recent_refresh(desk, monkeypatch, backup_failure):
    if backup_failure:
        fail_recent(desk, monkeypatch)
    window = desk.window
    window.show_maintenance()
    window.maintenance.table.selectRow(0)
    click(window.maintenance.start)
    ticket = window._regime_ticket
    assert ticket is not None
    window.maintenance.reason.setText("new context")
    window._start_regime()
    window._start_regime()
    with pytest.raises(BusinessRuleError, match="expired"):
        desk.session.start_regime(ticket, "duplicate")
    assert scalar(desk.path, "SELECT count(*) FROM history_regimes WHERE character_id=1") == 2
    assert (
        scalar(
            desk.path, "SELECT active FROM history_regimes WHERE character_id=1 AND regime_number=1"
        )
        == 0
    )
    assert (
        scalar(
            desk.path,
            "SELECT included_games FROM character_stats WHERE regime_id=(SELECT regime_id FROM history_regimes WHERE character_id=1 AND active=1)",
        )
        == 0
    )
    assert window.maintenance.rows[0].active_regime_number == 2
    assert window.maintenance.rows[0].regime_reason == "new context"
    if backup_failure:
        assert "Recent backup failed" in window.banner.message.text()
    else:
        assert len(desk.backups()) == 1


@pytest.mark.parametrize("state", ["pending", "completed"])
def test_admin_presentation_and_integration_require_draft(desk, state):
    if state == "pending":
        calculate(desk.window)
    else:
        complete(desk.window)
    desk.window.show_maintenance()
    desk.window.maintenance.table.selectRow(0)
    assert not desk.window.maintenance.start.isEnabled()
    assert not desk.window.correction_button.isEnabled()
    assert not desk.window.restore_button.isEnabled()
    assert desk.window.maintenance.table.rowCount() == 34
    for operation in (
        lambda: desk.session.begin_regime(1),
        lambda: desk.session.begin_correction("any"),
        lambda: desk.session.begin_restore("any"),
    ):
        with pytest.raises(BusinessRuleError, match="Draft"):
            operation()
