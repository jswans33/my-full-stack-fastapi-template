import ast
import logging
import os
from pathlib import Path

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# File extensions
PYTHON_FILE_EXTENSION = ".py"
PLANTUML_FILE_EXTENSION = ".puml"

# PlantUML settings
PLANTUML_START = "@startuml"
PLANTUML_END = "@enduml"
PLANTUML_SETTINGS = [
    "skinparam classAttributeIconSize 0",
]

# Default directories to process
DEFAULT_SUBDIRS = ["models", "services"]

# Project paths - make them relative to the script location
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
APP_DIR = PROJECT_ROOT / "app"
DEFAULT_PROJECT_DIR = str(APP_DIR)
DEFAULT_OUTPUT_DIR = str(Path("docs") / "source" / "_generated_uml")

# Ensure output directory exists
Path(DEFAULT_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
logger.info(f"Output directory: {DEFAULT_OUTPUT_DIR}")


def get_annotation(node: ast.AST | None) -> str:
    """Extract type annotation from AST node."""
    if node is None:
        return "Any"

    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.Subscript):
        # Handle List[str], Optional[int], etc.
        return ast.unparse(node)
    if isinstance(node, ast.BinOp):
        # Handle Union types (X | Y)
        return ast.unparse(node)
    return ast.unparse(node)


def method_signature(node: ast.FunctionDef) -> str:
    """Extract method signature including parameters and return type."""
    params = []

    # Skip 'self' parameter for instance methods
    args_to_process = (
        node.args.args[1:]
        if node.args.args and node.args.args[0].arg == "self"
        else node.args.args
    )

    # Process parameters
    for arg in args_to_process:
        param_type = get_annotation(arg.annotation)
        params.append(f"{arg.arg}: {param_type}")

    # Handle default values
    defaults = [None] * (
        len(args_to_process) - len(node.args.defaults)
    ) + node.args.defaults
    for i, default in enumerate(defaults):
        if default:
            params[i] = f"{params[i]} = {ast.unparse(default)}"

    # Handle *args
    if node.args.vararg:
        vararg_type = get_annotation(node.args.vararg.annotation)
        params.append(f"*{node.args.vararg.arg}: {vararg_type}")

    # Handle **kwargs
    if node.args.kwarg:
        kwarg_type = get_annotation(node.args.kwarg.annotation)
        params.append(f"**{node.args.kwarg.arg}: {kwarg_type}")

    # Get return type
    returns = get_annotation(node.returns)

    return f"{node.name}({', '.join(params)}) -> {returns}"


def method_name_with_visibility(method_name: str, node: ast.FunctionDef) -> str:
    """Determine method visibility based on name."""
    if method_name.startswith("__") and method_name.endswith("__"):
        return method_name  # Special methods remain as is
    if method_name.startswith("__"):
        return f"-{method_name[2:]}"  # Private methods
    if method_name.startswith("_"):
        return f"#{method_name[1:]}"  # Protected methods
    return f"+{method_name}"  # Public methods


def find_class_relationships(
    annotation: ast.AST,
    known_classes: set[str],
) -> list[tuple[str, str]]:
    """Find relationships to other classes in type annotations."""
    relationships = []

    if isinstance(annotation, ast.Name) and annotation.id in known_classes:
        relationships.append(("-->", annotation.id))  # Basic association
    elif isinstance(annotation, ast.Subscript):
        # Handle List[Class], Optional[Class], etc.
        value = annotation.value
        if isinstance(value, ast.Name):
            collection_type = value.id
            if collection_type in ("List", "Sequence", "Collection"):
                # For collections, use composition with multiplicity
                if (
                    isinstance(annotation.slice, ast.Name)
                    and annotation.slice.id in known_classes
                ):
                    relationships.append(("*-->", annotation.slice.id))
            elif collection_type == "Optional" and isinstance(
                annotation.slice,
                ast.Name,
            ):
                if annotation.slice.id in known_classes:
                    relationships.append(("-->", annotation.slice.id))

    return relationships


# Type aliases for clarity
ClassAttributes = tuple[str, str, str]  # (name, type, visibility)
ClassRelationship = tuple[str, str]  # (relationship_type, target_class)
ImportInfo = tuple[str, str]  # (module, name)
FunctionInfo = dict[str, str | list[str]]  # Function information
ClassInfo = dict[
    str,
    str
    | list[str]
    | list[ClassAttributes]
    | list[ClassRelationship]
    | list[ImportInfo],
]


