from datetime import UTC, datetime

import pytest
from PySide6.QtCore import Qt

from probability_calibration_tool.application.reliability_views import ReliabilityResult
from probability_calibration_tool.application.reliability_views import StartupDisposition as D
from probability_calibration_tool.infrastructure.error_reporting import ErrorPresentation
from probability_calibration_tool.ui.presentation import BackupCandidate

from .helpers import click, widget_text


@pytest.mark.parametrize("disposition", list(D))
def test_all_startup_dispositions_have_safe_presentation(window, disposition):
    result = ReliabilityResult(disposition, error=ErrorPresentation("Friendly error", "error-123"))
    window.present_startup(result)
    page = window.stack.currentWidget()
    if disposition == D.READY_DRAFT:
        assert page is window.round
    elif disposition == D.READY_RECOVERY:
        assert page is window.recovery
    elif disposition == D.EMERGENCY_RECOVERY:
        assert page is window.emergency
    elif disposition == D.RECOVERY_ERROR:
        assert page is window.recovery_error
    else:
        assert page is window.safety
    if disposition not in (D.READY_DRAFT, D.READY_RECOVERY):
        assert not window.round_button.isEnabled()
        assert not window.characters.buttons[1].isEnabled()
    assert "error-123" in widget_text(window)
    assert "Traceback" not in widget_text(window)
    if disposition == D.UNSUPPORTED_NEWER_SCHEMA:
        assert "will not write" in widget_text(page)
        assert "Force Open" not in widget_text(page)


def test_emergency_requires_explicit_valid_selection_and_injected_action(window, qapp):
    calls = []
    window.ports.request_restore = lambda candidate_id: (
        calls.append(candidate_id) or "Request received."
    )
    candidates = (
        BackupCandidate("valid", "Recent", datetime(2026, 9, 1, tzinfo=UTC)),
        BackupCandidate("corrupt", "Unavailable", datetime(2026, 9, 1, tzinfo=UTC), valid=False),
    )
    window.present_startup(ReliabilityResult(D.EMERGENCY_RECOVERY), candidates=candidates)
    qapp.processEvents()
    page = window.emergency
    assert page.candidates.currentRow() == -1
    assert not page.restore.isEnabled() and calls == []
    assert not (page.candidates.item(1).flags() & Qt.ItemFlag.ItemIsSelectable)
    page.candidates.setCurrentRow(1)
    window.render_from_workflow()
    assert not page.restore.isEnabled()
    page.candidates.setCurrentRow(0)
    window.render_from_workflow()
    assert page.restore.isEnabled()
    click(page.restore)
    assert calls == ["valid"]
    assert "Request received" in window.banner.message.text()


def test_operational_warning_does_not_claim_transaction_failed(window):
    window.present_startup(
        ReliabilityResult(
            D.READY_DRAFT, ("Saved successfully; Recent backup could not be created.",)
        )
    )
    assert window.stack.currentWidget() is window.round
    assert "Saved successfully" in window.banner.message.text()
    assert "Warning:" in window.banner.message.text()
