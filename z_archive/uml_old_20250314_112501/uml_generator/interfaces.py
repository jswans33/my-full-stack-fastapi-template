from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol

from .models import FileModel


class FileSystem(Protocol):
    """Interface for file system operations."""

    def read_file(self, path: Path) -> str:
        """Read file content as string."""
        ...

    def write_file(self, path: Path, content: str) -> None:
        """Write content to file."""
        ...

    def ensure_directory(self, path: Path) -> None:
        """Ensure directory exists, create if needed."""
        ...

    def find_files(self, directory: Path, pattern: str) -> list[Path]:
        """Find files matching pattern in directory."""
        ...


class FileParser(ABC):
    """Abstract base class for file parsers."""

    @abstractmethod
    def parse_file(self, file_path: Path) -> FileModel:
        """Parse file and return model representation."""
        pass

    @abstractmethod
    def get_supported_extensions(self) -> set[str]:
        """Return set of supported file extensions."""
        pass


class DiagramGenerator(ABC):
    """Abstract base class for diagram generators."""

    @abstractmethod
    def generate_diagram(self, file_model: FileModel, output_path: Path) -> None:
        """Generate diagram from file model and write to output path."""
        pass

    @abstractmethod
    def get_output_extension(self) -> str:
        """Return output file extension for this generator."""
        pass

    def generate_index(self, output_dir: Path, diagrams: list[Path]) -> None:
        """Generate an index file for the generated diagrams.

        This is an optional method that generators can implement to create
        an index of all generated diagrams.
        """
        pass


class ParserFactory(ABC):
    """Factory for creating appropriate parser based on file extension."""

    @abstractmethod
    def create_parser(self, file_extension: str) -> FileParser:
        """Create parser for given file extension."""
        pass


class GeneratorFactory(ABC):
    """Factory for creating diagram generators."""

    @abstractmethod
    def create_generator(self, output_format: str) -> DiagramGenerator:
        """Create generator for given output format."""
        pass