def parse_imports(tree: ast.AST) -> list[tuple[str, str]]:
    """Parse imports from an AST tree.

    Returns a list of tuples (module, name) for each imported name.
    """
    imports = []

    for node in ast.walk(tree):
        # Handle 'import module' statements
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append((name.name, name.asname or name.name))

        # Handle 'from module import name' statements
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for name in node.names:
                imports.append((f"{module}.{name.name}", name.asname or name.name))

    return imports


def parse_classes_from_file(
    filepath: str,
) -> tuple[dict[str, ClassInfo], list[FunctionInfo]]:
    """Parse Python classes, their inheritance, methods, attributes, relationships, and standalone functions."""
    file_path = Path(filepath)
    filename = file_path.name
    logger.info(f"Parsing file: {filename}")

    with open(file_path, encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=str(file_path))

    # Parse imports
    imports = parse_imports(tree)
    logger.debug(f"Imports in {filename}: {imports}")

    # First pass: collect all class names
    class_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    }

    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
            methods = []
            attributes = []
            relationships = []

            for class_body_item in node.body:
                # Class methods
                if isinstance(class_body_item, ast.FunctionDef):
                    method_name = class_body_item.name
                    methods.append(
                        method_name_with_visibility(
                            method_name=method_signature(class_body_item),
                            node=class_body_item,
                        ),
                    )

                # Class attributes (simple assignments like "x = 10")
                elif isinstance(class_body_item, ast.Assign):
                    for target in class_body_item.targets:
                        if isinstance(target, ast.Name):
                            attr_name = target.id
                            visibility = "-" if attr_name.startswith("_") else "+"
                            attributes.append((attr_name, "Any", visibility))

                # Attributes with type annotations
                elif isinstance(class_body_item, ast.AnnAssign):
                    if isinstance(class_body_item.target, ast.Name):
                        attr_name = class_body_item.target.id
                        attr_type = get_annotation(class_body_item.annotation)
                        visibility = "-" if attr_name.startswith("_") else "+"
                        attributes.append((attr_name, attr_type, visibility))

                        # Check for relationships in type annotations
                        new_relationships = find_class_relationships(
                            class_body_item.annotation,
                            class_names,
                        )
                        if new_relationships:
                            relationships.extend(
                                (rel_type, target)
                                for rel_type, target in new_relationships
                            )

            classes[class_name] = {
                "name": class_name,
                "filename": filename,
                "bases": bases,
                "methods": methods,
                "attributes": attributes,
                "relationships": relationships,
                "imports": imports,  # Add imports to class info
            }

    # Extract standalone functions
    functions = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.FunctionDef)
            and not hasattr(node, "parent")
            and not any(
                isinstance(parent, ast.ClassDef)
                for parent in ast.iter_child_nodes(node)
            )
        ):
            function_name = node.name
            function_signature = method_signature(node)
            visibility = "+" if not function_name.startswith("_") else "-"
            functions.append(
                {
                    "name": function_name,
                    "signature": function_signature,
                    "visibility": visibility,
                    "imports": imports,
                },
            )

    return classes, functions


