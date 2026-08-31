"""Synchronous, in-memory interaction state. Database services enforce their own rules too."""

from ._checks import require_bool
from .commands import CalculateCommand
from .enums import RecoveryState, WorkflowState
from .errors import InvalidWorkflowTransitionError, MultiplePendingRoundsError
from .recovery_service import RecoveryService
from .round_service import RoundService
from .views import CompletionResult, LockedAnalysisView, RecoveryView, VoidResult


class Workflow:
    def __init__(self, rounds: RoundService, recovery: RecoveryService) -> None:
        self._rounds = rounds
        self._recovery = recovery
        self._state = WorkflowState.DRAFT
        self._inputs: CalculateCommand | None = None
        self._analysis: LockedAnalysisView | None = None
        self._result: bool | None = None
        self._include: bool | None = None
        self._prediction_revision_locked = False

    @property
    def state(self) -> WorkflowState:
        return self._state

    @property
    def inputs(self) -> CalculateCommand | None:
        return self._inputs

    @property
    def analysis(self) -> LockedAnalysisView | None:
        return self._analysis

    @property
    def post_run_choices(self) -> tuple[bool | None, bool | None]:
        return self._result, self._include

    @property
    def can_modify_prediction(self) -> bool:
        """Read-only presentation of the existing modify state and irreversible audit lock."""
        return self._state == WorkflowState.PENDING_LOCKED and not self._prediction_revision_locked

    def _require(self, *states: WorkflowState) -> None:
        if self._state not in states:
            raise InvalidWorkflowTransitionError(
                f"Operation is not allowed in {self._state.value}."
            )

    def set_inputs(self, command: CalculateCommand) -> None:
        self._require(WorkflowState.DRAFT, WorkflowState.PENDING_EDIT)
        self._inputs = command

    def calculate(self) -> LockedAnalysisView:
        self._require(WorkflowState.DRAFT, WorkflowState.PENDING_EDIT)
        if self._inputs is None:
            raise InvalidWorkflowTransitionError("Prediction inputs have not been provided.")
        previous_state = self._state
        self._state = WorkflowState.CALCULATING
        try:
            if previous_state == WorkflowState.DRAFT:
                view = self._rounds.calculate(self._inputs)
            else:
                assert self._analysis is not None
                view = self._rounds.recalculate(self._analysis.round_id, self._inputs)
        except Exception:
            self._state = previous_state
            raise
        self._analysis = view
        if previous_state == WorkflowState.DRAFT:
            self._prediction_revision_locked = False
        self._state = WorkflowState.PENDING_LOCKED
        return view

    def modify(self) -> None:
        self._require(WorkflowState.PENDING_LOCKED)
        if self._prediction_revision_locked:
            raise InvalidWorkflowTransitionError(
                "Prediction revision is closed after result selection or recovery."
            )
        self._result = self._include = None
        self._state = WorkflowState.PENDING_EDIT

    def choose_result(self, result: bool) -> None:
        self._require(WorkflowState.PENDING_LOCKED)
        require_bool(result, "result")
        self._result = result
        # Outcome knowledge cannot be undone by changing post-run choices or going Back.
        self._prediction_revision_locked = True
        self._confirm_if_ready()

    def choose_include(self, include_character_history: bool) -> None:
        self._require(WorkflowState.PENDING_LOCKED)
        require_bool(include_character_history, "include_character_history")
        self._include = include_character_history
        self._confirm_if_ready()

    def _confirm_if_ready(self) -> None:
        if self._result is not None and self._include is not None:
            self._state = WorkflowState.CONFIRM_SAVE

    def back(self) -> None:
        self._require(WorkflowState.CONFIRM_SAVE)
        self._state = WorkflowState.PENDING_LOCKED

    def confirm_save(self) -> CompletionResult:
        self._require(WorkflowState.CONFIRM_SAVE)
        assert self._analysis is not None and self._result is not None and self._include is not None
        self._state = WorkflowState.COMPLETING
        try:
            result = self._rounds.complete_pending(
                self._analysis.round_id, self._result, self._include
            )
        except Exception:
            self._state = WorkflowState.CONFIRM_SAVE
            raise
        self._state = WorkflowState.COMPLETED_NOTICE
        return result

    def void_pending(self, reason: str | None = None) -> VoidResult:
        self._require(WorkflowState.PENDING_LOCKED)
        assert self._analysis is not None
        result = self._rounds.void_pending(self._analysis.round_id, reason)
        self._clear()
        return result

    def inspect_recovery(self) -> RecoveryView:
        self._require(WorkflowState.DRAFT)
        try:
            view = self._recovery.inspect()
        except MultiplePendingRoundsError:
            self._state = WorkflowState.RECOVERY_ERROR
            raise
        if view.state == RecoveryState.RECOVERABLE:
            self._state = WorkflowState.RECOVERY
        return view

    def continue_recovery(self) -> LockedAnalysisView:
        self._require(WorkflowState.RECOVERY)
        try:
            view = self._recovery.continue_pending()
        except MultiplePendingRoundsError:
            self._state = WorkflowState.RECOVERY_ERROR
            raise
        self._analysis = view
        self._inputs = view.inputs
        self._result = self._include = None
        # Lost memory-only choices cannot prove that the outcome was not already known.
        self._prediction_revision_locked = True
        self._state = WorkflowState.PENDING_LOCKED
        return view

    def dismiss_completed(self) -> None:
        self._require(WorkflowState.COMPLETED_NOTICE)
        self._clear()

    def _clear(self) -> None:
        self._state = WorkflowState.DRAFT
        self._inputs = self._analysis = None
        self._result = self._include = None
        self._prediction_revision_locked = False
