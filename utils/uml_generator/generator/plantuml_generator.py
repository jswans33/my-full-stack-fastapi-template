"""Generator for PlantUML diagrams."""

import logging
from pathlib import Path
from typing import Any

from ..interfaces import DiagramGenerator, FileSystem
from ..models import FileModel


class PlantUmlGenerator(DiagramGenerator):
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

        # Write PlantUML content to file
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

        content = [
            "UML Class Diagrams",
            "==================",
            "",
            ".. toctree::",
            "   :maxdepth: 1",
            "",
        ]

        for diagram_path in sorted(diagrams):
            name = diagram_path.stem
            content.extend(
                [
                    f"{name}",
                    f"{'-' * len(name)}",
                    "",
                    f".. uml:: {diagram_path.name}",
                    "   :align: center",
                    "",
                ],
            )

        self.file_system.write_file(output_path, "\n".join(content))
        self.logger.info(f"Generated UML index at {output_path}")
