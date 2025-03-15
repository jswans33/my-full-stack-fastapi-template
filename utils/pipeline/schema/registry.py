"""
Schema registry module.

This module provides functionality for managing document schemas.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from utils.pipeline.utils.logging import get_logger


class SchemaRegistry:
    """
    Registry for document schemas.

    This class provides functionality for:
    1. Storing known document schemas
    2. Matching new documents against known schemas
    3. Recording new schemas
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the schema registry.

        Args:
            config: Configuration dictionary for the registry
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Set up registry storage
        self.storage_dir = self._get_storage_dir()
        self._ensure_storage_dir()

        # Load existing schemas
        self.schemas = self._load_schemas()

    def record(self, document_data: Dict[str, Any], document_type: str) -> bool:
        """
        Record a document schema in the registry.

        Args:
            document_data: Document data to record
            document_type: Type of the document

        Returns:
            True if schema was recorded successfully, False otherwise
        """
        try:
            # Extract schema from document data
            schema = self._extract_schema(document_data)

            # Add metadata
            schema["document_type"] = document_type
            schema["recorded_at"] = datetime.now().isoformat()

            # Generate schema ID
            schema_id = self._generate_schema_id(document_type)

            # Save schema to storage
            self._save_schema(schema_id, schema)

            # Update in-memory schemas
            self.schemas[schema_id] = schema

            self.logger.info(
                f"Recorded schema {schema_id} for document type {document_type}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error recording schema: {str(e)}", exc_info=True)
            return False

    def match(self, document_data: Dict[str, Any]) -> Tuple[Optional[str], float]:
        """
        Match a document against known schemas.

        Args:
            document_data: Document data to match

        Returns:
            Tuple of (schema_id, confidence) for the best matching schema
        """
        if not self.schemas:
            return None, 0.0

        # Extract schema from document data
        schema = self._extract_schema(document_data)

        # Find best matching schema
        best_match = None
        best_confidence = 0.0

        for schema_id, known_schema in self.schemas.items():
            confidence = self._calculate_match_confidence(schema, known_schema)
            if confidence > best_confidence:
                best_match = schema_id
                best_confidence = confidence

        return best_match, best_confidence

    def get_schema(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a schema by ID.

        Args:
            schema_id: ID of the schema to get

        Returns:
            Schema dictionary or None if not found
        """
        return self.schemas.get(schema_id)

    def list_schemas(self, document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all schemas or schemas of a specific type.

        Args:
            document_type: Optional document type to filter by

        Returns:
            List of schema dictionaries
        """
        if document_type:
            return [
                {"id": schema_id, **schema}
                for schema_id, schema in self.schemas.items()
                if schema.get("document_type") == document_type
            ]

        return [
            {"id": schema_id, **schema} for schema_id, schema in self.schemas.items()
        ]

    def _get_storage_dir(self) -> Path:
        """Get the storage directory for schemas."""
        # Use configured directory if available
        if "storage_dir" in self.config:
            return Path(self.config["storage_dir"])

        # Default to package directory
        return Path(__file__).parent / "data" / "schemas"

    def _ensure_storage_dir(self) -> None:
        """Ensure the storage directory exists."""
        os.makedirs(self.storage_dir, exist_ok=True)

    def _load_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load existing schemas from storage."""
        schemas = {}

        try:
            # Load all JSON files in the storage directory
            for file_path in self.storage_dir.glob("*.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        schema = json.load(f)
                        schema_id = file_path.stem
                        schemas[schema_id] = schema
                except Exception as e:
                    self.logger.warning(f"Error loading schema {file_path}: {str(e)}")

            self.logger.info(f"Loaded {len(schemas)} schemas from storage")

        except Exception as e:
            self.logger.error(f"Error loading schemas: {str(e)}", exc_info=True)

        return schemas

    def _save_schema(self, schema_id: str, schema: Dict[str, Any]) -> None:
        """
        Save a schema to storage.

        Args:
            schema_id: ID of the schema
            schema: Schema dictionary
        """
        file_path = self.storage_dir / f"{schema_id}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

    def _extract_schema(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract schema from document data.

        Args:
            document_data: Document data to extract schema from

        Returns:
            Schema dictionary
        """
        # Extract metadata
        metadata = document_data.get("metadata", {})

        # Extract content structure
        content = document_data.get("content", [])
        content_structure = self._extract_content_structure(content)

        # Extract table structure
        tables = document_data.get("tables", [])
        table_structure = self._extract_table_structure(tables)

        # Build schema
        schema = {
            "metadata_fields": list(metadata.keys()),
            "content_structure": content_structure,
            "table_structure": table_structure,
            "section_count": len(content),
            "table_count": len(tables),
        }

        return schema

    def _extract_content_structure(
        self, content: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract structure from content sections.

        Args:
            content: List of content sections

        Returns:
            List of section structures
        """
        structure = []

        for section in content:
            # Extract basic section structure
            section_structure = {
                "level": section.get("level", 0),
                "has_title": bool(section.get("title")),
                "has_content": bool(section.get("content")),
                "has_children": bool(section.get("children")),
                "child_count": len(section.get("children", [])),
            }

            # Add to structure
            structure.append(section_structure)

            # Process children recursively
            if section.get("children"):
                child_structure = self._extract_content_structure(section["children"])
                section_structure["children"] = child_structure

        return structure

    def _extract_table_structure(
        self, tables: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract structure from tables.

        Args:
            tables: List of tables

        Returns:
            List of table structures
        """
        structure = []

        for table in tables:
            # Extract basic table structure
            table_structure = {
                "has_headers": "headers" in table,
                "header_count": len(table.get("headers", [])),
                "row_count": len(table.get("data", [])),
            }

            # Add to structure
            structure.append(table_structure)

        return structure

    def _generate_schema_id(self, document_type: str) -> str:
        """
        Generate a unique schema ID.

        Args:
            document_type: Type of the document

        Returns:
            Unique schema ID
        """
        # Use timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Clean document type for use in filename
        clean_type = document_type.lower().replace(" ", "_")

        return f"{clean_type}_{timestamp}"

    def _calculate_match_confidence(
        self, schema1: Dict[str, Any], schema2: Dict[str, Any]
    ) -> float:
        """
        Calculate match confidence between two schemas.

        Args:
            schema1: First schema
            schema2: Second schema

        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0
        total_weight = 0.0

        # Compare metadata fields (weight: 0.2)
        weight = 0.2
        total_weight += weight

        metadata1 = set(schema1.get("metadata_fields", []))
        metadata2 = set(schema2.get("metadata_fields", []))

        if metadata1 and metadata2:
            common = len(metadata1.intersection(metadata2))
            total = len(metadata1.union(metadata2))
            score += weight * (common / total if total > 0 else 0.0)

        # Compare section counts (weight: 0.3)
        weight = 0.3
        total_weight += weight

        section_count1 = schema1.get("section_count", 0)
        section_count2 = schema2.get("section_count", 0)

        if section_count1 > 0 and section_count2 > 0:
            # Calculate similarity based on ratio
            ratio = min(section_count1, section_count2) / max(
                section_count1, section_count2
            )
            score += weight * ratio

        # Compare table counts (weight: 0.2)
        weight = 0.2
        total_weight += weight

        table_count1 = schema1.get("table_count", 0)
        table_count2 = schema2.get("table_count", 0)

        if table_count1 > 0 or table_count2 > 0:
            # Calculate similarity based on ratio
            max_count = max(table_count1, table_count2)
            min_count = min(table_count1, table_count2)
            ratio = min_count / max_count if max_count > 0 else 0.0
            score += weight * ratio
        elif table_count1 == 0 and table_count2 == 0:
            # Both have no tables, consider it a match
            score += weight

        # Compare content structure (weight: 0.3)
        weight = 0.3
        total_weight += weight

        # Simple structure comparison based on section levels
        structure1 = schema1.get("content_structure", [])
        structure2 = schema2.get("content_structure", [])

        if structure1 and structure2:
            # Compare level distributions
            levels1 = [s.get("level", 0) for s in structure1]
            levels2 = [s.get("level", 0) for s in structure2]

            # Calculate average level
            avg1 = sum(levels1) / len(levels1) if levels1 else 0
            avg2 = sum(levels2) / len(levels2) if levels2 else 0

            # Calculate similarity based on average level difference
            level_diff = abs(avg1 - avg2)
            level_sim = 1.0 / (
                1.0 + level_diff
            )  # Similarity decreases as difference increases

            score += weight * level_sim

        # Normalize score
        return score / total_weight if total_weight > 0 else 0.0
