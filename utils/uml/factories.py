"""Factory classes for UML diagram generation.

This module provides factory classes for creating diagram analyzers and generators.
"""

import logging
from collections.abc import Callable
from typing import Any

from utils.uml.core.exceptions import DiagramTypeError
from utils.uml.core.filesystem import FileSystem
from utils.uml.core.interfaces import DiagramAnalyzer, DiagramFactory, DiagramGenerator
from utils.uml.diagrams.activity_diagram.analyzer import ActivityAnalyzer
from utils.uml.diagrams.activity_diagram.generator import ActivityDiagramGenerator
from utils.uml.diagrams.class_diagram.analyzer import ClassAnalyzer
from utils.uml.diagrams.class_diagram.generator import ClassDiagramGenerator
from utils.uml.diagrams.sequence_diagram.analyzer import SequenceAnalyzer
from utils.uml.diagrams.sequence_diagram.generator import SequenceDiagramGenerator
from utils.uml.diagrams.state_diagram.analyzer import StateAnalyzer
from utils.uml.diagrams.state_diagram.generator import StateDiagramGenerator


class DefaultDiagramFactory(DiagramFactory):
    """Default implementation of DiagramFactory."""

    def __init__(self, file_system: FileSystem, settings: dict[str, Any] | None = None):
        """Initialize factory with file system and settings.

        Args:
            file_system: The file system implementation to use
            settings: Optional settings for the factory
        """
        self.file_system = file_system
        self.settings = settings or {}
        self.logger = logging.getLogger(__name__)

        # Cache for created instances
        self._analyzers: dict[str, DiagramAnalyzer] = {}
        self._generators: dict[str, DiagramGenerator] = {}

        # Define creator functions
        self._analyzer_creators: dict[str, Callable[..., DiagramAnalyzer]] = {}
        self._generator_creators: dict[str, Callable[..., DiagramGenerator]] = {}

        # Register built-in diagram types
        self._register_built_in_types()

    def _register_built_in_types(self) -> None:
        """Register built-in diagram types."""
        # Register sequence diagram
        self._analyzer_creators["sequence"] = lambda **kwargs: SequenceAnalyzer(
            self.file_system,
            kwargs.get("root_dir", "."),
        )
        self._generator_creators["sequence"] = (
            lambda **kwargs: SequenceDiagramGenerator(
                self.file_system,
                {**self.settings.get("sequence_generator", {}), **kwargs},
            )
        )

        # Register class diagram
        self._analyzer_creators["class"] = lambda **kwargs: ClassAnalyzer(
            self.file_system
        )
        self._generator_creators["class"] = lambda **kwargs: ClassDiagramGenerator(
            self.file_system,
            {**self.settings.get("class_generator", {}), **kwargs},
        )

        # Register activity diagram
        self._analyzer_creators["activity"] = lambda **kwargs: ActivityAnalyzer(
            self.file_system
        )
        self._generator_creators["activity"] = (
            lambda **kwargs: ActivityDiagramGenerator(
                self.file_system,
                {**self.settings.get("activity_generator", {}), **kwargs},
            )
        )

        # Register state diagram
        self._analyzer_creators["state"] = lambda **kwargs: StateAnalyzer(
            self.file_system
        )
        self._generator_creators["state"] = lambda **kwargs: StateDiagramGenerator(
            self.file_system,
            {**self.settings.get("state_generator", {}), **kwargs},
        )

    def create_analyzer(self, diagram_type: str, **kwargs) -> DiagramAnalyzer:
        """Create an analyzer for the given diagram type.

        Args:
            diagram_type: The type of diagram to create an analyzer for
            **kwargs: Additional analyzer-specific arguments

        Returns:
            A diagram analyzer for the given diagram type

        Raises:
            DiagramTypeError: If the diagram type is not supported
        """
        # Return cached analyzer if available
        if diagram_type in self._analyzers:
            return self._analyzers[diagram_type]

        # Create analyzer if type is supported
        if diagram_type in self._analyzer_creators:
            analyzer = self._analyzer_creators[diagram_type](**kwargs)
            self._analyzers[diagram_type] = analyzer
            return analyzer

        # Diagram type not supported
        self.logger.error(f"No analyzer available for diagram type: {diagram_type}")
        raise DiagramTypeError(f"Unsupported diagram type: {diagram_type}")

    def create_generator(self, diagram_type: str, **kwargs) -> DiagramGenerator:
        """Create a generator for the given diagram type.

        Args:
            diagram_type: The type of diagram to create a generator for
            **kwargs: Additional generator-specific arguments

        Returns:
            A diagram generator for the given diagram type

        Raises:
            DiagramTypeError: If the diagram type is not supported
        """
        # Return cached generator if available
        if diagram_type in self._generators:
            return self._generators[diagram_type]

        # Create generator if type is supported
        if diagram_type in self._generator_creators:
            generator = self._generator_creators[diagram_type](**kwargs)
            self._generators[diagram_type] = generator
            return generator

        # Diagram type not supported
        self.logger.error(f"No generator available for diagram type: {diagram_type}")
        raise DiagramTypeError(f"Unsupported diagram type: {diagram_type}")

    def register_analyzer(
        self,
        diagram_type: str,
        creator_func: Callable[..., DiagramAnalyzer],
    ) -> None:
        """Register a new analyzer creator function for a diagram type.

        Args:
            diagram_type: The diagram type to register the analyzer for
            creator_func: A function that creates an analyzer instance
        """
        # Clear cache for this type to force recreation on next use
        if diagram_type in self._analyzers:
            del self._analyzers[diagram_type]

        # Register the creator function
        self._analyzer_creators[diagram_type] = creator_func

    def register_generator(
        self,
        diagram_type: str,
        creator_func: Callable[..., DiagramGenerator],
    ) -> None:
        """Register a new generator creator function for a diagram type.

        Args:
            diagram_type: The diagram type to register the generator for
            creator_func: A function that creates a generator instance
        """
        # Clear cache for this type to force recreation on next use
        if diagram_type in self._generators:
            del self._generators[diagram_type]

        # Register the creator function
        self._generator_creators[diagram_type] = creator_func
