from dataclasses import fields

import pytest

from probability_calibration_tool.application.errors import BusinessRuleError
from probability_calibration_tool.infrastructure.backup import BackupCategory

from .helpers import complete


def test_inventory_filters_corrupt_temporary_quarantine_and_unrelated(desk):
    complete(desk.window)
    good = desk.backups()[0].path
    directory = good.parent
    corrupt = directory / good.name.replace("recent_", "recent_", 1).replace(".db", "-corrupt.db")
    corrupt.write_bytes(b"not a database")
    for name in (".candidate_unfinished.tmp", "UNVERIFIED_CORRUPT.db", "unrelated.db"):
        (directory / name).write_bytes(b"test")
    candidates = desk.session.catalog.refresh()
    assert len(candidates) == 2  # startup Daily plus completed Recent
    assert {row.category for row in candidates} == {"daily", "recent"}
    for row in candidates:
        assert row.valid
        assert {field.name for field in fields(row)} == {
            "candidate_id",
            "category",
            "created_at",
            "reason",
            "valid",
        }
        assert str(directory) not in repr(row)
        assert len(row.candidate_id) == 36
        assert desk.session.catalog.resolve(row.candidate_id).exists()
    assert corrupt.exists()


def test_stale_or_arbitrary_handle_rejected_after_refresh(desk):
    first = desk.session.catalog.refresh()[0]
    second = desk.session.catalog.refresh()[0]
    assert first.candidate_id != second.candidate_id
    for handle in (first.candidate_id, str(desk.runtime.paths.database), "../probability.db"):
        with pytest.raises(BusinessRuleError, match="expired"):
            desk.session.catalog.resolve(handle)


def test_failed_refresh_also_invalidates_old_generation(desk, monkeypatch):
    first = desk.session.catalog.refresh()[0]

    def fail(category):
        if category == BackupCategory.RECENT:
            raise OSError("catalog unavailable")

    monkeypatch.setattr(desk.host.backup, "inventory", fail)
    with pytest.raises(OSError):
        desk.session.catalog.refresh()
    with pytest.raises(BusinessRuleError, match="expired"):
        desk.session.catalog.resolve(first.candidate_id)
