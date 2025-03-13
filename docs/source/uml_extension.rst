UML Diagram Extensions
=====================

This document outlines how to extend the current UML generator to support additional diagram types.

Current Architecture
-------------------

Our current UML generation system has these main components:

- **Parsers**: Extract information from Python code (classes, methods, imports, etc.)
- **Generators**: Convert parsed code models into PlantUML syntax
- **Service**: Orchestrates the process of parsing and generating
- **Filesystem**: Handles reading source files and writing output files
- **Config**: Manages settings for parsers and generators

Extending to New Diagram Types
-----------------------------

The current system is designed for Class Diagrams, but we can extend it to support additional diagram types with the following approach:

1. Create New Generator Classes
------------------------------

For each diagram type, we would need to create a specialized generator:

.. code-block:: python

    # Example structure for a sequence diagram generator
    class SequenceDiagramGenerator(DiagramGenerator):
        def __init__(self, file_system, settings=None):
            super().__init__(file_system, settings)
            self.plantuml_start = "@startuml"
            self.plantuml_end = "@enduml"
            
        def generate_diagram(self, interaction_model, output_path):
            """Generate a sequence diagram from an interaction model."""
            uml_lines = [self.plantuml_start]
            
            # Generate participant definitions
            for participant in interaction_model.participants:
                uml_lines.append(f'participant "{participant.name}"')
            
            # Generate interaction arrows
            for interaction in interaction_model.interactions:
                uml_lines.append(f'{interaction.source} -> {interaction.target}: {interaction.message}')
                
            uml_lines.append(self.plantuml_end)
            content = "\n".join(uml_lines)
            
            self.file_system.write_file(output_path, content)

2. Create New Model Classes
--------------------------

Each diagram type needs specific model classes to represent its elements:

.. code-block:: python

    # Example models for sequence diagrams
    @dataclass
    class Participant:
        name: str
        type: str = "object"  # or "actor", "boundary", etc.

    @dataclass
    class Interaction:
        source: str
        target: str
        message: str
        is_async: bool = False
        is_return: bool = False

    @dataclass
    class SequenceModel:
        participants: list[Participant]
        interactions: list[Interaction]
        title: str = None

3. Create Configuration Extensions
--------------------------------

Extend the configuration system to support settings for new diagram types:

.. code-block:: python

    @dataclass
    class SequenceDiagramConfig:
        show_return_messages: bool = True
        show_activation: bool = True
        group_by_lifeline: bool = False

4. Implementation Strategy by Diagram Type
----------------------------------------

### 1. Sequence Diagrams

**Automatic Generation Approach**:

- Parse function call trees from code
- Analyze method invocations in code to track call sequences
- Generate sequence diagrams from call traces

**Manual Definition Approach**:

- Create a DSL (Domain Specific Language) or YAML format for defining sequences
- Allow developers to manually specify interactions
- Example:

.. code-block:: yaml

    sequence_diagram:
      title: User Authentication Flow
      participants:
        - name: Client
          type: actor
        - name: AuthController
          type: boundary
        - name: UserService
          type: control
        - name: Database
          type: entity
      interactions:
        - from: Client
          to: AuthController
          message: loginRequest(username, password)
        - from: AuthController
          to: UserService
          message: validateCredentials(username, password)
        - from: UserService
          to: Database
          message: findUserByUsername(username)
        # ...and so on

### 2. Component Diagrams

**Automatic Generation**:

- Analyze imports and dependencies between modules
- Map directories to components
- Generate component relationships based on import statements

.. code-block:: python

    def generate_component_diagram(project_root):
        components = {}
        dependencies = []
        
        # Traverse all Python files
        for py_file in find_all_py_files(project_root):
            module_name = get_module_name(py_file)
            component = get_component_for_module(module_name)
            components[component.name] = component
            
            # Extract imports
            for imported_module in extract_imports(py_file):
                imported_component = get_component_for_module(imported_module)
                dependencies.append((component.name, imported_component.name))
        
        # Generate PlantUML component diagram
        uml = ["@startuml"]
        for component in components.values():
            uml.append(f'[{component.name}] as {component.id}')
        
        for src, dest in dependencies:
            uml.append(f'{components[src].id} --> {components[dest].id}')
        
        uml.append("@enduml")
        return "\n".join(uml)

### 3. Package Diagrams

Similar to component diagrams but focused on Python packages:

.. code-block:: python

    def analyze_package_dependencies(project_root):
        packages = set()
        dependencies = []
        
        for py_file in find_all_py_files(project_root):
            package = get_package_name(py_file)
            packages.add(package)
            
            for imported_package in extract_imported_packages(py_file):
                if imported_package in packages:
                    dependencies.append((package, imported_package))
        
        return packages, dependencies

### 4. State Diagrams

These require more manual definition as state transitions often aren't explicit in code:

