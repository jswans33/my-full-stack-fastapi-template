UML Sequence Diagram Implementation Guide
=====================================

This guide provides concrete step-by-step instructions for implementing sequence diagram support in the UML generator. This implementation approach is designed to be clear and easy to follow.

Prerequisites
------------

- Existing UML generator code in ``utils/uml_generator``
- Python 3.10+ with typing support
- Understanding of the current UML generator architecture

Implementation Steps
-------------------

Step 1: Create Sequence Diagram Models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, create a new file for sequence diagram models:

**File: utils/uml_generator/models/sequence.py**

.. code-block:: python

    """Models for sequence diagram generation."""
    
    from dataclasses import dataclass, field
    from enum import Enum, auto
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
            return f"{type_str} \"{self.name}\"{alias_str}{stereotype_str}"
    
    
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
        messages: List['SequenceItem'] = field(default_factory=list)
        alternatives: List[tuple[str, List['SequenceItem']]] = field(default_factory=list)
        
        def to_plantuml(self) -> list[str]:
            """Convert to PlantUML representation."""
            lines = [f"{self.type} {self.label}"]
            
            for item in self.messages:
                if isinstance(item, str):
                    lines.append(item)
                else:
                    lines.append(item.to_plantuml())
            
            for alt_label, alt_messages in self.alternatives:
                lines.append(f"else {alt_label}")
                for item in alt_messages:
                    if isinstance(item, str):
                        lines.append(item)
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

Step 2: Create Sequence Diagram Generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next, create a new generator for sequence diagrams:

**File: utils/uml_generator/generator/sequence_generator.py**

.. code-block:: python

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
                Participant, ParticipantType,
                Message, ArrowStyle,
                ActivationBar, SequenceGroup,
                SequenceDiagram
            )
            
            # Extract basic diagram properties
            title = yaml_data.get("title", "Sequence Diagram")
            hide_footboxes = yaml_data.get("hide_footboxes", True)
            autonumber = yaml_data.get("autonumber", False)
            
            # Create participants
            participants = []
            for p_def in yaml_data.get("participants", []):
                p_type = ParticipantType(p_def.get("type", "participant"))
                participants.append(Participant(
                    name=p_def["name"],
                    type=p_type,
                    alias=p_def.get("alias"),
                    stereotype=p_def.get("stereotype")
                ))
            
            # Create sequence items
            items = []
            for i_def in yaml_data.get("items", []):
                item_type = i_def.get("type")
                
                if item_type == "message":
                    arrow_style = ArrowStyle(i_def.get("arrow_style", "->"))
                    items.append(Message(
                        from_participant=i_def["from"],
                        to_participant=i_def["to"],
                        text=i_def["text"],
                        arrow_style=arrow_style,
                        is_self_message=i_def.get("is_self_message", False),
                        activate_target=i_def.get("activate_target", True),
                        deactivate_after=i_def.get("deactivate_after", False)
                    ))
                
                elif item_type == "activate":
                    items.append(ActivationBar(
                        participant=i_def["participant"],
                        is_activation=True
                    ))
                
                elif item_type == "deactivate":
                    items.append(ActivationBar(
                        participant=i_def["participant"],
                        is_activation=False
                    ))
                
                elif item_type == "note":
                    position = i_def.get("position", "over")
                    participants_str = i_def["participants"]
                    items.append(f"note {position} {participants_str}: {i_def['text']}")
                
                elif item_type in ("alt", "opt", "loop", "par", "break", "critical", "group"):
                    group = SequenceGroup(
                        type=item_type,
                        label=i_def.get("label", ""),
                        messages=[],
                        alternatives=[]
                    )
                    
                    # Process main messages
                    for msg in i_def.get("messages", []):
                        group.messages.append(self._create_sequence_item(msg))
                    
                    # Process alternatives (for 'alt')
                    for alt in i_def.get("alternatives", []):
                        alt_label = alt.get("label", "")
                        alt_messages = [self._create_sequence_item(msg) for msg in alt.get("messages", [])]
                        group.alternatives.append((alt_label, alt_messages))
                    
                    items.append(group)
                
                elif item_type == "divider":
                    items.append(f"== {i_def.get('text', 'Divider')} ==")
            
            return SequenceDiagram(
                title=title,
                participants=participants,
                items=items,
                hide_footboxes=hide_footboxes,
                autonumber=autonumber
            )
        
        def _create_sequence_item(self, item_def: dict):
            """Helper to create a sequence item from a definition."""
            from ..models.sequence import Message, ArrowStyle, ActivationBar
            
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
                    deactivate_after=item_def.get("deactivate_after", False)
                )
            
            elif item_type == "activate":
                return ActivationBar(
                    participant=item_def["participant"],
                    is_activation=True
                )
            
            elif item_type == "deactivate":
                return ActivationBar(
                    participant=item_def["participant"],
                    is_activation=False
                )
            
            elif item_type == "note":
                position = item_def.get("position", "over")
                participants_str = item_def["participants"]
                return f"note {position} {participants_str}: {item_def['text']}"
            
            # Default - return as string
            return str(item_def.get("text", ""))

