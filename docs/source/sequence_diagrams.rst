Sequence Diagram Implementation
==========================

This document provides a technical overview of the sequence diagram implementation in the UML generator. It explains the architecture, components, and how the two approaches (YAML-based and code analysis-based) are implemented.

Architecture Overview
-------------------

The sequence diagram functionality consists of two complementary subsystems:

1. **YAML Definition System**: Integrated directly into the main UML generator
2. **Static Code Analysis System**: Implemented as a separate module with integration hooks

Both systems share the same output format (PlantUML) and are designed to work together to provide comprehensive sequence diagram support.

YAML Definition System
--------------------

The YAML definition system is tightly integrated with the existing UML generator architecture.

Key Components:

**Models** (``utils/uml_generator/models/sequence.py``)
    Defines the data structures representing sequence diagram elements:
    
    - ``ParticipantType`` - Enumeration of participant types (actor, boundary, etc.)
    - ``Participant`` - Represents an object in the sequence
    - ``ArrowStyle`` - Enumeration of message arrow styles
    - ``Message`` - Represents communication between participants
    - ``ActivationBar`` - Represents activation/deactivation of a participant
    - ``SequenceGroup`` - Represents logical groupings (alt, opt, loop)
    - ``SequenceDiagram`` - Top-level container for the entire diagram

**Generator** (``utils/uml_generator/generator/sequence_generator.py``)
    Converts the sequence models to PlantUML syntax:
    
    - ``SequenceDiagramGenerator`` - Main generator class
    - ``generate_diagram()`` - Generates PlantUML from a SequenceDiagram model
    - ``generate_from_yaml()`` - Parses YAML into a model and generates PlantUML
    - ``_create_model_from_yaml()`` - Converts YAML structure to model objects

**Factory Integration** (``utils/uml_generator/factories.py``)
    Updated to support sequence diagram generation:
    
    .. code-block:: python
        
        def create_generator(self, type_name: str) -> DiagramGenerator:
            if type_name == "plantuml":
                return PlantUmlGenerator(...)
            elif type_name == "sequence":
                return SequenceDiagramGenerator(...)
            else:
                raise ValueError(f"Unsupported generator type: {type_name}")

**CLI Extension** (``utils/uml_generator/cli.py``)
    Added a new command for sequence diagram generation:
    
    .. code-block:: python
        
        @cli.command()
        @click.option("--file", "-f", required=True, help="YAML file...")
        @click.option("--output", "-o", required=True, help="Output file...")
        def generate_sequence(file, output):
            """Generate a sequence diagram from a YAML definition file."""
            # Implementation...

**Main Generator Integration** (``utils/run_uml_generator.py``)
    Added sequence diagram processing to the main workflow:
    
    .. code-block:: python
        
        def generate_sequence_diagrams() -> None:
            """Generate sequence diagrams from YAML definitions."""
            sequence_dir = Path("examples/sequence_diagrams")
            # Process YAML files...

Static Code Analysis System
-------------------------

The static code analysis system is implemented as a separate module with its own components.

Key Components:

**Models** (``utils/sequence_extractor/models.py``)
    Defines data structures for the static analyzer:
    
    - ``Participant``, ``MessageType``, ``Message`` - Similar to YAML models
    - ``FunctionCall`` - Represents a function call extracted from code
    - ``SequenceDiagram`` - Container for the entire sequence

**Analyzer** (``utils/sequence_extractor/analyzer.py``)
    Performs static code analysis to extract sequence information:
    
    - ``MethodCallVisitor`` - AST visitor that extracts method calls
    - ``ClassDefVisitor`` - AST visitor that extracts class definitions
    - ``SequenceAnalyzer`` - Main analyzer that processes Python files
    - ``generate_sequence_diagram()`` - Creates a diagram from analysis results

**Generator** (``utils/sequence_extractor/generator.py``)
    Converts extracted sequence information to PlantUML:
    
    - ``PlantUmlSequenceGenerator`` - Generates PlantUML from sequence models
    - ``generate_plantuml()`` - Creates the PlantUML text representation
    - ``generate_file()`` - Writes the diagram to a file

**CLI Tool** (``utils/extract_sequence.py``)
    Command-line interface for the static analyzer:
    
    .. code-block:: python
        
        def main():
            """Run the sequence diagram extractor."""
            parser = argparse.ArgumentParser(...)
            # Parse arguments, run analyzer, generate diagram...

**FastAPI Integration** (``utils/extract_app_sequences.py``)
    Script specifically for analyzing FastAPI applications:
    
    .. code-block:: python
        
        # Define important entry points for sequence diagrams
        ENTRY_POINTS = [
            # User Authentication Flows
            ("login", "login_access_token", "authentication_flow"),
            # Other entry points...
        ]
        
        # Process each entry point...

Class Hierarchy
-------------

The following diagram shows the key classes in the sequence diagram implementation:

.. code-block:: text

    ┌─────────────────────┐      ┌───────────────────────┐
    │  YAML-Based System  │      │ Static Analysis System │
    └─────────────────────┘      └───────────────────────┘
              │                              │
    ┌─────────┴─────────┐          ┌────────┴────────┐
    │  SequenceDiagram  │          │  SequenceDiagram │
    └───────────────────┘          └─────────────────┘
              │                              │
    ┌─────────┴─────────┐          ┌────────┴────────┐
    │Participant,Message│          │Participant,Message
    │ActivationBar, etc │          │FunctionCall, etc │
    └───────────────────┘          └─────────────────┘
              │                              │
    ┌─────────┴─────────┐          ┌────────┴────────┐
    │SequenceDiagramGen.│          │SequenceAnalyzer │
    │  generate_diagram │          │generate_sequence │
    └───────────────────┘          └─────────────────┘
              │                              │
              └──────────────┬───────────────┘
                             │
                     ┌───────┴───────┐
                     │   PlantUML    │
                     │ Sequence      │
                     │ Diagram       │
                     └───────────────┘

