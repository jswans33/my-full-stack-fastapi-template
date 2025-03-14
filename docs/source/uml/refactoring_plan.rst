UML Generator Refactoring Plan
==========================

This document outlines the refactoring plan for the UML generator code to create a unified structure for all diagram types, including the existing class and sequence diagrams, and the planned activity and state diagrams.

Current Structure Analysis
-------------------------

The current UML generation code is spread across two main directories:

1. ``utils/uml_generator/`` - A well-structured package for class diagrams with:
   - Models, parsers, generators
   - Configuration handling
   - CLI interface
   - File system operations
   - Factory pattern implementation

2. ``utils/sequence_extractor/`` - A simpler structure for sequence diagrams with:
   - Models for sequence diagrams
   - Analyzer for extracting sequence information
   - Generator for PlantUML output

This separation creates duplication and makes it harder to maintain a consistent approach across diagram types.

Refactoring Goals
----------------

1. Create a unified, extensible architecture for all UML diagram types
2. Eliminate code duplication
3. Standardize interfaces and patterns
4. Prepare the codebase for adding activity and state diagrams
5. Improve maintainability and testability

Proposed Directory Structure
---------------------------

.. code-block:: text

    utils/
    ├── uml/                           # Main UML package
    │   ├── __init__.py                # Package initialization
    │   ├── cli.py                     # Command-line interface
    │   ├── config/                    # Configuration handling
    │   │   ├── __init__.py
    │   │   └── loader.py
    │   ├── core/                      # Core functionality
    │   │   ├── __init__.py
    │   │   ├── exceptions.py          # Exception classes
    │   │   ├── filesystem.py          # File system operations
    │   │   ├── interfaces.py          # Abstract interfaces
    │   │   └── service.py             # Core service logic
    │   ├── diagrams/                  # Diagram-specific code
    │   │   ├── __init__.py
    │   │   ├── base.py                # Base classes for diagrams
    │   │   ├── class_diagram/         # Class diagram specific code
    │   │   │   ├── __init__.py
    │   │   │   ├── models.py
    │   │   │   ├── analyzer.py
    │   │   │   └── generator.py
    │   │   ├── sequence_diagram/      # Sequence diagram specific code
    │   │   │   ├── __init__.py
    │   │   │   ├── models.py
    │   │   │   ├── analyzer.py
    │   │   │   └── generator.py
    │   │   ├── activity_diagram/      # Activity diagram specific code (future)
    │   │   │   ├── __init__.py
    │   │   │   ├── models.py
    │   │   │   ├── analyzer.py
    │   │   │   └── generator.py
    │   │   └── state_diagram/         # State diagram specific code (future)
    │   │       ├── __init__.py
    │   │       ├── models.py
    │   │       ├── analyzer.py
    │   │       └── generator.py
    │   ├── factories.py               # Factory classes
    │   ├── run.py                     # Main entry point
    │   └── utils/                     # Utility functions
    │       ├── __init__.py
    │       └── path_resolver.py
    ├── extract_class.py               # CLI script for class diagrams
    ├── extract_sequence.py            # CLI script for sequence diagrams
    ├── extract_activity.py            # CLI script for activity diagrams (future)
    ├── extract_state.py               # CLI script for state diagrams (future)
    └── run_uml_generator.py           # Main script to run all generators

Refactoring Steps
----------------

Phase 1: Restructure Existing Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create the new directory structure
2. Move and refactor the class diagram code from ``utils/uml_generator/``
3. Move and refactor the sequence diagram code from ``utils/sequence_extractor/``
4. Create unified interfaces and base classes
5. Update imports and references

Phase 2: Standardize Interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create a consistent interface for all diagram types:
   - Models
   - Analyzers
   - Generators

2. Standardize the factory pattern for all diagram types

3. Create a unified configuration system

Phase 3: Update CLI and Entry Points
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Update the main ``run_uml_generator.py`` script
2. Create/update individual extraction scripts
3. Ensure backward compatibility

Phase 4: Prepare for New Diagram Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create placeholder directories and files for activity and state diagrams
2. Define interfaces and base classes for new diagram types
3. Update factories to support new diagram types

