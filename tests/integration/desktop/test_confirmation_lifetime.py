import pytest
from PySide6.QtCore import QTimer

from probability_calibration_tool.application.desktop_session import DisposedSessionError
from probability_calibration_tool.application.errors import BusinessRuleError
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.desktop_host import DesktopHost
from probability_calibration_tool.infrastructure.backup import BackupCategory

from .helpers import begin_correction, click, complete, scalar


def begin(window, kind):
    if kind == "regime":
        window.show_maintenance()
        window.maintenance.table.selectRow(0)
        click(window.maintenance.start)
    elif kind == "correction":
        begin_correction(window)
    else:
        window.show_restore()
        window.restore_page.candidates.setCurrentRow(0)
        click(window.restore_page.restore)
    ticket = getattr(window, f"_{kind}_ticket")
    assert ticket is not None
    return ticket


def submit(session, kind, ticket):
    if kind == "regime":
        return session.start_regime(ticket, "new context")
    if kind == "correction":
        return session.correct(ticket, False, True, "audit repair")
    return session.restore(ticket)


def test_regime_round_trip_revokes_authority_and_restores_usable_maintenance(desk):
    window = desk.window
    ticket = begin(window, "regime")
    before = desk.path.read_bytes()
    click(window.round_button)
    click(window.maintenance_button)
    assert window._regime_ticket is None
    assert window.maintenance.table.isEnabled()
    assert window.maintenance.start.isVisible()
    assert not window.maintenance.confirmation.isVisible()
    assert window.maintenance.selected() is None
    window.maintenance.table.selectRow(0)
    assert window.maintenance.start.isEnabled()
    with pytest.raises(BusinessRuleError, match="Confirmation expired"):
        desk.session.start_regime(ticket, "stale Isaac confirmation")
    assert desk.path.read_bytes() == before
    assert not desk.backups()


def test_fresh_magdalene_confirmation_cannot_use_stale_isaac_identity(
    desk, desktop_app, monkeypatch
):
    window = desk.window
    stale = begin(window, "regime")
    click(window.round_button)
    click(window.maintenance_button)
    window.maintenance.table.selectRow(1)
    assert window.maintenance.selected().display_name == "Magdalene"
    click(window.maintenance.start)
    with pytest.raises(BusinessRuleError, match="Confirmation expired"):
        desk.session.start_regime(stale, "stale Isaac confirmation")
    attempts = []
    create = desk.host.backup.create

    def counted(category, reason=None):
        attempts.append(category)
        return create(category, reason)

    monkeypatch.setattr(desk.host.backup, "create", counted)
    QTimer.singleShot(0, window._start_regime)
    QTimer.singleShot(0, window._start_regime)
    desktop_app.processEvents()
    assert scalar(desk.path, "SELECT count(*) FROM history_regimes WHERE character_id=1") == 1
    assert scalar(desk.path, "SELECT count(*) FROM history_regimes WHERE character_id=2") == 2
    assert attempts == [BackupCategory.RECENT]
    assert len(desk.backups()) == 1


@pytest.mark.parametrize("kind", ["regime", "correction", "restore"])
@pytest.mark.parametrize("destination", ["round", "maintenance", "correction", "restore"])
def test_navigation_and_reentry_revoke_both_ticket_layers(desk, kind, destination):
    complete(desk.window)
    click(desk.window.round.new_round)
    ticket = begin(desk.window, kind)
    before, backups = desk.path.read_bytes(), desk.backups()
    getattr(desk.window, f"show_{destination}")()
    assert getattr(desk.window, f"_{kind}_ticket") is None
    with pytest.raises(BusinessRuleError, match="Confirmation expired"):
        submit(desk.session, kind, ticket)
    source_page = "maintenance" if kind == "regime" else kind
    getattr(desk.window, f"show_{source_page}")()
    assert getattr(desk.window, f"_{kind}_ticket") is None
    assert desk.window.maintenance.table.isEnabled()
    assert not desk.window.maintenance.confirmation.isVisible()
    assert not desk.window.correction.form.isVisible()
    assert not desk.window.restore_page.confirm.isVisible()
    assert desk.path.read_bytes() == before
    assert desk.backups() == backups


