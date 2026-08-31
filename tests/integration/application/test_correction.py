from dataclasses import asdict, replace
from inspect import signature

import pytest

from probability_calibration_tool import core
from probability_calibration_tool.application import CorrectionService
from probability_calibration_tool.application.errors import (
    CorrectionBlockedError,
    InputValidationError,
    RoundNotCompletedError,
    RoundNotFoundError,
)
from probability_calibration_tool.domain.enums import RoundStatus
from probability_calibration_tool.persistence.repositories import (
    CharacterStatsRepository,
    RoundRepository,
    SnapshotRepository,
)
from probability_calibration_tool.persistence.unit_of_work import UnitOfWork

from .helpers import COMMAND, InjectedFailure


def test_correction_exact_a_b_facts_timestamps_and_snapshot_without_math(h, monkeypatch):
    h.seed_history()
    command = replace(COMMAND, reference_history=True)
    view = h.rounds.calculate(command)
    exposure_time = h.clock.now()
    prediction_time = h.clock.advance()
    h.rounds.recalculate(view.round_id, replace(command, p_h_raw=80))
    h.clock.advance()
    h.rounds.complete_pending(view.round_id, True, True)
    original, snapshot = h.record(view.round_id), h.snapshot(view.round_id)
    assert original.revision_count == 1 and original.subjective_independence_compromised
    correction_time = h.clock.advance()

    def forbidden(*args):
        pytest.fail("Correction must copy the saved prediction, never rerun Core")

    for function in (
        "compute_historical_estimate",
        "compute_subjective_estimate",
        "analyze_historical_odds",
        "analyze_subjective_odds",
        "classify_model_relation",
    ):
        monkeypatch.setattr(core, function, forbidden)
    result = h.corrections.correct_post_run(view.round_id, False, True, "Wrong outcome")
    a, b = h.record(view.round_id), h.record(result.replacement_round_id)
    assert a == replace(
        original,
        status=RoundStatus.VOIDED,
        voided_at=correction_time,
        void_reason="Wrong outcome",
        last_updated_at=correction_time,
    )
    assert b == replace(
        original,
        round_id=result.replacement_round_id,
        supersedes_round_id=original.round_id,
        created_at=correction_time,
        last_updated_at=correction_time,
        completed_at=correction_time,
        result=False,
    )
    assert b.calculated_at == prediction_time == a.calculated_at
    assert b.history_exposed_at == exposure_time == a.history_exposed_at
    assert h.snapshot(a.round_id) == snapshot
    assert h.snapshot(b.round_id) == replace(snapshot, round_id=b.round_id)
    assert asdict(h.snapshot(b.round_id)) == {**asdict(snapshot), "round_id": b.round_id}
    assert h.snapshot(b.round_id).history_data_through_at == prediction_time
    assert result.corrected_at == correction_time and result.original_round_id == original.round_id
    assert result.result is False and result.include_character_history is True
    assert h.backup.calls == ["pre_history_correction"]
    stats = h.stats()
    assert (stats.included_games, stats.wins, stats.losses) == (21, 19, 2)
    # Original record retained its ORIGINAL post-run facts for audit.
    assert a.result is True and a.include_character_history is True
    assert a.completed_at == original.completed_at


@pytest.mark.parametrize("original_include", [False, True])
@pytest.mark.parametrize("corrected_include", [False, True])
def test_correction_rebuilds_source_stats_for_inclusion_changes(
    h, original_include, corrected_include
):
    h.seed_history(1, 0)
    view = h.rounds.calculate(COMMAND)
    h.rounds.complete_pending(view.round_id, True, original_include)
    result = h.corrections.correct_post_run(
        view.round_id, False, corrected_include, "post-run facts"
    )
    stats = h.stats()
    assert (stats.included_games, stats.wins, stats.losses) == (
        1 + corrected_include,
        1,
        int(corrected_include),
    )
    with h.factory() as uow:
        ids = [record.round_id for record in uow.rounds.eligible_history(1, stats.regime_id)]
    assert view.round_id not in ids
    assert (result.replacement_round_id in ids) is corrected_include


