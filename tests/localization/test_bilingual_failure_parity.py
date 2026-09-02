from __future__ import annotations

import shutil
import sqlite3
from contextlib import contextmanager
from datetime import timedelta

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from probability_calibration_tool.application.commands import CalculateCommand
from probability_calibration_tool.application.desktop_session import DesktopSession
from probability_calibration_tool.application.enums import WorkflowState
from probability_calibration_tool.application.errors import (
    BusinessRuleError,
    ErrorCode,
    InputValidationError,
    RoundNotCompletedError,
    RoundNotFoundError,
    RoundNotPendingError,
)
from probability_calibration_tool.application.reliability_views import StartupDisposition
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.desktop_host import DesktopHost
from probability_calibration_tool.infrastructure.backup import BackupService
from probability_calibration_tool.infrastructure.paths import AppPaths
from probability_calibration_tool.localization import Language
from probability_calibration_tool.ui.localization import (
    expected_error,
    is_public_expected_error,
)

from .qa_helpers import (
    STAMP,
    FakeClock,
    FakeIds,
    ParityHarness,
    activated_track,
    build_official_qm,
    canonical_database,
    create_seed_database,
    run_bilingual_pair,
)

VALID = CalculateCommand(1, False, 70, "2.00", "3.00")
PRIVATE = "PRIVATE sql=rounds traceback-token"


@pytest.fixture(scope="module")
def step6_failure_qm(tmp_path_factory):
    return build_official_qm(tmp_path_factory.mktemp("step6-failure-official-qm"))


@contextmanager
def _real_desktop_track(root, app, candidate_qm, language, seed):
    paths = AppPaths.from_root(root / "business")
    paths.create_directories()
    shutil.copyfile(seed, paths.database)
    business_clock = FakeClock(STAMP + timedelta(days=10))
    business_ids = FakeIds(100)
    backup = BackupService(
        paths,
        clock=FakeClock(STAMP + timedelta(days=10)),
        ids=FakeIds(1000),
    )

    def session_factory(runtime, backup_service, restore):
        return DesktopSession(
            runtime,
            backup_service,
            restore,
            clock=business_clock,
            ids=business_ids,
        )

    with (
        activated_track(app, root / "localization", language, candidate_qm) as context,
        StartupService(paths).start() as runtime,
    ):
        backup.logger = runtime.logger
        host = DesktopHost(runtime, backup=backup, session_factory=session_factory)
        host.bind_localization(context)
        try:
            host.show_initial_state()
            assert runtime.result.disposition == StartupDisposition.READY_DRAFT
            yield host, runtime, paths
        finally:
            host.dispose()


def _run_real_desktop_pair(tmp_path, app, candidate_qm, seed, scenario):
    outputs = {}
    for language in (Language.EN, Language.ZH_CN):
        with _real_desktop_track(
            tmp_path / language.value, app, candidate_qm, language, seed
        ) as track:
            outputs[language] = scenario(*track)
    assert outputs[Language.EN] == outputs[Language.ZH_CN]
    return outputs


def _click(widget):
    QTest.mouseClick(widget, Qt.MouseButton.LeftButton)


def _drive_calculate(window):
    _click(window.characters.buttons[1])
    _click(window.round.pre.reference.buttons[False])
    window.round.pre.probability.setText("70")
    window.round.pre.win_odds.setText("2.00")
    window.round.pre.lose_odds.setText("3.00")
    _click(window.round.pre.primary)


def _scalar(path, query, params=()):
    with sqlite3.connect(path) as connection:
        return connection.execute(query, params).fetchone()[0]


def _spy_unexpected(monkeypatch, host):
    reports = []
    original = host.session.report_unexpected

    def report_once(error):
        presentation = original(error)
        reports.append((error, presentation))
        return presentation

    monkeypatch.setattr(host.session, "report_unexpected", report_once)
    host.window.ports.report_unexpected = report_once
    return reports


def _unexpected_oracle(runtime, window, reports):
    assert len(reports) == 1
    error, presentation = reports[0]
    rendered = window.banner.message.text()
    log = runtime.paths.log_file.read_text(encoding="utf-8")
    assert presentation.error_id in rendered
    assert PRIVATE not in rendered and "Traceback" not in rendered
    assert PRIVATE in str(error)
    assert presentation.error_id in log and PRIVATE in log and "Traceback" in log
    return {
        "report_unexpected_count": len(reports),
        "safe_code": presentation.code,
        "error_id_present": bool(presentation.error_id),
        "private_ui_leak": PRIVATE in rendered,
        "technical_log": PRIVATE in log and "Traceback" in log,
    }


