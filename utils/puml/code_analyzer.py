"""
Code Analyzer for PlantUML

This module analyzes Python code and generates PlantUML diagrams based on the code structure.
It extracts classes, functions, and relationships between them.

Usage:
    python -m utils.puml.code_analyzer --path=<path> --output=<output_file> [--include-modules] [--include-functions]
"""

import argparse
import ast
import logging
import os
import sys

from utils.puml.config import OUTPUT_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("code_analyzer")


class CodeVisitor(ast.NodeVisitor):
    """AST visitor that extracts classes, functions, and relationships from Python code."""

    def __init__(self, filename: str, module_name: str):
        self.filename = filename
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

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
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

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
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

    def visit_Assign(self, node: ast.Assign) -> None:
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

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visit an annotated assignment."""
        if self.current_class and isinstance(node.target, ast.Name):
            attr_name = node.target.id
            if not attr_name.startswith("_") or attr_name.startswith("__"):
                logger.debug(f"  Found annotated attribute: {attr_name}")

                # Get the type annotation if possible
                type_annotation = ""
                if isinstance(node.annotation, ast.Name):
                    type_annotation = node.annotation.id
                elif isinstance(node.annotation, ast.Subscript):
                    if isinstance(node.annotation.value, ast.Name):
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

    def visit_Import(self, node: ast.Import) -> None:
        """Visit an import statement."""
        for name in node.names:
            self.imports[name.asname or name.name] = name.name
            logger.debug(f"Import: {name.name} as {name.asname or name.name}")

        # Continue visiting
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
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

    def visit_Call(self, node: ast.Call) -> None:
        """Visit a function call."""
        if isinstance(node.func, ast.Attribute) and isinstance(
            node.func.value,
            ast.Name,
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


def analyze_file(file_path: str) -> CodeVisitor | None:
    """
    Analyze a Python file and extract its structure.

    Args:
        file_path: Path to the Python file

    Returns:
        CodeVisitor with the extracted information, or None if the file couldn't be parsed
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        # Parse the source code into an AST
        tree = ast.parse(source, filename=file_path)

        # Get the module name from the file path
        module_name = os.path.splitext(os.path.basename(file_path))[0]

        # Visit the AST to extract information
        visitor = CodeVisitor(file_path, module_name)
        visitor.visit(tree)

        return visitor
    except Exception as e:
        logger.error(f"Error analyzing file {file_path}: {e}")
        return None


def analyze_directory(
    directory: str,
    exclude_dirs: list[str] | None = None,
) -> list[CodeVisitor]:
    """
    Analyze all Python files in a directory and its subdirectories.

    Args:
        directory: Directory to analyze
        exclude_dirs: List of directory names to exclude

    Returns:
        List of CodeVisitor objects with the extracted information
    """
    if exclude_dirs is None:
        exclude_dirs = ["__pycache__", "venv", ".venv", ".git", "node_modules"]

    visitors = []

    logger.info(f"Analyzing directory: {directory}")

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                visitor = analyze_file(file_path)
                if visitor:
                    visitors.append(visitor)

    logger.info(f"Analyzed {len(visitors)} Python files")
    return visitors


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
    """
    logger.info("Generating class diagram")

    # Start the diagram
    diagram = [
        '@startuml "Code Analysis Class Diagram"',
        "",
        "' This diagram was automatically generated by the code analyzer",
        "",
    ]

    # Add all classes
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

    # Add standalone functions if requested
    if include_functions:
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
    method_calls_added = set()
    for visitor in visitors:
        for caller, called, rel_type in visitor.method_calls:
            # Only add each relationship once and only if both caller and called are known
            rel_key = f"{caller}_{called}"
            if rel_key not in method_calls_added:
                # Check if the called method is in our known classes/methods
                called_parts = called.split(".")
                if len(called_parts) >= 2:
                    obj_name, method_name = called_parts[0], called_parts[1]
                    if obj_name in visitor.imports:
                        # This is a call to an imported module
                        if include_functions:
                            diagram.append(
                                f"{caller.replace('.', '_')} ..> {called.replace('.', '_')} : calls",
                            )
                            method_calls_added.add(rel_key)

    # End the diagram
    diagram.append("")
    diagram.append("@enduml")

    return "\n".join(diagram)


def generate_module_diagram(visitors: list[CodeVisitor]) -> str:
    """
    Generate a PlantUML component diagram showing module dependencies.

    Args:
        visitors: List of CodeVisitor objects with the extracted information

    Returns:
        PlantUML diagram as a string
    """
    logger.info("Generating module diagram")

    # Start the diagram
    diagram = [
        '@startuml "Code Analysis Module Diagram"',
        "",
        "' This diagram was automatically generated by the code analyzer",
        "",
    ]

    # Track modules and their imports
    modules = {}

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
        for import_alias, import_name in visitor.imports.items():
            # Extract the top-level module
            top_module = import_name.split(".")[0]
            if top_module != module_name:  # Don't add self-imports
                modules[module_name]["imports"].add(top_module)

    # Add components for each module
    for module_name, module_info in modules.items():
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


def save_diagram(diagram: str, output_file: str) -> None:
    """
    Save a PlantUML diagram to a file.

    Args:
        diagram: PlantUML diagram as a string
        output_file: Path to save the diagram to
    """
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Save the diagram
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(diagram)

    logger.info(f"Saved diagram to {output_file}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze code and generate PlantUML diagrams",
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Path to the Python file or directory to analyze",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file for the PlantUML diagram",
    )
    parser.add_argument(
        "--include-modules",
        action="store_true",
        help="Generate a module diagram instead of a class diagram",
    )
    parser.add_argument(
        "--include-functions",
        action="store_true",
        help="Include standalone functions in the class diagram",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()


def main() -> int:
    """Main function."""
    # Parse command-line arguments
    args = parse_args()

    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Analyze the code
    if os.path.isdir(args.path):
        visitors = analyze_directory(args.path)
    elif os.path.isfile(args.path) and args.path.endswith(".py"):
        visitor = analyze_file(args.path)
        visitors = [visitor] if visitor else []
    else:
        logger.error(f"Invalid path: {args.path}")
        return 1

    if not visitors:
        logger.error("No Python files were successfully analyzed")
        return 1

    # Generate the diagram
    if args.include_modules:
        diagram = generate_module_diagram(visitors)
        diagram_type = "module"
    else:
        diagram = generate_class_diagram(visitors, args.include_functions)
        diagram_type = "class"

    # Determine the output file
    if args.output:
        output_file = args.output
    else:
        # Use a default output file based on the input path
        if os.path.isdir(args.path):
            base_name = os.path.basename(os.path.abspath(args.path))
        else:
            base_name = os.path.splitext(os.path.basename(args.path))[0]

        output_file = os.path.join(
            OUTPUT_DIR,
            "code_analysis",
            f"{base_name}_{diagram_type}_diagram.puml",
        )

    # Save the diagram
    save_diagram(diagram, output_file)

    print(f"\nGenerated {diagram_type} diagram: {output_file}")
    print(
        "You can render it using: python -m utils.puml.cli render --file=code_analysis/"
        + f"{os.path.basename(output_file)}",
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
