"""
Markdown formatter implementation.

This module provides functionality for formatting extracted PDF content into Markdown.
"""

from typing import Any, Dict

from utils.pipeline.strategies.formatter import FormatterStrategy
from utils.pipeline.utils.logging import get_logger


class MarkdownFormatter(FormatterStrategy):
    """Formats extracted PDF content into readable Markdown."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def format(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the analyzed data into a Markdown structure.

        Args:
            analyzed_data: Data from the PDF analyzer

        Returns:
            Formatted data structure with Markdown content
        """
        self.logger.info("Formatting PDF content as Markdown")

        try:
            # Build hierarchical structure
            formatted_data = {
                "document": {
                    "metadata": analyzed_data.get("metadata", {}),
                    "path": analyzed_data.get("path", ""),
                    "type": analyzed_data.get("type", ""),
                },
                "content": self._build_markdown_content(
                    analyzed_data.get("sections", [])
                ),
                "tables": self._format_tables(analyzed_data.get("tables", [])),
                "summary": analyzed_data.get("summary", {}),
                "validation": analyzed_data.get("validation", {}),
            }

            return formatted_data

        except Exception as e:
            self.logger.error(f"Error formatting PDF content: {str(e)}", exc_info=True)
            raise

    def _build_markdown_content(self, sections: list) -> str:
        """
        Convert sections into Markdown format.

        Args:
            sections: List of section dictionaries

        Returns:
            Markdown formatted string
        """
        if not sections:
            return ""

        markdown = []
        for section in sections:
            level = section.get("level", 0)
            title = section.get("title", "")
            content = section.get("content", "")

            # Add section header with appropriate level
            if title:
                markdown.append(f"{'#' * (level + 1)} {title}\n")

            # Add section content
            if content:
                markdown.append(f"{content}\n")

            # Process children recursively
            children = section.get("children", [])
            if children:
                markdown.append(self._build_markdown_content(children))

        return "\n".join(markdown)

    def _format_tables(self, tables: list) -> str:
        """
        Format tables in Markdown.

        Args:
            tables: List of table data

        Returns:
            Markdown formatted tables
        """
        if not tables:
            return ""

        markdown = []
        for table in tables:
            if "headers" in table and "data" in table:
                # Add table headers
                headers = table["headers"]
                markdown.append("| " + " | ".join(headers) + " |")
                markdown.append("| " + " | ".join(["---"] * len(headers)) + " |")

                # Add table data
                for row in table["data"]:
                    markdown.append("| " + " | ".join(str(cell) for cell in row) + " |")
                markdown.append("\n")

        return "\n".join(markdown)

    def write(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Write formatted data to a Markdown file.

        Args:
            data: Formatted data to write
            output_path: Path to output file
        """
        with open(output_path, "w", encoding="utf-8") as f:
            # Write document metadata
            doc = data.get("document", {})
            f.write("# Document Information\n\n")
            f.write(f"- Path: {doc.get('path', '')}\n")
            f.write(f"- Type: {doc.get('type', '')}\n\n")

            # Write metadata
            metadata = doc.get("metadata", {})
            if metadata:
                f.write("## Metadata\n\n")
                for key, value in metadata.items():
                    f.write(f"- {key}: {value}\n")
                f.write("\n")

            # Write content
            content = data.get("content", "")
            if content:
                f.write("# Content\n\n")
                f.write(content)
                f.write("\n\n")

            # Write tables
            tables = data.get("tables", "")
            if tables:
                f.write("# Tables\n\n")
                f.write(tables)
                f.write("\n")

            # Write summary
            summary = data.get("summary", {})
            if summary:
                f.write("# Summary\n\n")
                for key, value in summary.items():
                    f.write(f"## {key}\n\n{value}\n\n")
