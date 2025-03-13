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

Next Steps: Activity and State Diagram Extractors
-----------------------------------------------

Following the same approach as the sequence diagram extractor, we will develop code analyzers for activity and state diagrams. These will use static analysis to extract flow control and state transitions from Python code.

Activity Diagram Extractor
-------------------------

The activity diagram extractor will analyze function control flow to generate diagrams that show how code executes through different paths:

**Folder Structure**:
```
utils/activity_extractor/
  ├── __init__.py
  ├── analyzer.py
  ├── generator.py
  └── models.py
```

**Models (models.py)**:

.. code-block:: python

    """Data models for activity diagram extraction."""
    
    from dataclasses import dataclass, field
    from enum import Enum
    from typing import Dict, List, Optional, Set
    
    
    class NodeType(Enum):
        """Types of nodes in an activity diagram."""
        
        START = "start"
        END = "end"
        ACTIVITY = "activity"
        DECISION = "decision"
        MERGE = "merge"
        FORK = "fork"
        JOIN = "join"
    
    
    @dataclass
    class ActivityNode:
        """Represents a node in an activity diagram."""
        
        id: str
        type: NodeType
        name: str = ""
        function_name: Optional[str] = None
        line_number: int = 0
        
        # For decision nodes
        condition: Optional[str] = None
        
        def __hash__(self):
            return hash(self.id)
    
    
    @dataclass
    class ActivityEdge:
        """Represents an edge between activity nodes."""
        
        source_id: str
        target_id: str
        label: Optional[str] = None
        guard: Optional[str] = None  # Condition for decision branches
        
        def __hash__(self):
            return hash((self.source_id, self.target_id))
    
    
    @dataclass
    class ActivityDiagram:
        """Represents an activity diagram."""
        
        title: str
        nodes: Set[ActivityNode] = field(default_factory=set)
        edges: Set[ActivityEdge] = field(default_factory=set)
        swimlanes: Dict[str, List[str]] = field(default_factory=dict)  # className -> [nodeIds]
        
        def add_node(self, node: ActivityNode) -> None:
            """Add a node to the diagram."""
            self.nodes.add(node)
        
        def add_edge(self, edge: ActivityEdge) -> None:
            """Add an edge to the diagram."""
            self.edges.add(edge)
        
        def add_to_swimlane(self, class_name: str, node_id: str) -> None:
            """Add a node to a swimlane."""
            if class_name not in self.swimlanes:
                self.swimlanes[class_name] = []
            
            if node_id not in self.swimlanes[class_name]:
                self.swimlanes[class_name].append(node_id)
    
    
    @dataclass
    class ControlFlowInfo:
        """Information about control flow in a function."""
        
        # Map from line number to node ID
        line_to_node: Dict[int, str] = field(default_factory=dict)
        
        # Decision nodes with their condition
        decisions: Dict[str, str] = field(default_factory=dict)
        
        # Guard conditions for edges
        edge_guards: Dict[tuple[str, str], str] = field(default_factory=dict)

**Analyzer (analyzer.py)**:

