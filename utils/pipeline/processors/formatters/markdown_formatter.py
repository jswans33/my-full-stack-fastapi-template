"""
Markdown formatter implementation.

This module provides functionality for formatting extracted PDF content into Markdown.
"""

from typing import Any, Dict, List

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
            content_tree = self._build_content_tree(analyzed_data.get("sections", []))

            # Convert content tree to markdown string
            content_markdown = ""
            for section in content_tree:
                content_markdown += self._format_section_to_markdown(section)

            # Convert tables to markdown string
            tables_markdown = ""
            for table in analyzed_data.get("tables", []):
                tables_markdown += self._format_table_to_markdown(table)

            # Create formatted data with strings for content and tables
            formatted_data = {
                "document": {
                    "metadata": analyzed_data.get("metadata", {}),
                    "path": analyzed_data.get("path", ""),
                    "type": analyzed_data.get("type", ""),
                },
                "content": content_markdown,
                "tables": tables_markdown,
                "summary": analyzed_data.get("summary", {}),
                "validation": analyzed_data.get("validation", {}),
            }

            # Add classification if present
            if "classification" in analyzed_data:
                formatted_data["classification"] = analyzed_data["classification"]

            return formatted_data

        except Exception as e:
            self.logger.error(f"Error formatting PDF content: {str(e)}", exc_info=True)
            raise

    def _build_content_tree(
        self, sections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Build a hierarchical tree structure from flat sections list.
        This matches the structure returned by JSONFormatter._build_content_tree().

        Args:
            sections: List of section dictionaries

        Returns:
            List of sections with hierarchical structure
        """
        if not sections:
            return []

        # Initialize with root level sections
        result = []
        current_section = None
        current_level = 0
        section_stack = []  # [(section, level)]

        for section in sections:
            title = section.get("title", "")
            level = section.get("level", 0)
            content = section.get("content", "")

            new_section = {
                "title": title,
                "content": content,
                "children": [],
                "level": level,
            }

            # Add any additional metadata
            if "font" in section:
                new_section["font"] = section["font"]

            # Handle section nesting
            if not current_section:
                # First section
                result.append(new_section)
                current_section = new_section
                current_level = level
                section_stack.append((current_section, current_level))
            else:
                if level > current_level:
                    # Child section
                    current_section["children"].append(new_section)
                    section_stack.append((current_section, current_level))
                    current_section = new_section
                    current_level = level
                else:
                    # Sibling or uncle section
                    while section_stack and section_stack[-1][1] >= level:
                        section_stack.pop()

                    if section_stack:
                        # Add as child to nearest parent
                        parent, _ = section_stack[-1]
                        parent["children"].append(new_section)
                    else:
                        # No parent found, add to root
                        result.append(new_section)

                    current_section = new_section
                    current_level = level
                    section_stack.append((current_section, current_level))

        return result

    def _format_section_to_markdown(self, section: Dict[str, Any]) -> str:
        """
        Convert a section dictionary to markdown text.

        Args:
            section: Section dictionary with title, content, children, and level

        Returns:
            Markdown formatted string for the section
        """
        markdown_lines = []

        # Add section header with appropriate level
        if section.get("title"):
            level = section.get("level", 0)
            markdown_lines.append(f"{'#' * (level + 1)} {section['title']}\n")

        # Add section content
        if section.get("content"):
            markdown_lines.append(f"{section['content']}\n")

        # Process children recursively
        for child in section.get("children", []):
            markdown_lines.append(self._format_section_to_markdown(child))

        return "\n".join(markdown_lines)

    def _format_table_to_markdown(self, table: Dict[str, Any]) -> str:
        """
        Format a table dictionary to markdown.

        Args:
            table: Table dictionary with headers and data

        Returns:
            Markdown formatted table string
        """
        markdown_lines = []

        if "headers" in table and "data" in table:
            # Add table headers
            headers = table["headers"]
            markdown_lines.append("| " + " | ".join(headers) + " |")
            markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

            # Add table data
            for row in table["data"]:
                markdown_lines.append(
                    "| " + " | ".join(str(cell) for cell in row) + " |"
                )

            markdown_lines.append("")  # Add empty line after table

        return "\n".join(markdown_lines)

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
                f.write("\n")

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

            # Write classification if present
            classification = data.get("classification", {})
            if classification:
                f.write("# Classification\n\n")
                f.write(
                    f"- Document Type: {classification.get('document_type', 'Unknown')}\n"
                )
                f.write(f"- Confidence: {classification.get('confidence', 0.0):.2f}\n")
                f.write(
                    f"- Schema Pattern: {classification.get('schema_pattern', 'Unknown')}\n"
                )

                key_features = classification.get("key_features", [])
                if key_features:
                    f.write("- Key Features:\n")
                    for feature in key_features:
                        f.write(f"  - {feature}\n")
                f.write("\n")
