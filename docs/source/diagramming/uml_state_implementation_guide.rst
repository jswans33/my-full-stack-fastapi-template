UML State Diagram Implementation Guide
==================================

This guide provides concrete step-by-step instructions for implementing state diagram support in the UML generator. This implementation approach follows the same pattern as the sequence and activity diagram extractors.

Prerequisites
------------

- Existing UML generator code in ``utils/uml_generator``
- Existing sequence and activity extractors
- Python 3.10+ with typing support
- Understanding of the current UML generator architecture

Implementation Steps
-------------------

Step 1: Create State Diagram Models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, create a new file for state diagram models:

**File: utils/state_extractor/models.py**

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

Step 2: Create State Diagram Analyzer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next, create an analyzer that extracts state diagrams from Python code:

**File: utils/state_extractor/analyzer.py**

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

Step 3: Create State Diagram Generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next, create a generator that converts state diagram models to PlantUML:

**File: utils/state_extractor/generator.py**

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

Step 4: Create Module Initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create the state extractor package initialization file:

**File: utils/state_extractor/__init__.py**

.. code-block:: python

    """State diagram extractor for Python code.
    
    This module provides functionality to extract state diagrams from Python code
    through static analysis of state patterns and state transitions.
    """
    
    from .analyzer import StateAnalyzer
    from .generator import PlantUmlStateGenerator
    from .models import State, StateDiagram, StateType, Transition
    
    __all__ = [
        "State",
        "StateAnalyzer",
        "StateDiagram",
        "StateType",
        "Transition",
        "PlantUmlStateGenerator",
    ]

Step 5: Create Command-Line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a command-line tool for extracting state diagrams:

**File: utils/extract_state.py**

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

Step 6: Update run_uml_generator.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the main UML generator script to include state diagram extraction:

**File: utils/run_uml_generator.py** (partial update)

.. code-block:: python

    # Add import for state extractor
    from utils.state_extractor import StateAnalyzer, PlantUmlStateGenerator
    
    # Add a function to generate state diagrams
    def generate_state_diagrams(base_dir: Path, output_dir: Path) -> None:
        """Generate state diagrams from Python code."""
        print("Generating state diagrams...")
        
        # Define the source directory to analyze
        source_dir = base_dir / "backend" / "app"
        
        # Create the output directory
        state_output_dir = output_dir / "state"
        state_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create analyzer and analyze the source
        analyzer = StateAnalyzer(source_dir)
        analyzer.analyze_directory()
        
        # Define classes to generate diagrams for
        # This could be read from a configuration file
        targets = [
            "Document",
            "Order",
            "User",
            # Add more targets as needed
        ]
        
        # Generate diagrams for each target
        for class_name in targets:
            try:
                diagram = analyzer.generate_state_diagram(class_name)
                
                # Create generator and generate the diagram
                generator = PlantUmlStateGenerator()
                
                output_file = state_output_dir / f"{class_name}_state.puml"
                generator.generate_file(diagram, output_file)
                
                print(f"Generated state diagram for {class_name}")
                
            except ValueError as e:
                print(f"Could not generate state diagram for {class_name}: {e}")
    
    # Update the main function to include state diagram generation
    def main():
        # ... existing code ...
        
        # Generate activity diagrams
        generate_activity_diagrams(base_dir, output_dir)
        
        # Generate state diagrams
        generate_state_diagrams(base_dir, output_dir)
        
        # ... existing code ...

Step 7: Create a State Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To help annotate state patterns in code, create state and transition decorators:

**File: utils/state_decorators.py**