.. code-block:: python

    """Analyzer for extracting activity diagrams from Python code."""
    
    import ast
    import os
    from pathlib import Path
    from typing import Dict, List, Optional, Set, Tuple
    
    from .models import (
        ActivityDiagram,
        ActivityEdge,
        ActivityNode,
        ControlFlowInfo,
        NodeType,
    )
    
    
    class FunctionControlFlowVisitor(ast.NodeVisitor):
        """AST visitor that extracts control flow from a Python function."""
        
        def __init__(self, function_name: str, class_name: Optional[str] = None):
            self.function_name = function_name
            self.class_name = class_name
            self.nodes: Set[ActivityNode] = set()
            self.edges: Set[ActivityEdge] = set()
            self.node_count = 0
            self.control_flow = ControlFlowInfo()
            
            # Create start node
            self.start_node = self._create_node(
                NodeType.START, "Start", function_name=function_name
            )
            self.current_node = self.start_node
            
            # Special node for function exit
            self.end_node = self._create_node(
                NodeType.END, "End", function_name=function_name
            )
        
        def _create_node(
            self,
            node_type: NodeType,
            name: str,
            line_number: int = 0,
            function_name: Optional[str] = None,
            condition: Optional[str] = None,
        ) -> ActivityNode:
            """Create a new activity node with a unique ID."""
            node_id = f"node_{self.node_count}"
            self.node_count += 1
            
            node = ActivityNode(
                id=node_id,
                type=node_type,
                name=name,
                line_number=line_number,
                function_name=function_name,
                condition=condition,
            )
            
            self.nodes.add(node)
            
            if line_number > 0:
                self.control_flow.line_to_node[line_number] = node_id
            
            return node
        
        def _add_edge(
            self,
            source: ActivityNode,
            target: ActivityNode,
            label: Optional[str] = None,
            guard: Optional[str] = None,
        ) -> None:
            """Add an edge between two nodes."""
            edge = ActivityEdge(
                source_id=source.id,
                target_id=target.id,
                label=label,
                guard=guard,
            )
            
            self.edges.add(edge)
            
            if guard:
                self.control_flow.edge_guards[(source.id, target.id)] = guard
        
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            """Visit a function definition node."""
            # Create an activity node for the function
            function_node = self._create_node(
                NodeType.ACTIVITY,
                f"Function: {node.name}",
                node.lineno,
                function_name=node.name,
            )
            
            # Connect start node to function node
            self._add_edge(self.start_node, function_node)
            
            # Set current node
            self.current_node = function_node
            
            # Visit the function body
            for item in node.body:
                self.visit(item)
            
            # Connect last node to end node if not already connected
            if self.current_node != self.end_node:
                self._add_edge(self.current_node, self.end_node)
        
        def visit_If(self, node: ast.If) -> None:
            """Visit an if statement node."""
            line_number = node.lineno
            
            # Get the condition as a string
            condition = ast.unparse(node.test).strip()
            
            # Create a decision node
            decision_node = self._create_node(
                NodeType.DECISION,
                f"If: {condition}",
                line_number,
                function_name=self.function_name,
                condition=condition,
            )
            
            # Store the condition for this decision
            self.control_flow.decisions[decision_node.id] = condition
            
            # Connect current node to decision node
            self._add_edge(self.current_node, decision_node)
            
            # Remember the original current node to continue after if block
            prev_node = self.current_node
            
            # Set decision as current node
            self.current_node = decision_node
            
            # Create a merge node for after the if statement
            merge_node = self._create_node(
                NodeType.MERGE, "Merge", function_name=self.function_name
            )
            
            # Process the 'if' body
            self.current_node = decision_node
            for item in node.body:
                self.visit(item)
            
            # Connect last node in 'if' body to merge node
            self._add_edge(self.current_node, merge_node, guard="True")
            
            # Process the 'else' body if it exists
            if node.orelse:
                self.current_node = decision_node
                for item in node.orelse:
                    self.visit(item)
                
                # Connect last node in 'else' body to merge node
                self._add_edge(self.current_node, merge_node, guard="False")
            else:
                # If no else clause, connect decision directly to merge with False guard
                self._add_edge(decision_node, merge_node, guard="False")
            
            # Set merge as current node
            self.current_node = merge_node
        
        def visit_For(self, node: ast.For) -> None:
            """Visit a for loop node."""
            line_number = node.lineno
            
            # Get the loop condition as a string
            target = ast.unparse(node.target).strip()
            iter_expr = ast.unparse(node.iter).strip()
            condition = f"{target} in {iter_expr}"
            
            # Create a decision node for the loop condition
            decision_node = self._create_node(
                NodeType.DECISION,
                f"For: {condition}",
                line_number,
                function_name=self.function_name,
                condition=condition,
            )
            
            # Connect current node to decision node
            self._add_edge(self.current_node, decision_node)
            
            # Set decision as current node
            self.current_node = decision_node
            
            # Process the loop body
            for item in node.body:
                self.visit(item)
            
            # Connect back to decision for next iteration
            self._add_edge(self.current_node, decision_node, label="Next iteration")
            
            # Create a node for after the loop
            after_loop = self._create_node(
                NodeType.ACTIVITY, "After loop", function_name=self.function_name
            )
            
            # Connect decision to after_loop when loop ends
            self._add_edge(decision_node, after_loop, guard="Loop ended")
            
            # Set after_loop as current node
            self.current_node = after_loop
            
            # Handle else clause if it exists
            if node.orelse:
                for item in node.orelse:
                    self.visit(item)
        
        def visit_While(self, node: ast.While) -> None:
            """Visit a while loop node."""
            line_number = node.lineno
            
            # Get the condition as a string
            condition = ast.unparse(node.test).strip()
            
            # Create a decision node for the loop condition
            decision_node = self._create_node(
                NodeType.DECISION,
                f"While: {condition}",
                line_number,
                function_name=self.function_name,
                condition=condition,
            )
            
            # Connect current node to decision node
            self._add_edge(self.current_node, decision_node)
            
            # Set decision as current node
            self.current_node = decision_node
            
            # Process the loop body
            for item in node.body:
                self.visit(item)
            
            # Connect back to decision for next iteration
            self._add_edge(self.current_node, decision_node, label="Next iteration")
            
            # Create a node for after the loop
            after_loop = self._create_node(
                NodeType.ACTIVITY, "After loop", function_name=self.function_name
            )
            
            # Connect decision to after_loop when condition is False
            self._add_edge(decision_node, after_loop, guard="False")
            
            # Set after_loop as current node
            self.current_node = after_loop
            
            # Handle else clause if it exists
            if node.orelse:
                for item in node.orelse:
                    self.visit(item)
        
        def visit_Try(self, node: ast.Try) -> None:
            """Visit a try-except statement."""
            line_number = node.lineno
            
            # Create a fork node for the try block (to represent potential exception paths)
            fork_node = self._create_node(
                NodeType.FORK, "Try", line_number, function_name=self.function_name
            )
            
            # Connect current node to fork
            self._add_edge(self.current_node, fork_node)
            
            # Create a join node for after the try-except
            join_node = self._create_node(
                NodeType.JOIN, "After try-except", function_name=self.function_name
            )
            
            # Process the try body
            self.current_node = fork_node
            for item in node.body:
                self.visit(item)
            
            # Connect last node in try body to join
            self._add_edge(self.current_node, join_node, label="No exception")
            
            # Process each except handler
            for handler in node.handlers:
                # Reset current node to fork for each handler
                self.current_node = fork_node
                
                # Get exception type as string
                if handler.type:
                    exc_type = ast.unparse(handler.type).strip()
                    label = f"Exception: {exc_type}"
                else:
                    label = "Exception: any"
                
                # Create activity node for the except block
                except_node = self._create_node(
                    NodeType.ACTIVITY,
                    f"Except: {label}",
                    handler.lineno,
                    function_name=self.function_name,
                )
                
                # Connect fork to except
                self._add_edge(fork_node, except_node, label=label)
                
                # Update current node
                self.current_node = except_node
                
                # Process except body
                for item in handler.body:
                    self.visit(item)
                
                # Connect last node in except body to join
                self._add_edge(self.current_node, join_node)
            
            # Process else block if it exists
            if node.orelse:
                # This runs if no exception occurred
                self.current_node = fork_node
                for item in node.orelse:
                    self.visit(item)
                
                # Connect to join
                self._add_edge(self.current_node, join_node, label="No exception")
            
            # Process finally block if it exists
            if node.finalbody:
                # Create activity node for finally
                finally_node = self._create_node(
                    NodeType.ACTIVITY, "Finally", function_name=self.function_name
                )
                
                # Connect join to finally
                self._add_edge(join_node, finally_node)
                
                # Update current node
                self.current_node = finally_node
                
                # Process finally body
                for item in node.finalbody:
                    self.visit(item)
            else:
                # Set join as current node
                self.current_node = join_node
        
        def visit_Return(self, node: ast.Return) -> None:
            """Visit a return statement."""
            line_number = node.lineno
            
            # Get the return value as a string
            if node.value:
                return_value = ast.unparse(node.value).strip()
                label = f"Return: {return_value}"
            else:
                label = "Return"
            
            # Create return activity node
            return_node = self._create_node(
                NodeType.ACTIVITY, label, line_number, function_name=self.function_name
            )
            
            # Connect current node to return node
            self._add_edge(self.current_node, return_node)
            
            # Connect return node to end node
            self._add_edge(return_node, self.end_node)
            
            # Set end as current node (any code after return is unreachable)
            self.current_node = self.end_node
        
        def generic_visit(self, node: ast.AST) -> None:
            """Visit a node and continue."""
            # For most statements, create an activity node
            if isinstance(
                node,
                (
                    ast.Assign,
                    ast.AugAssign,
                    ast.Expr,
                    ast.Assert,
                    ast.Raise,
                    ast.Pass,
                    ast.Break,
                    ast.Continue,
                ),
            ):
                if hasattr(node, "lineno"):
                    line_number = node.lineno
                    
                    # Get statement as string
                    statement = ast.unparse(node).strip()
                    
                    # Create activity node
                    activity_node = self._create_node(
                        NodeType.ACTIVITY,
                        statement[:50] + ("..." if len(statement) > 50 else ""),
                        line_number,
                        function_name=self.function_name,
                    )
                    
                    # Connect current node to activity
                    self._add_edge(self.current_node, activity_node)
                    
                    # Update current node
                    self.current_node = activity_node
                    
                    # Special handling for break and continue
                    if isinstance(node, ast.Break):
                        # Break will be properly handled when implemented fully
                        pass
                    elif isinstance(node, ast.Continue):
                        # Continue will be properly handled when implemented fully
                        pass
            
            # Continue with standard visitor pattern
            super().generic_visit(node)
    
    
    class ClassActivityVisitor(ast.NodeVisitor):
        """AST visitor that extracts activity diagram from a Python class."""
        
        def __init__(self, class_name: str):
            self.class_name = class_name
            self.function_visitors: Dict[str, FunctionControlFlowVisitor] = {}
        
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            """Visit a function definition node."""
            function_name = node.name
            
            # Create a control flow visitor for this function
            visitor = FunctionControlFlowVisitor(function_name, self.class_name)
            visitor.visit(node)
            
            # Store the visitor
            self.function_visitors[function_name] = visitor
    
    
    class ActivityAnalyzer:
        """Analyzer for extracting activity diagrams from Python code."""
        
        def __init__(self, root_dir: str | Path = "."):
            self.root_dir = Path(root_dir)
            self.class_visitors: Dict[str, ClassActivityVisitor] = {}
        
        def analyze_file(self, file_path: str | Path) -> None:
            """Analyze a single Python file."""
            path = Path(file_path) if isinstance(file_path, str) else file_path
            
            # Read and parse the file
            with open(path, encoding="utf-8") as f:
                code = f.read()
            
            try:
                tree = ast.parse(code)
                
                # Find class definitions and analyze each
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        
                        # Create a visitor for this class
                        visitor = ClassActivityVisitor(class_name)
                        visitor.visit(node)
                        
                        # Store the visitor
                        self.class_visitors[class_name] = visitor
                
            except SyntaxError as e:
                print(f"Syntax error in {file_path}: {e}")
        
        def analyze_directory(self, dir_path: str | Path | None = None) -> None:
            """Analyze all Python files in a directory."""
            if dir_path is None:
                target_dir = self.root_dir
            else:
                target_dir = Path(dir_path) if isinstance(dir_path, str) else dir_path
            
            # Walk through the directory and analyze Python files
            for root, _, files in os.walk(target_dir):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        self.analyze_file(file_path)
        
        def generate_activity_diagram(
            self, class_name: str, method_name: str
        ) -> ActivityDiagram:
            """Generate an activity diagram for a specific method."""
            # Create the diagram
            diagram = ActivityDiagram(title=f"{class_name}.{method_name} Activity")
            
            # Check if the class and method exist
            if class_name not in self.class_visitors:
                raise ValueError(f"Class {class_name} not found")
            
            class_visitor = self.class_visitors[class_name]
            
            if method_name not in class_visitor.function_visitors:
                raise ValueError(f"Method {method_name} not found in class {class_name}")
            
            # Get the function visitor
            function_visitor = class_visitor.function_visitors[method_name]
            
            # Add all nodes and edges to the diagram
            for node in function_visitor.nodes:
                diagram.add_node(node)
                diagram.add_to_swimlane(class_name, node.id)
            
            for edge in function_visitor.edges:
                diagram.add_edge(edge)
            
            return diagram