.. code-block:: python

    # Example state diagram definition
    @dataclass
    class State:
        name: str
        entry_actions: list[str] = field(default_factory=list)
        exit_actions: list[str] = field(default_factory=list)
        
    @dataclass
    class Transition:
        source: str  # state name
        target: str  # state name 
        trigger: str = None
        guard: str = None
        action: str = None

    @dataclass
    class StateMachine:
        name: str
        states: list[State]
        transitions: list[Transition]
        initial_state: str = None

Implementation Strategy
----------------------

A phased approach to implementing these diagram types:

1. **Phase 1: Framework Extensions**
   - Create base classes for new diagram types
   - Update the generator factory to support multiple diagram types
   - Extend the CLI to specify which diagram types to generate

2. **Phase 2: Package and Component Diagrams**
   - Start with these as they're most similar to our existing class diagrams
   - They can be automatically generated from static code analysis

3. **Phase 3: Sequence Diagrams**
   - Implement support for manually defined sequence diagrams
   - Create tools to extract sequence information from code where possible

4. **Phase 4: Activity and State Diagrams**
   - Add templates and generators for these more complex diagram types
   - Create annotation-based approach to mark states and transitions in code

5. **Phase 5: Use Case and Deployment Diagrams**
   - These are typically more documentation-oriented
   - Create a YAML-based definition format for these

Example Extension Implementation
-------------------------------

Here's how we could modify our main UML generator:

.. code-block:: python

    # In factories.py
    class ExtendedGeneratorFactory:
        def __init__(self, file_system, settings=None):
            self.file_system = file_system
            self.settings = settings or {}
            
        def create_generator(self, diagram_type):
            if diagram_type == "class":
                return PlantUmlGenerator(self.file_system, self.settings)
            elif diagram_type == "sequence":
                return SequenceDiagramGenerator(self.file_system, self.settings)
            elif diagram_type == "component":
                return ComponentDiagramGenerator(self.file_system, self.settings)
            elif diagram_type == "package":
                return PackageDiagramGenerator(self.file_system, self.settings)
            # ...other diagram types
            else:
                raise ValueError(f"Unsupported diagram type: {diagram_type}")

Command-line Interface Updates:

.. code-block:: python

    # In cli.py
    parser.add_argument(
        "--diagram-type",
        choices=["class", "sequence", "component", "package", "activity", "state", "usecase", "deployment"],
        default="class",
        help="Type of diagram to generate",
    )

Example manual diagram definition file (``auth_sequence.yaml``):

.. code-block:: yaml

    diagram:
      type: sequence
      title: Authentication Flow
      participants:
        - name: User
          type: actor
        - name: AuthController
        - name: UserService
        - name: Database
      interactions:
        - from: User
          to: AuthController
          message: "login(credentials)"
        - from: AuthController
          to: UserService
          message: "authenticate(username, password)"
        - from: UserService
          to: Database
          message: "findUser(username)"
        - from: Database
          to: UserService
          message: "User or null"
          return: true
        - from: UserService
          to: AuthController
          message: "AuthResult"
          return: true
        - from: AuthController
          to: User
          message: "JWT Token / Error"
          return: true

Then we could create a command to generate diagrams from these definition files:

.. code-block:: bash

    python -m uml_generator.cli generate-from-definition --file auth_sequence.yaml --output auth_flow.puml

Implementation Progress
---------------------

We have successfully implemented both approaches for sequence diagram generation:

1. **YAML Definition Approach (Completed)**
   - Implemented models in `utils/uml_generator/models/sequence.py` 
   - Created generator in `utils/uml_generator/generator/sequence_generator.py`
   - Added factory support and CLI commands
   - YAML diagrams are generated automatically via `run_uml_generator.py`

2. **Static Code Analysis Approach (Completed)**
   - Created `utils/sequence_extractor/` with analyzer, models, and generator
   - Implemented CLI tool in `utils/extract_sequence.py`
   - Integrated into main workflow in `utils/run_uml_generator.py`
   - Can automatically extract sequence diagrams from Python code

Both approaches are now functional and integrated into the UML generator system. Diagrams are generated in the `docs/source/_generated_uml/sequence/` directory.

**Known Issues**: When running the UML generator, you may see error messages about parameter mismatches like `AttributeModel.__init__() got an unexpected keyword argument 'default_value'`. These occur when the UML generator tries to analyze our sequence diagram implementation code itself. These errors do not prevent the sequence diagrams from being generated correctly.

Conclusion
----------

The current UML generator provides a solid foundation we can extend to support multiple diagram types. We have successfully implemented:

1. Package and Component diagrams which can be automatically generated from code analysis
2. Sequence diagrams with both YAML definition and static code analysis approaches

For future work, we could enhance the static analyzer with better type inference and variable tracking to automatically detect more complex relationships between classes.

Both approaches now work together in the same workflow and produce diagrams in the standard PlantUML format, making them easy to include in documentation.