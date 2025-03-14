"""Exception classes for UML diagram generation.

This module defines the exception classes used throughout the UML generation package.
"""


class UMLGeneratorError(Exception):
    """Base exception for all UML generator errors."""

    def __init__(self, message: str, cause: Exception | None = None):
        """Initialize a UML generator error.

        Args:
            message: The error message
            cause: The exception that caused this error, if any
        """
        self.message = message
        self.cause = cause
        super().__init__(message)


class ConfigurationError(UMLGeneratorError):
    """Exception raised for configuration errors."""

    pass


class ParserError(UMLGeneratorError):
    """Exception raised when parsing code fails."""

    pass


class GeneratorError(UMLGeneratorError):
    """Exception raised when generating diagrams fails."""

    pass


class FileSystemError(UMLGeneratorError):
    """Exception raised for file system operations errors."""

    pass


class DiagramTypeError(UMLGeneratorError):
    """Exception raised when an unsupported diagram type is requested."""

    pass
