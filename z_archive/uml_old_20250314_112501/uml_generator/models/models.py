"""Domain models for UML generation."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Visibility(Enum):
    """Visibility levels for attributes and methods."""

    PUBLIC = "+"
    PRIVATE = "-"
    PROTECTED = "#"


@dataclass
class Parameter:
    """Function/method parameter representation."""

    name: str
    type_annotation: str
    default_value: str | None = None


@dataclass
class AttributeModel:
    """Class attribute representation."""

    name: str
    type_annotation: str
    visibility: Visibility = Visibility.PUBLIC


@dataclass
class MethodModel:
    """Method representation with signature information."""

    name: str
    parameters: list[Parameter]
    return_type: str
    visibility: Visibility = Visibility.PUBLIC

    @property
    def signature(self) -> str:
        """Generate method signature string."""
        params = [
            f"{param.name}: {param.type_annotation}"
            + (f" = {param.default_value}" if param.default_value else "")
            for param in self.parameters
        ]
        return f"{self.name}({', '.join(params)}) -> {self.return_type}"


@dataclass
class RelationshipModel:
    """Relationship between classes."""

    source: str
    target: str
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

    name: str
    filename: str
    bases: list[str] = field(default_factory=list)
    methods: list[MethodModel] = field(default_factory=list)
    attributes: list[AttributeModel] = field(default_factory=list)
    relationships: list[RelationshipModel] = field(default_factory=list)
    imports: list[ImportModel] = field(default_factory=list)


@dataclass
class FunctionModel:
    """Standalone function representation."""

    name: str
    parameters: list[Parameter]
    return_type: str
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
