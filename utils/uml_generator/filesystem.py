from pathlib import Path

from .interfaces import FileSystem


class DefaultFileSystem(FileSystem):
    """Default implementation of FileSystem interface."""

    def read_file(self, path: Path) -> str:
        """Read file content as string."""
        with open(path, encoding="utf-8") as f:
            return f.read()

    def write_file(self, path: Path, content: str) -> None:
        """Write content to file."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def ensure_directory(self, path: Path) -> None:
        """Ensure directory exists, create if needed."""
        path.mkdir(parents=True, exist_ok=True)

    def find_files(self, directory: Path, pattern: str) -> list[Path]:
        """Find files matching pattern in directory."""
        if not isinstance(directory, Path):
            directory = Path(directory)
        # Use rglob for recursive search
        return list(directory.rglob(pattern))