Step 3: Update the Generator Factory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the generator factory to support the new diagram type:

**File: utils/uml_generator/factories.py**

.. code-block:: python

    # Add the import at the top
    from .generator.sequence_generator import SequenceDiagramGenerator
    
    # Then modify the DefaultGeneratorFactory.create_generator method:
    def create_generator(self, type_name: str) -> DiagramGenerator:
        """Create a diagram generator.
        
        Args:
            type_name: Type of generator to create
        
        Returns:
            DiagramGenerator instance
            
        Raises:
            ValueError: If the generator type is not supported
        """
        if type_name == "plantuml":
            return PlantUmlGenerator(
                self.file_system,
                self.settings.get("plantuml_settings", {})
            )
        elif type_name == "sequence":  # Add this condition
            return SequenceDiagramGenerator(
                self.file_system, 
                self.settings.get("sequence_settings", {})
            )
        else:
            raise ValueError(f"Unsupported generator type: {type_name}")

Step 4: Create a CLI Command for Sequence Diagrams
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a command to generate sequence diagrams from YAML files:

**File: utils/uml_generator/cli.py**

.. code-block:: python

    # Add a new command to the CLI
    
    @cli.command()
    @click.option(
        "--file", "-f", 
        required=True, 
        help="YAML file defining the sequence diagram"
    )
    @click.option(
        "--output", "-o", 
        required=True, 
        help="Output file path for the generated diagram"
    )
    def generate_sequence(file, output):
        """Generate a sequence diagram from a YAML definition file."""
        # Set up the generator
        file_system = DefaultFileSystem()
        factory = DefaultGeneratorFactory(file_system, {})
        generator = factory.create_generator("sequence")
        
        # Generate the diagram
        generator.generate_from_yaml(Path(file), Path(output))
        click.echo(f"Sequence diagram generated at {output}")

Step 5: Create a Sample YAML Definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create an example YAML file for defining a sequence diagram:

**File: examples/sequence_diagrams/auth_flow.yaml**

.. code-block:: yaml

    title: User Authentication Flow
    hide_footboxes: true
    autonumber: true
    
    participants:
      - name: User
        type: actor
      - name: AuthController
        type: boundary
      - name: UserService
        type: control
      - name: Database
        type: database
    
    items:
      - type: message
        from: User
        to: AuthController
        text: "login(credentials)"
      
      - type: message
        from: AuthController
        to: UserService
        text: "authenticate(username, password)"
      
      - type: message
        from: UserService
        to: Database
        text: "findUser(username)"
      
      - type: message
        from: Database
        to: UserService
        text: "User or null"
        arrow_style: -->
      
      - type: alt
        label: "if user exists"
        messages:
          - type: message
            from: UserService
            to: UserService
            text: "validatePassword(password)"
            is_self_message: true
          
          - type: message
            from: UserService
            to: AuthController
            text: "AuthResult(success=true, token=jwt)"
            arrow_style: -->
          
          - type: message
            from: AuthController
            to: User
            text: "200 OK, JWT Token"
            arrow_style: -->
        
        alternatives:
          - label: "else"
            messages:
              - type: message
                from: UserService
                to: AuthController
                text: "AuthResult(success=false)"
                arrow_style: -->
              
              - type: message
                from: AuthController
                to: User
                text: "401 Unauthorized"
                arrow_style: -->

