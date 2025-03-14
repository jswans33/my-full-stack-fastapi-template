"""File system operations for UML diagram generation.

This module provides a default implementation of the FileSystem interface
for performing file system operations.
"""

from pathlib import Path

from utils.uml.core.exceptions import FileSystemError


class FileSystem:
    """Interface for file system operations."""

    def read_file(self, path: str | Path) -> str:
        """Read file content as string.

        Args:
            path: Path to the file to read

        Returns:
            The content of the file as a string

        Raises:
            FileSystemError: If the file cannot be read
        """
        ...

    def write_file(self, path: str | Path, content: str) -> None:
        """Write content to file.

        Args:
            path: Path to the file to write
            content: Content to write to the file

        Raises:
            FileSystemError: If the file cannot be written
        """
        ...

    def ensure_directory(self, path: str | Path) -> None:
        """Ensure directory exists, create if needed.

        Args:
            path: Path to the directory to ensure exists

        Raises:
            FileSystemError: If the directory cannot be created
        """
        ...

    def find_files(self, directory: str | Path, pattern: str) -> list[Path]:
        """Find files matching pattern in directory.

        Args:
            directory: Directory to search in
            pattern: Glob pattern to match files against

        Returns:
            A list of paths to files matching the pattern

        Raises:
            FileSystemError: If the directory cannot be accessed
        """
        ...


class DefaultFileSystem(FileSystem):
    """Default implementation of FileSystem interface."""

    def read_file(self, path: str | Path) -> str:
        """Read file content as string."""
        try:
            path = Path(path) if isinstance(path, str) else path
            with open(path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise FileSystemError(f"Failed to read file {path}: {e}", cause=e)

    def write_file(self, path: str | Path, content: str) -> None:
        """Write content to file."""
        try:
            path = Path(path) if isinstance(path, str) else path
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            raise FileSystemError(f"Failed to write file {path}: {e}", cause=e)

    def ensure_directory(self, path: str | Path) -> None:
        """Ensure directory exists, create if needed."""
        try:
            path = Path(path) if isinstance(path, str) else path
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise FileSystemError(f"Failed to create directory {path}: {e}", cause=e)

    def find_files(self, directory: str | Path, pattern: str) -> list[Path]:
        """Find files matching pattern in directory."""
        try:
            directory = Path(directory) if isinstance(directory, str) else directory
            # Use rglob for recursive search
            return list(directory.rglob(pattern))
        except Exception as e:
            raise FileSystemError(
                f"Failed to find files in {directory} with pattern {pattern}: {e}",
                cause=e,
            )
