"""
Example usage of the document classification system.

This script demonstrates how to:
1. Configure and initialize the classification system
2. Register custom classifiers
3. Classify documents using multiple strategies
4. Use ensemble classification
"""

import os
import sys
from typing import Any, Dict

import yaml

# Add the root directory to Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, root_dir)

from utils.pipeline.processors.classifiers.ml_based import MLBasedClassifier
from utils.pipeline.processors.document_classifier import DocumentClassifier


def load_config() -> Dict[str, Any]:
    """Load classification configuration from YAML file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(
        script_dir, "..", "config", "example_classifier_config.yaml"
    )
    print(f"Loading config from: {config_path}")
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return {}


def main():
    # Load configuration
    config = load_config()

    # Initialize document classifier
    classifier = DocumentClassifier(config)

    # Register additional ML-based classifier
    classifier.add_classifier(
        "ml_based",
        MLBasedClassifier,
        config.get("classifiers", {}).get("ml_based", {}),
    )

    # Example document data
    document_data = {
        "metadata": {
            "title": "Project Proposal - System Upgrade",
            "author": "John Smith",
            "date": "2025-03-15",
        },
        "content": [
            {
                "title": "Executive Summary",
                "content": "This proposal outlines our approach to upgrading...",
            },
            {
                "title": "Scope of Work",
                "content": "The project will be completed in three phases...",
            },
            {
                "title": "Payment Terms",
                "content": "Payment schedule: 30% upfront, 40% at milestone...",
            },
            {
                "title": "Delivery Schedule",
                "content": "Phase 1 will be delivered within 4 weeks...",
            },
        ],
        "tables": [
            {
                "title": "Cost Breakdown",
                "headers": ["Item", "Cost"],
                "rows": [
                    ["Phase 1", "$50,000"],
                    ["Phase 2", "$75,000"],
                    ["Phase 3", "$60,000"],
                ],
            }
        ],
    }

    # Classify document
    result = classifier.classify(document_data)

    # Print classification results
    print("\nDocument Classification Results:")
    print("-" * 30)
    print(f"Document Type: {result['document_type']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Schema Pattern: {result['schema_pattern']}")
    print("\nKey Features:")
    for feature in result.get("key_features", []):
        print(f"- {feature}")

    print("\nClassifiers Used:")
    for classifier_name in result.get("classifiers", []):
        print(f"- {classifier_name}")

    # Example of updating classifier configuration
    new_config = {
        "name": "ML-Based Classifier",
        "version": "1.0.1",
        "model": {
            "confidence_threshold": 0.8,  # Increased threshold
            "feature_weights": {
                "section_density": 0.4,  # Adjusted weights
                "table_density": 0.3,
                "avg_section_length": 0.2,
                "metadata_completeness": 0.1,
            },
        },
    }
    classifier.update_classifier_config("ml_based", new_config)

    # Get information about available classifiers
    print("\nAvailable Classifiers:")
    print("-" * 30)
    for info in classifier.get_available_classifiers():
        print(f"\nClassifier: {info['name']}")
        print(f"Supported Types: {', '.join(info['supported_types'])}")
        if info["has_config"]:
            print("Has Custom Configuration: Yes")
        print(f"Info: {info['info']}")


if __name__ == "__main__":
    main()
