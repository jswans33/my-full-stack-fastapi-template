"""UML Generator Package.

A tool for automatically generating UML class diagrams from Python source code.
This package provides functionality to analyze Python files and generate
PlantUML diagrams representing the class structure, relationships, and module
organization of your codebase.

Key Components:
- CLI: Command-line interface for running the generator
- Parser: Python AST parser for code analysis
- Generator: PlantUML diagram generation
- Models: Data models representing code structure
- Service: Core orchestration logic

Example Usage:
    ```bash
    python -m uml_generator -d path/to/code --recursive
    ```

For more information, see the README.md file.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

from .cli import main
from .models import (
    AttributeModel,
    ClassModel,
    FileModel,
    FunctionModel,
    ImportModel,
    MethodModel,
    ParameterModel,
    RelationshipModel,
    Visibility,
)
from .path_resolver import UmlPathResolver
from .service import UmlGeneratorService

__all__ = [
    "main",
    "UmlGeneratorService",
    "UmlPathResolver",
    "AttributeModel",
    "ClassModel",
    "FileModel",
    "FunctionModel",
    "ImportModel",
    "MethodModel",
    "ParameterModel",
    "RelationshipModel",
    "Visibility",
]
