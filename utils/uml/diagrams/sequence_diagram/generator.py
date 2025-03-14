"""Generator for converting sequence diagrams to PlantUML format.

This module provides functionality for generating PlantUML sequence diagrams from
sequence diagram models.
"""

from pathlib import Path
from typing import Any

from utils.uml.core.exceptions import GeneratorError
from utils.uml.core.filesystem import FileSystem
from utils.uml.core.interfaces import DiagramModel
from utils.uml.diagrams.base import BaseDiagramGenerator
from utils.uml.diagrams.sequence_diagram.models import (
    ActivationBar,
    Message,
    MessageType,
    Participant,
    SequenceDiagram,
)


class SequenceDiagramGenerator(BaseDiagramGenerator):
    """Generates PlantUML sequence diagrams from sequence models."""

    def __init__(self, file_system: FileSystem, settings: dict[str, Any] | None = None):
        """Initialize a sequence diagram generator.

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

    def _format_participant(self, participant: Participant) -> str:
        """Format a participant as PlantUML.

        Args:
            participant: The participant to format

        Returns:
            The formatted participant string
        """
        participant_type = participant.type.value

        if participant.alias:
            return f'{participant_type} "{participant.name}" as {participant.alias}'

        # Handle special characters in class names by optionally using quotes
        if any(c in participant.name for c in " .-,;:/\\()[]{}<>!@#$%^&*+=|`~"):
            return f'{participant_type} "{participant.name}"'
        return f"{participant_type} {participant.name}"

    def _format_message(self, message: Message) -> str:
        """Format a message as PlantUML.

        Args:
            message: The message to format

        Returns:
            The formatted message string
        """
        arrow = message.message_type.value

        # Format the message text
        if message.method_name:
            text = f"{message.method_name}()"
        else:
            text = message.text

        # Self messages are handled differently
        if message.is_self_message:
            return (
                f"{message.from_participant} {arrow} {message.from_participant}: {text}"
            )
        return f"{message.from_participant} {arrow} {message.to_participant}: {text}"

    def _format_activation(self, activation: ActivationBar) -> str:
        """Format an activation/deactivation as PlantUML.

        Args:
            activation: The activation bar to format

        Returns:
            The formatted activation string
        """
        if activation.is_start:
            return f"activate {activation.participant}"
        return f"deactivate {activation.participant}"

    def generate_plantuml(self, diagram: SequenceDiagram) -> str:
        """Generate PlantUML code from a sequence diagram model.

        Args:
            diagram: The sequence diagram model

        Returns:
            The generated PlantUML code
        """
        lines = ["@startuml", ""]

        # Add title
        if diagram.title:
            lines.append(f"title {diagram.title}")
            lines.append("")

        # Add global settings from the settings dict, or use defaults
        hide_footboxes = self.settings.get("HIDE_FOOTBOXES", True)
        autonumber = self.settings.get("AUTONUMBER", False)

        settings = [
            "skinparam sequenceMessageAlign center",
            "skinparam monochrome true",
            "skinparam lifelinestrategy solid",
        ]

        if hide_footboxes:
            settings.append("hide footbox")

        if autonumber:
            settings.append("autonumber")

        lines.extend(settings)
        lines.append("")

        # Add participants
        for participant in diagram.participants:
            lines.append(self._format_participant(participant))
        lines.append("")

        # Process messages and activations
        active_participants = set()

        for i, message in enumerate(diagram.messages):
            # Handle activations
            if message.message_type in (
                MessageType.SYNCHRONOUS,
                MessageType.ASYNCHRONOUS,
            ):
                # Ensure source is activated if not already
                if (
                    message.from_participant not in active_participants
                    and message.from_participant != message.to_participant
                ):
                    lines.append(f"activate {message.from_participant}")
                    active_participants.add(message.from_participant)

                # Add the message
                lines.append(self._format_message(message))

                # Activate the target
                if (
                    not message.is_self_message
                    and message.to_participant not in active_participants
                ):
                    lines.append(f"activate {message.to_participant}")
                    active_participants.add(message.to_participant)

            elif message.message_type == MessageType.REPLY:
                # Add the message
                lines.append(self._format_message(message))

                # Deactivate the source on return
                if message.from_participant in active_participants:
                    lines.append(f"deactivate {message.from_participant}")
                    active_participants.remove(message.from_participant)

            else:
                # Other message types (CREATE, etc.)
                lines.append(self._format_message(message))

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
            **kwargs: Additional generator-specific arguments

        Raises:
            GeneratorError: If the diagram cannot be generated
        """
        try:
            # Ensure the model is a SequenceDiagram
            if not isinstance(model, SequenceDiagram):
                raise GeneratorError(
                    f"Expected SequenceDiagram, got {type(model).__name__}",
                )

            # Generate the PlantUML code
            plantuml_code = self.generate_plantuml(model)

            # Ensure output directory exists and write the file
            output_path = (
                Path(output_path) if isinstance(output_path, str) else output_path
            )
            self.file_system.ensure_directory(output_path.parent)
            self.file_system.write_file(output_path, plantuml_code)

        except Exception as e:
            raise GeneratorError(
                f"Failed to generate sequence diagram: {e}",
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
        # Filter to only include sequence diagrams
        sequence_diagrams = [
            d
            for d in diagrams
            if d.name.endswith(".puml") and self._is_sequence_diagram(d)
        ]

        if not sequence_diagrams:
            return

        try:
            output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
            index_path = output_dir / "sequence_index.rst"

            # Create basic RST index
            lines = [
                "Sequence Diagrams",
                "================",
                "",
                ".. toctree::",
                "   :maxdepth: 1",
                "",
            ]

            # Add diagram references
            for diagram in sorted(sequence_diagrams):
                rel_path = diagram.relative_to(output_dir)
                # Use forward slashes for cross-platform compatibility
                lines.append(f"   {str(rel_path).replace('\\', '/')}")

            lines.append("")  # Add trailing newline

            # Write the index file
            self.file_system.write_file(index_path, "\n".join(lines))

        except Exception as e:
            raise GeneratorError(
                f"Failed to generate sequence diagram index: {e}",
                cause=e,
            )

    def _is_sequence_diagram(self, file_path: Path) -> bool:
        """Check if a file is a sequence diagram.

        Args:
            file_path: The path to the file to check

        Returns:
            True if the file is a sequence diagram, False otherwise
        """
        try:
            content = self.file_system.read_file(file_path)
            # Simple heuristic: look for sequence diagram indicators
            indicators = [
                "participant",
                "actor",
                "activate",
                "deactivate",
                "skinparam sequenceMessageAlign",
            ]
            return any(indicator in content for indicator in indicators)
        except Exception:
            return False