**Generator (generator.py)**:

.. code-block:: python

    """Generator for converting activity diagrams to PlantUML format."""
    
    from pathlib import Path
    
    from .models import ActivityDiagram, ActivityEdge, ActivityNode, NodeType
    
    
    class PlantUmlActivityGenerator:
        """Generates PlantUML activity diagrams from our activity model."""
        
        def __init__(self):
            self.indentation = "  "
            self.current_indent = 0
        
        def _indent(self) -> str:
            """Get the current indentation string."""
            return self.indentation * self.current_indent
        
        def _increase_indent(self) -> None:
            """Increase indentation level."""
            self.current_indent += 1
        
        def _decrease_indent(self) -> None:
            """Decrease indentation level."""
            self.current_indent = max(0, self.current_indent - 1)
        
        def _format_node(self, node: ActivityNode) -> str:
            """Format a node as PlantUML."""
            if node.type == NodeType.START:
                return f"start"
            elif node.type == NodeType.END:
                return f"end"
            elif node.type == NodeType.DECISION:
                if node.condition:
                    return f"if ({node.condition}) then (yes)"
                return f"if ({node.name}) then (yes)"
            elif node.type == NodeType.FORK:
                return f"fork"
            elif node.type == NodeType.JOIN:
                return f"end fork"
            elif node.type == NodeType.MERGE:
                return f"endif"
            else:  # ACTIVITY
                if "Return" in node.name:
                    return f":{node.name}\\nreturn;"
                return f":{node.name};"
        
        def _format_edge(self, edge: ActivityEdge) -> str:
            """Format an edge as PlantUML."""
            if edge.guard:
                if edge.guard.lower() == "false":
                    return f"else (no)"
                # For other guards, add as a note
                return f"note on link\n{edge.guard}\nend note"
            
            if edge.label:
                return f"-> {edge.label};"
            
            return "->"
        
        def generate_plantuml(self, diagram: ActivityDiagram) -> str:
            """Generate PlantUML code from an activity diagram model."""
            lines = ["@startuml", ""]
            
            # Add title
            if diagram.title:
                lines.append(f"title {diagram.title}")
                lines.append("")
            
            # Add skinparam settings
            lines.extend(
                [
                    "skinparam ActivityBackgroundColor white",
                    "skinparam ActivityBorderColor black",
                    "skinparam ArrowColor black",
                    "",
                ]
            )
            
            # Add swimlanes if defined
            if diagram.swimlanes:
                for swimlane, node_ids in diagram.swimlanes.items():
                    lines.append(f"|{swimlane}|")
                    
                    # Find nodes in this swimlane
                    swimlane_nodes = [n for n in diagram.nodes if n.id in node_ids]
                    swimlane_nodes.sort(key=lambda n: n.line_number)
                    
                    # Process nodes in this swimlane
                    for node in swimlane_nodes:
                        lines.append(self._format_node(node))
                        
                        # Find outgoing edges
                        outgoing_edges = [
                            e for e in diagram.edges if e.source_id == node.id
                        ]
                        
                        for edge in outgoing_edges:
                            lines.append(self._format_edge(edge))
            else:
                # No swimlanes, just process nodes and edges
                # This is a simplified approach and would need more work
                # to properly handle complex control flow
                
                # First add the start node
                start_nodes = [n for n in diagram.nodes if n.type == NodeType.START]
                if start_nodes:
                    lines.append(self._format_node(start_nodes[0]))
                
                # Then add activities
                for node in [n for n in diagram.nodes if n.type == NodeType.ACTIVITY]:
                    lines.append(self._format_node(node))
                
                # Add decisions, forks, etc.
                for node in [
                    n
                    for n in diagram.nodes
                    if n.type
                    in (
                        NodeType.DECISION,
                        NodeType.MERGE,
                        NodeType.FORK,
                        NodeType.JOIN,
                    )
                ]:
                    lines.append(self._format_node(node))
                
                # Finally add end nodes
                end_nodes = [n for n in diagram.nodes if n.type == NodeType.END]
                if end_nodes:
                    lines.append(self._format_node(end_nodes[0]))
            
            # End the diagram
            lines.append("")
            lines.append("@enduml")
            
            return "\n".join(lines)
        
        def generate_file(
            self,
            diagram: ActivityDiagram,
            output_path: str | Path,
        ) -> None:
            """Generate a PlantUML file from an activity diagram model."""
            plantuml_code = self.generate_plantuml(diagram)
            
            # Ensure output directory exists
            output_path = Path(output_path) if isinstance(output_path, str) else output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(plantuml_code)

