"""
Path utilities for the UML generator.

This module provides utility functions for working with paths in the UML generator.
"""

import os
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory.

    This function uses a more reliable approach to find the project root
    by looking for specific markers like docs/source/_generated_uml.

    Returns:
        Path to the project root directory
    """
    # Start with the current file's directory
    current_dir = Path(__file__).parent.absolute()

    # Look for the project root by checking for the docs/source/_generated_uml directory
    # Start from the current directory and go up to 5 levels
    for _ in range(5):
        # Check if this could be the project root
        if (current_dir / "docs" / "source" / "_generated_uml").exists():
            return current_dir

        # Move up one directory
        parent = current_dir.parent
        if parent == current_dir:  # We've reached the filesystem root
            break
        current_dir = parent

    # If we couldn't find the project root, use the current working directory
    # This is a fallback and might not be correct in all cases
    return Path(os.getcwd())


def get_output_base_dir() -> Path:
    """Get the base output directory for UML diagrams.

    Returns:
        Path to the base output directory
    """
    return get_project_root() / "docs" / "source" / "_generated_uml"


def get_output_dir(diagram_type: str | None = None) -> Path:
    """Get the output directory for a specific diagram type.

    Args:
        diagram_type: Type of diagram (class, sequence, activity, state)

    Returns:
        Path to the output directory
    """
    base_dir = get_output_base_dir()

    if diagram_type:
        return base_dir / diagram_type

    return base_dir