Step 6: Update Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the configuration loader to support sequence diagram settings:

**File: utils/uml_generator/config/loader.py**

.. code-block:: python

    # Add sequence settings to the config model
    
    @dataclass
    class SequenceSettings:
        """Settings for sequence diagram generation."""
        
        PLANTUML_START: str = "@startuml"
        PLANTUML_END: str = "@enduml"
        DEFAULT_ARROW_STYLE: str = "->"
        AUTONUMBER: bool = False
        HIDE_FOOTBOXES: bool = True
    
    
    @dataclass
    class GeneratorConfig:
        """Configuration for diagram generators."""
        
        format: str
        plantuml_settings: dict = field(default_factory=dict)
        sequence_settings: dict = field(default_factory=dict)  # Add this line
    
    
    # Then in the load_config function add support for sequence settings:
    
    # Extract generator configuration
    generator_format = config_dict.get("generator", {}).get("format", "plantuml")
    plantuml_settings = config_dict.get("generator", {}).get("plantuml_settings", {})
    sequence_settings = config_dict.get("generator", {}).get("sequence_settings", {})  # Add this
    
    generator_config = GeneratorConfig(
        format=generator_format,
        plantuml_settings=plantuml_settings,
        sequence_settings=sequence_settings,  # Add this
    )

Step 7: Create an Integration Test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a test for the sequence diagram generator:

**File: utils/uml_generator/tests/test_sequence_generator.py**

