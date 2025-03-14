UML Documentation Reorganization Plan
====================================

Current UML Documentation Structure
----------------------------------

The current UML documentation is spread across multiple files with some overlap and potential confusion:

.. code-block:: text

    docs/source/
    ├── uml_setup.rst                      # UML setup and dependencies
    ├── uml_diagrams.rst                   # UML class diagrams
    ├── uml_structure.rst                  # Directory structure
    ├── uml_extension.rst                  # Extension options
    ├── uml_sequence_implementation_guide.rst  # Sequence diagram implementation
    ├── uml_activity_implementation_guide.rst  # Activity diagram implementation
    ├── uml_state_implementation_guide.rst     # State diagram implementation
    ├── uml_state_implementation_diff.rst      # Diff for state diagrams
    ├── uml_modular_structure.rst          # Modular structure (original)
    ├── uml_modular_structure_updated.rst  # Modular structure (updated)
    ├── uml_diagram_outputs.rst            # Output structure
    ├── sequence_diagrams.rst              # Sequence diagrams
    └── sequence_diagram_usage.rst         # Sequence diagram usage guide

Proposed Reorganization
----------------------

I propose reorganizing the UML documentation into a clearer hierarchical structure:

.. code-block:: text

    docs/source/uml/                       # New subdirectory for all UML docs
    ├── index.rst                          # UML documentation overview
    ├── setup.rst                          # Setup and dependencies
    │
    ├── diagrams/                          # Diagram-specific documentation
    │   ├── index.rst                      # Overview of available diagrams
    │   ├── class_diagrams.rst             # Class diagrams
    │   ├── sequence_diagrams.rst          # Sequence diagrams
    │   ├── activity_diagrams.rst          # Activity diagrams
    │   └── state_diagrams.rst             # State diagrams
    │
    ├── architecture/                      # Architecture documentation
    │   ├── index.rst                      # Architecture overview
    │   ├── modular_structure.rst          # Modular architecture
    │   └── outputs.rst                    # Output structure
    │
    └── implementation/                    # Implementation guides
        ├── index.rst                      # Implementation overview
        ├── sequence_diagrams.rst          # Sequence diagram implementation
        ├── activity_diagrams.rst          # Activity diagram implementation
        └── state_diagrams.rst             # State diagram implementation

Steps to Implement Reorganization
-------------------------------

1. Create the new directory structure
2. Move and rename existing files
3. Update cross-references
4. Update the main index.rst

File Content and Mappings
-----------------------

uml/index.rst
^^^^^^^^^^^^^

A new overview page that introduces UML diagram generation in the project.

uml/setup.rst
^^^^^^^^^^^^^

Move content from the existing uml_setup.rst.

uml/diagrams/index.rst
^^^^^^^^^^^^^^^^^^^^^

Create an overview page that introduces the different diagram types.

uml/diagrams/class_diagrams.rst
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Move content from uml_diagrams.rst.

uml/diagrams/sequence_diagrams.rst
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Combine content from sequence_diagrams.rst and sequence_diagram_usage.rst.

uml/diagrams/activity_diagrams.rst
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

New file with examples of activity diagrams.

uml/diagrams/state_diagrams.rst
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

New file with examples of state diagrams.

uml/architecture/index.rst
^^^^^^^^^^^^^^^^^^^^^^^^

Overview of the UML generator architecture.

uml/architecture/modular_structure.rst
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use content from uml_modular_structure_updated.rst.

uml/architecture/outputs.rst
^^^^^^^^^^^^^^^^^^^^^^^^^^

Use content from uml_diagram_outputs.rst.

uml/implementation/index.rst
^^^^^^^^^^^^^^^^^^^^^^^^^^

Overview of implementation guides for adding diagram types.

uml/implementation/sequence_diagrams.rst
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Move content from uml_sequence_implementation_guide.rst.

uml/implementation/activity_diagrams.rst
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Move content from uml_activity_implementation_guide.rst.

uml/implementation/state_diagrams.rst
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Combine content from uml_state_implementation_guide.rst and uml_state_implementation_diff.rst.

Main Index Updates
----------------

The main index.rst file will need to be updated to point to the new UML structure:

.. code-block:: rst

    .. toctree::
       :maxdepth: 2
       :caption: Contents:
    
       overview
       sop
       architecture
       database
       backend/index
       frontend/index
       deployment
       development
       uml/index
       
Benefits of Reorganization
------------------------

1. **Clearer structure**: Hierarchical organization is easier to navigate
2. **Better separation of concerns**: Setup, diagram types, architecture, and implementation are distinct
3. **Simplified main index**: One entry point to all UML documentation
4. **Room for growth**: Easy to add new diagram types without cluttering the main index
5. **Improved cross-referencing**: Related documents are grouped together