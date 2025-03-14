UML Activity Diagram Implementation Guide
====================================

This guide provides concrete step-by-step instructions for implementing activity diagram support in the UML generator. This implementation approach follows the same pattern as the sequence diagram extractor.

Prerequisites
------------

- Existing UML generator code in ``utils/uml_generator``
- Existing sequence extractor in ``utils/sequence_extractor``
- Python 3.10+ with typing support
- Understanding of the current UML generator architecture

Implementation Steps
-------------------

Step 1: Create Activity Diagram Models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, create a new file for activity diagram models:

**File: utils/activity_extractor/models.py**

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

Step 2: Create Activity Diagram Analyzer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next, create an analyzer that extracts activity diagrams from Python code:

**File: utils/activity_extractor/analyzer.py**

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

Step 3: Create Activity Diagram Generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next, create a generator that converts activity diagram models to PlantUML:

**File: utils/activity_extractor/generator.py**

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

Step 4: Create Module Initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create the activity extractor package initialization file:

**File: utils/activity_extractor/__init__.py**

.. code-block:: python

    """Activity diagram extractor for Python code.
    
    This module provides functionality to extract activity diagrams from Python code
    through static analysis of control flow in functions and methods.
    """
    
    from .analyzer import ActivityAnalyzer, FunctionControlFlowVisitor
    from .generator import PlantUmlActivityGenerator
    from .models import ActivityDiagram, ActivityEdge, ActivityNode, NodeType
    
    __all__ = [
        "ActivityAnalyzer",
        "ActivityDiagram",
        "ActivityEdge",
        "ActivityNode",
        "FunctionControlFlowVisitor",
        "NodeType",
        "PlantUmlActivityGenerator",
    ]

Step 5: Create Command-Line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a command-line tool for extracting activity diagrams:

**File: utils/extract_activity.py**

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

Step 6: Update run_uml_generator.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the main UML generator script to include activity diagram extraction:

**File: utils/run_uml_generator.py** (partial update)

.. code-block:: python

    # Add import for activity extractor
    from utils.activity_extractor import ActivityAnalyzer, PlantUmlActivityGenerator
    
    # Add a function to generate activity diagrams
    def generate_activity_diagrams(base_dir: Path, output_dir: Path) -> None:
        """Generate activity diagrams from Python code."""
        print("Generating activity diagrams...")
        
        # Define the source directory to analyze
        source_dir = base_dir / "utils"
        
        # Create the output directory
        activity_output_dir = output_dir / "activity"
        activity_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create analyzer and analyze the source
        analyzer = ActivityAnalyzer(source_dir)
        analyzer.analyze_directory()
        
        # Define classes and methods to generate diagrams for
        # This could be read from a configuration file
        targets = [
            ("SequenceAnalyzer", "generate_sequence_diagram"),
            ("PlantUmlGenerator", "generate_diagram"),
            # Add more targets as needed
        ]
        
        # Generate diagrams for each target
        for class_name, method_name in targets:
            try:
                diagram = analyzer.generate_activity_diagram(class_name, method_name)
                
                # Create generator and generate the diagram
                generator = PlantUmlActivityGenerator()
                
                output_file = activity_output_dir / f"{class_name}_{method_name}_activity.puml"
                generator.generate_file(diagram, output_file)
                
                print(f"Generated activity diagram for {class_name}.{method_name}")
                
            except ValueError as e:
                print(f"Could not generate activity diagram for {class_name}.{method_name}: {e}")
    
    # Update the main function to include activity diagram generation
    def main():
        # ... existing code ...
        
        # Generate activity diagrams
        generate_activity_diagrams(base_dir, output_dir)
        
        # ... existing code ...

Step 7: Create a Sample Test
~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a test file to verify the activity diagram extractor:

**File: utils/activity_extractor/tests/test_activity_extractor.py**

