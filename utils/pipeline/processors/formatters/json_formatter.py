"""
JSON formatter implementation.

This module provides functionality for formatting extracted PDF content into JSON.
"""

import json
from typing import Any, Dict, List

from utils.pipeline.strategies.formatter import FormatterStrategy
from utils.pipeline.utils.logging import get_logger


class JSONFormatter(FormatterStrategy):
    """Formats extracted PDF content into readable JSON with proper indentation."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def format(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the analyzed data into a hierarchical JSON structure.

        Args:
            analyzed_data: Data from the PDF analyzer

        Returns:
            Formatted JSON structure with proper indentation
        """
        self.logger.info("Formatting PDF content as JSON")

        try:
            # Build hierarchical structure
            formatted_data = {
                "document": {
                    "metadata": analyzed_data.get("metadata", {}),
                    "path": analyzed_data.get("path", ""),
                    "type": analyzed_data.get("type", ""),
                },
                "content": self._build_content_tree(analyzed_data.get("sections", [])),
                "tables": analyzed_data.get("tables", []),
                "summary": analyzed_data.get("summary", {}),
                "validation": analyzed_data.get("validation", {}),
                "classification": analyzed_data.get(
                    "classification", {}
                ),  # Include classification information
            }

            return formatted_data

        except Exception as e:
            self.logger.error(f"Error formatting PDF content: {str(e)}", exc_info=True)
            raise

    def _build_content_tree(
        self, sections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Build a hierarchical tree structure from flat sections list.

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
            title = section["title"]
            level = self._determine_section_level(title)

            new_section = {
                "title": title,
                "content": section.get("content", ""),
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

    def _determine_section_level(self, title: str) -> int:
        """
        Determine section level based on title format.

        Args:
            title: Section title

        Returns:
            Integer indicating section level (0 = top level)
        """
        # Main section headers (e.g., "HEATING SYSTEMS")
        if title.isupper() and len(title.split()) > 1:
            return 0

        # Numbered sections (e.g., "1.0", "2.1", etc.)
        if any(title.startswith(str(i) + ".") for i in range(1, 20)):
            return 1

        # Lettered subsections (e.g., "A.", "B.", etc.)
        if len(title) == 2 and title[0].isupper() and title[1] == ".":
            return 2

        # Numbered subsections (e.g., "1.", "2.", etc.)
        if title.rstrip(".").isdigit():
            return 2

        # Default to deepest level
        return 3

    def write(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Write formatted data to a JSON file with proper indentation.

        Args:
            data: Formatted data to write
            output_path: Path to output file
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
