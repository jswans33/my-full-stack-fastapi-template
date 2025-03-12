"""
PlantUML Core Utilities

This module provides core utilities and shared functionality for the PlantUML package.
"""

import logging
from pathlib import Path

from .exceptions import LoggingError, PathError
from .settings import settings


def setup_logger(name: str = "puml", verbose: bool | None = None) -> logging.Logger:
    """
    Set up and configure a logger with consistent formatting.

    Args:
        name: Logger name
        verbose: Override the global verbose setting

    Returns:
        Configured logger instance

    Raises:
        LoggingError: If there is an error configuring the logger
    """
    try:
        # Use provided verbose setting or fall back to global setting
        is_verbose = verbose if verbose is not None else settings.verbose
        level = logging.DEBUG if is_verbose else logging.INFO

        # Get or create logger
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Only add handler if none exist
        if not logger.handlers and not (logger.parent and logger.parent.handlers):
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(settings.log_format))
            logger.addHandler(handler)

        return logger
    except Exception as e:
        raise LoggingError(f"Failed to setup logger: {e}") from e


def ensure_dir_exists(path: str | Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists

    Returns:
        Path object for the directory

    Raises:
        PathError: If the directory cannot be created
    """
    try:
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj
    except Exception as e:
        raise PathError(f"Failed to create directory {path}: {e}") from e


def get_relative_path(path: str | Path, base_dir: str | Path) -> Path:
    """
    Get the path relative to a base directory.

    Args:
        path: Path to get relative path for
        base_dir: Base directory to get path relative to

    Returns:
        Relative path from base_dir to path

    Raises:
        PathError: If the relative path cannot be determined
    """
    try:
        path_obj = Path(path).resolve()
        base_obj = Path(base_dir).resolve()

        # Handle the case where path is a file
        if path_obj.is_file():
            path_obj = path_obj.parent

        return path_obj.relative_to(base_obj)
    except ValueError as e:
        raise PathError(f"Could not determine relative path: {e}") from e


def get_output_path(input_file: str | Path, format: str) -> Path:
    """
    Generate the output path for a rendered diagram.

    Args:
        input_file: Path to the input .puml file
        format: Output format (e.g., 'svg', 'png')

    Returns:
        Path where the rendered diagram should be saved

    Raises:
        PathError: If the output path cannot be determined
    """
    try:
        # Get path relative to source directory
        rel_path = get_relative_path(input_file, settings.source_dir)

        # Create output subdirectory matching source structure
        output_subdir = settings.output_dir / rel_path
        ensure_dir_exists(output_subdir)

        # Generate output filename
        input_path = Path(input_file)
        output_name = input_path.stem + f".{format}"
        return output_subdir / output_name
    except Exception as e:
        raise PathError(f"Failed to generate output path: {e}") from e


# Initialize logger for this module
logger = setup_logger(__name__)
