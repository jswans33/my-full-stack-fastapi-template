"""Type annotation parsing utilities."""

import ast
import logging

from ...exceptions import TypeAnnotationError


class TypeAnnotationParser:
    """Parser for Python type annotations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_annotation(self, node: ast.AST | None) -> str:
        """Extract type annotation from AST node.

        Args:
            node: AST node containing type annotation, or None

        Returns:
            String representation of the type annotation

        Raises:
            TypeAnnotationError: If the type annotation cannot be parsed
        """
        try:
            if node is None:
                return "Any"

            if isinstance(node, ast.Name):
                return node.id
            if isinstance(node, ast.Constant):
                return str(node.value)
            if isinstance(node, ast.Subscript):
                # Handle complex type annotations like List[str], Dict[str, int], etc.
                value = node.value
                if isinstance(value, ast.Name):
                    collection_type = value.id
                    if collection_type in ("List", "Set", "Sequence", "Collection"):
                        # Handle single type parameter
                        if isinstance(node.slice, ast.Name):
                            return f"{collection_type}[{node.slice.id}]"
                        if isinstance(node.slice, ast.Constant):
                            # Handle string literals in annotations
                            return f"{collection_type}[{node.slice.value}]"
                        return ast.unparse(node)
                    if collection_type == "Dict":
                        # Handle Dict with key,value types
                        return ast.unparse(node)
                    if collection_type == "Optional":
                        # Handle Optional[Type]
                        if isinstance(node.slice, ast.Name):
                            return f"Optional[{node.slice.id}]"
                        if isinstance(node.slice, ast.Constant):
                            return f"Optional[{node.slice.value}]"
                        return ast.unparse(node)
                    if collection_type == "Union":
                        # Handle Union[Type1, Type2]
                        return ast.unparse(node)
                return ast.unparse(node)
            if isinstance(node, ast.BinOp):
                # Handle string concatenation in annotations
                return ast.unparse(node)
            if isinstance(node, ast.Attribute):
                # Handle module.type annotations
                return ast.unparse(node)

            return ast.unparse(node)
        except Exception as e:
            raise TypeAnnotationError(
                f"Failed to parse type annotation: {e!s}",
                line_number=getattr(node, "lineno", None),
            )

    def extract_class_from_slice(
        self, node: ast.AST, known_classes: set[str]
    ) -> str | None:
        """Extract class name from AST node if it represents a known class."""
        if isinstance(node, ast.Name) and node.id in known_classes:
            return node.id
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            class_name = node.value.strip("'\"")
            if class_name in known_classes:
                return class_name
        return None
