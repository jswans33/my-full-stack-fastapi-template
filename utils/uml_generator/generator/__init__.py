"""Generator module for UML diagram generation.

This module provides generators for converting parsed code models into various
UML diagram formats. Currently supports PlantUML output format.
"""

from .plantuml_generator import PlantUmlGenerator

__all__ = ["PlantUmlGenerator"]