**Usage (extract_activity.py)**:

.. code-block:: python

    #!/usr/bin/env python
    """Extract activity diagrams from Python code."""
    
    import argparse
    from pathlib import Path
    
    from utils.activity_extractor import ActivityAnalyzer, PlantUmlActivityGenerator
    
    
    def main():
        """Run the activity diagram extractor."""
        parser = argparse.ArgumentParser(
            description="Extract activity diagrams from Python code"
        )
        parser.add_argument(
            "--source",
            "-s",
            required=True,
            help="Source directory or file to analyze",
        )
        parser.add_argument(
            "--output",
            "-o",
            required=True,
            help="Output directory for generated diagrams",
        )
        parser.add_argument(
            "--class",
            "-c",
            dest="class_name",
            required=True,
            help="Class containing the method to diagram",
        )
        parser.add_argument(
            "--method",
            "-m",
            required=True,
            help="Method to generate activity diagram for",
        )
        
        args = parser.parse_args()
        
        # Create output directory if it doesn't exist
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create analyzer and analyze the source
        analyzer = ActivityAnalyzer(args.source)
        
        source_path = Path(args.source)
        if source_path.is_file():
            analyzer.analyze_file(source_path)
        else:
            analyzer.analyze_directory(source_path)
        
        # Generate the diagram
        try:
            diagram = analyzer.generate_activity_diagram(args.class_name, args.method)
            
            # Create generator and generate the diagram
            generator = PlantUmlActivityGenerator()
            
            output_file = output_dir / f"{args.class_name}_{args.method}_activity.puml"
            generator.generate_file(diagram, output_file)
            
            print(f"Activity diagram generated at {output_file}")
            
        except ValueError as e:
            print(f"Error: {e}")
            return 1
        
        return 0
    
    
    if __name__ == "__main__":
        exit(main())

