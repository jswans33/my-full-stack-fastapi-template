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
ClassInfo = dict[str, str | list[str] | list[ClassAttributes] | list[ClassRelationship]]


def parse_classes_from_file(
    filepath: str,
) -> dict[str, ClassInfo]:
    """Parse Python classes, their inheritance, methods, attributes, and relationships."""
    file_path = Path(filepath)
    filename = file_path.name
    logger.info(f"Parsing file: {filename}")

    with open(file_path, encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=str(file_path))

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
            }

    return classes


def generate_plantuml(classes: dict[str, ClassInfo]) -> str:
    """Generate PlantUML code from class definitions."""
    uml_lines = [PLANTUML_START, *PLANTUML_SETTINGS]

    # Group classes by filename
    classes_by_file: dict[str, list[dict]] = {}
    for class_info in classes.values():
        # Cast filename to str since we know it's a string in the dictionary
        filename = str(class_info.get("filename", "unknown"))
        if filename not in classes_by_file:
            classes_by_file[filename] = []
        classes_by_file[filename].append(class_info)

    # First pass: output all classes grouped by file as packages
    for filename, file_classes in classes_by_file.items():
        # Create a package for each file
        uml_lines.append(f'\npackage "{filename}" {{')

        # Add classes to the package
        for class_info in file_classes:
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

    # Second pass: output all relationships
    uml_lines.append("\n' Relationships")
    for class_info in classes.values():
        class_name = class_info["name"]
        filename = class_info.get("filename", "unknown")
        qualified_name = f'"{filename}".{class_name}'

        # Add inheritance lines
        for base in class_info["bases"]:
            # Check if base is in our classes to qualify it
            base_qualified = base
            for other_class in classes.values():
                if other_class["name"] == base:
                    base_qualified = (
                        f'"{other_class.get("filename", "unknown")}".{base}'
                    )
                    break

            uml_lines.append(f"{base_qualified} <|-- {qualified_name}")

        # Add other relationships
        if "relationships" in class_info:
            relationships: list[ClassRelationship] = class_info["relationships"]  # type: ignore
            for rel_type, target in relationships:
                # Check if target is in our classes to qualify it
                target_qualified = target
                for other_class in classes.values():
                    if other_class["name"] == target:
                        target_qualified = (
                            f'"{other_class.get("filename", "unknown")}".{target}'
                        )
                        break

                uml_lines.append(f"{qualified_name} {rel_type} {target_qualified}")

    uml_lines.append(PLANTUML_END)
    return "\n".join(uml_lines)


def generate_uml_for_file(file_path: str, output_dir: str) -> None:
    """Generate UML diagram for a single Python file."""
    file_path_obj = Path(file_path)
    filename = file_path_obj.stem  # Get filename without extension

    logger.info(f"Generating UML for file: {file_path}")

    try:
        # Parse classes from the file
        classes = parse_classes_from_file(file_path)

        if not classes:
            logger.warning(f"No classes found in file: {file_path}")
            return

        # Generate PlantUML code
        plantuml_code = generate_plantuml(classes)

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
                "class_count": len(classes),
            },
        )
    except Exception as e:
        logger.exception(
            f"Error generating UML for {file_path}",
            exc_info=e,
        )


def generate_uml_for_folder(src_dir: str, output_dir: str) -> None:
    """Generate UML diagrams for all Python files in a directory."""
    src_path = Path(src_dir)

    logger.info(
        "Starting UML generation",
        extra={"source_dir": str(src_path), "output_dir": output_dir},
    )

    if not src_path.exists():
        logger.warning(f"Source directory does not exist: {src_path}")
        return

    file_count = 0
    for root, _, files in os.walk(src_path):
        for file in files:
            if file.endswith(PYTHON_FILE_EXTENSION):
                file_path = os.path.join(root, file)
                generate_uml_for_file(file_path, output_dir)
                file_count += 1

    if file_count == 0:
        logger.warning(f"No Python files found in directory: {src_path}")


def generate_all(
    directory: str,
    output_dir: str,
    subdirs: list[str] | None = None,
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
    generate_uml_for_folder(directory, output_dir)

    # Then process each subdirectory
    for subdir in subdirs:
        dir_path = os.path.join(directory, subdir)
        if os.path.exists(dir_path):
            generate_uml_for_folder(dir_path, output_dir)
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
        generate_uml_for_folder(args.directory, args.output)

        # Process subdirectories if recursive flag is set
        if args.recursive:
            for subdir in args.subdirs:
                dir_path = os.path.join(args.directory, subdir)
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    logger.info(f"Processing subdirectory: {dir_path}")
                    generate_uml_for_folder(dir_path, args.output)
                else:
                    logger.warning(f"Subdirectory not found: {dir_path}")

    elif args.app_dir:
        # Process the app directory
        logger.info(f"Processing app directory: {DEFAULT_PROJECT_DIR}")
        generate_all(DEFAULT_PROJECT_DIR, args.output, args.subdirs)

    logger.info("UML generation completed")
    logger.info(f"Output directory: {args.output}")
