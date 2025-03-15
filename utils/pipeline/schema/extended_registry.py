"""
Extended schema registry module.

This module extends the SchemaRegistry with analysis and visualization capabilities.
"""

from typing import Any, Dict, List, Optional, Union

from utils.pipeline.schema.registry import SchemaRegistry


class ExtendedSchemaRegistry(SchemaRegistry):
    """
    Extended registry for document schemas with analysis and visualization capabilities.

    This class extends SchemaRegistry with:
    1. Schema analysis functionality
    2. Schema comparison functionality
    3. Schema visualization functionality
    """

    def analyze(self, document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze schemas of the specified document type.

        Args:
            document_type: Optional document type to filter by

        Returns:
            Analysis results
        """
        from utils.pipeline.schema.analyzer import SchemaAnalyzer

        analyzer = SchemaAnalyzer(self)
        return analyzer.analyze_schemas(document_type)

    def compare(self, schema_id1: str, schema_id2: str) -> Dict[str, Any]:
        """
        Compare two schemas and identify similarities/differences.

        Args:
            schema_id1: ID of first schema
            schema_id2: ID of second schema

        Returns:
            Comparison results
        """
        from utils.pipeline.schema.analyzer import SchemaAnalyzer

        analyzer = SchemaAnalyzer(self)
        return analyzer.compare_schemas(schema_id1, schema_id2)

    def visualize(
        self,
        visualization_type: str = "clusters",
        schema_ids: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
    ) -> Union[str, List[str]]:
        """
        Generate visualizations for schemas.

        Args:
            visualization_type: Type of visualization to generate
            schema_ids: List of schema IDs to visualize, or None for all schemas
            output_dir: Directory to save visualizations, or None for default

        Returns:
            Path(s) to the generated visualization(s)
        """
        from utils.pipeline.schema.visualizer import SchemaVisualizer

        visualizer = SchemaVisualizer(self)
        return visualizer.visualize(visualization_type, schema_ids, output_dir)