State Diagram Extractor
----------------------

The state diagram extractor will analyze classes with state patterns to automatically generate state transition diagrams:

**Folder Structure**:
```
utils/state_extractor/
  ├── __init__.py
  ├── analyzer.py
  ├── generator.py
  └── models.py
```

**Models (models.py)**:

.. code-block:: python

    """Data models for state diagram extraction."""
    
    from dataclasses import dataclass, field
    from enum import Enum
    from typing import Dict, List, Optional, Set
    
    
    class StateType(Enum):
        """Types of states in a state diagram."""
        
        INITIAL = "initial"
        NORMAL = "normal"
        FINAL = "final"
        CHOICE = "choice"
        FORK = "fork"
        JOIN = "join"
        HISTORY = "history"
    
    
    @dataclass
    class State:
        """Represents a state in a state diagram."""
        
        id: str
        name: str
        type: StateType = StateType.NORMAL
        
        # Actions
        entry_actions: List[str] = field(default_factory=list)
        exit_actions: List[str] = field(default_factory=list)
        internal_actions: Dict[str, str] = field(default_factory=dict)
        
        # Method that handles this state
        method_name: Optional[str] = None
        line_number: int = 0
        
        def __hash__(self):
            return hash(self.id)
    
    
    @dataclass
    class Transition:
        """Represents a transition between states."""
        
        source_id: str
        target_id: str
        
        # Transition metadata
        event: Optional[str] = None
        guard: Optional[str] = None
        action: Optional[str] = None
        
        # Method that triggers this transition
        method_name: Optional[str] = None
        line_number: int = 0
        
        def __hash__(self):
            return hash((self.source_id, self.target_id, self.event))
    
    
    @dataclass
    class StateDiagram:
        """Represents a state diagram."""
        
        title: str
        states: Set[State] = field(default_factory=set)
        transitions: Set[Transition] = field(default_factory=set)
        
        # Track the initial state
        initial_state_id: Optional[str] = None
        
        def add_state(self, state: State) -> None:
            """Add a state to the diagram."""
            self.states.add(state)
            
            # If this is the initial state, track it
            if state.type == StateType.INITIAL and self.initial_state_id is None:
                self.initial_state_id = state.id
        
        def add_transition(self, transition: Transition) -> None:
            """Add a transition to the diagram."""
            self.transitions.add(transition)
    
    
    @dataclass
    class StateInfo:
        """Information about a state found in code."""
        
        state_name: str
        state_id: str
        method_name: Optional[str] = None
        entry_actions: List[str] = field(default_factory=list)
        exit_actions: List[str] = field(default_factory=list)
        is_initial: bool = False
        is_final: bool = False
        line_number: int = 0
    
    
    @dataclass
    class TransitionInfo:
        """Information about a transition found in code."""
        
        source_state: str
        target_state: str
        event: Optional[str] = None
        guard: Optional[str] = None
        action: Optional[str] = None
        method_name: Optional[str] = None
        line_number: int = 0

**Analyzer (analyzer.py)**:

