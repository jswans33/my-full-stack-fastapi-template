#!/usr/bin/env python3
"""
Test script for schema storage enhancements.

This script tests the enhanced schema storage capabilities:
1. Storing content samples (up to 5 sections) without truncation
2. Storing table data samples (up to 3 tables)
3. Including more detailed metadata about sections and tables
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from typing import Any, Dict

from utils.pipeline.schema.registry import SchemaRegistry
from utils.pipeline.schema.visualizer import SchemaVisualizer
from utils.pipeline.utils.progress import PipelineProgress


def main():
    """Main entry point for testing schema storage enhancements."""
    progress = PipelineProgress()
    progress.display_success("Testing Schema Storage Enhancements")

    # Create test document data
    test_data = create_test_document_data()

    # Test schema storage
    schema_id = test_schema_storage(test_data, progress)

    # Test schema visualization
    if schema_id:
        test_schema_visualization(schema_id, progress)

    progress.display_success("Schema Storage Enhancement Tests Completed")


def create_test_document_data() -> Dict[str, Any]:
    """
    Create test document data with content and tables.

    Returns:
        Test document data dictionary
    """
    # Create test content sections
    content = [
        {
            "title": "Section 1: Introduction",
            "content": "This is the introduction section with a detailed explanation of the document's purpose. "
            * 5,
            "level": 1,
            "children": [],
        },
        {
            "title": "Section 2: Methodology",
            "content": "This section describes the methodology used in the document. "
            * 5,
            "level": 1,
            "children": [
                {
                    "title": "Section 2.1: Data Collection",
                    "content": "This subsection describes the data collection process. "
                    * 5,
                    "level": 2,
                    "children": [],
                },
                {
                    "title": "Section 2.2: Data Analysis",
                    "content": "This subsection describes the data analysis process. "
                    * 5,
                    "level": 2,
                    "children": [],
                },
            ],
        },
        {
            "title": "Section 3: Results",
            "content": "This section presents the results of the analysis. " * 5,
            "level": 1,
            "children": [],
        },
        {
            "title": "Section 4: Discussion",
            "content": "This section discusses the implications of the results. " * 5,
            "level": 1,
            "children": [],
        },
        {
            "title": "Section 5: Conclusion",
            "content": "This section concludes the document with a summary of findings. "
            * 5,
            "level": 1,
            "children": [],
        },
        {
            "title": "Section 6: References",
            "content": "This section lists the references used in the document. " * 5,
            "level": 1,
            "children": [],
        },
    ]

    # Create test tables
    tables = [
        {
            "headers": ["ID", "Name", "Value", "Description"],
            "data": [
                ["1", "Item A", "10.5", "First item in the table"],
                ["2", "Item B", "20.3", "Second item in the table"],
                ["3", "Item C", "15.7", "Third item in the table"],
                ["4", "Item D", "8.2", "Fourth item in the table"],
                ["5", "Item E", "12.9", "Fifth item in the table"],
                ["6", "Item F", "18.1", "Sixth item in the table"],
            ],
            "column_count": 4,
            "row_count": 6,
            "detection_method": "border_detection",
            "page": 1,
            "border_info": {
                "x0": 50,
                "y0": 100,
                "x1": 550,
                "y1": 300,
                "rows": 6,
                "cols": 4,
            },
        },
        {
            "headers": ["Category", "Subcategory", "Count", "Percentage"],
            "data": [
                ["A", "A1", "150", "30%"],
                ["A", "A2", "100", "20%"],
                ["B", "B1", "200", "40%"],
                ["B", "B2", "50", "10%"],
            ],
            "column_count": 4,
            "row_count": 4,
            "detection_method": "labeled_table",
            "page": 2,
            "table_label": "Table 2: Category Distribution",
        },
        {
            "headers": ["Date", "Event", "Location", "Attendees"],
            "data": [
                ["2023-01-15", "Meeting A", "Room 101", "10"],
                ["2023-02-20", "Meeting B", "Room 102", "15"],
                ["2023-03-25", "Meeting C", "Room 103", "8"],
            ],
            "column_count": 4,
            "row_count": 3,
            "detection_method": "layout_analysis",
            "page": 3,
        },
        {
            "headers": ["Quarter", "Revenue", "Expenses", "Profit"],
            "data": [
                ["Q1", "$100,000", "$80,000", "$20,000"],
                ["Q2", "$120,000", "$90,000", "$30,000"],
                ["Q3", "$110,000", "$85,000", "$25,000"],
                ["Q4", "$130,000", "$95,000", "$35,000"],
            ],
            "column_count": 4,
            "row_count": 4,
            "detection_method": "text_analysis",
            "page": 4,
        },
    ]

    # Create test metadata
    metadata = {
        "title": "Test Document",
        "author": "Test Author",
        "date": "2023-04-01",
        "version": "1.0",
        "keywords": "test, schema, storage, enhancement",
    }

    # Create test document data
    return {
        "content": content,
        "tables": tables,
        "metadata": metadata,
        "path": "test_document.pdf",
    }


def test_schema_storage(
    document_data: Dict[str, Any], progress: PipelineProgress
) -> str:
    """
    Test schema storage enhancements.

    Args:
        document_data: Test document data
        progress: Progress tracker

    Returns:
        Schema ID if successful, empty string otherwise
    """
    progress.display_success("Testing schema storage...")

    # Initialize registry
    registry = SchemaRegistry()

    # Record schema
    schema_id = registry.record(document_data, "TEST_DOCUMENT", "Test Document")

    if not schema_id:
        progress.display_error("Failed to record schema")
        return ""

    progress.display_success(f"Recorded schema with ID: {schema_id}")

    # Get schema
    schema = registry.get_schema(schema_id)

    if not schema:
        progress.display_error(f"Failed to retrieve schema with ID: {schema_id}")
        return ""

    # Verify schema structure
    verify_schema_structure(schema, progress)

    return schema_id


def verify_schema_structure(schema: Dict[str, Any], progress: PipelineProgress) -> None:
    """
    Verify the structure of the enhanced schema.

    Args:
        schema: Schema to verify
        progress: Progress tracker
    """
    # Check basic schema information
    progress.display_success("Verifying basic schema information...")

    assert "document_type" in schema, "Missing document_type"
    assert schema["document_type"] == "TEST_DOCUMENT", "Incorrect document_type"

    assert "document_name" in schema, "Missing document_name"
    assert schema["document_name"] == "Test Document", "Incorrect document_name"

    assert "section_count" in schema, "Missing section_count"
    assert schema["section_count"] == 6, "Incorrect section_count"

    assert "table_count" in schema, "Missing table_count"
    assert schema["table_count"] == 4, "Incorrect table_count"

    progress.display_success("Basic schema information verified")

    # Check content samples
    progress.display_success("Verifying content samples...")

    assert "content_samples" in schema, "Missing content_samples"
    assert len(schema["content_samples"]) == 5, "Incorrect number of content samples"

    # Check first content sample
    first_sample = schema["content_samples"][0]
    assert "title" in first_sample, "Missing title in first content sample"
    assert first_sample["title"] == "Section 1: Introduction", (
        "Incorrect title in first content sample"
    )

    assert "content" in first_sample, "Missing content in first content sample"
    assert len(first_sample["content"]) > 100, (
        "Content in first sample is too short (may be truncated)"
    )

    assert "level" in first_sample, "Missing level in first content sample"
    assert first_sample["level"] == 1, "Incorrect level in first content sample"

    progress.display_success("Content samples verified")

    # Check table samples
    progress.display_success("Verifying table samples...")

    assert "table_samples" in schema, "Missing table_samples"
    assert len(schema["table_samples"]) == 3, "Incorrect number of table samples"

    # Check first table sample
    first_table = schema["table_samples"][0]
    assert "headers" in first_table, "Missing headers in first table sample"
    assert len(first_table["headers"]) == 4, (
        "Incorrect number of headers in first table sample"
    )

    assert "data_sample" in first_table, "Missing data_sample in first table sample"
    assert len(first_table["data_sample"]) == 5, (
        "Incorrect number of rows in first table sample"
    )

    assert "column_count" in first_table, "Missing column_count in first table sample"
    assert first_table["column_count"] == 4, (
        "Incorrect column_count in first table sample"
    )

    assert "row_count" in first_table, "Missing row_count in first table sample"
    assert first_table["row_count"] == 6, "Incorrect row_count in first table sample"

    assert "detection_method" in first_table, (
        "Missing detection_method in first table sample"
    )
    assert first_table["detection_method"] == "border_detection", (
        "Incorrect detection_method in first table sample"
    )

    assert "border_info" in first_table, "Missing border_info in first table sample"
    assert "rows" in first_table["border_info"], "Missing rows in border_info"
    assert first_table["border_info"]["rows"] == 6, "Incorrect rows in border_info"

    progress.display_success("Table samples verified")

    # Print schema summary
    progress.display_success("Schema structure verification complete")
    progress.display_success(f"Schema ID: {schema.get('id', 'unknown')}")
    progress.display_success(f"Document Type: {schema.get('document_type', 'unknown')}")
    progress.display_success(f"Section Count: {schema.get('section_count', 0)}")
    progress.display_success(f"Table Count: {schema.get('table_count', 0)}")
    progress.display_success(
        f"Content Samples: {len(schema.get('content_samples', []))}"
    )
    progress.display_success(f"Table Samples: {len(schema.get('table_samples', []))}")


def test_schema_visualization(schema_id: str, progress: PipelineProgress) -> None:
    """
    Test schema visualization with enhanced schema.

    Args:
        schema_id: ID of the schema to visualize
        progress: Progress tracker
    """
    progress.display_success("Testing schema visualization...")

    # Initialize registry and visualizer
    registry = SchemaRegistry()
    visualizer = SchemaVisualizer(registry)

    # Create visualizations directory using absolute path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)  # utils/pipeline/tests -> utils/pipeline
    viz_dir = os.path.join(base_dir, "schema", "data", "visualizations")
    print(f"Creating visualization directory (absolute path): {viz_dir}")
    print(
        f"Directory exists before makedirs: {os.path.exists(os.path.dirname(viz_dir))}"
    )
    os.makedirs(viz_dir, exist_ok=True)
    print(f"Directory created: {os.path.exists(viz_dir)}")

    # Test table visualization
    progress.display_success("Generating table visualization...")

    output_path = os.path.join(viz_dir, f"tables_{schema_id}.png")
    print(f"Output path for table visualization: {output_path}")
    print(f"Output directory exists: {os.path.exists(os.path.dirname(output_path))}")
    result = visualizer.visualize_table_patterns(schema_id, output_path)
    print(f"Visualization result: {result}")
    print(f"Output file exists: {os.path.exists(output_path)}")

    if isinstance(result, list):
        progress.display_success(f"Generated {len(result)} table visualizations:")
        for path in result:
            progress.display_success(f"  - {path}")
    else:
        progress.display_success(f"Visualization result: {result}")

    # Test structure visualization
    progress.display_success("Generating structure visualization...")

    output_path = os.path.join(viz_dir, f"structure_{schema_id}.png")
    result = visualizer.visualize_schema_structure(schema_id, output_path)

    progress.display_success(f"Structure visualization result: {result}")

    progress.display_success("Schema visualization tests completed")


if __name__ == "__main__":
    main()
