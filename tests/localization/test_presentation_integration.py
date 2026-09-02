import shutil
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path

import pytest

from probability_calibration_tool.application.desktop_session import DesktopSession
from probability_calibration_tool.application.errors import (
    BusinessRuleError,
    ErrorCode,
    InputValidationError,
    RoundNotCompletedError,
    RoundNotFoundError,
    RoundNotPendingError,
)
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.core.errors import CoreValidationCode, InvalidOddsError
from probability_calibration_tool.core.validation import parse_odds_text, validate_odds
from probability_calibration_tool.desktop_host import DesktopHost
from probability_calibration_tool.infrastructure.backup import BackupCategory, BackupService
from probability_calibration_tool.infrastructure.paths import AppPaths
from probability_calibration_tool.localization import Language, initialize_localization
from probability_calibration_tool.ui.language_dialog import LanguageDialog

from . import test_presentation

marker = test_presentation.marker


@pytest.fixture
def rig(tmp_path, monkeypatch, localization_app):
    monkeypatch.syspath_prepend(str(Path(__file__).parents[1] / "integration"))
    from desktop.helpers import DesktopRig

    with StartupService(AppPaths.from_root(tmp_path / "desktop")).start() as runtime:
        host = DesktopHost(runtime)
        try:
            host.show_initial_state()
            yield DesktopRig(runtime, host)
        finally:
            host.dispose()


@pytest.mark.parametrize("translated", [False, True])
@pytest.mark.parametrize(
    "case",
    [
        "unexpected_error_id_safe_ui_and_matching_full_traceback_log",
        "committed_calculate_render_failure_does_not_retry",
        "committed_complete_render_failure_does_not_retry",
        "regime_refresh_failure_does_not_repeat_successful_business_commit",
        "warning_presentation_failure_does_not_retry_commit",
    ],
)
def test_existing_error_and_no_retry_assertions_in_both_presentations(
    rig, monkeypatch, marker, translated, case
):
    from desktop import test_error_boundary

    if translated:
        marker()
        rig.host.show_initial_state()
    getattr(test_error_boundary, "test_" + case)(rig, monkeypatch)


@pytest.mark.parametrize("translated", [False, True])
def test_correction_refresh_failure_and_warning_priority_in_both_presentations(
    rig, monkeypatch, marker, translated
):
    from desktop.test_compound_failure_priority import (
        test_correction_commit_recent_failure_refresh_failure_retains_unexpected_id,
    )

    if translated:
        marker()
        rig.host.show_initial_state()
    test_correction_commit_recent_failure_refresh_failure_retains_unexpected_id(
        rig, monkeypatch, "correction_candidates"
    )


def test_localization_helper_failure_after_calculate_never_reexecutes(rig, monkeypatch, marker):
    from desktop.helpers import calculate, scalar

    from probability_calibration_tool.ui import analysis_panel

    marker()
    calls = []
    original = rig.session.workflow._target._rounds._rounds.calculate

    def calculate_once(command):
        calls.append(command)
        return original(command)

    def fail(*args):
        raise RuntimeError("secret localization helper failure")

    monkeypatch.setattr(rig.session.workflow._target._rounds._rounds, "calculate", calculate_once)
    monkeypatch.setattr(analysis_panel, "template", fail)
    calculate(rig.window)
    assert len(calls) == 1 and scalar(rig.path, "SELECT count(*) FROM rounds") == 1
    assert "Error ID:" in rig.window.banner.message.text()
    assert "secret" not in rig.window.banner.message.text()


def test_error_localization_itself_fails_nonrecursively_with_same_id(rig, monkeypatch):
    from desktop.helpers import calculate, scalar

    from probability_calibration_tool.ui import analysis_panel, localization

    reports = []
    original = rig.session.report_unexpected

    def report(exc):
        result = original(exc)
        reports.append(result)
        return result

    def fail(*args):
        raise RuntimeError("SECRET broken translation helper")

    monkeypatch.setattr(rig.session, "report_unexpected", report)
    monkeypatch.setattr(analysis_panel, "template", fail)
    monkeypatch.setattr(localization, "template", fail)
    calculate(rig.window)
    assert scalar(rig.path, "SELECT count(*) FROM rounds") == 1
    assert len(reports) == 1
    assert reports[0].error_id in rig.window.banner.message.text()
    assert "SECRET" not in rig.window.banner.message.text()
    log = rig.runtime.paths.log_file.read_text()
    assert reports[0].error_id in log and "SECRET" in log and "Traceback" in log