.. code-block:: python

    """Analyzer for extracting state diagrams from Python code."""
    
    import ast
    import os
    import re
    from pathlib import Path
    from typing import Dict, List, Optional, Set, Tuple
    
    from .models import (
        State,
        StateDiagram,
        StateInfo,
        StateType,
        Transition,
        TransitionInfo,
    )
    
    
    class StateAttributeVisitor(ast.NodeVisitor):
        """AST visitor that finds attributes related to state."""
        
        def __init__(self):
            self.state_attributes: List[ast.Attribute] = []
        
        def visit_Attribute(self, node: ast.Attribute) -> None:
            """Visit an attribute access node."""
            if (
                isinstance(node.value, ast.Name)
                and node.value.id == "self"
                and node.attr == "state"
            ):
                self.state_attributes.append(node)
            
            self.generic_visit(node)
    
    
    class StateTransitionVisitor(ast.NodeVisitor):
        """AST visitor that extracts state transitions from a Python class."""
        
        def __init__(self, class_name: str):
            self.class_name = class_name
            self.transitions: List[TransitionInfo] = []
            self.states: Dict[str, StateInfo] = {}
            self.current_method: Optional[str] = None
            self.current_line: int = 0
        
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            """Visit a function definition node."""
            self.current_method = node.name
            self.current_line = node.lineno
            
            # Extract state information from method decorators
            for decorator in node.decorator_list:
                self._process_decorator(decorator)
            
            # Look for state transitions in the method body
            self._find_state_transitions(node)
            
            # Continue visiting the method body
            self.generic_visit(node)
            
            # Clear current method tracking
            self.current_method = None
        
        def _process_decorator(self, decorator: ast.expr) -> None:
            """Process a decorator to extract state information."""
            # Handle @state decorator
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == "state":
                    # @state("state_name")
                    if decorator.args:
                        state_name = self._extract_string_value(decorator.args[0])
                        if state_name:
                            # Generate a stable ID
                            state_id = f"state_{len(self.states)}"
                            
                            # Extract additional info from keywords
                            is_initial = self._extract_keyword_value(
                                decorator, "initial", False
                            )
                            is_final = self._extract_keyword_value(
                                decorator, "final", False
                            )
                            
                            # Create state info
                            state_info = StateInfo(
                                state_name=state_name,
                                state_id=state_id,
                                method_name=self.current_method,
                                is_initial=is_initial,
                                is_final=is_final,
                                line_number=self.current_line,
                            )
                            
                            self.states[state_name] = state_info
                
                # Handle @transition decorator
                elif decorator.func.id == "transition":
                    # @transition(source="state1", target="state2", event="event_name")
                    source = self._extract_keyword_value(decorator, "source", "")
                    target = self._extract_keyword_value(decorator, "target", "")
                    event = self._extract_keyword_value(decorator, "event", None)
                    guard = self._extract_keyword_value(decorator, "guard", None)
                    action = self._extract_keyword_value(decorator, "action", None)
                    
                    if source and target:
                        transition_info = TransitionInfo(
                            source_state=source,
                            target_state=target,
                            event=event,
                            guard=guard,
                            action=action,
                            method_name=self.current_method,
                            line_number=self.current_line,
                        )
                        
                        self.transitions.append(transition_info)
        
        def _extract_string_value(self, node: ast.expr) -> Optional[str]:
            """Extract a string value from an AST node."""
            if isinstance(node, ast.Str):
                return node.s
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                return node.value
            return None
        
        def _extract_keyword_value(self, call_node: ast.Call, keyword: str, default=None):
            """Extract a keyword argument value from a function call."""
            for kw in call_node.keywords:
                if kw.arg == keyword:
                    if isinstance(kw.value, ast.Str):
                        return kw.value.s
                    elif isinstance(kw.value, ast.Constant):
                        return kw.value.value
                    elif isinstance(kw.value, ast.Name):
                        # For variables like True, False
                        if kw.value.id == "True":
                            return True
                        elif kw.value.id == "False":
                            return False
                    # For complex expressions, return string representation
                    return ast.unparse(kw.value).strip()
            return default
        
        def _find_state_transitions(self, node: ast.FunctionDef) -> None:
            """Find state transitions in a method body."""
            # First find all assignments to self.state
            state_attrs = []
            attr_visitor = StateAttributeVisitor()
            attr_visitor.visit(node)
            state_attrs.extend(attr_visitor.state_attributes)
            
            # Process each state attribute assignment
            for stmt in ast.walk(node):
                if (
                    isinstance(stmt, ast.Assign)
                    and isinstance(stmt.targets[0], ast.Attribute)
                    and isinstance(stmt.targets[0].value, ast.Name)
                    and stmt.targets[0].value.id == "self"
                    and stmt.targets[0].attr == "state"
                ):
                    # Found an assignment like "self.state = new_state"
                    target_state = self._extract_state_from_assignment(stmt.value)
                    
                    if target_state:
                        # Look for condition checks before this assignment
                        current_state = self._extract_current_state_from_context(stmt)
                        
                        if current_state:
                            # Create a transition
                            transition_info = TransitionInfo(
                                source_state=current_state,
                                target_state=target_state,
                                method_name=self.current_method,
                                line_number=getattr(stmt, "lineno", self.current_line),
                            )
                            
                            self.transitions.append(transition_info)
        
        def _extract_state_from_assignment(self, value: ast.expr) -> Optional[str]:
            """Extract state name from an assignment value."""
            if isinstance(value, ast.Str):
                return value.s
            elif isinstance(value, ast.Constant) and isinstance(value.value, str):
                return value.value
            
            # Handle variable references
            elif isinstance(value, ast.Name):
                # This could be a variable holding a state name
                # For simplicity, we'll use the variable name as state name
                return value.id
            
            return None
        
        def _extract_current_state_from_context(self, stmt: ast.AST) -> Optional[str]:
            """
            Attempt to extract the current state from the context around a statement.
            
            Looks for conditions like "if self.state == 'old_state':" before the statement.
            """
            # This is a simplified approach that looks for certain patterns
            # A more robust solution would need control flow analysis
            
            # Look for a parent If node
            parent_if = None
            for parent in ast.iter_child_nodes(stmt):
                if isinstance(parent, ast.If):
                    parent_if = parent
                    break
            
            if parent_if and isinstance(parent_if.test, ast.Compare):
                compare = parent_if.test
                
                # Check for comparison like self.state == 'state_name'
                if (
                    isinstance(compare.left, ast.Attribute)
                    and isinstance(compare.left.value, ast.Name)
                    and compare.left.value.id == "self"
                    and compare.left.attr == "state"
                    and len(compare.ops) == 1
                    and isinstance(compare.ops[0], ast.Eq)
                    and len(compare.comparators) == 1
                ):
                    
                    # Extract state name from right side
                    comparator = compare.comparators[0]
                    if isinstance(comparator, ast.Str):
                        return comparator.s
                    elif isinstance(comparator, ast.Constant) and isinstance(
                        comparator.value, str
                    ):
                        return comparator.value
            
            return None
    
    
    class StatePatternDetector(ast.NodeVisitor):
        """AST visitor that detects state pattern usage in a class."""
        
        def __init__(self):
            self.has_state_field = False
            self.state_transitions: Dict[Tuple[str, str], List[ast.AST]] = {}
        
        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            """Visit a class definition to look for state pattern."""
            # Look for state field in attributes
            for body_item in node.body:
                if isinstance(body_item, ast.Assign):
                    for target in body_item.targets:
                        if isinstance(target, ast.Name) and target.id == "state":
                            self.has_state_field = True
            
            # Visit all methods
            self.generic_visit(node)
        
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            """Visit a method to look for state transitions."""
            # Skip if it's not an instance method
            if not node.args.args or node.args.args[0].arg != "self":
                return
            
            # Look for state changes in the method
            for body_item in ast.walk(node):
                if isinstance(body_item, ast.Assign):
                    for target in body_item.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"
                            and target.attr == "state"
                        ):
                            # Found a state change
                            # For simplicity, record the node
                            method_name = node.name
                            self.state_transitions.setdefault((method_name, ""), []).append(
                                body_item
                            )
    
    
    class StateAnalyzer:
        """Analyzer for extracting state diagrams from Python code."""
        
        def __init__(self, root_dir: str | Path = "."):
            self.root_dir = Path(root_dir)
            self.class_transitions: Dict[str, List[TransitionInfo]] = {}
            self.class_states: Dict[str, Dict[str, StateInfo]] = {}
        
        def analyze_file(self, file_path: str | Path) -> None:
            """Analyze a single Python file for state patterns."""
            path = Path(file_path) if isinstance(file_path, str) else file_path
            
            # Read and parse the file
            with open(path, encoding="utf-8") as f:
                code = f.read()
            
            try:
                tree = ast.parse(code)
                
                # Look for classes with state pattern
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        
                        # First detect if the class uses state pattern
                        detector = StatePatternDetector()
                        detector.visit(node)
                        
                        if detector.has_state_field or detector.state_transitions:
                            # Class uses state pattern, extract transitions
                            visitor = StateTransitionVisitor(class_name)
                            visitor.visit(node)
                            
                            # Store the results
                            self.class_transitions[class_name] = visitor.transitions
                            self.class_states[class_name] = visitor.states
                
            except SyntaxError as e:
                print(f"Syntax error in {file_path}: {e}")
        
        def analyze_directory(self, dir_path: str | Path | None = None) -> None:
            """Analyze all Python files in a directory for state patterns."""
            if dir_path is None:
                target_dir = self.root_dir
            else:
                target_dir = Path(dir_path) if isinstance(dir_path, str) else dir_path
            
            # Walk through the directory and analyze Python files
            for root, _, files in os.walk(target_dir):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        self.analyze_file(file_path)
        
        def generate_state_diagram(self, class_name: str) -> StateDiagram:
            """Generate a state diagram for a specific class."""
            # Check if class exists
            if class_name not in self.class_transitions:
                raise ValueError(f"Class {class_name} not found or has no state transitions")
            
            # Create the diagram
            diagram = StateDiagram(title=f"{class_name} State Diagram")
            
            # Add states from explicit annotations
            if class_name in self.class_states:
                for state_info in self.class_states[class_name].values():
                    state_type = (
                        StateType.INITIAL
                        if state_info.is_initial
                        else StateType.FINAL
                        if state_info.is_final
                        else StateType.NORMAL
                    )
                    
                    state = State(
                        id=state_info.state_id,
                        name=state_info.state_name,
                        type=state_type,
                        method_name=state_info.method_name,
                        line_number=state_info.line_number,
                        entry_actions=state_info.entry_actions,
                        exit_actions=state_info.exit_actions,
                    )
                    
                    diagram.add_state(state)
            
            # Add states from transitions
            transitions = self.class_transitions[class_name]
            
            # Track states found in transitions
            states_by_name: Dict[str, State] = {}
            
            # First pass: collect all states
            for transition in transitions:
                # Add source state if not already added
                if transition.source_state not in states_by_name:
                    state_id = f"state_{len(states_by_name)}"
                    state = State(
                        id=state_id,
                        name=transition.source_state,
                        method_name=transition.method_name,
                        line_number=transition.line_number,
                    )
                    states_by_name[transition.source_state] = state
                
                # Add target state if not already added
                if transition.target_state not in states_by_name:
                    state_id = f"state_{len(states_by_name)}"
                    state = State(
                        id=state_id,
                        name=transition.target_state,
                        method_name=transition.method_name,
                        line_number=transition.line_number,
                    )
                    states_by_name[transition.target_state] = state
            
            # Add all states to the diagram
            for state in states_by_name.values():
                diagram.add_state(state)
            
            # Add transitions
            for transition_info in transitions:
                source_id = states_by_name[transition_info.source_state].id
                target_id = states_by_name[transition_info.target_state].id
                
                transition = Transition(
                    source_id=source_id,
                    target_id=target_id,
                    event=transition_info.event,
                    guard=transition_info.guard,
                    action=transition_info.action,
                    method_name=transition_info.method_name,
                    line_number=transition_info.line_number,
                )
                
                diagram.add_transition(transition)
            
            return diagram

