"""
PDF validator implementation.

This module provides functionality for validating extracted PDF data.
"""

from typing import Any, Dict

from utils.pipeline.strategies.base import ValidatorStrategy
from utils.pipeline.utils.logging import get_logger


class PDFValidator(ValidatorStrategy):
    """Validates extracted PDF data."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def validate(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted PDF data.

        Args:
            extracted_data: Data extracted from the PDF

        Returns:
            Validated data with validation results
        """
        self.logger.info(
            f"Validating extracted data for: {extracted_data.get('path', 'unknown')}"
        )

        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }

        # Validate metadata
        self._validate_metadata(extracted_data, validation_results)

        # Validate sections
        self._validate_sections(extracted_data, validation_results)

        # Validate tables
        self._validate_tables(extracted_data, validation_results)

        # Update validation status
        if validation_results["errors"]:
            validation_results["is_valid"] = False

        # Return validated data
        return {
            **extracted_data,
            "validation": validation_results,
        }

    def _validate_metadata(
        self, extracted_data: Dict[str, Any], validation_results: Dict[str, Any]
    ) -> None:
        """Validate metadata section."""
        metadata = extracted_data.get("metadata", {})
        if not metadata:
            validation_results["warnings"].append("Missing or empty metadata")
            return

        # Check required metadata fields
        required_fields = ["page_count"]
        for field in required_fields:
            if field not in metadata:
                validation_results["errors"].append(
                    f"Missing required metadata: {field}"
                )

        # Check optional metadata fields
        optional_fields = ["title", "author", "subject", "keywords"]
        for field in optional_fields:
            if not metadata.get(field):
                validation_results["warnings"].append(
                    f"Missing optional metadata: {field}"
                )

    def _validate_sections(
        self, extracted_data: Dict[str, Any], validation_results: Dict[str, Any]
    ) -> None:
        """Validate sections content."""
        sections = extracted_data.get("sections", [])
        if not sections:
            validation_results["warnings"].append("No sections extracted")
            return

        for i, section in enumerate(sections):
            # Validate section structure
            if not isinstance(section, dict):
                validation_results["errors"].append(
                    f"Invalid section structure at index {i}"
                )
                continue

            # Validate section title
            if not section.get("title"):
                validation_results["errors"].append(f"Section {i + 1} missing title")

            # Validate section content
            if not section.get("content"):
                validation_results["warnings"].append(
                    f"Section '{section.get('title', f'Section {i + 1}')}' has no content"
                )

            # Check for reasonable content length
            content = section.get("content", "")
            if len(content) < 10:  # Arbitrary minimum length
                validation_results["warnings"].append(
                    f"Section '{section.get('title', f'Section {i + 1}')}' has very short content"
                )

    def _validate_tables(
        self, extracted_data: Dict[str, Any], validation_results: Dict[str, Any]
    ) -> None:
        """Validate extracted tables."""
        tables = extracted_data.get("tables", [])
        if not tables:
            validation_results["warnings"].append("No tables extracted")
            return

        for i, table in enumerate(tables):
            # Validate table structure
            if not isinstance(table, dict):
                validation_results["errors"].append(
                    f"Invalid table structure at index {i}"
                )
                continue

            # Validate required table fields
            required_fields = ["page", "table_number", "data"]
            for field in required_fields:
                if field not in table:
                    validation_results["errors"].append(
                        f"Table {i + 1} missing required field: {field}"
                    )

            # Validate table data
            data = table.get("data")
            if isinstance(data, str):
                # This is likely a fallback message when table extraction failed
                validation_results["warnings"].append(
                    f"Table {i + 1} contains placeholder data: {data}"
                )
            elif isinstance(data, list):
                if not data:
                    validation_results["warnings"].append(f"Table {i + 1} is empty")
