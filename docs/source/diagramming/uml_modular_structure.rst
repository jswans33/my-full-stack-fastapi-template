UML Generation Modular Structure
============================

Overview
--------

The UML generation tools are designed with a modular architecture, with independent extractors for different diagram types. Each module is self-contained and can be used separately, with integration points in the main UML generator script.

Module Structure
---------------

.. code-block:: text

    utils/
    │
    ├── run_uml_generator.py     # Main script that calls all diagram generators
    │
    ├── uml_generator/           # Original UML generator (class diagrams)
    │   ├── __init__.py
    │   ├── interfaces.py
    │   ├── filesystem.py
    │   ├── factories.py
    │   ├── service.py
    │   ├── generator/
    │   └── models/
    │
    ├── sequence_extractor/      # Sequence diagram extractor (existing)
    │   ├── __init__.py
    │   ├── analyzer.py
    │   ├── generator.py
    │   └── models.py
    │
    ├── activity_extractor/      # Activity diagram extractor (new module)
    │   ├── __init__.py
    │   ├── analyzer.py
    │   ├── generator.py
    │   ├── models.py
    │   └── tests/
    │
    ├── state_extractor/         # State diagram extractor (new module)
    │   ├── __init__.py
    │   ├── analyzer.py
    │   ├── generator.py
    │   ├── models.py
    │   └── tests/
    │
    ├── extract_sequence.py      # CLI tool for sequence diagrams
    ├── extract_activity.py      # CLI tool for activity diagrams
    └── extract_state.py         # CLI tool for state diagrams

Each module follows the same pattern:

1. **Models** - Data structures specific to that diagram type
2. **Analyzer** - AST-based code analysis for extracting diagram elements
3. **Generator** - Converts models to PlantUML output
4. **CLI utilities** - Direct command-line access to the extractors

Integration Points
-----------------

The modules are independent but integrate at two points:

1. **run_uml_generator.py** - Imports and calls the generators from each module
2. **Documentation** - All diagram outputs are combined in the documentation

Example: Using a Specific Extractor
----------------------------------

Each extractor can be used directly, without involving the other modules:

.. code-block:: python

    # Using just the activity diagram extractor
    from utils.activity_extractor import ActivityAnalyzer, PlantUmlActivityGenerator
    
    analyzer = ActivityAnalyzer("./utils")
    analyzer.analyze_directory()
    
    diagram = analyzer.generate_activity_diagram("ClassName", "methodName")
    
    generator = PlantUmlActivityGenerator()
    generator.generate_file(diagram, "output.puml")

Module Independence
------------------

The modular design offers several advantages:

1. **Separation of concerns** - Each diagram type has its own extraction logic
2. **Maintainability** - Changes to one extractor don't affect others
3. **Testing isolation** - Each module can be tested independently
4. **Deployment flexibility** - Extractors can be run individually or together

Implementation Guidelines
------------------------

When adding new diagram types, follow these principles:

1. Create a new module with a consistent structure (models, analyzer, generator)
2. Implement a standalone CLI tool for direct access
3. Integrate with run_uml_generator.py 
4. Update documentation to include the new diagram type

This modular architecture allows for easy extension with new diagram types while maintaining a clean codebase.