.. code-block:: python

    """Decorators for defining state machines in Python classes."""
    
    from functools import wraps
    from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union, cast
    
    
    T = TypeVar("T")
    
    
    def state(
        state_name: str,
        *,
        initial: bool = False,
        final: bool = False,
        entry_actions: Optional[List[str]] = None,
        exit_actions: Optional[List[str]] = None,
    ) -> Callable[[T], T]:
        """Decorator to mark a method as a state handler.
        
        Args:
            state_name: Name of the state
            initial: Whether this is the initial state
            final: Whether this is a final state
            entry_actions: Actions to perform when entering this state
            exit_actions: Actions to perform when exiting this state
        
        Returns:
            Decorated method
        """
        
        def decorator(method: T) -> T:
            # Store state information on the method
            setattr(method, "_state_info", {
                "name": state_name,
                "initial": initial,
                "final": final,
                "entry_actions": entry_actions or [],
                "exit_actions": exit_actions or [],
            })
            
            return method
        
        return decorator
    
    
    def transition(
        *,
        source: str,
        target: str,
        event: Optional[str] = None,
        guard: Optional[str] = None,
        action: Optional[str] = None,
    ) -> Callable[[T], T]:
        """Decorator to mark a method as a state transition.
        
        Args:
            source: Source state name
            target: Target state name
            event: Event triggering the transition
            guard: Guard condition for the transition
            action: Action to perform during the transition
        
        Returns:
            Decorated method
        """
        
        def decorator(method: T) -> T:
            # Store transition information on the method
            setattr(method, "_transition_info", {
                "source": source,
                "target": target,
                "event": event,
                "guard": guard,
                "action": action,
            })
            
            @wraps(method)
            def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
                # Check if guard condition is met
                if guard and not eval(f"self.{guard}"):
                    return None
                
                # Execute the transition method
                result = method(self, *args, **kwargs)
                
                # Update the state
                if hasattr(self, "state"):
                    self.state = target
                
                return result
            
            return cast(T, wrapper)
        
        return decorator

Step 8: Update Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the UML diagrams documentation to include state diagrams:

**File: docs/source/uml_diagrams.rst** (partial update)

.. code-block:: rst

    State Diagrams
    --------------
    
    Document Lifecycle
    ~~~~~~~~~~~~~~~~
    
    .. uml:: ../_generated_uml/state/Document_state.puml
    
    Order Processing
    ~~~~~~~~~~~~~~~
    
    .. uml:: ../_generated_uml/state/Order_state.puml

Step 9: Usage Example
~~~~~~~~~~~~~~~~~~~

Here's how to use the state diagram extractor:

**Option 1: From the command line**

.. code-block:: bash

    # Extract a state diagram for a specific class
    python -m utils.extract_state --source ./backend/app --output ./docs/source/_generated_uml/state --class Document

**Option 2: From Python code**

.. code-block:: python

    from pathlib import Path
    from utils.state_extractor import StateAnalyzer, PlantUmlStateGenerator
    
    # Create analyzer and analyze source code
    analyzer = StateAnalyzer("./backend/app")
    analyzer.analyze_directory()
    
    # Generate state diagram for a specific class
    diagram = analyzer.generate_state_diagram("Document")
    
    # Generate PlantUML file
    generator = PlantUmlStateGenerator()
    output_path = Path("docs/source/_generated_uml/state/Document_state.puml")
    generator.generate_file(diagram, output_path)

**Option 3: Using state decorators in your code**

.. code-block:: python

    from utils.state_decorators import state, transition
    
    class Document:
        def __init__(self):
            self.state = "draft"
            self.content = ""
            self.reviewers = []
        
        @state("draft", initial=True, entry_actions=["create empty document"])
        def handle_draft(self):
            """Handle draft state."""
            # Draft state behavior
            pass
        
        @transition(source="draft", target="review", event="submit")
        def submit_for_review(self):
            """Submit document for review."""
            self.notify_reviewers()
            return True
        
        @state("review", entry_actions=["notify reviewers"])
        def handle_review(self):
            """Handle review state."""
            # Review state behavior
            pass
        
        @transition(source="review", target="draft", event="request_changes")
        def request_changes(self, comments):
            """Request changes to the document."""
            self.add_comments(comments)
            return True
        
        @transition(source="review", target="approved", event="approve", guard="all_reviewers_approved")
        def approve(self):
            """Approve the document."""
            return True
        
        @state("approved", entry_actions=["notify author"])
        def handle_approved(self):
            """Handle approved state."""
            # Approved state behavior
            pass
        
        @transition(source="approved", target="published", event="publish")
        def publish(self):
            """Publish the document."""
            self.generate_public_link()
            return True
        
        @state("published", entry_actions=["update timestamp", "generate public link"])
        def handle_published(self):
            """Handle published state."""
            # Published state behavior
            pass
        
        def all_reviewers_approved(self):
            """Check if all reviewers have approved."""
            return all(reviewer.has_approved for reviewer in self.reviewers)
        
        def notify_reviewers(self):
            """Notify reviewers."""
            pass
        
        def add_comments(self, comments):
            """Add comments to the document."""
            pass
        
        def generate_public_link(self):
            """Generate a public link for the document."""
            pass

Conclusion
----------

This implementation guide provides a complete approach for adding state diagram extraction to the UML generator. The implementation follows the same pattern as the sequence and activity extractors, using AST-based static analysis to detect state patterns and transitions in Python code.

