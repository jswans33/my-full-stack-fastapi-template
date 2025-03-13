Sequence Diagram Generation Guide
============================

This guide explains how to use the sequence diagram generation capabilities of the UML generator. The system offers two complementary approaches to create sequence diagrams:

1. **YAML Definition-Based**: Define sequence diagrams explicitly using YAML
2. **Static Code Analysis-Based**: Extract sequence diagrams automatically from Python code

Both approaches generate standard PlantUML sequence diagrams that can be included in your documentation.

Quick Start
----------

**Run everything at once**:

.. code-block:: bash

    python -m utils.run_uml_generator

This generates all UML diagrams including class diagrams and sequence diagrams.

**Generate sequence diagrams specifically for backend/app**:

.. code-block:: bash

    python -m utils.extract_app_sequences

This analyzes the FastAPI routes in backend/app and generates sequence diagrams for key endpoints.

YAML Definition Approach
-----------------------

The YAML-based approach gives you precise control over the content and layout of your sequence diagrams.

Creating a YAML Definition
~~~~~~~~~~~~~~~~~~~~~~~~~

Create a YAML file in the ``examples/sequence_diagrams/`` directory:

.. code-block:: yaml

    title: User Authentication Flow
    hide_footboxes: true
    autonumber: true
    
    participants:
      - name: Client
        type: actor
      - name: AuthController 
        type: boundary
      - name: UserService
        type: control
      - name: Database
        type: database
    
    items:
      - type: message
        from: Client
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
        text: "return user"
        arrow_style: -->

YAML Structure
~~~~~~~~~~~~~

- **title**: Diagram title
- **participants**: Array of objects in the sequence
  - **name**: Display name
  - **type**: actor, boundary, control, entity, database, etc.
  - **alias** (optional): Short name to use in interactions
- **items**: Array of interactions
  - **type**: message, activate, deactivate, alt, opt, loop, etc.
  - **from/to**: Participant names for messages
  - **text**: Message content
  - **arrow_style** (optional): ->, ->>, -->, etc.

Running the Generator
~~~~~~~~~~~~~~~~~~~

YAML-based sequence diagrams are automatically generated when you run:

.. code-block:: bash

    python -m utils.run_uml_generator

Or you can generate a specific diagram:

.. code-block:: bash

    python -m utils.uml_generator.cli generate-sequence \
        --file examples/sequence_diagrams/auth_flow.yaml \
        --output docs/source/_generated_uml/sequence/auth_flow.puml

Static Code Analysis Approach
---------------------------

The static analysis approach extracts sequence diagrams directly from your Python code by analyzing method calls and dependencies.

Extracting From FastAPI Routes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To extract sequence diagrams from your FastAPI application's routes:

.. code-block:: bash

    # Run the dedicated script for backend/app
    python -m utils.extract_app_sequences

This script:

1. Identifies key API endpoints in your application
2. Analyzes each endpoint to trace function calls
3. Generates sequence diagrams showing the interaction flow
4. Saves diagrams to ``docs/source/_generated_uml/sequence/``

Key endpoints analyzed include:

- Authentication flows (login, token verification)
- User management (signup, profile updates, password changes)
- Item operations (create, update, delete)
- And more

Extracting Custom Sequences
~~~~~~~~~~~~~~~~~~~~~~~~~

For custom sequence extraction from any class or function:

.. code-block:: bash

    # For FastAPI router functions
    python -m utils.extract_sequence \
        --dir backend/app \
        --module api.routes.login \
        --function login_access_token \
        --output docs/source/_generated_uml/sequence/login_flow.puml
    
    # For class methods
    python -m utils.extract_sequence \
        --dir backend/app \
        --class UserService \
        --method create_user \
        --output docs/source/_generated_uml/sequence/create_user_service.puml

How Static Analysis Works
~~~~~~~~~~~~~~~~~~~~~~~

The sequence extractor:

1. Analyzes Python source code to identify classes and methods
2. Traces method calls to build a call graph
3. Follows the execution flow starting from an entry point
4. Generates a sequence diagram showing the interactions

Including in Documentation
------------------------

To include sequence diagrams in your Sphinx documentation:

.. code-block:: rst

    Sequence Diagram
    ~~~~~~~~~~~~~~~
    
    .. uml:: _generated_uml/sequence/auth_flow.puml

Or for automatically generated diagrams:

.. code-block:: rst

    User Creation Flow
    ~~~~~~~~~~~~~~~~~
    
    .. uml:: _generated_uml/sequence/user_signup.puml

Troubleshooting
-------------

**Problem**: No sequence diagrams are generated

**Solution**: Ensure you have:
- Created YAML files in ``examples/sequence_diagrams/``
- Or run ``python -m utils.extract_app_sequences`` for code analysis

**Problem**: Static analysis misses some method calls

**Solution**: Static analysis has limitations. For complete diagrams:
- Use the YAML approach for critical sequences
- Enhance ``utils/extract_app_sequences.py`` with additional entry points

**Problem**: Errors when running the UML generator

**Solution**: Errors like ``AttributeModel.__init__() got an unexpected keyword argument`` are related to the UML generator trying to analyze the sequence diagram code itself. These don't prevent diagrams from being generated correctly.

Advanced Usage
------------

Customizing Sequence Extraction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Edit ``utils/extract_app_sequences.py`` to change which endpoints are analyzed:

.. code-block:: python

    ENTRY_POINTS = [
        # Add your endpoints here
        ("module_name", "function_name", "output_filename"),
    ]

Testing the Implementation
~~~~~~~~~~~~~~~~~~~~~~~

Use the provided test scripts to verify everything works:

**Windows**:

.. code-block:: batch

    .\test_sequence_diagrams.bat

**Unix/Linux/macOS**:

.. code-block:: bash

    chmod +x test_sequence_diagrams.sh
    ./test_sequence_diagrams.sh

These scripts test both YAML-based and code analysis-based approaches.

Integration with Main UML Generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``utils/run_uml_generator.py`` script has been updated to:

1. Process YAML files in examples/sequence_diagrams/
2. Run the extract_app_sequences.py script
3. Include all sequence diagrams in the documentation

This ensures that sequence diagrams are automatically generated whenever you run the UML generator.