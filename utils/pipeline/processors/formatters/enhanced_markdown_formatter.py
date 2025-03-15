"""
Enhanced Markdown formatter implementation.

This module provides advanced functionality for formatting extracted PDF content into Markdown
with improved structure recognition, table handling, and formatting features.
"""

import re
from typing import Any, Dict, List, Optional

from utils.pipeline.processors.formatters.markdown_formatter import MarkdownFormatter
from utils.pipeline.utils.logging import get_logger


class EnhancedMarkdownFormatter(MarkdownFormatter):
    """
    Enhanced formatter for converting extracted PDF content into readable Markdown.

    Features:
    - Content segmentation (paragraphs, lists, code blocks, etc.)
    - Enhanced table formatting with support for complex tables
    - Inline formatting detection
    - Special element handling (notes, warnings, definitions, etc.)
    - Post-processing for improved readability
    - Markdown validation
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the enhanced markdown formatter.

        Args:
            config: Optional configuration dictionary
        """
        super().__init__()
        self.config = config or {}
        self.logger = get_logger(__name__)

    def format(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the analyzed data into a Markdown structure with enhanced features.

        Args:
            analyzed_data: Data from the PDF analyzer

        Returns:
            Formatted data structure with Markdown content
        """
        self.logger.info("Formatting PDF content as Markdown with enhanced features")

        try:
            # Build hierarchical structure
            content_tree = self._build_content_tree(analyzed_data.get("sections", []))

            # Convert content tree to markdown string with enhanced formatting
            content_markdown = ""
            for section in content_tree:
                content_markdown += self._format_section_to_markdown(section)

            # Convert tables to markdown string with enhanced table formatting
            tables_markdown = ""
            for table in analyzed_data.get("tables", []):
                tables_markdown += self._format_table_to_markdown(table)

            # Apply post-processing to improve overall formatting
            if self.config.get("post_processing", True):
                content_markdown = self._post_process_markdown(content_markdown)
                tables_markdown = self._post_process_markdown(tables_markdown)

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

            # Validate the markdown output
            if self.config.get("validation", True):
                validation_result = self._validate_markdown(
                    content_markdown + "\n\n" + tables_markdown
                )
                formatted_data["markdown_validation"] = validation_result

            return formatted_data

        except Exception as e:
            self.logger.error(f"Error formatting PDF content: {str(e)}", exc_info=True)
            raise

    def _build_content_tree(
        self, sections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Build an enhanced hierarchical tree structure from flat sections list.

        Args:
            sections: List of section dictionaries

        Returns:
            List of sections with hierarchical structure and enhanced metadata
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

            # Enhance section with additional metadata
            new_section = {
                "title": title,
                "content": content,
                "children": [],
                "level": level,
                "id": self._generate_section_id(title),  # For cross-references
                "has_lists": bool(
                    re.search(
                        r"^\s*(\d+\.|\d+\)|\-|\*|\•|\([a-zA-Z]\))",
                        content,
                        re.MULTILINE,
                    )
                ),
                "has_code": bool(re.search(r"^\s{4,}|\t", content, re.MULTILINE)),
                "has_tables": "table" in content.lower() or "|" in content,
            }

            # Add any additional metadata
            if "font" in section:
                new_section["font"] = section["font"]

            # Handle section nesting with improved logic
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

    def _generate_section_id(self, title: str) -> str:
        """
        Generate a unique ID for a section based on its title.
        Useful for cross-references.

        Args:
            title: Section title

        Returns:
            Section ID string
        """
        # Remove special characters and convert to lowercase
        section_id = re.sub(r"[^\w\s-]", "", title.lower())
        # Replace spaces with hyphens
        section_id = re.sub(r"\s+", "-", section_id)
        return section_id

    def _format_section_to_markdown(self, section: Dict[str, Any]) -> str:
        """
        Convert a section dictionary to markdown text with enhanced formatting.

        Args:
            section: Section dictionary with title, content, children, and level

        Returns:
            Markdown formatted string for the section
        """
        markdown_lines = []

        # Add section header with appropriate level and ID for cross-references
        if section.get("title"):
            level = section.get("level", 0)
            section_id = section.get("id", self._generate_section_id(section["title"]))

            # Use HTML anchor if enabled in config
            if self.config.get("html_anchors", True):
                markdown_lines.append(
                    f'{"#" * (level + 1)} {section["title"]} <a id="{section_id}"></a>\n'
                )
            else:
                markdown_lines.append(f"{'#' * (level + 1)} {section['title']}\n")

        # Process content with improved formatting
        if section.get("content"):
            # Segment content into structural elements if enabled
            if self.config.get("content_segmentation", True):
                segmented = self._segment_content(section["content"])

                # Format paragraphs
                for paragraph in segmented["paragraphs"]:
                    # Process inline formatting if enabled
                    if self.config.get("inline_formatting", True):
                        formatted_paragraph = self._process_inline_formatting(paragraph)
                    else:
                        formatted_paragraph = paragraph

                    markdown_lines.append(f"{formatted_paragraph}\n\n")

                # Format lists
                for list_info in segmented["lists"]:
                    list_type = list_info["type"]
                    for item in list_info["items"]:
                        if list_type == "numbered":
                            # Use consistent numbering for markdown
                            content = item["content"]
                            if self.config.get("inline_formatting", True):
                                content = self._process_inline_formatting(content)
                            markdown_lines.append(f"1. {content}\n")
                        else:
                            # Use asterisks for bullet lists
                            content = item["content"]
                            if self.config.get("inline_formatting", True):
                                content = self._process_inline_formatting(content)
                            markdown_lines.append(f"* {content}\n")
                    markdown_lines.append("\n")

                # Format code blocks
                for code_block in segmented["code_blocks"]:
                    markdown_lines.append("```\n" + code_block + "\n```\n\n")

                # Format blockquotes
                for blockquote in segmented["blockquotes"]:
                    lines = blockquote.split("\n")
                    for line in lines:
                        markdown_lines.append(f"> {line}\n")
                    markdown_lines.append("\n")

                # Format special elements
                for element in segmented["special_elements"]:
                    if element["type"] == "note":
                        markdown_lines.append(
                            self._format_note(element["note_type"], element["content"])
                        )
                    elif element["type"] == "definition":
                        markdown_lines.append(
                            self._format_definition(
                                element["term"], element["definition"]
                            )
                        )
                    elif element["type"] == "figure_caption":
                        markdown_lines.append(
                            self._format_figure_caption(
                                element["figure_number"], element["caption"]
                            )
                        )
            else:
                # Use simple formatting (original behavior)
                markdown_lines.append(f"{section['content']}\n")

        # Process children recursively
        for child in section.get("children", []):
            markdown_lines.append(self._format_section_to_markdown(child))

        return "\n".join(markdown_lines)

    def _segment_content(self, content: str) -> Dict[str, Any]:
        """
        Segment content into paragraphs, lists, and other elements.

        Args:
            content: Raw content string

        Returns:
            Dictionary with segmented content elements
        """
        segmented = {
            "paragraphs": [],
            "lists": [],
            "code_blocks": [],
            "blockquotes": [],
            "special_elements": [],
        }

        # Split content into lines for analysis
        lines = content.split("\n")

        # Initialize tracking variables
        current_paragraph = []
        current_list = []
        current_code_block = []
        current_blockquote = []

        # Track state
        in_list = False
        in_code_block = False
        in_blockquote = False
        list_type = None  # "numbered" or "bullet"

        # Process each line
        line_index = 0
        while line_index < len(lines):
            line = lines[line_index]
            stripped_line = line.strip()

            # Skip empty lines but handle them appropriately based on context
            if not stripped_line:
                # End current paragraph if we have one
                if current_paragraph:
                    segmented["paragraphs"].append(" ".join(current_paragraph))
                    current_paragraph = []

                # End current list if we have one
                if in_list and current_list:
                    segmented["lists"].append(
                        {"type": list_type, "items": current_list}
                    )
                    current_list = []
                    in_list = False

                # End current code block if we have one
                if in_code_block and current_code_block:
                    segmented["code_blocks"].append("\n".join(current_code_block))
                    current_code_block = []
                    in_code_block = False

                # End current blockquote if we have one
                if in_blockquote and current_blockquote:
                    segmented["blockquotes"].append("\n".join(current_blockquote))
                    current_blockquote = []
                    in_blockquote = False

                line_index += 1
                continue

            # Check for special elements
            special_element = self._identify_special_element(line, lines, line_index)
            if special_element:
                # End any current content
                if current_paragraph:
                    segmented["paragraphs"].append(" ".join(current_paragraph))
                    current_paragraph = []

                segmented["special_elements"].append(special_element)
                line_index += special_element.get("lines_consumed", 1)
                continue

            # Check for list items
            list_item = self._identify_list_item(line)
            if list_item:
                # End any non-list content
                if current_paragraph:
                    segmented["paragraphs"].append(" ".join(current_paragraph))
                    current_paragraph = []

                # Start a new list if needed
                if not in_list:
                    in_list = True
                    list_type = list_item["type"]

                # Add the list item
                current_list.append(list_item)
                line_index += 1
                continue

            # Check for code blocks
            if line.startswith("    ") or line.startswith("\t"):
                # This might be a code block
                if not in_code_block:
                    in_code_block = True

                # End any non-code content
                if current_paragraph:
                    segmented["paragraphs"].append(" ".join(current_paragraph))
                    current_paragraph = []

                # Add to code block
                current_code_block.append(line.lstrip())
                line_index += 1
                continue

            # Check for blockquotes
            if line.startswith(">"):
                # This is a blockquote
                if not in_blockquote:
                    in_blockquote = True

                # End any non-blockquote content
                if current_paragraph:
                    segmented["paragraphs"].append(" ".join(current_paragraph))
                    current_paragraph = []

                # Add to blockquote
                current_blockquote.append(line[1:].strip())
                line_index += 1
                continue

            # Regular paragraph text

            # End any special content
            if in_list and current_list:
                segmented["lists"].append({"type": list_type, "items": current_list})
                current_list = []
                in_list = False

            if in_code_block and current_code_block:
                segmented["code_blocks"].append("\n".join(current_code_block))
                current_code_block = []
                in_code_block = False

            if in_blockquote and current_blockquote:
                segmented["blockquotes"].append("\n".join(current_blockquote))
                current_blockquote = []
                in_blockquote = False

            # Add to paragraph
            current_paragraph.append(stripped_line)
            line_index += 1

        # Handle any remaining content
        if current_paragraph:
            segmented["paragraphs"].append(" ".join(current_paragraph))

        if in_list and current_list:
            segmented["lists"].append({"type": list_type, "items": current_list})

        if in_code_block and current_code_block:
            segmented["code_blocks"].append("\n".join(current_code_block))

        if in_blockquote and current_blockquote:
            segmented["blockquotes"].append("\n".join(current_blockquote))

        return segmented

    def _identify_special_element(
        self, line: str, lines: List[str], line_index: int
    ) -> Optional[Dict[str, Any]]:
        """
        Identify special elements in text lines.

        Args:
            line: Current line
            lines: All lines
            line_index: Index of current line

        Returns:
            Dictionary with special element information or None
        """
        # Check for section references (e.g., "See Section 3.2")
        section_ref_match = re.search(r"(See|refer to)\s+[Ss]ection\s+(\d+\.\d+)", line)
        if section_ref_match:
            return {
                "type": "section_reference",
                "section": section_ref_match.group(2),
                "content": line,
                "lines_consumed": 1,
            }

        # Check for figure references (e.g., "Figure 2: System Diagram")
        figure_match = re.match(r"^(Figure|Fig\.)\s+(\d+)[\:\.]?\s+(.+)$", line)
        if figure_match:
            return {
                "type": "figure_caption",
                "figure_number": figure_match.group(2),
                "caption": figure_match.group(3),
                "content": line,
                "lines_consumed": 1,
            }

        # Check for note/warning blocks
        note_match = re.match(
            r"^(NOTE|CAUTION|WARNING)\s*[\:\-]?\s*(.+)$", line, re.IGNORECASE
        )
        if note_match:
            note_type = note_match.group(1).lower()
            content = note_match.group(2)

            # Check if note continues on next lines
            lines_consumed = 1
            next_line_index = line_index + 1
            while (
                next_line_index < len(lines)
                and lines[next_line_index].strip()
                and not re.match(
                    r"^(NOTE|CAUTION|WARNING)\s*[\:\-]",
                    lines[next_line_index],
                    re.IGNORECASE,
                )
            ):
                content += " " + lines[next_line_index].strip()
                lines_consumed += 1
                next_line_index += 1

            return {
                "type": "note",
                "note_type": note_type,
                "content": content,
                "lines_consumed": lines_consumed,
            }

        # Check for definition terms
        definition_match = re.match(r"^([A-Z][A-Za-z\s]+)[\:\-]\s+(.+)$", line)
        if (
            definition_match and len(definition_match.group(1)) < 40
        ):  # Avoid false positives
            return {
                "type": "definition",
                "term": definition_match.group(1).strip(),
                "definition": definition_match.group(2),
                "content": line,
                "lines_consumed": 1,
            }

        return None

    def _identify_list_item(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Identify if a line is a list item.

        Args:
            line: Line to check

        Returns:
            Dictionary with list item information or None
        """
        # Check for numbered list items
        numbered_match = re.match(r"^\s*(\d+\.|\d+\))\s+(.+)$", line)
        if numbered_match:
            return {
                "type": "numbered",
                "marker": numbered_match.group(1),
                "content": numbered_match.group(2),
            }

        # Check for bullet list items
        bullet_match = re.match(r"^\s*([\-\*\•]|\([a-zA-Z]\))\s+(.+)$", line)
        if bullet_match:
            return {
                "type": "bullet",
                "marker": bullet_match.group(1),
                "content": bullet_match.group(2),
            }

        return None

    def _process_inline_formatting(self, text: str) -> str:
        """
        Process inline formatting like bold, italic, etc.

        Args:
            text: Text to process

        Returns:
            Text with markdown inline formatting
        """
        # Bold text (often indicated by ALL CAPS in technical docs)
        text = re.sub(r"\b([A-Z]{2,})\b", r"**\1**", text)

        # Italic for emphasized terms
        text = re.sub(r"_([^_]+)_", r"*\1*", text)

        # Code for technical terms
        text = re.sub(r"`([^`]+)`", r"`\1`", text)

        # Handle URLs
        text = re.sub(r"(https?://[^\s]+)", r"[\1](\1)", text)

        return text

    def _format_note(self, note_type: str, content: str) -> str:
        """
        Format notes, cautions, and warnings.

        Args:
            note_type: Type of note (note, caution, warning)
            content: Note content

        Returns:
            Formatted note string
        """
        if note_type.lower() == "note":
            return f"> **Note:** {content}\n\n"
        elif note_type.lower() == "caution":
            return f"> ⚠️ **Caution:** {content}\n\n"
        elif note_type.lower() == "warning":
            return f"> ⚠️ **WARNING:** {content}\n\n"
        else:
            return f"> **{note_type}:** {content}\n\n"

    def _format_definition(self, term: str, definition: str) -> str:
        """
        Format a definition term and its definition.

        Args:
            term: Term being defined
            definition: Definition text

        Returns:
            Formatted definition string
        """
        return f"**{term}**: {definition}\n\n"

    def _format_figure_caption(self, figure_number: str, caption: str) -> str:
        """
        Format figure captions.

        Args:
            figure_number: Figure number
            caption: Caption text

        Returns:
            Formatted figure caption string
        """
        return f"**Figure {figure_number}:** {caption}\n\n"

    def _format_table_to_markdown(self, table: Dict[str, Any]) -> str:
        """
        Format a table dictionary to markdown, choosing the appropriate format.

        Args:
            table: Table dictionary with headers and data

        Returns:
            Markdown formatted table string
        """
        # Check if enhanced tables are enabled
        if not self.config.get("enhanced_tables", True):
            # Use original simple table formatting
            return super()._format_table_to_markdown(table)

        # Check if this is a complex table that needs HTML formatting
        is_complex = False

        # Case 1: Table has merged cells
        if "merged_cells" in table and table["merged_cells"]:
            is_complex = True

        # Case 2: Table was detected using border detection (might have complex structure)
        if (
            table.get("detection_method") == "border_detection"
            and "border_info" in table
        ):
            # Check if the grid structure suggests merged cells
            border_info = table["border_info"]
            if (
                border_info.get("rows", 0) > 0
                and border_info.get("cols", 0) > 0
                and len(table.get("data", [])) != border_info["rows"]
            ):
                is_complex = True

        # Case 3: Inconsistent row lengths
        row_lengths = [len(row) for row in table.get("data", [])]
        if row_lengths and max(row_lengths) != min(row_lengths):
            is_complex = True

        # Use HTML format for complex tables if enabled
        if is_complex and self.config.get("html_for_complex_tables", True):
            return self._format_complex_table_to_markdown(table)

        # Use standard markdown for simple tables
        return self._format_simple_table_to_markdown(table)

    def _format_simple_table_to_markdown(self, table: Dict[str, Any]) -> str:
        """
        Format a simple table to markdown.

        Args:
            table: Table dictionary with headers and data

        Returns:
            Markdown formatted table string
        """
        markdown_lines = []

        if "headers" in table and "data" in table:
            # Get headers
            headers = table["headers"]

            # Ensure we have headers
            if not headers and table["data"]:
                # Generate generic headers if none exist
                headers = [f"Column {i + 1}" for i in range(table["column_count"])]

            if headers:
                markdown_lines.append("| " + " | ".join(headers) + " |")

                # Add separator row with alignment
                separators = []
                for header in headers:
                    # Check if column contains numeric data for right alignment
                    is_numeric = self._is_numeric_column(header, table["data"])
                    if is_numeric:
                        separators.append("---:")  # Right-aligned
                    else:
                        separators.append("---")  # Left-aligned

                markdown_lines.append("| " + " | ".join(separators) + " |")

                # Add table data with proper formatting
                for row in table["data"]:
                    # Ensure row has enough cells
                    while len(row) < len(headers):
                        row.append("")

                    # Format cells
                    formatted_cells = []
                    for i, cell in enumerate(row):
                        # Clean and format cell content
                        cell_text = str(cell).replace(
                            "|", "\\|"
                        )  # Escape pipe characters
                        formatted_cells.append(cell_text)

                    markdown_lines.append("| " + " | ".join(formatted_cells) + " |")

                markdown_lines.append("")  # Add empty line after table

        return "\n".join(markdown_lines)

    def _format_complex_table_to_markdown(self, table: Dict[str, Any]) -> str:
        """
        Format complex tables with merged cells using HTML for better representation.

        Args:
            table: Table dictionary with headers and data

        Returns:
            HTML table formatted as markdown string
        """
        markdown_lines = []

        # Extract merged cells information
        merged_cells = table.get("merged_cells", [])

        # Create a grid to track which cells are part of merged cells
        rows = table.get("row_count", 0)
        cols = table.get("column_count", 0)
        grid = []
        for _ in range(rows):
            grid.append([None for _ in range(cols)])

        # Mark merged cells in the grid
        for cell in merged_cells:
            for r in range(cell["start_row"], cell["end_row"] + 1):
                for c in range(cell["start_col"], cell["end_col"] + 1):
                    if r == cell["start_row"] and c == cell["start_col"]:
                        # This is the top-left cell of the merged area
                        cell_info = {
                            "rowspan": cell["rowspan"],
                            "colspan": cell["colspan"],
                            "is_main": True,
                        }
                        grid[r][c] = cell_info
                    else:
                        # This cell is part of a merged area but not the main cell
                        cell_info = {
                            "is_main": False,
                            "main_row": cell["start_row"],
                            "main_col": cell["start_col"],
                        }
                        grid[r][c] = cell_info

        # Start HTML table
        markdown_lines.append("<table>")

        # Add table headers
        headers = table.get("headers", [])
        if headers:
            markdown_lines.append("  <thead>")
            markdown_lines.append("    <tr>")

            for col, header in enumerate(headers):
                # Check if this header cell is part of a merged cell
                cell_info = grid[0][col] if col < len(grid[0]) else None

                if cell_info and cell_info["is_main"]:
                    # This is the main cell of a merged area
                    markdown_lines.append(
                        f'      <th rowspan="{cell_info["rowspan"]}" colspan="{cell_info["colspan"]}">{header}</th>'
                    )
                elif not cell_info or cell_info["is_main"] is None:
                    # Regular cell
                    markdown_lines.append(f"      <th>{header}</th>")
                # Skip cells that are part of a merged area but not the main cell

            markdown_lines.append("    </tr>")
            markdown_lines.append("  </thead>")

        # Add table body
        markdown_lines.append("  <tbody>")

        # Process data rows
        data = table.get("data", [])
        for row_idx, row in enumerate(data):
            markdown_lines.append("    <tr>")

            for col_idx, cell in enumerate(row):
                # Skip header row if we already processed it
                if headers and row_idx == 0:
                    continue

                # Adjust for header row
                actual_row = row_idx if not headers else row_idx + 1

                # Check if this cell is part of a merged cell
                cell_info = (
                    grid[actual_row][col_idx]
                    if actual_row < len(grid) and col_idx < len(grid[actual_row])
                    else None
                )

                if cell_info and cell_info["is_main"]:
                    # This is the main cell of a merged area
                    markdown_lines.append(
                        f'      <td rowspan="{cell_info["rowspan"]}" colspan="{cell_info["colspan"]}">{cell}</td>'
                    )
                elif not cell_info or cell_info["is_main"] is None:
                    # Regular cell
                    markdown_lines.append(f"      <td>{cell}</td>")
                # Skip cells that are part of a merged area but not the main cell

            markdown_lines.append("    </tr>")

        markdown_lines.append("  </tbody>")
        markdown_lines.append("</table>")

        # Add simplified table as a comment for viewers that don't support HTML
        if self.config.get("add_simplified_fallback", True):
            simplified = self._add_simplified_table_fallback(table)
            markdown_lines.insert(0, simplified)

        return "\n".join(markdown_lines)

    def _add_simplified_table_fallback(self, table: Dict[str, Any]) -> str:
        """
        Add a simplified markdown table as a comment for viewers that don't support HTML.

        Args:
            table: Table dictionary with headers and data

        Returns:
            Markdown comment with simplified table
        """
        # Create a simplified version of the table
        simplified = ["<!-- Simplified table for basic markdown viewers:"]
        simplified.append("")

        # Add headers
        headers = table.get("headers", [])
        if headers:
            simplified.append("| " + " | ".join(headers) + " |")
            simplified.append("| " + " | ".join(["---"] * len(headers)) + " |")

        # Add data rows
        for row in table.get("data", []):
            # Ensure row has enough cells
            while len(row) < len(headers):
                row.append("")
            simplified.append("| " + " | ".join(str(cell) for cell in row) + " |")

        simplified.append("")
        simplified.append("-->")

        return "\n".join(simplified)

    def _is_numeric_column(self, header: str, data: List[List[str]]) -> bool:
        """
        Determine if a column contains primarily numeric data.

        Args:
            header: Column header
            data: Table data

        Returns:
            True if column is primarily numeric, False otherwise
        """
        # Find the column index
        headers = [header]
        numeric_count = 0
        total_count = 0

        # Check each row for numeric values in this column
        for row in data:
            if not row:
                continue

            # Find the column index
            col_idx = 0

            # Check if cell is numeric
            if col_idx < len(row):
                cell = row[col_idx]
                if re.match(r"^\s*-?\d+(\.\d+)?\s*$", str(cell)):
                    numeric_count += 1
                total_count += 1

        # Consider numeric if more than 70% of cells are numeric
        return total_count > 0 and numeric_count / total_count > 0.7

    def _post_process_markdown(self, markdown: str) -> str:
        """
        Post-process markdown to improve formatting and readability.

        Args:
            markdown: Raw markdown string

        Returns:
            Improved markdown string
        """
        # Fix consecutive blank lines (more than 2)
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)

        # Fix list formatting
        list_pattern = r"(\n\s*[-*]\s+[^\n]+)(\n\s*[-*]\s+[^\n]+)+"
        for match in re.finditer(list_pattern, markdown):
            list_text = match.group(0)
            # Ensure proper spacing around lists
            if not list_text.startswith("\n\n"):
                markdown = markdown.replace(list_text, f"\n\n{list_text}")
            if not list_text.endswith("\n\n"):
                markdown = markdown.replace(list_text, f"{list_text}\n\n")

        # Fix table formatting
        table_pattern = r"(\n\|[^\n]+\|)(\n\|[^\n]+\|)+"
        for match in re.finditer(table_pattern, markdown):
            table_text = match.group(0)
            # Ensure proper spacing around tables
            if not table_text.startswith("\n\n"):
                markdown = markdown.replace(table_text, f"\n\n{table_text}")
            if not table_text.endswith("\n\n"):
                markdown = markdown.replace(table_text, f"{table_text}\n\n")

        # Fix heading spacing
        heading_pattern = r"(\n#{1,6}\s+[^\n]+)"
        for match in re.finditer(heading_pattern, markdown):
            heading_text = match.group(0)
            # Ensure proper spacing around headings
            if not heading_text.startswith("\n\n") and not heading_text.startswith(
                "\n\n\n"
            ):
                markdown = markdown.replace(heading_text, f"\n\n{heading_text}")

        # Fix code block spacing
        code_pattern = r"(\n```[^\n]*\n[^`]*\n```)"
        for match in re.finditer(code_pattern, markdown):
            code_text = match.group(0)
            # Ensure proper spacing around code blocks
            if not code_text.startswith("\n\n"):
                markdown = markdown.replace(code_text, f"\n\n{code_text}")
            if not code_text.endswith("\n\n"):
                markdown = markdown.replace(code_text, f"{code_text}\n\n")

        # Fix HTML table spacing
        html_table_pattern = r"(\n<table>.*?</table>)"
        for match in re.finditer(html_table_pattern, markdown, re.DOTALL):
            table_text = match.group(0)
            # Ensure proper spacing around HTML tables
            if not table_text.startswith("\n\n"):
                markdown = markdown.replace(table_text, f"\n\n{table_text}")
            if not table_text.endswith("\n\n"):
                markdown = markdown.replace(table_text, f"{table_text}\n\n")

        return markdown

    def _validate_markdown(self, markdown: str) -> Dict[str, Any]:
        """
        Validate markdown output and report issues.

        Args:
            markdown: Markdown string to validate

        Returns:
            Validation results dictionary
        """
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "stats": {
                "headings": 0,
                "paragraphs": 0,
                "lists": 0,
                "tables": 0,
                "code_blocks": 0,
                "blockquotes": 0,
            },
        }

        # Check for common markdown issues

        # 1. Check for broken links
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        for match in re.finditer(link_pattern, markdown):
            link_text, link_url = match.groups()
            if not link_url or link_url.isspace():
                validation["warnings"].append(f"Empty link URL for text: '{link_text}'")

        # 2. Check for malformed tables
        table_lines = []
        in_table = False
        for line in markdown.split("\n"):
            if line.startswith("|") and not in_table:
                in_table = True
                table_lines = [line]
                validation["stats"]["tables"] += 1
            elif line.startswith("|") and in_table:
                table_lines.append(line)
            elif not line.startswith("|") and in_table:
                in_table = False
                # Validate the table
                if len(table_lines) < 3:
                    validation["warnings"].append(
                        "Table has fewer than 3 rows (header, separator, data)"
                    )
                else:
                    # Check if all rows have the same number of columns
                    col_counts = [line.count("|") - 1 for line in table_lines]
                    if len(set(col_counts)) > 1:
                        validation["warnings"].append(
                            "Table has inconsistent column counts"
                        )

        # 3. Check for heading hierarchy
        heading_levels = []
        for line in markdown.split("\n"):
            if line.startswith("#"):
                heading_match = re.match(r"^(#+)", line)
                if heading_match:
                    level = len(heading_match.group(1))
                    heading_levels.append(level)
                    validation["stats"]["headings"] += 1

        # Check if heading levels increase by more than one
        for i in range(1, len(heading_levels)):
            if heading_levels[i] > heading_levels[i - 1] + 1:
                validation["warnings"].append(
                    f"Heading level jumps from {heading_levels[i - 1]} to {heading_levels[i]}"
                )

        # 4. Count other elements
        for line in markdown.split("\n"):
            if line.strip() and not line.startswith("#") and not line.startswith("|"):
                if line.startswith("```"):
                    validation["stats"]["code_blocks"] += 1
                elif line.startswith(">"):
                    validation["stats"]["blockquotes"] += 1
                elif (
                    line.startswith("*")
                    or line.startswith("-")
                    or re.match(r"^\d+\.", line)
                ):
                    validation["stats"]["lists"] += 1
                elif line.strip():
                    validation["stats"]["paragraphs"] += 1

        # Set validity based on errors
        if validation["errors"]:
            validation["is_valid"] = False

        return validation

    def write(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Write formatted data to a Markdown file with enhanced features.

        Args:
            data: Formatted data to write
            output_path: Path to output file
        """
        try:
            # Generate markdown content
            markdown_content = ""

            # Write document metadata
            doc = data.get("document", {})
            markdown_content += "# Document Information\n\n"
            markdown_content += f"- Path: {doc.get('path', '')}\n"
            markdown_content += f"- Type: {doc.get('type', '')}\n\n"

            # Write metadata
            metadata = doc.get("metadata", {})
            if metadata:
                markdown_content += "## Metadata\n\n"
                for key, value in metadata.items():
                    markdown_content += f"- {key}: {value}\n"
                markdown_content += "\n"

            # Write content
            content = data.get("content", "")
            if content:
                markdown_content += "# Content\n\n"
                markdown_content += content
                markdown_content += "\n"

            # Write tables
            tables = data.get("tables", "")
            if tables:
                markdown_content += "# Tables\n\n"
                markdown_content += tables
                markdown_content += "\n"

            # Write summary
            summary = data.get("summary", {})
            if summary:
                markdown_content += "# Summary\n\n"
                for key, value in summary.items():
                    markdown_content += f"## {key}\n\n{value}\n\n"

            # Write classification if present
            classification = data.get("classification", {})
            if classification:
                markdown_content += "# Classification\n\n"
                markdown_content += f"- Document Type: {classification.get('document_type', 'Unknown')}\n"
                markdown_content += (
                    f"- Confidence: {classification.get('confidence', 0.0):.2f}\n"
                )
                markdown_content += f"- Schema Pattern: {classification.get('schema_pattern', 'Unknown')}\n"

                key_features = classification.get("key_features", [])
                if key_features:
                    markdown_content += "- Key Features:\n"
                    for feature in key_features:
                        markdown_content += f"  - {feature}\n"
                markdown_content += "\n"

            # Apply post-processing if enabled
            if self.config.get("post_processing", True):
                markdown_content = self._post_process_markdown(markdown_content)

            # Validate markdown if enabled
            if self.config.get("validation", True):
                validation = self._validate_markdown(markdown_content)

                # Log validation results
                if validation["warnings"]:
                    self.logger.warning(
                        f"Markdown validation warnings: {validation['warnings']}"
                    )
                if validation["errors"]:
                    self.logger.error(
                        f"Markdown validation errors: {validation['errors']}"
                    )

                # Add validation report as a comment at the end of the file
                if self.config.get("include_validation_report", False):
                    markdown_content += "\n\n<!-- Markdown Validation Report\n"
                    markdown_content += f"Valid: {validation['is_valid']}\n"
                    if validation["warnings"]:
                        markdown_content += "Warnings:\n"
                        for warning in validation["warnings"]:
                            markdown_content += f"- {warning}\n"
                    if validation["errors"]:
                        markdown_content += "Errors:\n"
                        for error in validation["errors"]:
                            markdown_content += f"- {error}\n"
                    markdown_content += "Stats:\n"
                    for key, value in validation["stats"].items():
                        markdown_content += f"- {key}: {value}\n"
                    markdown_content += "-->\n"

            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            self.logger.info(f"Successfully wrote enhanced markdown to {output_path}")

        except Exception as e:
            self.logger.error(f"Error writing markdown file: {str(e)}", exc_info=True)
            raise