def _p12_expected_failures(h):
    workflow = h.workflow()
    workflow.set_inputs(CalculateCommand(1, False, 70, "invalid", "3.00"))
    before_invalid = canonical_database(h.path)
    with pytest.raises(InputValidationError) as validation:
        workflow.calculate()
    after_invalid = canonical_database(h.path)
    assert after_invalid == before_invalid
    validation_error = validation.value
    validation_display = expected_error(validation_error)

    h.rounds.calculate(VALID)
    with pytest.raises(BusinessRuleError) as business:
        h.regimes.start_new_regime(1, "opaque 用户 reason")
    business_error = business.value
    business_display = expected_error(business_error)

    assert PRIVATE not in validation_display + business_display
    return {
        "validation": {
            "code": validation_error.code,
            "field": validation_error.field,
            "public": is_public_expected_error(validation_error),
            "state": workflow.state,
            "database_unchanged": after_invalid == before_invalid,
            "before": before_invalid,
            "after": after_invalid,
        },
        "business": {
            "code": business_error.code,
            "public": is_public_expected_error(business_error),
        },
        "database": canonical_database(h.path),
    }


def test_p12_formal_bilingual_expected_validation_and_business_failure_parity(
    tmp_path, localization_app, step6_failure_qm
):
    run_bilingual_pair(tmp_path, localization_app, step6_failure_qm, _p12_expected_failures)


UNEXPECTED_FACTORIES = {
    "unknown": lambda: BusinessRuleError(PRIVATE, code=ErrorCode.UNKNOWN),
    "unrecognized": lambda: InputValidationError("win_odds", PRIVATE, code="unrecognized"),
    "round-not-found": lambda: RoundNotFoundError(PRIVATE),
    "round-not-pending": lambda: RoundNotPendingError(PRIVATE),
    "round-not-completed": lambda: RoundNotCompletedError(PRIVATE),
}


@pytest.mark.parametrize("case", UNEXPECTED_FACTORIES, ids=UNEXPECTED_FACTORIES)
def test_p13_formal_bilingual_unknown_and_stale_failure_parity(
    case, tmp_path, monkeypatch, localization_app, step6_failure_qm
):
    seed = tmp_path / "shared-p13-seed.db"
    create_seed_database(seed)

    def scenario(host, runtime, paths):
        before = canonical_database(paths.database)
        calls = []
        raised = []
        reports = _spy_unexpected(monkeypatch, host)
        target = host.session.workflow._target._rounds._rounds

        def fail_actual_calculate(command):
            calls.append(command)
            error = UNEXPECTED_FACTORIES[case]()
            raised.append(error)
            raise error

        monkeypatch.setattr(target, "calculate", fail_actual_calculate)
        _drive_calculate(host.window)
        after = canonical_database(paths.database)
        assert len(calls) == 1
        assert after == before
        assert len(raised) == 1 and not is_public_expected_error(raised[0])
        failure = _unexpected_oracle(runtime, host.window, reports)
        return {
            "actual_business_call_count": len(calls),
            "original_error_code": raised[0].code,
            "state": host.session.workflow.state,
            "database_unchanged": after == before,
            "before": before,
            "after": after,
            "failure": failure,
        }

    _run_real_desktop_pair(tmp_path, localization_app, step6_failure_qm, seed, scenario)