def test_core_application_semantic_map_is_explicit_exhaustive():
    from probability_calibration_tool.application.analysis_builder import (
        CORE_INPUT_ERRORS,
        _input_failure,
    )
    from probability_calibration_tool.core.errors import CoreValidationError

    assert set(CORE_INPUT_ERRORS) == set(CoreValidationCode) - {CoreValidationCode.UNKNOWN}
    for code, (expected, _) in CORE_INPUT_ERRORS.items():
        error = _input_failure("win_odds", CoreValidationError("PRIVATE diagnostic", code=code))
        assert error.field == "win_odds" and error.code == expected
        assert "PRIVATE" not in str(error)


@pytest.mark.parametrize(
    "field,code,text",
    [
        ("win_odds", ErrorCode.ODDS_NUMERIC, "Odds must be a finite numeric multiplier."),
        ("win_odds", ErrorCode.ODDS_RANGE, "Odds must be finite and at least 1."),
        ("lose_odds", ErrorCode.ODDS_SYNTAX, "Odds must use unsigned decimal notation."),
    ],
)
def test_input_placement_by_field_message_by_code_never_diagnostic(
    rig, monkeypatch, marker, field, code, text
):
    from desktop.helpers import calculate

    marker()

    def fail(*args):
        raise InputValidationError(field, "PRIVATE SQL pending_edit", code=code)

    monkeypatch.setattr(rig.session.workflow._target._rounds._rounds, "calculate", fail)
    calculate(rig.window)
    assert rig.window.round.pre.errors[field].text() == "⟦Errors⟧ " + text
    other = "lose_odds" if field == "win_odds" else "win_odds"
    assert not rig.window.round.pre.errors[other].text()


@pytest.mark.parametrize("translated", [False, True])
@pytest.mark.parametrize(
    "failure_factory",
    [
        partial(
            InputValidationError,
            "win_odds",
            "PRIVATE unrecognized input diagnostic",
            code="unrecognized",
        ),
        partial(
            BusinessRuleError,
            "PRIVATE unknown business diagnostic",
            code=ErrorCode.UNKNOWN,
        ),
        partial(RoundNotFoundError, "PRIVATE stale round_not_found diagnostic"),
        partial(RoundNotPendingError, "PRIVATE stale pending lifecycle diagnostic"),
        partial(RoundNotCompletedError, "PRIVATE stale completed lifecycle diagnostic"),
    ],
    ids=["unrecognized-input", "unknown-business", "not-found", "not-pending", "not-completed"],
)
def test_internal_or_unmapped_expected_error_uses_unexpected_id_and_full_log(
    rig, monkeypatch, marker, translated, failure_factory
):
    from desktop.helpers import calculate, scalar

    if translated:
        marker()
        rig.host.show_initial_state()
    calls = []

    def fail(*args):
        calls.append(args)
        raise failure_factory()

    monkeypatch.setattr(rig.session.workflow._target._rounds._rounds, "calculate", fail)
    calculate(rig.window)
    text = rig.window.banner.message.text()
    assert len(calls) == 1 and scalar(rig.path, "SELECT count(*) FROM rounds") == 0
    assert "Error ID:" in text and "PRIVATE" not in text
    assert "round_not_found" not in text and "pending lifecycle" not in text
    log = rig.runtime.paths.log_file.read_text()
    assert "PRIVATE" in log and "Traceback" in log


def test_internal_error_after_committed_calculate_is_not_retried(rig, monkeypatch):
    from desktop.helpers import calculate, scalar

    calls = []
    original = rig.session.workflow._target._rounds._rounds.calculate

    def commit_then_fail(command):
        calls.append(command)
        original(command)
        raise RoundNotFoundError("PRIVATE stale record after committed Calculate")

    monkeypatch.setattr(rig.session.workflow._target._rounds._rounds, "calculate", commit_then_fail)
    calculate(rig.window)
    assert len(calls) == 1 and scalar(rig.path, "SELECT count(*) FROM rounds") == 1
    assert "Error ID:" in rig.window.banner.message.text()
    assert "PRIVATE" not in rig.window.banner.message.text()
    assert "PRIVATE stale record" in rig.runtime.paths.log_file.read_text()


