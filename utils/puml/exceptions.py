"""
PlantUML Utilities Exceptions

This module defines custom exceptions used throughout the PlantUML utilities package.
"""


class PlantUMLError(Exception):
    """Base exception for all PlantUML utility errors."""

    pass


class ConfigurationError(PlantUMLError):
    """Raised when there is a configuration-related error."""

    pass


class ProjectRootError(ConfigurationError):
    """Raised when the project root directory cannot be determined."""

    pass


class PathError(PlantUMLError):
    """Raised when there is a path-related error."""

    pass


class RenderError(PlantUMLError):
    """Raised when there is an error rendering a diagram."""

    pass


class LoggingError(PlantUMLError):
    """Raised when there is a logging-related error."""

    pass


class AnalyzerError(PlantUMLError):
    """Base exception for code analyzer errors."""

    pass


class InvalidPathError(AnalyzerError):
    """Raised when an invalid path is provided."""

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Path does not exist or is not a Python file: {path}")


class NoFilesAnalyzedError(AnalyzerError):
    """Raised when no Python files were successfully analyzed."""

    def __init__(self):
        super().__init__("No Python files were successfully analyzed")


class ParseError(AnalyzerError):
    """Raised when there is an error parsing Python code."""

    def __init__(self, path: str, error: Exception):
        self.path = path
        self.original_error = error
        super().__init__(f"Error parsing {path}: {error}")


class DiagramGenerationError(AnalyzerError):
    """Raised when there is an error generating a diagram."""

    pass


class CacheError(AnalyzerError):
    """Raised when there is an error with the caching system."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.original_error = original_error
        super().__init__(f"Cache error: {message}")


class FilterError(AnalyzerError):
    """Raised when there is an error applying filters to the analysis."""

    def __init__(self, message: str, pattern: str | None = None):
        self.pattern = pattern
        super().__init__(
            f"Filter error: {message}" + (f" (pattern: {pattern})" if pattern else ""),
        )