@pytest.mark.parametrize("kind", ["regime", "correction", "restore"])
def test_back_revokes_ui_and_session_without_business_or_backup(desk, kind):
    complete(desk.window)
    click(desk.window.round.new_round)
    ticket = begin(desk.window, kind)
    before, backups = desk.path.read_bytes(), desk.backups()
    page = {
        "regime": desk.window.maintenance,
        "correction": desk.window.correction,
        "restore": desk.window.restore_page,
    }[kind]
    click(page.back)
    assert getattr(desk.window, f"_{kind}_ticket") is None
    with pytest.raises(BusinessRuleError, match="Confirmation expired"):
        submit(desk.session, kind, ticket)
    assert desk.path.read_bytes() == before
    assert desk.backups() == backups


@pytest.mark.parametrize("kind", ["regime", "correction", "restore"])
def test_cancellation_is_matching_identity_only_and_idempotent(desk, kind):
    complete(desk.window)
    click(desk.window.round.new_round)
    stale = begin(desk.window, kind)
    identity = desk.session._tickets[kind][1]
    fresh = getattr(desk.session, f"begin_{kind}")(identity)
    cancel = getattr(desk.session, f"cancel_{kind}")
    before, backups = desk.path.read_bytes(), desk.backups()
    for ticket in (stale, stale, None, object()):
        cancel(ticket)
    # Late cancellation of an obsolete interaction must not revoke the fresh authority.
    assert desk.session._consume(kind, fresh) == identity
    current = getattr(desk.session, f"begin_{kind}")(identity)
    cancel(current)
    cancel(current)
    with pytest.raises(BusinessRuleError, match="Confirmation expired"):
        submit(desk.session, kind, current)
    assert desk.path.read_bytes() == before
    assert desk.backups() == backups


@pytest.mark.parametrize("kind", ["regime", "correction", "restore"])
def test_cancellation_requires_active_session(desk, kind):
    cancel = getattr(desk.session, f"cancel_{kind}")
    desk.host.dispose()
    with pytest.raises(DisposedSessionError):
        cancel(None)


@pytest.mark.parametrize("kind", ["regime", "correction", "restore"])
def test_failed_page_reload_revokes_before_query_or_population(desk, monkeypatch, kind):
    complete(desk.window)
    click(desk.window.round.new_round)
    ticket = begin(desk.window, kind)

    def fail():
        raise RuntimeError("injected reload failure")

    target, method, page = {
        "regime": (desk.window.ports, "maintenance_rows", "maintenance"),
        "correction": (desk.session, "correction_candidates", "correction"),
        "restore": (desk.session.catalog, "refresh", "restore"),
    }[kind]
    monkeypatch.setattr(target, method, fail)
    getattr(desk.window, f"show_{page}")()
    assert getattr(desk.window, f"_{kind}_ticket") is None
    with pytest.raises(BusinessRuleError, match="Confirmation expired"):
        submit(desk.session, kind, ticket)
    assert "Error ID" in desk.window.banner.message.text()


@pytest.mark.parametrize("kind", ["regime", "correction", "restore"])
def test_confirm_revokes_even_if_pre_action_render_aborts(desk, monkeypatch, kind):
    complete(desk.window)
    click(desk.window.round.new_round)
    ticket = begin(desk.window, kind)
    before, backups = desk.path.read_bytes(), desk.backups()

    def fail():
        raise RuntimeError("injected pre-action render failure")

    monkeypatch.setattr(desk.window, "_render", fail)
    confirm = {
        "regime": desk.window._start_regime,
        "correction": desk.window._confirm_correction,
        "restore": desk.window._confirm_restore,
    }[kind]
    confirm()
    assert getattr(desk.window, f"_{kind}_ticket") is None
    with pytest.raises(BusinessRuleError, match="Confirmation expired"):
        submit(desk.session, kind, ticket)
    assert desk.path.read_bytes() == before
    assert desk.backups() == backups


@pytest.mark.parametrize("cancel", ["back", "reload"])
def test_emergency_restore_cancellation_revokes_authority(paths, desktop_app, cancel):
    with StartupService(paths).start():
        pass
    paths.database.write_bytes(b"corrupt live database")
    with StartupService(paths).start() as runtime:
        host = DesktopHost(runtime)
        try:
            host.show_initial_state()
            window = host.window
            window.restore_page.candidates.setCurrentRow(0)
            click(window.restore_page.restore)
            ticket = window._restore_ticket
            assert ticket is not None
            if cancel == "back":
                click(window.restore_page.back)
            else:
                window._load_backups()
            assert window._restore_ticket is None
            with pytest.raises(BusinessRuleError, match="Confirmation expired"):
                host.lease.restore(ticket)
            assert paths.database.read_bytes() == b"corrupt live database"
            assert not list(paths.safety.iterdir())
        finally:
            host.dispose()
