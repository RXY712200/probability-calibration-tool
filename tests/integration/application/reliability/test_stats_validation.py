import logging

import pytest
from infrastructure.helpers import InjectedFailure, mutate

from probability_calibration_tool.application.stats_validation_service import StatsValidationService
from probability_calibration_tool.core.model_specs import STATS_VERSION
from probability_calibration_tool.persistence.repositories import CharacterStatsRepository


@pytest.mark.parametrize("damage", ["missing", "version", "counts", "wins_losses", "last_id"])
def test_stats_drift_repaired_from_source_with_warning(rig, caplog, damage):
    ids = rig.h.seed_history(2, 1)
    if damage == "missing":
        mutate(rig.paths.database, "DELETE FROM character_stats WHERE character_id=1")
    else:
        assignment = {
            "version": "stats_version=9",
            "counts": "included_games=8,wins=7,losses=1",
            "wins_losses": "wins=1,losses=2",
            "last_id": f"last_included_round_id='{ids[0]}'",
        }[damage]
        mutate(rig.paths.database, f"UPDATE character_stats SET {assignment} WHERE character_id=1")
    with caplog.at_level(logging.WARNING):
        result = StatsValidationService().validate(rig.paths.database)
    assert len(result.repaired_regime_ids) == 1
    stats = rig.h.stats()
    assert (
        stats.included_games,
        stats.wins,
        stats.losses,
        stats.last_included_round_id,
        stats.stats_version,
    ) == (3, 2, 1, ids[-1], STATS_VERSION)
    assert "Rebuilt derived stats" in caplog.text
    assert StatsValidationService().validate(rig.paths.database).repaired_regime_ids == ()


def test_inactive_and_active_regimes_repaired_together(rig):
    rig.h.seed_history(1, 1)
    old = rig.h.stats().regime_id
    new = rig.h.regimes.start_new_regime(1)
    rig.h.seed_history(1, 0)
    mutate(rig.paths.database, "UPDATE character_stats SET stats_version=9 WHERE character_id=1")
    result = StatsValidationService().validate(rig.paths.database)
    assert set(result.repaired_regime_ids) == {old, new.regime_id}
    assert rig.h.stats(1, old).included_games == 2
    assert rig.h.stats().included_games == 1


def test_stats_batch_failure_rolls_back_missing_insert_and_all_repairs(rig, monkeypatch):
    mutate(rig.paths.database, "DELETE FROM character_stats WHERE character_id=1")
    mutate(rig.paths.database, "UPDATE character_stats SET stats_version=9 WHERE character_id=2")
    before = rig.h.capture()
    original = CharacterStatsRepository.rebuild_stats
    calls = []

    def fail(self, character_id, regime_id):
        result = original(self, character_id, regime_id)
        calls.append(regime_id)
        if len(calls) == 2:
            raise InjectedFailure("second repair")
        return result

    monkeypatch.setattr(CharacterStatsRepository, "rebuild_stats", fail)
    with pytest.raises(InjectedFailure):
        StatsValidationService().validate(rig.paths.database)
    assert len(calls) == 2
    assert rig.h.capture() == before
