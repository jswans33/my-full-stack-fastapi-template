"""
Base formatter strategy.

This module provides the base strategy interface for formatters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class FormatterStrategy(ABC):
    """Base strategy for formatters."""

    @abstractmethod
    def format(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the analyzed data into a specific output structure.

        Args:
            analyzed_data: Data to format

        Returns:
            Formatted data structure
        """
        pass

    @abstractmethod
    def write(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Write formatted data to a file.

        Args:
            data: Formatted data to write
            output_path: Path to output file
        """
        pass
