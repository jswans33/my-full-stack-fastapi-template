"""Analyzer for extracting sequence diagrams from Python code."""

import ast
import os
from pathlib import Path

from .models import (
    FunctionCall,
    Message,
    MessageType,
    Participant,
    ParticipantType,
    SequenceDiagram,
)


class ClassInfo:
    """Information about a Python class."""

    def __init__(self, name: str, module: str):
        self.name = name
        self.module = module
        self.methods: set[str] = set()
        self.base_classes: list[str] = []

    @property
    def full_name(self) -> str:
        """Get the full name with module."""
        return f"{self.module}.{self.name}"


class MethodCallVisitor(ast.NodeVisitor):
    """AST visitor that extracts method calls."""

    def __init__(self, class_name: str, method_name: str, file_path: str):
        self.class_name = class_name
        self.method_name = method_name
        self.file_path = file_path
        self.calls: list[FunctionCall] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Visit a function call node."""
        # Track the line number
        line_number = getattr(node, "lineno", 0)

        # Handle method calls: obj.method()
        if isinstance(node.func, ast.Attribute) and isinstance(
            node.func.value, ast.Name
        ):
            obj_name = node.func.value.id
            method_name = node.func.attr

            # Skip calls to self
            if obj_name == "self":
                # This is a call to another method in the same class
                self.calls.append(
                    FunctionCall(
                        caller_class=self.class_name,
                        caller_method=self.method_name,
                        called_class=self.class_name,
                        called_method=method_name,
                        line_number=line_number,
                        file_path=self.file_path,
                    )
                )
            else:
                # This is a call to another object's method
                self.calls.append(
                    FunctionCall(
                        caller_class=self.class_name,
                        caller_method=self.method_name,
                        called_class=obj_name,  # This is only the variable name, not necessarily the class
                        called_method=method_name,
                        line_number=line_number,
                        file_path=self.file_path,
                    )
                )

        # Handle constructor calls: ClassName()
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id

            # Assume it's a constructor call if the name is capitalized
            if func_name[0].isupper():
                self.calls.append(
                    FunctionCall(
                        caller_class=self.class_name,
                        caller_method=self.method_name,
                        called_class=func_name,
                        called_method="__init__",
                        is_constructor=True,
                        line_number=line_number,
                        file_path=self.file_path,
                    )
                )
            else:
                # This is a normal function call
                self.calls.append(
                    FunctionCall(
                        caller_class=self.class_name,
                        caller_method=self.method_name,
                        called_class=None,  # It's a standalone function
                        called_method=func_name,
                        line_number=line_number,
                        file_path=self.file_path,
                    )
                )

        # Continue visiting child nodes
        self.generic_visit(node)


class ClassDefVisitor(ast.NodeVisitor):
    """AST visitor that extracts class definitions."""

    def __init__(self, module_name: str, file_path: str):
        self.module_name = module_name
        self.file_path = file_path
        self.classes: dict[str, ClassInfo] = {}
        self.method_calls: list[FunctionCall] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition node."""
        class_name = node.name

        # Create class info
        class_info = ClassInfo(class_name, self.module_name)

        # Extract base classes
        for base in node.bases:
            if isinstance(base, ast.Name):
                class_info.base_classes.append(base.id)

        self.classes[class_name] = class_info

        # Visit all methods in the class
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_name = item.name
                class_info.methods.add(method_name)

                # Find method calls inside this method
                visitor = MethodCallVisitor(class_name, method_name, self.file_path)
                visitor.visit(item)
                self.method_calls.extend(visitor.calls)


class SequenceAnalyzer:
    """Analyzer for extracting sequence diagrams from Python code."""

    def __init__(self, root_dir: str | Path = "."):
        self.root_dir = Path(root_dir)
        self.classes: dict[str, ClassInfo] = {}
        self.function_calls: list[FunctionCall] = []

    def analyze_file(self, file_path: str | Path) -> None:
        """Analyze a single Python file."""
        path = Path(file_path) if isinstance(file_path, str) else file_path

        # Use the file name without extension as module name
        module_name = path.stem

        # Read and parse the file
        with open(path, encoding="utf-8") as f:
            code = f.read()

        try:
            tree = ast.parse(code)

            # Visit the AST to extract classes and method calls
            visitor = ClassDefVisitor(module_name, str(path))
            visitor.visit(tree)

            # Store the results
            self.classes.update(visitor.classes)
            self.function_calls.extend(visitor.method_calls)

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

    def generate_sequence_diagram(
        self, entry_class: str, entry_method: str
    ) -> SequenceDiagram:
        """Generate a sequence diagram starting from an entry point."""
        # Create the diagram
        diagram = SequenceDiagram(title=f"{entry_class}.{entry_method} Sequence")

        # Add the entry point class as a participant
        entry_participant = Participant(name=entry_class, type=ParticipantType.CLASS)
        diagram.add_participant(entry_participant)

        # Process the call graph starting from the entry point
        self._process_call_graph(diagram, entry_class, entry_method)

        return diagram

    def _process_call_graph(
        self,
        diagram: SequenceDiagram,
        caller_class: str,
        caller_method: str,
        level: int = 0,
        processed: set[tuple[str, str]] | None = None,
    ) -> None:
        """Process the call graph recursively."""
        if processed is None:
            processed = set()

        # Avoid infinite recursion
        call_key = (caller_class, caller_method)
        if call_key in processed or level > 10:  # Limit recursion depth
            return

        processed.add(call_key)

        # Find all calls made from this method
        calls = [
            call
            for call in self.function_calls
            if call.caller_class == caller_class and call.caller_method == caller_method
        ]

        for call in calls:
            # Skip if called_class is None (function calls)
            if call.called_class is None:
                continue

            # Add the called class as a participant
            called_participant = Participant(
                name=call.called_class, type=ParticipantType.CLASS
            )
            diagram.add_participant(called_participant)

            # Add the message
            message_type = (
                MessageType.CREATE if call.is_constructor else MessageType.SYNCHRONOUS
            )
            is_self = caller_class == call.called_class

            message = Message(
                from_participant=caller_class,
                to_participant=call.called_class,
                text=call.called_method,
                message_type=message_type,
                is_self_message=is_self,
                level=level,
                method_name=call.called_method,
            )
            diagram.add_message(message)

            # Recursively process the called method
            self._process_call_graph(
                diagram,
                call.called_class,
                call.called_method,
                level + 1,
                processed,
            )

            # Add a return message if it's a synchronous call
            if message_type == MessageType.SYNCHRONOUS and not is_self:
                return_message = Message(
                    from_participant=call.called_class,
                    to_participant=caller_class,
                    text="return",
                    message_type=MessageType.REPLY,
                    level=level,
                )
                diagram.add_message(return_message)
