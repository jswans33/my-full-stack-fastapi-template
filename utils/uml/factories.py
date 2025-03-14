"""Factory classes for UML diagram generation.

This module provides factory classes for creating diagram analyzers and generators.
"""

import logging
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
        # Create analyzer if not cached
        if diagram_type not in self._analyzers:
            if diagram_type == "sequence":
                # Create sequence analyzer
                root_dir = kwargs.get("root_dir", ".")
                analyzer = SequenceAnalyzer(self.file_system, root_dir)
                self._analyzers["sequence"] = analyzer
            elif diagram_type == "class":
                # Create class analyzer
                analyzer = ClassAnalyzer(self.file_system)
                self._analyzers["class"] = analyzer
            elif diagram_type == "activity":
                # Create activity analyzer
                analyzer = ActivityAnalyzer(self.file_system)
                self._analyzers["activity"] = analyzer
            elif diagram_type == "state":
                # Create state analyzer
                analyzer = StateAnalyzer(self.file_system)
                self._analyzers["state"] = analyzer
            else:
                self.logger.error(
                    f"No analyzer available for diagram type: {diagram_type}",
                )
                raise DiagramTypeError(f"Unsupported diagram type: {diagram_type}")

        return self._analyzers[diagram_type]

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
        # Create generator if not cached
        if diagram_type not in self._generators:
            if diagram_type == "sequence":
                # Create sequence generator
                settings = {**self.settings.get("sequence_generator", {}), **kwargs}
                generator = SequenceDiagramGenerator(self.file_system, settings)
                self._generators["sequence"] = generator
            elif diagram_type == "class":
                # Create class generator
                settings = {**self.settings.get("class_generator", {}), **kwargs}
                generator = ClassDiagramGenerator(self.file_system, settings)
                self._generators["class"] = generator
            elif diagram_type == "activity":
                # Create activity generator
                settings = {**self.settings.get("activity_generator", {}), **kwargs}
                generator = ActivityDiagramGenerator(self.file_system, settings)
                self._generators["activity"] = generator
            elif diagram_type == "state":
                # Create state generator
                settings = {**self.settings.get("state_generator", {}), **kwargs}
                generator = StateDiagramGenerator(self.file_system, settings)
                self._generators["state"] = generator
            else:
                self.logger.error(
                    f"No generator available for diagram type: {diagram_type}",
                )
                raise DiagramTypeError(f"Unsupported diagram type: {diagram_type}")

        return self._generators[diagram_type]

    def register_analyzer(
        self,
        diagram_type: str,
        analyzer_class: type[DiagramAnalyzer],
    ) -> None:
        """Register a new analyzer class for a diagram type.

        Args:
            diagram_type: The diagram type to register the analyzer for
            analyzer_class: The analyzer class to register
        """
        # This basic implementation doesn't support dynamic registration
        # Clear cache for this type to force recreation on next use
        if diagram_type in self._analyzers:
            del self._analyzers[diagram_type]

    def register_generator(
        self,
        diagram_type: str,
        generator_class: type[DiagramGenerator],
    ) -> None:
        """Register a new generator class for a diagram type.

        Args:
            diagram_type: The diagram type to register the generator for
            generator_class: The generator class to register
        """
        # This basic implementation doesn't support dynamic registration
        # Clear cache for this type to force recreation on next use
        if diagram_type in self._generators:
            del self._generators[diagram_type]
