"""Relationship detection between Python classes."""

import ast
import logging

from ...exceptions import TypeAnnotationError
from .type_parser import TypeAnnotationParser


class RelationshipParser:
    """Parser for detecting relationships between Python classes."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.type_parser = TypeAnnotationParser()

    def find_relationships(
        self,
        annotation: ast.AST,
        known_classes: set[str],
    ) -> list[tuple[str, str]]:
        """Find relationships to other classes in type annotations.

        This method analyzes type annotations to detect various kinds of relationships:
        - Basic association (-->): Simple reference to another class
        - Composition (*-->): Collection types (List, Set, etc.) containing other classes
        - Aggregation (o-->): Dict with class as value type
        - Optional association (..>): Optional[Class] references

        Args:
            annotation: AST node containing type annotation
            known_classes: Set of class names that exist in the codebase

        Returns:
            List of tuples (relationship_type, target_class)
            where relationship_type is one of: '-->', '*-->', 'o-->', '..>'

        Raises:
            TypeAnnotationError: If the type annotation cannot be parsed
        """
        try:
            relationships = []

            # Handle direct class reference
            if isinstance(annotation, ast.Name):
                if annotation.id in known_classes:
                    relationships.append(("-->", annotation.id))  # Basic association
                return relationships

            # Handle subscript types (generics)
            if isinstance(annotation, ast.Subscript):
                value = annotation.value
                if not isinstance(value, ast.Name):
                    return relationships

                collection_type = value.id

                # Handle collection types (List, Set, etc.)
                if collection_type in (
                    "List",
                    "Set",
                    "Sequence",
                    "Collection",
                    "Iterable",
                ):
                    target_class = self.type_parser.extract_class_from_slice(
                        annotation.slice,
                        known_classes,
                    )
                    if target_class:
                        relationships.append(("*-->", target_class))  # Composition

                # Handle dictionary types
                elif collection_type == "Dict":
                    if isinstance(annotation.slice, ast.Tuple):
                        # Check if value type is a known class
                        if (
                            len(annotation.slice.elts) == 2
                        ):  # Dict[key_type, value_type]
                            value_type = annotation.slice.elts[1]
                            if (
                                isinstance(value_type, ast.Name)
                                and value_type.id in known_classes
                            ):
                                relationships.append(
                                    ("o-->", value_type.id)
                                )  # Aggregation
                            elif isinstance(value_type, ast.Constant) and isinstance(
                                value_type.value,
                                str,
                            ):
                                class_name = value_type.value.strip("'\"")
                                if class_name in known_classes:
                                    relationships.append(("o-->", class_name))

                # Handle Optional types
                elif collection_type == "Optional":
                    target_class = self.type_parser.extract_class_from_slice(
                        annotation.slice,
                        known_classes,
                    )
                    if target_class:
                        relationships.append(
                            ("..>", target_class)
                        )  # Optional association

                # Handle Union types
                elif collection_type == "Union":
                    if isinstance(annotation.slice, ast.Tuple):
                        for type_arg in annotation.slice.elts:
                            target_class = self.type_parser.extract_class_from_slice(
                                type_arg,
                                known_classes,
                            )
                            if target_class:
                                relationships.append(("-->", target_class))

            return relationships

        except Exception as e:
            raise TypeAnnotationError(
                f"Failed to analyze relationships in type annotation: {e!s}",
                line_number=getattr(annotation, "lineno", None),
            )
