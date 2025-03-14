"""Sequence diagram generator."""

import logging
from pathlib import Path

from ..interfaces import DiagramGenerator, FileSystem
from ..models.sequence import SequenceDiagram


class SequenceDiagramGenerator(DiagramGenerator):
    """Generator for sequence diagrams in PlantUML format."""

    def __init__(self, file_system: FileSystem, settings=None):
        """Initialize the sequence diagram generator.

        Args:
            file_system: Interface for file system operations
            settings: Optional settings dictionary
        """
        self.file_system = file_system
        self.settings = settings or {}
        self.logger = logging.getLogger(__name__)

    def get_output_extension(self) -> str:
        """Return the file extension for generated diagrams."""
        return ".puml"

    def generate_diagram(self, diagram: SequenceDiagram, output_path: Path) -> None:
        """Generate a sequence diagram from a SequenceDiagram model.

        Args:
            diagram: The sequence diagram model
            output_path: Path where the diagram should be saved
        """
        self.logger.info(f"Generating sequence diagram: {diagram.title}")

        # Generate PlantUML content
        uml_content = diagram.to_plantuml()

        # Ensure output directory exists
        self.file_system.ensure_directory(output_path.parent)

        # Write the content to the output file
        self.file_system.write_file(output_path, uml_content)

        self.logger.info(f"Generated sequence diagram at {output_path}")

    def generate_from_yaml(self, yaml_path: Path, output_path: Path) -> None:
        """Generate a sequence diagram from a YAML definition.

        Args:
            yaml_path: Path to the YAML definition file
            output_path: Path where the diagram should be saved
        """
        try:
            import yaml
        except ImportError:
            self.logger.error("PyYAML is required for YAML-based diagram generation")
            raise ImportError("PyYAML is required. Install with 'pip install pyyaml'")

        # Read and parse the YAML file
        yaml_content = self.file_system.read_file(yaml_path)
        diagram_def = yaml.safe_load(yaml_content)

        # Create the sequence diagram model from the YAML definition
        sequence_model = self._create_model_from_yaml(diagram_def)

        # Generate the diagram
        self.generate_diagram(sequence_model, output_path)

    def _create_model_from_yaml(self, yaml_data: dict) -> SequenceDiagram:
        """Create a SequenceDiagram model from YAML data.

        Args:
            yaml_data: Dictionary parsed from YAML

        Returns:
            SequenceDiagram model
        """
        from ..models.sequence import (
            ActivationBar,
            ArrowStyle,
            Message,
            Participant,
            ParticipantType,
            SequenceDiagram,
            SequenceGroup,
        )

        # Extract basic diagram properties
        title = yaml_data.get("title", "Sequence Diagram")
        hide_footboxes = yaml_data.get("hide_footboxes", True)
        autonumber = yaml_data.get("autonumber", False)

        # Create participants
        participants = []
        for p_def in yaml_data.get("participants", []):
            p_type = ParticipantType(p_def.get("type", "participant"))
            participants.append(
                Participant(
                    name=p_def["name"],
                    type=p_type,
                    alias=p_def.get("alias"),
                    stereotype=p_def.get("stereotype"),
                )
            )

        # Create sequence items
        items = []
        for i_def in yaml_data.get("items", []):
            item_type = i_def.get("type")

            if item_type == "message":
                arrow_style = ArrowStyle(i_def.get("arrow_style", "->"))
                items.append(
                    Message(
                        from_participant=i_def["from"],
                        to_participant=i_def["to"],
                        text=i_def["text"],
                        arrow_style=arrow_style,
                        is_self_message=i_def.get("is_self_message", False),
                        activate_target=i_def.get("activate_target", True),
                        deactivate_after=i_def.get("deactivate_after", False),
                    )
                )

            elif item_type == "activate":
                items.append(
                    ActivationBar(participant=i_def["participant"], is_activation=True)
                )

            elif item_type == "deactivate":
                items.append(
                    ActivationBar(participant=i_def["participant"], is_activation=False)
                )

            elif item_type == "note":
                position = i_def.get("position", "over")
                participants_str = i_def["participants"]
                items.append(f"note {position} {participants_str}: {i_def['text']}")

            elif item_type in (
                "alt",
                "opt",
                "loop",
                "par",
                "break",
                "critical",
                "group",
            ):
                group = SequenceGroup(
                    type=item_type,
                    label=i_def.get("label", ""),
                    messages=[],
                    alternatives=[],
                )

                # Process main messages
                for msg in i_def.get("messages", []):
                    group.messages.append(self._create_sequence_item(msg))

                # Process alternatives (for 'alt')
                for alt in i_def.get("alternatives", []):
                    alt_label = alt.get("label", "")
                    alt_messages = [
                        self._create_sequence_item(msg)
                        for msg in alt.get("messages", [])
                    ]
                    group.alternatives.append((alt_label, alt_messages))

                items.append(group)

            elif item_type == "divider":
                items.append(f"== {i_def.get('text', 'Divider')} ==")

        return SequenceDiagram(
            title=title,
            participants=participants,
            items=items,
            hide_footboxes=hide_footboxes,
            autonumber=autonumber,
        )

    def _create_sequence_item(self, item_def: dict):
        """Helper to create a sequence item from a definition."""
        from ..models.sequence import ActivationBar, ArrowStyle, Message

        item_type = item_def.get("type")

        if item_type == "message":
            arrow_style = ArrowStyle(item_def.get("arrow_style", "->"))
            return Message(
                from_participant=item_def["from"],
                to_participant=item_def["to"],
                text=item_def["text"],
                arrow_style=arrow_style,
                is_self_message=item_def.get("is_self_message", False),
                activate_target=item_def.get("activate_target", True),
                deactivate_after=item_def.get("deactivate_after", False),
            )

        elif item_type == "activate":
            return ActivationBar(
                participant=item_def["participant"], is_activation=True
            )

        elif item_type == "deactivate":
            return ActivationBar(
                participant=item_def["participant"], is_activation=False
            )

        elif item_type == "note":
            position = item_def.get("position", "over")
            participants_str = item_def["participants"]
            return f"note {position} {participants_str}: {item_def['text']}"

        # Default - return as string
        return str(item_def.get("text", ""))
