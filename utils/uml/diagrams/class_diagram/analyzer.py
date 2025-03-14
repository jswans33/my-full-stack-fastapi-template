"""Analyzer for extracting class diagrams from Python code.

This module provides functionality for analyzing Python code and extracting
class diagrams from it.
"""

import ast
import logging
import os
from pathlib import Path
from typing import Any

from utils.uml.core.exceptions import ParserError
from utils.uml.core.filesystem import FileSystem
from utils.uml.diagrams.base import BaseDiagramAnalyzer
from utils.uml.diagrams.class_diagram.models import (
    AttributeModel,
    ClassDiagram,
    ClassModel,
    FileModel,
    FunctionModel,
    ImportModel,
    MethodModel,
    ParameterModel,
    RelationshipModel,
    TypeAnnotation,
    Visibility,
)


class ClassAnalyzer(BaseDiagramAnalyzer):
    """Analyzer for extracting class diagrams from Python code."""

    def __init__(self, file_system: FileSystem):
        """Initialize the class analyzer.

        Args:
            file_system: The file system implementation to use
        """
        super().__init__(file_system)
        self.logger = logging.getLogger(__name__)
        self.processed_files: set[Path] = set()
        self.current_module = ""

    def analyze(
        self,
        path: str | Path,
        module_name: str | None = None,
        exclude_patterns: list[str] | None = None,
        include_private: bool = False,
        **kwargs: Any,
    ) -> ClassDiagram:
        """Analyze the source code at the given path and generate a class diagram.

        Args:
            path: Path to the source code to analyze
            module_name: Optional name of the module being analyzed
            exclude_patterns: Optional list of patterns to exclude
            include_private: Whether to include private members
            **kwargs: Additional analyzer-specific arguments

        Returns:
            A class diagram model

        Raises:
            ParserError: If the analysis fails
        """
        try:
            # Create the diagram
            diagram = ClassDiagram(
                name=module_name
                or (Path(path).name if isinstance(path, str) else path.name),
            )

            # Determine if we're analyzing a directory or a single file
            target_path = Path(path) if isinstance(path, str) else path

            if target_path.is_dir():
                self._analyze_directory(
                    diagram,
                    target_path,
                    exclude_patterns or [],
                    include_private,
                )
            else:
                self._analyze_file(
                    diagram,
                    target_path,
                    include_private=include_private,
                )

            # Process relationships between classes
            self._process_relationships(diagram)

            return diagram
        except Exception as e:
            raise ParserError(f"Failed to analyze code at {path}: {e}", cause=e)

    def _analyze_directory(
        self,
        diagram: ClassDiagram,
        directory: Path,
        exclude_patterns: list[str],
        include_private: bool,
    ) -> None:
        """Analyze all Python files in a directory.

        Args:
            diagram: The class diagram to populate
            directory: The directory to analyze
            exclude_patterns: Patterns to exclude
            include_private: Whether to include private members
        """
        for root, _, files in os.walk(directory):
            # Skip directories matching exclude patterns
            if any(pattern in root for pattern in exclude_patterns):
                continue

            # Process Python files
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(os.path.join(root, file))

                    # Skip files matching exclude patterns
                    if any(pattern in str(file_path) for pattern in exclude_patterns):
                        continue

                    self._analyze_file(
                        diagram,
                        file_path,
                        include_private=include_private,
                    )

    def _analyze_file(
        self,
        diagram: ClassDiagram,
        file_path: Path,
        include_private: bool = False,
    ) -> None:
        """Analyze a single Python file.

        Args:
            diagram: The class diagram to populate
            file_path: The file to analyze
            include_private: Whether to include private members
        """
        # Skip if already processed
        if file_path in self.processed_files:
            return

        self.processed_files.add(file_path)

        try:
            # Read and parse the file
            code = self.file_system.read_file(file_path)
            tree = ast.parse(code)

            # Create file model
            file_model = FileModel(path=file_path)

            # Extract imports, classes, and functions
            visitor = ClassDefinitionVisitor(
                file_path=file_path,
                include_private=include_private,
            )
            visitor.visit(tree)

            # Add imports, classes, and functions to the file model
            file_model.imports = visitor.imports
            file_model.classes = visitor.classes
            file_model.functions = visitor.functions

            # Add the file model to the diagram
            diagram.add_file(file_model)

        except SyntaxError as e:
            self.logger.error(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Failed to analyze file {file_path}: {e}")

    def _process_relationships(self, diagram: ClassDiagram) -> None:
        """Process relationships between classes.

        Args:
            diagram: The class diagram to process
        """
        # Dictionary to map class names to their full names
        class_dict: dict[str, tuple[str, ClassModel]] = {}

        # Build the class dictionary
        for file in diagram.files:
            for cls in file.classes:
                class_dict[cls.name] = (cls.name, cls)

        # Process inheritance relationships
        for file in diagram.files:
            for cls in file.classes:
                # Add inheritance relationships
                for base in cls.bases:
                    if base in class_dict:
                        base_name, _ = class_dict[base]
                        relationship = RelationshipModel(
                            source=cls.name,
                            target=base_name,
                            type="--|>",  # UML inheritance
                        )
                        diagram.add_relationship(relationship)


class ClassDefinitionVisitor(ast.NodeVisitor):
    """AST visitor that extracts class and function definitions."""

    def __init__(
        self,
        file_path: Path,
        include_private: bool = False,
    ):
        """Initialize the class definition visitor.

        Args:
            file_path: The path to the file being analyzed
            include_private: Whether to include private members
        """
        self.file_path = file_path
        self.include_private = include_private
        self.imports: list[ImportModel] = []
        self.classes: list[ClassModel] = []
        self.functions: list[FunctionModel] = []
        self.module_name = file_path.stem

    def visit_Import(self, node: ast.Import) -> None:
        """Visit an import node.

        Args:
            node: The AST node representing an import
        """
        for name in node.names:
            import_model = ImportModel(
                module=name.name,
                name=name.name.split(".")[-1],
                alias=name.asname,
            )
            self.imports.append(import_model)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit an import from node.

        Args:
            node: The AST node representing an import from
        """
        if node.module is None:
            return

        for name in node.names:
            import_model = ImportModel(
                module=node.module,
                name=name.name,
                alias=name.asname,
            )
            self.imports.append(import_model)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition node.

        Args:
            node: The AST node representing a class definition
        """
        # Skip private classes if not included
        if not self.include_private and node.name.startswith("_"):
            return

        # Create class model
        class_model = ClassModel(
            name=node.name,
            filename=str(self.file_path),
            bases=[
                self._get_base_name(base)
                for base in node.bases
                if isinstance(base, (ast.Name, ast.Attribute))
            ],
            docstring=ast.get_docstring(node),
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
        )

        # Process class body
        for item in node.body:
            # Process attribute assignments
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        # Class attribute
                        attr_name = target.id
                        if self.include_private or not attr_name.startswith("_"):
                            visibility = (
                                Visibility.PRIVATE
                                if attr_name.startswith("__")
                                else Visibility.PROTECTED
                                if attr_name.startswith("_")
                                else Visibility.PUBLIC
                            )

                            # Get default value as string
                            try:
                                default_value = ast.unparse(item.value)
                            except (AttributeError, ValueError):
                                default_value = None

                            attr = AttributeModel(
                                name=attr_name,
                                type_annotation="Any",  # No type info available
                                visibility=visibility,
                                default_value=default_value,
                            )
                            class_model.attributes.append(attr)

            # Process annotated assignments
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attr_name = item.target.id
                if self.include_private or not attr_name.startswith("_"):
                    visibility = (
                        Visibility.PRIVATE
                        if attr_name.startswith("__")
                        else Visibility.PROTECTED
                        if attr_name.startswith("_")
                        else Visibility.PUBLIC
                    )

                    # Get type annotation
                    type_annotation = self._get_type_annotation(item.annotation)

                    # Get default value if present
                    default_value = None
                    if item.value:
                        try:
                            default_value = ast.unparse(item.value)
                        except (AttributeError, ValueError):
                            pass

                    attr = AttributeModel(
                        name=attr_name,
                        type_annotation=type_annotation,
                        visibility=visibility,
                        default_value=default_value,
                    )
                    class_model.attributes.append(attr)

            # Process methods
            elif isinstance(item, ast.FunctionDef):
                method_name = item.name
                if (
                    self.include_private
                    or not method_name.startswith("_")
                    or method_name == "__init__"
                ):
                    method = self._process_function(item, is_class_method=True)
                    if isinstance(
                        method, MethodModel
                    ):  # Type check to ensure correct type
                        class_model.methods.append(method)

        # Add the class model
        self.classes.append(class_model)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition node.

        Args:
            node: The AST node representing a function definition
        """
        # Skip private functions if not included
        if not self.include_private and node.name.startswith("_"):
            return

        # Only process top-level functions (not inside a class)
        # We can tell by checking the context/parent type
        for ancestor in ast.iter_child_nodes(node):
            if isinstance(ancestor, ast.ClassDef):
                # This is a method inside a class, already handled by visit_ClassDef
                return

        # This is a top-level function
        function = self._process_function(node, is_class_method=False)
        if isinstance(function, FunctionModel):
            self.functions.append(function)

        self.generic_visit(node)

    def _process_function(
        self,
        node: ast.FunctionDef,
        is_class_method: bool = False,
    ) -> MethodModel | FunctionModel:
        """Process a function definition.

        Args:
            node: The AST node representing a function definition
            is_class_method: Whether this is a method in a class

        Returns:
            A method model if is_class_method is True, otherwise a function model
        """
        # Determine visibility
        visibility = (
            Visibility.PRIVATE
            if node.name.startswith("__")
            else Visibility.PROTECTED
            if node.name.startswith("_")
            else Visibility.PUBLIC
        )

        # Process parameters
        parameters: list[ParameterModel] = []
        for i, arg in enumerate(node.args.args):
            # Skip 'self' parameter for class methods
            if is_class_method and i == 0 and arg.arg == "self":
                continue

            # Get type annotation if present
            type_annotation = (
                self._get_type_annotation(arg.annotation) if arg.annotation else "Any"
            )

            # Get default value if present
            default_value = None
            if i >= len(node.args.args) - len(node.args.defaults):
                default_idx = i - (len(node.args.args) - len(node.args.defaults))
                try:
                    default_value = ast.unparse(node.args.defaults[default_idx])
                except (AttributeError, ValueError, IndexError):
                    pass

            param = ParameterModel(
                name=arg.arg,
                type_annotation=type_annotation,
                default_value=default_value,
            )
            parameters.append(param)

        # Get return type annotation
        return_type = (
            self._get_type_annotation(node.returns) if node.returns else "None"
        )

        # Check for staticmethod or classmethod decorators
        is_static = any(
            self._get_decorator_name(d) == "staticmethod" for d in node.decorator_list
        )
        is_classmethod = any(
            self._get_decorator_name(d) == "classmethod" for d in node.decorator_list
        )

        # Create appropriate model
        if is_class_method:
            return MethodModel(
                name=node.name,
                parameters=parameters,
                return_type=return_type,
                visibility=visibility,
                is_static=is_static,
                is_classmethod=is_classmethod,
                docstring=ast.get_docstring(node),
                decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            )
        return FunctionModel(
            name=node.name,
            parameters=parameters,
            return_type=return_type,
            visibility=visibility,
        )

    def _get_base_name(self, node: ast.expr) -> str:
        """Get the name of a base class.

        Args:
            node: The AST node representing a base class

        Returns:
            The name of the base class
        """
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            try:
                return ast.unparse(node)
            except (AttributeError, ValueError):
                return f"{self._get_base_name(node.value)}.{node.attr}"
        return "object"  # Default base class

    def _get_decorator_name(self, node: ast.expr) -> str:
        """Get the name of a decorator.

        Args:
            node: The AST node representing a decorator

        Returns:
            The name of the decorator
        """
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node, ast.Attribute):
            try:
                return ast.unparse(node)
            except (AttributeError, ValueError):
                return f"{self._get_base_name(node.value)}.{node.attr}"
        try:
            return ast.unparse(node)
        except (AttributeError, ValueError):
            return "unknown"

    def _get_type_annotation(self, node: ast.expr) -> TypeAnnotation:
        """Get a string representation of a type annotation.

        Args:
            node: The AST node representing a type annotation

        Returns:
            A string representation of the type annotation
        """
        try:
            return ast.unparse(node)
        except (AttributeError, ValueError):
            if isinstance(node, ast.Name):
                return node.id
            if isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Name):
                    value_name = node.value.id
                    try:
                        slice_name = ast.unparse(node.slice)
                        return f"{value_name}[{slice_name}]"
                    except (AttributeError, ValueError):
                        return f"{value_name}[...]"
                return "..."
            if isinstance(node, ast.Attribute):
                return f"{self._get_base_name(node.value)}.{node.attr}"
            return "Any"  # Default type
