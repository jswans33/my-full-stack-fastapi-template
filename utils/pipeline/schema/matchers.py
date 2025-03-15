"""
Schema matchers module.

This module provides functionality for matching document schemas.
"""

from typing import Any, Dict, List, Optional

from utils.pipeline.utils.logging import get_logger


class SchemaMatcher:
    """
    Base class for schema matchers.

    Schema matchers are used to compare document schemas and determine
    if they match a known pattern.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the schema matcher.

        Args:
            config: Configuration dictionary for the matcher
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

    def match(self, schema: Dict[str, Any], known_schema: Dict[str, Any]) -> float:
        """
        Match a schema against a known schema.

        Args:
            schema: Schema to match
            known_schema: Known schema to match against

        Returns:
            Confidence score between 0.0 and 1.0
        """
        raise NotImplementedError("Subclasses must implement match()")


class StructureMatcher(SchemaMatcher):
    """
    Matches schemas based on their structure.

    This matcher compares the structure of documents, including:
    - Section hierarchy
    - Table structure
    - Metadata fields
    """

    def match(self, schema: Dict[str, Any], known_schema: Dict[str, Any]) -> float:
        """
        Match a schema against a known schema based on structure.

        Args:
            schema: Schema to match
            known_schema: Known schema to match against

        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0
        total_weight = 0.0

        # Compare metadata fields (weight: 0.2)
        weight = 0.2
        total_weight += weight

        metadata1 = set(schema.get("metadata_fields", []))
        metadata2 = set(known_schema.get("metadata_fields", []))

        if metadata1 and metadata2:
            common = len(metadata1.intersection(metadata2))
            total = len(metadata1.union(metadata2))
            score += weight * (common / total if total > 0 else 0.0)

        # Compare section counts (weight: 0.3)
        weight = 0.3
        total_weight += weight

        section_count1 = schema.get("section_count", 0)
        section_count2 = known_schema.get("section_count", 0)

        if section_count1 > 0 and section_count2 > 0:
            # Calculate similarity based on ratio
            ratio = min(section_count1, section_count2) / max(
                section_count1, section_count2
            )
            score += weight * ratio

        # Compare table counts (weight: 0.2)
        weight = 0.2
        total_weight += weight

        table_count1 = schema.get("table_count", 0)
        table_count2 = known_schema.get("table_count", 0)

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

        # Compare structure recursively
        structure1 = schema.get("content_structure", [])
        structure2 = known_schema.get("content_structure", [])

        structure_sim = self._compare_structures(structure1, structure2)
        score += weight * structure_sim

        # Normalize score
        return score / total_weight if total_weight > 0 else 0.0

    def _compare_structures(
        self, structure1: List[Dict[str, Any]], structure2: List[Dict[str, Any]]
    ) -> float:
        """
        Compare two content structures recursively.

        Args:
            structure1: First structure
            structure2: Second structure

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not structure1 or not structure2:
            return 0.0 if structure1 or structure2 else 1.0  # Both empty = match

        # Compare counts
        count_sim = min(len(structure1), len(structure2)) / max(
            len(structure1), len(structure2)
        )

        # Compare levels
        levels1 = [s.get("level", 0) for s in structure1]
        levels2 = [s.get("level", 0) for s in structure2]

        avg_level1 = sum(levels1) / len(levels1) if levels1 else 0
        avg_level2 = sum(levels2) / len(levels2) if levels2 else 0

        level_diff = abs(avg_level1 - avg_level2)
        level_sim = 1.0 / (
            1.0 + level_diff
        )  # Similarity decreases as difference increases

        # Compare children
        child_sims = []
        for i in range(min(len(structure1), len(structure2))):
            s1 = structure1[i]
            s2 = structure2[i]

            # Compare basic properties
            prop_sim = 0.0
            prop_count = 0

            # Compare has_title
            if "has_title" in s1 and "has_title" in s2:
                prop_sim += 1.0 if s1["has_title"] == s2["has_title"] else 0.0
                prop_count += 1

            # Compare has_content
            if "has_content" in s1 and "has_content" in s2:
                prop_sim += 1.0 if s1["has_content"] == s2["has_content"] else 0.0
                prop_count += 1

            # Compare has_children
            if "has_children" in s1 and "has_children" in s2:
                prop_sim += 1.0 if s1["has_children"] == s2["has_children"] else 0.0
                prop_count += 1

            # Calculate property similarity
            prop_sim = prop_sim / prop_count if prop_count > 0 else 0.0

            # Compare children recursively
            children1 = s1.get("children", [])
            children2 = s2.get("children", [])

            child_sim = self._compare_structures(children1, children2)

            # Combine property and child similarity
            section_sim = 0.7 * prop_sim + 0.3 * child_sim
            child_sims.append(section_sim)

        # Calculate average child similarity
        avg_child_sim = sum(child_sims) / len(child_sims) if child_sims else 0.0

        # Combine all similarities
        return 0.4 * count_sim + 0.3 * level_sim + 0.3 * avg_child_sim


class ContentMatcher(SchemaMatcher):
    """
    Matches schemas based on their content patterns.

    This matcher compares the content patterns of documents, including:
    - Section titles
    - Content keywords
    - Table headers
    """

    def match(self, schema: Dict[str, Any], known_schema: Dict[str, Any]) -> float:
        """
        Match a schema against a known schema based on content patterns.

        Args:
            schema: Schema to match
            known_schema: Known schema to match against

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # This is a placeholder implementation
        # In a real implementation, we would extract and compare content patterns

        # For now, return a simple structural match
        structure_matcher = StructureMatcher(self.config)
        return structure_matcher.match(schema, known_schema)


class SchemaMatcherFactory:
    """Factory for creating schema matchers."""

    @staticmethod
    def create_matcher(
        matcher_type: str, config: Optional[Dict[str, Any]] = None
    ) -> SchemaMatcher:
        """
        Create a schema matcher of the specified type.

        Args:
            matcher_type: Type of matcher to create
            config: Configuration dictionary for the matcher

        Returns:
            Schema matcher instance
        """
        if matcher_type == "structure":
            return StructureMatcher(config)
        elif matcher_type == "content":
            return ContentMatcher(config)
        else:
            # Default to structure matcher
            return StructureMatcher(config)
