from ._checks import active_regime
from .errors import ApplicationInvariantError
from .ports import UowFactory
from .views import MaintenanceCharacterView


class MaintenanceService:
    def __init__(self, uow_factory: UowFactory) -> None:
        self._uow_factory = uow_factory

    def list_characters(self) -> tuple[MaintenanceCharacterView, ...]:
        views = []
        with self._uow_factory() as uow:
            for character in uow.characters.list_all():
                if not character.active:
                    continue
                regime = active_regime(uow, character.character_id)
                stats = uow.stats.get(character.character_id, regime.regime_id)
                if stats is None:
                    raise ApplicationInvariantError("Active regime has no stats cache.")
                views.append(
                    MaintenanceCharacterView(
                        character.character_id,
                        character.display_name,
                        regime.regime_number,
                        regime.started_at,
                        regime.reason,
                        stats.included_games,
                    )
                )
        return tuple(views)