**Generator (generator.py)**:

.. code-block:: python

    """Generator for converting state diagrams to PlantUML format."""
    
    from pathlib import Path
    
    from .models import State, StateDiagram, StateType, Transition
    
    
    class PlantUmlStateGenerator:
        """Generates PlantUML state diagrams from our state model."""
        
        def __init__(self):
            self.indentation = "  "
            self.current_indent = 0
        
        def _indent(self) -> str:
            """Get the current indentation string."""
            return self.indentation * self.current_indent
        
        def _increase_indent(self) -> None:
            """Increase indentation level."""
            self.current_indent += 1
        
        def _decrease_indent(self) -> None:
            """Decrease indentation level."""
            self.current_indent = max(0, self.current_indent - 1)
        
        def _format_state(self, state: State) -> str:
            """Format a state as PlantUML."""
            if state.type == StateType.INITIAL:
                return f"[*] --> {state.name}"
            elif state.type == StateType.FINAL:
                return f"{state.name} --> [*]"
            
            # Normal state
            lines = [f"state {state.name} {{"]
            self._increase_indent()
            
            # Add entry actions
            if state.entry_actions:
                lines.append(f"{self._indent()}entry / {'; '.join(state.entry_actions)}")
            
            # Add exit actions
            if state.exit_actions:
                lines.append(f"{self._indent()}exit / {'; '.join(state.exit_actions)}")
            
            # Add internal actions
            for event, action in state.internal_actions.items():
                lines.append(f"{self._indent()}{event} / {action}")
            
            self._decrease_indent()
            lines.append("}")
            
            return "\n".join(lines)
        
        def _format_transition(self, transition: Transition) -> str:
            """Format a transition as PlantUML."""
            # Get states by ID
            source_id = transition.source_id
            target_id = transition.target_id
            
            # Build the transition line
            parts = []
            
            if transition.event:
                parts.append(transition.event)
            
            if transition.guard:
                parts.append(f"[{transition.guard}]")
            
            if transition.action:
                parts.append(f"/ {transition.action}")
            
            if parts:
                label = " ".join(parts)
                return f"{source_id} --> {target_id} : {label}"
            else:
                return f"{source_id} --> {target_id}"
        
        def generate_plantuml(self, diagram: StateDiagram) -> str:
            """Generate PlantUML code from a state diagram model."""
            lines = ["@startuml", ""]
            
            # Add title
            if diagram.title:
                lines.append(f"title {diagram.title}")
                lines.append("")
            
            # Add skinparam settings
            lines.extend(
                [
                    "skinparam State {",
                    "  BackgroundColor white",
                    "  BorderColor black",
                    "  ArrowColor black",
                    "}",
                    "",
                ]
            )
            
            # Add states
            for state in diagram.states:
                if state.type != StateType.INITIAL and state.type != StateType.FINAL:
                    lines.append(self._format_state(state))
            
            lines.append("")
            
            # Add initial transitions if defined
            if diagram.initial_state_id:
                for state in diagram.states:
                    if state.id == diagram.initial_state_id:
                        lines.append(f"[*] --> {state.name}")
                        break
            
            # Add all other transitions
            for transition in diagram.transitions:
                # Get source and target states
                source_state = next(
                    (s for s in diagram.states if s.id == transition.source_id), None
                )
                target_state = next(
                    (s for s in diagram.states if s.id == transition.target_id), None
                )
                
                if source_state and target_state:
                    lines.append(
                        f"{source_state.name} --> {target_state.name} : {transition.event or ''}"
                        + (f" [{transition.guard}]" if transition.guard else "")
                        + (f" / {transition.action}" if transition.action else "")
                    )
            
            # End the diagram
            lines.append("")
            lines.append("@enduml")
            
            return "\n".join(lines)
        
        def generate_file(
            self,
            diagram: StateDiagram,
            output_path: str | Path,
        ) -> None:
            """Generate a PlantUML file from a state diagram model."""
            plantuml_code = self.generate_plantuml(diagram)
            
            # Ensure output directory exists
            output_path = Path(output_path) if isinstance(output_path, str) else output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(plantuml_code)

