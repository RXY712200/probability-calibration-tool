import logging
from datetime import UTC, datetime

from probability_calibration_tool.core.model_specs import STATS_VERSION
from probability_calibration_tool.domain.records import CharacterStatsRecord
from probability_calibration_tool.persistence.unit_of_work import create_uow_factory

from .reliability_views import StatsValidationResult


class StatsValidationService:
    def __init__(self, logger=None):
        self.logger = logger if logger is not None else logging.getLogger(__name__)

    def validate(self, path, *, repair: bool = True) -> StatsValidationResult:
        repaired = []
        with create_uow_factory(path)() as uow:
            for regime in uow.regimes.list_all():
                rows = uow.rounds.eligible_history(regime.character_id, regime.regime_id)
                wins = sum(row.result is True for row in rows)
                expected = (
                    len(rows),
                    wins,
                    len(rows) - wins,
                    rows[-1].round_id if rows else None,
                    STATS_VERSION,
                )
                stats = uow.stats.get(regime.character_id, regime.regime_id)
                actual = (
                    None
                    if stats is None
                    else (
                        stats.included_games,
                        stats.wins,
                        stats.losses,
                        stats.last_included_round_id,
                        stats.stats_version,
                    )
                )
                if actual == expected:
                    continue
                if not repair:
                    raise RuntimeError("Stats cache validation failed.")
                if stats is None:
                    uow.stats.insert(
                        CharacterStatsRecord(
                            regime.character_id,
                            regime.regime_id,
                            0,
                            0,
                            0,
                            None,
                            datetime.now(UTC),
                            STATS_VERSION,
                        )
                    )
                uow.stats.rebuild_stats(regime.character_id, regime.regime_id)
                repaired.append(regime.regime_id)
            if repaired:
                uow.commit()
        if repaired:
            self.logger.warning("Rebuilt derived stats cache for %d regime(s).", len(repaired))
        return StatsValidationResult(tuple(repaired))