.. code-block:: python

    """Tests for activity diagram extractor."""
    
    import ast
    import tempfile
    from pathlib import Path
    
    from ..analyzer import ActivityAnalyzer, FunctionControlFlowVisitor
    from ..generator import PlantUmlActivityGenerator
    from ..models import ActivityDiagram, NodeType
    
    
    class TestActivityExtractor:
        """Tests for the activity diagram extractor."""
        
        def test_function_flow_visitor(self):
            """Test extracting control flow from a function."""
            # Sample function with control flow
            code = """
            def process_order(self, order):
                if not order:
                    return None
                
                if order.status == "pending":
                    order.status = "processing"
                    
                    try:
                        self.validate_order(order)
                    except ValidationError as e:
                        order.status = "error"
                        order.error_message = str(e)
                        return False
                    
                    for item in order.items:
                        if not self.check_inventory(item):
                            order.status = "backordered"
                            return False
                    
                    order.status = "processed"
                    return True
                else:
                    return False
            """
            
            # Parse the code
            tree = ast.parse(code)
            function_def = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_def = node
                    break
            
            assert function_def is not None
            
            # Create visitor and visit the function
            visitor = FunctionControlFlowVisitor("process_order", "OrderProcessor")
            visitor.visit(function_def)
            
            # Check basic structure
            assert len(visitor.nodes) > 0
            assert len(visitor.edges) > 0
            
            # Check that we have start and end nodes
            start_nodes = [n for n in visitor.nodes if n.type == NodeType.START]
            end_nodes = [n for n in visitor.nodes if n.type == NodeType.END]
            assert len(start_nodes) == 1
            assert len(end_nodes) == 1
            
            # Check that we have decision nodes for if statements
            decision_nodes = [n for n in visitor.nodes if n.type == NodeType.DECISION]
            assert len(decision_nodes) >= 3  # At least 3 if statements
        
        def test_generate_activity_diagram(self):
            """Test generating an activity diagram from code."""
            # Create a temporary directory for test files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create a test Python file
                test_file = temp_path / "test_class.py"
                with open(test_file, "w") as f:
                    f.write("""
                    class OrderProcessor:
                        def process_order(self, order):
                            if not order:
                                return None
                            
                            if order.status == "pending":
                                order.status = "processing"
                                
                                try:
                                    self.validate_order(order)
                                except ValidationError as e:
                                    order.status = "error"
                                    order.error_message = str(e)
                                    return False
                                
                                for item in order.items:
                                    if not self.check_inventory(item):
                                        order.status = "backordered"
                                        return False
                                
                                order.status = "processed"
                                return True
                            else:
                                return False
                    """)
                
                # Create analyzer and analyze the file
                analyzer = ActivityAnalyzer(temp_path)
                analyzer.analyze_file(test_file)
                
                # Generate activity diagram
                diagram = analyzer.generate_activity_diagram("OrderProcessor", "process_order")
                
                # Verify diagram structure
                assert diagram.title == "OrderProcessor.process_order Activity"
                assert len(diagram.nodes) > 0
                assert len(diagram.edges) > 0
                assert "OrderProcessor" in diagram.swimlanes
                
                # Create generator and generate PlantUML
                generator = PlantUmlActivityGenerator()
                plantuml_code = generator.generate_plantuml(diagram)
                
                # Check PlantUML output
                assert "@startuml" in plantuml_code
                assert "title OrderProcessor.process_order Activity" in plantuml_code
                assert "@enduml" in plantuml_code
                assert "if" in plantuml_code  # Should have decision nodes
                assert "return" in plantuml_code  # Should have return statements

Step 8: Update Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the UML diagrams documentation to include activity diagrams:

**File: docs/source/uml_diagrams.rst** (partial update)

.. code-block:: rst

    Activity Diagrams
    ----------------
    
    Process Order Flow
    ~~~~~~~~~~~~~~~~~
    
    .. uml:: ../_generated_uml/activity/OrderProcessor_process_order_activity.puml
    
    Generate Sequence Diagram Flow
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    .. uml:: ../_generated_uml/activity/SequenceAnalyzer_generate_sequence_diagram_activity.puml

Step 9: Usage Example
~~~~~~~~~~~~~~~~~~~

Here's how to use the activity diagram extractor:

**Option 1: From the command line**

.. code-block:: bash

    # Extract an activity diagram for a specific class method
    python -m utils.extract_activity --source ./utils --output ./docs/source/_generated_uml/activity --class OrderProcessor --method process_order

**Option 2: From Python code**

.. code-block:: python

    from pathlib import Path
    from utils.activity_extractor import ActivityAnalyzer, PlantUmlActivityGenerator
    
    # Create analyzer and analyze source code
    analyzer = ActivityAnalyzer("./utils")
    analyzer.analyze_directory()
    
    # Generate activity diagram for a specific class method
    diagram = analyzer.generate_activity_diagram("OrderProcessor", "process_order")
    
    # Generate PlantUML file
    generator = PlantUmlActivityGenerator()
    output_path = Path("docs/source/_generated_uml/activity/OrderProcessor_process_order_activity.puml")
    generator.generate_file(diagram, output_path)

**Option 3: Using run_uml_generator.py**

.. code-block:: bash

    # Run the UML generator which now includes activity diagram generation
    python -m utils.run_uml_generator

Conclusion
----------

This implementation guide provides a complete approach for adding activity diagram extraction to the UML generator. The implementation follows the same pattern as the sequence extractor, using AST-based static analysis to extract control flow from Python code.

Key files created:

- ``utils/activity_extractor/models.py`` - Data models for activity diagrams
- ``utils/activity_extractor/analyzer.py`` - AST-based analyzer for control flow
- ``utils/activity_extractor/generator.py`` - PlantUML generator for activity diagrams
- ``utils/activity_extractor/__init__.py`` - Package initialization
- ``utils/extract_activity.py`` - Command-line tool
- ``utils/activity_extractor/tests/test_activity_extractor.py`` - Tests

