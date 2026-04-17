"""Tests del logger estructurado."""

import logging

from hookman.logger import get_logger, reset_logger


def test_logger_has_stream_handler():
    reset_logger()
    log = get_logger("INFO")
    assert any(isinstance(h, logging.StreamHandler) for h in log.handlers)


def test_logger_respects_level():
    reset_logger()
    log = get_logger("DEBUG")
    assert log.level == logging.DEBUG


def test_logger_invalid_level_falls_back():
    reset_logger()
    log = get_logger("BOGUS")
    assert log.level == logging.INFO


def test_logger_is_singleton():
    reset_logger()
    a = get_logger()
    b = get_logger()
    assert a is b
    # Un único handler por más que se llame varias veces
    assert len(a.handlers) == 1
