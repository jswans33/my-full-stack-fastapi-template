"""Sphinx configuration."""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

# Type aliases for better readability
ClassName = str
MethodName = str
AttributeName = str
TypeAnnotation = str


class Visibility(str, Enum):
    """Visibility levels for class members."""

    PUBLIC = "+"
    PRIVATE = "-"
    PROTECTED = "#"


@dataclass
class ParameterModel:
    """Function/method parameter representation."""

    name: str
    type_annotation: TypeAnnotation
    default_value: str | None = None


@dataclass
class AttributeModel:
    """Class attribute representation."""

    name: AttributeName
    type_annotation: TypeAnnotation
    visibility: Visibility = Visibility.PUBLIC
    default_value: str | None = None
    docstring: str | None = None
    decorators: list[str] = field(default_factory=list)


@dataclass
class MethodModel:
    """Method representation with signature information."""

    name: MethodName
    parameters: list[ParameterModel]
    return_type: TypeAnnotation
    visibility: Visibility = Visibility.PUBLIC
    is_static: bool = False
    is_classmethod: bool = False
    docstring: str | None = None
    decorators: list[str] = field(default_factory=list)
    default_value: str | None = None

    @property
    def signature(self) -> str:
        """Generate method signature string."""
        params = [
            f"{param.name}: {param.type_annotation}"
            + (f" = {param.default_value}" if param.default_value else "")
            for param in self.parameters
        ]
        prefix = ""
        if self.is_static:
            prefix = "@staticmethod "
        elif self.is_classmethod:
            prefix = "@classmethod "
        return f"{prefix}{self.name}({', '.join(params)}) -> {self.return_type}"


@dataclass
class RelationshipModel:
    """Relationship between classes."""

    source: ClassName
    target: ClassName
    type: str  # -->: association, *-->: composition, etc.


@dataclass
class ImportModel:
    """Import statement representation."""

    module: str
    name: str
    alias: str | None = None


@dataclass
class ClassModel:
    """Class representation with methods, attributes and relationships."""

    name: ClassName
    filename: str
    bases: list[ClassName] = field(default_factory=list)
    methods: list[MethodModel] = field(default_factory=list)
    attributes: list[AttributeModel] = field(default_factory=list)
    relationships: list[RelationshipModel] = field(default_factory=list)
    imports: list[ImportModel] = field(default_factory=list)
    docstring: str | None = None
    decorators: list[str] = field(default_factory=list)


@dataclass
class FunctionModel:
    """Standalone function representation."""

    name: str
    parameters: list[ParameterModel]
    return_type: TypeAnnotation
    visibility: Visibility = Visibility.PUBLIC

    @property
    def signature(self) -> str:
        """Generate function signature string."""
        params = [
            f"{param.name}: {param.type_annotation}"
            + (f" = {param.default_value}" if param.default_value else "")
            for param in self.parameters
        ]
        return f"{self.name}({', '.join(params)}) -> {self.return_type}"


@dataclass
class FileModel:
    """File representation containing classes and functions."""

    path: Path
    classes: list[ClassModel] = field(default_factory=list)
    functions: list[FunctionModel] = field(default_factory=list)
    imports: list[ImportModel] = field(default_factory=list)

    @property
    def filename(self) -> str:
        """Get filename without extension."""
        return self.path.stem


# Basic Sphinx configuration
project = "FastAPI Full Stack Template"
copyright = "2025, FastAPI Team"
author = "FastAPI Team"
version = "1.0"
release = "1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "myst_parser",
    "sphinxcontrib.mermaid",
    "sphinxcontrib.plantuml",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# PlantUML configuration
plantuml = r"java -jar C:\ProgramData\chocolatey\lib\plantuml\tools\plantuml.jar"
plantuml_output_format = "svg"
plantuml_latex_output_format = "pdf"


# UML Generation Code
class FileSystem(Protocol):
    """Protocol for file system operations."""

    def ensure_directory(self, path: Path) -> None:
        """Ensure directory exists."""
        ...

    def write_file(self, path: Path, content: str) -> None:
        """Write content to file."""
        ...


class UmlPathResolver:
    """Handles path resolution for UML files."""

    def __init__(self, source_dir: Path, generated_dir: Path):
        """Initialize the path resolver.

        Args:
            source_dir: The source directory (docs/source)
            generated_dir: The generated UML directory (docs/source/_generated_uml)
        """
        self.source_dir = source_dir.resolve()
        self.generated_dir = generated_dir.resolve()
        print("\nPath resolver initialized:")
        print(f"Source dir: {self.source_dir}")
        print(f"Generated dir: {self.generated_dir}")

    def get_plantuml_generator_path(self, file_path: Path) -> str:
        """Get path for use in plantuml_generator.py.

        Args:
            file_path: The absolute path to a .puml file

        Returns:
            Path for use in index.rst, using forward slashes.
            Path is relative to _generated_uml since that's configured as the plantuml search path.
        """
        abs_file_path = file_path.resolve()
        rel_path = abs_file_path.relative_to(self.generated_dir)
        rel_path_str = str(rel_path).replace(os.sep, "/")

        print(f"\nPath resolution for: {file_path}")
        print(f"Absolute path: {abs_file_path}")
        print(f"Relative path: {rel_path_str}")

        # Return path relative to _generated_uml directory since:
        # 1. Files are already in that directory
        # 2. Sphinx search path points to that directory
        # 3. Paths in index.rst should be relative to search path
        # 4. This matches how Sphinx will look for the files
        return "_generated_uml/" + rel_path_str

    def get_sphinx_path(self, file_path: Path) -> str:
        """Get path for use in Sphinx .rst files.

        Args:
            file_path: The absolute path to a .puml file

        Returns:
            Path for use in Sphinx .rst files, using forward slashes
        """
        abs_file_path = file_path.resolve()
        rel_path = abs_file_path.relative_to(self.source_dir)
        rel_path_str = str(rel_path).replace(os.sep, "/")

        print(f"\nPath resolution for: {file_path}")
        print(f"Absolute path: {abs_file_path}")
        print(f"Relative path: {rel_path_str}")

        return rel_path_str

    def get_search_paths(self) -> list[str]:
        """Get search paths for Sphinx configuration.

        Returns:
            List of paths where Sphinx should look for .puml files
        """
        return [str(self.generated_dir)]


