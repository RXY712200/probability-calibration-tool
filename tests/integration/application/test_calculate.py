from dataclasses import asdict, fields, replace
from uuid import UUID

import pytest

from probability_calibration_tool import core
from probability_calibration_tool.application import _view_builder
from probability_calibration_tool.application.enums import HistoricalDisplayState
from probability_calibration_tool.application.errors import (
    InputValidationError,
    PendingRoundExistsError,
)
from probability_calibration_tool.application.views import NonnumericHistoryView, VisibleHistoryView
from probability_calibration_tool.domain.enums import HistoryModelStatus, RoundStatus
from probability_calibration_tool.persistence.repositories import SnapshotRepository
from probability_calibration_tool.persistence.unit_of_work import UnitOfWork

from .helpers import COMMAND, InjectedFailure


@pytest.mark.parametrize("reference", [False, True])
@pytest.mark.parametrize(
    "counts,status",
    [
        ((0, 0), HistoryModelStatus.NO_HISTORY),
        ((1, 0), HistoryModelStatus.INSUFFICIENT),
        ((19, 1), HistoryModelStatus.VALID),
    ],
)
def test_calculate_safe_history_matrix_golden_a_b_c(h, reference, counts, status):
    prior = h.seed_history(*counts)
    cutoff = h.clock.now()
    view = h.rounds.calculate(replace(COMMAND, reference_history=reference))
    record, snapshot = h.record(view.round_id), h.snapshot(view.round_id)
    assert record.status == RoundStatus.PENDING
    assert record.created_at == record.calculated_at == record.last_updated_at == cutoff
    assert snapshot.history_model_status == status
    assert (snapshot.history_wins, snapshot.history_losses) == counts
    assert snapshot.history_sample_size == sum(counts)
    assert snapshot.history_data_through_at == cutoff
    assert snapshot.last_included_historical_round_id == (prior[-1] if prior else None)
    assert record.revision_count == 0
    assert record.result is record.include_character_history is record.completed_at is None
    assert (record.win_odds_raw, record.lose_odds_raw) == ("2.00", "3.00")
    assert (record.win_odds, record.lose_odds) == (2.0, 3.0)
    estimate = core.compute_historical_estimate(*counts)
    assert snapshot.history_probability == estimate.probability
    assert snapshot.history_lower == estimate.lower
    assert snapshot.history_upper == estimate.upper
    visible = reference and status == HistoryModelStatus.VALID
    assert record.history_exposed is visible
    assert record.history_exposed_at == (cutoff if visible else None)
    assert not record.subjective_independence_compromised
    if visible:
        assert isinstance(view.history, VisibleHistoryView)
        assert view.history.state == HistoricalDisplayState.VISIBLE
        assert (view.history.wins, view.history.losses) == counts
        assert view.history.probability == estimate.probability
        assert view.history.odds == core.analyze_historical_odds(estimate, 2.0, 3.0)
        assert view.history.win_model_relation == snapshot.win_model_relation
        assert view.history.lose_model_relation == snapshot.lose_model_relation
    else:
        assert isinstance(view.history, NonnumericHistoryView)
        expected = (
            HistoricalDisplayState.HIDDEN if not reference else HistoricalDisplayState(status.value)
        )
        assert asdict(view.history) == {"state": expected}
        assert {field.name for field in fields(view.history)} == {"state"}
        # Relations are directional too: they live ONLY inside the visible history variant.
        assert "win_model_relation" not in asdict(view)
        assert "lose_model_relation" not in asdict(view)
    assert view.subjective == core.compute_subjective_estimate(70)
    assert view.subjective_odds == core.analyze_subjective_odds(view.subjective, 2.0, 3.0)
    with h.factory() as uow:
        assert [row.round_id for row in uow.rounds.list_pending()] == [view.round_id]
    assert len(h.capture()["round_analysis_snapshots"]) == len(prior) + 1


def test_golden_c_exposure_and_snapshot_durable_before_view_construction(h, monkeypatch):
    h.seed_history()
    original = _view_builder.locked_view
    calls = []

    def project(record, snapshot):
        assert h.record(record.round_id) == record
        assert h.snapshot(record.round_id) == snapshot
        assert record.history_exposed and record.history_exposed_at == h.clock.now()
        calls.append(record.round_id)
        return original(record, snapshot)

    monkeypatch.setattr(_view_builder, "locked_view", project)
    view = h.rounds.calculate(replace(COMMAND, reference_history=True))
    assert calls == [view.round_id]


