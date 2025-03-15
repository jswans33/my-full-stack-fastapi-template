"""
PDF analyzer implementation.

This module provides functionality for analyzing PDF document structure.
"""

from typing import Any, Dict

import pypdf

from utils.pipeline.strategies.base import AnalyzerStrategy
from utils.pipeline.utils.logging import get_logger


class PDFAnalyzer(AnalyzerStrategy):
    """Analyzes PDF document structure and content."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def analyze(self, input_path: str) -> Dict[str, Any]:
        """
        Analyze PDF document structure.

        Args:
            input_path: Path to PDF file

        Returns:
            Dictionary containing analysis results
        """
        self.logger.info("Analyzing PDF: %s", input_path)

        try:
            with open(input_path, "rb") as f:
                pdf = pypdf.PdfReader(f)

                # Extract basic metadata
                metadata = {}
                if pdf.metadata:
                    metadata = {
                        "title": pdf.metadata.get("/Title", ""),
                        "author": pdf.metadata.get("/Author", ""),
                        "subject": pdf.metadata.get("/Subject", ""),
                        "creator": pdf.metadata.get("/Creator", ""),
                        "producer": pdf.metadata.get("/Producer", ""),
                        "creation_date": pdf.metadata.get("/CreationDate", ""),
                        "modification_date": pdf.metadata.get("/ModDate", ""),
                    }

                # Extract page information
                pages = []
                for i, page in enumerate(pdf.pages):
                    page_info = {
                        "number": i + 1,
                        "size": page.mediabox,
                        "rotation": page.get("/Rotate", 0),
                        "content": page.extract_text(),
                    }
                    pages.append(page_info)

                # Build sections from content
                sections = []
                current_section = None

                for page in pages:
                    content = page["content"]
                    lines = content.split("\n")

                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue

                        # Simple heuristic for section detection
                        if line.isupper() or line.startswith(
                            ("#", "Chapter", "Section")
                        ):
                            # New section
                            if current_section:
                                sections.append(current_section)
                            current_section = {
                                "title": line,
                                "content": "",
                                "level": 0 if line.isupper() else 1,
                            }
                        elif current_section:
                            current_section["content"] += line + "\n"
                        else:
                            # Text before first section
                            current_section = {
                                "title": "Introduction",
                                "content": line + "\n",
                                "level": 0,
                            }

                # Add last section
                if current_section:
                    sections.append(current_section)

                return {
                    "path": input_path,
                    "type": "pdf",
                    "metadata": metadata,
                    "pages": pages,
                    "sections": sections,
                }

        except Exception as e:
            self.logger.error("Failed to analyze PDF: %s", str(e), exc_info=True)
            # Return minimal structure for error case
            return {
                "path": input_path,
                "type": "pdf",
                "metadata": {},
                "sections": [
                    {
                        "title": "Error",
                        "content": f"Failed to analyze PDF: {str(e)}",
                        "level": 0,
                    }
                ],
            }
