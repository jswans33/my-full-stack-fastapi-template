UML State Diagram Implementation Guide
==================================

This guide provides concrete step-by-step instructions for implementing state diagram support in the UML generator. This implementation approach follows the same pattern as the sequence and activity diagram extractors.

Prerequisites
------------

- Existing UML generator code in ``utils/uml_generator``
- Existing sequence and activity extractors
- Python 3.10+ with typing support
- Understanding of the current UML generator architecture

Implementation Overview
---------------------

The implementation of state diagram support involves several key components:

1. **Data Models**: Define the structure of state diagrams, states, and transitions
2. **Analyzer**: Extract state patterns from Python code using AST analysis
3. **Generator**: Convert state diagram models to PlantUML format
4. **CLI Tool**: Provide a command-line interface for generating state diagrams
5. **Decorators**: Support explicit state and transition annotations in code

The implementation follows the same modular approach as the sequence and activity diagram extractors, making it easy to integrate with the existing UML generator.

Key Features
----------

The state diagram extractor can analyze Python classes to extract state patterns, including:

- Explicit state field assignments
- State transition methods
- Decorator-based state definitions

The extracted diagrams show the states of objects or systems and the transitions between them, which is particularly useful for understanding object lifecycles and reactive systems.

Implementation Steps
------------------

The implementation is divided into several steps:

1. Create state diagram models
2. Implement the state analyzer
3. Create the PlantUML generator
4. Add module initialization
5. Create a command-line interface
6. Update the main UML generator
7. Add state decorators
8. Update documentation

For detailed implementation of each step, refer to the following sections:

- :doc:`state_diagrams_models`
- :doc:`state_diagrams_analyzer`
- :doc:`state_diagrams_generator`
- :doc:`state_diagrams_usage`

Usage Example
-----------

Here's a simple example of how to use the state diagram extractor:

.. code-block:: python

    from pathlib import Path
    from utils.state_extractor import StateAnalyzer, PlantUmlStateGenerator
    
    # Create analyzer and analyze source code
    analyzer = StateAnalyzer("./backend/app")
    analyzer.analyze_directory()
    
    # Generate state diagram for a specific class
    diagram = analyzer.generate_state_diagram("Document")
    
    # Generate PlantUML file
    generator = PlantUmlStateGenerator()
    output_path = Path("docs/source/_generated_uml/state/Document_state.puml")
    generator.generate_file(diagram, output_path)

Implementation Diff
-----------------

Below is a summary of the changes needed to implement the state diagram extractor:

.. code-block:: diff

    # Create directories
    + mkdir -p utils/state_extractor
    + mkdir -p docs/source/_generated_uml/state

    # Create files
    + touch utils/state_extractor/__init__.py
    + touch utils/state_extractor/models.py
    + touch utils/state_extractor/analyzer.py
    + touch utils/state_extractor/generator.py
    + touch utils/extract_state.py
    + touch utils/state_decorators.py

Key files created:

- ``utils/state_extractor/models.py`` - Data models for state diagrams
- ``utils/state_extractor/analyzer.py`` - AST-based analyzer for state patterns
- ``utils/state_extractor/generator.py`` - PlantUML generator for state diagrams
- ``utils/state_extractor/__init__.py`` - Package initialization
- ``utils/extract_state.py`` - Command-line tool
- ``utils/state_decorators.py`` - Decorators for marking states and transitions

Conclusion
---------

This implementation guide provides a complete approach for adding state diagram extraction to the UML generator. The implementation follows the same pattern as the sequence and activity extractors, using AST-based static analysis to detect state patterns and transitions in Python code.

The state diagram extractor enhances the UML generator with the ability to visualize object lifecycles and state machines, making it easier to understand complex stateful systems.