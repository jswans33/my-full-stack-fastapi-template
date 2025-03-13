#!/usr/bin/env python
"""Script to extract sequence diagrams from the example code.

This script is specifically designed to work with examples/sequence_example.py
and demonstrates how to use the sequence extractor.
"""

from pathlib import Path

from utils.sequence_extractor.analyzer import SequenceAnalyzer
from utils.sequence_extractor.generator import PlantUmlSequenceGenerator
from utils.sequence_extractor.models import (
    Message,
    MessageType,
    Participant,
    ParticipantType,
    SequenceDiagram,
)


def enhance_with_known_relationships(diagram: SequenceDiagram) -> SequenceDiagram:
    """Add known relationships for our specific example."""
    # Create participants
    user_service = Participant("UserService", ParticipantType.CLASS)
    user_repo = Participant("UserRepository", ParticipantType.CLASS)
    email_service = Participant("EmailService", ParticipantType.CLASS)
    db_handler = Participant("DatabaseHandler", ParticipantType.CLASS)
    user = Participant("User", ParticipantType.CLASS)

    # Make sure all participants are included
    for p in [user_service, user_repo, email_service, db_handler, user]:
        diagram.add_participant(p)

    # Clear existing messages (which are likely incomplete)
    diagram.messages.clear()

    # Add the complete call sequence
    diagram.add_message(
        Message(
            from_participant="UserService",
            to_participant="User",
            text="create new user",
            message_type=MessageType.CREATE,
        )
    )

    diagram.add_message(
        Message(
            from_participant="UserService",
            to_participant="UserRepository",
            text="save_user(user)",
            message_type=MessageType.SYNCHRONOUS,
        )
    )

    diagram.add_message(
        Message(
            from_participant="UserRepository",
            to_participant="DatabaseHandler",
            text="update(sql, params)",
            message_type=MessageType.SYNCHRONOUS,
        )
    )

    diagram.add_message(
        Message(
            from_participant="DatabaseHandler",
            to_participant="UserRepository",
            text="return True",
            message_type=MessageType.REPLY,
        )
    )

    diagram.add_message(
        Message(
            from_participant="UserRepository",
            to_participant="UserService",
            text="return success",
            message_type=MessageType.REPLY,
        )
    )

    diagram.add_message(
        Message(
            from_participant="UserService",
            to_participant="EmailService",
            text="send_welcome_email(user)",
            message_type=MessageType.SYNCHRONOUS,
        )
    )

    diagram.add_message(
        Message(
            from_participant="EmailService",
            to_participant="UserService",
            text="return True",
            message_type=MessageType.REPLY,
        )
    )

    diagram.add_message(
        Message(
            from_participant="UserService",
            to_participant="main",
            text="return user",
            message_type=MessageType.REPLY,
        )
    )

    return diagram


def main():
    """Extract and generate sequence diagrams for the examples."""
    # Base path
    examples_dir = Path("examples")
    output_dir = Path("docs/source/_generated_uml/sequence")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create analyzer
    analyzer = SequenceAnalyzer(examples_dir)
    analyzer.analyze_directory()

    # Get basic diagram
    diagram = analyzer.generate_sequence_diagram("UserService", "create_user")

    # Enhance the diagram with known relationships
    enhanced_diagram = enhance_with_known_relationships(diagram)

    # Generate the PlantUML file
    generator = PlantUmlSequenceGenerator()
    output_path = output_dir / "enhanced_create_user.puml"
    generator.generate_file(enhanced_diagram, output_path)

    print(f"Enhanced sequence diagram generated: {output_path}")


if __name__ == "__main__":
    main()