def generate_plantuml(
    classes_and_functions: tuple[dict[str, ClassInfo], list[FunctionInfo]],
    filename: str,
    show_imports: bool = False,
) -> str:
    """Generate PlantUML code from class definitions and functions for a specific file."""
    classes_dict, functions_list = classes_and_functions
    uml_lines = [PLANTUML_START, *PLANTUML_SETTINGS]

    # Create a package for the file
    uml_lines.append(f'\npackage "{filename}" {{')

    # Add functions to the package if any
    if functions_list:
        uml_lines.append("  class Functions <<(F,orange)>> {")
        for function in functions_list:
            visibility = function["visibility"]
            signature = function["signature"]
            uml_lines.append(f"    {visibility} {signature}")
        uml_lines.append("  }")

    # Add classes to the package
    for class_info in classes_dict.values():
        uml_lines.append(f"  class {class_info['name']} {{")

        # Handle attributes
        attributes: list[ClassAttributes] = class_info["attributes"]  # type: ignore
        for attr in attributes:
            attr_name, attr_type, visibility = attr
            uml_lines.append(f"    {visibility} {attr_name}: {attr_type}")

        # Handle methods
        for method in class_info["methods"]:
            uml_lines.append(f"    {method}")  # Visibility is already included

        uml_lines.append("  }")

    # Close the package
    uml_lines.append("}")

    # Add imports section if show_imports is True
    if show_imports and any(
        "imports" in class_info for class_info in classes_dict.values()
    ):
        uml_lines.append("\n' Imports")
        for class_info in classes_dict.values():
            if "imports" in class_info:
                class_name = class_info["name"]
                qualified_name = f'"{filename}".{class_name}'

                # Add import relationships
                imports: list[ImportInfo] = class_info.get("imports", [])  # type: ignore
                for module, name in imports:
                    # Show imports for classes, functions, and types
                    # Skip built-ins and standard library modules
                    if not module.startswith(
                        ("typing", "collections", "datetime", "builtins"),
                    ):
                        # Classes (start with uppercase)
                        if name[0].isupper():
                            uml_lines.append(
                                f"note right of {qualified_name}: imports class {name} from {module}",
                            )
                        # Functions and types (don't start with underscore)
                        elif not name.startswith("_"):
                            uml_lines.append(
                                f"note right of {qualified_name}: imports function/type {name} from {module}",
                            )

    # Add relationships
    uml_lines.append("\n' Relationships")
    for class_info in classes_dict.values():
        class_name = class_info["name"]
        qualified_name = f'"{filename}".{class_name}'

        # Add inheritance lines
        for base in class_info["bases"]:
            # For now, we assume base classes might be in other files
            uml_lines.append(f"{base} <|-- {qualified_name}")

        # Add other relationships
        if "relationships" in class_info:
            relationships: list[ClassRelationship] = class_info["relationships"]  # type: ignore
            for rel_type, target in relationships:
                # For now, we assume target classes might be in other files
                uml_lines.append(f"{qualified_name} {rel_type} {target}")

    uml_lines.append(PLANTUML_END)
    return "\n".join(uml_lines)


def generate_uml_for_file(
    file_path: str,
    output_dir: str,
    show_imports: bool = False,
) -> None:
    """Generate UML diagram for a single Python file."""
    file_path_obj = Path(file_path)
    filename = file_path_obj.stem  # Get filename without extension

    logger.info(f"Generating UML for file: {file_path}")

    try:
        # Parse classes and functions from the file
        classes_and_functions = parse_classes_from_file(file_path)
        classes_dict, functions_list = classes_and_functions

        if not classes_dict and not functions_list:
            logger.warning(f"No classes or functions found in file: {file_path}")
            return

        # Generate PlantUML code - pass the filename explicitly and show_imports flag
        plantuml_code = generate_plantuml(classes_and_functions, filename, show_imports)

        # Create output path
        output_path = Path(output_dir) / f"{filename}{PLANTUML_FILE_EXTENSION}"

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write PlantUML code to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(plantuml_code)

        logger.info(
            f"Generated UML diagram for {filename}",
            extra={
                "output_path": str(output_path),
                "class_count": len(classes_dict),
                "function_count": len(functions_list),
            },
        )
    except Exception as e:
        logger.exception(
            f"Error generating UML for {file_path}",
            exc_info=e,
        )


def generate_uml_for_folder(
    src_dir: str,
    output_dir: str,
    list_only: bool = False,
    show_imports: bool = False,
) -> None:
    """Generate UML diagrams for all Python files in a directory."""
    src_path = Path(src_dir)

    logger.info(
        "Starting UML generation",
        extra={"source_dir": str(src_path), "output_dir": output_dir},
    )

    if not src_path.exists():
        logger.warning(f"Source directory does not exist: {src_path}")
        return

    # List all Python files in the directory for troubleshooting
    python_files = []
    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file.endswith(PYTHON_FILE_EXTENSION):
                file_path = os.path.join(root, file)
                python_files.append(file_path)

    # Log the files found
    if python_files:
        logger.info(f"Found {len(python_files)} Python files in {src_path}")
        for file_path in python_files:
            logger.info(f"  - {file_path}")
    else:
        logger.warning(f"No Python files found in directory: {src_path}")
        return

    # Process each file
    file_count = 0
    for file_path in python_files:
        try:
            generate_uml_for_file(file_path, output_dir)
            file_count += 1
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")

    logger.info(
        f"Successfully processed {file_count} out of {len(python_files)} files in {src_path}",
    )


