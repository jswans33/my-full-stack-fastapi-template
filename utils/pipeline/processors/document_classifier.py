"""
Document classifier module.

This module provides functionality for classifying documents based on their structure and content.
"""

from typing import Any, Dict, Optional

from utils.pipeline.utils.logging import get_logger


class DocumentClassifier:
    """
    Classifies documents based on their structure and content patterns.

    This classifier analyzes the document structure to identify patterns that match
    known document types such as proposals, quotations, specifications, etc.
    """

    def __init__(
        self,
        classifier_type: str = "rule_based",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the document classifier.

        Args:
            classifier_type: Type of classifier to use (rule_based, pattern_matcher, etc.)
            config: Configuration dictionary for the classifier
        """
        self.classifier_type = classifier_type
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Initialize classifier strategy based on type
        if classifier_type == "rule_based":
            from utils.pipeline.processors.classifiers.rule_based import (
                RuleBasedClassifier,
            )

            self.classifier_strategy = RuleBasedClassifier(self.config)
        elif classifier_type == "pattern_matcher":
            from utils.pipeline.processors.classifiers.pattern_matcher import (
                PatternMatcherClassifier,
            )

            self.classifier_strategy = PatternMatcherClassifier(self.config)
        else:
            # Default to rule-based
            from utils.pipeline.processors.classifiers.rule_based import (
                RuleBasedClassifier,
            )

            self.classifier_strategy = RuleBasedClassifier(self.config)
            self.logger.warning(
                f"Unknown classifier type: {classifier_type}, using rule_based"
            )

    def classify(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify the document based on its structure and content.

        Args:
            document_data: Processed document data

        Returns:
            Classification result with document type, confidence, and schema pattern
        """
        self.logger.info("Classifying document")

        try:
            # Extract features from document
            features = self._extract_features(document_data)

            # Classify document using strategy
            classification = self.classifier_strategy.classify(document_data, features)

            self.logger.info(
                f"Document classified as: {classification['document_type']} with confidence: {classification['confidence']}"
            )
            return classification

        except Exception as e:
            self.logger.error(f"Error classifying document: {str(e)}", exc_info=True)
            # Return unknown classification on error
            return {
                "document_type": "UNKNOWN",
                "confidence": 0.0,
                "schema_pattern": "unknown",
                "key_features": [],
            }

    def _extract_features(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from document data for classification.

        Args:
            document_data: Processed document data

        Returns:
            Dictionary of extracted features
        """
        features = {}

        # Extract metadata features
        metadata = document_data.get("metadata", {})
        features["has_title"] = bool(metadata.get("title"))
        features["has_author"] = bool(metadata.get("author"))
        features["creator"] = metadata.get("creator", "")
        features["producer"] = metadata.get("producer", "")

        # Extract content features
        content = document_data.get("content", [])
        features["section_count"] = len(content)

        # Extract section titles
        section_titles = [
            section.get("title", "").lower()
            for section in content
            if section.get("title")
        ]
        features["section_titles"] = section_titles

        # Check for common document patterns
        features["has_payment_terms"] = any(
            "payment" in title for title in section_titles
        )
        features["has_delivery_terms"] = any(
            "delivery" in title for title in section_titles
        )
        features["has_subtotal"] = any("subtotal" in title for title in section_titles)
        features["has_total"] = any("total" in title for title in section_titles)

        # Check for pricing patterns in content
        all_content = " ".join([section.get("content", "") for section in content])
        features["has_dollar_amounts"] = "$" in all_content
        features["has_quantities"] = any(word.isdigit() for word in all_content.split())

        # Check for tables
        tables = document_data.get("tables", [])
        features["table_count"] = len(tables)

        return features
