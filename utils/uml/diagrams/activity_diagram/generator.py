"""Generator for converting activity diagrams to PlantUML format.

This module provides functionality for generating PlantUML activity diagrams from
activity diagram models.
"""

from pathlib import Path
from typing import Any

from utils.uml.core.exceptions import GeneratorError
from utils.uml.core.filesystem import FileSystem
from utils.uml.core.interfaces import DiagramModel
from utils.uml.diagrams.activity_diagram.models import (
    ActivityDiagram,
)
from utils.uml.diagrams.base import BaseDiagramGenerator


class ActivityDiagramGenerator(BaseDiagramGenerator):
    """Generates PlantUML activity diagrams from activity diagram models."""

    def __init__(self, file_system: FileSystem, settings: dict[str, Any] | None = None):
        """Initialize an activity diagram generator.

        Args:
            file_system: The file system implementation to use
            settings: Optional settings for the generator
        """
        super().__init__(file_system, settings)

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
            **kwargs: Additional generator-specific arguments

        Raises:
            GeneratorError: If the diagram cannot be generated
        """
        try:
            # Ensure the model is an ActivityDiagram
            if not isinstance(model, ActivityDiagram):
                raise GeneratorError(
                    f"Expected ActivityDiagram, got {type(model).__name__}",
                )

            # Generate the PlantUML code
            plantuml_code = self.generate_plantuml(model, **kwargs)

            # Ensure output directory exists and write the file
            output_path = (
                Path(output_path) if isinstance(output_path, str) else output_path
            )
            self.file_system.ensure_directory(output_path.parent)
            self.file_system.write_file(output_path, plantuml_code)

        except Exception as e:
            raise GeneratorError(
                f"Failed to generate activity diagram: {e}",
                cause=e,
            )

    def generate_plantuml(
        self,
        diagram: ActivityDiagram,
        **kwargs,
    ) -> str:
        """Generate PlantUML code from an activity diagram model.

        Args:
            diagram: The activity diagram model
            **kwargs: Additional generator-specific arguments

        Returns:
            The generated PlantUML code
        """
        lines = ["@startuml", ""]

        # Add title
        if diagram.name:
            lines.append(f"title {diagram.name}")
            lines.append("")

        # Add global settings
        use_monochrome = self.settings.get("MONOCHROME", True)
        settings = [
            "skinparam ActivityBackgroundColor white",
            "skinparam ActivityBorderColor black",
            "skinparam ArrowColor black",
            "skinparam monochrome true" if use_monochrome else "",
        ]

        # Filter out empty settings
        settings = [s for s in settings if s]
        lines.extend(settings)
        lines.append("")

        # Add start nodes
        for start_node in diagram.start_nodes:
            lines.append("start")

        # Add activities
        for activity in diagram.activities:
            activity_name = activity.name or activity.id
            lines.append(f":{activity_name};")

        # Add decision nodes
        for decision in diagram.decision_nodes:
            decision_name = decision.name or decision.id
            lines.append(f"if ({decision_name}) then (yes)")
            lines.append("else (no)")
            lines.append("endif")

        # Add fork nodes
        for fork in diagram.fork_nodes:
            fork_name = fork.name or fork.id
            lines.append("fork")
            lines.append("fork again")
            lines.append("end fork")

        # Add end nodes
        for end_node in diagram.end_nodes:
            lines.append("stop")

        # Add transitions
        lines.append("")
        lines.append("' Transitions")

        # Process transitions
        for transition in diagram.transitions:
            source = transition.source_id
            target = transition.target_id
            label = f" : {transition.label}" if transition.label else ""

            # For decision nodes, we've already added the if/else structure
            # So we don't need to add explicit transitions
            if any(d.id == source for d in diagram.decision_nodes):
                continue

            lines.append(f"{source} --> {target}{label}")

        # End the diagram
        lines.append("")
        lines.append("@enduml")

        return "\n".join(lines)

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
        # Filter to only include activity diagrams
        activity_diagrams = [
            d
            for d in diagrams
            if d.name.endswith(".puml") and self._is_activity_diagram(d)
        ]

        if not activity_diagrams:
            return

        try:
            output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
            index_path = output_dir / "activity_index.rst"

            # Create basic RST index
            lines = [
                "Activity Diagrams",
                "=================",
                "",
                ".. toctree::",
                "   :maxdepth: 1",
                "",
            ]

            # Add diagram references
            for diagram in sorted(activity_diagrams):
                rel_path = diagram.relative_to(output_dir)
                # Use forward slashes for cross-platform compatibility
                lines.append(f"   {str(rel_path).replace('\\', '/')}")

            lines.append("")  # Add trailing newline

            # Write the index file
            self.file_system.write_file(index_path, "\n".join(lines))

        except Exception as e:
            raise GeneratorError(
                f"Failed to generate activity diagram index: {e}",
                cause=e,
            )

    def _is_activity_diagram(self, file_path: Path) -> bool:
        """Check if a file is an activity diagram.

        Args:
            file_path: The path to the file to check

        Returns:
            True if the file is an activity diagram, False otherwise
        """
        try:
            content = self.file_system.read_file(file_path)
            # Simple heuristic: look for activity diagram indicators
            indicators = [
                "start",
                "stop",
                "if (",
                "fork",
                "skinparam ActivityBackgroundColor",
            ]
            return any(indicator in content for indicator in indicators)
        except Exception:
            return False
