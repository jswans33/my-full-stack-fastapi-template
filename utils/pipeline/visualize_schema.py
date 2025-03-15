#!/usr/bin/env python3
"""
Script to visualize a specific schema.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.pipeline.schema.extended_registry import ExtendedSchemaRegistry
from utils.pipeline.utils.progress import PipelineProgress


def main():
    """Main entry point for schema visualization."""
    progress = PipelineProgress()

    # Check arguments
    if len(sys.argv) < 2:
        print_usage()
        return

    # Parse command
    command = sys.argv[1]

    if command == "list":
        # List available schemas
        list_schemas(progress)
        return
    elif command == "help":
        print_usage()
        return
    elif command in ["clusters", "features", "structure", "tables"]:
        # Visualization command
        visualization_type = command

        # Check if schema ID is provided
        if len(sys.argv) < 3 and visualization_type not in ["clusters", "features"]:
            print(
                f"Error: Schema ID is required for {visualization_type} visualization"
            )
            print_usage()
            return

        # Get schema ID (optional for clusters and features)
        schema_id = sys.argv[2] if len(sys.argv) >= 3 else "all"

        # Generate visualization
        generate_visualization(visualization_type, schema_id, progress)
    else:
        print(f"Unknown command: {command}")
        print_usage()


def print_usage():
    """Print usage information."""
    print("Usage:")
    print(
        "  python visualize_schema.py list                     - List available schemas"
    )
    print(
        "  python visualize_schema.py clusters [schema_id]     - Generate cluster visualization"
    )
    print(
        "  python visualize_schema.py features [schema_id]     - Generate feature visualization"
    )
    print(
        "  python visualize_schema.py structure <schema_id>    - Generate structure visualization"
    )
    print(
        "  python visualize_schema.py tables <schema_id>       - Generate table visualization"
    )
    print(
        "  python visualize_schema.py help                     - Show this help message"
    )


def list_schemas(progress):
    """List available schemas."""
    # Initialize registry
    registry = ExtendedSchemaRegistry()

    # Get all schemas
    schemas = registry.list_schemas()

    if not schemas:
        progress.display_error("No schemas found in registry")
        return

    # Display schemas
    progress.display_success(f"Found {len(schemas)} schemas:")

    # Group schemas by document type
    schemas_by_type = {}
    for schema in schemas:
        doc_type = schema.get("document_type", "UNKNOWN")
        if doc_type not in schemas_by_type:
            schemas_by_type[doc_type] = []
        schemas_by_type[doc_type].append(schema)

    # Display schemas by type
    for doc_type, type_schemas in schemas_by_type.items():
        progress.display_success(f"\n{doc_type} ({len(type_schemas)}):")
        for schema in type_schemas:
            schema_id = schema.get("id")
            recorded_at = schema.get("recorded_at", "Unknown")
            document_name = schema.get("document_name", "")
            progress.display_success(f"  - {schema_id} ({recorded_at}) {document_name}")


def generate_visualization(visualization_type, schema_id, progress):
    """Generate visualization for schema."""
    # Create visualizations directory
    viz_dir = os.path.join("utils", "pipeline", "schema", "data", "visualizations")
    os.makedirs(viz_dir, exist_ok=True)

    # Initialize registry
    registry = ExtendedSchemaRegistry()

    # Prepare schema IDs
    schema_ids = None
    if schema_id != "all":
        schema_ids = [schema_id]

    # Generate visualization
    progress.display_success(
        f"Generating {visualization_type} visualization for schema {schema_id}..."
    )
    viz_path = registry.visualize(visualization_type, schema_ids, viz_dir)

    # Handle multiple visualization paths
    if isinstance(viz_path, list):
        progress.display_success(f"Generated {len(viz_path)} visualizations:")
        for path in viz_path:
            progress.display_success(f"  - {path}")
    else:
        progress.display_success(f"Visualization saved to: {viz_path}")


if __name__ == "__main__":
    main()
