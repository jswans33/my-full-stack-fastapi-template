"""
Test script to verify the classification override fix.

This script tests the fix for the classification override issue where HVAC documents
with multiple tables were being classified as "FORM" instead of "HVAC_SPECIFICATION".
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from utils.pipeline.processors.classifiers.rule_based import RuleBasedClassifier
from utils.pipeline.utils.logging import get_logger

# Set up logging
logger = get_logger(__name__)


def create_test_document(table_count=5):
    """
    Create a test document with HVAC content and multiple tables.

    Args:
        table_count: Number of tables to include in the document

    Returns:
        Dictionary representing a document with HVAC content and tables
    """
    # Create a document with HVAC content
    document = {
        "path": "test_documents/HVAC_SPECIFICATION_with_tables.pdf",
        "content": [
            {
                "title": "HVAC System Specifications",
                "content": """
                This document outlines the specifications for the HVAC system.
                The system includes heating, ventilation, and air conditioning components.
                Temperature control is maintained through thermostats.
                Humidity levels are monitored and controlled.
                Airflow is regulated through dampers and diffusers.
                """,
            },
            {
                "title": "System Components",
                "content": """
                The HVAC system includes the following components:
                - Air handling units (AHU)
                - Variable air volume (VAV) boxes
                - Chillers and boilers
                - Ductwork and piping
                - Thermostats and sensors
                """,
            },
        ],
        "metadata": {
            "title": "HVAC Specification Document",
            "author": "Test Author",
            "date": "2025-03-15",
        },
    }

    # Add tables to the document
    document["tables"] = []
    for i in range(table_count):
        document["tables"].append(
            {
                "page": 1,
                "table_number": i + 1,
                "headers": ["Component", "Capacity", "Efficiency", "Manufacturer"],
                "data": [
                    ["AHU-1", "10,000 CFM", "95%", "Carrier"],
                    ["Chiller-1", "500 tons", "0.6 kW/ton", "Trane"],
                    ["Boiler-1", "2,000 MBH", "95%", "Cleaver-Brooks"],
                ],
                "column_count": 4,
                "row_count": 3,
                "detection_method": "layout_analysis",
            }
        )

    return document


def create_features(document):
    """
    Extract features from a document for classification.

    Args:
        document: Document data

    Returns:
        Dictionary of features
    """
    # Extract section titles
    section_titles = [
        section.get("title", "") for section in document.get("content", [])
    ]

    # Count tables and sections
    table_count = len(document.get("tables", []))
    section_count = len(document.get("content", []))

    return {
        "section_titles": section_titles,
        "table_count": table_count,
        "section_count": section_count,
    }


def test_classification_with_hvac_config():
    """
    Test classification with HVAC configuration.

    This test verifies that an HVAC document with multiple tables is correctly
    classified as "HVAC_SPECIFICATION" instead of "FORM" when using the HVAC
    configuration.
    """
    # Load HVAC configuration
    try:
        import json

        config_path = os.path.join("utils", "pipeline", "config", "hvac_config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Error loading HVAC configuration: {str(e)}")
        config = {}

    # Create classifier with HVAC configuration
    classifier = RuleBasedClassifier(config)

    # Create test document with multiple tables
    document = create_test_document(table_count=5)
    features = create_features(document)

    # Classify document
    result = classifier.classify(document, features)

    # Print classification result
    logger.info(f"Classification result: {result}")

    # Check if document was correctly classified as HVAC_SPECIFICATION
    if result.get("document_type") == "HVAC_SPECIFICATION":
        logger.info(
            "✅ Test PASSED: Document correctly classified as HVAC_SPECIFICATION"
        )
    else:
        logger.error(
            f"❌ Test FAILED: Document classified as {result.get('document_type')} instead of HVAC_SPECIFICATION"
        )
        logger.error(f"Confidence: {result.get('confidence')}")
        logger.error(f"Key features: {result.get('key_features')}")


def test_classification_before_fix():
    """
    Simulate classification behavior before the fix.

    This test demonstrates how the document would have been classified before
    the fix by forcing the classifier to use generic classification.
    """
    # Load HVAC configuration
    try:
        import json

        config_path = os.path.join("utils", "pipeline", "config", "hvac_config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Error loading HVAC configuration: {str(e)}")
        config = {}

    # Create classifier with HVAC configuration
    classifier = RuleBasedClassifier(config)

    # Create test document with multiple tables
    document = create_test_document(table_count=5)
    features = create_features(document)

    # Force generic classification (simulating behavior before fix)
    result = classifier._classify_generic(document, features)

    # Print classification result
    logger.info(f"Classification result (before fix): {result}")

    # Check if document would have been classified as FORM
    if result.get("document_type") == "FORM":
        logger.info(
            "✅ Test PASSED: Document would have been classified as FORM before the fix"
        )
    else:
        logger.error(
            f"❌ Test FAILED: Document would have been classified as {result.get('document_type')} instead of FORM"
        )


if __name__ == "__main__":
    # Run tests
    logger.info("=== Testing Classification Override Fix ===")
    logger.info("Testing classification with HVAC configuration (after fix):")
    test_classification_with_hvac_config()

    logger.info("\nSimulating classification behavior before fix:")
    test_classification_before_fix()
