"""Generator for converting class diagrams to PlantUML format.

This module provides functionality for generating PlantUML class diagrams from
class diagram models.
"""

from pathlib import Path
from typing import Any

from utils.uml.core.exceptions import GeneratorError
from utils.uml.core.filesystem import FileSystem
from utils.uml.core.interfaces import DiagramModel
from utils.uml.diagrams.base import BaseDiagramGenerator
from utils.uml.diagrams.class_diagram.models import (
    AttributeModel,
    ClassDiagram,
    ClassModel,
    MethodModel,
    RelationshipModel,
)


class ClassDiagramGenerator(BaseDiagramGenerator):
    """Generates PlantUML class diagrams from class diagram models."""

    def __init__(self, file_system: FileSystem, settings: dict[str, Any] | None = None):
        """Initialize a class diagram generator.

        Args:
            file_system: The file system implementation to use
            settings: Optional settings for the generator
        """
        super().__init__(file_system, settings)
        self.indentation = "  "
        self.current_indent = 0

    def _indent(self) -> str:
        """Get the current indentation string."""
        return self.indentation * self.current_indent

    def _increase_indent(self) -> None:
        """Increase indentation level."""
        self.current_indent += 1

    def _decrease_indent(self) -> None:
        """Decrease indentation level."""
        self.current_indent = max(0, self.current_indent - 1)

    def _format_class(self, class_model: ClassModel, skinny: bool = False) -> list[str]:
        """Format a class model as PlantUML.

        Args:
            class_model: The class model to format
            skinny: Whether to use a skinny class representation

        Returns:
            List of PlantUML lines for the class
        """
        lines = []

        # Class declaration with stereotype if it has decorators
        class_line = "class"
        stereotype = None

        # Check for common decorators and assign stereotypes
        if class_model.decorators:
            for decorator in class_model.decorators:
                if decorator in ("dataclass", "dataclasses.dataclass"):
                    stereotype = "<<dataclass>>"
                elif decorator in ("abc.ABC", "ABC", "ABCMeta"):
                    stereotype = "<<abstract>>"
                elif decorator in ("Enum", "enum.Enum"):
                    stereotype = "<<enumeration>>"
                elif decorator in ("Protocol", "typing.Protocol"):
                    stereotype = "<<protocol>>"

        class_line = f"{class_line} {class_model.name}"
        if stereotype:
            class_line = f"{class_line} {stereotype}"

        lines.append(class_line + " {")
        self._increase_indent()

        # Add attributes
        if class_model.attributes and not skinny:
            for attr in class_model.attributes:
                lines.append(self._format_attribute(attr))

        # Add a separator if we have both attributes and methods
        if class_model.attributes and class_model.methods and not skinny:
            lines.append("--")

        # Add methods
        if class_model.methods and not skinny:
            for method in class_model.methods:
                lines.append(self._format_method(method))

        self._decrease_indent()
        lines.append("}")

        return lines

    def _format_attribute(self, attr: AttributeModel) -> str:
        """Format an attribute as PlantUML.

        Args:
            attr: The attribute to format

        Returns:
            PlantUML formatted attribute
        """
        # Format visibility prefix
        visibility = attr.visibility.value

        # Format default value
        default = f" = {attr.default_value}" if attr.default_value else ""

        # Format type annotation
        type_str = f": {attr.type_annotation}" if attr.type_annotation != "Any" else ""

        return f"{self._indent()}{visibility} {attr.name}{type_str}{default}"

    def _format_method(self, method: MethodModel) -> str:
        """Format a method as PlantUML.

        Args:
            method: The method to format

        Returns:
            PlantUML formatted method
        """
        # Format visibility prefix
        visibility = method.visibility.value

        # Format method modifiers
        modifiers = ""
        if method.is_static:
            modifiers += "{static} "
        elif method.is_classmethod:
            modifiers += "{classmethod} "

        # Format parameters
        params = []
        for param in method.parameters:
            param_str = param.name
            if param.type_annotation and param.type_annotation != "Any":
                param_str += f": {param.type_annotation}"
            if param.default_value:
                param_str += f" = {param.default_value}"
            params.append(param_str)

        param_str = ", ".join(params)
        return_type = (
            f": {method.return_type}"
            if method.return_type and method.return_type != "None"
            else ""
        )

        return f"{self._indent()}{visibility} {modifiers}{method.name}({param_str}){return_type}"

    def _format_relationship(self, rel: RelationshipModel) -> str:
        """Format a relationship as PlantUML.

        Args:
            rel: The relationship to format

        Returns:
            PlantUML formatted relationship
        """
        return f"{rel.source} {rel.type} {rel.target}"

    def generate_plantuml(
        self,
        diagram: ClassDiagram,
        skinny: bool = False,
    ) -> str:
        """Generate PlantUML code from a class diagram model.

        Args:
            diagram: The class diagram model
            skinny: Whether to use skinny class representations

        Returns:
            The generated PlantUML code
        """
        lines = ["@startuml", ""]

        # Add title
        if diagram.name:
            lines.append(f"title {diagram.name}")
            lines.append("")

        # Add global settings from the settings dict, or use defaults
        use_monochrome = self.settings.get("MONOCHROME", True)
        hide_fields = skinny or self.settings.get("HIDE_FIELDS", False)
        hide_methods = skinny or self.settings.get("HIDE_METHODS", False)
        hide_empty_members = self.settings.get("HIDE_EMPTY_MEMBERS", True)

        settings = [
            "skinparam ClassAttributeIconSize 0",
            "skinparam ClassBackgroundColor white",
            "skinparam ClassBorderColor black",
            "hide empty members" if hide_empty_members else "",
            "hide fields" if hide_fields else "",
            "hide methods" if hide_methods else "",
            "skinparam monochrome true" if use_monochrome else "",
        ]

        # Filter out empty settings
        settings = [s for s in settings if s]
        lines.extend(settings)
        lines.append("")

        # Add package organization if available
        # Group classes by their modules/packages
        packages: dict[str, list[ClassModel]] = {}

        for file_model in diagram.files:
            package_name = file_model.path.parent.name
            if package_name not in packages:
                packages[package_name] = []

            packages[package_name].extend(file_model.classes)

        # Output classes by package
        for package_name, classes in packages.items():
            if not classes:
                continue

            if package_name and package_name != ".":
                lines.append(f"package {package_name} {{")
                self._increase_indent()

            # Add classes in this package
            for class_model in classes:
                class_lines = self._format_class(class_model, skinny=skinny)
                lines.extend([f"{self._indent()}{line}" for line in class_lines])
                lines.append("")

            if package_name and package_name != ".":
                self._decrease_indent()
                lines.append("}")
                lines.append("")

        # Add non-packaged classes
        standalone_classes = []
        for file_model in diagram.files:
            if file_model.path.parent.name in packages:
                continue
            standalone_classes.extend(file_model.classes)

        for class_model in standalone_classes:
            class_lines = self._format_class(class_model, skinny=skinny)
            lines.extend(class_lines)
            lines.append("")

        # Add relationships
        lines.append("' Relationships")
        # First, add inheritance relationships
        for rel in diagram.global_relationships:
            if rel.type == "--|>":  # Inheritance relationships first
                lines.append(self._format_relationship(rel))

        # Then add other relationships
        for rel in diagram.global_relationships:
            if rel.type != "--|>":  # Other relationships
                lines.append(self._format_relationship(rel))

        # End the diagram
        lines.append("")
        lines.append("@enduml")

        return "\n".join(lines)

    def generate_diagram(
        self,
        model: DiagramModel,
        output_path: str | Path,
        **kwargs,
    ) -> None:
        """Generate a UML diagram from the given model and write it to the output path.

        Args:
            model: The diagram model to generate a diagram from
            output_path: The path to write the diagram to
            **kwargs: Additional generator-specific arguments:
                - skinny: Whether to use skinny class representations

        Raises:
            GeneratorError: If the diagram cannot be generated
        """
        try:
            # Ensure the model is a ClassDiagram
            if not isinstance(model, ClassDiagram):
                raise GeneratorError(
                    f"Expected ClassDiagram, got {type(model).__name__}",
                )

            # Generate the PlantUML code
            skinny = kwargs.get("skinny", False)
            plantuml_code = self.generate_plantuml(model, skinny=skinny)

            # Ensure output directory exists and write the file
            output_path = (
                Path(output_path) if isinstance(output_path, str) else output_path
            )
            self.file_system.ensure_directory(output_path.parent)
            self.file_system.write_file(output_path, plantuml_code)

        except Exception as e:
            raise GeneratorError(
                f"Failed to generate class diagram: {e}",
                cause=e,
            )

    def generate_index(
        self,
        output_dir: str | Path,
        diagrams: list[Path],
        **kwargs,
    ) -> None:
        """Generate an index file for all diagrams in the output directory.

        Args:
            output_dir: The directory containing the diagrams
            diagrams: A list of paths to all diagrams
            **kwargs: Additional generator-specific arguments

        Raises:
            GeneratorError: If the index file cannot be generated
        """
        # Filter to only include class diagrams
        class_diagrams = [
            d
            for d in diagrams
            if d.name.endswith(".puml") and self._is_class_diagram(d)
        ]

        if not class_diagrams:
            return

        try:
            output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
            index_path = output_dir / "class_index.rst"

            # Create basic RST index
            lines = [
                "Class Diagrams",
                "==============",
                "",
                ".. toctree::",
                "   :maxdepth: 1",
                "",
            ]

            # Add diagram references
            for diagram in sorted(class_diagrams):
                rel_path = diagram.relative_to(output_dir)
                # Use forward slashes for cross-platform compatibility
                lines.append(f"   {str(rel_path).replace('\\', '/')}")

            lines.append("")  # Add trailing newline

            # Write the index file
            self.file_system.write_file(index_path, "\n".join(lines))

        except Exception as e:
            raise GeneratorError(
                f"Failed to generate class diagram index: {e}",
                cause=e,
            )

    def _is_class_diagram(self, file_path: Path) -> bool:
        """Check if a file is a class diagram.

        Args:
            file_path: The path to the file to check

        Returns:
            True if the file is a class diagram, False otherwise
        """
        try:
            content = self.file_system.read_file(file_path)
            # Simple heuristic: look for class diagram indicators
            indicators = [
                "class ",
                "interface ",
                "enum ",
                "package ",
                "namespace ",
                "skinparam ClassAttributeIconSize",
            ]
            return any(indicator in content for indicator in indicators)
        except Exception:
            return False
