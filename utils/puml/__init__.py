"""
PlantUML Utilities Package

This package provides utilities for working with PlantUML diagrams in the project.

Features:
- Render PlantUML diagrams to PNG or SVG images
- View rendered diagrams in a React-based viewer
- Analyze code and generate PlantUML diagrams automatically
- Command-line interface for rendering, viewing, and analyzing code
"""

import sys
from pathlib import Path

# Add the project root to sys.path to allow imports to work
# regardless of where the code is executed from
package_dir = Path(__file__).parent.absolute()
project_root = package_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the main functions for the public API
try:
    # Try absolute imports first
    from utils.puml.code_analyzer import (
        analyze_and_generate_diagram,
        analyze_file,
        generate_class_diagram,
        generate_module_diagram,
        save_diagram,
    )
    from utils.puml.core import ensure_dir_exists, setup_logger
    from utils.puml.render_diagrams import (
        launch_viewer,
        render_all_diagrams,
        render_diagram,
    )
    from utils.puml.settings import settings
except ImportError:
    # Fall back to relative imports
    from .code_analyzer import (
        analyze_and_generate_diagram,
        analyze_file,
        generate_class_diagram,
        generate_module_diagram,
        save_diagram,
    )
    from .core import ensure_dir_exists, setup_logger
    from .render_diagrams import (
        launch_viewer,
        render_all_diagrams,
        render_diagram,
    )
    from .settings import settings

# Define what's available when using "from utils.puml import *"
__all__ = [
    # Rendering functions
    "render_diagram",
    "render_all_diagrams",
    "launch_viewer",
    # Code analysis functions
    "analyze_file",
    "analyze_and_generate_diagram",
    "generate_class_diagram",
    "generate_module_diagram",
    "save_diagram",
    # Configuration
    "settings",
    # Utilities
    "setup_logger",
    "ensure_dir_exists",
]
