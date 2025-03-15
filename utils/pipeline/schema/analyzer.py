"""
Schema analyzer module.

This module provides functionality for analyzing and comparing document schemas.
"""

import json
from typing import Any, Dict, List, Optional

from utils.pipeline.utils.logging import get_logger


class SchemaAnalyzer:
    """
    Analyzes document schemas to extract patterns and insights.

    This class provides functionality for:
    1. Analyzing schemas to extract patterns and insights
    2. Comparing schemas to identify similarities and differences
    3. Clustering similar schemas together
    """

    def __init__(self, registry, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the schema analyzer.

        Args:
            registry: Schema registry instance
            config: Configuration dictionary for the analyzer
        """
        self.registry = registry
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Default configuration
        self.default_config = {
            "similarity_threshold": 0.7,
            "cluster_method": "hierarchical",
            "feature_weights": {"metadata": 0.3, "structure": 0.4, "tables": 0.3},
        }

        # Merge with provided config
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value

    def analyze_schemas(self, document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze schemas to extract patterns and insights.

        Args:
            document_type: Optional document type to filter by

        Returns:
            Analysis results
        """
        # Get schemas to analyze
        schemas = self.registry.list_schemas(document_type)

        if not schemas:
            return {"error": "No schemas found for analysis"}

        # Analyze document types
        doc_types = {}
        for schema in schemas:
            doc_type = schema.get("document_type", "UNKNOWN")
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

        # Analyze metadata fields
        common_metadata = self._find_common_metadata(schemas)

        # Analyze table patterns
        table_patterns = self._analyze_table_patterns(schemas)

        # Analyze section patterns
        section_patterns = self._analyze_section_patterns(schemas)

        return {
            "schema_count": len(schemas),
            "document_types": doc_types,
            "common_metadata": common_metadata,
            "table_patterns": table_patterns,
            "section_patterns": section_patterns,
        }

    def compare_schemas(self, schema_id1: str, schema_id2: str) -> Dict[str, Any]:
        """
        Compare two schemas and identify similarities and differences.

        Args:
            schema_id1: ID of first schema
            schema_id2: ID of second schema

        Returns:
            Comparison results
        """
        schema1 = self.registry.get_schema(schema_id1)
        schema2 = self.registry.get_schema(schema_id2)

        if not schema1:
            return {"error": f"Schema {schema_id1} not found"}
        if not schema2:
            return {"error": f"Schema {schema_id2} not found"}

        # Use existing matcher for comparison
        from utils.pipeline.schema.matchers import StructureMatcher

        matcher = StructureMatcher()
        similarity = matcher.match(schema1, schema2)

        # Detailed comparison
        comparison = {
            "overall_similarity": similarity,
            "same_document_type": schema1.get("document_type")
            == schema2.get("document_type"),
            "metadata_comparison": self._compare_metadata(schema1, schema2),
            "structure_comparison": self._compare_structure(schema1, schema2),
            "table_comparison": self._compare_tables(schema1, schema2),
        }

        return comparison

    def cluster_schemas(
        self, similarity_threshold: Optional[float] = None
    ) -> List[List[str]]:
        """
        Cluster schemas based on similarity.

        Args:
            similarity_threshold: Minimum similarity threshold for clustering

        Returns:
            List of clusters, where each cluster is a list of schema IDs
        """
        if similarity_threshold is None:
            similarity_threshold = self.config["similarity_threshold"]

        # Get all schemas
        schemas = self.registry.list_schemas()
        if not schemas:
            return []

        # Extract schema IDs
        schema_ids = [schema["id"] for schema in schemas]

        # Implement a simple hierarchical clustering
        clusters = []
        processed = set()

        for schema_id1 in schema_ids:
            if schema_id1 in processed:
                continue

            cluster = [schema_id1]
            processed.add(schema_id1)

            for schema_id2 in schema_ids:
                if schema_id2 in processed or schema_id1 == schema_id2:
                    continue

                comparison = self.compare_schemas(schema_id1, schema_id2)
                if (
                    "error" not in comparison
                    and comparison["overall_similarity"] >= similarity_threshold
                ):
                    cluster.append(schema_id2)
                    processed.add(schema_id2)

            clusters.append(cluster)

        return clusters

    def get_schema_summary(self, schema_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a summary of a schema or all schemas.

        Args:
            schema_id: ID of the schema to summarize, or None for all schemas

        Returns:
            Dictionary with schema summary information
        """
        if schema_id:
            schema = self.registry.get_schema(schema_id)
            if not schema:
                return {"error": f"Schema {schema_id} not found"}
            return self._summarize_schema(schema_id, schema)

        # Summarize all schemas
        summaries = {}
        for schema in self.registry.list_schemas():
            if "id" in schema:
                schema_id = schema["id"]
                summaries[schema_id] = self._summarize_schema(schema_id, schema)

        return summaries

    def export_analysis(
        self, analysis: Dict[str, Any], output_path: str, format: str = "json"
    ) -> str:
        """
        Export analysis results to file.

        Args:
            analysis: Analysis results to export
            output_path: Path to save the results
            format: Export format (json, csv)

        Returns:
            Path to the exported file
        """
        try:
            if format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(analysis, f, indent=2)
            elif format == "csv":
                # Convert to CSV format
                try:
                    import pandas as pd

                    # Convert analysis to DataFrame
                    # This is a simplified conversion - would need to be adapted for different analyses
                    if "document_types" in analysis:
                        df = pd.DataFrame(
                            list(analysis["document_types"].items()),
                            columns=["Document Type", "Count"],
                        )
                        df.to_csv(output_path, index=False)
                    else:
                        # Generic fallback
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write(
                                "Analysis results cannot be converted to CSV format\n"
                            )
                            f.write(
                                f"Please use JSON format instead: {json.dumps(analysis, indent=2)}"
                            )
                except ImportError:
                    return "Error: pandas is required for CSV export. Please install it or use JSON format."
            else:
                return f"Unsupported export format: {format}"

            return output_path
        except Exception as e:
            self.logger.error(f"Error exporting analysis: {str(e)}", exc_info=True)
            return f"Error exporting analysis: {str(e)}"

    def _find_common_metadata(self, schemas: List[Dict[str, Any]]) -> Dict[str, float]:
        """Find common metadata fields across schemas."""
        field_counts = {}

        for schema in schemas:
            metadata_fields = schema.get("metadata_fields", [])
            for field in metadata_fields:
                field_counts[field] = field_counts.get(field, 0) + 1

        # Calculate frequency (percentage of schemas with each field)
        total_schemas = len(schemas)
        return {field: count / total_schemas for field, count in field_counts.items()}

    def _analyze_table_patterns(self, schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze table patterns across schemas."""
        # Count schemas with tables
        schemas_with_tables = sum(
            1 for schema in schemas if schema.get("table_count", 0) > 0
        )

        # Calculate average tables per schema
        total_tables = sum(schema.get("table_count", 0) for schema in schemas)
        avg_tables = total_tables / len(schemas) if schemas else 0

        # Analyze table structures
        row_counts = []
        header_counts = []

        for schema in schemas:
            table_structures = schema.get("table_structure", [])
            for table in table_structures:
                row_counts.append(table.get("row_count", 0))
                header_counts.append(table.get("header_count", 0))

        return {
            "schemas_with_tables": schemas_with_tables,
            "schemas_with_tables_pct": schemas_with_tables / len(schemas)
            if schemas
            else 0,
            "avg_tables_per_schema": avg_tables,
            "avg_rows_per_table": sum(row_counts) / len(row_counts)
            if row_counts
            else 0,
            "avg_headers_per_table": sum(header_counts) / len(header_counts)
            if header_counts
            else 0,
            "tables_with_headers_pct": sum(1 for h in header_counts if h > 0)
            / len(header_counts)
            if header_counts
            else 0,
        }

    def _analyze_section_patterns(
        self, schemas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze section patterns across schemas."""
        # Count schemas with sections
        schemas_with_sections = sum(
            1 for schema in schemas if schema.get("section_count", 0) > 0
        )

        # Calculate average sections per schema
        total_sections = sum(schema.get("section_count", 0) for schema in schemas)
        avg_sections = total_sections / len(schemas) if schemas else 0

        return {
            "schemas_with_sections": schemas_with_sections,
            "schemas_with_sections_pct": schemas_with_sections / len(schemas)
            if schemas
            else 0,
            "avg_sections_per_schema": avg_sections,
        }

    def _summarize_schema(
        self, schema_id: Any, schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a summary for a single schema."""
        summary = {
            "schema_id": schema_id,
            "document_type": schema.get("document_type", "UNKNOWN"),
            "recorded_at": schema.get("recorded_at", "Unknown"),
            "metadata_fields": len(schema.get("metadata_fields", [])),
            "section_count": schema.get("section_count", 0),
            "table_count": schema.get("table_count", 0),
        }

        # Analyze table structure
        table_structure = schema.get("table_structure", [])
        if table_structure:
            summary["avg_rows_per_table"] = sum(
                t.get("row_count", 0) for t in table_structure
            ) / len(table_structure)
            summary["tables_with_headers"] = sum(
                1 for t in table_structure if t.get("has_headers", False)
            )

        # Analyze content structure
        content_structure = schema.get("content_structure", [])
        if content_structure:
            summary["max_section_depth"] = self._get_max_section_depth(
                content_structure
            )

        return summary

    def _get_max_section_depth(self, structure, current_depth=1):
        """Recursively find the maximum depth of nested sections."""
        if not structure:
            return current_depth - 1

        max_depth = current_depth
        for section in structure:
            if "children" in section and section["children"]:
                child_depth = self._get_max_section_depth(
                    section["children"], current_depth + 1
                )
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _compare_metadata(
        self, schema1: Dict[str, Any], schema2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare metadata fields between schemas."""
        fields1 = set(schema1.get("metadata_fields", []))
        fields2 = set(schema2.get("metadata_fields", []))

        common = fields1.intersection(fields2)
        only_in_1 = fields1 - fields2
        only_in_2 = fields2 - fields1

        return {
            "common_fields": list(common),
            "only_in_schema1": list(only_in_1),
            "only_in_schema2": list(only_in_2),
            "similarity": len(common) / len(fields1.union(fields2))
            if fields1 or fields2
            else 1.0,
        }

    def _compare_structure(
        self, schema1: Dict[str, Any], schema2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare content structure between schemas."""
        section_count1 = schema1.get("section_count", 0)
        section_count2 = schema2.get("section_count", 0)

        structure1 = schema1.get("content_structure", [])
        structure2 = schema2.get("content_structure", [])

        # Use a simplified structure comparison
        return {
            "section_count_1": section_count1,
            "section_count_2": section_count2,
            "section_count_diff": abs(section_count1 - section_count2),
            "similarity": min(section_count1, section_count2)
            / max(section_count1, section_count2)
            if max(section_count1, section_count2) > 0
            else 1.0,
        }

    def _compare_tables(
        self, schema1: Dict[str, Any], schema2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare table structure between schemas."""
        table_count1 = schema1.get("table_count", 0)
        table_count2 = schema2.get("table_count", 0)

        tables1 = schema1.get("table_structure", [])
        tables2 = schema2.get("table_structure", [])

        # Calculate average rows per table
        avg_rows1 = (
            sum(t.get("row_count", 0) for t in tables1) / table_count1
            if table_count1 > 0
            else 0
        )
        avg_rows2 = (
            sum(t.get("row_count", 0) for t in tables2) / table_count2
            if table_count2 > 0
            else 0
        )

        return {
            "table_count_1": table_count1,
            "table_count_2": table_count2,
            "table_count_diff": abs(table_count1 - table_count2),
            "avg_rows_1": avg_rows1,
            "avg_rows_2": avg_rows2,
            "avg_rows_diff": abs(avg_rows1 - avg_rows2),
            "count_similarity": min(table_count1, table_count2)
            / max(table_count1, table_count2)
            if max(table_count1, table_count2) > 0
            else 1.0,
        }
