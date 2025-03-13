UML Generation Modular Structure
============================

Overview
--------

The UML generation tools are designed with a modular architecture, with independent extractors for different diagram types. Each module is self-contained and can be used separately, with integration points in the main UML generator script.

Current Module Structure
-----------------------

.. code-block:: text

    utils/
    │
    ├── run_uml_generator.py              # Main script that calls all diagram generators
    │
    ├── extract_sequence.py               # CLI tool for sequence diagrams
    ├── extract_app_sequences.py          # Application-specific sequence extraction
    │
    ├── uml_generator/                    # Original UML generator (class diagrams)
    │   ├── __init__.py
    │   ├── cli.py
    │   ├── config.py
    │   ├── exceptions.py
    │   ├── factories.py
    │   ├── filesystem.py
    │   ├── interfaces.py
    │   ├── models.py
    │   ├── path_resolver.py
    │   ├── service.py
    │   ├── config/                       # Configuration handling
    │   ├── generator/                    # Diagram generators
    │   │   ├── plantuml_generator.py     # Class diagram generator
    │   │   └── sequence_generator.py     # YAML-based sequence generator
    │   ├── models/                       # Data models
    │   │   ├── models.py                 # Class diagram models
    │   │   └── sequence.py               # Sequence diagram models
    │   └── parsers/                      # Code parsers
    │
    └── sequence_extractor/               # Static analysis sequence extractor
        ├── __init__.py
        ├── analyzer.py                   # Sequence analyzer
        ├── generator.py                  # PlantUML generator
        └── models.py                     # Sequence diagram models

Proposed New Modules
-------------------

The implementation guides describe adding two new modules following the same pattern as the sequence extractor:

.. code-block:: text

    utils/
    │
    ├── activity_extractor/               # Activity diagram extractor (new)
    │   ├── __init__.py
    │   ├── analyzer.py                   # AST-based activity analyzer
    │   ├── generator.py                  # PlantUML generator for activities
    │   ├── models.py                     # Activity diagram models
    │   └── tests/                        # Tests for activity extractor
    │
    ├── state_extractor/                  # State diagram extractor (new)
    │   ├── __init__.py
    │   ├── analyzer.py                   # AST-based state analyzer
    │   ├── generator.py                  # PlantUML generator for states
    │   ├── models.py                     # State diagram models
    │   └── tests/                        # Tests for state extractor
    │
    ├── extract_activity.py               # CLI tool for activity diagrams
    └── extract_state.py                  # CLI tool for state diagrams

Module Design Principles
-----------------------

Each extractor module follows these design principles:

1. **Self-contained**: Each module includes everything needed for its specific diagram type.
2. **Consistent API**: All modules follow the same basic interface pattern.
3. **Independent operation**: Each module can be used directly without the others.
4. **Clean integration**: The modules integrate through the main UML generator script.

The typical module structure includes:

1. **Models**: Data structures specific to the diagram type
2. **Analyzer**: Code analysis logic to extract diagram elements
3. **Generator**: Converts models to PlantUML output format
4. **CLI**: Command-line interface for direct user access

Integration Points
-----------------

The modules integrate at two main points:

1. **run_uml_generator.py**: The main script imports and calls each extractor:

.. code-block:: python

    # Current integration of sequence extractor
    from utils.sequence_extractor.analyzer import SequenceAnalyzer
    from utils.sequence_extractor.generator import PlantUmlSequenceGenerator
    
    def generate_static_sequence_diagrams():
        analyzer = SequenceAnalyzer(app_dir)
        analyzer.analyze_directory()
        
        generator = PlantUmlSequenceGenerator()
        # ...generate diagrams...

    # Proposed integration of activity extractor
    from utils.activity_extractor import ActivityAnalyzer, PlantUmlActivityGenerator
    
    def generate_activity_diagrams(base_dir: Path, output_dir: Path):
        analyzer = ActivityAnalyzer(source_dir)
        analyzer.analyze_directory()
        
        generator = PlantUmlActivityGenerator()
        # ...generate diagrams...

2. **CLI tools**: Each module has its own CLI tool for direct usage:

.. code-block:: bash

    # Current CLI for sequence diagrams
    python -m utils.extract_sequence --dir backend/app --class UserService --method create_user
    
    # Proposed CLI for activity diagrams
    python -m utils.extract_activity --source ./utils --output ./docs/output --class MyClass --method my_method
    
    # Proposed CLI for state diagrams
    python -m utils.extract_state --source ./backend/app --output ./docs/output --class Document

Example: Using a Module Directly
------------------------------

Each extractor can be used directly in Python code:

.. code-block:: python

    # Using sequence extractor (current implementation)
    from utils.sequence_extractor.analyzer import SequenceAnalyzer
    from utils.sequence_extractor.generator import PlantUmlSequenceGenerator
    
    analyzer = SequenceAnalyzer("./backend/app")
    analyzer.analyze_directory()
    
    diagram = analyzer.generate_sequence_diagram("UserController", "create_user")
    
    generator = PlantUmlSequenceGenerator()
    generator.generate_file(diagram, "diagrams/create_user.puml")

Benefits of the Modular Approach
------------------------------

The modular design offers several advantages:

1. **Focused development**: Each diagram type can be developed independently
2. **Easier maintenance**: Changes to one extractor don't affect others
3. **Selective deployment**: Users can use only the diagram types they need
4. **Incremental adoption**: New diagram types can be added without modifying existing code
5. **Isolated testing**: Each module can be tested in isolation

Implementation Guidelines
------------------------

When adding new diagram types, follow these principles:

1. Create a new module with a consistent structure (models, analyzer, generator)
2. Implement a standalone CLI tool for direct access
3. Integrate with run_uml_generator.py 
4. Update documentation to include the new diagram type
5. Add tests for the new functionality

This modular architecture allows for easy extension with new diagram types while maintaining a clean, maintainable codebase.