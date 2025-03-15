"""
PDF formatter implementation.

This module provides functionality for formatting validated PDF data for output.
"""

from typing import Any, Dict

from utils.pipeline.strategies.base import FormatterStrategy
from utils.pipeline.utils.logging import get_logger


class PDFFormatter(FormatterStrategy):
    """Formats validated PDF data for output."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def format(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format validated PDF data for output.

        Args:
            validated_data: Validated data from the PDF validator

        Returns:
            Formatted output data
        """
        self.logger.info(
            f"Formatting output for: {validated_data.get('path', 'unknown')}"
        )

        # Create a clean output structure
        output = {
            "document": {
                "type": "pdf",
                "path": validated_data.get("path", ""),
                "metadata": self._format_metadata(validated_data.get("metadata", {})),
            },
            "content": {
                "sections": self._format_sections(validated_data.get("sections", [])),
                "tables": self._format_tables(validated_data.get("tables", [])),
            },
            "validation": validated_data.get("validation", {"is_valid": True}),
        }

        # Add summary information
        output["summary"] = self._create_summary(output)

        return output

    def _format_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format metadata section."""
        formatted_metadata = {}

        # Format standard metadata fields
        standard_fields = [
            "page_count",
            "title",
            "author",
            "subject",
            "keywords",
            "creator",
            "producer",
            "creation_date",
            "modification_date",
        ]

        for field in standard_fields:
            value = metadata.get(field)
            if value is not None:
                formatted_metadata[field] = value

        # Format any additional metadata fields
        for key, value in metadata.items():
            if key not in standard_fields and value is not None:
                formatted_metadata[key] = value

        return formatted_metadata

    def _format_sections(self, sections: list) -> list:
        """Format document sections."""
        formatted_sections = []

        for section in sections:
            if not isinstance(section, dict):
                continue

            formatted_section = {
                "title": section.get("title", "").strip(),
                "content": self._clean_content(section.get("content", "")),
            }

            # Add any additional section metadata if present
            for key, value in section.items():
                if key not in ["title", "content"] and value is not None:
                    formatted_section[key] = value

            formatted_sections.append(formatted_section)

        return formatted_sections

    def _format_tables(self, tables: list) -> list:
        """Format extracted tables."""
        formatted_tables = []

        for table in tables:
            if not isinstance(table, dict):
                continue

            formatted_table = {
                "page": table.get("page"),
                "table_number": table.get("table_number"),
                "data": table.get("data"),
            }

            # Add accuracy score if available
            accuracy = table.get("accuracy")
            if accuracy is not None:
                formatted_table["accuracy"] = accuracy

            # Add any additional table metadata if present
            for key, value in table.items():
                if (
                    key not in ["page", "table_number", "data", "accuracy"]
                    and value is not None
                ):
                    formatted_table[key] = value

            formatted_tables.append(formatted_table)

        return formatted_tables

    def _clean_content(self, content: str) -> str:
        """Clean and normalize content text."""
        if not content:
            return ""

        # Remove any trailing whitespace from lines while preserving intentional line breaks
        lines = [line.rstrip() for line in content.splitlines()]

        # Remove any empty lines at the start and end while preserving internal empty lines
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        return "\n".join(lines)

    def _create_summary(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the document content."""
        content = output["content"]
        validation = output["validation"]

        summary = {
            "title": output["document"]["metadata"].get("title", "Untitled"),
            "page_count": output["document"]["metadata"].get("page_count", 0),
            "section_count": len(content["sections"]),
            "table_count": len(content["tables"]),
            "is_valid": validation.get("is_valid", True),
            "has_errors": bool(validation.get("errors", [])),
            "has_warnings": bool(validation.get("warnings", [])),
        }

        # Add error and warning counts if present
        errors = validation.get("errors", [])
        warnings = validation.get("warnings", [])
        if errors:
            summary["error_count"] = len(errors)
        if warnings:
            summary["warning_count"] = len(warnings)

        return summary
