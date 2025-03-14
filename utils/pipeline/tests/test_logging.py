"""
Tests for the logging module.

This file tests the centralized logging configuration.
"""

import logging

from ..utils.logging import (
    DEFAULT_LEVEL,
    disable_logging,
    enable_debug_logging,
    get_logger,
    set_log_level,
    setup_logger,
)


def test_setup_logger_default():
    """Test logger setup with default configuration."""
    logger = setup_logger("test")
    assert logger.level == DEFAULT_LEVEL
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_setup_logger_custom_level():
    """Test logger setup with custom log level."""
    # Test with string level
    logger = setup_logger("test.level.string", level="DEBUG")
    assert logger.level == logging.DEBUG

    # Test with integer level
    logger = setup_logger("test.level.int", level=logging.ERROR)
    assert logger.level == logging.ERROR


def test_setup_logger_with_file(tmp_path):
    """Test logger setup with file output."""
    log_file = tmp_path / "test.log"
    logger = setup_logger("test.file", log_file=str(log_file))

    # Should have both console and file handlers
    assert len(logger.handlers) == 2
    assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    # Test that the log directory is created
    nested_log_file = tmp_path / "logs" / "nested" / "test.log"
    logger = setup_logger("test.file.nested", log_file=str(nested_log_file))
    assert nested_log_file.parent.exists()


def test_get_logger():
    """Test the convenience get_logger function."""
    logger = get_logger("test.get")
    assert logger.level == DEFAULT_LEVEL
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_set_log_level():
    """Test setting log level for all pipeline loggers."""
    # Create some test loggers
    logger1 = get_logger("pipeline.test1")
    logger2 = get_logger("pipeline.test2")
    other_logger = get_logger("other.logger")  # Should not be affected

    # Test setting level with string
    set_log_level("DEBUG")
    assert logger1.level == logging.DEBUG
    assert logger2.level == logging.DEBUG
    assert other_logger.level == DEFAULT_LEVEL  # Should not change

    # Test setting level with integer
    set_log_level(logging.ERROR)
    assert logger1.level == logging.ERROR
    assert logger2.level == logging.ERROR
    assert other_logger.level == DEFAULT_LEVEL  # Should not change


def test_enable_debug_logging():
    """Test enabling debug logging."""
    logger = get_logger("pipeline.debug")
    enable_debug_logging()
    assert logger.level == logging.DEBUG


def test_disable_logging():
    """Test disabling logging."""
    logger = get_logger("pipeline.disabled")
    disable_logging()
    assert logger.level == logging.CRITICAL


def test_logger_output(tmp_path, capsys):
    """Test actual logger output."""
    # Test console output
    logger = get_logger("test.output")
    test_message = "Test log message"
    logger.info(test_message)
    captured = capsys.readouterr()
    assert test_message in captured.err

    # Test file output
    log_file = tmp_path / "output.log"
    logger = setup_logger("test.output.file", log_file=str(log_file))
    logger.info(test_message)

    with open(log_file) as f:
        log_content = f.read()
        assert test_message in log_content


def test_multiple_setup_calls():
    """Test that multiple setup calls don't duplicate handlers."""
    logger_name = "test.multiple"
    logger1 = setup_logger(logger_name)
    initial_handlers = len(logger1.handlers)

    # Second setup call should not add handlers
    logger2 = setup_logger(logger_name)
    assert len(logger2.handlers) == initial_handlers
    assert logger1 is logger2  # Should be the same logger instance
