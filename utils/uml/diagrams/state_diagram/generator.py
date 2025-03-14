"""Generator for converting state diagrams to PlantUML format.

This module provides functionality for generating PlantUML state diagrams from
state diagram models.
"""

from pathlib import Path
from typing import Any

from utils.uml.core.exceptions import GeneratorError
from utils.uml.core.filesystem import FileSystem
from utils.uml.core.interfaces import DiagramModel
from utils.uml.diagrams.base import BaseDiagramGenerator
from utils.uml.diagrams.state_diagram.models import (
    StateDiagram,
)


class StateDiagramGenerator(BaseDiagramGenerator):
    """Generates PlantUML state diagrams from state diagram models."""

    def __init__(self, file_system: FileSystem, settings: dict[str, Any] | None = None):
        """Initialize a state diagram generator.

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
            # Ensure the model is a StateDiagram
            if not isinstance(model, StateDiagram):
                raise GeneratorError(
                    f"Expected StateDiagram, got {type(model).__name__}",
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
                f"Failed to generate state diagram: {e}",
                cause=e,
            )

    def generate_plantuml(
        self,
        diagram: StateDiagram,
        **kwargs,
    ) -> str:
        """Generate PlantUML code from a state diagram model.

        Args:
            diagram: The state diagram model
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
            "skinparam StateBackgroundColor white",
            "skinparam StateBorderColor black",
            "skinparam ArrowColor black",
            "skinparam monochrome true" if use_monochrome else "",
        ]

        # Filter out empty settings
        settings = [s for s in settings if s]
        lines.extend(settings)
        lines.append("")

        # Add start states
        for start_state in diagram.start_states:
            lines.append(f"[*] --> {start_state.id}")

        # Add states
        for state in diagram.states:
            # State with actions
            if state.entry_actions or state.exit_actions or state.internal_actions:
                lines.append(f"state {state.name} {{")

                # Entry actions
                for action in state.entry_actions:
                    lines.append(f"  entry / {action}")

                # Exit actions
                for action in state.exit_actions:
                    lines.append(f"  exit / {action}")

                # Internal actions
                for action in state.internal_actions:
                    lines.append(f"  {action}")

                lines.append("}")
            else:
                # Simple state
                lines.append(f"state {state.name}")

        # Add composite states
        for composite in diagram.composite_states:
            lines.append(f"state {composite.name} {{")

            # Add substates
            for substate in composite.substates:
                lines.append(f"  state {substate.name}")

            # Add internal transitions
            for transition in composite.internal_transitions:
                source = transition.source_id
                target = transition.target_id
                event = f" : {transition.event}" if transition.event else ""
                guard = f" [{transition.guard}]" if transition.guard else ""
                action = f" / {transition.action}" if transition.action else ""

                lines.append(f"  {source} --> {target}{event}{guard}{action}")

            lines.append("}")

        # Add end states
        for end_state in diagram.end_states:
            lines.append(f"{end_state.id} --> [*]")

        # Add transitions
        lines.append("")
        lines.append("' Transitions")

        # Process transitions
        for transition in diagram.transitions:
            source = transition.source_id
            target = transition.target_id
            event = f" : {transition.event}" if transition.event else ""
            guard = f" [{transition.guard}]" if transition.guard else ""
            action = f" / {transition.action}" if transition.action else ""

            # Skip transitions from start states and to end states (already handled)
            if source in [s.id for s in diagram.start_states] or target in [
                e.id for e in diagram.end_states
            ]:
                continue

            lines.append(f"{source} --> {target}{event}{guard}{action}")

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
        # Filter to only include state diagrams
        state_diagrams = [
            d
            for d in diagrams
            if d.name.endswith(".puml") and self._is_state_diagram(d)
        ]

        if not state_diagrams:
            return

        try:
            output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
            index_path = output_dir / "state_index.rst"

            # Create basic RST index
            lines = [
                "State Diagrams",
                "==============",
                "",
                ".. toctree::",
                "   :maxdepth: 1",
                "",
            ]

            # Add diagram references
            for diagram in sorted(state_diagrams):
                rel_path = diagram.relative_to(output_dir)
                # Use forward slashes for cross-platform compatibility
                lines.append(f"   {str(rel_path).replace('\\', '/')}")

            lines.append("")  # Add trailing newline

            # Write the index file
            self.file_system.write_file(index_path, "\n".join(lines))

        except Exception as e:
            raise GeneratorError(
                f"Failed to generate state diagram index: {e}",
                cause=e,
            )

    def _is_state_diagram(self, file_path: Path) -> bool:
        """Check if a file is a state diagram.

        Args:
            file_path: The path to the file to check

        Returns:
            True if the file is a state diagram, False otherwise
        """
        try:
            content = self.file_system.read_file(file_path)
            # Simple heuristic: look for state diagram indicators
            indicators = [
                "state ",
                "[*] -->",
                "--> [*]",
                "skinparam StateBackgroundColor",
            ]
            return any(indicator in content for indicator in indicators)
        except Exception:
            return False
