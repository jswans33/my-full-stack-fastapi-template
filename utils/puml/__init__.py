"""
PlantUML Utilities Package

This package provides utilities for working with PlantUML diagrams in the project.

Features:
- Render PlantUML diagrams to PNG or SVG images
- View rendered diagrams in a React-based viewer
- Analyze code and generate PlantUML diagrams automatically
- Command-line interface for rendering, viewing, and analyzing code
"""

import os
import sys

# Add the parent directory to sys.path to allow imports to work
# regardless of where the code is executed from
package_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(package_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try to import using relative imports first, then fall back to absolute imports
try:
    # Import the main functions for the public API
    from .code_analyzer import (
        analyze_and_generate_diagram,
        analyze_directory,
        analyze_file,
        generate_class_diagram,
        generate_module_diagram,
        save_diagram,
    )
    from .config import (
        DEFAULT_FORMAT,
        FORMATS,
        OUTPUT_DIR,
        SOURCE_DIR,
    )
    from .core import ensure_dir_exists, setup_logger
    from .render_diagrams import (
        launch_viewer,
        render_all_diagrams,
        render_diagram,
    )
except (ImportError, ValueError):
    # Fall back to absolute imports
    from utils.puml.code_analyzer import (
        analyze_and_generate_diagram,
        analyze_directory,
        analyze_file,
        generate_class_diagram,
        generate_module_diagram,
        save_diagram,
    )
    from utils.puml.config import (
        DEFAULT_FORMAT,
        FORMATS,
        OUTPUT_DIR,
        SOURCE_DIR,
    )
    from utils.puml.core import ensure_dir_exists, setup_logger
    from utils.puml.render_diagrams import (
        launch_viewer,
        render_all_diagrams,
        render_diagram,
    )

# Define what's available when using "from utils.puml import *"
__all__ = [
    # Rendering functions
    "render_diagram",
    "render_all_diagrams",
    "launch_viewer",
    # Code analysis functions
    "analyze_file",
    "analyze_directory",
    "analyze_and_generate_diagram",
    "generate_class_diagram",
    "generate_module_diagram",
    "save_diagram",
    # Configuration
    "SOURCE_DIR",
    "OUTPUT_DIR",
    "DEFAULT_FORMAT",
    "FORMATS",
    # Utilities
    "setup_logger",
    "ensure_dir_exists",
]
