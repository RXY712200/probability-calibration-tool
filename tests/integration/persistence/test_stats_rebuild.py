import sqlite3
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from probability_calibration_tool.core.model_specs import STATS_VERSION
from probability_calibration_tool.domain.enums import RoundStatus
from probability_calibration_tool.domain.records import CharacterStatsRecord, RoundRecord
from probability_calibration_tool.persistence.repositories import (
    CharacterStatsRepository,
    RoundRepository,
)

from .helpers import STAMP, STAMP_TEXT, insert_row, make_round, update_row


@pytest.fixture
def history_population(
    connection: sqlite3.Connection,
) -> tuple[list[RoundRecord], list[RoundRecord]]:
    insert_row(
        connection,
        "history_regimes",
        {
            "regime_id": "other-regime",
            "character_id": 1,
            "regime_number": 2,
            "started_at": STAMP_TEXT,
            "ended_at": STAMP_TEXT,
            "active": 0,
            "reason": "different regime",
        },
    )
    repo = RoundRepository(connection)
    eligible = [
        make_round(
            f"eligible-{19 - number:02}",
            RoundStatus.COMPLETED,
            result=number < 16,
            calculated_at=STAMP + timedelta(seconds=number),
        )
        for number in range(20)
    ]
    distractors = [
        make_round("excluded", RoundStatus.COMPLETED, include_character_history=False),
        make_round("pending"),
        make_round(
            "voided",
            RoundStatus.VOIDED,
            result=True,
            include_character_history=True,
            completed_at=STAMP,
        ),
        make_round(
            "other-character", RoundStatus.COMPLETED, character_id=2, history_regime_id="regime-1-2"
        ),
        make_round("other-regime", RoundStatus.COMPLETED, history_regime_id="other-regime"),
    ]
    for record in eligible + distractors:
        repo.insert(record)
    return eligible, distractors


def test_eligible_history_includes_only_exact_character_regime_completed_included(
    connection: sqlite3.Connection, history_population: tuple[list[RoundRecord], list[RoundRecord]]
) -> None:
    eligible, distractors = history_population
    result = RoundRepository(connection).eligible_history(1, "regime-1-1")
    assert result == eligible
    assert all(isinstance(record, RoundRecord) for record in result)
    assert {record.round_id for record in result}.isdisjoint(
        record.round_id for record in distractors
    )
    for record in distractors:
        assert (
            connection.execute(
                "SELECT COUNT(*) FROM rounds WHERE round_id = ?", (record.round_id,)
            ).fetchone()[0]
            == 1
        )
    assert [
        record.round_id for record in RoundRepository(connection).eligible_history(2, "regime-1-2")
    ] == ["other-character"]
    assert [
        record.round_id
        for record in RoundRepository(connection).eligible_history(1, "other-regime")
    ] == ["other-regime"]


@pytest.mark.parametrize("cached_version", [STATS_VERSION, STATS_VERSION + 1])
def test_stats_rebuild_replaces_corrupt_cache_from_rounds_only(
    connection: sqlite3.Connection,
    history_population: tuple[list[RoundRecord], list[RoundRecord]],
    cached_version: int,
) -> None:
    eligible, _ = history_population
    repo = CharacterStatsRepository(connection)
    untouched = repo.get(2, "regime-1-2")
    update_row(
        connection,
        "character_stats",
        {
            "included_games": 3,
            "wins": 2,
            "losses": 1,
            "last_included_round_id": eligible[0].round_id,
            "stats_version": cached_version,
            "updated_at": "2000-01-01T00:00:00.000000Z",
        },
        "character_id = ? AND regime_id = ?",
        (1, "regime-1-1"),
    )
    corrupt = repo.get(1, "regime-1-1")
    assert corrupt is not None
    assert (corrupt.included_games, corrupt.wins, corrupt.losses) == (3, 2, 1)
    assert (corrupt.stats_version != STATS_VERSION) is (cached_version != STATS_VERSION)
    assert connection.execute("SELECT COUNT(*) FROM round_analysis_snapshots").fetchone()[0] == 0
    start = datetime.now(UTC)
    result = repo.rebuild_stats(1, "regime-1-1")
    end = datetime.now(UTC)
    assert isinstance(result, CharacterStatsRecord)
    assert (result.included_games, result.wins, result.losses, result.stats_version) == (
        20,
        16,
        4,
        STATS_VERSION,
    )
    assert result.last_included_round_id == "eligible-00"
    assert result.last_included_round_id == eligible[-1].round_id
    assert start <= result.updated_at <= end
    assert result.updated_at.tzinfo is UTC
    assert repo.get(1, "regime-1-1") == result
    assert repo.get(2, "regime-1-2") == untouched
    assert connection.execute("SELECT COUNT(*) FROM rounds").fetchone()[0] == 25
    again = repo.rebuild_stats(1, "regime-1-1")
    assert replace(again, updated_at=result.updated_at) == result


def test_latest_round_uses_prediction_time_before_stable_id_tiebreak(
    connection: sqlite3.Connection,
) -> None:
    repo = RoundRepository(connection)
    repo.insert(
        make_round("zzz-earlier", RoundStatus.COMPLETED, calculated_at=STAMP - timedelta(seconds=1))
    )
    repo.insert(make_round("aaa-later", RoundStatus.COMPLETED, calculated_at=STAMP))
    stats = CharacterStatsRepository(connection).rebuild_stats(1, "regime-1-1")
    assert stats.last_included_round_id == "aaa-later"
    repo.insert(make_round("bbb-same-time", RoundStatus.COMPLETED, calculated_at=STAMP))
    ordered = repo.eligible_history(1, "regime-1-1")
    assert [record.round_id for record in ordered] == ["zzz-earlier", "aaa-later", "bbb-same-time"]
    stats = CharacterStatsRepository(connection).rebuild_stats(1, "regime-1-1")
    assert stats.included_games == 3
    assert stats.last_included_round_id == "bbb-same-time"
