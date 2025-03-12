"""
PlantUML Configuration

This module contains configuration settings for the PlantUML utilities.
"""

import os

# Project root directory
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

# Default source directory for diagrams
SOURCE_DIR = os.path.join(PROJECT_ROOT, "docs", "diagrams")

# Default output directory for rendered diagrams
OUTPUT_DIR = os.path.join(SOURCE_DIR, "output")

# PlantUML server URLs
PLANTUML_SERVER_SVG = "http://www.plantuml.com/plantuml/svg/"
PLANTUML_SERVER_PNG = "http://www.plantuml.com/plantuml/img/"

# Supported output formats
FORMATS = ["svg", "png"]

# Default output format
DEFAULT_FORMAT = "svg"
