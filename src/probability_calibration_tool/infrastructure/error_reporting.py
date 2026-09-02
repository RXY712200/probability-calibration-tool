import logging
from dataclasses import dataclass
from enum import StrEnum
from uuid import uuid4


class SafeErrorCode(StrEnum):
    OPERATION_FAILED = "operation_failed"
    RESTORE_RECOVERY_REQUIRED = "restore_recovery_required"
    RESTORE_NOT_REPLACED = "restore_not_replaced"
    RECENT_BACKUP_FAILED = "recent_backup_failed"
    DAILY_BACKUP_FAILED = "daily_backup_failed"


class WarningCode(StrEnum):
    STATS_REBUILT = "stats_rebuilt"
    BACKUP_OVER_RETENTION = "backup_over_retention"
    QUARANTINE_COPY_FAILED = "quarantine_copy_failed"
    MULTIPLE_PENDING = "multiple_pending"


@dataclass(frozen=True)
class ErrorPresentation:
    message: str
    error_id: str
    code: SafeErrorCode = SafeErrorCode.OPERATION_FAILED


def report_error(
    logger: logging.Logger, error: Exception, message: str, *, code=SafeErrorCode.OPERATION_FAILED
) -> ErrorPresentation:
    error_id = str(uuid4())
    logger.error(
        "error_id=%s %s", error_id, message, exc_info=(type(error), error, error.__traceback__)
    )
    return ErrorPresentation(message, error_id, code)
