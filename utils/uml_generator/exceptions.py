"""Custom exceptions for the UML generator."""


class UmlGeneratorError(Exception):
    """Base exception for UML generator errors."""

    pass


class ParserError(UmlGeneratorError):
    """Raised when there's an error during code parsing."""

    def __init__(
        self, message: str, filename: str | None = None, line_number: int | None = None
    ):
        self.filename = filename
        self.line_number = line_number
        super().__init__(
            f"Parser error in {filename or 'unknown file'}"
            + (f" at line {line_number}" if line_number else "")
            + f": {message}"
        )


class SyntaxParsingError(ParserError):
    """Raised when there's a syntax error in the source code."""

    pass


class TypeAnnotationError(ParserError):
    """Raised when there's an error parsing type annotations."""

    pass


class ImportError(ParserError):
    """Raised when there's an error parsing imports."""

    pass


class FileSystemError(UmlGeneratorError):
    """Raised when there's an error accessing the file system."""

    pass


class ConfigurationError(UmlGeneratorError):
    """Raised when there's an error in the configuration."""

    pass


class GeneratorError(UmlGeneratorError):
    """Raised when there's an error during UML diagram generation."""

    pass
