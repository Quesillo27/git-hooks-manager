"""Logger estructurado para hookman.

Niveles: DEBUG, INFO, WARNING, ERROR. Se controla con HOOKMAN_LOG_LEVEL.
La salida principal va a stderr. Los comandos siguen imprimiendo a stdout
para no romper composición con pipes.
"""

import logging
import sys
from typing import Optional

from hookman.config import DEFAULT_LOG_LEVEL


_LOGGER_NAME = "hookman"
_configured = False


def get_logger(level: Optional[str] = None) -> logging.Logger:
    """Devuelve el logger configurado de hookman."""
    global _configured
    logger = logging.getLogger(_LOGGER_NAME)
    if not _configured:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] hookman: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        _configured = True

    target_level = (level or DEFAULT_LOG_LEVEL).upper()
    if target_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        target_level = "INFO"
    logger.setLevel(getattr(logging, target_level))
    return logger


def reset_logger() -> None:
    """Resetea el logger — útil para tests."""
    global _configured
    logger = logging.getLogger(_LOGGER_NAME)
    for h in list(logger.handlers):
        logger.removeHandler(h)
    _configured = False
