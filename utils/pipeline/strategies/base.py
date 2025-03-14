"""
Base strategy interfaces for document processing.

This module defines the abstract base classes for the strategy pattern
used in the document processing pipeline.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class AnalyzerStrategy(ABC):
    """Base interface for document analyzer strategies."""

    @abstractmethod
    def analyze(self, input_path: str) -> Dict[str, Any]:
        """
        Analyze document structure and extract metadata.

        Args:
            input_path: Path to the document

        Returns:
            Dictionary with document structure and metadata
        """
        pass


class CleanerStrategy(ABC):
    """Base interface for document cleaner strategies."""

    @abstractmethod
    def clean(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize document content.

        Args:
            analysis_result: Result from the document analyzer

        Returns:
            Cleaned data dictionary
        """
        pass


class ExtractorStrategy(ABC):
    """Base interface for document extractor strategies."""

    @abstractmethod
    def extract(self, cleaned_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from cleaned content.

        Args:
            cleaned_data: Cleaned data from the document cleaner

        Returns:
            Extracted structured data
        """
        pass


class ValidatorStrategy(ABC):
    """Base interface for document validator strategies."""

    @abstractmethod
    def validate(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted document data.

        Args:
            extracted_data: Data extracted from the document

        Returns:
            Validated data with validation results
        """
        pass


class FormatterStrategy(ABC):
    """Base interface for document formatter strategies."""

    @abstractmethod
    def format(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format validated document data for output.

        Args:
            validated_data: Validated data from the document validator

        Returns:
            Formatted output data
        """
        pass
