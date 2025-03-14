"""
PDF cleaner implementation.

This module provides functionality for cleaning and normalizing PDF content.
"""

import re
from typing import Any, Dict

from utils.pipeline.utils.logging import get_logger


class PDFCleaner:
    """Cleans and normalizes PDF content."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def clean(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize PDF content.

        Args:
            analysis_result: Analysis results from PDFAnalyzer

        Returns:
            Dictionary containing cleaned data
        """
        self.logger.info("Cleaning PDF content for: %s", analysis_result.get("path"))

        try:
            # Clean sections
            cleaned_sections = []
            for section in analysis_result.get("sections", []):
                cleaned_section = self._clean_section(section)
                if cleaned_section["content"].strip():  # Only keep non-empty sections
                    cleaned_sections.append(cleaned_section)

            # Clean metadata
            cleaned_metadata = self._clean_metadata(analysis_result.get("metadata", {}))

            # Clean page content
            cleaned_pages = []
            for page in analysis_result.get("pages", []):
                cleaned_page = self._clean_page(page)
                cleaned_pages.append(cleaned_page)

            return {
                "path": analysis_result.get("path"),
                "type": analysis_result.get("type"),
                "metadata": cleaned_metadata,
                "pages": cleaned_pages,
                "sections": cleaned_sections,
            }

        except Exception as e:
            self.logger.error("Failed to clean PDF content: %s", str(e), exc_info=True)
            return analysis_result  # Return original data on error

    def _clean_section(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a single section."""
        content = section.get("content", "")

        # Remove excessive whitespace
        content = re.sub(r"\s+", " ", content)
        content = re.sub(r"\n\s*\n", "\n\n", content)
        content = content.strip()

        # Clean up common OCR artifacts
        content = re.sub(
            r"[^\S\n]+", " ", content
        )  # Replace multiple spaces with single
        content = re.sub(r"(?<=[.!?])\s+", "\n", content)  # Line break after sentences
        content = re.sub(r"[^\x00-\x7F]+", "", content)  # Remove non-ASCII characters

        return {
            "title": section.get("title", "").strip(),
            "content": content,
            "level": section.get("level", 0),
        }

    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata fields."""
        cleaned = {}
        for key, value in metadata.items():
            if isinstance(value, str):
                # Remove non-printable characters and normalize whitespace
                value = "".join(char for char in value if char.isprintable())
                value = re.sub(r"\s+", " ", value).strip()
            cleaned[key] = value
        return cleaned

    def _clean_page(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Clean page content."""
        content = page.get("content", "")

        # Basic content cleaning
        content = re.sub(r"\s+", " ", content)  # Normalize whitespace
        content = re.sub(r"[^\x00-\x7F]+", "", content)  # Remove non-ASCII
        content = content.strip()

        return {
            "number": page.get("number"),
            "size": page.get("size"),
            "rotation": page.get("rotation", 0),
            "content": content,
        }