Key files created:

- ``utils/state_extractor/models.py`` - Data models for state diagrams
- ``utils/state_extractor/analyzer.py`` - AST-based analyzer for state patterns
- ``utils/state_extractor/generator.py`` - PlantUML generator for state diagrams
- ``utils/state_extractor/__init__.py`` - Package initialization
- ``utils/extract_state.py`` - Command-line tool
- ``utils/state_decorators.py`` - Decorators for marking states and transitions

The state diagram extractor can analyze Python classes to extract state patterns, including:

- Explicit state field assignments
- State transition methods
- Decorator-based state definitions

The extracted diagrams show the states of objects or systems and the transitions between them, which is particularly useful for understanding object lifecycles and reactive systems.

Implementation Diff
-----------------

Below is a diff showing the changes needed to implement the state diagram extractor:

.. code-block:: diff

    # Create directories
    + mkdir -p utils/state_extractor
    + mkdir -p docs/source/_generated_uml/state

    # Create files
    + touch utils/state_extractor/__init__.py
    + touch utils/state_extractor/models.py
    + touch utils/state_extractor/analyzer.py
    + touch utils/state_extractor/generator.py
    + touch utils/extract_state.py
    + touch utils/state_decorators.py

    # Modify run_uml_generator.py
    diff --git a/utils/run_uml_generator.py b/utils/run_uml_generator.py
    index abcdefg..1234567 100644
    --- a/utils/run_uml_generator.py
    +++ b/utils/run_uml_generator.py
    @@ -11,6 +11,7 @@ from utils.uml_generator.factories import DefaultGeneratorFactory
     from utils.uml_generator.service import UmlGeneratorService
     from utils.sequence_extractor import SequenceAnalyzer, PlantUmlSequenceGenerator
     from utils.activity_extractor import ActivityAnalyzer, PlantUmlActivityGenerator
    +from utils.state_extractor import StateAnalyzer, PlantUmlStateGenerator
     
     
     def generate_class_diagrams(base_dir: Path, output_dir: Path) -> None:
    @@ -76,6 +77,36 @@ def generate_activity_diagrams(base_dir: Path, output_dir: Path) -> None:
                 print(f"Could not generate activity diagram for {class_name}.{method_name}: {e}")
     
     
    +def generate_state_diagrams(base_dir: Path, output_dir: Path) -> None:
    +    """Generate state diagrams from Python code."""
    +    print("Generating state diagrams...")
    +    
    +    # Define the source directory to analyze
    +    source_dir = base_dir / "backend" / "app"
    +    
    +    # Create the output directory
    +    state_output_dir = output_dir / "state"
    +    state_output_dir.mkdir(parents=True, exist_ok=True)
    +    
    +    # Create analyzer and analyze the source
    +    analyzer = StateAnalyzer(source_dir)
    +    analyzer.analyze_directory()
    +    
    +    # Define classes to generate diagrams for
    +    targets = [
    +        "Document",
    +        "Order",
    +        "User",
    +        # Add more targets as needed
    +    ]
    +    
    +    # Generate diagrams for each target
    +    for class_name in targets:
    +        try:
    +            diagram = analyzer.generate_state_diagram(class_name)
    +            generator = PlantUmlStateGenerator()
    +            output_file = state_output_dir / f"{class_name}_state.puml"
    +            generator.generate_file(diagram, output_file)
    +            print(f"Generated state diagram for {class_name}")
    +        except ValueError as e:
    +            print(f"Could not generate state diagram for {class_name}: {e}")
    +
     def main():
         """Run the UML generator."""
         base_dir = Path(__file__).parent.parent
    @@ -118,6 +149,9 @@ def main():
         # Generate activity diagrams
         generate_activity_diagrams(base_dir, output_dir)
         
    +    # Generate state diagrams
    +    generate_state_diagrams(base_dir, output_dir)
    +    
         print(f"UML diagrams generated in {output_dir}")
     
     
    # Update docs/source/uml_diagrams.rst
    diff --git a/docs/source/uml_diagrams.rst b/docs/source/uml_diagrams.rst
    index abcdefg..1234567 100644
    --- a/docs/source/uml_diagrams.rst
    +++ b/docs/source/uml_diagrams.rst
    @@ -30,3 +30,14 @@ Generate Sequence Diagram Flow
     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     
     .. uml:: ../_generated_uml/activity/SequenceAnalyzer_generate_sequence_diagram_activity.puml
    +
    +State Diagrams
    +-------------
    +
    +Document Lifecycle
    +~~~~~~~~~~~~~~~~
    +
    +.. uml:: ../_generated_uml/state/Document_state.puml
    +
    +Order Processing
    +~~~~~~~~~~~~~~~
    +
    +.. uml:: ../_generated_uml/state/Order_state.puml            
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

