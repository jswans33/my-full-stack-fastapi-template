"""
Code Analyzer for PlantUML

This module analyzes Python code and generates PlantUML diagrams based on the code structure.
It extracts classes, functions, and relationships between them.
"""

import ast
from pathlib import Path
from typing import TypedDict

from .core import ensure_dir_exists, setup_logger
from .exceptions import (
    AnalyzerError,
    DiagramGenerationError,
    InvalidPathError,
    NoFilesAnalyzedError,
    ParseError,
)
from .settings import settings


# Define a TypedDict for module information
class ModuleInfo(TypedDict):
    imports: set[str]
    classes: list[str]
    functions: list[str]


# Set up logger
logger = setup_logger("code_analyzer")


class CodeVisitor(ast.NodeVisitor):
    """AST visitor that extracts classes, functions, and relationships from Python code."""

    def __init__(self, filename: str | Path, module_name: str):
        self.filename = str(filename)
        self.module_name = module_name
        self.classes: dict[str, dict] = {}
        self.functions: dict[str, dict] = {}
        self.imports: dict[str, str] = {}
        self.relationships: list[tuple[str, str, str]] = []
        self.current_class: str | None = None
        self.current_function: str | None = None
        self.base_classes: dict[str, list[str]] = {}
        self.method_calls: list[tuple[str, str, str]] = []
        logger.info(f"Analyzing file: {filename} (module: {module_name})")

    # Note: We're keeping the method names as-is despite the N802 warnings
    # because these are overriding methods from ast.NodeVisitor and need to match
    # the expected method names for the visitor pattern to work correctly.

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        """Visit a class definition."""
        class_name = f"{self.module_name}.{node.name}"
        logger.debug(f"Found class: {class_name}")

        # Store class information
        self.classes[class_name] = {
            "name": node.name,
            "full_name": class_name,
            "methods": [],
            "attributes": [],
            "docstring": ast.get_docstring(node),
            "lineno": node.lineno,
        }

        # Store base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
                self.relationships.append((class_name, base.id, "inherits"))
                logger.debug(f"  Inherits from: {base.id}")
            elif isinstance(base, ast.Attribute):
                base_name = self._get_attribute_name(base)
                bases.append(base_name)
                self.relationships.append((class_name, base_name, "inherits"))
                logger.debug(f"  Inherits from: {base_name}")

        self.base_classes[class_name] = bases

        # Visit class body with this class as the current class
        old_class = self.current_class
        self.current_class = class_name
        for item in node.body:
            self.visit(item)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        """Visit a function definition."""
        if self.current_class:
            # This is a method
            method_name = node.name
            full_name = f"{self.current_class}.{method_name}"
            logger.debug(f"Found method: {full_name}")

            # Add to class methods
            self.classes[self.current_class]["methods"].append(
                {
                    "name": method_name,
                    "full_name": full_name,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node),
                    "lineno": node.lineno,
                },
            )

            # Check if it's a special method
            if method_name.startswith("__") and method_name.endswith("__"):
                logger.debug(f"  Special method: {method_name}")
        else:
            # This is a standalone function
            function_name = f"{self.module_name}.{node.name}"
            logger.debug(f"Found function: {function_name}")

            self.functions[function_name] = {
                "name": node.name,
                "full_name": function_name,
                "args": [arg.arg for arg in node.args.args],
                "docstring": ast.get_docstring(node),
                "lineno": node.lineno,
            }

        # Visit function body
        old_function = self.current_function
        self.current_function = (
            function_name
            if not self.current_class
            else f"{self.current_class}.{node.name}"
        )
        for item in node.body:
            self.visit(item)
        self.current_function = old_function

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa: N802
        """Visit an assignment."""
        if self.current_class:
            # Check if this is a class attribute assignment
            for target in node.targets:
                if isinstance(target, ast.Name):
                    attr_name = target.id
                    if not attr_name.startswith("_") or attr_name.startswith("__"):
                        logger.debug(f"  Found attribute: {attr_name}")
                        self.classes[self.current_class]["attributes"].append(
                            {
                                "name": attr_name,
                                "lineno": node.lineno,
                            },
                        )

        # Continue visiting
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:  # noqa: N802
        """Visit an annotated assignment."""
        if self.current_class and isinstance(node.target, ast.Name):
            attr_name = node.target.id
            if not attr_name.startswith("_") or attr_name.startswith("__"):
                logger.debug(f"  Found annotated attribute: {attr_name}")

                # Get the type annotation if possible
                type_annotation = ""
                if isinstance(node.annotation, ast.Name):
                    type_annotation = node.annotation.id
                elif isinstance(node.annotation, ast.Subscript) and isinstance(
                    node.annotation.value, ast.Name
                ):
                    type_annotation = node.annotation.value.id

                self.classes[self.current_class]["attributes"].append(
                    {
                        "name": attr_name,
                        "type": type_annotation,
                        "lineno": node.lineno,
                    },
                )

        # Continue visiting
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        """Visit an import statement."""
        for name in node.names:
            self.imports[name.asname or name.name] = name.name
            logger.debug(f"Import: {name.name} as {name.asname or name.name}")

        # Continue visiting
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        """Visit an import from statement."""
        if node.module:
            for name in node.names:
                imported_name = name.name
                as_name = name.asname or imported_name
                full_name = f"{node.module}.{imported_name}"
                self.imports[as_name] = full_name
                logger.debug(f"ImportFrom: {full_name} as {as_name}")

        # Continue visiting
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        """Visit a function call."""
        if isinstance(node.func, ast.Attribute) and isinstance(
            node.func.value, ast.Name
        ):
            # This might be a method call on an object
            obj_name = node.func.value.id
            method_name = node.func.attr

            if self.current_function:
                caller = self.current_function
                called = f"{obj_name}.{method_name}"
                self.method_calls.append((caller, called, "calls"))
                logger.debug(f"Method call: {caller} -> {called}")

        # Continue visiting
        self.generic_visit(node)

    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get the full name of an attribute."""
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        if isinstance(node.value, ast.Attribute):
            return f"{self._get_attribute_name(node.value)}.{node.attr}"
        return node.attr


def analyze_file(file_path: str | Path) -> CodeVisitor | None:
    """
    Analyze a Python file and extract its structure.

    Args:
        file_path: Path to the Python file

    Returns:
        CodeVisitor with the extracted information

    Raises:
        ParseError: If there is an error parsing the file
    """
    path = Path(file_path)
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        module_name = path.stem
        visitor = CodeVisitor(path, module_name)
        visitor.visit(tree)
        return visitor
    except Exception as e:
        raise ParseError(str(path), e)


def analyze_directory(
    directory: str | Path,
    exclude_dirs: list[str] | None = None,
) -> list[CodeVisitor]:
    """
    Analyze all Python files in a directory and its subdirectories.

    Args:
        directory: Directory to analyze
        exclude_dirs: List of directory names to exclude

    Returns:
        List of CodeVisitor objects with the extracted information

    Raises:
        AnalyzerError: If there is an error analyzing the directory
    """
    if exclude_dirs is None:
        exclude_dirs = ["__pycache__", "venv", ".venv", ".git", "node_modules"]

    try:
        path = Path(directory)
        visitors = []
        logger.info(f"Analyzing directory: {path}")

        # Use pathlib's rglob to find all Python files
        for file_path in path.rglob("*.py"):
            # Skip files in excluded directories
            if any(d in file_path.parts for d in exclude_dirs):
                continue

            try:
                visitor = analyze_file(file_path)
                if visitor:
                    visitors.append(visitor)
            except ParseError as e:
                logger.warning(str(e))

        logger.info(f"Analyzed {len(visitors)} Python files")
        return visitors
    except Exception as e:
        raise AnalyzerError(f"Error analyzing directory {directory}: {e}")


def _add_classes_to_diagram(visitors: list[CodeVisitor], diagram: list[str]) -> None:
    """Add class definitions to the diagram."""
    for visitor in visitors:
        for class_name, class_info in visitor.classes.items():
            # Start the class definition
            diagram.append(
                f'class "{class_info["name"]}" as {class_name.replace(".", "_")} {{',
            )

            # Add attributes
            for attr in class_info["attributes"]:
                attr_type = attr.get("type", "")
                if attr_type:
                    diagram.append(f"  {attr['name']}: {attr_type}")
                else:
                    diagram.append(f"  {attr['name']}")

            # Add methods
            for method in class_info["methods"]:
                args_str = ", ".join(method["args"])
                diagram.append(f"  +{method['name']}({args_str})")

            # End the class definition
            diagram.append("}")
            diagram.append("")


def _add_functions_to_diagram(visitors: list[CodeVisitor], diagram: list[str]) -> None:
    """Add standalone functions to the diagram."""
    for visitor in visitors:
        for func_name, func_info in visitor.functions.items():
            # Add the function as a class with a stereotype
            diagram.append(
                f'class "{func_info["name"]}" as {func_name.replace(".", "_")} <<function>> {{',
            )
            args_str = ", ".join(func_info["args"])
            diagram.append(f"  +{func_info['name']}({args_str})")
            diagram.append("}")
            diagram.append("")


def _add_relationships_to_diagram(
    visitors: list[CodeVisitor],
    diagram: list[str],
    include_functions: bool,
) -> None:
    """Add relationships between classes and functions to the diagram."""
    # Add inheritance relationships
    for visitor in visitors:
        for class_name, bases in visitor.base_classes.items():
            for base in bases:
                # Check if the base class is a known class or an import
                base_full = visitor.imports.get(base, base)
                diagram.append(
                    f"{class_name.replace('.', '_')} --|> {base_full.replace('.', '_')}",
                )

    # Add method call relationships (simplified)
    method_calls_added: set[str] = set()
    for visitor in visitors:
        for caller, called, _ in visitor.method_calls:
            # Only add each relationship once and only if both caller and called are known
            rel_key = f"{caller}_{called}"
            if rel_key not in method_calls_added:
                # Check if the called method is in our known classes/methods
                called_parts = called.split(".")
                if (
                    len(called_parts) >= 2
                    and called_parts[0] in visitor.imports
                    and include_functions
                ):
                    # This is a call to an imported module
                    diagram.append(
                        f"{caller.replace('.', '_')} ..> {called.replace('.', '_')} : calls",
                    )
                    method_calls_added.add(rel_key)


def generate_class_diagram(
    visitors: list[CodeVisitor],
    include_functions: bool = False,
) -> str:
    """
    Generate a PlantUML class diagram from the analyzed code.

    Args:
        visitors: List of CodeVisitor objects with the extracted information
        include_functions: Whether to include standalone functions in the diagram

    Returns:
        PlantUML diagram as a string

    Raises:
        DiagramGenerationError: If there is an error generating the diagram
    """
    try:
        logger.info("Generating class diagram")

        # Start the diagram
        diagram = [
            '@startuml "Code Analysis Class Diagram"',
            "",
            "' This diagram was automatically generated by the code analyzer",
            "",
        ]

        # Add classes, functions, and relationships using helper functions
        _add_classes_to_diagram(visitors, diagram)

        if include_functions:
            _add_functions_to_diagram(visitors, diagram)

        _add_relationships_to_diagram(visitors, diagram, include_functions)

        # End the diagram
        diagram.append("")
        diagram.append("@enduml")

        return "\n".join(diagram)
    except Exception as e:
        raise DiagramGenerationError(f"Error generating class diagram: {e}")


def generate_module_diagram(visitors: list[CodeVisitor]) -> str:
    """
    Generate a PlantUML component diagram showing module dependencies.

    Args:
        visitors: List of CodeVisitor objects with the extracted information

    Returns:
        PlantUML diagram as a string

    Raises:
        DiagramGenerationError: If there is an error generating the diagram
    """
    try:
        logger.info("Generating module diagram")

        # Start the diagram
        diagram = [
            '@startuml "Code Analysis Module Diagram"',
            "",
            "' This diagram was automatically generated by the code analyzer",
            "",
        ]

        # Track modules and their imports
        modules: dict[str, ModuleInfo] = {}

        # Add all modules
        for visitor in visitors:
            module_name = visitor.module_name
            if module_name not in modules:
                modules[module_name] = {
                    "imports": set(),
                    "classes": [
                        class_info["name"] for class_info in visitor.classes.values()
                    ],
                    "functions": [
                        func_info["name"] for func_info in visitor.functions.values()
                    ],
                }

            # Add imports
            for _, import_name in visitor.imports.items():
                # Extract the top-level module
                top_module = import_name.split(".")[0]
                if top_module != module_name:  # Don't add self-imports
                    modules[module_name]["imports"].add(top_module)

        # Add components for each module
        for module_name in modules:
            diagram.append(f"[{module_name}] as {module_name.replace('.', '_')}")

        diagram.append("")

        # Add dependencies between modules
        for module_name, module_info in modules.items():
            for imported_module in module_info["imports"]:
                if (
                    imported_module in modules
                ):  # Only add if the imported module is in our analysis
                    diagram.append(
                        f"{module_name.replace('.', '_')} --> {imported_module.replace('.', '_')}",
                    )

        # End the diagram
        diagram.append("")
        diagram.append("@enduml")

        return "\n".join(diagram)
    except Exception as e:
        raise DiagramGenerationError(f"Error generating module diagram: {e}")


def save_diagram(diagram: str, output_file: str | Path) -> None:
    """
    Save a PlantUML diagram to a file.

    Args:
        diagram: PlantUML diagram as a string
        output_file: Path to save the diagram to

    Raises:
        DiagramGenerationError: If there is an error saving the diagram
    """
    try:
        path = Path(output_file)
        ensure_dir_exists(path.parent)
        path.write_text(diagram, encoding="utf-8")
        logger.info(f"Saved diagram to {path}")
    except Exception as e:
        raise DiagramGenerationError(f"Error saving diagram to {output_file}: {e}")


def analyze_and_generate_diagram(
    path: str | Path = ".",
    output: str | Path | None = None,
    modules: bool = False,
    functions: bool = False,
) -> Path:
    """
    Analyze code and generate a PlantUML diagram.

    This is the main entry point for code analysis functionality.

    Args:
        path: Path to the Python file or directory to analyze
        output: Output file for the PlantUML diagram
        modules: Whether to generate a module diagram instead of a class diagram
        functions: Whether to include standalone functions in the class diagram

    Returns:
        Path to the generated diagram file

    Raises:
        InvalidPathError: If the provided path is invalid
        NoFilesAnalyzedError: If no Python files were successfully analyzed
        AnalyzerError: If there is an error during analysis
    """
    try:
        input_path = Path(path)

        # Analyze the code
        if input_path.is_dir():
            logger.info(f"Analyzing directory: {input_path}")
            visitors = analyze_directory(input_path)
        elif input_path.is_file() and input_path.suffix == ".py":
            logger.info(f"Analyzing file: {input_path}")
            visitor = analyze_file(input_path)
            visitors = [visitor] if visitor else []
        else:
            logger.error(f"Invalid path: {input_path}")
            raise InvalidPathError(str(input_path))

        if not visitors:
            logger.error("No Python files were successfully analyzed")
            raise NoFilesAnalyzedError()

        # Generate the diagram
        if modules:
            diagram = generate_module_diagram(visitors)
            diagram_type = "module"
        else:
            diagram = generate_class_diagram(visitors, functions)
            diagram_type = "class"

        # Determine the output file
        if output:
            output_path = Path(output)
        else:
            # Use a default output file based on the input path
            base_name = input_path.stem if input_path.is_file() else input_path.name
            output_path = (
                settings.output_dir
                / "code_analysis"
                / f"{base_name}_{diagram_type}_diagram.puml"
            )

        # Save the diagram
        save_diagram(diagram, output_path)
        logger.info(f"Generated {diagram_type} diagram: {output_path}")

        return output_path
    except (InvalidPathError, NoFilesAnalyzedError):
        raise
    except Exception as e:
        raise AnalyzerError(f"Error analyzing and generating diagram: {e}")
