from . import _view_builder
from ._checks import pending_rounds, require_snapshot
from .enums import RecoveryState
from .errors import ErrorCode, RoundNotPendingError
from .ports import UowFactory
from .views import LockedAnalysisView, RecoveryView


class RecoveryService:
    def __init__(self, uow_factory: UowFactory) -> None:
        self._uow_factory = uow_factory

    def inspect(self) -> RecoveryView:
        with self._uow_factory() as uow:
            rows = pending_rounds(uow)
        if not rows:
            return RecoveryView(RecoveryState.NONE, None)
        return RecoveryView(RecoveryState.RECOVERABLE, rows[0].round_id)

    def continue_pending(self) -> LockedAnalysisView:
        with self._uow_factory() as uow:
            rows = pending_rounds(uow)
            if not rows:
                raise RoundNotPendingError(
                    "No pending round is available for recovery.",
                    code=ErrorCode.NO_PENDING_RECOVERY,
                )
            record = rows[0]
            snapshot = require_snapshot(uow, record.round_id)
        # These are already durable records. No Core call, write, ID or clock is involved.
        return _view_builder.locked_view(record, snapshot)