Technical Implementation Details
-----------------------------

AST-Based Analysis
~~~~~~~~~~~~~~~~

The static code analyzer uses Python's Abstract Syntax Tree (AST) module to parse and analyze Python source code:

1. ``ast.parse()`` creates an AST representation of the source code
2. Custom visitors (``MethodCallVisitor``, ``ClassDefVisitor``) traverse the AST
3. The visitors extract method calls, class definitions, and dependencies
4. This information is used to construct a call graph
5. The call graph is transformed into a sequence diagram

Here's a simplified view of how AST nodes are processed:

.. code-block:: python

    def visit_Call(self, node: ast.Call) -> None:
        """Visit a function call node."""
        # For method calls: obj.method()
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            obj_name = node.func.value.id
            method_name = node.func.attr
            
            # Track the method call...
            
        # Continue visiting child nodes
        self.generic_visit(node)

YAML Parsing
~~~~~~~~~~~

The YAML definition system uses a structured schema to define sequence diagrams:

1. YAML content is parsed using PyYAML
2. The parsed dictionary is converted to model objects
3. The model objects are then rendered as PlantUML

The YAML schema validation is performed during the conversion process:

.. code-block:: python

    def _create_model_from_yaml(self, yaml_data: dict) -> SequenceDiagram:
        """Create a SequenceDiagram model from YAML data."""
        # Extract basic properties
        title = yaml_data.get("title", "Sequence Diagram")
        hide_footboxes = yaml_data.get("hide_footboxes", True)
        
        # Create participants from YAML
        participants = []
        for p_def in yaml_data.get("participants", []):
            # Validate and convert...
            
        # Create sequence items from YAML 
        items = []
        for i_def in yaml_data.get("items", []):
            # Validate and convert...
            
        return SequenceDiagram(...)

FastAPI Integration
~~~~~~~~~~~~~~~~

The system includes special handling for FastAPI router functions:

1. ``extract_app_sequences.py`` identifies key API endpoints
2. It uses the module path (e.g., ``api.routes.login``) to locate the code
3. For each endpoint, it extracts the sequence of method calls
4. These calls are converted into a sequence diagram

Importlib is used to dynamically import and analyze modules:

.. code-block:: python

    # Add the root directory to Python path
    sys.path.insert(0, str(dir_path.parent))
    
    # Import the module
    module_obj = importlib.import_module(args.module, package=dir_path.name)

Integration with Main UML Generator
---------------------------------

The sequence diagram functionality is integrated with the main UML generator in several ways:

1. YAML-based diagrams are automatically processed during normal operation
2. The ``utils/run_uml_generator.py`` script calls ``utils/extract_app_sequences.py``
3. All generated diagrams appear in ``docs/source/_generated_uml/sequence/``
4. The diagrams are included in the index and available in the documentation

This integration ensures that sequence diagrams are always up-to-date with the codebase.

Limitations and Future Improvements
--------------------------------

Static Analysis Limitations
~~~~~~~~~~~~~~~~~~~~~~~~

The current static analysis has some limitations:

1. **Type Inference**: Limited ability to determine actual types of variables
2. **Control Flow**: Does not fully track conditions and loops
3. **External Libraries**: Limited analysis of external dependencies
4. **Dynamic Features**: Cannot analyze dynamic Python features (e.g., ``getattr``)

Future improvements could address these limitations by:

1. Adding more sophisticated type inference
2. Implementing control flow analysis
3. Tracking object lifecycles more accurately
4. Providing plugins for common frameworks like FastAPI

YAML Definition Improvements
~~~~~~~~~~~~~~~~~~~~~~~~~

Future improvements to the YAML system could include:

1. Advanced activation/deactivation tracking
2. Better support for nested alternatives and loops
3. Mixed notation (text and graphical elements)
4. Integration with JSON Schema for validation

Integration Improvements
~~~~~~~~~~~~~~~~~~~~

Integration between the two approaches could be enhanced by:

1. Using YAML definitions to supplement static analysis
2. Automatic suggestions for YAML based on static analysis
3. A unified CLI for both approaches
4. A graphical editor for sequence diagrams

Testing Strategy
-------------

The sequence diagram implementation includes comprehensive tests:

1. **Unit Tests**: Test individual components (models, generators)
2. **Integration Tests**: Test end-to-end functionality
3. **Example Tests**: Scripts to verify real-world examples
4. **Validation Tests**: Ensure generated PlantUML is valid

These tests ensure that both approaches work correctly and produce valid diagrams.

Conclusion
---------

The sequence diagram implementation provides two complementary approaches:

1. **YAML Definition**: For precise control and detailed diagrams
2. **Static Analysis**: For automatic extraction from existing code

Together, these approaches offer a powerful solution for documenting system interactions. The implementation is well-integrated with the existing UML generator and follows the same architectural principles.

For usage instructions, see the :doc:`sequence_diagram_usage` guide.