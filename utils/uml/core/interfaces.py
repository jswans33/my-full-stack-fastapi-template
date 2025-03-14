"""Interfaces for UML diagram generation.

This module defines the core interfaces for UML diagram generation, including
models, analyzers, and generators.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class DiagramModel(ABC):
    """Base interface for all diagram models.

    A diagram model represents the parsed information that will be used to generate
    a UML diagram.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the diagram."""
        pass

    @property
    @abstractmethod
    def diagram_type(self) -> str:
        """Return the type of the diagram (class, sequence, etc.)."""
        pass


class DiagramAnalyzer(ABC):
    """Base interface for all diagram analyzers.

    A diagram analyzer is responsible for analyzing source code and creating a
    diagram model from it.
    """

    @abstractmethod
    def analyze(self, path: str | Path, **kwargs) -> DiagramModel:
        """Analyze the source code at the given path and return a diagram model.

        Args:
            path: Path to the source code to analyze
            **kwargs: Additional analyzer-specific arguments

        Returns:
            A diagram model containing the analyzed information
        """
        pass


class DiagramGenerator(ABC):
    """Base interface for all diagram generators.

    A diagram generator is responsible for generating a UML diagram from a
    diagram model.
    """

    @abstractmethod
    def generate_diagram(
        self,
        model: DiagramModel,
        output_path: str | Path,
        **kwargs,
    ) -> None:
        """Generate a UML diagram from the given model and write it to the output path.

        Args:
            model: The diagram model to generate a diagram from
            output_path: The path to write the diagram to
            **kwargs: Additional generator-specific arguments
        """
        pass

    @abstractmethod
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
        """
        pass


class DiagramFactory(ABC):
    """Base interface for diagram factories.

    A diagram factory is responsible for creating appropriate diagram analyzers and
    generators based on the diagram type.
    """

    @abstractmethod
    def create_analyzer(self, diagram_type: str, **kwargs) -> DiagramAnalyzer:
        """Create an analyzer for the given diagram type.

        Args:
            diagram_type: The type of diagram to create an analyzer for
            **kwargs: Additional factory-specific arguments

        Returns:
            A diagram analyzer for the given diagram type
        """
        pass

    @abstractmethod
    def create_generator(self, diagram_type: str, **kwargs) -> DiagramGenerator:
        """Create a generator for the given diagram type.

        Args:
            diagram_type: The type of diagram to create a generator for
            **kwargs: Additional factory-specific arguments

        Returns:
            A diagram generator for the given diagram type
        """
        pass
