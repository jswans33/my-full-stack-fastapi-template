"""Path resolution utilities for UML generation."""

import os
from pathlib import Path


class UmlPathResolver:
    """Handles path resolution for UML files."""

    def __init__(self, source_dir: Path, generated_dir: Path):
        """Initialize the path resolver.

        Args:
            source_dir: The source directory (docs/source)
            generated_dir: The generated UML directory (docs/source/_generated_uml)
        """
        self.source_dir = source_dir.resolve()
        self.generated_dir = generated_dir.resolve()
        print("\nPath resolver initialized:")
        print(f"Source dir: {self.source_dir}")
        print(f"Generated dir: {self.generated_dir}")

    def get_plantuml_generator_path(self, file_path: Path) -> str:
        """Get path for use in plantuml_generator.py.

        Args:
            file_path: The absolute path to a .puml file

        Returns:
            Path for use in index.rst, using forward slashes.
            Path is relative to _generated_uml since that's configured as the plantuml search path.
        """
        abs_file_path = file_path.resolve()
        rel_path = abs_file_path.relative_to(self.generated_dir)
        rel_path_str = str(rel_path).replace(os.sep, "/")

        print(f"\nPath resolution for: {file_path}")
        print(f"Absolute path: {abs_file_path}")
        print(f"Relative path: {rel_path_str}")

        # Return path relative to _generated_uml directory since:
        # 1. Files are already in that directory
        # 2. Sphinx search path points to that directory
        # 3. Paths in index.rst should be relative to search path
        # 4. This matches how Sphinx will look for the files
        return rel_path_str

    def get_sphinx_path(self, file_path: Path) -> str:
        """Get path for use in Sphinx .rst files.

        Args:
            file_path: The absolute path to a .puml file

        Returns:
            Path for use in Sphinx .rst files, using forward slashes
        """
        abs_file_path = file_path.resolve()
        rel_path = abs_file_path.relative_to(self.source_dir)
        rel_path_str = str(rel_path).replace(os.sep, "/")

        print(f"\nPath resolution for: {file_path}")
        print(f"Absolute path: {abs_file_path}")
        print(f"Relative path: {rel_path_str}")

        return rel_path_str

    def get_search_paths(self) -> list[str]:
        """Get search paths for Sphinx configuration.

        Returns:
            List of paths where Sphinx should look for .puml files
        """
        return [str(self.generated_dir)]
