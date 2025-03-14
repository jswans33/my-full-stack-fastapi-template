"""Import statement parsing utilities."""

import ast
import logging

from ...exceptions import ImportError
from ...models import ImportModel


class ImportParser:
    """Parser for Python import statements."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_imports(self, tree: ast.AST) -> list[ImportModel]:
        """Parse imports from an AST tree.

        Args:
            tree: AST tree to parse

        Returns:
            List of ImportModel objects

        Raises:
            ImportError: If there's an error parsing imports
        """
        try:
            imports: list[ImportModel] = []

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

        except Exception as e:
            raise ImportError(
                f"Failed to parse imports: {e!s}",
                line_number=getattr(node, "lineno", None),
            )
