import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from uuid import uuid4


def bootstrap_logger() -> logging.Logger:
    logger = logging.getLogger(f"probability.bootstrap.{uuid4()}")
    logger.propagate = False
    logger.addHandler(logging.StreamHandler())
    return logger


def full_logger(path: Path) -> logging.Logger:
    """Caller must own the runtime lock before opening the shared log."""
    logger = logging.getLogger(f"probability.{uuid4()}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = RotatingFileHandler(path, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
    return logger


def close_logger(logger: logging.Logger) -> None:
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