**Usage (extract_state.py)**:

.. code-block:: python

    #!/usr/bin/env python
    """Extract state diagrams from Python code."""
    
    import argparse
    from pathlib import Path
    
    from utils.state_extractor import StateAnalyzer, PlantUmlStateGenerator
    
    
    def main():
        """Run the state diagram extractor."""
        parser = argparse.ArgumentParser(
            description="Extract state diagrams from Python code"
        )
        parser.add_argument(
            "--source",
            "-s",
            required=True,
            help="Source directory or file to analyze",
        )
        parser.add_argument(
            "--output",
            "-o",
            required=True,
            help="Output directory for generated diagrams",
        )
        parser.add_argument(
            "--class",
            "-c",
            dest="class_name",
            required=True,
            help="Class to generate state diagram for",
        )
        
        args = parser.parse_args()
        
        # Create output directory if it doesn't exist
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create analyzer and analyze the source
        analyzer = StateAnalyzer(args.source)
        
        source_path = Path(args.source)
        if source_path.is_file():
            analyzer.analyze_file(source_path)
        else:
            analyzer.analyze_directory(source_path)
        
        # Generate the diagram
        try:
            diagram = analyzer.generate_state_diagram(args.class_name)
            
            # Create generator and generate the diagram
            generator = PlantUmlStateGenerator()
            
            output_file = output_dir / f"{args.class_name}_state.puml"
            generator.generate_file(diagram, output_file)
            
            print(f"State diagram generated at {output_file}")
            
        except ValueError as e:
            print(f"Error: {e}")
            return 1
        
        return 0
    
    
    if __name__ == "__main__":
        exit(main())

Conclusion
----------

The current UML generator provides a solid foundation we can extend to support multiple diagram types. We have successfully implemented:

1. Package and Component diagrams which can be automatically generated from code analysis
2. Sequence diagrams with both YAML definition and static code analysis approaches

We've also outlined the implementation for Activity and State diagram extractors following the same pattern used in the sequence extractor. These new extractors provide:

1. Automatic analysis of Python code to identify control flow for activity diagrams
2. Detection of state patterns and transitions in class implementations
3. PlantUML generators for both diagram types

The implementation follows our established architecture while adding specialized analyzers that can extract complex behavioral patterns from source code. The next steps will be to implement these extractors and integrate them with the main UML generator workflow.

Both approaches now work together in the same workflow and produce diagrams in the standard PlantUML format, making them easy to include in documentation.