def _p14_real_calculate(monkeypatch, host, runtime, paths):
    calls = []
    failed_renders = []
    reports = _spy_unexpected(monkeypatch, host)
    target = host.session.workflow._target._rounds._rounds
    actual_calculate = target.calculate
    actual_render = host.window.round.analysis.render

    def calculate_once(command):
        calls.append(command)
        return actual_calculate(command)

    def fail_real_analysis_render(view, **kwargs):
        if view is not None:
            failed_renders.append(view.round_id)
            raise RuntimeError(PRIVATE + " calculate analysis rendering")
        return actual_render(view, **kwargs)

    monkeypatch.setattr(target, "calculate", calculate_once)
    monkeypatch.setattr(host.window.round.analysis, "render", fail_real_analysis_render)
    _drive_calculate(host.window)
    pending = _scalar(paths.database, "SELECT count(*) FROM rounds WHERE status='pending'")
    snapshots = _scalar(paths.database, "SELECT count(*) FROM round_analysis_snapshots")
    total_rounds = _scalar(paths.database, "SELECT count(*) FROM rounds")
    failure = _unexpected_oracle(runtime, host.window, reports)
    assert len(calls) == 1
    assert len(failed_renders) == 1
    assert (pending, snapshots, total_rounds) == (1, 1, 1)
    assert host.session.workflow.state == WorkflowState.PENDING_LOCKED
    return {
        "actual_business_call_count": len(calls),
        "failed_render_count": len(failed_renders),
        "pending_round_count": pending,
        "snapshot_count": snapshots,
        "total_round_count": total_rounds,
        "state": host.session.workflow.state,
        "failure": failure,
        "database": canonical_database(paths.database),
    }


def _p14_real_correction(monkeypatch, original_id, host, runtime, paths):
    window = host.window
    window.show_correction()
    window.correction.candidates.setCurrentRow(0)
    _click(window.correction.start)
    _click(window.correction.result.buttons[False])
    _click(window.correction.include.buttons[False])
    window.correction.reason.setText("opaque 更正 reason")

    reports = _spy_unexpected(monkeypatch, host)
    calls = []
    service = host.session._corrections
    actual_correction = service.correct_post_run

    def correct_once(round_id, result, include, reason):
        calls.append((round_id, result, include, reason))
        return actual_correction(round_id, result, include, reason)

    def fail_real_post_commit_refresh():
        raise RuntimeError(PRIVATE + " correction candidate refresh")

    monkeypatch.setattr(service, "correct_post_run", correct_once)
    monkeypatch.setattr(host.session, "correction_candidates", fail_real_post_commit_refresh)
    _click(window.correction.confirm)
    window._confirm_correction()  # consumed confirmation remains a no-op, never a retry

    total_rounds = _scalar(paths.database, "SELECT count(*) FROM rounds")
    original_voided = _scalar(
        paths.database,
        "SELECT count(*) FROM rounds WHERE round_id=? AND status='voided'",
        (original_id,),
    )
    replacements = _scalar(
        paths.database,
        "SELECT count(*) FROM rounds WHERE supersedes_round_id=? AND status='completed'",
        (original_id,),
    )
    supersedes = _scalar(
        paths.database, "SELECT count(*) FROM rounds WHERE supersedes_round_id IS NOT NULL"
    )
    snapshots = _scalar(paths.database, "SELECT count(*) FROM round_analysis_snapshots")
    failure = _unexpected_oracle(runtime, window, reports)
    assert len(calls) == 1
    assert calls[0] == (original_id, False, False, "opaque 更正 reason")
    assert (total_rounds, original_voided, replacements, supersedes, snapshots) == (
        2,
        1,
        1,
        1,
        2,
    )
    return {
        "actual_business_call_count": len(calls),
        "total_round_count": total_rounds,
        "original_voided_count": original_voided,
        "completed_replacement_count": replacements,
        "supersedes_relationship_count": supersedes,
        "snapshot_count": snapshots,
        "failure": failure,
        "database": canonical_database(paths.database),
    }


@pytest.mark.parametrize("variant", ["calculate", "correction"])
def test_p14_formal_bilingual_commit_then_presentation_failure_is_never_retried(
    variant, tmp_path, monkeypatch, localization_app, step6_failure_qm
):
    seed = tmp_path / "shared-p14-seed.db"
    create_seed_database(seed)
    original_id = None
    if variant == "correction":
        harness = ParityHarness(seed)
        original = harness.rounds.calculate(VALID)
        harness.rounds.complete_pending(original.round_id, True, True)
        original_id = original.round_id

    def scenario(host, runtime, paths):
        if variant == "calculate":
            return _p14_real_calculate(monkeypatch, host, runtime, paths)
        return _p14_real_correction(monkeypatch, original_id, host, runtime, paths)

    _run_real_desktop_pair(tmp_path, localization_app, step6_failure_qm, seed, scenario)
