"""
Code analysis implementation.

This module provides the core functionality for analyzing Python source code
and building a representation of its structure.
"""

import ast
from pathlib import Path

from utils.puml.core import setup_logger
from utils.puml.exceptions import AnalyzerError, ParseError
from utils.puml.models import Class, Function, Module

# Set up logger
logger = setup_logger("analyzer")


class CodeVisitor(ast.NodeVisitor):
    """AST visitor that extracts code structure from Python source."""

    def __init__(self, path: Path):
        self.module = Module(path=path, name=path.stem)
        self.current_class: Class | None = None
        self.current_function: Function | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Process a class definition node."""
        class_name = node.name
        full_name = f"{self.module.name}.{class_name}"

        # Get base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(self._get_attribute_name(base))

        # Create class object
        class_obj = Class(
            name=class_name,
            full_name=full_name,
            bases=bases,
            docstring=ast.get_docstring(node),
            lineno=node.lineno,
        )

        # Add inheritance relationships
        for base in bases:
            class_obj.add_relationship(base, "inherits")

        # Process class body
        old_class = self.current_class
        self.current_class = class_obj
        for item in node.body:
            self.visit(item)
        self.current_class = old_class

        # Add class to module
        self.module.add_class(class_obj)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Process a function definition node."""
        func_name = node.name
        parent_name = (
            self.current_class.full_name if self.current_class else self.module.name
        )
        full_name = f"{parent_name}.{func_name}"

        # Create function object
        function = Function(
            name=func_name,
            full_name=full_name,
            args=[arg.arg for arg in node.args.args],
            docstring=ast.get_docstring(node),
            lineno=node.lineno,
            is_method=bool(self.current_class),
        )

        # Add return type annotation if present
        if node.returns:
            if isinstance(node.returns, ast.Name):
                function.return_type = node.returns.id
            elif isinstance(node.returns, ast.Attribute):
                function.return_type = self._get_attribute_name(node.returns)

        # Process function body
        old_function = self.current_function
        self.current_function = function
        for item in node.body:
            self.visit(item)
        self.current_function = old_function

        # Add function to appropriate container
        if self.current_class:
            self.current_class.add_method(function)
        else:
            self.module.add_function(function)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Process an annotated assignment node."""
        if self.current_class and isinstance(node.target, ast.Name):
            attr_name = node.target.id
            if not attr_name.startswith("_") or attr_name.startswith("__"):
                type_annotation = ""
                if isinstance(node.annotation, ast.Name):
                    type_annotation = node.annotation.id
                elif isinstance(node.annotation, ast.Subscript):
                    type_annotation = self._get_subscript_name(node.annotation)

                self.current_class.add_attribute(
                    name=attr_name,
                    type_annotation=type_annotation,
                    lineno=node.lineno,
                )

    def visit_Assign(self, node: ast.Assign) -> None:
        """Process an assignment node."""
        if self.current_class:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    attr_name = target.id
                    if not attr_name.startswith("_") or attr_name.startswith("__"):
                        self.current_class.add_attribute(
                            name=attr_name,
                            lineno=node.lineno,
                        )

    def visit_Import(self, node: ast.Import) -> None:
        """
        Process an import node.

        Handles imports like:
        - import foo
        - import foo.bar
        - import foo as bar
        """
        for name in node.names:
            imported_name = name.name
            as_name = name.asname or imported_name

            # Track both the imported name and any submodules
            parts = imported_name.split(".")
            for i in range(len(parts)):
                partial_import = ".".join(parts[: i + 1])
                self.module.add_import(
                    name=as_name if i == len(parts) - 1 else partial_import,
                    source=partial_import,
                    is_direct=i == len(parts) - 1,
                )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Process an import from node.

        Handles imports like:
        - from foo import bar
        - from foo.bar import baz
        - from foo import bar as baz
        - from . import foo
        - from .foo import bar
        - from ..foo import bar
        """
        # Handle relative imports
        if node.level > 0:
            # Calculate the full module path for relative import
            current_package = self.module.name.split(".")
            if len(current_package) < node.level:
                logger.warning(
                    f"Invalid relative import in {self.module.name}: "
                    f"attempted to go up {node.level} levels but only {len(current_package)} available",
                )
                return

            base_package = ".".join(current_package[: -node.level])
            if node.module:
                base_module = (
                    f"{base_package}.{node.module}" if base_package else node.module
                )
            else:
                base_module = base_package
        else:
            base_module = node.module

        if base_module:
            for name in node.names:
                imported_name = name.name
                as_name = name.asname or imported_name

                # Handle star imports
                if imported_name == "*":
                    self.module.add_import(
                        name="*",
                        source=base_module,
                        is_direct=True,
                        is_star=True,
                    )
                    logger.warning(
                        f"Star import from {base_module} in {self.module.name}"
                    )
                else:
                    full_name = f"{base_module}.{imported_name}"
                    self.module.add_import(
                        name=as_name,
                        source=full_name,
                        is_direct=True,
                    )

    def visit_Call(self, node: ast.Call) -> None:
        """Process a function call node."""
        if isinstance(node.func, ast.Attribute) and isinstance(
            node.func.value,
            ast.Name,
        ):
            if self.current_function:
                obj_name = node.func.value.id
                method_name = node.func.attr
                called = f"{obj_name}.{method_name}"
                self.current_function.add_call(called)

        self.generic_visit(node)

    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get the full name of an attribute node."""
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        if isinstance(node.value, ast.Attribute):
            return f"{self._get_attribute_name(node.value)}.{node.attr}"
        return node.attr

    def _get_subscript_name(self, node: ast.Subscript) -> str:
        """Get the string representation of a subscript type annotation."""
        if isinstance(node.value, ast.Name):
            return node.value.id
        return "Any"  # Default to Any for complex subscripts


def analyze_file(file_path: str | Path) -> Module:
    """
    Analyze a Python file and extract its structure.

    Args:
        file_path: Path to the Python file to analyze

    Returns:
        Module object containing the analyzed code structure

    Raises:
        ParseError: If there is an error parsing the file
    """
    try:
        path = Path(file_path)
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))

        visitor = CodeVisitor(path)
        visitor.visit(tree)

        logger.info(f"Successfully analyzed {path}")
        return visitor.module
    except Exception as e:
        raise ParseError(str(path), e)


def analyze_directory(
    directory: str | Path,
    exclude_dirs: set[str] | None = None,
) -> list[Module]:
    """
    Analyze all Python files in a directory and its subdirectories.

    Args:
        directory: Directory to analyze
        exclude_dirs: Set of directory names to exclude

    Returns:
        List of Module objects containing the analyzed code structure

    Raises:
        AnalyzerError: If there is an error analyzing the directory
    """
    if exclude_dirs is None:
        exclude_dirs = {"__pycache__", ".git", "venv", ".venv", "node_modules"}

    try:
        path = Path(directory)
        modules = []
        logger.info(f"Analyzing directory: {path}")

        for file_path in path.rglob("*.py"):
            if any(d in file_path.parts for d in exclude_dirs):
                continue

            try:
                module = analyze_file(file_path)
                modules.append(module)
            except ParseError as e:
                logger.warning(str(e))

        logger.info(f"Analyzed {len(modules)} Python files")
        return modules
    except Exception as e:
        raise AnalyzerError(f"Error analyzing directory {directory}: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        analyze_file(sys.argv[1])
    else:
        analyze_directory(".")
