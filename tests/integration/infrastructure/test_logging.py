from dataclasses import asdict
from logging.handlers import RotatingFileHandler

from probability_calibration_tool.infrastructure.error_reporting import report_error
from probability_calibration_tool.infrastructure.logging_setup import (
    bootstrap_logger,
    close_logger,
    full_logger,
)


def test_bootstrap_does_not_open_rotating_log(rig):
    logger = bootstrap_logger()
    try:
        assert not any(isinstance(handler, RotatingFileHandler) for handler in logger.handlers)
        assert not rig.paths.log_file.exists()
    finally:
        close_logger(logger)


def test_error_id_traceback_safe_presentation_and_real_rotation(rig):
    logger = full_logger(rig.paths.log_file)
    try:
        handler = logger.handlers[0]
        assert isinstance(handler, RotatingFileHandler)
        assert handler.maxBytes == 2 * 1024 * 1024 and handler.backupCount == 5
        try:
            raise RuntimeError("private exception details")
        except RuntimeError as exc:
            first = report_error(logger, exc, "Operation failed safely.")
            second = report_error(logger, exc, "Operation failed safely.")
        handler.flush()
        log = rig.paths.log_file.read_text(encoding="utf-8")
        assert first.error_id != second.error_id
        assert first.error_id in log and "Traceback" in log and "private exception details" in log
        assert set(asdict(first)) == {"message", "error_id"}
        assert "Traceback" not in str(asdict(first)) and "private" not in str(asdict(first))
        for index in range(7):
            logger.warning("generation=%s %s", index, "x" * (2 * 1024 * 1024))
        handler.flush()
        assert all(rig.paths.log_file.with_name(f"app.log.{i}").exists() for i in range(1, 6))
        assert not rig.paths.log_file.with_name("app.log.6").exists()
        assert "generation=6" in rig.paths.log_file.read_text(encoding="utf-8")
    finally:
        close_logger(logger)
