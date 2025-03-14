"""Tests for sequence diagram generator."""

import tempfile
from pathlib import Path

from ..filesystem import DefaultFileSystem
from ..generator.sequence_generator import SequenceDiagramGenerator
from ..models.sequence import (
    ArrowStyle,
    Message,
    Participant,
    ParticipantType,
    SequenceDiagram,
)


class TestSequenceDiagramGenerator:
    """Tests for the SequenceDiagramGenerator class."""

    def test_generate_simple_diagram(self):
        """Test generating a simple sequence diagram."""
        # Create diagram model
        diagram = SequenceDiagram(
            title="Test Sequence Diagram",
            participants=[
                Participant("Client", ParticipantType.ACTOR),
                Participant("Server", ParticipantType.PARTICIPANT),
            ],
            items=[
                Message("Client", "Server", "Request Data"),
                Message("Server", "Client", "Response Data", ArrowStyle.REPLY),
            ],
        )

        # Create generator
        file_system = DefaultFileSystem()
        generator = SequenceDiagramGenerator(file_system)

        # Generate diagram to a temporary file
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "test_sequence.puml"
            generator.generate_diagram(diagram, output_path)

            # Verify the file exists
            assert output_path.exists()

            # Read the file contents
            content = output_path.read_text()

            # Verify the content
            assert "@startuml" in content
            assert "title Test Sequence Diagram" in content
            assert 'actor "Client"' in content
            assert 'participant "Server"' in content
            assert "Client -> Server: Request Data" in content
            assert "Server --> Client: Response Data" in content
            assert "@enduml" in content
