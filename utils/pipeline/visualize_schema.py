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

    if len(sys.argv) < 3:
        print("Usage: python visualize_schema.py <visualization_type> <schema_id>")
        print("Visualization types: clusters, features, structure, tables")
        return

    visualization_type = sys.argv[1]
    schema_id = sys.argv[2]

    # Create visualizations directory
    viz_dir = os.path.join("utils", "pipeline", "schema", "data", "visualizations")
    os.makedirs(viz_dir, exist_ok=True)

    # Initialize registry
    registry = ExtendedSchemaRegistry()

    # Generate visualization
    progress.display_success(
        f"Generating {visualization_type} visualization for schema {schema_id}..."
    )
    viz_path = registry.visualize(visualization_type, [schema_id], viz_dir)
    progress.display_success(f"Visualization saved to: {viz_path}")


if __name__ == "__main__":
    main()
