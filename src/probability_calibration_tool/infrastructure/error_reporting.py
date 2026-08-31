import logging
from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class ErrorPresentation:
    message: str
    error_id: str


def report_error(logger: logging.Logger, error: Exception, message: str) -> ErrorPresentation:
    error_id = str(uuid4())
    logger.error(
        "error_id=%s %s", error_id, message, exc_info=(type(error), error, error.__traceback__)
    )
    return ErrorPresentation(message, error_id)
