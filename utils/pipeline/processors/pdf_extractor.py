"""
PDF data extractor implementation.

This module provides functionality for extracting structured data from PDF content.
"""

import re
from typing import Any, Dict, List

import fitz  # PyMuPDF

from utils.pipeline.strategies.base import ExtractorStrategy
from utils.pipeline.utils.logging import get_logger


class PDFExtractor(ExtractorStrategy):
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
                    # Add to current section content WITHOUT truncation
                    current_section["content"] += line + "\n"

        # Add the last section
        if current_section["content"]:
            sections.append(current_section)

        return sections

    def _extract_tables(self, doc) -> List[Dict[str, Any]]:
        """
        Extract tables from the PDF document with improved structure detection.

        Args:
            doc: PyMuPDF document

        Returns:
            List of extracted tables with structure
        """
        tables = []

        try:
            # Use PyMuPDF's improved table detection
            for page_num, page in enumerate(doc):
                # First try to detect tables using layout analysis
                try:
                    # Get blocks that might be tables
                    blocks = page.get_text("dict")["blocks"]

                    for block in blocks:
                        # Check if block has multiple lines (potential table)
                        if "lines" in block and len(block["lines"]) > 2:
                            table_data = []
                            headers = []

                            # Process rows
                            for row_idx, line in enumerate(block["lines"]):
                                if "spans" not in line:
                                    continue

                                row_data = [span["text"] for span in line["spans"]]

                                # First row might be headers
                                if row_idx == 0 and any(
                                    cell.isupper() for cell in row_data if cell
                                ):
                                    headers = row_data
                                else:
                                    table_data.append(row_data)

                            # Only add if we have actual data
                            if table_data:
                                # Add table with structure
                                tables.append(
                                    {
                                        "page": page_num + 1,
                                        "table_number": len(tables) + 1,
                                        "headers": headers,
                                        "data": table_data,
                                        "column_count": len(headers)
                                        if headers
                                        else (
                                            max(len(row) for row in table_data)
                                            if table_data
                                            else 0
                                        ),
                                        "row_count": len(table_data),
                                        "detection_method": "layout_analysis",
                                    }
                                )
                except Exception as layout_error:
                    self.logger.warning(f"Layout analysis failed: {str(layout_error)}")

                # Fallback to text-based table detection
                if not any(table["page"] == page_num + 1 for table in tables):
                    text = page.get_text("text")

                    # Look for common table indicators
                    if any(pattern in text for pattern in ["TABLE", "Table", "|", "+"]):
                        # Try to detect table structure from text
                        lines = text.split("\n")
                        table_start = -1
                        table_end = -1

                        # Find table boundaries
                        for i, line in enumerate(lines):
                            if "TABLE" in line.upper() and table_start == -1:
                                table_start = i
                            elif table_start != -1 and not line.strip():
                                # Empty line might indicate end of table
                                if i > table_start + 2:  # At least 2 rows
                                    table_end = i
                                    break

                        # If we found a table
                        if table_start != -1 and table_end != -1:
                            table_lines = lines[table_start:table_end]

                            # Try to detect headers and data
                            headers = []
                            data = []

                            # First non-empty line after title might be headers
                            for i, line in enumerate(table_lines):
                                if i > 0 and line.strip():  # Skip title
                                    # Split by common delimiters
                                    cells = re.split(r"\s{2,}|\t|\|", line)
                                    cells = [
                                        cell.strip() for cell in cells if cell.strip()
                                    ]

                                    if not headers and any(
                                        cell.isupper() for cell in cells
                                    ):
                                        headers = cells
                                    else:
                                        data.append(cells)

                            # Add table with structure
                            if data:  # Only add if we have data
                                tables.append(
                                    {
                                        "page": page_num + 1,
                                        "table_number": len(tables) + 1,
                                        "headers": headers,
                                        "data": data,
                                        "column_count": len(headers)
                                        if headers
                                        else (
                                            max(len(row) for row in data) if data else 0
                                        ),
                                        "row_count": len(data),
                                        "detection_method": "text_analysis",
                                    }
                                )
        except Exception as e:
            self.logger.warning(f"Error during table extraction: {str(e)}")
            # Continue processing even if table extraction fails

        return tables
