"""
PDF data extractor implementation.

This module provides functionality for extracting structured data from PDF content.
"""

import re
from typing import Any, Dict, List

import fitz

from utils.pipeline.utils.logging import get_logger


class PDFExtractor:
    """Extracts structured data from PDF content."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def extract(self, cleaned_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from cleaned PDF content.

        Args:
            cleaned_data: Cleaned data from the PDF cleaner

        Returns:
            Extracted structured data including schema
        """
        self.logger.info(
            f"Extracting data from PDF: {cleaned_data.get('path', 'unknown')}"
        )

        try:
            # Extract sections and content
            doc = fitz.open(cleaned_data["path"])

            # Extract text by sections
            sections = self._extract_sections(doc)

            # Extract tables if present
            tables = self._extract_tables(doc)

            # Extract schema structure
            schema = self._extract_schema(sections)

            doc.close()

            # Return extracted data
            return {
                "metadata": cleaned_data["metadata"],
                "sections": sections,
                "tables": tables,
                "schema": schema,
                "path": cleaned_data["path"],
            }

        except Exception as e:
            self.logger.error(
                f"Error extracting data from PDF: {str(e)}", exc_info=True
            )
            raise

    def _extract_schema(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract schema structure from sections.

        Args:
            sections: List of extracted sections

        Returns:
            Schema structure
        """
        schema = {
            "type": "object",
            "title": "CSI Specification Schema",
            "properties": {},
            "required": [],
        }

        # Track section numbers and their hierarchy
        current_section = None
        section_pattern = re.compile(r"^([A-Z][0-9]+(?:\.[0-9]+)*)")

        for section in sections:
            title = section.get("title", "")
            match = section_pattern.match(title)

            if match:
                section_number = match.group(1)
                section_name = title.replace(section_number, "").strip()

                # Add to schema properties
                schema["properties"][section_number] = {
                    "type": "object",
                    "title": section_name,
                    "properties": {
                        "content": {"type": "string"},
                        "subsections": {"type": "object"},
                    },
                }

                # Track required fields
                schema["required"].append(section_number)

                # Handle subsections
                if "children" in section:
                    subsections_schema = self._extract_schema(section["children"])
                    schema["properties"][section_number]["properties"][
                        "subsections"
                    ] = subsections_schema

        return schema

    def _extract_sections(self, doc) -> List[Dict[str, Any]]:
        """
        Extract sections from the PDF document.

        Args:
            doc: PyMuPDF document

        Returns:
            List of sections with titles and content
        """
        sections = []
        current_section = {"title": "Introduction", "content": ""}

        for page in doc:
            text = page.get_text("text")

            # Split text into lines
            lines = text.split("\n")

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Heuristic for section headers (customize based on document)
                if (
                    re.match(r"^[0-9.]+\s+[A-Z]", line)
                    or line.isupper()
                    or len(line) < 50
                    and line.endswith(":")
                ):
                    # Save previous section if it has content
                    if current_section["content"]:
                        sections.append(current_section)

                    # Start new section
                    current_section = {"title": line, "content": ""}
                else:
                    # Add to current section content
                    current_section["content"] += line + "\n"

        # Add the last section
        if current_section["content"]:
            sections.append(current_section)

        return sections

    def _extract_tables(self, doc) -> List[Dict[str, Any]]:
        """
        Extract tables from the PDF document.

        Args:
            doc: PyMuPDF document

        Returns:
            List of extracted tables
        """
        tables = []

        try:
            # Simple table detection using PyMuPDF
            for page_num, page in enumerate(doc):
                text = page.get_text("text")
                # Look for common table indicators
                if any(pattern in text for pattern in ["TABLE", "Table", "|", "+"]):
                    # Extract text blocks that might be tables
                    blocks = page.get_text("blocks")
                    for i, block in enumerate(blocks):
                        if (
                            len(block[4].split("\n")) > 2
                        ):  # More than 2 lines might be a table
                            tables.append(
                                {
                                    "page": page_num + 1,
                                    "table_number": len(tables) + 1,
                                    "data": block[4].split("\n"),
                                    "accuracy": None,
                                }
                            )
        except Exception as e:
            self.logger.warning(f"Error during table extraction: {str(e)}")
            # Continue processing even if table extraction fails

        return tables
