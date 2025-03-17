"""
Example script demonstrating schema analysis and visualization.
"""

from utils.pipeline.schema.extended_registry import ExtendedSchemaRegistry
from utils.pipeline.utils.progress import PipelineProgress


def main():
    """Run schema analysis example."""
    progress = PipelineProgress()

    try:
        # Initialize extended schema registry
        registry = ExtendedSchemaRegistry()
        schemas = registry.list_schemas()

        if not schemas:
            progress.display_error("No schemas found. Process some documents first.")
            return

        progress.display_success(f"Found {len(schemas)} schemas")

        # Analyze schemas
        progress.display_success("Analyzing schemas...")
        analysis = registry.analyze()

        # Display analysis results
        progress.display_success("\nSchema Analysis Results:")
        progress.display_success(f"Total Schemas: {analysis.get('schema_count', 0)}")

        doc_types = analysis.get("document_types", {})
        if doc_types:
            progress.display_success("\nDocument Types:")
            for doc_type, count in doc_types.items():
                progress.display_success(f"  {doc_type}: {count}")

        # Display common metadata fields
        common_metadata = analysis.get("common_metadata", {})
        if common_metadata:
            progress.display_success("\nCommon Metadata Fields:")
            for field, frequency in sorted(
                common_metadata.items(), key=lambda x: x[1], reverse=True
            ):
                progress.display_success(f"  {field}: {frequency:.2f}")

        # Display table patterns
        table_patterns = analysis.get("table_patterns", {})
        if table_patterns:
            progress.display_success("\nTable Patterns:")
            progress.display_success(
                f"  Schemas with tables: {table_patterns.get('schemas_with_tables', 0)}"
            )
            progress.display_success(
                f"  Average tables per schema: {table_patterns.get('avg_tables_per_schema', 0):.2f}"
            )
            progress.display_success(
                f"  Average rows per table: {table_patterns.get('avg_rows_per_table', 0):.2f}"
            )

        # Generate visualizations if there are multiple schemas
        if len(schemas) >= 2:
            progress.display_success("\nGenerating visualizations...")

            # Create visualizations directory
            import os

            viz_dir = os.path.join(
                "utils", "pipeline", "schema", "data", "visualizations"
            )
            os.makedirs(viz_dir, exist_ok=True)

            # Generate cluster visualization
            try:
                cluster_viz = registry.visualize("clusters", output_dir=viz_dir)
                progress.display_success(
                    f"Cluster visualization saved to: {cluster_viz}"
                )
            except Exception as e:
                progress.display_error(
                    f"Error generating cluster visualization: {str(e)}"
                )

            # Generate feature visualization
            try:
                feature_viz = registry.visualize("features", output_dir=viz_dir)
                progress.display_success(
                    f"Feature visualization saved to: {feature_viz}"
                )
            except Exception as e:
                progress.display_error(
                    f"Error generating feature visualization: {str(e)}"
                )

            # Compare first two schemas
            schema_id1 = schemas[0]["id"]
            schema_id2 = schemas[1]["id"]

            progress.display_success(
                f"\nComparing schemas: {schema_id1} vs {schema_id2}"
            )
            comparison = registry.compare(schema_id1, schema_id2)

            progress.display_success(
                f"Overall Similarity: {comparison.get('overall_similarity', 0):.2f}"
            )
            progress.display_success(
                f"Same Document Type: {comparison.get('same_document_type', False)}"
            )

            # Generate structure visualizations
            try:
                structure_viz = registry.visualize(
                    "structure", [schema_id1, schema_id2], viz_dir
                )
                progress.display_success(
                    f"Structure visualizations saved to: {structure_viz}"
                )
            except Exception as e:
                progress.display_error(
                    f"Error generating structure visualization: {str(e)}"
                )

        progress.display_success("\nSchema analysis complete!")

    except Exception as e:
        progress.display_error(f"Error analyzing schemas: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
