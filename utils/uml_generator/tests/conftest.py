from pathlib import Path

import pytest

from ..interfaces import FileSystem


class MockFileSystem(FileSystem):
    """Mock file system for testing."""

    def __init__(self, files: dict[str, str] | None = None):
        self.files = files or {}
        self.written_files = {}
        self.file_patterns: dict[str, list[str]] = {}

    def find_files(self, directory: Path, pattern: str) -> list[Path]:
        """Mock finding files matching pattern."""
        key = str(directory)
        if key not in self.file_patterns:
            # Return files in the mocked directory
            return [
                Path(f)
                for f in self.files.keys()
                if f.startswith(key) and f.endswith(pattern.replace("*", ""))
            ]
        return [Path(f) for f in self.file_patterns[key]]

    def read_file(self, path: Path) -> str:
        return self.files.get(str(path), "")

    def write_file(self, path: Path, content: str) -> None:
        self.written_files[str(path)] = content

    def ensure_directory(self, path: Path) -> None:
        pass


@pytest.fixture
def mock_fs():
    """Create empty mock filesystem."""
    return MockFileSystem()


@pytest.fixture
def sample_code():
    """Return sample Python code for testing."""
    return """
    from typing import List, Optional

    class BaseModel:
        id: int
        created_at: str

        def save(self) -> None:
            pass

    class User(BaseModel):
        name: str
        email: str
        _password: str

        def __init__(self, name: str, email: str):
            self.name = name
            self.email = email

    class Post:
        title: str
        content: str
        author: User
        comments: List['Comment']

        def __init__(self, title: str, content: str, author: User):
            self.title = title
            self.content = content
            self.author = author

    class Comment:
        text: str
        author: User
        post: Post
    """