The activity diagram extractor can analyze Python functions and methods to extract control flow, including:

- If-else conditions
- For and while loops
- Try-except blocks
- Return statements

The extracted diagrams show the flow of execution through code, making it easier to understand complex methods and algorithms.

Implementation Diff
-----------------

Below is a diff showing the changes needed to implement the activity diagram extractor:

.. code-block:: diff

    # Create directories
    + mkdir -p utils/activity_extractor
    + mkdir -p utils/activity_extractor/tests
    + mkdir -p docs/source/_generated_uml/activity

    # Create files
    + touch utils/activity_extractor/__init__.py
    + touch utils/activity_extractor/models.py
    + touch utils/activity_extractor/analyzer.py
    + touch utils/activity_extractor/generator.py
    + touch utils/extract_activity.py
    + touch utils/activity_extractor/tests/test_activity_extractor.py

    # Modify run_uml_generator.py
    diff --git a/utils/run_uml_generator.py b/utils/run_uml_generator.py
    index 1234567..abcdefg 100644
    --- a/utils/run_uml_generator.py
    +++ b/utils/run_uml_generator.py
    @@ -10,6 +10,7 @@ from utils.uml_generator.filesystem import DefaultFileSystem
     from utils.uml_generator.factories import DefaultGeneratorFactory
     from utils.uml_generator.service import UmlGeneratorService
     from utils.sequence_extractor import SequenceAnalyzer, PlantUmlSequenceGenerator
    +from utils.activity_extractor import ActivityAnalyzer, PlantUmlActivityGenerator
     
     
     def generate_class_diagrams(base_dir: Path, output_dir: Path) -> None:
    @@ -75,6 +76,36 @@ def generate_sequence_diagrams(base_dir: Path, output_dir: Path) -> None:
                 f"Could not generate sequence diagram for {module_path}: {e}"
             )
     
    +def generate_activity_diagrams(base_dir: Path, output_dir: Path) -> None:
    +    """Generate activity diagrams from Python code."""
    +    print("Generating activity diagrams...")
    +    
    +    # Define the source directory to analyze
    +    source_dir = base_dir / "utils"
    +    
    +    # Create the output directory
    +    activity_output_dir = output_dir / "activity"
    +    activity_output_dir.mkdir(parents=True, exist_ok=True)
    +    
    +    # Create analyzer and analyze the source
    +    analyzer = ActivityAnalyzer(source_dir)
    +    analyzer.analyze_directory()
    +    
    +    # Define classes and methods to generate diagrams for
    +    targets = [
    +        ("SequenceAnalyzer", "generate_sequence_diagram"),
    +        ("PlantUmlGenerator", "generate_diagram"),
    +        # Add more targets as needed
    +    ]
    +    
    +    # Generate diagrams for each target
    +    for class_name, method_name in targets:
    +        try:
    +            diagram = analyzer.generate_activity_diagram(class_name, method_name)
    +            generator = PlantUmlActivityGenerator()
    +            output_file = activity_output_dir / f"{class_name}_{method_name}_activity.puml"
    +            generator.generate_file(diagram, output_file)
    +            print(f"Generated activity diagram for {class_name}.{method_name}")
    +        except ValueError as e:
    +            print(f"Could not generate activity diagram for {class_name}.{method_name}: {e}")
    +
     def main():
         """Run the UML generator."""
         base_dir = Path(__file__).parent.parent
    @@ -87,6 +118,9 @@ def main():
         # Generate sequence diagrams from Python modules
         generate_sequence_diagrams(base_dir, output_dir)
         
    +    # Generate activity diagrams
    +    generate_activity_diagrams(base_dir, output_dir)
    +    
         print(f"UML diagrams generated in {output_dir}")
     
     
    # Update docs/source/uml_diagrams.rst
    diff --git a/docs/source/uml_diagrams.rst b/docs/source/uml_diagrams.rst
    index 1234567..abcdefg 100644
    --- a/docs/source/uml_diagrams.rst
    +++ b/docs/source/uml_diagrams.rst
    @@ -20,3 +20,14 @@ Authentication Flow
     ~~~~~~~~~~~~~~~~~~
     
     .. uml:: ../_generated_uml/sequence/auth_flow.puml
    +
    +Activity Diagrams
    +----------------
    +
    +Process Order Flow
    +~~~~~~~~~~~~~~~~~
    +
    +.. uml:: ../_generated_uml/activity/OrderProcessor_process_order_activity.puml
    +
    +Generate Sequence Diagram Flow
    +~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    +
    +.. uml:: ../_generated_uml/activity/SequenceAnalyzer_generate_sequence_diagram_activity.puml