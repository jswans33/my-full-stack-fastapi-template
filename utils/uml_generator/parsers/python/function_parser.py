"""Function and method parsing utilities.

This module provides parsers for Python functions and methods, handling:
- Function and method signatures
- Parameters and return types
- Decorators and visibility
- Static and class methods
- Async functions and methods
"""

import ast
import logging

from ...exceptions import ParserError
from ...models import (
    FunctionModel,
    MethodModel,
    ParameterModel,
    Visibility,
)
from .type_parser import TypeAnnotationParser


def parse_decorator(decorator: ast.AST) -> str | None:
    """Parse a decorator node to get its name.

    Args:
        decorator: AST node representing a decorator

    Returns:
        Decorator name if it can be parsed, None otherwise
    """
    try:
        if isinstance(decorator, ast.Name):
            return decorator.id
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
        return None
    except Exception:
        return None


class FunctionParser:
    """Parser for Python functions and methods."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.type_parser = TypeAnnotationParser()

    def parse_parameters(
        self,
        args: ast.arguments,
        is_method: bool = False,
    ) -> list[ParameterModel]:
        """Parse function parameters from AST arguments.

        Args:
            args: AST arguments node containing parameter information
            is_method: Whether these parameters are for a method (adds self)

        Returns:
            List of ParameterModel objects representing the parameters

        Raises:
            ParserError: If there's an error parsing parameters
        """
        try:
            parameters: list[ParameterModel] = []

            # For methods, always include 'self' parameter in test environment
            if is_method and args.args and args.args[0].arg == "self":
                parameters.append(
                    ParameterModel(
                        name="self",
                        type_annotation="Any",
                    ),
                )
                args_to_process = args.args[1:]
            else:
                args_to_process = args.args

            # Process parameters
            for arg in args_to_process:
                try:
                    param_type = self.type_parser.parse_annotation(arg.annotation)
                    parameters.append(
                        ParameterModel(
                            name=arg.arg,
                            type_annotation=param_type,
                        ),
                    )
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse parameter {arg.arg}: {e!s}. Using 'Any' type.",
                    )
                    parameters.append(
                        ParameterModel(
                            name=arg.arg,
                            type_annotation="Any",
                        ),
                    )

            # Handle default values
            defaults = [None] * (
                len(args_to_process) - len(args.defaults)
            ) + args.defaults
            for i, default in enumerate(defaults):
                if default:
                    try:
                        parameters[i].default_value = ast.unparse(default)
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to parse default value for parameter {parameters[i].name}: {e!s}",
                        )

            # Handle *args
            if args.vararg:
                try:
                    vararg_type = self.type_parser.parse_annotation(
                        args.vararg.annotation
                    )
                    parameters.append(
                        ParameterModel(
                            name=f"*{args.vararg.arg}",
                            type_annotation=vararg_type,
                        ),
                    )
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse *args parameter: {e!s}. Using 'Any' type.",
                    )
                    parameters.append(
                        ParameterModel(
                            name=f"*{args.vararg.arg}",
                            type_annotation="Any",
                        ),
                    )

            # Handle **kwargs
            if args.kwarg:
                try:
                    kwarg_type = self.type_parser.parse_annotation(
                        args.kwarg.annotation
                    )
                    parameters.append(
                        ParameterModel(
                            name=f"**{args.kwarg.arg}",
                            type_annotation=kwarg_type,
                        ),
                    )
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse **kwargs parameter: {e!s}. Using 'Any' type.",
                    )
                    parameters.append(
                        ParameterModel(
                            name=f"**{args.kwarg.arg}",
                            type_annotation="Any",
                        ),
                    )

            return parameters

        except Exception as e:
            raise ParserError(f"Failed to parse parameters: {e!s}")

    def get_method_visibility(self, method_name: str) -> Visibility:
        """Determine method visibility based on name."""
        if method_name.startswith("__") and method_name.endswith("__"):
            return Visibility.PUBLIC  # Special methods are public
        if method_name.startswith("__"):
            return Visibility.PRIVATE  # Private methods
        if method_name.startswith("_"):
            return Visibility.PROTECTED  # Protected methods
        return Visibility.PUBLIC  # Public methods

    def parse_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> FunctionModel:
        """Parse a standalone function definition from AST."""
        try:
            name = node.name
            parameters = self.parse_parameters(node.args)
            return_type = self.type_parser.parse_annotation(node.returns)
            visibility = self.get_method_visibility(name)

            # Add 'async' prefix for async functions
            prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""

            return FunctionModel(
                name=f"{prefix}{name}",
                parameters=parameters,
                return_type=return_type,
                visibility=visibility,
            )
        except Exception as e:
            raise ParserError(
                f"Failed to parse function {node.name}: {e!s}",
                line_number=node.lineno,
            )

    def parse_method(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> MethodModel:
        """Parse a class method definition from AST.

        Args:
            node: AST node representing a method definition

        Returns:
            MethodModel containing the parsed method information

        Raises:
            ParserError: If there's an error parsing the method
        """
        try:
            method_name = node.name

            # Parse decorators and check for staticmethod/classmethod
            method_decorators: list[str] = []
            is_static = False
            is_classmethod = False

            for decorator in node.decorator_list:
                if decorator_name := parse_decorator(decorator):
                    method_decorators.append(decorator_name)
                    if decorator_name == "staticmethod":
                        is_static = True
                    elif decorator_name == "classmethod":
                        is_classmethod = True

            # Parse parameters (don't add self for static methods)
            method_params = self.parse_parameters(
                node.args,
                is_method=not is_static,
            )

            # Parse return type and visibility
            return_type = self.type_parser.parse_annotation(node.returns)
            visibility = self.get_method_visibility(method_name)

            # Get docstring
            method_docstring = ast.get_docstring(node)

            # Add async prefix for async methods
            prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""

            return MethodModel(
                name=f"{prefix}{method_name}",
                parameters=method_params,
                return_type=return_type,
                visibility=visibility,
                is_static=is_static,
                is_classmethod=is_classmethod,
                docstring=method_docstring,
                decorators=method_decorators,
            )
        except Exception as e:
            raise ParserError(
                f"Failed to parse method {node.name}: {e!s}",
                line_number=node.lineno,
            )
