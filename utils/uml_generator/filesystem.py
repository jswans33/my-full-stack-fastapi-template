import os
from pathlib import Path
from typing import List

from .interfaces import FileSystem


class DefaultFileSystem(FileSystem):
    """Default implementation of FileSystem interface."""
    
    def read_file(self, path: Path) -> str:
        """Read file content as string."""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write_file(self, path: Path, content: str) -> None:
        """Write content to file."""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def ensure_directory(self, path: Path) -> None:
        """Ensure directory exists, create if needed."""
        path.mkdir(parents=True, exist_ok=True)
    
    def find_files(self, directory: Path, pattern: str) -> List[Path]:
        """Find files matching pattern in directory."""
        return list(directory.glob(pattern))
