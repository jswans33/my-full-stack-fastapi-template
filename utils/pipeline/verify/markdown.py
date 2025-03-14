"""
Markdown structure verifier.

This module provides verification for Markdown structure output.
"""

from typing import Any, Dict, List, Tuple

from utils.pipeline.verify.base import BaseVerifier


class MarkdownVerifier(BaseVerifier):
    """Verifies Markdown structure output."""

    def verify(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Verify Markdown structure and content.

        Args:
            data: Markdown data to verify

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        try:
            # Verify required top-level keys
            required_keys = {"document", "content", "validation"}
            self._verify_required_keys(data, required_keys, errors)

            # Verify document metadata
            if "document" in data:
                self._verify_document_metadata(data["document"], errors)

            # Verify content is a string
            if "content" in data:
                self._verify_content(data["content"], errors, warnings)

            # Verify tables format if present
            if "tables" in data:
                self._verify_tables(data["tables"], errors, warnings)

            is_valid = len(errors) == 0
            return is_valid, errors, warnings

        except Exception as e:
            errors.append(f"Verification failed: {str(e)}")
            return False, errors, warnings

    def _verify_required_keys(
        self, data: Dict[str, Any], required_keys: set, errors: List[str]
    ) -> None:
        """Verify all required keys are present."""
        missing_keys = required_keys - set(data.keys())
        if missing_keys:
            errors.append(f"Missing required keys: {', '.join(missing_keys)}")

    def _verify_document_metadata(
        self, document: Dict[str, Any], errors: List[str]
    ) -> None:
        """Verify document metadata structure."""
        required_metadata = {"metadata", "path", "type"}
        self._verify_required_keys(document, required_metadata, errors)

        metadata = document.get("metadata", {})
        if not isinstance(metadata, dict):
            errors.append("Document metadata must be a dictionary")

    def _verify_content(
        self, content: str, errors: List[str], warnings: List[str]
    ) -> None:
        """Verify markdown content structure."""
        if not isinstance(content, str):
            errors.append("Content must be a string")
            return

        # Check for basic markdown structure
        if not content.strip():
            warnings.append("Content is empty")
            return

        # Check for header hierarchy
        lines = content.split("\n")
        current_level = 0
        for line in lines:
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                if level > current_level + 1:
                    warnings.append(
                        f"Header level jump from {current_level} to {level}: {line.strip()}"
                    )
                current_level = level

    def _verify_tables(
        self, tables: str, errors: List[str], warnings: List[str]
    ) -> None:
        """Verify markdown tables structure."""
        if not isinstance(tables, str):
            errors.append("Tables must be a string")
            return

        if not tables.strip():
            return

        lines = tables.split("\n")
        in_table = False
        header_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                in_table = False
                continue

            if line.startswith("|"):
                if not in_table:
                    # New table started
                    in_table = True
                    header_count = line.count("|") - 1
                else:
                    # Check consistent column count
                    if line.count("|") - 1 != header_count:
                        errors.append(f"Inconsistent table column count: {line}")
