"""
Schema vectorizer module.

This module provides functionality for converting document schemas to numerical vectors.
"""

from typing import Any, Dict, List, Optional

from utils.pipeline.utils.logging import get_logger


class SchemaVectorizer:
    """
    Converts document schemas to numerical feature vectors.

    This class provides functionality for:
    1. Converting schemas to numerical vectors for comparison
    2. Extracting features from schema structure and content
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the schema vectorizer.

        Args:
            config: Configuration dictionary for the vectorizer
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

    def vectorize_schema(self, schema: Dict[str, Any]) -> List[float]:
        """
        Convert a schema to a numerical feature vector.

        Args:
            schema: Schema to vectorize

        Returns:
            List representing the schema features
        """
        # Initialize feature vector components
        features = []

        # 1. Metadata features
        metadata_fields = schema.get("metadata_fields", [])
        features.append(float(len(metadata_fields)))

        # Common metadata fields (one-hot encoding)
        common_fields = [
            "title",
            "author",
            "subject",
            "creator",
            "producer",
            "creation_date",
        ]
        for field in common_fields:
            features.append(1.0 if field in metadata_fields else 0.0)

        # 2. Structure features
        features.append(float(schema.get("section_count", 0)))

        # Calculate hierarchy depth and distribution
        content_structure = schema.get("content_structure", [])
        max_depth = self._calculate_max_depth(content_structure)
        features.append(float(max_depth))

        # Level distribution (percentage of sections at each level, up to 5 levels)
        level_counts = self._count_sections_by_level(content_structure)
        total_sections = sum(level_counts.values())

        for level in range(1, 6):  # Levels 1-5
            if total_sections > 0:
                features.append(level_counts.get(level, 0) / total_sections)
            else:
                features.append(0.0)

        # 3. Table features
        table_count = schema.get("table_count", 0)
        features.append(float(table_count))

        table_structure = schema.get("table_structure", [])

        # Average rows per table
        if table_count > 0:
            avg_rows = (
                sum(table.get("row_count", 0) for table in table_structure)
                / table_count
            )
        else:
            avg_rows = 0.0
        features.append(avg_rows)

        # Average headers per table
        if table_count > 0:
            avg_headers = (
                sum(table.get("header_count", 0) for table in table_structure)
                / table_count
            )
        else:
            avg_headers = 0.0
        features.append(avg_headers)

        # Percentage of tables with headers
        if table_count > 0:
            tables_with_headers = sum(
                1 for table in table_structure if table.get("has_headers", False)
            )
            features.append(tables_with_headers / table_count)
        else:
            features.append(0.0)

        # Table size distribution (small: <5 rows, medium: 5-15 rows, large: >15 rows)
        small_tables = sum(
            1 for table in table_structure if table.get("row_count", 0) < 5
        )
        medium_tables = sum(
            1 for table in table_structure if 5 <= table.get("row_count", 0) <= 15
        )
        large_tables = sum(
            1 for table in table_structure if table.get("row_count", 0) > 15
        )

        if table_count > 0:
            features.append(small_tables / table_count)
            features.append(medium_tables / table_count)
            features.append(large_tables / table_count)
        else:
            features.append(0.0)
            features.append(0.0)
            features.append(0.0)

        return features

    def get_feature_names(self) -> List[str]:
        """
        Get names of features in the vector.

        Returns:
            List of feature names
        """
        feature_names = [
            "metadata_field_count",
        ]

        # Common metadata fields
        common_fields = [
            "title",
            "author",
            "subject",
            "creator",
            "producer",
            "creation_date",
        ]
        for field in common_fields:
            feature_names.append(f"has_{field}")

        # Structure features
        feature_names.extend(
            [
                "section_count",
                "max_depth",
            ]
        )

        # Level distribution
        for level in range(1, 6):
            feature_names.append(f"level_{level}_pct")

        # Table features
        feature_names.extend(
            [
                "table_count",
                "avg_rows_per_table",
                "avg_headers_per_table",
                "tables_with_headers_pct",
                "small_tables_pct",
                "medium_tables_pct",
                "large_tables_pct",
            ]
        )

        return feature_names

    def _calculate_max_depth(self, structure, current_depth=1):
        """Calculate maximum depth of the section hierarchy."""
        if not structure:
            return current_depth - 1

        max_depth = current_depth
        for section in structure:
            if "children" in section and section["children"]:
                child_depth = self._calculate_max_depth(
                    section["children"], current_depth + 1
                )
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _count_sections_by_level(self, structure, current_level=1, counts=None):
        """Count sections at each level of the hierarchy."""
        if counts is None:
            counts = {}

        if not structure:
            return counts

        # Count sections at this level
        counts[current_level] = counts.get(current_level, 0) + len(structure)

        # Count children
        for section in structure:
            if "children" in section and section["children"]:
                self._count_sections_by_level(
                    section["children"], current_level + 1, counts
                )

        return counts
