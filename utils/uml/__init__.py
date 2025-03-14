"""UML diagram generation package.

This package provides tools for generating UML diagrams from Python code.
"""

# Import key modules to make them available at the package level
from utils.uml.core.filesystem import DefaultFileSystem, FileSystem
from utils.uml.core.service import UmlService
from utils.uml.factories import DefaultDiagramFactory

# Define package version
__version__ = "0.1.0"
