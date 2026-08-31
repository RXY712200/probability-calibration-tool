"""Narrow injected presentation contracts, not production service composition."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from probability_calibration_tool.application.commands import CalculateCommand
from probability_calibration_tool.application.views import LockedAnalysisView, RecoveryView


@dataclass(frozen=True)
class CharacterOption:
    character_id: int
    display_name: str


@dataclass(frozen=True)
class RecoveryPresentation:
    recovery: RecoveryView
    analysis: LockedAnalysisView | None = None

    def __post_init__(self):
        if self.analysis is not None and self.analysis.round_id != self.recovery.round_id:
            raise ValueError("Recovery presentation must describe the same pending round.")


@dataclass(frozen=True)
class BackupCandidate:
    candidate_id: str
    category: str
    created_at: datetime
    reason: str | None = None
    valid: bool = True


@dataclass
class PresentationPorts:
    # None means the corresponding Phase 6 integration is not supplied.
    maintenance_rows: Callable | None = None
    start_regime: Callable | None = None
    recovery_preview: Callable[[], RecoveryPresentation] | None = None
    request_restore: Callable | None = None
    report_unexpected: Callable | None = None


def calculate_command(character_id, reference, probability_text, win_text, lose_text):
    # Transport conversion only: no range checks, clamping, odds parsing or normalization.
    # Malformed text is passed through so Application supplies structured field errors.
    try:
        probability = int(probability_text)
    except ValueError:
        probability = probability_text
    return CalculateCommand(character_id, reference, probability, win_text, lose_text)
