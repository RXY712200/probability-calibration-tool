from dataclasses import dataclass
from enum import StrEnum

from probability_calibration_tool.infrastructure.error_reporting import (
    ErrorPresentation,
    WarningCode,
)


class StartupDisposition(StrEnum):
    READY_DRAFT = "ready_draft"
    READY_RECOVERY = "ready_recovery"
    RECOVERY_ERROR = "recovery_error"
    EMERGENCY_RECOVERY = "emergency_recovery"
    UNSUPPORTED_NEWER_SCHEMA = "unsupported_newer_schema"
    ALREADY_RUNNING = "already_running"
    DATA_SAFETY_ERROR = "data_safety_error"


@dataclass(frozen=True)
class ReliabilityResult:
    disposition: StartupDisposition
    warnings: tuple[WarningCode | ErrorPresentation, ...] = ()
    error: ErrorPresentation | None = None


@dataclass(frozen=True)
class InvariantReport:
    issues: tuple[str, ...]
    pending_count: int


@dataclass(frozen=True)
class StatsValidationResult:
    repaired_regime_ids: tuple[str, ...]


def ready_disposition(pending_count: int) -> StartupDisposition:
    if pending_count > 1:
        return StartupDisposition.RECOVERY_ERROR
    return StartupDisposition.READY_RECOVERY if pending_count else StartupDisposition.READY_DRAFT
