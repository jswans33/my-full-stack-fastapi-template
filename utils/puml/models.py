"""
Data models for code analysis.

This module defines the core data structures used to represent Python code elements
during analysis.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Function:
    """Represents a Python function or method."""

    name: str
    full_name: str
    args: list[str]
    docstring: str | None = None
    lineno: int = 0
    calls: set[str] = field(default_factory=set)
    is_method: bool = False
    return_type: str | None = None

    def add_call(self, target: str) -> None:
        """Add a function/method call relationship."""
        self.calls.add(target)


@dataclass
class Class:
    """Represents a Python class."""

    name: str
    full_name: str
    bases: list[str]
    docstring: str | None = None
    lineno: int = 0
    methods: dict[str, Function] = field(default_factory=dict)
    attributes: dict[str, dict[str, Any]] = field(default_factory=dict)
    relationships: set[tuple[str, str, str]] = field(default_factory=set)

    def add_method(self, method: Function) -> None:
        """Add a method to the class."""
        method.is_method = True
        self.methods[method.name] = method

    def add_attribute(
        self,
        name: str,
        type_annotation: str = "",
        lineno: int = 0,
    ) -> None:
        """Add an attribute to the class."""
        self.attributes[name] = {
            "name": name,
            "type": type_annotation,
            "lineno": lineno,
        }

    def add_relationship(self, target: str, relationship_type: str) -> None:
        """Add a relationship to another class."""
        self.relationships.add((self.full_name, target, relationship_type))


@dataclass
class Module:
    """Represents a Python module."""

    path: Path
    name: str
    classes: dict[str, Class] = field(default_factory=dict)
    functions: dict[str, Function] = field(default_factory=dict)
    imports: dict[str, dict[str, Any]] = field(default_factory=dict)
    relationships: set[tuple[str, str, str]] = field(default_factory=set)

    def add_class(self, class_obj: Class) -> None:
        """Add a class to the module."""
        self.classes[class_obj.full_name] = class_obj

    def add_function(self, function: Function) -> None:
        """Add a function to the module."""
        self.functions[function.full_name] = function

    def add_import(
        self,
        name: str,
        source: str,
        is_direct: bool = True,
        is_star: bool = False,
    ) -> None:
        """
        Add an import statement.

        Args:
            name: The name used in this module (after 'as' if present)
            source: The original module/object being imported
            is_direct: Whether this is a direct import or part of a package path
            is_star: Whether this is a star import (from x import *)
        """
        self.imports[name] = {
            "source": source,
            "is_direct": is_direct,
            "is_star": is_star,
            "used": False,  # Will be set to True when the import is used
        }

    def add_relationship(
        self,
        source: str,
        target: str,
        relationship_type: str,
    ) -> None:
        """Add a relationship between code elements."""
        self.relationships.add((source, target, relationship_type))

    def get_qualified_name(self, name: str) -> str:
        """Get the fully qualified name for a symbol."""
        if name in self.imports:
            return self.imports[name]["source"]
        return f"{self.name}.{name}"

    def get_direct_dependencies(self) -> set[str]:
        """Get set of directly imported module names."""
        return {
            info["source"].split(".")[0]
            for info in self.imports.values()
            if info["is_direct"]
        }

    def get_star_imports(self) -> set[str]:
        """Get set of modules imported with star imports."""
        return {info["source"] for info in self.imports.values() if info["is_star"]}

    def mark_import_used(self, name: str) -> None:
        """Mark an import as used in the code."""
        if name in self.imports:
            self.imports[name]["used"] = True

    def get_unused_imports(self) -> set[str]:
        """Get set of imported names that are never used."""
        return {
            name
            for name, info in self.imports.items()
            if info["is_direct"] and not info["used"] and not info["is_star"]
        }
