Class Diagrams
=============

The UML generator creates class diagrams for Python code, showing classes, methods, attributes and relationships.

.. uml:: ../../_generated_uml/all.puml

UML Generator Structure
---------------------

The UML generator tool itself is analyzed and visualized:

.. uml:: ../../_generated_uml/uml_generator/models.puml

.. uml:: ../../_generated_uml/uml_generator/generator/plantuml_generator.puml

Creating Class Diagrams
---------------------

Class diagrams show the static structure of a system, including:

* Classes with their attributes and methods
* Relationships between classes (inheritance, association, etc.)
* Interfaces and their implementations

To generate class diagrams:

.. code-block:: bash

   # Generate class diagrams for all Python files in a directory
   python -m utils.run_uml_generator --dir path/to/directory

   # Generate a class diagram for a specific file
   python -m utils.run_uml_generator --file path/to/file.py

The generator analyzes the Python code and extracts:

* Class definitions and hierarchies
* Methods and their parameters
* Class attributes and properties
* Relationships between classes

Customizing Class Diagrams
------------------------

You can customize the generated diagrams by:

1. Adding PlantUML directives in code comments
2. Creating a configuration file
3. Using command-line options

Example of adding directives in code:

.. code-block:: python

   class User:
       """
       Represents a user in the system.
       
       @uml.note: This is a core domain entity
       @uml.color: #85BBF0
       """
       # ...