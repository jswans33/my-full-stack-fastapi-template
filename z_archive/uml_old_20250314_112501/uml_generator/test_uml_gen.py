import ast
import logging
from pathlib import Path
from typing import Dict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PlantUML settings
PLANTUML_START = "@startuml"
PLANTUML_END = "@enduml"
PLANTUML_SETTINGS = [
    "skinparam classAttributeIconSize 0",
]


def get_annotation(node: ast.AST | None) -> str:
    """Extract type annotation from AST node."""
    if node is None:
        return "Any"

    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.Subscript):
        return ast.unparse(node)
    if isinstance(node, ast.BinOp):
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
        value = annotation.value
        if isinstance(value, ast.Name):
            collection_type = value.id
            if collection_type in ("List", "Sequence", "Collection"):
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


def parse_imports(tree: ast.AST) -> list[tuple[str, str]]:
    """Parse imports from an AST tree."""
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append((name.name, name.asname or name.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for name in node.names:
                imports.append((f"{module}.{name.name}", name.asname or name.name))

    return imports


def parse_classes_from_file(
    filepath: str,
) -> tuple[dict[str, Dict], list[Dict]]:
    """Parse Python classes and functions from a file."""
    file_path = Path(filepath)
    filename = file_path.name
    logger.info(f"Parsing file: {filename}")

    with open(file_path, encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=str(file_path))

    imports = parse_imports(tree)
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
                if isinstance(class_body_item, ast.FunctionDef):
                    method_name = class_body_item.name
                    methods.append(
                        method_name_with_visibility(
                            method_name=method_signature(class_body_item),
                            node=class_body_item,
                        ),
                    )
                elif isinstance(class_body_item, ast.Assign):
                    for target in class_body_item.targets:
                        if isinstance(target, ast.Name):
                            attr_name = target.id
                            visibility = "-" if attr_name.startswith("_") else "+"
                            attributes.append((attr_name, "Any", visibility))
                elif isinstance(class_body_item, ast.AnnAssign):
                    if isinstance(class_body_item.target, ast.Name):
                        attr_name = class_body_item.target.id
                        attr_type = get_annotation(class_body_item.annotation)
                        visibility = "-" if attr_name.startswith("_") else "+"
                        attributes.append((attr_name, attr_type, visibility))

                        new_relationships = find_class_relationships(
                            class_body_item.annotation,
                            class_names,
                        )
                        if new_relationships:
                            relationships.extend(new_relationships)

            classes[class_name] = {
                "name": class_name,
                "filename": filename,
                "bases": bases,
                "methods": methods,
                "attributes": attributes,
                "relationships": relationships,
                "imports": imports,
            }

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
    classes_and_functions: tuple[dict[str, Dict], list[Dict]],
    filename: str,
    show_imports: bool = False,
) -> str:
    """Generate PlantUML code from class definitions and functions."""
    classes_dict, functions_list = classes_and_functions
    uml_lines = [PLANTUML_START, *PLANTUML_SETTINGS]

    uml_lines.append(f'\npackage "{filename}" {{')

    if functions_list:
        uml_lines.append("  class Functions <<(F,orange)>> {")
        for function in functions_list:
            visibility = function["visibility"]
            signature = function["signature"]
            uml_lines.append(f"    {visibility} {signature}")
        uml_lines.append("  }")

    for class_info in classes_dict.values():
        uml_lines.append(f"  class {class_info['name']} {{")

        for attr_name, attr_type, visibility in class_info["attributes"]:
            uml_lines.append(f"    {visibility} {attr_name}: {attr_type}")

        for method in class_info["methods"]:
            uml_lines.append(f"    {method}")

        uml_lines.append("  }")

    uml_lines.append("}")

    if show_imports:
        uml_lines.append("\n' Imports")
        for class_info in classes_dict.values():
            if "imports" in class_info:
                class_name = class_info["name"]
                qualified_name = f'"{filename}".{class_name}'

                for module, name in class_info["imports"]:
                    if not module.startswith(
                        ("typing", "collections", "datetime", "builtins"),
                    ):
                        if name[0].isupper():
                            uml_lines.append(
                                f"note right of {qualified_name}: imports class {name} from {module}",
                            )
                        elif not name.startswith("_"):
                            uml_lines.append(
                                f"note right of {qualified_name}: imports function/type {name} from {module}",
                            )

    uml_lines.append("\n' Relationships")
    for class_info in classes_dict.values():
        class_name = class_info["name"]
        qualified_name = f'"{filename}".{class_name}'

        for base in class_info["bases"]:
            uml_lines.append(f"{base} <|-- {qualified_name}")

        if "relationships" in class_info:
            for rel_type, target in class_info["relationships"]:
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
    filename = file_path_obj.stem

    logger.info(f"Generating UML for file: {file_path}")

    try:
        classes_and_functions = parse_classes_from_file(file_path)
        classes_dict, functions_list = classes_and_functions

        if not classes_dict and not functions_list:
            logger.warning(f"No classes or functions found in file: {file_path}")
            return

        plantuml_code = generate_plantuml(classes_and_functions, filename, show_imports)

        output_path = Path(output_dir) / f"{filename}.puml"
        output_path.parent.mkdir(parents=True, exist_ok=True)

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
    except Exception:
        logger.exception(f"Error generating UML for {file_path}")


def main():
    # Define paths
    current_dir = Path(__file__).resolve().parent
    target_file = current_dir / "generator" / "plantuml_generator.py"
    output_dir = current_dir.parent.parent / "docs" / "source" / "_generated_uml"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate UML diagram
    logger.info(f"Generating UML diagram for {target_file}")
    generate_uml_for_file(
        file_path=str(target_file), output_dir=str(output_dir), show_imports=True
    )
    logger.info("UML generation completed")


if __name__ == "__main__":
    main()
