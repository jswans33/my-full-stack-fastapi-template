"""Class parsing utilities."""

import ast
import logging

from ...exceptions import ParserError
from ...models import (
    AttributeModel,
    ClassModel,
    RelationshipModel,
)
from .function_parser import FunctionParser
from .relationship_parser import RelationshipParser
from .type_parser import TypeAnnotationParser


class ClassParser:
    """Parser for Python classes."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.type_parser = TypeAnnotationParser()
        self.relationship_parser = RelationshipParser()
        self.function_parser = FunctionParser()

    def parse_class(
        self,
        node: ast.ClassDef,
        known_classes: set[str],
        filename: str,
    ) -> ClassModel:
        """Parse a class definition from AST.

        Args:
            node: AST node for class definition
            known_classes: Set of class names in the codebase
            filename: Name of the file containing this class

        Returns:
            ClassModel containing the parsed class information

        Raises:
            ParserError: If there's an error parsing the class structure
            TypeAnnotationError: If there's an error parsing type annotations
        """
        try:
            class_name = node.name

            # Parse base classes with error handling
            bases = []
            for base in node.bases:
                try:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        # Handle module.Class style inheritance
                        bases.append(ast.unparse(base))
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse base class in {class_name}: {e!s}",
                    )

            methods = []
            attributes = []
            relationships = []

            # Get class docstring
            docstring = ast.get_docstring(node)

            # Parse decorators
            decorators = []
            for decorator in node.decorator_list:
                try:
                    if isinstance(decorator, ast.Name):
                        decorators.append(decorator.id)
                    elif isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Name):
                            decorators.append(decorator.func.id)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse decorator in {class_name}: {e!s}",
                    )

            for class_body_item in node.body:
                try:
                    # Class methods (including async methods)
                    if isinstance(
                        class_body_item, (ast.FunctionDef, ast.AsyncFunctionDef)
                    ):
                        method = self.function_parser.parse_method(class_body_item)
                        methods.append(method)

                    # Class attributes (simple assignments)
                    elif isinstance(class_body_item, ast.Assign):
                        for target in class_body_item.targets:
                            if isinstance(target, ast.Name):
                                attr_name = target.id
                                visibility = self.function_parser.get_method_visibility(
                                    attr_name
                                )
                                # Try to infer type from assigned value
                                value_type = "Any"
                                default_value = None
                                if isinstance(class_body_item.value, ast.Constant):
                                    value_type = type(
                                        class_body_item.value.value
                                    ).__name__
                                    default_value = ast.unparse(class_body_item.value)
                                attributes.append(
                                    AttributeModel(
                                        name=attr_name,
                                        type_annotation=value_type,
                                        visibility=visibility,
                                        default_value=default_value,
                                    ),
                                )

                    # Attributes with type annotations
                    elif isinstance(class_body_item, ast.AnnAssign):
                        if isinstance(class_body_item.target, ast.Name):
                            attr_name = class_body_item.target.id
                            attr_type = self.type_parser.parse_annotation(
                                class_body_item.annotation
                            )
                            visibility = self.function_parser.get_method_visibility(
                                attr_name
                            )

                            # Get default value if present
                            default_value = None
                            if class_body_item.value:
                                default_value = ast.unparse(class_body_item.value)

                            attributes.append(
                                AttributeModel(
                                    name=attr_name,
                                    type_annotation=attr_type,
                                    visibility=visibility,
                                    default_value=default_value,
                                ),
                            )

                            # Check for relationships in type annotations
                            new_relationships = (
                                self.relationship_parser.find_relationships(
                                    class_body_item.annotation,
                                    known_classes,
                                )
                            )
                            for rel_type, target in new_relationships:
                                relationships.append(
                                    RelationshipModel(
                                        source=class_name,
                                        target=target,
                                        type=rel_type,
                                    ),
                                )
                except Exception as e:
                    self.logger.error(
                        f"Error parsing class member in {class_name}: {e!s}",
                    )
                    continue

            return ClassModel(
                name=class_name,
                filename=filename,
                bases=bases,
                methods=methods,
                attributes=attributes,
                relationships=relationships,
                docstring=docstring,
                decorators=decorators,
            )

        except Exception as e:
            raise ParserError(
                f"Failed to parse class {node.name}: {e!s}",
                filename=filename,
                line_number=node.lineno,
            )