Step 3: Create State Diagram Generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next, create a generator that converts state diagram models to PlantUML:

**File: utils/state_extractor/generator.py**

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

Step 4: Create Module Initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create the state extractor package initialization file:

**File: utils/state_extractor/__init__.py**

.. code-block:: python

    """State diagram extractor for Python code.
    
    This module provides functionality to extract state diagrams from Python code
    through static analysis of state patterns and state transitions.
    """
    
    from .analyzer import StateAnalyzer
    from .generator import PlantUmlStateGenerator
    from .models import State, StateDiagram, StateType, Transition
    
    __all__ = [
        "State",
        "StateAnalyzer",
        "StateDiagram",
        "StateType",
        "Transition",
        "PlantUmlStateGenerator",
    ]

Step 5: Create Command-Line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a command-line tool for extracting state diagrams:

**File: utils/extract_state.py**

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

Step 6: Update run_uml_generator.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the main UML generator script to include state diagram extraction:

**File: utils/run_uml_generator.py** (partial update)

.. code-block:: python

    # Add import for state extractor
    from utils.state_extractor import StateAnalyzer, PlantUmlStateGenerator
    
    # Add a function to generate state diagrams
    def generate_state_diagrams(base_dir: Path, output_dir: Path) -> None:
        """Generate state diagrams from Python code."""
        print("Generating state diagrams...")
        
        # Define the source directory to analyze
        source_dir = base_dir / "backend" / "app"
        
        # Create the output directory
        state_output_dir = output_dir / "state"
        state_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create analyzer and analyze the source
        analyzer = StateAnalyzer(source_dir)
        analyzer.analyze_directory()
        
        # Define classes to generate diagrams for
        # This could be read from a configuration file
        targets = [
            "Document",
            "Order",
            "User",
            # Add more targets as needed
        ]
        
        # Generate diagrams for each target
        for class_name in targets:
            try:
                diagram = analyzer.generate_state_diagram(class_name)
                
                # Create generator and generate the diagram
                generator = PlantUmlStateGenerator()
                
                output_file = state_output_dir / f"{class_name}_state.puml"
                generator.generate_file(diagram, output_file)
                
                print(f"Generated state diagram for {class_name}")
                
            except ValueError as e:
                print(f"Could not generate state diagram for {class_name}: {e}")
    
    # Update the main function to include state diagram generation
    def main():
        # ... existing code ...
        
        # Generate activity diagrams
        generate_activity_diagrams(base_dir, output_dir)
        
        # Generate state diagrams
        generate_state_diagrams(base_dir, output_dir)
        
        # ... existing code ...

Step 7: Create a State Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To help annotate state patterns in code, create state and transition decorators:

**File: utils/state_decorators.py**

.. code-block:: python

    """Decorators for defining state machines in Python classes."""
    
    from functools import wraps
    from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union, cast
    
    
    T = TypeVar("T")
    
    
    def state(
        state_name: str,
        *,
        initial: bool = False,
        final: bool = False,
        entry_actions: Optional[List[str]] = None,
        exit_actions: Optional[List[str]] = None,
    ) -> Callable[[T], T]:
        """Decorator to mark a method as a state handler.
        
        Args:
            state_name: Name of the state
            initial: Whether this is the initial state
            final: Whether this is a final state
            entry_actions: Actions to perform when entering this state
            exit_actions: Actions to perform when exiting this state
        
        Returns:
            Decorated method
        """
        
        def decorator(method: T) -> T:
            # Store state information on the method
            setattr(method, "_state_info", {
                "name": state_name,
                "initial": initial,
                "final": final,
                "entry_actions": entry_actions or [],
                "exit_actions": exit_actions or [],
            })
            
            return method
        
        return decorator
    
    
    def transition(
        *,
        source: str,
        target: str,
        event: Optional[str] = None,
        guard: Optional[str] = None,
        action: Optional[str] = None,
    ) -> Callable[[T], T]:
        """Decorator to mark a method as a state transition.
        
        Args:
            source: Source state name
            target: Target state name
            event: Event triggering the transition
            guard: Guard condition for the transition
            action: Action to perform during the transition
        
        Returns:
            Decorated method
        """
        
        def decorator(method: T) -> T:
            # Store transition information on the method
            setattr(method, "_transition_info", {
                "source": source,
                "target": target,
                "event": event,
                "guard": guard,
                "action": action,
            })
            
            @wraps(method)
            def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
                # Check if guard condition is met
                if guard and not eval(f"self.{guard}"):
                    return None
                
                # Execute the transition method
                result = method(self, *args, **kwargs)
                
                # Update the state
                if hasattr(self, "state"):
                    self.state = target
                
                return result
            
            return cast(T, wrapper)
        
        return decorator

