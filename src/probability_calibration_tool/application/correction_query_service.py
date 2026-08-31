"""Detached audit identifiers, not a historical analysis browser."""

from dataclasses import dataclass
from datetime import datetime

from probability_calibration_tool.persistence.database import deserialize_utc

from .ports import UowFactory


@dataclass(frozen=True)
class CorrectionCandidate:
    round_id: str
    display_name: str
    completed_at: datetime


class CorrectionQueryService:
    def __init__(self, factory: UowFactory):
        self._factory = factory

    def list_candidates(self) -> tuple[CorrectionCandidate, ...]:
        with self._factory() as uow:
            return tuple(
                CorrectionCandidate(round_id, name, deserialize_utc(completed))
                for round_id, name, completed in uow.rounds.correction_identifiers()
            )
