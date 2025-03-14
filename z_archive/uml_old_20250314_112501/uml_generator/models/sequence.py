"""Models for sequence diagram generation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ParticipantType(Enum):
    """Types of participants in a sequence diagram."""

    ACTOR = "actor"
    BOUNDARY = "boundary"
    CONTROL = "control"
    ENTITY = "entity"
    DATABASE = "database"
    COLLECTIONS = "collections"
    PARTICIPANT = "participant"  # Default


@dataclass
class Participant:
    """Represents a participant in a sequence diagram."""

    name: str
    type: ParticipantType = ParticipantType.PARTICIPANT
    alias: Optional[str] = None
    stereotype: Optional[str] = None

    def to_plantuml(self) -> str:
        """Convert to PlantUML representation."""
        type_str = self.type.value
        alias_str = f" as {self.alias}" if self.alias else ""
        stereotype_str = f" <<{self.stereotype}>>" if self.stereotype else ""
        return f'{type_str} "{self.name}"{alias_str}{stereotype_str}'


class ArrowStyle(Enum):
    """Arrow styles for sequence diagram messages."""

    SYNC = "->"
    ASYNC = "->>"
    REPLY = "-->"
    CREATE = "-->>"
    SELF = "->"  # Will be handled specially in generation


@dataclass
class Message:
    """Represents a message between participants."""

    from_participant: str  # Name or alias
    to_participant: str  # Name or alias
    text: str
    arrow_style: ArrowStyle = ArrowStyle.SYNC
    is_self_message: bool = False
    activate_target: bool = True
    deactivate_after: bool = False

    def to_plantuml(self) -> str:
        """Convert to PlantUML representation."""
        arrow = self.arrow_style.value
        activation = ""
        if self.activate_target:
            activation = "+"
        if self.deactivate_after:
            activation = "-"

        if self.is_self_message:
            return f"{self.from_participant} {arrow}{activation} {self.from_participant}: {self.text}"
        else:
            return f"{self.from_participant} {arrow}{activation} {self.to_participant}: {self.text}"


@dataclass
class ActivationBar:
    """Represents an activation/deactivation in the sequence."""

    participant: str
    is_activation: bool = True  # True for activate, False for deactivate

    def to_plantuml(self) -> str:
        """Convert to PlantUML representation."""
        action = "activate" if self.is_activation else "deactivate"
        return f"{action} {self.participant}"


@dataclass
class SequenceGroup:
    """Represents a group of messages (alt, opt, loop, etc.)."""

    type: str  # alt, opt, loop, par, break, critical, group
    label: str
    messages: List["SequenceItem"] = field(default_factory=list)
    alternatives: List[tuple[str, List["SequenceItem"]]] = field(default_factory=list)

    def to_plantuml(self) -> list[str]:
        """Convert to PlantUML representation."""
        lines = [f"{self.type} {self.label}"]

        for item in self.messages:
            if isinstance(item, str):
                lines.append(item)
            else:
                if isinstance(item, SequenceGroup):
                    lines.extend(item.to_plantuml())
                else:
                    lines.append(item.to_plantuml())

        for alt_label, alt_messages in self.alternatives:
            lines.append(f"else {alt_label}")
            for item in alt_messages:
                if isinstance(item, str):
                    lines.append(item)
                else:
                    if isinstance(item, SequenceGroup):
                        lines.extend(item.to_plantuml())
                    else:
                        lines.append(item.to_plantuml())

        lines.append("end")
        return lines


# Type alias for items that can appear in a sequence
SequenceItem = Message | ActivationBar | SequenceGroup | str


@dataclass
class SequenceDiagram:
    """Main model for a sequence diagram."""

    title: str
    participants: List[Participant] = field(default_factory=list)
    items: List[SequenceItem] = field(default_factory=list)
    hide_footboxes: bool = True
    autonumber: bool = False

    def to_plantuml(self) -> str:
        """Convert the entire diagram to PlantUML notation."""
        lines = ["@startuml", f"title {self.title}"]

        if self.hide_footboxes:
            lines.append("hide footboxes")

        if self.autonumber:
            lines.append("autonumber")

        # Add all participants
        for participant in self.participants:
            lines.append(participant.to_plantuml())

        # Add sequence items
        for item in self.items:
            if isinstance(item, str):
                lines.append(item)
            elif isinstance(item, SequenceGroup):
                lines.extend(item.to_plantuml())
            else:
                lines.append(item.to_plantuml())

        lines.append("@enduml")
        return "\n".join(lines)
