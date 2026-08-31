from dataclasses import replace

from probability_calibration_tool.core.model_specs import STATS_VERSION
from probability_calibration_tool.domain.records import CharacterStatsRecord, HistoryRegimeRecord

from ._checks import active_regime, pending_rounds, utc_now, validate_reason
from .errors import RegimeSwitchBlockedError
from .ports import Clock, IdGenerator, UowFactory
from .views import RegimeSummaryView


class RegimeService:
    def __init__(self, uow_factory: UowFactory, clock: Clock, ids: IdGenerator) -> None:
        self._uow_factory = uow_factory
        self._clock = clock
        self._ids = ids

    def start_new_regime(self, character_id: int, reason: str | None = None) -> RegimeSummaryView:
        validate_reason(reason)
        with self._uow_factory() as uow:
            if pending_rounds(uow):
                raise RegimeSwitchBlockedError("A pending round blocks all regime switching.")
            old = active_regime(uow, character_id)
            now = utc_now(self._clock)
            uow.regimes.update(replace(old, active=False, ended_at=now))
            new = HistoryRegimeRecord(
                self._ids.new_id(), character_id, old.regime_number + 1, now, None, True, reason
            )
            uow.regimes.insert(new)
            uow.stats.insert(
                CharacterStatsRecord(character_id, new.regime_id, 0, 0, 0, None, now, STATS_VERSION)
            )
            uow.commit()
        return RegimeSummaryView(character_id, new.regime_id, new.regime_number, now, reason, 0)
