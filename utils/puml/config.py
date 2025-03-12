"""
PlantUML Configuration

This module contains configuration settings for the PlantUML utilities.
"""

import os
import sys


# Determine the project root directory more robustly
def get_project_root():
    """
    Get the project root directory in a way that works regardless of where the code is executed from.

    Returns:
        str: The absolute path to the project root directory
    """
    # Start with the directory containing this file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Try to find the project root by looking for key directories/files
    # that indicate the project root
    potential_root = current_dir
    for _ in range(5):  # Limit the search depth to avoid infinite loops
        # Check if this looks like the project root
        if os.path.isdir(os.path.join(potential_root, "docs")) and os.path.isdir(
            os.path.join(potential_root, "utils")
        ):
            return potential_root

        # Move up one directory
        parent = os.path.dirname(potential_root)
        if parent == potential_root:  # We've reached the filesystem root
            break
        potential_root = parent

    # If we couldn't find a definitive project root, use the default approach
    return os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))


# Project root directory
PROJECT_ROOT = get_project_root()

# Default source directory for diagrams
SOURCE_DIR = os.path.join(PROJECT_ROOT, "docs", "diagrams")

# Default output directory for rendered diagrams
OUTPUT_DIR = os.path.join(SOURCE_DIR, "output")

# PlantUML server URLs
PLANTUML_SERVER_SVG = "http://www.plantuml.com/plantuml/svg/"
PLANTUML_SERVER_PNG = "http://www.plantuml.com/plantuml/img/"

# Supported output formats
FORMATS: list[str] = ["svg", "png"]

# Default output format
DEFAULT_FORMAT = "svg"

# Add the project root to sys.path to ensure imports work correctly
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
