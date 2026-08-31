import sqlite3

import pytest

from probability_calibration_tool.domain.enums import HistoryModelStatus

from .helpers import insert_row, make_snapshot, sql_values

HISTORICAL_EV_FIELDS = [
    f"historical_{side}_ev_{position}"
    for side in ("win", "lose")
    for position in ("center", "min", "max")
]
HISTORICAL_STATE_FIELDS = [f"historical_{side}_ev_state" for side in ("win", "lose")]
POSTERIOR_FIELDS = [
    f"historical_{side}_threshold_posterior_probability" for side in ("win", "lose")
]
RELATION_FIELDS = ["win_model_relation", "lose_model_relation"]
HISTORY_PROBABILITY_FIELDS = ["history_probability", "history_lower", "history_upper"]


@pytest.mark.parametrize("status", list(HistoryModelStatus))
def test_canonical_snapshot_insert(
    snapshot_connection: sqlite3.Connection, status: HistoryModelStatus
) -> None:
    values = sql_values(make_snapshot(status))
    insert_row(snapshot_connection, "round_analysis_snapshots", values)
    stored = dict(
        snapshot_connection.execute(
            "SELECT * FROM round_analysis_snapshots WHERE round_id = 'current'"
        ).fetchone()
    )
    assert stored == values


GENERAL_MUTATIONS = [
    pytest.param({"p_h_used": 0}, id="used-below-one"),
    pytest.param({"p_h_used": 100}, id="used-above-99"),
    pytest.param({"subjective_p_min": 0.5}, id="subjective-min-equals-center"),
    pytest.param({"subjective_p_max": 0.5}, id="subjective-max-equals-center"),
    pytest.param({"subjective_logit_half_width": 0}, id="zero-half-width"),
    pytest.param({"subjective_logit_half_width": -0.1}, id="negative-half-width"),
    pytest.param({"history_sample_size": 21}, id="sample-arithmetic"),
    pytest.param({"history_wins": -1}, id="negative-wins"),
    pytest.param({"history_losses": -1}, id="negative-losses"),
    pytest.param({"history_statistically_ready": 2}, id="invalid-ready-boolean"),
    pytest.param({"history_lower": 0.91}, id="historical-lower-above-center"),
    pytest.param({"history_upper": 0.89}, id="historical-upper-below-center"),
]
GENERAL_MUTATIONS += [
    pytest.param({field: 0}, id=f"invalid-{field}")
    for field in (
        "subjective_model_version",
        "odds_analysis_version",
        "history_model_version",
        "history_gate_version",
    )
]
GENERAL_MUTATIONS += [
    pytest.param({field: "unknown"}, id=f"invalid-{field}")
    for field in (
        "subjective_win_ev_state",
        "subjective_lose_ev_state",
        "odds_combination_status",
        "history_model_status",
        *HISTORICAL_STATE_FIELDS,
        *RELATION_FIELDS,
    )
]
GENERAL_MUTATIONS += [
    pytest.param({field: value}, id=f"range-{field}-{value}")
    for field in (
        "subjective_probability",
        "subjective_p_min",
        "subjective_p_max",
        "break_even_win",
        "break_even_lose_event",
        "break_even_lose_as_win_probability",
        *HISTORY_PROBABILITY_FIELDS,
        *POSTERIOR_FIELDS,
    )
    for value in (-0.01, 1.01)
]
GENERAL_MUTATIONS += [
    pytest.param({"subjective_p_min": 0}, id="strict-min-greater-than-zero"),
    pytest.param({"subjective_p_max": 1}, id="strict-max-less-than-one"),
]
for prefix, center in (
    ("subjective_win", 0.0),
    ("subjective_lose", 0.0),
    ("historical_win", 0.8),
    ("historical_lose", -0.8),
):
    GENERAL_MUTATIONS += [
        pytest.param({f"{prefix}_ev_min": center + 0.1}, id=f"{prefix}-min-above-center"),
        pytest.param({f"{prefix}_ev_max": center - 0.1}, id=f"{prefix}-max-below-center"),
    ]


@pytest.mark.parametrize("changes", GENERAL_MUTATIONS)
def test_general_snapshot_constraint_matrix(
    snapshot_connection: sqlite3.Connection, changes: dict[str, object]
) -> None:
    values = sql_values(make_snapshot(HistoryModelStatus.VALID))
    values.update(changes)
    with pytest.raises(sqlite3.IntegrityError) as caught:
        insert_row(snapshot_connection, "round_analysis_snapshots", values)
    assert caught.value.sqlite_errorname == "SQLITE_CONSTRAINT_CHECK"


