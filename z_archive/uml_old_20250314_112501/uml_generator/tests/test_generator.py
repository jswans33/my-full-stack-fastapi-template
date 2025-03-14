"""Tests for PlantUML diagram generator."""

from pathlib import Path

import pytest

from ..generator.plantuml_generator import PlantUmlGenerator
from ..interfaces import FileSystem
from ..models import (
    AttributeModel,
    ClassModel,
    FileModel,
    MethodModel,
    Parameter,
    RelationshipModel,
    Visibility,
)


class MockFileSystem(FileSystem):
    """Mock file system for testing."""

    def __init__(self):
        self.files = {}

    def read_file(self, path: Path) -> str:
        return self.files.get(str(path), "")

    def write_file(self, path: Path, content: str) -> None:
        self.files[str(path)] = content

    def ensure_directory(self, path: Path) -> None:
        pass

    def find_files(self, directory: Path, pattern: str) -> list[Path]:
        """Mock finding files matching pattern."""
        files = []
        for path in self.files.keys():
            if path.startswith(str(directory)) and path.endswith(
                pattern.replace("*", ""),
            ):
                files.append(Path(path))
        return files


@pytest.fixture
def generator():
    """Create generator instance with mock filesystem."""
    return PlantUmlGenerator(MockFileSystem())


def test_generate_simple_class(generator):
    """Test generating diagram for a simple class."""
    model = FileModel(
        path=Path("test.py"),
        classes=[
            ClassModel(
                name="SimpleClass",
                filename="test",
                attributes=[
                    AttributeModel(
                        name="x",
                        type_annotation="int",
                        visibility=Visibility.PUBLIC,
                    ),
                ],
                methods=[
                    MethodModel(
                        name="method",
                        parameters=[
                            Parameter(name="self", type_annotation="SimpleClass"),
                            Parameter(name="arg", type_annotation="str"),
                        ],
                        return_type="None",
                        visibility=Visibility.PUBLIC,
                    ),
                ],
            ),
        ],
    )

    output_path = Path("test.puml")
    generator.generate_diagram(model, output_path)

    content = generator.file_system.files[str(output_path)]
    assert "@startuml" in content
    assert "class SimpleClass" in content
    assert "+x: int" in content  # No space after + in the actual output
    assert "+method(self: SimpleClass, arg: str) -> None" in content
    assert "@enduml" in content


def test_generate_inheritance(generator):
    """Test generating diagram with inheritance."""
    model = FileModel(
        path=Path("test.py"),
        classes=[
            ClassModel(name="Base", filename="test"),
            ClassModel(
                name="Child",
                filename="test",
                bases=["Base"],
            ),
        ],
    )

    output_path = Path("test.puml")
    generator.generate_diagram(model, output_path)

    content = generator.file_system.files[str(output_path)]
    assert "Base <|-- " in content


def test_generate_relationships(generator):
    """Test generating diagram with relationships."""
    model = FileModel(
        path=Path("test.py"),
        classes=[
            ClassModel(
                name="User",
                filename="test",
                relationships=[
                    RelationshipModel(
                        source="User",
                        target="Post",
                        type="*-->",
                    ),
                ],
            ),
        ],
    )

    output_path = Path("test.puml")
    generator.generate_diagram(model, output_path)

    content = generator.file_system.files[str(output_path)]
    assert "User *--> Post" in content


def test_generate_visibility(generator):
    """Test generating diagram with different visibility modifiers."""
    model = FileModel(
        path=Path("test.py"),
        classes=[
            ClassModel(
                name="TestClass",
                filename="test",
                attributes=[
                    AttributeModel(
                        name="public_attr",
                        type_annotation="int",
                        visibility=Visibility.PUBLIC,
                    ),
                    AttributeModel(
                        name="private_attr",
                        type_annotation="str",
                        visibility=Visibility.PRIVATE,
                    ),
                    AttributeModel(
                        name="protected_attr",
                        type_annotation="bool",
                        visibility=Visibility.PROTECTED,
                    ),
                ],
                methods=[
                    MethodModel(
                        name="public_method",
                        parameters=[
                            Parameter(name="self", type_annotation="TestClass"),
                        ],
                        return_type="None",
                        visibility=Visibility.PUBLIC,
                    ),
                    MethodModel(
                        name="private_method",
                        parameters=[
                            Parameter(name="self", type_annotation="TestClass"),
                        ],
                        return_type="None",
                        visibility=Visibility.PRIVATE,
                    ),
                ],
            ),
        ],
    )

    output_path = Path("test.puml")
    generator.generate_diagram(model, output_path)

    content = generator.file_system.files[str(output_path)]
    assert "+public_attr: int" in content
    assert "-private_attr: str" in content
    assert "#protected_attr: bool" in content
    assert "+public_method" in content
    assert "-private_method" in content


def test_generate_index(generator):
    """Test generating index file."""
    diagrams = [
        Path("test1.puml"),
        Path("test2.puml"),
        Path("test3.puml"),
    ]
    output_dir = Path("output")

    generator.generate_index(output_dir, diagrams)

    content = generator.file_system.files[str(output_dir / "index.rst")]
    assert "UML Class Diagrams" in content
    assert ".. toctree::" in content
    for diagram in diagrams:
        assert f".. uml:: {diagram.name}" in content


def test_plantuml_settings(generator):
    """Test custom PlantUML settings."""
    custom_settings = {
        "PLANTUML_START": "@startuml custom",
        "PLANTUML_END": "@enduml custom",
        "PLANTUML_SETTINGS": [
            "skinparam classAttributeIconSize 0",
            "skinparam monochrome true",
        ],
    }

    generator = PlantUmlGenerator(MockFileSystem(), custom_settings)
    model = FileModel(
        path=Path("test.py"),
        classes=[ClassModel(name="Test", filename="test")],
    )

    output_path = Path("test.puml")
    generator.generate_diagram(model, output_path)

    content = generator.file_system.files[str(output_path)]
    assert "@startuml custom" in content
    assert "skinparam monochrome true" in content
    assert "@enduml custom" in content
