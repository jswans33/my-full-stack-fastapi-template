"""Base classes for UML diagrams.

This module provides base implementations of the core interfaces for UML diagrams.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from utils.uml.core.exceptions import GeneratorError
from utils.uml.core.filesystem import FileSystem
from utils.uml.core.interfaces import DiagramAnalyzer, DiagramGenerator, DiagramModel


class BaseDiagramModel(DiagramModel, ABC):
    """Base implementation of the DiagramModel interface."""

    def __init__(self, name: str, diagram_type: str):
        """Initialize a base diagram model.

        Args:
            name: The name of the diagram
            diagram_type: The type of the diagram (class, sequence, etc.)
        """
        self._name = name
        self._diagram_type = diagram_type

    @property
    def name(self) -> str:
        """Return the name of the diagram."""
        return self._name

    @property
    def diagram_type(self) -> str:
        """Return the type of the diagram."""
        return self._diagram_type


class BaseDiagramAnalyzer(DiagramAnalyzer, ABC):
    """Base implementation of the DiagramAnalyzer interface."""

    def __init__(self, file_system: FileSystem):
        """Initialize a base diagram analyzer.

        Args:
            file_system: The file system implementation to use
        """
        self.file_system = file_system

    @abstractmethod
    def analyze(self, path: str | Path, **kwargs) -> DiagramModel:
        """Analyze the source code at the given path and return a diagram model."""
        pass


class BaseDiagramGenerator(DiagramGenerator, ABC):
    """Base implementation of the DiagramGenerator interface."""

    def __init__(self, file_system: FileSystem, settings: dict[str, Any] | None = None):
        """Initialize a base diagram generator.

        Args:
            file_system: The file system implementation to use
            settings: Optional settings for the generator
        """
        self.file_system = file_system
        self.settings = settings or {}

    @abstractmethod
    def generate_diagram(
        self,
        model: DiagramModel,
        output_path: str | Path,
        **kwargs,
    ) -> None:
        """Generate a UML diagram from the given model and write it to the output path."""
        pass

    def generate_index(
        self,
        output_dir: str | Path,
        diagrams: list[Path],
        **kwargs,
    ) -> None:
        """Generate an index file for all diagrams in the output directory.

        Args:
            output_dir: The directory containing the diagrams
            diagrams: A list of paths to all diagrams
            **kwargs: Additional generator-specific arguments

        Raises:
            GeneratorError: If the index file cannot be generated
        """
        try:
            output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
            index_path = output_dir / "index.rst"

            # Create basic RST index
            lines = [
                "UML Diagrams",
                "===========",
                "",
                ".. toctree::",
                "   :maxdepth: 2",
                "   :caption: Available Diagrams:",
                "",
            ]

            # Add diagram references
            for diagram in sorted(diagrams):
                rel_path = diagram.relative_to(output_dir)
                # Use forward slashes for cross-platform compatibility
                lines.append(f"   {str(rel_path).replace('\\', '/')}")

            lines.append("")  # Add trailing newline

            # Write the index file
            self.file_system.write_file(index_path, "\n".join(lines))

        except Exception as e:
            raise GeneratorError(f"Failed to generate index file: {e}", cause=e)