def test_direct_main_and_safety_paths_cannot_render_internal_codes(rig, monkeypatch):
    from probability_calibration_tool.ui.main_window import MainWindow
    from probability_calibration_tool.ui.safety_window import SafetyWindow

    reports = []
    original = rig.session.report_unexpected

    def report(exc):
        result = original(exc)
        reports.append((exc, result))
        return result

    rig.window.ports.report_unexpected = report
    monkeypatch.setattr(rig.session, "report_unexpected", report)

    def unknown_business():
        raise BusinessRuleError("PRIVATE direct MainWindow diagnostic", code=ErrorCode.UNKNOWN)

    MainWindow._invoke(rig.window, unknown_business)
    assert reports[-1][1].error_id in rig.window.banner.message.text()
    assert "PRIVATE" not in rig.window.banner.message.text()
    SafetyWindow._input_error(
        rig.window, InputValidationError("win_odds", "PRIVATE SafetyWindow diagnostic")
    )
    assert reports[-1][1].error_id in rig.window.banner.message.text()
    assert "PRIVATE" not in rig.window.banner.message.text()
    log = rig.runtime.paths.log_file.read_text()
    assert "PRIVATE direct MainWindow" in log and "PRIVATE SafetyWindow" in log


@pytest.mark.parametrize(
    "value,code",
    [
        (True, CoreValidationCode.ODDS_NUMERIC),
        ("2", CoreValidationCode.ODDS_NUMERIC),
        (10**10000, CoreValidationCode.ODDS_BINARY64),
        (float("nan"), CoreValidationCode.ODDS_RANGE),
        (float("inf"), CoreValidationCode.ODDS_RANGE),
        (float("-inf"), CoreValidationCode.ODDS_RANGE),
        (0.99, CoreValidationCode.ODDS_RANGE),
    ],
    ids=[
        "boolean",
        "numeric-string",
        "oversized",
        "nan",
        "positive-inf",
        "negative-inf",
        "below-one",
    ],
)
def test_core_invalid_sets_and_semantic_classification_unchanged(value, code):
    with pytest.raises(InvalidOddsError) as caught:
        validate_odds(value)
    assert caught.value.code == code


@pytest.mark.parametrize("value", ["-2", "+2", "1e2", " 2", ".2", ""])
def test_core_decimal_syntax_classification(value):
    with pytest.raises(InvalidOddsError) as caught:
        parse_odds_text(value)
    assert caught.value.code == CoreValidationCode.ODDS_SYNTAX


def test_unclassified_core_failure_uses_safe_unexpected_boundary(rig, monkeypatch, marker):
    from desktop.helpers import calculate

    from probability_calibration_tool import core
    from probability_calibration_tool.core.errors import CoreValidationError

    marker()

    def fail(*args):
        raise CoreValidationError("SECRET unclassified SQL failure")

    monkeypatch.setattr(core, "parse_odds_text", fail)
    calculate(rig.window)
    assert "Error ID:" in rig.window.banner.message.text()
    assert "SECRET" not in rig.window.banner.message.text()
    assert "SECRET" in rig.runtime.paths.log_file.read_text()


TABLES = {
    "characters",
    "history_regimes",
    "rounds",
    "round_analysis_snapshots",
    "character_stats",
    "meta",
}


