"""Data models for sequence diagram extraction.

This module provides the data models for representing sequence diagrams.
"""

from dataclasses import dataclass, field
from enum import Enum

from utils.uml.diagrams.base import BaseDiagramModel


class ParticipantType(Enum):
    """Types of participants in a sequence diagram."""

    ACTOR = "actor"
    BOUNDARY = "boundary"
    CONTROL = "control"
    ENTITY = "entity"
    DATABASE = "database"
    CLASS = "class"  # Regular Python class


@dataclass
class Participant:
    """Represents a participant in a sequence diagram."""

    name: str
    type: ParticipantType = ParticipantType.CLASS
    module: str | None = None
    alias: str | None = None

    @property
    def full_name(self) -> str:
        """Get the full name with module.

        Returns:
            The full name of the participant, including module if available.
        """
        if self.module:
            return f"{self.module}.{self.name}"
        return self.name


class MessageType(Enum):
    """Types of messages in a sequence diagram."""

    SYNCHRONOUS = "->"
    ASYNCHRONOUS = "->>"
    REPLY = "-->"
    CREATE = "-->>"
    SELF = "->"


@dataclass
class Message:
    """Represents a message between participants."""

    from_participant: str
    to_participant: str
    text: str
    message_type: MessageType = MessageType.SYNCHRONOUS
    is_self_message: bool = False
    level: int = 0  # Call stack level
    method_name: str | None = None
    arguments: list[str] = field(default_factory=list)

    @property
    def formatted_text(self) -> str:
        """Format the text with arguments if needed.

        Returns:
            Formatted text for the message, including method name and arguments if available.
        """
        if self.method_name:
            args_str = ", ".join(self.arguments)
            return f"{self.method_name}({args_str})"
        return self.text


@dataclass
class ActivationBar:
    """Represents activation of a participant."""

    participant: str
    is_start: bool = True  # True for activation start, False for deactivation


class SequenceDiagram(BaseDiagramModel):
    """Represents a sequence diagram."""

    def __init__(self, title: str):
        """Initialize a sequence diagram.

        Args:
            title: The title of the diagram
        """
        super().__init__(name=title, diagram_type="sequence")
        self.title = title
        self.participants: list[Participant] = []
        self.messages: list[Message] = []
        self.activations: list[ActivationBar] = []

    def add_participant(self, participant: Participant) -> None:
        """Add a participant if it doesn't already exist.

        Args:
            participant: The participant to add
        """
        if not any(p.name == participant.name for p in self.participants):
            self.participants.append(participant)

    def add_message(self, message: Message) -> None:
        """Add a message to the diagram.

        Args:
            message: The message to add
        """
        self.messages.append(message)

        # Add activation/deactivation if it's a method call
        if message.message_type in (MessageType.SYNCHRONOUS, MessageType.ASYNCHRONOUS):
            # Start activation on the target
            self.activations.append(
                ActivationBar(
                    participant=message.to_participant,
                    is_start=True,
                ),
            )
        elif message.message_type == MessageType.REPLY:
            # End activation on the source
            self.activations.append(
                ActivationBar(
                    participant=message.from_participant,
                    is_start=False,
                ),
            )


@dataclass
class FunctionCall:
    """Represents a function call extracted from code."""

    caller_class: str | None
    caller_method: str | None
    called_class: str | None
    called_method: str
    arguments: list[str] = field(default_factory=list)
    is_constructor: bool = False
    line_number: int = 0
    file_path: str | None = None
