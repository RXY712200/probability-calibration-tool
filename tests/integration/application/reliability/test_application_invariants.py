from contextlib import closing
from dataclasses import replace

import pytest
from infrastructure.helpers import mutate

from probability_calibration_tool.application.invariant_service import InvariantService
from probability_calibration_tool.infrastructure.sqlite_health import open_existing
from probability_calibration_tool.persistence.reliability import read_source_inventory


@pytest.mark.parametrize(
    "damage,expected",
    [
        ("identity", "identities"),
        ("no_active", "active regime"),
        ("missing_snapshot", "snapshot"),
        ("exposure", "exposure"),
    ],
)
def test_source_invariant_damage_is_reported_never_repaired(rig, damage, expected):
    ids = rig.h.seed_history(19, 1) if damage == "exposure" else rig.h.seed_history(1, 0)
    if damage == "identity":
        mutate(
            rig.paths.database, "UPDATE characters SET display_name='wrong' WHERE character_id=1"
        )
    elif damage == "no_active":
        mutate(
            rig.paths.database,
            "UPDATE history_regimes SET active=0,ended_at=started_at WHERE character_id=1",
        )
    elif damage == "missing_snapshot":
        mutate(
            rig.paths.database, "DELETE FROM round_analysis_snapshots WHERE round_id=?", (ids[0],)
        )
    else:
        from application.helpers import COMMAND

        view = rig.h.rounds.calculate(COMMAND)
        mutate(
            rig.paths.database,
            "UPDATE rounds SET reference_history=1 WHERE round_id=?",
            (view.round_id,),
        )
    before = rig.h.capture()
    report = InvariantService().inspect(rig.paths.database)
    assert any(expected in issue.lower() for issue in report.issues)
    assert rig.h.capture() == before


def test_supersede_cycle_and_branch_detection_with_controlled_inventory(rig):
    rig.h.seed_history(3, 0)
    with closing(open_existing(rig.paths.database)) as connection:
        inventory = read_source_inventory(connection)
    rows = list(inventory.rounds)
    cycle = [
        dict(row, supersedes_round_id=rows[(index + 1) % 3]["round_id"])
        for index, row in enumerate(rows)
    ]
    report = InvariantService().inspect_inventory(replace(inventory, rounds=tuple(cycle)))
    assert any("cycle" in issue for issue in report.issues)
    branch = (
        rows[0],
        dict(rows[1], supersedes_round_id=rows[0]["round_id"]),
        dict(rows[2], supersedes_round_id=rows[0]["round_id"]),
    )
    report = InvariantService().inspect_inventory(replace(inventory, rounds=branch))
    assert any("branches" in issue for issue in report.issues)


def test_accepted_correction_chain_and_inactive_regimes_pass_source_invariants(rig):
    a = rig.h.seed_history(2, 1)[0]
    b = rig.h.corrections.correct_post_run(a, False, True, "first")
    rig.h.corrections.correct_post_run(b.replacement_round_id, True, True, "second")
    rig.h.regimes.start_new_regime(1)
    assert InvariantService().inspect(rig.paths.database).issues == ()


def test_missing_cache_is_not_source_corruption(rig):
    mutate(rig.paths.database, "DELETE FROM character_stats WHERE character_id=1")
    assert InvariantService().inspect(rig.paths.database).issues == ()
