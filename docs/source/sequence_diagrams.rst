Sequence Diagram Implementation
===========================

This document explains the implementation of sequence diagram generation in the UML generator.

Overview
--------

Two approaches have been implemented for generating sequence diagrams:

1. **YAML Definition-Based**: Define sequence diagrams explicitly in YAML files
2. **Static Code Analysis-Based**: Extract sequence diagrams from Python code

Both approaches generate PlantUML sequence diagrams that show interactions between objects over time.

YAML Definition Approach
-----------------------

The YAML definition approach allows you to create detailed sequence diagrams by explicitly defining all participants and interactions.

**Implementation Components:**

* ``models/sequence.py``: Data models for sequence diagram elements
* ``generator/sequence_generator.py``: Converts sequence models to PlantUML syntax
* Command-line interface in ``cli.py`` for generating from YAML
* Examples in ``examples/sequence_diagrams/``

**How to Use:**

1. Create a YAML file in the examples/sequence_diagrams/ directory
2. Run the UML generator: ``python -m utils.run_uml_generator``
3. Or use the CLI directly: ``python -m utils.uml_generator.cli generate-sequence -f examples/sequence_diagrams/auth_flow.yaml -o output.puml``

**Example YAML:**

.. code-block:: yaml

    title: User Authentication Flow
    participants:
      - name: User
        type: actor
      - name: AuthController
        type: boundary
      - name: UserService
        type: control
    items:
      - type: message
        from: User
        to: AuthController
        text: "login(credentials)"

Static Code Analysis Approach
----------------------------

The static code analysis approach extracts sequence diagrams directly from Python code by analyzing method calls.

**Implementation Components:**

* ``sequence_extractor/models.py``: Models representing sequence elements
* ``sequence_extractor/analyzer.py``: AST-based code analyzer that extracts method calls
* ``sequence_extractor/generator.py``: Converts sequence models to PlantUML
* ``extract_sequence.py``: Command-line tool for extracting diagrams from code
* Example code in ``examples/sequence_example.py``

**How to Use:**

.. code-block:: bash

    # Basic usage
    python -m utils.extract_sequence --dir path/to/code --class ClassName --method methodName

    # With output specification
    python -m utils.extract_sequence --dir examples --class UserService --method create_user --output diagrams/user_service.puml

**Example of Enhanced Extraction:**

For more complex code bases, custom extraction scripts can be created, as shown in ``examples/extract_user_sequence.py``, which enhances the automatically extracted diagram with additional known relationships.

Limitations and Future Work
--------------------------

**Current Limitations:**

1. **Static Analysis Limitations**:
   * Only detects direct method calls (may miss instance variable method calls)
   * Doesn't track object types across assignments
   * Limited inference of actual class types

2. **YAML Definition Limitations**:
   * Manual creation can be time-consuming
   * Requires in-depth knowledge of the system

**Future Enhancements:**

1. **Improved Static Analysis**:
   * Better type inference for variables
   * Tracking object creation and method calls through variables
   * Support for inheritance and polymorphism

2. **Hybrid Approach**:
   * Combine automatic analysis with manual annotations
   * Allow partial sequence definitions that get augmented with analysis

3. **Integration with Debugging**:
   * Runtime tracing for capturing actual call sequences
   * Integration with profiling tools

Both approaches offer valuable ways to document system interactions. The YAML approach provides precise control over diagrams, while the static analysis offers more automation but may require enhancement for complex code bases.