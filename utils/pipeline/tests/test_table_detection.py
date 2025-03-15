"""
Test script to verify the table detection enhancements.

This script tests the enhanced table detection capabilities in the PDFExtractor,
including border detection, layout analysis, and text-based detection.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import fitz  # PyMuPDF

from utils.pipeline.processors.pdf_extractor import PDFExtractor
from utils.pipeline.utils.logging import get_logger

# Set up logging
logger = get_logger(__name__)


def test_table_detection():
    """
    Test the enhanced table detection capabilities.

    This test verifies that tables are correctly detected using the three
    detection methods: border detection, layout analysis, and text-based detection.
    """
    # Use the existing sample PDF file with absolute path
    test_pdf_path = "C:/Repos/FCA-dashboard3/my-full-stack-fastapi-template/utils/pipeline/data/tests/pdf/sample.pdf"

    # For Git Bash, use forward slashes
    test_pdf_path = test_pdf_path.replace("\\", "/")

    logger.info(f"Looking for PDF at absolute path: {test_pdf_path}")

    # Check if the file exists
    if not os.path.exists(test_pdf_path):
        logger.error(f"❌ Test FAILED: Sample PDF file not found at {test_pdf_path}")
        return []

    logger.info(f"Using sample PDF file: {test_pdf_path}")

    # Create a PDFExtractor instance
    extractor = PDFExtractor()

    # Open the test PDF
    doc = fitz.open(test_pdf_path)

    # Extract tables
    tables = extractor._extract_tables(doc)

    # Close the document
    doc.close()

    # Log the number of tables detected
    logger.info(f"Detected {len(tables)} tables")

    # Check if we detected the expected number of tables
    if len(tables) >= 2:
        logger.info("✅ Test PASSED: Expected tables detected")
    else:
        logger.error(
            f"❌ Test FAILED: Only {len(tables)} tables detected, expected at least 2"
        )

    # Check detection methods
    detection_methods = [table["detection_method"] for table in tables]

    # Count detection methods
    detection_method_counts = {}
    for method in detection_methods:
        if method in detection_method_counts:
            detection_method_counts[method] += 1
        else:
            detection_method_counts[method] = 1

    # Log detection methods summary
    logger.info("Detection methods summary:")
    for method, count in detection_method_counts.items():
        logger.info(f"  - {method}: {count} tables ({count / len(tables) * 100:.1f}%)")

    # Check if border detection was used
    if "border_detection" in detection_methods:
        logger.info("✅ Test PASSED: Border detection successful")

        # Get the table detected by border detection
        border_table = next(
            table for table in tables if table["detection_method"] == "border_detection"
        )

        # Check if border info is present
        if "border_info" in border_table:
            logger.info("✅ Test PASSED: Border info present")
            logger.info(f"Border info: {border_table['border_info']}")
        else:
            logger.error("❌ Test FAILED: Border info missing")
    else:
        logger.warning("⚠️ Border detection not used for any table")

    # Check if layout analysis was used
    if "layout_analysis" in detection_methods:
        logger.info("✅ Test PASSED: Layout analysis successful")
    else:
        logger.warning("⚠️ Layout analysis not used for any table")

    # Check if text-based detection was used
    if "text_analysis" in detection_methods:
        logger.info("✅ Test PASSED: Text-based detection successful")
    else:
        logger.warning("⚠️ Text-based detection not used for any table")

    # Check table structure (only for the first 5 tables to avoid verbose output)
    max_tables_to_show = min(5, len(tables))
    if max_tables_to_show > 0:
        logger.info("\nSample of detected tables:")
        for i in range(max_tables_to_show):
            table = tables[i]
            logger.info(f"\nTable {i + 1} structure:")
            logger.info(f"Headers: {table.get('headers', [])}")
            logger.info(f"Column count: {table.get('column_count', 0)}")
            logger.info(f"Row count: {table.get('row_count', 0)}")
            logger.info(f"Detection method: {table.get('detection_method', 'unknown')}")

            # Check if headers were detected
            if table.get("headers") and len(table.get("headers", [])) > 0:
                logger.info(f"✅ Table {i + 1}: Headers detected")
            else:
                logger.warning(f"⚠️ Table {i + 1}: No headers detected")

            # Check if data was extracted
            if table.get("data") and len(table.get("data", [])) > 0:
                logger.info(
                    f"✅ Table {i + 1}: Data extracted ({len(table.get('data', []))} rows)"
                )

                # Log first row of data
                if table.get("data"):
                    logger.info(f"First row: {table['data'][0]}")
            else:
                logger.error(f"❌ Table {i + 1}: No data extracted")

    # Count tables with headers
    tables_with_headers = sum(
        1
        for table in tables
        if table.get("headers") and len(table.get("headers", [])) > 0
    )
    logger.info(
        f"\nTables with headers: {tables_with_headers} ({tables_with_headers / len(tables) * 100:.1f}%)"
    )

    return tables


if __name__ == "__main__":
    # Run the test
    logger.info("=== Testing Enhanced Table Detection ===")
    tables = test_table_detection()

    # Summary
    logger.info("\n=== Test Summary ===")
    logger.info(f"Total tables detected: {len(tables)}")

    # Count by detection method
    border_count = sum(
        1 for table in tables if table["detection_method"] == "border_detection"
    )
    layout_count = sum(
        1 for table in tables if table["detection_method"] == "layout_analysis"
    )
    text_count = sum(
        1 for table in tables if table["detection_method"] == "text_analysis"
    )

    logger.info(f"Tables detected by border detection: {border_count}")
    logger.info(f"Tables detected by layout analysis: {layout_count}")
    logger.info(f"Tables detected by text-based detection: {text_count}")