Step 8: Update Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the UML diagrams documentation to include state diagrams:

**File: docs/source/uml_diagrams.rst** (partial update)

.. code-block:: rst

    State Diagrams
    --------------
    
    Document Lifecycle
    ~~~~~~~~~~~~~~~~
    
    .. uml:: ../_generated_uml/state/Document_state.puml
    
    Order Processing
    ~~~~~~~~~~~~~~~
    
    .. uml:: ../_generated_uml/state/Order_state.puml

Step 9: Usage Example
~~~~~~~~~~~~~~~~~~~

Here's how to use the state diagram extractor:

**Option 1: From the command line**

.. code-block:: bash

    # Extract a state diagram for a specific class
    python -m utils.extract_state --source ./backend/app --output ./docs/source/_generated_uml/state --class Document

**Option 2: From Python code**

.. code-block:: python

    from pathlib import Path
    from utils.state_extractor import StateAnalyzer, PlantUmlStateGenerator
    
    # Create analyzer and analyze source code
    analyzer = StateAnalyzer("./backend/app")
    analyzer.analyze_directory()
    
    # Generate state diagram for a specific class
    diagram = analyzer.generate_state_diagram("Document")
    
    # Generate PlantUML file
    generator = PlantUmlStateGenerator()
    output_path = Path("docs/source/_generated_uml/state/Document_state.puml")
    generator.generate_file(diagram, output_path)

**Option 3: Using state decorators in your code**

.. code-block:: python

    from utils.state_decorators import state, transition
    
    class Document:
        def __init__(self):
            self.state = "draft"
            self.content = ""
            self.reviewers = []
        
        @state("draft", initial=True, entry_actions=["create empty document"])
        def handle_draft(self):
            """Handle draft state."""
            # Draft state behavior
            pass
        
        @transition(source="draft", target="review", event="submit")
        def submit_for_review(self):
            """Submit document for review."""
            self.notify_reviewers()
            return True
        
        @state("review", entry_actions=["notify reviewers"])
        def handle_review(self):
            """Handle review state."""
            # Review state behavior
            pass
        
        @transition(source="review", target="draft", event="request_changes")
        def request_changes(self, comments):
            """Request changes to the document."""
            self.add_comments(comments)
            return True
        
        @transition(source="review", target="approved", event="approve", guard="all_reviewers_approved")
        def approve(self):
            """Approve the document."""
            return True
        
        @state("approved", entry_actions=["notify author"])
        def handle_approved(self):
            """Handle approved state."""
            # Approved state behavior
            pass
        
        @transition(source="approved", target="published", event="publish")
        def publish(self):
            """Publish the document."""
            self.generate_public_link()
            return True
        
        @state("published", entry_actions=["update timestamp", "generate public link"])
        def handle_published(self):
            """Handle published state."""
            # Published state behavior
            pass
        
        def all_reviewers_approved(self):
            """Check if all reviewers have approved."""
            return all(reviewer.has_approved for reviewer in self.reviewers)
        
        def notify_reviewers(self):
            """Notify reviewers."""
            pass
        
        def add_comments(self, comments):
            """Add comments to the document."""
            pass
        
        def generate_public_link(self):
            """Generate a public link for the document."""
            pass

Conclusion
----------

This implementation guide provides a complete approach for adding state diagram extraction to the UML generator. The implementation follows the same pattern as the sequence and activity extractors, using AST-based static analysis to detect state patterns and transitions in Python code.

Key files created:

- ``utils/state_extractor/models.py`` - Data models for state diagrams
- ``utils/state_extractor/analyzer.py`` - AST-based analyzer for state patterns
- ``utils/state_extractor/generator.py`` - PlantUML generator for state diagrams
- ``utils/state_extractor/__init__.py`` - Package initialization
- ``utils/extract_state.py`` - Command-line tool
- ``utils/state_decorators.py`` - Decorators for marking states and transitions