def logical_database(path):
    with closing(sqlite3.connect(path)) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 1
        names = {
            row[0]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        assert names == TABLES
        return {
            table: db.execute(f"SELECT * FROM {table} ORDER BY 1, 2").fetchall()
            for table in sorted(TABLES)
        }


def test_deterministic_english_translated_business_database_backup_restore_parity(
    tmp_path, monkeypatch, marker, localization_app
):
    monkeypatch.syspath_prepend(str(Path(__file__).parents[1] / "integration"))
    from application.helpers import STAMP, FakeClock, FakeIdGenerator, Harness
    from desktop.helpers import begin_correction, calculate, click

    from probability_calibration_tool.persistence.repositories import meta, stats

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return (STAMP + timedelta(days=2)).astimezone(tz)

    # Cache/meta persistence has its own audit clock, separate from Application's
    # injected clock. Freeze it too; compare every stored field, including timestamps.
    monkeypatch.setattr(stats, "datetime", FixedDatetime)
    monkeypatch.setattr(meta, "datetime", FixedDatetime)
    seed = Harness(tmp_path / "identical-seed.db")
    seed.seed_history(19, 1)

    def scenario(root):
        paths = AppPaths.from_root(root)
        paths.database.parent.mkdir(parents=True)
        shutil.copyfile(seed.path, paths.database)
        clock, ids = FakeClock(STAMP + timedelta(days=2)), FakeIdGenerator(100)
        backup_calls, states = [], []

        class Backup(BackupService):
            def create(self, category, reason=None):
                backup_calls.append((category, reason))
                return super().create(category, reason)

        def session_factory(runtime, backup, restore):
            return DesktopSession(runtime, backup, restore, clock=clock, ids=ids)

        # Real close/start/Recovery retains the exact pending prediction and snapshot.
        with StartupService(paths).start() as runtime:
            host = DesktopHost(runtime, backup=Backup(paths), session_factory=session_factory)
            try:
                host.show_initial_state()
                first = calculate(host.window, reference=True)
                states.append(host.window.workflow.state)
                click(host.window.round.pre.modify)
                host.window.round.pre.probability.setText("0")
                click(host.window.round.pre.primary)
                prediction = host.window.workflow.analysis
                assert prediction.round_id == first.round_id and prediction.subjective.p_h_raw == 0
                states.append(host.window.workflow.state)
                before_recovery = logical_database(paths.database)
            finally:
                host.dispose()
        context = initialize_localization(localization_app, paths.root)
        with StartupService(paths).start() as runtime:
            host = DesktopHost(runtime, backup=Backup(paths), session_factory=session_factory)
            host.bind_localization(context)
            try:
                host.show_initial_state()
                states.append(host.window.workflow.state)
                click(host.window.recovery.continue_button)
                assert host.window.workflow.analysis == prediction
                assert logical_database(paths.database) == before_recovery
                click(host.window.round.post.result.buttons[True])
                click(host.window.round.post.include.buttons[True])
                click(host.window.round.post.save)
                states.append(host.window.workflow.state)
                completed = logical_database(paths.database)
                candidate = next(
                    entry.path for entry in host.backup.inventory(BackupCategory.RECENT)
                )
                click(host.window.round.new_round)
                begin_correction(host.window, reason="same correction")
                host.window._confirm_correction()
                corrected = logical_database(paths.database)
                host.window.show_round()
                host.window.show_maintenance()
                host.window.maintenance.table.selectRow(0)
                click(host.window.maintenance.start)
                host.window.maintenance.reason.setText("same regime")
                host.window._start_regime()
                after_regime = logical_database(paths.database)
                # Preference save is independent of all six tables and backup triggers.
                calls_before = list(backup_calls)
                dialog = LanguageDialog(context)
                dialog._confirm()
                assert logical_database(paths.database) == after_regime
                assert backup_calls == calls_before
                settings_before = context.settings_path.read_bytes()
                host.window.show_restore()
                index = next(
                    i
                    for i, row in enumerate(host.window.restore_page.rows)
                    if host.session.catalog.resolve(row.candidate_id) == candidate
                )
                host.window.restore_page.candidates.setCurrentRow(index)
                host.window._begin_restore()
                old = host.session
                host.window._confirm_restore()
                assert host.session is not old and old.disposed
                states.append(host.window.workflow.state)
                restored = logical_database(paths.database)
                assert restored == completed
                assert context.settings_path.read_bytes() == settings_before
                assert context.preferred_language == context.effective_language == Language.EN
                # Backup files contain exactly business tables, never settings/catalog payloads.
                assert logical_database(candidate) == completed
                assert not any(
                    p.name == "settings.ini" or p.suffix in {".ts", ".qm"}
                    for p in (paths.root / "backups").rglob("*")
                )
                return (
                    states,
                    prediction,
                    completed,
                    corrected,
                    after_regime,
                    restored,
                    backup_calls,
                )
            finally:
                host.dispose()

    english = scenario(tmp_path / "english")
    marker()
    translated = scenario(tmp_path / "translated")
    assert translated == english
