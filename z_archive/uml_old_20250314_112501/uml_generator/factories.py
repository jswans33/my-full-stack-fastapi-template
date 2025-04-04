import logging
from typing import Any

from .generator.plantuml_generator import PlantUmlGenerator
from .generator.sequence_generator import SequenceDiagramGenerator
from .interfaces import (
    DiagramGenerator,
    FileParser,
    FileSystem,
    GeneratorFactory,
    ParserFactory,
)
from .parsers.python import PythonAstParser


class DefaultParserFactory(ParserFactory):
    """Default implementation of ParserFactory."""

    def __init__(self, file_system: FileSystem):
        self.file_system = file_system
        self.logger = logging.getLogger(__name__)
        self._parsers = {}

    def create_parser(self, file_extension: str) -> FileParser:
        """Create parser for given file extension."""
        if file_extension not in self._parsers:
            if file_extension == ".py":
                self._parsers[file_extension] = PythonAstParser(self.file_system)
            else:
                self.logger.warning(
                    f"No parser available for extension: {file_extension}",
                )
                raise ValueError(f"Unsupported file extension: {file_extension}")

        return self._parsers[file_extension]


class DefaultGeneratorFactory(GeneratorFactory):
    """Default implementation of GeneratorFactory."""

    def __init__(self, file_system: FileSystem, settings: dict[str, Any] | None = None):
        self.file_system = file_system
        self.settings = settings or {}
        self.logger = logging.getLogger(__name__)
        self._generators = {}

    def create_generator(self, output_format: str) -> DiagramGenerator:
        """Create generator for given output format."""
        if output_format not in self._generators:
            if output_format == "plantuml":
                self._generators[output_format] = PlantUmlGenerator(
                    self.file_system,
                    self.settings,
                )
            elif output_format == "sequence":
                self._generators[output_format] = SequenceDiagramGenerator(
                    self.file_system,
                    self.settings.get("sequence_settings", {}),
                )
            else:
                self.logger.warning(
                    f"No generator available for format: {output_format}",
                )
                raise ValueError(f"Unsupported output format: {output_format}")

        return self._generators[output_format]
