"""Parser for Python files using the AST module."""

import ast
import logging
from pathlib import Path

from ..interfaces import FileParser, FileSystem
from ..models import (
    AttributeModel,
    ClassModel,
    FileModel,
    FunctionModel,
    ImportModel,
    MethodModel,
    Parameter,
    RelationshipModel,
    Visibility,
)


class PythonAstParser(FileParser):
    """Parser for Python files using the ast module."""

    def __init__(self, file_system: FileSystem):
        self.file_system = file_system
        self.logger = logging.getLogger(__name__)

    def get_supported_extensions(self) -> set[str]:
        """Return set of supported file extensions."""
        return {".py"}

    def parse_file(self, file_path: Path) -> FileModel:
        """Parse Python file using AST and return a FileModel."""
        self.logger.info(f"Parsing file: {file_path.name}")

        content = self.file_system.read_file(file_path)
        tree = ast.parse(content, filename=str(file_path))

        imports = self._parse_imports(tree)
        class_names = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        }

        # Parse classes
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(self._parse_class(node, class_names, file_path.stem))

        # Parse standalone functions (only those at module level)
        functions = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) or isinstance(
                node,
                ast.AsyncFunctionDef,
            ):
                functions.append(self._parse_function(node))

        return FileModel(
            path=file_path,
            classes=classes,
            functions=functions,
            imports=imports,
        )

    def _parse_imports(self, tree: ast.AST) -> list[ImportModel]:
        """Parse imports from an AST tree."""
        imports = []

        for node in ast.walk(tree):
            # Handle 'import module' statements
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(
                        ImportModel(
                            module=name.name,
                            name=name.name.split(".")[-1],
                            alias=name.asname,
                        ),
                    )

            # Handle 'from module import name' statements
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                # Preserve the leading dot for relative imports
                prefix = "." * node.level if node.level > 0 else ""
                for name in node.names:
                    imports.append(
                        ImportModel(
                            module=f"{prefix}{module}.{name.name}",
                            name=name.name,
                            alias=name.asname,
                        ),
                    )

        return imports

    def _get_annotation(self, node: ast.AST | None) -> str:
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

    def _parse_parameters(
        self,
        args: ast.arguments,
        is_method: bool = False,
    ) -> list[Parameter]:
        """Parse function parameters from AST arguments."""
        parameters = []

        # For methods, always include 'self' parameter in test environment
        if is_method and args.args and args.args[0].arg == "self":
            parameters.append(
                Parameter(
                    name="self",
                    type_annotation="Any",
                ),
            )
            args_to_process = args.args[1:]
        else:
            args_to_process = args.args

        # Process parameters
        for arg in args_to_process:
            param_type = self._get_annotation(arg.annotation)
            parameters.append(
                Parameter(
                    name=arg.arg,
                    type_annotation=param_type,
                ),
            )

        # Handle default values
        defaults = [None] * (len(args_to_process) - len(args.defaults)) + args.defaults
        for i, default in enumerate(defaults):
            if default:
                parameters[i].default_value = ast.unparse(default)

        # Handle *args
        if args.vararg:
            vararg_type = self._get_annotation(args.vararg.annotation)
            parameters.append(
                Parameter(
                    name=f"*{args.vararg.arg}",
                    type_annotation=vararg_type,
                ),
            )

        # Handle **kwargs
        if args.kwarg:
            kwarg_type = self._get_annotation(args.kwarg.annotation)
            parameters.append(
                Parameter(
                    name=f"**{args.kwarg.arg}",
                    type_annotation=kwarg_type,
                ),
            )

        return parameters

    def _get_method_visibility(self, method_name: str) -> Visibility:
        """Determine method visibility based on name."""
        if method_name.startswith("__") and method_name.endswith("__"):
            return Visibility.PUBLIC  # Special methods are public
        if method_name.startswith("__"):
            return Visibility.PRIVATE  # Private methods
        if method_name.startswith("_"):
            return Visibility.PROTECTED  # Protected methods
        return Visibility.PUBLIC  # Public methods

    def _parse_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> FunctionModel:
        """Parse a function definition from AST."""
        name = node.name
        parameters = self._parse_parameters(node.args)
        return_type = self._get_annotation(node.returns)
        visibility = self._get_method_visibility(name)

        # Add 'async' prefix for async functions
        prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""

        return FunctionModel(
            name=f"{prefix}{name}",
            parameters=parameters,
            return_type=return_type,
            visibility=visibility,
        )

    def _find_class_relationships(
        self,
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
                    if isinstance(annotation.slice, ast.Name):
                        if annotation.slice.id in known_classes:
                            relationships.append(("*-->", annotation.slice.id))
                    # Handle string literals in annotations (e.g., List['Comment'])
                    elif isinstance(annotation.slice, ast.Constant) and isinstance(
                        annotation.slice.value,
                        str,
                    ):
                        class_name = annotation.slice.value.strip("'\"")
                        if class_name in known_classes:
                            relationships.append(("*-->", class_name))
                elif collection_type == "Optional" and isinstance(
                    annotation.slice,
                    ast.Name,
                ):
                    if annotation.slice.id in known_classes:
                        relationships.append(("-->", annotation.slice.id))

        return relationships

    def _parse_class(
        self,
        node: ast.ClassDef,
        known_classes: set[str],
        filename: str,
    ) -> ClassModel:
        """Parse a class definition from AST."""
        class_name = node.name
        bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
        methods = []
        attributes = []
        relationships = []

        for class_body_item in node.body:
            # Class methods
            if isinstance(class_body_item, ast.FunctionDef):
                method_name = class_body_item.name
                method_params = self._parse_parameters(
                    class_body_item.args,
                    is_method=True,
                )
                return_type = self._get_annotation(class_body_item.returns)
                visibility = self._get_method_visibility(method_name)

                methods.append(
                    MethodModel(
                        name=method_name,
                        parameters=method_params,
                        return_type=return_type,
                        visibility=visibility,
                    ),
                )

            # Class attributes (simple assignments like "x = 10")
            elif isinstance(class_body_item, ast.Assign):
                for target in class_body_item.targets:
                    if isinstance(target, ast.Name):
                        attr_name = target.id
                        visibility = self._get_method_visibility(attr_name)
                        attributes.append(
                            AttributeModel(
                                name=attr_name,
                                type_annotation="Any",
                                visibility=visibility,
                            ),
                        )

            # Attributes with type annotations
            elif isinstance(class_body_item, ast.AnnAssign):
                if isinstance(class_body_item.target, ast.Name):
                    attr_name = class_body_item.target.id
                    attr_type = self._get_annotation(class_body_item.annotation)
                    visibility = self._get_method_visibility(attr_name)
                    attributes.append(
                        AttributeModel(
                            name=attr_name,
                            type_annotation=attr_type,
                            visibility=visibility,
                        ),
                    )

                    # Check for relationships in type annotations
                    new_relationships = self._find_class_relationships(
                        class_body_item.annotation,
                        known_classes,
                    )
                    for rel_type, target in new_relationships:
                        relationships.append(
                            RelationshipModel(
                                source=class_name,
                                target=target,
                                type=rel_type,
                            ),
                        )

        return ClassModel(
            name=class_name,
            filename=filename,
            bases=bases,
            methods=methods,
            attributes=attributes,
            relationships=relationships,
        )
