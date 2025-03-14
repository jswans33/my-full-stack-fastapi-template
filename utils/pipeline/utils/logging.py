"""
Centralized logging configuration for the pipeline.

This module provides a consistent logging setup across all pipeline components.
"""

import logging
from pathlib import Path
from typing import Optional, Union

# Default log format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Default log level
DEFAULT_LEVEL = logging.INFO


def setup_logger(
    name: str,
    level: Optional[Union[str, int]] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Set up a logger with consistent formatting and optional file output.

    Args:
        name: Name of the logger (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string
        log_file: Path to log file (if file logging is desired)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Enable propagation to parent loggers
    logger.propagate = True

    # If this is a pipeline logger, inherit level from root pipeline logger
    if name.startswith("pipeline."):
        root_logger = logging.getLogger("pipeline")
        logger.setLevel(root_logger.level)
    else:
        # Set log level (default to INFO if not specified or invalid)
        if isinstance(level, str):
            level = getattr(logging, level.upper(), DEFAULT_LEVEL)
        logger.setLevel(level or DEFAULT_LEVEL)

    # Create formatter
    formatter = logging.Formatter(log_format or DEFAULT_FORMAT)

    # Always add console handler if none exists
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with default configuration.

    This is a convenience function for getting a logger with default settings.
    For custom configuration, use setup_logger directly.

    Args:
        name: Name of the logger (usually __name__)

    Returns:
        Configured logger instance
    """
    return setup_logger(name)


def set_log_level(level: Union[str, int]) -> None:
    """
    Set the log level for all pipeline loggers.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), DEFAULT_LEVEL)

    # Get the root pipeline logger
    root_logger = logging.getLogger("pipeline")
    root_logger.setLevel(level)

    # Update all child loggers
    for name, logger in logging.root.manager.loggerDict.items():
        if isinstance(logger, logging.Logger) and name.startswith("pipeline"):
            logger.setLevel(level)
            # Ensure child loggers inherit from parent
            logger.propagate = True


def enable_debug_logging() -> None:
    """Enable debug logging for all pipeline components."""
    set_log_level(logging.DEBUG)


def disable_logging() -> None:
    """Disable logging for all pipeline components."""
    set_log_level(logging.CRITICAL)
