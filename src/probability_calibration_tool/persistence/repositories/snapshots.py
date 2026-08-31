import sqlite3

from probability_calibration_tool.domain.enums import (
    EvState,
    HistoryModelStatus,
    ModelRelation,
    OddsCombinationStatus,
)
from probability_calibration_tool.domain.records import RoundAnalysisSnapshotRecord
from probability_calibration_tool.persistence.database import (
    deserialize_utc,
    ensure_write_transaction,
    serialize_utc,
)


class SnapshotRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def insert(self, record: RoundAnalysisSnapshotRecord) -> None:
        values = record.__dict__.copy()
        values["history_data_through_at"] = serialize_utc(values["history_data_through_at"])
        values["history_statistically_ready"] = int(values["history_statistically_ready"])
        columns = ", ".join(values)
        ensure_write_transaction(self._connection)
        self._connection.execute(
            f"INSERT INTO round_analysis_snapshots ({columns}) VALUES ({', '.join('?' for _ in values)})",
            tuple(values.values()),
        )

    def get(self, round_id: str) -> RoundAnalysisSnapshotRecord | None:
        row = self._connection.execute(
            "SELECT * FROM round_analysis_snapshots WHERE round_id = ?", (round_id,)
        ).fetchone()
        if row is None:
            return None
        values = dict(row)
        values["history_data_through_at"] = deserialize_utc(values["history_data_through_at"])
        values["history_statistically_ready"] = bool(values["history_statistically_ready"])
        for field in (
            "subjective_win_ev_state",
            "subjective_lose_ev_state",
            "historical_win_ev_state",
            "historical_lose_ev_state",
        ):
            if values[field] is not None:
                values[field] = EvState(values[field])
        values["odds_combination_status"] = OddsCombinationStatus(values["odds_combination_status"])
        values["history_model_status"] = HistoryModelStatus(values["history_model_status"])
        values["win_model_relation"] = ModelRelation(values["win_model_relation"])
        values["lose_model_relation"] = ModelRelation(values["lose_model_relation"])
        return RoundAnalysisSnapshotRecord(**values)

    def update(self, record: RoundAnalysisSnapshotRecord) -> None:
        values = record.__dict__.copy()
        values["history_data_through_at"] = serialize_utc(values["history_data_through_at"])
        values["history_statistically_ready"] = int(values["history_statistically_ready"])
        assignments = ", ".join(f"{column} = ?" for column in values if column != "round_id")
        parameters = tuple(value for column, value in values.items() if column != "round_id") + (
            values["round_id"],
        )
        ensure_write_transaction(self._connection)
        self._connection.execute(
            f"UPDATE round_analysis_snapshots SET {assignments} WHERE round_id = ?",
            parameters,
        )
