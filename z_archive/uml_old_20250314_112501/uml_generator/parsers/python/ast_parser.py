"""Main Python AST parser implementation."""

import ast
import logging
from pathlib import Path

from ...exceptions import FileSystemError, ParserError, SyntaxParsingError
from ...interfaces import FileSystem
from ...models import FileModel
from ..base_parser import BaseParser
from .class_parser import ClassParser
from .function_parser import FunctionParser
from .import_parser import ImportParser


class PythonAstParser(BaseParser):
    """Parser for Python files using the AST module."""

    def __init__(self, file_system: FileSystem):
        super().__init__(file_system)
        self.logger = logging.getLogger(__name__)
        self.class_parser = ClassParser()
        self.function_parser = FunctionParser()
        self.import_parser = ImportParser()

    def get_supported_extensions(self) -> set[str]:
        """Return set of supported file extensions."""
        return {".py"}

    def parse_file(self, file_path: Path) -> FileModel:
        """Parse Python file using AST and return a FileModel.

        Args:
            file_path: Path to the Python file to parse

        Returns:
            FileModel containing the parsed file information

        Raises:
            ParserError: Base class for all parsing errors
            SyntaxParsingError: When the file contains invalid Python syntax
            ImportError: When there's an error parsing imports
            TypeAnnotationError: When there's an error parsing type annotations
            FileSystemError: When the file cannot be read
        """
        self.logger.info(f"Parsing file: {file_path.name}")

        try:
            content = self.file_system.read_file(file_path)
        except Exception as e:
            raise FileSystemError(f"Failed to read file {file_path}: {e!s}")

        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            raise SyntaxParsingError(
                message=str(e),
                filename=str(file_path),
                line_number=e.lineno,
            )
        except Exception as e:
            raise ParserError(f"Failed to parse {file_path}: {e!s}", str(file_path))

        # Parse imports
        imports = self.import_parser.parse_imports(tree)

        # Get all class names for relationship detection
        class_names = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        }

        # Parse classes with error handling
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                try:
                    class_model = self.class_parser.parse_class(
                        node,
                        class_names,
                        file_path.stem,
                    )
                    classes.append(class_model)
                except Exception as e:
                    self.logger.error(
                        f"Error parsing class {node.name} in {file_path}: {e!s}",
                    )
                    # Continue parsing other classes instead of failing completely
                    continue

        # Parse standalone functions (only those at module level)
        functions = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                try:
                    function_model = self.function_parser.parse_function(node)
                    functions.append(function_model)
                except Exception as e:
                    self.logger.error(
                        f"Error parsing function {node.name} in {file_path}: {e!s}",
                    )
                    # Continue parsing other functions
                    continue

        return FileModel(
            path=file_path,
            classes=classes,
            functions=functions,
            imports=imports,
        )
