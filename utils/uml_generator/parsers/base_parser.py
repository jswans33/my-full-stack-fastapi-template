"""Base parser interface and common utilities."""

from abc import ABC, abstractmethod
from pathlib import Path

from ..interfaces import FileSystem
from ..models import FileModel


class BaseParser(ABC):
    """Base class for all parsers."""

    def __init__(self, file_system: FileSystem):
        self.file_system = file_system

    @abstractmethod
    def get_supported_extensions(self) -> set[str]:
        """Return set of supported file extensions."""
        pass

    @abstractmethod
    def parse_file(self, file_path: Path) -> FileModel:
        """Parse a file and return a FileModel."""
        pass