def test_backup_failure_precedes_any_correction_transaction_or_id_generation(h):
    original_id = h.seed_history(1, 0)[0]
    before = h.capture()
    id_count = h.ids.count
    events = []

    class TracedUow(UnitOfWork):
        def __enter__(self):
            events.append("preflight_enter" if not events else "correction_enter")
            return super().__enter__()

        def __exit__(self, *args):
            super().__exit__(*args)
            events.append("preflight_closed")

    def backup_observer():
        assert events == ["preflight_enter", "preflight_closed"]
        assert h.capture() == before
        events.append("backup_failed")

    h.backup.on_backup = backup_observer
    h.backup.fail = True
    service = CorrectionService(lambda: TracedUow(h.path), h.clock, h.ids, h.backup)
    with pytest.raises(InjectedFailure, match="Safety verification"):
        service.correct_post_run(original_id, False, True, "wrong result")
    assert events == ["preflight_enter", "preflight_closed", "backup_failed"]
    assert h.capture() == before and h.ids.count == id_count
    assert h.backup.calls == ["pre_history_correction"]


def test_verified_backup_finishes_before_first_mutation(h, monkeypatch):
    original_id = h.seed_history(1, 0)[0]
    events = []
    h.backup.on_backup = lambda: events.append("verified_backup")
    original = RoundRepository.update

    def update(self, record):
        assert events == ["verified_backup"]
        events.append("void_A")
        original(self, record)

    monkeypatch.setattr(RoundRepository, "update", update)
    h.corrections.correct_post_run(original_id, False, True, "wrong result")
    assert events == ["verified_backup", "void_A"]


@pytest.mark.parametrize("failure", ["after_A", "B_snapshot", "stats", "commit"])
def test_correction_rollback_restores_a_snapshot_and_stats_and_removes_b(h, monkeypatch, failure):
    original_id = h.seed_history(1, 1)[0]
    before = h.capture()
    h.clock.advance()
    original_snapshot_insert = SnapshotRepository.insert
    original_stats = CharacterStatsRepository.rebuild_stats

    def fail_insert(*args):
        assert h.backup.calls == ["pre_history_correction"]
        raise InjectedFailure("after A")

    def fail_snapshot(self, snapshot):
        original_snapshot_insert(self, snapshot)
        raise InjectedFailure("after B snapshot")

    def fail_stats(self, *args):
        original_stats(self, *args)
        raise InjectedFailure("after stats")

    def fail_commit(self):
        raise InjectedFailure("commit")

    if failure == "after_A":
        monkeypatch.setattr(RoundRepository, "insert", fail_insert)
    elif failure == "B_snapshot":
        monkeypatch.setattr(SnapshotRepository, "insert", fail_snapshot)
    elif failure == "stats":
        monkeypatch.setattr(CharacterStatsRepository, "rebuild_stats", fail_stats)
    else:
        monkeypatch.setattr(UnitOfWork, "commit", fail_commit)
    with pytest.raises(InjectedFailure):
        h.corrections.correct_post_run(original_id, False, True, "wrong result")
    assert h.capture() == before
    assert h.record(original_id).status == RoundStatus.COMPLETED
    assert h.backup.calls == ["pre_history_correction"]


def test_correction_chains_allowed_but_branching_is_semantic_error(h):
    a_id = h.seed_history(1, 0)[0]
    a_snapshot = h.snapshot(a_id)
    b = h.corrections.correct_post_run(a_id, False, True, "first correction")
    h.clock.advance()
    c = h.corrections.correct_post_run(b.replacement_round_id, True, True, "second correction")
    assert h.record(a_id).status == RoundStatus.VOIDED
    assert h.record(b.replacement_round_id).status == RoundStatus.VOIDED
    assert h.record(c.replacement_round_id).status == RoundStatus.COMPLETED
    assert h.record(c.replacement_round_id).supersedes_round_id == b.replacement_round_id
    assert h.snapshot(a_id) == a_snapshot
    assert h.snapshot(c.replacement_round_id) == replace(
        a_snapshot, round_id=c.replacement_round_id
    )
    assert (h.stats().included_games, h.stats().wins, h.stats().losses) == (1, 1, 0)
    before = h.capture()
    backup_calls = h.backup.calls[:]
    for old_id in (a_id, b.replacement_round_id):
        with pytest.raises(RoundNotCompletedError):
            h.corrections.correct_post_run(old_id, False, False, "would branch")
    assert h.capture() == before and h.backup.calls == backup_calls