def generate_all(
    directory: str,
    output_dir: str,
    subdirs: list[str] | None = None,
    list_only: bool = False,
    show_imports: bool = False,
) -> None:
    """Generate UML diagrams for specified subdirectories."""
    if subdirs is None:
        subdirs = DEFAULT_SUBDIRS

    logger.info(
        "Starting UML generation for all directories",
        extra={
            "base_directory": directory,
            "output_directory": output_dir,
            "subdirectories": subdirs,
        },
    )

    # Process the base directory itself first
    generate_uml_for_folder(directory, output_dir, list_only, show_imports)

    # Then process each subdirectory
    for subdir in subdirs:
        dir_path = os.path.join(directory, subdir)
        if os.path.exists(dir_path):
            generate_uml_for_folder(dir_path, output_dir, list_only, show_imports)
        else:
            logger.warning(
                "Directory not found",
                extra={"directory_path": dir_path},
            )

    logger.info("UML generation completed")


def parse_args():
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate PlantUML class diagrams from Python source code.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # Show defaults in help
        epilog="""
Examples:
  # Process a single file
  python generate_uml.py -f backend/app/models.py
  
  # Process a directory
  python generate_uml.py -d backend/app
  
  # Process the app directory
  python generate_uml.py --app-dir
  
  # Process a directory recursively
  python generate_uml.py -d backend/app --recursive
  
  # Specify a custom output directory
  python generate_uml.py -d backend/app -o custom/output/path
  
  # Enable verbose logging
  python generate_uml.py -d backend/app -v
  
For more information, see the README.md file in this directory.
        """,
    )

    # Create a mutually exclusive group for input sources
    input_group = parser.add_mutually_exclusive_group(required=True)

    input_group.add_argument(
        "-f",
        "--file",
        help="Process a single Python file",
    )

    input_group.add_argument(
        "-d",
        "--directory",
        help="Process a directory containing Python files",
    )

    input_group.add_argument(
        "--app-dir",
        action="store_true",
        help=f"Process the app directory ({DEFAULT_PROJECT_DIR})",
    )

    # Output directory
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for PlantUML files",
    )

    # Optional arguments
    parser.add_argument(
        "--subdirs",
        nargs="+",  # One or more arguments
        default=DEFAULT_SUBDIRS,
        help="List of subdirectories to process (only with --directory or --app-dir)",
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively process directories",
    )

    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only list Python files without generating UML diagrams (for troubleshooting)",
    )

    parser.add_argument(
        "--show-imports",
        action="store_true",
        help="Show imports (classes, functions, and types) in the UML diagrams",
    )

    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Generate a report of files processed and the number of classes and functions found",
    )

    # Verbosity options
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    verbosity_group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress all output except errors",
    )

    verbosity_group.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Configure logging based on verbosity options
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    elif args.verbose:
        logger.setLevel(logging.INFO)
    elif args.quiet:
        logger.setLevel(logging.ERROR)

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # Process based on input type
    if args.file:
        # Process a single file
        if not os.path.exists(args.file):
            logger.error(f"File not found: {args.file}")
            exit(1)

        if not args.file.endswith(PYTHON_FILE_EXTENSION):
            logger.error(f"Not a Python file: {args.file}")
            exit(1)

        logger.info(f"Processing single file: {args.file}")
        generate_uml_for_file(args.file, args.output)

    elif args.directory:
        # Process a specific directory
        if not os.path.exists(args.directory):
            logger.error(f"Directory not found: {args.directory}")
            exit(1)

        if not os.path.isdir(args.directory):
            logger.error(f"Not a directory: {args.directory}")
            exit(1)

        logger.info(f"Processing directory: {args.directory}")
        generate_uml_for_folder(
            args.directory,
            args.output,
            args.list_only,
            args.show_imports,
        )

        # Process subdirectories if recursive flag is set
        if args.recursive:
            for subdir in args.subdirs:
                dir_path = os.path.join(args.directory, subdir)
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    logger.info(f"Processing subdirectory: {dir_path}")
                    generate_uml_for_folder(
                        dir_path,
                        args.output,
                        args.list_only,
                        args.show_imports,
                    )
                else:
                    logger.warning(f"Subdirectory not found: {dir_path}")

    elif args.app_dir:
        # Process the app directory
        logger.info(f"Processing app directory: {DEFAULT_PROJECT_DIR}")
        generate_all(DEFAULT_PROJECT_DIR, args.output, args.subdirs)

    logger.info("UML generation completed")
    logger.info(f"Output directory: {args.output}")
