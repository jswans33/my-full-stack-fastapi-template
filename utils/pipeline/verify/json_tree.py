"""
JSON tree structure verifier.

This module provides verification for JSON tree structure output.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from utils.pipeline.verify.base import BaseVerifier


class JSONTreeVerifier(BaseVerifier):
    """Verifies JSON tree structure output."""

    def verify(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Verify JSON tree structure and content.

        Args:
            data: JSON data to verify

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        try:
            # Verify required top-level keys
            required_keys = {"document", "content", "validation"}
            self._verify_required_keys(data, required_keys, "root", errors)

            # Verify document metadata
            if "document" in data:
                self._verify_document_metadata(data["document"], errors, warnings)

            # Verify content structure
            if "content" in data:
                self._verify_content_structure(data["content"], errors, warnings)

            # Check for circular references
            if "content" in data:
                self._check_circular_references(data["content"], errors)

            is_valid = len(errors) == 0
            return is_valid, errors, warnings

        except Exception as e:
            errors.append(f"Verification failed: {str(e)}")
            return False, errors, warnings

    def _verify_required_keys(
        self,
        data: Dict[str, Any],
        required_keys: Set[str],
        context: str,
        errors: List[str],
    ) -> None:
        """Verify all required keys are present."""
        missing_keys = required_keys - set(data.keys())
        if missing_keys:
            errors.append(
                f"Missing required keys in {context}: {', '.join(missing_keys)}"
            )

    def _verify_document_metadata(
        self, document: Dict[str, Any], errors: List[str], warnings: List[str]
    ) -> None:
        """Verify document metadata structure."""
        required_metadata = {"metadata", "path", "type"}
        self._verify_required_keys(document, required_metadata, "document", errors)

        metadata = document.get("metadata", {})
        if not isinstance(metadata, dict):
            errors.append("Document metadata must be a dictionary")

    def _verify_content_structure(
        self,
        content: List[Dict[str, Any]],
        errors: List[str],
        warnings: List[str],
        parent_level: Optional[int] = None,
    ) -> None:
        """Verify content structure recursively."""
        if not isinstance(content, list):
            errors.append("Content must be a list of sections")
            return

        for section in content:
            if not isinstance(section, dict):
                errors.append("Each section must be a dictionary")
                continue

            # Check required section keys
            required_keys = {"title", "content", "children", "level"}
            self._verify_required_keys(section, required_keys, "section", errors)

            # Verify level is valid
            level = section.get("level")
            if not isinstance(level, int) or level < 0:
                errors.append(
                    f"Invalid level {level} for section '{section.get('title')}'"
                )
                continue

            # Verify level is consistent with parent
            if parent_level is not None and isinstance(level, int):
                if level <= parent_level:
                    warnings.append(
                        f"Section '{section.get('title')}' level {level} is not greater than parent level {parent_level}"
                    )

            # Verify children recursively
            children = section.get("children", [])
            if children:
                self._verify_content_structure(children, errors, warnings, level)

    def _check_circular_references(
        self,
        content: List[Dict[str, Any]],
        errors: List[str],
        visited: Optional[Set[int]] = None,
    ) -> None:
        """Check for circular references in content structure."""
        if visited is None:
            visited = set()

        for section in content:
            section_id = id(section)
            if section_id in visited:
                errors.append(
                    f"Circular reference detected in section '{section.get('title')}'"
                )
                continue

            visited.add(section_id)
            children = section.get("children", [])
            if children:
                self._check_circular_references(children, errors, visited)
            visited.remove(section_id)
