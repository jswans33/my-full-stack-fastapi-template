"""
PDF data extractor implementation.

This module provides functionality for extracting structured data from PDF content.
"""

import re
from typing import Any, Dict, List, Tuple

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

    def _contains_table_label(self, text: str) -> bool:
        """
        Check if text contains explicit table labels.
        Uses a regex pattern to find table labels anywhere in the text.

        Args:
            text: Text to check for table labels

        Returns:
            Boolean indicating if the text contains table labels
        """
        # Look for common table indicators like "TABLE X", "Table X", etc.
        # Using word boundary to find labels anywhere in text
        return bool(re.search(r"\b(TABLE|Table)\s+[A-Za-z0-9\-\._]+", text))

    def _is_likely_table(self, block: Dict[str, Any]) -> bool:
        """
        Determine if a block is likely to be a table based on structure.
        Uses stricter criteria to reduce false positives.

        Args:
            block: A block from PyMuPDF's layout analysis

        Returns:
            Boolean indicating if the block is likely a table
        """
        if "lines" not in block or len(block["lines"]) < 3:
            return False

        # Check for consistent number of spans across lines
        span_counts = [len(line.get("spans", [])) for line in block["lines"]]

        # Require at least 2 columns consistently across rows
        if min(span_counts) < 2:
            return False

        # Check for consistency in column count (allow some variation)
        if max(span_counts) - min(span_counts) > 1:
            return False

        # Check for consistent horizontal alignment of spans (column alignment)
        positions_per_column = {}
        for line in block["lines"]:
            for idx, span in enumerate(line.get("spans", [])):
                if idx < len(line.get("spans", [])):
                    x_pos = round(span["origin"][0], 1)
                    positions_per_column.setdefault(idx, []).append(x_pos)

        # Verify column alignment consistency
        for positions in positions_per_column.values():
            if (
                max(positions) - min(positions) > 20
            ):  # Slightly relaxed alignment tolerance
                return False

        # Check for explicit table indicators in text
        block_text = ""
        for line in block["lines"]:
            for span in line.get("spans", []):
                block_text += span.get("text", "") + " "

        if self._contains_table_label(block_text):
            return True

        # Check for grid-like structure (lines or borders)
        if "lines" in block and any("rect" in line for line in block["lines"]):
            return True

        # Must have at least 3 distinct column positions
        x_positions = []
        for line in block["lines"]:
            for span in line.get("spans", []):
                x_positions.append(span["origin"][0])

        unique_x = set(round(x, 1) for x in x_positions)
        if len(unique_x) < 3:  # Require at least 3 distinct column positions
            return False

        return True

    def _extract_table_data(
        self, block: Dict[str, Any]
    ) -> Tuple[List[List[str]], List[str], int]:
        """
        Extract structured data from a table block.

        Args:
            block: A block from PyMuPDF's layout analysis

        Returns:
            Tuple of (table_data, headers, column_count)
        """
        table_data = []
        headers = []

        # Identify potential column positions
        x_positions = []
        for line in block["lines"]:
            for span in line.get("spans", []):
                x_positions.append(span["origin"][0])

        # Group x-positions to identify column boundaries
        x_clusters = self._cluster_positions(x_positions)

        # Process rows
        for row_idx, line in enumerate(block["lines"]):
            if "spans" not in line:
                continue

            # Map spans to columns based on x-position
            row_data = [""] * len(x_clusters)
            for span in line["spans"]:
                col_idx = self._get_column_index(span["origin"][0], x_clusters)
                if col_idx >= 0:
                    row_data[col_idx] += span["text"] + " "

            # Clean up row data
            row_data = [cell.strip() for cell in row_data]

            # Skip empty rows
            if not any(cell for cell in row_data):
                continue

            # First row might be headers
            if row_idx == 0 and any(cell.isupper() for cell in row_data if cell):
                headers = row_data
            else:
                # Only add non-empty rows
                if any(cell for cell in row_data):
                    table_data.append(row_data)

        # Determine column count
        column_count = (
            len(headers)
            if headers
            else (max(len(row) for row in table_data) if table_data else 0)
        )

        return table_data, headers, column_count

    def _cluster_positions(
        self, positions: List[float], threshold: float = 10
    ) -> List[float]:
        """
        Cluster x-positions to identify column boundaries.

        Args:
            positions: List of x-positions
            threshold: Distance threshold for clustering

        Returns:
            List of average positions for each cluster
        """
        if not positions:
            return []

        # Sort positions
        sorted_pos = sorted(positions)

        # Initialize clusters
        clusters = [[sorted_pos[0]]]

        # Cluster positions
        for pos in sorted_pos[1:]:
            if pos - clusters[-1][-1] <= threshold:
                # Add to existing cluster
                clusters[-1].append(pos)
            else:
                # Start new cluster
                clusters.append([pos])

        # Get average position for each cluster
        return [sum(cluster) / len(cluster) for cluster in clusters]

    def _get_column_index(
        self, x_position: float, column_positions: List[float]
    ) -> int:
        """
        Determine which column a span belongs to based on its x-position.

        Args:
            x_position: X-position of the span
            column_positions: List of column positions

        Returns:
            Index of the column, or -1 if no match
        """
        for i, pos in enumerate(column_positions):
            if abs(x_position - pos) <= 20:  # Threshold for matching
                return i
        return -1

    def _detect_table_borders(self, page) -> List[Dict[str, Any]]:
        """
        Detect table borders in a page.

        Args:
            page: PyMuPDF page object

        Returns:
            List of dictionaries containing border information
        """
        border_info = []

        # Get the page's drawing commands which include lines and rectangles
        dl = page.get_drawings()

        # Filter for horizontal and vertical lines that might be table borders
        horizontal_lines = []
        vertical_lines = []

        for drawing in dl:
            if drawing["type"] == "l":  # Line
                # Get line coordinates
                x0, y0, x1, y1 = drawing["rect"]

                # Calculate line length and determine if horizontal or vertical
                width = abs(x1 - x0)
                height = abs(y1 - y0)

                # Lines with minimal curvature (nearly straight)
                if width > 20 and height < 2:  # Horizontal line
                    horizontal_lines.append(
                        {
                            "y": min(y0, y1),
                            "x0": min(x0, x1),
                            "x1": max(x0, x1),
                            "width": width,
                        }
                    )
                elif height > 20 and width < 2:  # Vertical line
                    vertical_lines.append(
                        {
                            "x": min(x0, x1),
                            "y0": min(y0, y1),
                            "y1": max(y0, y1),
                            "height": height,
                        }
                    )

            elif drawing["type"] == "re":  # Rectangle
                # Rectangles are often used for table cells or borders
                x0, y0, x1, y1 = drawing["rect"]

                # Add the four sides of the rectangle as lines
                # Top
                horizontal_lines.append(
                    {
                        "y": min(y0, y1),
                        "x0": min(x0, x1),
                        "x1": max(x0, x1),
                        "width": abs(x1 - x0),
                    }
                )
                # Bottom
                horizontal_lines.append(
                    {
                        "y": max(y0, y1),
                        "x0": min(x0, x1),
                        "x1": max(x0, x1),
                        "width": abs(x1 - x0),
                    }
                )
                # Left
                vertical_lines.append(
                    {
                        "x": min(x0, x1),
                        "y0": min(y0, y1),
                        "y1": max(y0, y1),
                        "height": abs(y1 - y0),
                    }
                )
                # Right
                vertical_lines.append(
                    {
                        "x": max(x0, x1),
                        "y0": min(y0, y1),
                        "y1": max(y0, y1),
                        "height": abs(y1 - y0),
                    }
                )

        # Group horizontal lines by similar y-coordinates (rows)
        y_threshold = 5  # Lines within 5 points are considered the same row
        horizontal_groups = self._group_lines_by_position(
            horizontal_lines, "y", y_threshold
        )

        # Group vertical lines by similar x-coordinates (columns)
        x_threshold = 5  # Lines within 5 points are considered the same column
        vertical_groups = self._group_lines_by_position(
            vertical_lines, "x", x_threshold
        )

        # If we have both horizontal and vertical lines forming a grid, it's likely a table
        if len(horizontal_groups) >= 3 and len(vertical_groups) >= 2:
            # Calculate table boundaries
            min_y = (
                min(group[0]["y"] for group in horizontal_groups)
                if horizontal_groups
                else 0
            )
            max_y = (
                max(group[0]["y"] for group in horizontal_groups)
                if horizontal_groups
                else 0
            )
            min_x = (
                min(group[0]["x"] for group in vertical_groups)
                if vertical_groups
                else 0
            )
            max_x = (
                max(group[0]["x"] for group in vertical_groups)
                if vertical_groups
                else 0
            )

            # Create border info
            border_info.append(
                {
                    "x0": min_x,
                    "y0": min_y,
                    "x1": max_x,
                    "y1": max_y,
                    "rows": len(horizontal_groups)
                    - 1,  # Number of rows (spaces between horizontal lines)
                    "cols": len(vertical_groups)
                    - 1,  # Number of columns (spaces between vertical lines)
                    "horizontal_lines": horizontal_groups,
                    "vertical_lines": vertical_groups,
                }
            )

        return border_info

    def _group_lines_by_position(
        self, lines: List[Dict[str, Any]], position_key: str, threshold: float
    ) -> List[List[Dict[str, Any]]]:
        """
        Group lines by their position (y for horizontal, x for vertical).

        Args:
            lines: List of line dictionaries
            position_key: Key to use for position ('x' or 'y')
            threshold: Distance threshold for grouping

        Returns:
            List of line groups
        """
        if not lines:
            return []

        # Sort lines by position
        sorted_lines = sorted(lines, key=lambda l: l[position_key])

        # Initialize groups
        groups = [[sorted_lines[0]]]

        # Group lines
        for line in sorted_lines[1:]:
            if abs(line[position_key] - groups[-1][0][position_key]) <= threshold:
                # Add to existing group
                groups[-1].append(line)
            else:
                # Start new group
                groups.append([line])

        return groups

    def _extract_labeled_tables(self, page, page_num) -> List[Dict[str, Any]]:
        """
        Extract tables that are explicitly labeled in the text.

        Args:
            page: PyMuPDF page object
            page_num: Page number

        Returns:
            List of tables extracted based on explicit labels
        """
        labeled_tables = []

        try:
            # Get page text
            text = page.get_text("text")

            # Find table labels
            table_matches = re.finditer(
                r"(TABLE\s+[A-Z0-9\-]+|Table\s+[A-Za-z0-9\-]+)", text
            )

            for match in table_matches:
                table_label = match.group(0)

                # Find the position of the table label
                label_pos = match.start()

                # Get text after the label to find the table content
                text_after_label = text[label_pos:]

                # Split into lines
                lines = text_after_label.split("\n")

                # Skip the label line
                table_lines = []
                table_start = False

                # Collect lines until we find an empty line or another table label
                for i, line in enumerate(lines):
                    if i == 0:  # This is the label line
                        continue

                    if not line.strip():
                        if table_start and len(table_lines) > 0:
                            # Empty line after table content - might be the end
                            break
                        continue

                    # Check if we've reached another table
                    if i > 1 and re.match(
                        r"(TABLE\s+[A-Z0-9\-]+|Table\s+[A-Za-z0-9\-]+)", line
                    ):
                        break

                    # Add line to table content
                    table_lines.append(line)
                    table_start = True

                # Process table lines to extract structure
                if len(table_lines) >= 2:  # Need at least header and one data row
                    # Try to identify headers and data
                    headers = []
                    data = []

                    # First line might be headers
                    header_line = table_lines[0]

                    # Split by common delimiters or multiple spaces
                    header_cells = re.split(r"\s{2,}|\t|\|", header_line)
                    header_cells = [
                        cell.strip() for cell in header_cells if cell.strip()
                    ]

                    if header_cells:
                        headers = header_cells

                    # Process data rows
                    for line in table_lines[1:]:
                        cells = re.split(r"\s{2,}|\t|\|", line)
                        cells = [cell.strip() for cell in cells if cell.strip()]

                        if cells:
                            data.append(cells)

                    # Only add if we have data
                    if data:
                        table_info = {
                            "page": page_num + 1,
                            "table_number": len(labeled_tables) + 1,
                            "table_label": table_label,
                            "headers": headers,
                            "data": data,
                            "column_count": len(headers)
                            if headers
                            else (max(len(row) for row in data) if data else 0),
                            "row_count": len(data),
                            "detection_method": "labeled_table",
                        }
                        labeled_tables.append(table_info)

                        # Enhanced logging for debugging
                        self.logger.debug(
                            f"Table found: page={page_num + 1}, method=labeled_table, "
                            f"label='{table_label}', rows={len(data)}, "
                            f"cols={table_info['column_count']}, headers={bool(headers)}"
                        )

        except Exception as e:
            self.logger.warning(f"Labeled table extraction failed: {str(e)}")

        return labeled_tables

    def _extract_tables(self, doc) -> List[Dict[str, Any]]:
        """
        Extract tables from the PDF document with improved structure detection.
        Uses a prioritized approach to reduce false positives.

        Args:
            doc: PyMuPDF document

        Returns:
            List of extracted tables with structure
        """
        tables = []

        try:
            # Use a prioritized approach to table detection
            for page_num, page in enumerate(doc):
                page_tables = []

                # STEP 1: First try to detect tables using border detection (most reliable)
                try:
                    border_info = self._detect_table_borders(page)

                    if border_info:
                        self.logger.info(
                            f"Found {len(border_info)} tables via border detection on page {page_num + 1}"
                        )

                        for table_border in border_info:
                            # Extract text within the table borders
                            table_rect = fitz.Rect(
                                table_border["x0"],
                                table_border["y0"],
                                table_border["x1"],
                                table_border["y1"],
                            )

                            # Get text within the table area
                            table_text = page.get_text("dict", clip=table_rect)

                            # Process text blocks within the table
                            table_data = []
                            headers = []

                            # Determine row boundaries from horizontal lines
                            row_boundaries = []
                            for group in table_border["horizontal_lines"]:
                                if group:  # Make sure the group is not empty
                                    row_boundaries.append(group[0]["y"])
                            row_boundaries.sort()

                            # Determine column boundaries from vertical lines
                            col_boundaries = []
                            for group in table_border["vertical_lines"]:
                                if group:  # Make sure the group is not empty
                                    col_boundaries.append(group[0]["x"])
                            col_boundaries.sort()

                            # Process text blocks and assign to cells based on position
                            for block in table_text.get("blocks", []):
                                if "lines" in block:
                                    for line in block["lines"]:
                                        if "spans" in line:
                                            for span in line["spans"]:
                                                # Find which row and column this text belongs to
                                                x, y = span["origin"]
                                                text = span["text"]

                                                # Find row index
                                                row_idx = -1
                                                for i in range(len(row_boundaries) - 1):
                                                    if (
                                                        row_boundaries[i]
                                                        <= y
                                                        < row_boundaries[i + 1]
                                                    ):
                                                        row_idx = i
                                                        break

                                                # Find column index
                                                col_idx = -1
                                                for i in range(len(col_boundaries) - 1):
                                                    if (
                                                        col_boundaries[i]
                                                        <= x
                                                        < col_boundaries[i + 1]
                                                    ):
                                                        col_idx = i
                                                        break

                                                # If we found a valid cell, add the text
                                                if row_idx >= 0 and col_idx >= 0:
                                                    # Ensure we have enough rows in table_data
                                                    while len(table_data) <= row_idx:
                                                        table_data.append(
                                                            [""]
                                                            * (len(col_boundaries) - 1)
                                                        )

                                                    # Ensure we have enough columns in this row
                                                    while (
                                                        len(table_data[row_idx])
                                                        <= col_idx
                                                    ):
                                                        table_data[row_idx].append("")

                                                    # Add text to the cell
                                                    table_data[row_idx][col_idx] += (
                                                        text + " "
                                                    )

                            # Clean up cell text
                            for row in table_data:
                                for i in range(len(row)):
                                    if i < len(row):  # Check to avoid index errors
                                        row[i] = row[i].strip()

                            # First row might be headers
                            if table_data and any(
                                cell.isupper() for cell in table_data[0] if cell
                            ):
                                headers = table_data[0]
                                table_data = table_data[1:]

                            # Only add if we have actual data
                            if table_data:
                                table_info = {
                                    "page": page_num + 1,
                                    "table_number": len(page_tables) + 1,
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
                                    "detection_method": "border_detection",
                                    "border_info": {
                                        "rows": table_border.get("rows", 0),
                                        "cols": table_border.get("cols", 0),
                                        "x0": table_border.get("x0", 0),
                                        "y0": table_border.get("y0", 0),
                                        "x1": table_border.get("x1", 0),
                                        "y1": table_border.get("y1", 0),
                                    },
                                }
                                page_tables.append(table_info)

                                # Enhanced logging for debugging
                                self.logger.debug(
                                    f"Table found: page={page_num + 1}, method=border_detection, "
                                    f"rows={len(table_data)}, cols={table_info['column_count']}, "
                                    f"headers={bool(headers)}"
                                )
                except Exception as border_error:
                    self.logger.warning(f"Border detection failed: {str(border_error)}")

                # STEP 2: Look for explicitly labeled tables if no tables found via borders
                if not page_tables:
                    try:
                        labeled_tables = self._extract_labeled_tables(page, page_num)
                        if labeled_tables:
                            self.logger.info(
                                f"Found {len(labeled_tables)} labeled tables on page {page_num + 1}"
                            )
                            page_tables.extend(labeled_tables)
                    except Exception as label_error:
                        self.logger.warning(
                            f"Labeled table extraction failed: {str(label_error)}"
                        )

                # STEP 3: Only if no tables found via borders or labels, try layout analysis with strict criteria
                if not page_tables:
                    try:
                        # Get blocks that might be tables
                        blocks = page.get_text("dict")["blocks"]

                        # Track how many potential tables we find
                        potential_tables = 0

                        # Identify potential table blocks based on multiple criteria
                        for block in blocks:
                            # Check if block has multiple lines (potential table)
                            if "lines" in block and len(block["lines"]) > 2:
                                # Additional checks for table-like structure with stricter criteria
                                is_table = self._is_likely_table(block)

                                if is_table:
                                    potential_tables += 1
                                    table_data, headers, column_count = (
                                        self._extract_table_data(block)
                                    )

                                    # Only add if we have actual data with at least 2 columns
                                    if table_data and column_count >= 2:
                                        # Add table with structure
                                        table_info = {
                                            "page": page_num + 1,
                                            "table_number": len(page_tables) + 1,
                                            "headers": headers,
                                            "data": table_data,
                                            "column_count": column_count,
                                            "row_count": len(table_data),
                                            "detection_method": "layout_analysis",
                                        }
                                        page_tables.append(table_info)

                                        # Enhanced logging for debugging
                                        self.logger.debug(
                                            f"Table found: page={page_num + 1}, method=layout_analysis, "
                                            f"rows={len(table_data)}, cols={column_count}, "
                                            f"headers={bool(headers)}"
                                        )

                        if potential_tables > 0:
                            self.logger.info(
                                f"Found {len(page_tables)} tables via layout analysis out of {potential_tables} potential tables on page {page_num + 1}"
                            )
                    except Exception as layout_error:
                        self.logger.warning(
                            f"Layout analysis failed: {str(layout_error)}"
                        )

                # STEP 4: Fallback to text-based table detection only if all other methods failed
                if not page_tables:
                    try:
                        text = page.get_text("text")

                        # Look for common table indicators
                        if any(
                            pattern in text for pattern in ["TABLE", "Table", "|", "+"]
                        ):
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
                                            cell.strip()
                                            for cell in cells
                                            if cell.strip()
                                        ]

                                        if not headers and any(
                                            cell.isupper() for cell in cells
                                        ):
                                            headers = cells
                                        else:
                                            data.append(cells)

                                # Add table with structure
                                if (
                                    data and len(data[0]) >= 2
                                ):  # Only add if we have data with at least 2 columns
                                    table_info = {
                                        "page": page_num + 1,
                                        "table_number": len(page_tables) + 1,
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
                                    page_tables.append(table_info)

                                    # Enhanced logging for debugging
                                    self.logger.debug(
                                        f"Table found: page={page_num + 1}, method=text_analysis, "
                                        f"rows={len(data)}, cols={table_info['column_count']}, "
                                        f"headers={bool(headers)}"
                                    )
                    except Exception as text_error:
                        self.logger.warning(
                            f"Text-based detection failed: {str(text_error)}"
                        )

                # Add all tables from this page
                tables.extend(page_tables)

                # Log summary for this page
                if page_tables:
                    self.logger.info(
                        f"Extracted {len(page_tables)} tables from page {page_num + 1}"
                    )
                else:
                    self.logger.info(f"No tables found on page {page_num + 1}")

        except Exception as e:
            self.logger.warning(f"Error during table extraction: {str(e)}")

        # Filter out small, irrelevant tables
        filtered_tables = self._filter_tables(tables)

        if len(filtered_tables) < len(tables):
            self.logger.info(
                f"Filtered out {len(tables) - len(filtered_tables)} small or irrelevant tables"
            )

        return filtered_tables

    def _filter_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out small or irrelevant tables.

        Args:
            tables: List of extracted tables

        Returns:
            Filtered list of tables
        """
        # Keep tables that have at least 2 rows and 2 columns
        filtered = []

        # Log all tables before filtering for debugging
        for i, table in enumerate(tables):
            self.logger.info(
                f"Table {i + 1} before filtering: page={table['page']}, "
                f"method={table.get('detection_method', 'unknown')}, "
                f"rows={table.get('row_count', 0)}, cols={table.get('column_count', 0)}, "
                f"has_label={('table_label' in table)}, label={table.get('table_label', 'none')}"
            )

        for table in tables:
            # Always keep tables with explicit labels regardless of other criteria
            if table["detection_method"] == "labeled_table" and "table_label" in table:
                self.logger.info(
                    f"Keeping labeled table on page {table['page']}: {table.get('table_label', 'unknown')}"
                )
                filtered.append(table)
                continue

            # Skip tables with insufficient data
            if table["row_count"] < 2 or table["column_count"] < 2:
                self.logger.info(
                    f"Filtering out small table on page {table['page']}: {table['row_count']} rows, {table['column_count']} columns"
                )
                continue

            # Skip tables with empty data
            if not table.get("data"):
                self.logger.info(f"Filtering out empty table on page {table['page']}")
                continue

            # For other tables, ensure they have meaningful content
            has_content = False
            for row in table.get("data", []):
                # Check if any cell has substantial content (more than just a few characters)
                if any(len(cell) > 5 for cell in row if cell):
                    has_content = True
                    break

            if has_content:
                filtered.append(table)
            else:
                self.logger.info(
                    f"Filtering out table with minimal content on page {table['page']}"
                )

        return filtered
