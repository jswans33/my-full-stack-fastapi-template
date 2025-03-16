"""
End-to-end test for the document classification system.
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from utils.pipeline.pipeline import Pipeline
from utils.pipeline.processors.document_classifier import DocumentClassifier


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Load test configuration."""
    config = {
        "enable_classification": True,
        "record_schemas": False,  # Disable for testing
        "ensemble": {
            "voting_method": "weighted_average",
            "minimum_confidence": 0.45,
            "classifier_weights": {
                "rule_based": 0.45,
                "pattern_matcher": 0.45,
                "ml_based": 0.1,
            },
        },
        # Add strategy paths
        "strategies": {
            "json": {
                "analyzer": "utils.pipeline.analyzer.base.MockStrategy",
                "cleaner": "utils.pipeline.cleaner.base.MockStrategy",
                "extractor": "utils.pipeline.processors.base.MockStrategy",
                "validator": "utils.pipeline.processors.base.MockStrategy",
            },
            "generic": {
                "analyzer": "utils.pipeline.analyzer.base.MockStrategy",
                "cleaner": "utils.pipeline.cleaner.base.MockStrategy",
                "extractor": "utils.pipeline.processors.base.MockStrategy",
                "validator": "utils.pipeline.processors.base.MockStrategy",
            },
        },
        "classifiers": {
            "rule_based": {
                "name": "Rule-Based Classifier",
                "version": "1.0.0",
                "classification": {
                    "rules": {
                        "PROPOSAL": {
                            "title_keywords": ["proposal", "project"],
                            "content_keywords": ["scope", "phases"],
                            "patterns": ["payment terms", "delivery schedule"],
                            "weights": {
                                "title_match": 0.4,
                                "content_match": 0.3,
                                "pattern_match": 0.3,
                            },
                            "threshold": 0.4,
                        }
                    }
                },
            },
            "pattern_matcher": {
                "patterns": [
                    {
                        "name": "PROPOSAL",
                        "required_features": [
                            "has_payment_terms",
                            "has_delivery_terms",
                        ],
                        "optional_features": ["has_dollar_amounts"],
                        "section_patterns": ["executive summary", "scope of work"],
                        "content_patterns": ["proposal", "project", "phases"],
                    }
                ]
            },
            "ml_based": {
                "model": {
                    "confidence_threshold": 0.7,
                    "feature_weights": {
                        "section_density": 0.3,
                        "table_density": 0.2,
                        "avg_section_length": 0.2,
                        "metadata_completeness": 0.3,
                    },
                }
            },
        },
    }
    return config


@pytest.fixture
def test_document() -> Dict[str, Any]:
    """Create a test document."""
    return {
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


@pytest.fixture
def test_document_path(test_document: Dict[str, Any], tmp_path: Path) -> str:
    """Create a temporary test document file."""
    doc_path = tmp_path / "test_proposal.json"
    with open(doc_path, "w") as f:
        json.dump(test_document, f)
    return str(doc_path)


def test_end_to_end_classification(
    test_config: Dict[str, Any], test_document_path: str, test_document: Dict[str, Any]
):
    """
    Test the complete classification flow from document input to final result.

    This test verifies:
    1. Pipeline initialization
    2. Document processing
    3. Feature extraction
    4. Classification by each classifier
    5. Ensemble combination
    6. Final result validation
    """
    # Initialize pipeline
    pipeline = Pipeline(test_config)
    assert pipeline is not None, "Pipeline should be initialized"

    # Process document
    result = pipeline.run(test_document_path)
    assert result is not None, "Pipeline should return a result"

    # Verify classification result
    assert result["document_type"] == "PROPOSAL", (
        "Document should be classified as PROPOSAL"
    )
    assert result["confidence"] >= 0.45, "Confidence should meet minimum threshold"
    assert result["schema_pattern"] == "standard_proposal", (
        "Should use standard proposal schema"
    )

    # Verify key features were detected
    key_features = result.get("key_features", [])
    assert "has_payment_terms" in key_features, "Should detect payment terms"
    assert "has_delivery_terms" in key_features, "Should detect delivery terms"
    assert "has_dollar_amounts" in key_features, "Should detect dollar amounts"

    # Verify all classifiers were used
    classifiers_used = result.get("classifiers", [])
    assert "rule_based" in classifiers_used, "Rule-based classifier should be used"
    assert "pattern_matcher" in classifiers_used, "Pattern matcher should be used"
    assert "ml_based" in classifiers_used, "ML classifier should be used"


def test_classifier_individual_results(
    test_config: Dict[str, Any], test_document: Dict[str, Any]
):
    """
    Test each classifier's individual results before ensemble combination.
    """
    # Initialize classifier directly
    classifier = DocumentClassifier(config=test_config)

    # Extract features
    features = classifier._extract_features(test_document)

    # Test rule-based classifier
    rule_based = classifier.factory.create_classifier("rule_based")
    rule_result = rule_based.classify(test_document, features)
    assert rule_result["document_type"] == "PROPOSAL"
    assert rule_result["confidence"] >= 0.4

    # Test pattern matcher
    pattern_matcher = classifier.factory.create_classifier("pattern_matcher")
    pattern_result = pattern_matcher.classify(test_document, features)
    assert pattern_result["document_type"] == "PROPOSAL"
    assert pattern_result["confidence"] >= 0.5

    # Test ML classifier
    ml_classifier = classifier.factory.create_classifier("ml_based")
    ml_result = ml_classifier.classify(test_document, features)
    assert ml_result["confidence"] > 0


def test_ensemble_combination(
    test_config: Dict[str, Any], test_document: Dict[str, Any]
):
    """
    Test the ensemble's combination of classifier results.
    """
    classifier = DocumentClassifier(config=test_config)

    # Get classification results
    result = classifier.classify(test_document)

    # Verify ensemble weighting
    assert result["confidence"] > 0.45, "Combined confidence should meet threshold"
    assert result["document_type"] == "PROPOSAL", (
        "Ensemble should agree on PROPOSAL type"
    )


def test_error_handling(test_config: Dict[str, Any], tmp_path: Path):
    """
    Test error handling with invalid input.
    """
    pipeline = Pipeline(test_config)

    # Test with empty document
    empty_doc_path = tmp_path / "empty.json"
    with open(empty_doc_path, "w") as f:
        json.dump({}, f)
    empty_result = pipeline.run(str(empty_doc_path))
    assert empty_result["document_type"] == "UNKNOWN"
    assert empty_result["confidence"] == 0.0

    # Test with missing required fields
    invalid_doc_path = tmp_path / "invalid.json"
    with open(invalid_doc_path, "w") as f:
        json.dump({"metadata": {}, "content": []}, f)
    invalid_result = pipeline.run(str(invalid_doc_path))
    assert invalid_result["confidence"] < 0.45  # Should have low confidence


def test_feature_extraction(test_config: Dict[str, Any], test_document: Dict[str, Any]):
    """
    Test the feature extraction process.
    """
    classifier = DocumentClassifier(config=test_config)
    features = classifier._extract_features(test_document)

    # Verify extracted features
    assert features["has_payment_terms"] is True
    assert features["has_delivery_terms"] is True
    assert features["has_dollar_amounts"] is True
    assert features["section_count"] == 4
    assert features["table_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