Detailed Implementation Plan
--------------------------

Step 1: Create New Directory Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Create main directories
    mkdir -p utils/uml/config
    mkdir -p utils/uml/core
    mkdir -p utils/uml/diagrams/base
    mkdir -p utils/uml/diagrams/class_diagram
    mkdir -p utils/uml/diagrams/sequence_diagram
    mkdir -p utils/uml/diagrams/activity_diagram
    mkdir -p utils/uml/diagrams/state_diagram
    mkdir -p utils/uml/utils

Step 2: Move Class Diagram Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Move models:
   - Move ``utils/uml_generator/models.py`` to ``utils/uml/diagrams/class_diagram/models.py``
   - Update imports and references

2. Move parsers:
   - Move ``utils/uml_generator/parsers/`` to ``utils/uml/diagrams/class_diagram/analyzer.py``
   - Update imports and references

3. Move generators:
   - Move ``utils/uml_generator/generator/plantuml_generator.py`` to ``utils/uml/diagrams/class_diagram/generator.py``
   - Update imports and references

Step 3: Move Sequence Diagram Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Move models:
   - Move ``utils/sequence_extractor/models.py`` to ``utils/uml/diagrams/sequence_diagram/models.py``
   - Update imports and references

2. Move analyzer:
   - Move ``utils/sequence_extractor/analyzer.py`` to ``utils/uml/diagrams/sequence_diagram/analyzer.py``
   - Update imports and references

3. Move generator:
   - Move ``utils/sequence_extractor/generator.py`` to ``utils/uml/diagrams/sequence_diagram/generator.py``
   - Update imports and references

Step 4: Create Unified Interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create base interfaces in ``utils/uml/core/interfaces.py``:
   - ``DiagramModel``
   - ``DiagramAnalyzer``
   - ``DiagramGenerator``

2. Create base classes in ``utils/uml/diagrams/base.py``:
   - ``BaseDiagramModel``
   - ``BaseDiagramAnalyzer``
   - ``BaseDiagramGenerator``

3. Update existing classes to implement these interfaces

Step 5: Update Factory Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create a unified factory in ``utils/uml/factories.py``:
   - ``DiagramFactory`` - Creates appropriate analyzers and generators

2. Update existing factories to use the new structure

Step 6: Update CLI and Entry Points
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Update ``utils/run_uml_generator.py`` to use the new structure
2. Create/update individual extraction scripts:
   - ``utils/extract_class.py``
   - ``utils/extract_sequence.py``

Step 7: Prepare for Activity and State Diagrams
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create placeholder files for activity diagrams:
   - ``utils/uml/diagrams/activity_diagram/models.py``
   - ``utils/uml/diagrams/activity_diagram/analyzer.py``
   - ``utils/uml/diagrams/activity_diagram/generator.py``

2. Create placeholder files for state diagrams:
   - ``utils/uml/diagrams/state_diagram/models.py``
   - ``utils/uml/diagrams/state_diagram/analyzer.py``
   - ``utils/uml/diagrams/state_diagram/generator.py``

3. Update factories to support new diagram types

Implementation Timeline
---------------------

1: Restructure and Move Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  1-2: Create new directory structure and move class diagram code
-  3-4: Move sequence diagram code
-  5: Create unified interfaces and base classes

2: Update and Test
~~~~~~~~~~~~~~~~~~~~

-  1-2: Update factory pattern and CLI
-  3-4: Test and fix issues
-  5: Create placeholder files for new diagram types

3: Documentation and Final Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  1-2: Update documentation
-  3-4: Comprehensive testing
-  5: Final review and cleanup

Benefits of Refactoring
---------------------

1. **Improved Maintainability**: Consistent structure across all diagram types
2. **Reduced Duplication**: Shared code and interfaces
3. **Better Extensibility**: Easy to add new diagram types
4. **Clearer Organization**: Logical grouping of related functionality
5. **Enhanced Testability**: Cleaner interfaces make testing easier

After completing this refactoring, implementing the activity and state diagrams will be much more straightforward as they can follow the established patterns and interfaces.