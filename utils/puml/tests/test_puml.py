"""
PlantUML Utilities Test Script

This script tests the PlantUML utilities to ensure they are working correctly.
It checks that the diagrams can be loaded and rendered.

Usage:
    python test_puml.py
"""

import os
import sys
import unittest
from pathlib import Path
from typing import Protocol, TypeVar, Union

# Add the project root to sys.path to ensure imports work correctly
project_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Define type variables for better type hints
PathLike = Union[str, Path]
P = TypeVar("P", str, Path)


# Define protocols for our functions
class EnsureDirExistsProtocol(Protocol):
    def __call__(self, path: PathLike) -> Path: ...


class RenderDiagramProtocol(Protocol):
    def __call__(
        self, puml_file: str, output_dir: str | None = None, format: str = "svg"
    ) -> bool: ...


# Define a function to get the source directory
def get_source_dir() -> Path:
    """Get the source directory for diagrams."""
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent.parent
    return project_root / "docs" / "diagrams"


# Set default values
SOURCE_DIR = get_source_dir()


# Define fallback functions in case imports fail
def default_ensure_dir_exists(path: PathLike) -> Path:
    """Ensure a directory exists."""
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def default_render_diagram(
    puml_file: str,
    output_dir: str | None = None,
    format: str = "svg",
) -> bool:
    """Stub for render_diagram if import fails."""
    print(f"Warning: Using stub render_diagram function for {puml_file}")
    return False


# Set initial values to the default functions
ensure_dir_exists: EnsureDirExistsProtocol = default_ensure_dir_exists
render_diagram: RenderDiagramProtocol = default_render_diagram

# Import the required modules
try:
    # Try absolute imports first (when running from project root)
    from utils.puml.core import ensure_dir_exists as core_ensure_dir_exists
    from utils.puml.render_diagrams import render_diagram as render_diagram_func
    from utils.puml.settings import settings

    # Update the variables with the imported functions
    SOURCE_DIR = settings.source_dir
    ensure_dir_exists = core_ensure_dir_exists
    render_diagram = render_diagram_func
except ImportError:
    try:
        # Then try relative imports (when running as a module)
        from ..core import ensure_dir_exists as core_ensure_dir_exists
        from ..render_diagrams import render_diagram as render_diagram_func
        from ..settings import settings

        # Update the variables with the imported functions
        SOURCE_DIR = settings.source_dir
        ensure_dir_exists = core_ensure_dir_exists
        render_diagram = render_diagram_func
    except (ImportError, ValueError):
        try:
            # Finally try direct imports (when running from the utils/puml directory)
            from core import ensure_dir_exists as core_ensure_dir_exists
            from render_diagrams import render_diagram as render_diagram_func
            from settings import settings

            # Update the variables with the imported functions
            SOURCE_DIR = settings.source_dir
            ensure_dir_exists = core_ensure_dir_exists
            render_diagram = render_diagram_func
        except ImportError:
            # If all imports fail, we'll use the default functions and SOURCE_DIR
            pass


class TestPlantUML(unittest.TestCase):
    """Test case for PlantUML utilities."""

    def setUp(self):
        """Set up the test case."""
        # Get the directory containing this script
        self.script_dir = Path(__file__).parent

        # Create a temporary output directory
        self.output_dir = self.script_dir / "test_output"
        ensure_dir_exists(self.output_dir)

    def tearDown(self):
        """Clean up after the test case."""
        # Remove the temporary output directory and its contents
        if self.output_dir.exists():
            # Walk through all files and directories
            for item in self.output_dir.glob("**/*"):
                if item.is_file():
                    try:
                        item.unlink()
                    except (PermissionError, OSError) as e:
                        print(f"Warning: Could not remove file {item}: {e}")

            # Remove all empty directories
            for item in sorted(self.output_dir.glob("**/*"), reverse=True):
                if item.is_dir():
                    try:
                        item.rmdir()
                    except (PermissionError, OSError) as e:
                        print(f"Warning: Could not remove directory {item}: {e}")

            # Finally remove the output directory itself
            try:
                self.output_dir.rmdir()
            except (PermissionError, OSError) as e:
                print(
                    f"Warning: Could not remove output directory {self.output_dir}: {e}"
                )

    def test_diagram_files_exist(self):
        """Test that the diagram files exist."""
        # Check that the diagram files exist
        diagram_files = [
            "architecture/puml_utilities.puml",
            "architecture/puml_viewer_class_diagram.puml",
        ]

        for file in diagram_files:
            file_path = SOURCE_DIR / file
            self.assertTrue(
                file_path.exists(),
                f"Diagram file not found: {file_path}",
            )

    def test_render_diagram_png(self):
        """Test that a diagram can be rendered to PNG."""
        # Get the path to a diagram file
        diagram_file = SOURCE_DIR / "architecture" / "puml_utilities.puml"

        # Render the diagram with explicit output directory
        result = render_diagram(str(diagram_file), str(self.output_dir), "png")

        # Check that the rendering was successful
        self.assertTrue(result, "Diagram rendering failed")

        # Check that the output file was created (with preserved directory structure)
        output_file = self.output_dir / "architecture" / "puml_utilities.png"
        self.assertTrue(
            output_file.exists(),
            f"Output file not found: {output_file}",
        )

    def test_render_diagram_svg(self):
        """Test that a diagram can be rendered to SVG."""
        # Get the path to a diagram file
        diagram_file = SOURCE_DIR / "architecture" / "puml_viewer_class_diagram.puml"

        # Render the diagram with explicit output directory
        result = render_diagram(str(diagram_file), str(self.output_dir), "svg")

        # Check that the rendering was successful
        self.assertTrue(result, "Diagram rendering failed")

        # Check that the output file was created (with preserved directory structure)
        output_file = self.output_dir / "architecture" / "puml_viewer_class_diagram.svg"
        self.assertTrue(
            output_file.exists(),
            f"Output file not found: {output_file}",
        )


def main():
    """Run the tests."""
    unittest.main()


if __name__ == "__main__":
    main()
