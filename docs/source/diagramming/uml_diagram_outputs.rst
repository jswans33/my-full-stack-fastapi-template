UML Diagram Output Structure
========================

This document outlines the directory structure where all generated UML diagrams are stored.

Output Directory Structure
-------------------------

All UML diagrams are generated within the `docs/source/_generated_uml/` directory with specific subdirectories for each diagram type:

.. code-block:: text

    docs/source/
    └── _generated_uml/              # Main UML output directory
        ├── index.rst                # Auto-generated index of all diagrams
        ├── all.puml                 # Combined class diagrams
        │
        ├── sequence/                # Sequence diagrams
        │   ├── auth_flow.puml       # Example YAML-based sequence diagram
        │   ├── UserService_create_user.puml  # Example code-based sequence
        │   └── ...
        │
        ├── activity/                # Activity diagrams (when implemented)
        │   ├── SequenceAnalyzer_generate_sequence_diagram_activity.puml
        │   ├── OrderProcessor_process_order_activity.puml
        │   └── ...
        │
        ├── state/                   # State diagrams (when implemented)
        │   ├── Document_state.puml
        │   ├── Order_state.puml
        │   └── ...
        │
        └── uml_generator/           # UML generator specific diagrams
            ├── factories.puml
            ├── models.puml
            └── ...

Generation Process
-----------------

1. **Class Diagrams** are generated directly in the main output directory
   - Source: Python code in the project
   - Output: `docs/source/_generated_uml/all.puml`

2. **Sequence Diagrams** are generated from two sources:
   - YAML definitions in `examples/sequence_diagrams/`
   - Static code analysis using `utils/sequence_extractor/`
   - Output: `docs/source/_generated_uml/sequence/*.puml`

3. **Activity Diagrams** (when implemented):
   - Source: Static code analysis using `utils/activity_extractor/`
   - Output: `docs/source/_generated_uml/activity/*.puml`

4. **State Diagrams** (when implemented):
   - Source: Static code analysis using `utils/state_extractor/`
   - Output: `docs/source/_generated_uml/state/*.puml`

Integration with Documentation
-----------------------------

The generated diagrams are referenced in RST documentation files like:

.. code-block:: rst

    Class Diagrams
    -------------
    
    .. uml:: ../_generated_uml/all.puml
    
    Sequence Diagrams
    ---------------
    
    .. uml:: ../_generated_uml/sequence/auth_flow.puml
    
    Activity Diagrams
    --------------
    
    .. uml:: ../_generated_uml/activity/OrderProcessor_process_order_activity.puml
    
    State Diagrams
    -----------
    
    .. uml:: ../_generated_uml/state/Document_state.puml

Running the Generator
-------------------

To generate all UML diagrams:

.. code-block:: bash

    python -m utils.run_uml_generator

To generate specific diagram types directly:

.. code-block:: bash

    # Sequence diagrams
    python -m utils.extract_sequence --dir backend/app --class UserService --method create_user
    
    # Activity diagrams (when implemented)
    python -m utils.extract_activity --source ./utils --output ./docs/source/_generated_uml/activity --class SequenceAnalyzer --method generate_sequence_diagram
    
    # State diagrams (when implemented)
    python -m utils.extract_state --source ./backend/app --output ./docs/source/_generated_uml/state --class Document