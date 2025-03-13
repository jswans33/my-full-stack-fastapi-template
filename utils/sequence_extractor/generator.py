"""Generator for converting sequence diagrams to PlantUML format."""

from pathlib import Path

from .models import ActivationBar, Message, MessageType, Participant, SequenceDiagram


class PlantUmlSequenceGenerator:
    """Generates PlantUML sequence diagrams from our sequence model."""

    def __init__(self):
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
        """Format a participant as PlantUML."""
        participant_type = participant.type.value

        if participant.alias:
            return f'{participant_type} "{participant.name}" as {participant.alias}'

        # Handle special characters in class names by optionally using quotes
        if any(c in participant.name for c in " .-,;:/\\()[]{}<>!@#$%^&*+=|`~"):
            return f'{participant_type} "{participant.name}"'
        return f"{participant_type} {participant.name}"

    def _format_message(self, message: Message) -> str:
        """Format a message as PlantUML."""
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
        """Format an activation/deactivation as PlantUML."""
        if activation.is_start:
            return f"activate {activation.participant}"
        return f"deactivate {activation.participant}"

    def generate_plantuml(self, diagram: SequenceDiagram) -> str:
        """Generate PlantUML code from a sequence diagram model."""
        lines = ["@startuml", ""]

        # Add title
        if diagram.title:
            lines.append(f"title {diagram.title}")
            lines.append("")

        # Add global settings
        lines.extend(
            [
                "skinparam sequenceMessageAlign center",
                "skinparam monochrome true",
                "skinparam lifelinestrategy solid",
                "hide footbox",
                "",
            ]
        )

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

    def generate_file(
        self,
        diagram: SequenceDiagram,
        output_path: str | Path,
    ) -> None:
        """Generate a PlantUML file from a sequence diagram model."""
        plantuml_code = self.generate_plantuml(diagram)

        # Ensure output directory exists
        output_path = Path(output_path) if isinstance(output_path, str) else output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(plantuml_code)
