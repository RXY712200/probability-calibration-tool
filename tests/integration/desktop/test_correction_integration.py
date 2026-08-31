from dataclasses import FrozenInstanceError, fields, replace

import pytest

from probability_calibration_tool.application.errors import BusinessRuleError, InputValidationError
from probability_calibration_tool.infrastructure.backup import BackupCategory

from .helpers import begin_correction, click, complete, fail_recent, rows, scalar, text_tree


@pytest.mark.parametrize("recent_failure", [False, True])
def test_real_correction_safety_commit_recent_and_both_refreshes(desk, monkeypatch, recent_failure):
    original_id = complete(desk.window)
    with desk.runtime.uow_factory()() as uow:
        original = uow.rounds.get(original_id)
        snapshot = uow.snapshots.get(original_id)
    click(desk.window.round.new_round)
    if recent_failure:
        fail_recent(desk, monkeypatch)
    events = []
    create = desk.host.backup.create

    def ordered_create(category, reason=None):
        events.append(category.value)
        status = scalar(desk.path, "SELECT status FROM rounds WHERE round_id=?", (original_id,))
        assert status == ("completed" if category == BackupCategory.SAFETY else "voided")
        if category == BackupCategory.SAFETY:
            assert reason == "pre_history_correction"
        return create(category, reason)

    monkeypatch.setattr(desk.host.backup, "create", ordered_create)
    begin_correction(desk.window)
    candidates = desk.session.correction_candidates
    maintenance = desk.session.maintenance_rows

    def candidates_after():
        events.append("candidates")
        return candidates()

    def maintenance_after():
        events.append("maintenance")
        return maintenance()

    monkeypatch.setattr(desk.session, "correction_candidates", candidates_after)
    monkeypatch.setattr(desk.session, "maintenance_rows", maintenance_after)
    ticket = desk.window._correction_ticket
    desk.window._confirm_correction()
    desk.window._confirm_correction()
    with pytest.raises(BusinessRuleError, match="expired"):
        desk.session.correct(ticket, False, True, "duplicate")
    assert events == ["safety", "recent", "candidates", "maintenance"]
    replacement_id = desk.window.correction.rows[0].round_id
    assert replacement_id != original_id
    with desk.runtime.uow_factory()() as uow:
        old, new = uow.rounds.get(original_id), uow.rounds.get(replacement_id)
        assert old.status.value == "voided"
        assert new.status.value == "completed"
        assert new.supersedes_round_id == original_id
        assert new.calculated_at == original.calculated_at
        assert new.result is False and new.include_character_history is True
        assert uow.snapshots.get(original_id) == snapshot
        assert uow.snapshots.get(replacement_id) == replace(snapshot, round_id=replacement_id)
    assert scalar(desk.path, "SELECT count(*) FROM rounds") == 2
    assert scalar(desk.path, "SELECT losses FROM character_stats WHERE character_id=1") == 1
    assert len(desk.backups(BackupCategory.SAFETY)) == 1
    assert "Correction saved" in desk.window.correction.notice.text()
    assert desk.window.maintenance.rows[0].included_sample_count == 1
    safety = desk.backups(BackupCategory.SAFETY)[0].path
    assert (
        scalar(safety, "SELECT status FROM rounds WHERE round_id=?", (original_id,)) == "completed"
    )
    if recent_failure:
        assert "Recent backup failed" in desk.window.banner.message.text()
        assert len(desk.backups()) == 1  # original completion only
    else:
        assert len(desk.backups()) == 2
        newest = max(desk.backups(), key=lambda e: e.created_at).path
        assert (
            scalar(
                newest, "SELECT supersedes_round_id FROM rounds WHERE round_id=?", (replacement_id,)
            )
            == original_id
        )


def test_safety_failure_blocks_correction_write_transaction_and_recent(desk, monkeypatch):
    original_id = complete(desk.window)
    click(desk.window.round.new_round)
    before_rounds, before_stats = rows(desk.path, "rounds"), rows(desk.path, "character_stats")
    recent_before = desk.backups()
    events = []
    factory = desk.session._corrections._uow_factory

    def counted_factory():
        events.append("preflight-uow")
        return factory()

    def fail(category, reason=None):
        events.append(category.value)
        raise OSError("injected Safety failure")

    monkeypatch.setattr(desk.session._corrections, "_uow_factory", counted_factory)
    monkeypatch.setattr(desk.host.backup, "create", fail)
    begin_correction(desk.window)
    click(desk.window.correction.confirm)
    assert events == ["preflight-uow", "safety"]
    assert rows(desk.path, "rounds") == before_rounds
    assert rows(desk.path, "character_stats") == before_stats
    assert (
        scalar(desk.path, "SELECT status FROM rounds WHERE round_id=?", (original_id,))
        == "completed"
    )
    assert desk.backups() == recent_before
    assert not desk.backups(BackupCategory.SAFETY)
    assert "Error ID" in desk.window.banner.message.text()


@pytest.mark.parametrize(
    "result,include,reason",
    [
        (False, True, ""),
        (False, True, "   \t"),
        (None, True, "repair"),
        (True, None, "repair"),
        ("loss", True, "repair"),
        (False, 1, "repair"),
    ],
)
def test_invalid_correction_fields_never_create_safety(desk, result, include, reason):
    original = complete(desk.window)
    click(desk.window.round.new_round)
    ticket = desk.session.begin_correction(original)
    with pytest.raises(InputValidationError):
        desk.session.correct(ticket, result, include, reason)
    assert not desk.backups(BackupCategory.SAFETY)
    assert scalar(desk.path, "SELECT count(*) FROM rounds") == 1


def test_candidate_dtos_are_minimal_detached_and_ui_cannot_browse_old_facts(desk):
    complete(desk.window)
    click(desk.window.round.new_round)
    candidates = desk.session.correction_candidates()
    maintenance = desk.session.maintenance_rows()
    with desk.runtime.quiescent():
        assert candidates[0].display_name == "Isaac"
        assert len(maintenance) == 34
        assert candidates[0].completed_at.tzinfo is not None
        assert {f.name for f in fields(candidates[0])} == {
            "round_id",
            "display_name",
            "completed_at",
        }
        with pytest.raises(FrozenInstanceError):
            candidates[0].display_name = "changed"
    desk.window.show_correction()
    content = text_tree(desk.window.correction)
    for forbidden in ("2.00", "3.00", "70%", "Jeffreys", "EV", "posterior", "0.92857"):
        assert forbidden not in content
    assert desk.window.correction.rows == candidates
    assert desk.window.correction.selected() is None
    assert desk.window.correction.result.value() is None
    assert desk.window.correction.include.value() is None
    assert len(desk.window.correction.findChildren(type(desk.window.correction.reason))) == 1


@pytest.mark.parametrize("reason", ["", " "])
def test_correction_ui_requires_explicit_facts_and_nonempty_reason(desk, reason):
    complete(desk.window)
    click(desk.window.round.new_round)
    begin_correction(desk.window, reason=reason)
    assert not desk.window.correction.confirm.isEnabled()
    assert not desk.backups(BackupCategory.SAFETY)
    desk.window.correction.reason.setText("audit fix")
    assert desk.window.correction.confirm.isEnabled()