NO_HISTORY_MUTATIONS = [
    pytest.param({"history_sample_size": 1}, id="nonzero-sample"),
    pytest.param({"history_wins": 1}, id="nonzero-wins"),
    pytest.param({"history_losses": 1}, id="nonzero-losses"),
    pytest.param({"history_sample_size": 1, "history_wins": 1}, id="nonzero-consistent-counts"),
    pytest.param({"history_statistically_ready": 1}, id="ready"),
    pytest.param({"last_included_historical_round_id": "prior"}, id="last-round-present"),
]
NO_HISTORY_MUTATIONS += [
    pytest.param({field: 0.5}, id=f"present-{field}")
    for field in HISTORY_PROBABILITY_FIELDS + HISTORICAL_EV_FIELDS + POSTERIOR_FIELDS
]
NO_HISTORY_MUTATIONS += [
    pytest.param({field: "crosses_threshold"}, id=f"present-{field}")
    for field in HISTORICAL_STATE_FIELDS
]
NO_HISTORY_MUTATIONS += [
    pytest.param({field: "uncertain"}, id=f"available-{field}") for field in RELATION_FIELDS
]


@pytest.mark.parametrize("changes", NO_HISTORY_MUTATIONS)
def test_no_history_null_matrix(
    snapshot_connection: sqlite3.Connection, changes: dict[str, object]
) -> None:
    values = sql_values(make_snapshot(HistoryModelStatus.NO_HISTORY))
    values.update(changes)
    with pytest.raises(sqlite3.IntegrityError) as caught:
        insert_row(snapshot_connection, "round_analysis_snapshots", values)
    assert caught.value.sqlite_errorname == "SQLITE_CONSTRAINT_CHECK"


INSUFFICIENT_MUTATIONS = [
    pytest.param({"history_sample_size": 0, "history_wins": 0}, id="zero-consistent-counts"),
    pytest.param({"history_statistically_ready": 1}, id="ready"),
]
INSUFFICIENT_MUTATIONS += [
    pytest.param({field: None}, id=f"missing-{field}") for field in HISTORY_PROBABILITY_FIELDS
]
INSUFFICIENT_MUTATIONS += [
    pytest.param({field: 0.5}, id=f"present-{field}")
    for field in HISTORICAL_EV_FIELDS + POSTERIOR_FIELDS
]
INSUFFICIENT_MUTATIONS += [
    pytest.param({field: "crosses_threshold"}, id=f"present-{field}")
    for field in HISTORICAL_STATE_FIELDS
]
INSUFFICIENT_MUTATIONS += [
    pytest.param({field: "uncertain"}, id=f"available-{field}") for field in RELATION_FIELDS
]


@pytest.mark.parametrize("changes", INSUFFICIENT_MUTATIONS)
def test_insufficient_null_matrix(
    snapshot_connection: sqlite3.Connection, changes: dict[str, object]
) -> None:
    values = sql_values(make_snapshot(HistoryModelStatus.INSUFFICIENT))
    values.update(changes)
    with pytest.raises(sqlite3.IntegrityError) as caught:
        insert_row(snapshot_connection, "round_analysis_snapshots", values)
    assert caught.value.sqlite_errorname == "SQLITE_CONSTRAINT_CHECK"


VALID_MUTATIONS = [
    pytest.param(
        {"history_sample_size": 0, "history_wins": 0, "history_losses": 0},
        id="zero-consistent-counts",
    ),
    pytest.param({"history_statistically_ready": 0}, id="not-ready"),
]
VALID_MUTATIONS += [
    pytest.param({field: None}, id=f"missing-{field}")
    for field in HISTORY_PROBABILITY_FIELDS
    + HISTORICAL_EV_FIELDS
    + HISTORICAL_STATE_FIELDS
    + POSTERIOR_FIELDS
]
VALID_MUTATIONS += [
    pytest.param({field: "history_unavailable"}, id=f"unavailable-{field}")
    for field in RELATION_FIELDS
]


@pytest.mark.parametrize("changes", VALID_MUTATIONS)
def test_valid_history_required_data_matrix(
    snapshot_connection: sqlite3.Connection, changes: dict[str, object]
) -> None:
    values = sql_values(make_snapshot(HistoryModelStatus.VALID))
    values.update(changes)
    with pytest.raises(sqlite3.IntegrityError) as caught:
        insert_row(snapshot_connection, "round_analysis_snapshots", values)
    assert caught.value.sqlite_errorname == "SQLITE_CONSTRAINT_CHECK"


@pytest.mark.parametrize("field", ["round_id", "last_included_historical_round_id"])
def test_snapshot_foreign_keys(snapshot_connection: sqlite3.Connection, field: str) -> None:
    values = sql_values(make_snapshot(HistoryModelStatus.VALID))
    values[field] = "missing"
    with pytest.raises(sqlite3.IntegrityError) as caught:
        insert_row(snapshot_connection, "round_analysis_snapshots", values)
    assert caught.value.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY"


def test_snapshot_is_one_per_round(snapshot_connection: sqlite3.Connection) -> None:
    values = sql_values(make_snapshot())
    insert_row(snapshot_connection, "round_analysis_snapshots", values)
    with pytest.raises(sqlite3.IntegrityError):
        insert_row(snapshot_connection, "round_analysis_snapshots", values)