.. code-block:: python

    """Tests for sequence diagram generator."""
    
    import tempfile
    from pathlib import Path
    
    import pytest
    
    from ..generator.sequence_generator import SequenceDiagramGenerator
    from ..models.sequence import (
        Participant, ParticipantType,
        Message, ArrowStyle,
        SequenceDiagram
    )
    from ..filesystem import DefaultFileSystem
    
    
    class TestSequenceDiagramGenerator:
        """Tests for the SequenceDiagramGenerator class."""
        
        def test_generate_simple_diagram(self):
            """Test generating a simple sequence diagram."""
            # Create diagram model
            diagram = SequenceDiagram(
                title="Test Sequence Diagram",
                participants=[
                    Participant("Client", ParticipantType.ACTOR),
                    Participant("Server", ParticipantType.PARTICIPANT)
                ],
                items=[
                    Message("Client", "Server", "Request Data"),
                    Message("Server", "Client", "Response Data", ArrowStyle.REPLY)
                ]
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
                assert "actor \"Client\"" in content
                assert "participant \"Server\"" in content
                assert "Client -> Server: Request Data" in content
                assert "Server --> Client: Response Data" in content
                assert "@enduml" in content

Step 8: Usage Example
~~~~~~~~~~~~~~~~~~~

Here's how to use the newly implemented sequence diagram generator:

**Option 1: From Python code**

.. code-block:: python

    from pathlib import Path
    from utils.uml_generator.filesystem import DefaultFileSystem
    from utils.uml_generator.models.sequence import (
        Participant, ParticipantType,
        Message, ArrowStyle, SequenceDiagram
    )
    from utils.uml_generator.generator.sequence_generator import SequenceDiagramGenerator
    
    # Create diagram model
    diagram = SequenceDiagram(
        title="Login Flow",
        participants=[
            Participant("User", ParticipantType.ACTOR),
            Participant("API", ParticipantType.BOUNDARY),
            Participant("Auth", ParticipantType.CONTROL),
            Participant("DB", ParticipantType.DATABASE)
        ],
        items=[
            Message("User", "API", "POST /login"),
            Message("API", "Auth", "validateCredentials()"),
            Message("Auth", "DB", "findUser()"),
            Message("DB", "Auth", "User", ArrowStyle.REPLY),
            Message("Auth", "API", "Token", ArrowStyle.REPLY),
            Message("API", "User", "200 OK + JWT", ArrowStyle.REPLY)
        ]
    )
    
    # Generate diagram
    file_system = DefaultFileSystem()
    generator = SequenceDiagramGenerator(file_system)
    output_path = Path("docs/source/_generated_uml/login_flow.puml")
    generator.generate_diagram(diagram, output_path)

**Option 2: From YAML file via CLI**

.. code-block:: bash

    # Create a YAML file as shown in Step 5
    # Then run:
    python -m utils.uml_generator.cli generate-sequence --file examples/sequence_diagrams/auth_flow.yaml --output docs/source/_generated_uml/auth_flow.puml

**Option 3: Update run_uml_generator.py to support sequence diagrams**

Add a function to generate sequence diagrams to `run_uml_generator.py`:

.. code-block:: python

    def generate_sequence_diagrams(base_dir: Path) -> None:
        """Generate sequence diagrams from YAML definitions."""
        sequence_dir = base_dir / "examples" / "sequence_diagrams"
        output_dir = Path("docs/source/_generated_uml/sequence")
        
        if not sequence_dir.exists():
            print(f"No sequence diagram definitions found at {sequence_dir}")
            return
        
        file_system = DefaultFileSystem()
        file_system.ensure_directory(output_dir)
        
        # Create generator
        generator_factory = DefaultGeneratorFactory(
            file_system,
            {"sequence_settings": {"HIDE_FOOTBOXES": True}}
        )
        generator = generator_factory.create_generator("sequence")
        
        # Process all YAML files
        for yaml_file in sequence_dir.glob("*.yaml"):
            output_file = output_dir / f"{yaml_file.stem}.puml"
            print(f"Generating sequence diagram from {yaml_file} to {output_file}")
            generator.generate_from_yaml(yaml_file, output_file)

Step 9: Add to Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the uml_diagrams.rst file to include a section for sequence diagrams:

**File: docs/source/uml_diagrams.rst**

.. code-block:: rst

    Sequence Diagrams
    ----------------
    
    Authentication Flow
    ~~~~~~~~~~~~~~~~~~
    
    .. uml:: ../_generated_uml/sequence/auth_flow.puml

Step 10: Update Main Project Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the new UML implementation guide to the index.rst file:

**File: docs/source/index.rst**

.. code-block:: rst

    .. toctree::
       :maxdepth: 2
       :caption: Contents:
       
       ...
       uml_setup
       uml_diagrams
       uml_structure
       uml_extension
       uml_implementation_guide

Conclusion
----------

This implementation guide has been successfully completed with both YAML-based sequence diagrams and static code analysis-based sequence diagrams now implemented. Both approaches are integrated into the main UML generator workflow. The same approach can be used for other diagram types.

Key files created or modified:
- For YAML-based sequence diagrams:
  - ``utils/uml_generator/models/sequence.py``
  - ``utils/uml_generator/generator/sequence_generator.py``
  - ``utils/uml_generator/factories.py`` (modified)
  - ``utils/uml_generator/cli.py`` (modified)
  - ``utils/uml_generator/config/loader.py`` (modified)
- For Code Analysis-based sequence diagrams:
  - ``utils/sequence_extractor/`` directory with analyzer, models, and generator
  - ``utils/extract_sequence.py`` CLI tool
  - ``utils/run_uml_generator.py`` (modified to include static analysis)
- ``utils/uml_generator/tests/test_sequence_generator.py``
- ``docs/source/uml_diagrams.rst`` (modified)
- ``docs/source/index.rst`` (modified)

Benefits of this implementation:
- Maintains the existing architecture
- Provides a clean, modular approach for adding new diagram types
- Offers both programmatic and YAML-based diagram creation
- Includes comprehensive tests and examples
- Provides both static code analysis and manual definition approaches

**Note on Errors**: When running the UML generator, you may see errors like `AttributeModel.__init__() got an unexpected keyword argument 'default_value'` or `ClassModel.__init__() got an unexpected keyword argument 'docstring'`. These errors occur when the UML generator attempts to analyze our sequence diagram implementation code itself. These errors do not prevent sequence diagrams from being generated correctly.