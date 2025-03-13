"""Integration tests for UML generator."""

import textwrap
from pathlib import Path

import pytest

from ..config import Configuration, create_config_from_args
from ..factories import DefaultGeneratorFactory, DefaultParserFactory
from ..interfaces import FileSystem
from ..service import UmlGeneratorService


class MockFileSystem(FileSystem):
    """Mock file system for testing."""

    def __init__(self, files: dict[str, str]):
        self.files = files
        self.written_files = {}

    def read_file(self, path: Path) -> str:
        return self.files.get(str(path), "")

    def write_file(self, path: Path, content: str) -> None:
        self.written_files[str(path)] = content

    def ensure_directory(self, path: Path) -> None:
        pass


@pytest.fixture
def mock_fs():
    """Create mock filesystem with test files."""
    files = {
        "test.py": textwrap.dedent("""
            from typing import List, Optional
            
            class User:
                name: str
                email: str
                
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
        """),
        "models/base.py": textwrap.dedent("""
            class BaseModel:
                id: int
                created_at: str
                
                def save(self) -> None:
                    pass
        """),
        "models/user.py": textwrap.dedent("""
            from .base import BaseModel
            
            class User(BaseModel):
                name: str
                email: str
                _password: str
        """),
    }
    return MockFileSystem(files)


@pytest.fixture
def service(mock_fs):
    """Create UML generator service with mock filesystem."""
    config = Configuration(
        input_path=Path("test.py"),
        output_dir=Path("output"),
        format="plantuml",
        recursive=False,
        list_only=False,
        show_imports=True,
        generate_report=True,
        verbose=True,
    )

    parser_factory = DefaultParserFactory(mock_fs)
    generator_factory = DefaultGeneratorFactory(mock_fs)

    return UmlGeneratorService(
        config=config,
        file_system=mock_fs,
        parser_factory=parser_factory,
        generator_factory=generator_factory,
    )


def test_process_single_file(service):
    """Test processing a single Python file."""
    service.config.input_path = Path("test.py")
    service.run()

    # Check output files
    assert "output/test.puml" in service.file_system.written_files
    content = service.file_system.written_files["output/test.puml"]

    # Verify diagram content
    assert "class User" in content
    assert "class Post" in content
    assert "class Comment" in content
    assert "Post *--> Comment" in content
    assert "Post --> User" in content
    assert "Comment --> User" in content


def test_process_directory(service):
    """Test processing a directory of Python files."""
    service.config.input_path = Path("models")
    service.run()

    # Check output files
    assert "output/base.puml" in service.file_system.written_files
    assert "output/user.puml" in service.file_system.written_files

    # Verify base model diagram
    base_content = service.file_system.written_files["output/base.puml"]
    assert "class BaseModel" in base_content
    assert "+ id: int" in base_content
    assert "+ save()" in base_content

    # Verify user model diagram
    user_content = service.file_system.written_files["output/user.puml"]
    assert "class User" in user_content
    assert "BaseModel <|-- User" in user_content
    assert "+ name: str" in user_content
    assert "- _password: str" in user_content


def test_recursive_processing(service):
    """Test recursive directory processing."""
    service.config.input_path = Path(".")
    service.config.recursive = True
    service.run()

    # Check that all files were processed
    assert "output/test.puml" in service.file_system.written_files
    assert "output/base.puml" in service.file_system.written_files
    assert "output/user.puml" in service.file_system.written_files


def test_list_only_mode(service):
    """Test list-only mode (no diagram generation)."""
    service.config.list_only = True
    service.run()

    # Verify no diagrams were generated
    assert not service.file_system.written_files


def test_show_imports(service):
    """Test import relationship generation."""
    service.config.show_imports = True
    service.run()

    content = service.file_system.written_files["output/test.puml"]
    assert "note right of" in content
    assert "imports List from typing" in content
    assert "imports Optional from typing" in content


def test_error_handling(service):
    """Test error handling for invalid files."""
    service.file_system.files["invalid.py"] = "invalid python code {"
    service.config.input_path = Path("invalid.py")

    with pytest.raises(Exception):
        service.run()


def test_config_from_args():
    """Test configuration creation from command line args."""
    args = type(
        "Args",
        (),
        {
            "file": "test.py",
            "directory": None,
            "app_dir": False,
            "output": "output",
            "format": "plantuml",
            "recursive": True,
            "list_only": False,
            "show_imports": True,
            "generate_report": True,
            "verbose": True,
            "quiet": False,
            "debug": False,
        },
    )()

    config = create_config_from_args(args)
    assert config.input_path == Path("test.py")
    assert config.output_dir == Path("output")
    assert config.format == "plantuml"
    assert config.recursive is True
    assert config.show_imports is True