The state diagram extractor can analyze Python classes to extract state patterns, including:

- Explicit state field assignments
- State transition methods
- Decorator-based state definitions

The extracted diagrams show the states of objects or systems and the transitions between them, which is particularly useful for understanding object lifecycles and reactive systems.

Implementation Diff
-----------------

Below is a diff showing the changes needed to implement the state diagram extractor:

.. code-block:: diff

    # Create directories
    + mkdir -p utils/state_extractor
    + mkdir -p docs/source/_generated_uml/state

    # Create files
    + touch utils/state_extractor/__init__.py
    + touch utils/state_extractor/models.py
    + touch utils/state_extractor/analyzer.py
    + touch utils/state_extractor/generator.py
    + touch utils/extract_state.py
    + touch utils/state_decorators.py

    # Modify run_uml_generator.py
    diff --git a/utils/run_uml_generator.py b/utils/run_uml_generator.py
    index abcdefg..1234567 100644
    --- a/utils/run_uml_generator.py
    +++ b/utils/run_uml_generator.py
    @@ -11,6 +11,7 @@ from utils.uml_generator.factories import DefaultGeneratorFactory
     from utils.uml_generator.service import UmlGeneratorService
     from utils.sequence_extractor import SequenceAnalyzer, PlantUmlSequenceGenerator
     from utils.activity_extractor import ActivityAnalyzer, PlantUmlActivityGenerator
    +from utils.state_extractor import StateAnalyzer, PlantUmlStateGenerator
     
     
     def generate_class_diagrams(base_dir: Path, output_dir: Path) -> None:
    @@ -76,6 +77,36 @@ def generate_activity_diagrams(base_dir: Path, output_dir: Path) -> None:
                 print(f"Could not generate activity diagram for {class_name}.{method_name}: {e}")
     
     
    +def generate_state_diagrams(base_dir: Path, output_dir: Path) -> None:
    +    """Generate state diagrams from Python code."""
    +    print("Generating state diagrams...")
    +    
    +    # Define the source directory to analyze
    +    source_dir = base_dir / "backend" / "app"
    +    
    +    # Create the output directory
    +    state_output_dir = output_dir / "state"
    +    state_output_dir.mkdir(parents=True, exist_ok=True)
    +    
    +    # Create analyzer and analyze the source
    +    analyzer = StateAnalyzer(source_dir)
    +    analyzer.analyze_directory()
    +    
    +    # Define classes to generate diagrams for
    +    targets = [
    +        "Document",
    +        "Order",
    +        "User",
    +        # Add more targets as needed
    +    ]
    +    
    +    # Generate diagrams for each target
    +    for class_name in targets:
    +        try:
    +            diagram = analyzer.generate_state_diagram(class_name)
    +            generator = PlantUmlStateGenerator()
    +            output_file = state_output_dir / f"{class_name}_state.puml"
    +            generator.generate_file(diagram, output_file)
    +            print(f"Generated state diagram for {class_name}")
    +        except ValueError as e:
    +            print(f"Could not generate state diagram for {class_name}: {e}")
    +
     def main():
         """Run the UML generator."""
         base_dir = Path(__file__).parent.parent
    @@ -118,6 +149,9 @@ def main():
         # Generate activity diagrams
         generate_activity_diagrams(base_dir, output_dir)
         
    +    # Generate state diagrams
    +    generate_state_diagrams(base_dir, output_dir)
    +    
         print(f"UML diagrams generated in {output_dir}")
     
     
    # Update docs/source/uml_diagrams.rst
    diff --git a/docs/source/uml_diagrams.rst b/docs/source/uml_diagrams.rst
    index abcdefg..1234567 100644
    --- a/docs/source/uml_diagrams.rst
    +++ b/docs/source/uml_diagrams.rst
    @@ -30,3 +30,14 @@ Generate Sequence Diagram Flow
     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     
     .. uml:: ../_generated_uml/activity/SequenceAnalyzer_generate_sequence_diagram_activity.puml
    +
    +State Diagrams
    +-------------
    +
    +Document Lifecycle
    +~~~~~~~~~~~~~~~~
    +
    +.. uml:: ../_generated_uml/state/Document_state.puml
    +
    +Order Processing
    +~~~~~~~~~~~~~~~
    +
    +.. uml:: ../_generated_uml/state/Order_state.puml