@pytest.mark.parametrize(
    "field",
    [
        "character_id",
        "p_h_raw",
        "win_odds_raw",
        "lose_odds_raw",
        "win_odds",
        "lose_odds",
        "reference_history",
        "snapshot",
        "history_regime_id",
    ],
)
def test_prerun_correction_is_impossible_in_public_api(h, field):
    original_id = h.seed_history(1, 0)[0]
    before = h.capture()
    assert set(signature(h.corrections.correct_post_run).parameters) == {
        "round_id",
        "result",
        "include_character_history",
        "reason",
    }
    with pytest.raises(TypeError):
        h.corrections.correct_post_run(original_id, False, True, "not permitted", **{field: 42})
    assert h.capture() == before and h.backup.calls == []


@pytest.mark.parametrize("reason", [None, "", " \t\n", 123])
def test_correction_requires_nonempty_text_reason(h, reason):
    original_id = h.seed_history(1, 0)[0]
    before = h.capture()
    with pytest.raises(InputValidationError) as caught:
        h.corrections.correct_post_run(original_id, False, True, reason)
    assert caught.value.field == "reason"
    assert h.capture() == before and h.backup.calls == []


@pytest.mark.parametrize(
    "result,include,field", [(1, True, "result"), (True, None, "include_character_history")]
)
def test_correction_fact_validation(h, result, include, field):
    original_id = h.seed_history(1, 0)[0]
    before = h.capture()
    with pytest.raises(InputValidationError) as caught:
        h.corrections.correct_post_run(original_id, result, include, "wrong facts")
    assert caught.value.field == field
    assert h.capture() == before and h.backup.calls == []


def test_pending_anywhere_blocks_correction_before_backup(h):
    original_id = h.seed_history(1, 0)[0]
    pending = h.rounds.calculate(replace(COMMAND, character_id=2))
    before = h.capture()
    for target in (original_id, pending.round_id):
        with pytest.raises(CorrectionBlockedError):
            h.corrections.correct_post_run(target, False, True, "blocked")
    assert h.capture() == before and h.backup.calls == []


def test_missing_correction_target_is_semantic_error(h):
    before = h.capture()
    with pytest.raises(RoundNotFoundError):
        h.corrections.correct_post_run("missing", False, True, "wrong result")
    assert h.capture() == before and h.backup.calls == []


def test_correction_rechecks_pending_after_backup(h):
    original_id = h.seed_history(1, 0)[0]
    original, snapshot, stats = h.record(original_id), h.snapshot(original_id), h.stats()
    h.backup.on_backup = lambda: h.rounds.calculate(replace(COMMAND, character_id=2))
    with pytest.raises(CorrectionBlockedError):
        h.corrections.correct_post_run(original_id, False, True, "racing pending")
    assert h.record(original_id) == original
    assert h.snapshot(original_id) == snapshot and h.stats() == stats


def test_correction_of_old_regime_rebuilds_only_that_regime(h):
    original_id = h.seed_history(1, 0)[0]
    old_regime_id = h.record(original_id).history_regime_id
    h.regimes.start_new_regime(1, "new")
    current_stats = h.stats()
    h.corrections.correct_post_run(original_id, False, True, "old result")
    assert h.stats() == current_stats
    old_stats = h.stats(1, old_regime_id)
    assert (old_stats.included_games, old_stats.wins, old_stats.losses) == (1, 0, 1)


def test_leakage_round21_stays_at_twenty_after_completion_and_later_correction(h):
    prior = h.seed_history(19, 1)
    round21 = h.rounds.calculate(replace(COMMAND, reference_history=True))
    prediction = h.snapshot(round21.round_id)
    assert (prediction.history_wins, prediction.history_losses, prediction.history_sample_size) == (
        19,
        1,
        20,
    )
    assert prediction.last_included_historical_round_id == prior[-1]
    h.clock.advance()
    h.rounds.complete_pending(round21.round_id, True, True)
    assert (h.stats().included_games, h.stats().wins, h.stats().losses) == (21, 20, 1)
    assert h.snapshot(round21.round_id) == prediction
    h.clock.advance()
    h.corrections.correct_post_run(prior[0], False, True, "earlier outcome correction")
    assert (h.stats().included_games, h.stats().wins, h.stats().losses) == (21, 19, 2)
    assert h.snapshot(round21.round_id) == prediction
    h.clock.advance()
    corrected21 = h.corrections.correct_post_run(
        round21.round_id, False, True, "round21 outcome correction"
    )
    assert h.snapshot(round21.round_id) == prediction
    assert h.snapshot(corrected21.replacement_round_id) == replace(
        prediction, round_id=corrected21.replacement_round_id
    )
    assert h.snapshot(corrected21.replacement_round_id).history_sample_size == 20