class PlantUmlGenerator:
    """Generator for PlantUML diagrams."""

    def __init__(
        self,
        file_system: FileSystem,
        settings: dict[str, Any] | None = None,
    ):
        self.file_system = file_system
        self.settings = settings or {}
        self.logger = logging.getLogger(__name__)

        # Configure PlantUML settings
        self.plantuml_start = self.settings.get("PLANTUML_START", "@startuml")
        self.plantuml_end = self.settings.get("PLANTUML_END", "@enduml")
        self.plantuml_settings = self.settings.get(
            "PLANTUML_SETTINGS",
            [
                "skinparam classAttributeIconSize 0",
            ],
        )
        self.show_imports = self.settings.get("show_imports", False)

    def get_output_extension(self) -> str:
        """Return output file extension for this generator."""
        return ".puml"

    def generate_diagram(self, file_model: FileModel, output_path: Path) -> None:
        """Generate a PlantUML diagram from a FileModel."""
        self.logger.info(f"Generating UML diagram for {file_model.filename}")

        uml_content = self._generate_plantuml(file_model)

        # Ensure output directory exists
        self.file_system.ensure_directory(output_path.parent)

        # Append PlantUML content to file
        if output_path.exists():
            current_content = output_path.read_text()
            uml_content = current_content + "\n\n" + uml_content
        self.file_system.write_file(output_path, uml_content)

        self.logger.info(
            f"Generated UML diagram at {output_path}",
            extra={
                "class_count": len(file_model.classes),
                "function_count": len(file_model.functions),
            },
        )

    def _generate_plantuml(self, file_model: FileModel) -> str:
        """Generate PlantUML code from a FileModel."""
        uml_lines = [self.plantuml_start, *self.plantuml_settings]

        # Create a package for the file
        uml_lines.append(f'\npackage "{file_model.filename}" {{')

        # Add functions to the package if any
        if file_model.functions:
            uml_lines.append("  class Functions <<(F,orange)>> {")
            for function in file_model.functions:
                visibility = function.visibility.value
                signature = function.signature
                uml_lines.append(f"    {visibility}{signature}")
            uml_lines.append("  }")

        # Add classes to the package
        for class_model in file_model.classes:
            uml_lines.append(f"  class {class_model.name} {{")

            # Handle attributes
            for attr in class_model.attributes:
                uml_lines.append(
                    f"    {attr.visibility.value}{attr.name}: {attr.type_annotation}",
                )

            # Handle methods
            for method in class_model.methods:
                uml_lines.append(f"    {method.visibility.value}{method.signature}")

            uml_lines.append("  }")

        # Close the package
        uml_lines.append("}")

        # Add imports section if show_imports is True
        if self.show_imports:
            uml_lines.append("\n' Imports")
            for class_model in file_model.classes:
                qualified_name = f'"{file_model.filename}".{class_model.name}'

                # Add import relationships
                for imp in file_model.imports:
                    # Skip built-ins and standard library modules
                    if not imp.module.startswith(
                        ("typing", "collections", "datetime", "builtins"),
                    ):
                        # Classes (start with uppercase)
                        if imp.name[0].isupper():
                            uml_lines.append(
                                f"note right of {qualified_name}: imports class {imp.name} from {imp.module}",
                            )
                        # Functions and types (don't start with underscore)
                        elif not imp.name.startswith("_"):
                            uml_lines.append(
                                f"note right of {qualified_name}: imports function/type {imp.name} from {imp.module}",
                            )

        # Add relationships
        uml_lines.append("\n' Relationships")
        for class_model in file_model.classes:
            qualified_name = f'"{file_model.filename}".{class_model.name}'

            # Add inheritance lines
            uml_lines.extend(
                f"{base} <|-- {qualified_name}" for base in class_model.bases
            )

            # Add other relationships
            for rel in class_model.relationships:
                uml_lines.append(f"{rel.source} {rel.type} {rel.target}")

        uml_lines.append(self.plantuml_end)
        return "\n".join(uml_lines)

    def generate_index(self, output_dir: Path, diagrams: list[Path]) -> None:
        """Generate an index.rst file for the generated UML diagrams."""
        output_path = output_dir / "index.rst"

        # Generate content with proper RST syntax
        content = [
            "UML Diagrams",
            "============",  # Make underline match title length
            "",
            "This documentation provides UML class diagrams for the project's components.",
            "",
            ".. contents:: Table of Contents",
            "   :depth: 2",
            "",
            "",  # Extra blank line before first section
            "Project Components",
            "-----------------",
            "",
            ".. uml:: all.puml",  # Reference the single file containing all diagrams
            "",
        ]

        self.file_system.write_file(output_path, "\n".join(content))
        self.logger.info(f"Generated UML index at {output_path}")


# Get absolute paths and initialize path resolver
docs_dir = Path(__file__).parent
generated_dir = docs_dir / "_generated_uml"
path_resolver = UmlPathResolver(docs_dir, generated_dir)

# Configure PlantUML search paths based on path resolver
plantuml_search_path = path_resolver.get_search_paths()
print(f"Using path resolver search paths: {plantuml_search_path}")
