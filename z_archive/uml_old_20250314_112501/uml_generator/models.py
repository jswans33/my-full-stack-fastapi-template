"""Data models for UML generator.

This module defines the data models used by the UML generator to represent
Python code structures like classes, methods, attributes, and relationships.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

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
    """Method representation with signature information.

    Attributes:
        name: Method name
        parameters: List of method parameters
        return_type: Return type annotation
        visibility: Method visibility (+: public, -: private, #: protected)
        is_static: Whether this is a static method
        is_classmethod: Whether this is a class method
        docstring: Method docstring if present
        decorators: List of decorator names
        default_value: Default value if present
    """

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
