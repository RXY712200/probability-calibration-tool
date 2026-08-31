"""Deterministic test data; no production calculations or persistence shortcuts."""

import sqlite3
from dataclasses import asdict, replace
from datetime import UTC, datetime, timedelta
from enum import Enum

from probability_calibration_tool.domain.enums import (
    EvState,
    HistoryModelStatus,
    ModelRelation,
    OddsCombinationStatus,
    RoundStatus,
)
from probability_calibration_tool.domain.records import (
    RoundAnalysisSnapshotRecord,
    RoundRecord,
)

STAMP = datetime(2026, 8, 30, 11, 23, 45, 123456, tzinfo=UTC)
STAMP_TEXT = "2026-08-30T11:23:45.123456Z"


def make_round(
    round_id: str = "current", status: RoundStatus = RoundStatus.PENDING, **changes: object
) -> RoundRecord:
    record = RoundRecord(
        round_id=round_id,
        created_at=STAMP,
        calculated_at=STAMP,
        last_updated_at=STAMP,
        completed_at=STAMP + timedelta(minutes=1) if status is RoundStatus.COMPLETED else None,
        voided_at=STAMP + timedelta(minutes=1) if status is RoundStatus.VOIDED else None,
        void_reason="test void" if status is RoundStatus.VOIDED else None,
        character_id=1,
        history_regime_id="regime-1-1",
        reference_history=False,
        p_h_raw=50,
        win_odds_raw="2.000",
        lose_odds_raw="02.0",
        win_odds=2.0,
        lose_odds=2.0,
        status=status,
        revision_count=0,
        result=True if status is RoundStatus.COMPLETED else None,
        include_character_history=True if status is RoundStatus.COMPLETED else None,
        history_exposed=False,
        history_exposed_at=None,
        subjective_independence_compromised=False,
        supersedes_round_id=None,
    )
    return replace(record, **changes)


def make_snapshot(
    status: HistoryModelStatus = HistoryModelStatus.NO_HISTORY, round_id: str = "current"
) -> RoundAnalysisSnapshotRecord:
    has_history = status is not HistoryModelStatus.NO_HISTORY
    valid = status is HistoryModelStatus.VALID
    return RoundAnalysisSnapshotRecord(
        round_id=round_id,
        p_h_used=50,
        subjective_probability=0.5,
        subjective_p_min=0.3,
        subjective_p_max=0.7,
        subjective_logit_half_width=0.4,
        subjective_model_version=1,
        odds_analysis_version=1,
        break_even_win=0.5,
        break_even_lose_event=0.5,
        break_even_lose_as_win_probability=0.5,
        subjective_win_ev_center=0.0,
        subjective_win_ev_min=-0.4,
        subjective_win_ev_max=0.4,
        subjective_win_margin_index=0.0,
        subjective_win_ev_state=EvState.CROSSES_THRESHOLD,
        subjective_lose_ev_center=0.0,
        subjective_lose_ev_min=-0.4,
        subjective_lose_ev_max=0.4,
        subjective_lose_margin_index=None,
        subjective_lose_ev_state=EvState.CROSSES_THRESHOLD,
        odds_combination_status=OddsCombinationStatus.CRITICAL,
        history_model_status=status,
        history_statistically_ready=valid,
        history_wins=19 if valid else int(has_history),
        history_losses=1 if valid else 0,
        history_sample_size=20 if valid else int(has_history),
        history_model_version=1,
        history_gate_version=1,
        history_probability=0.9 if valid else (0.75 if has_history else None),
        history_lower=0.8 if valid else (0.1 if has_history else None),
        history_upper=0.98 if valid else (0.999 if has_history else None),
        history_data_through_at=STAMP - timedelta(minutes=1),
        last_included_historical_round_id="prior" if has_history else None,
        historical_win_ev_center=0.8 if valid else None,
        historical_win_ev_min=0.6 if valid else None,
        historical_win_ev_max=0.96 if valid else None,
        historical_win_ev_state=EvState.ROBUST_POSITIVE if valid else None,
        historical_win_threshold_posterior_probability=0.99 if valid else None,
        historical_lose_ev_center=-0.8 if valid else None,
        historical_lose_ev_min=-0.96 if valid else None,
        historical_lose_ev_max=-0.6 if valid else None,
        historical_lose_ev_state=EvState.ROBUST_NEGATIVE if valid else None,
        historical_lose_threshold_posterior_probability=0.01 if valid else None,
        win_model_relation=ModelRelation.UNCERTAIN if valid else ModelRelation.HISTORY_UNAVAILABLE,
        lose_model_relation=ModelRelation.UNCERTAIN if valid else ModelRelation.HISTORY_UNAVAILABLE,
    )


def sql_values(record: object) -> dict[str, object]:
    """Independent test serialization for direct SQLite constraint tests."""
    values = asdict(record)
    for key, value in values.items():
        if isinstance(value, datetime):
            values[key] = (
                value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
            )
        elif isinstance(value, Enum):
            values[key] = value.value
        elif isinstance(value, bool):
            values[key] = int(value)
    return values


def insert_row(connection: sqlite3.Connection, table: str, values: dict[str, object]) -> None:
    """Only test-owned table/column names are interpolated; values are bound."""
    columns = ", ".join(values)
    placeholders = ", ".join("?" for _ in values)
    connection.execute(
        f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", tuple(values.values())
    )


def update_row(
    connection: sqlite3.Connection,
    table: str,
    changes: dict[str, object],
    where: str,
    parameters: tuple[object, ...],
) -> None:
    assignments = ", ".join(f"{name} = ?" for name in changes)
    connection.execute(
        f"UPDATE {table} SET {assignments} WHERE {where}", (*changes.values(), *parameters)
    )