@pytest.mark.parametrize("failure", ["snapshot_insert", "commit"])
def test_calculate_atomicity_and_no_official_release(h, monkeypatch, failure):
    h.seed_history()
    before = h.capture()
    called = []
    monkeypatch.setattr(_view_builder, "locked_view", lambda *args: called.append(args))

    def fail(*args):
        # The round write happened but is still invisible on a fresh connection.
        assert h.capture() == before
        raise InjectedFailure(failure)

    if failure == "snapshot_insert":
        monkeypatch.setattr(SnapshotRepository, "insert", fail)
    else:
        monkeypatch.setattr(UnitOfWork, "commit", fail)
    with pytest.raises(InjectedFailure):
        h.rounds.calculate(replace(COMMAND, reference_history=True))
    assert h.capture() == before
    assert called == []
    assert h.record(str(UUID(int=h.ids.count))) is None


@pytest.mark.parametrize(
    "changes,field",
    [
        ({"p_h_raw": -1}, "subjective_probability"),
        ({"p_h_raw": 101}, "subjective_probability"),
        ({"p_h_raw": 50.0}, "subjective_probability"),
        ({"p_h_raw": True}, "subjective_probability"),
        ({"win_odds_raw": "NaN"}, "win_odds"),
        ({"win_odds_raw": " 2"}, "win_odds"),
        ({"win_odds_raw": "1e2"}, "win_odds"),
        ({"win_odds_raw": "9" * 1000}, "win_odds"),
        ({"lose_odds_raw": "0.9"}, "lose_odds"),
        ({"lose_odds_raw": None}, "lose_odds"),
        ({"reference_history": 1}, "reference_history"),
        ({"character_id": True}, "character_id"),
        ({"character_id": 35}, "character_id"),
    ],
)
def test_core_validation_translated_to_field_errors_without_writes(h, changes, field):
    before = h.capture()
    with pytest.raises(InputValidationError) as caught:
        h.rounds.calculate(replace(COMMAND, **changes))
    assert caught.value.field == field
    assert h.capture() == before


@pytest.mark.parametrize("p_h_raw,p_h_used", [(0, 1), (100, 99)])
def test_core_boundary_normalization_not_reimplemented(h, p_h_raw, p_h_used):
    view = h.rounds.calculate(replace(COMMAND, p_h_raw=p_h_raw, win_odds_raw="1"))
    assert view.subjective.p_h_raw == p_h_raw
    assert view.subjective.p_h_used == p_h_used
    assert view.subjective_odds.win.robust_margin_index is None


def test_pending_blocks_second_calculation_globally(h):
    h.rounds.calculate(COMMAND)
    before = h.capture()
    with pytest.raises(PendingRoundExistsError):
        h.rounds.calculate(replace(COMMAND, character_id=2))
    assert h.capture() == before


def test_history_eligibility_is_same_character_current_regime_and_completed_included(h):
    old_ids = h.seed_history(2, 0)
    h.regimes.start_new_regime(1, "new rules")
    current_ids = h.seed_history(1, 1)
    h.seed_history(4, 0, character_id=2)
    h.seed_history(2, 0, include=False)
    void = h.rounds.calculate(COMMAND)
    h.rounds.void_pending(void.round_id)
    with h.factory() as uow:
        # A deliberately stale cache must not influence snapshot construction.
        stats = uow.stats.get(1, uow.regimes.get_active(1).regime_id)
        uow._connection.execute(
            "UPDATE character_stats SET included_games=99,wins=99,losses=0 WHERE regime_id=?",
            (stats.regime_id,),
        )
        uow.commit()
    view = h.rounds.calculate(COMMAND)
    snapshot = h.snapshot(view.round_id)
    assert (snapshot.history_wins, snapshot.history_losses, snapshot.history_sample_size) == (
        1,
        1,
        2,
    )
    assert snapshot.last_included_historical_round_id == current_ids[-1]
    assert snapshot.last_included_historical_round_id not in old_ids
    recalc = h.rounds.recalculate(view.round_id, COMMAND)
    assert recalc.round_id == view.round_id
    assert h.snapshot(view.round_id).history_sample_size == 2


def test_history_last_id_uses_prediction_chronology_not_uuid(h):
    h.ids.count = 100
    earlier = h.seed_history(1, 0)[0]
    h.ids.count = 0
    later = h.seed_history(0, 1)[0]
    assert earlier > later
    cutoff = h.clock.advance()
    view = h.rounds.calculate(COMMAND)
    snapshot = h.snapshot(view.round_id)
    assert snapshot.last_included_historical_round_id == later
    assert snapshot.history_data_through_at == cutoff
    assert snapshot.history_data_through_at > h.record(later).calculated_at
