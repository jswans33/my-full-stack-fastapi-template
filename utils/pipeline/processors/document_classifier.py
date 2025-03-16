"""
Document classifier module.

This module provides functionality for classifying documents based on their structure and content.
"""

from typing import Any, Dict, List, Optional

from utils.pipeline.strategies.classifier_factory import ClassifierFactory
from utils.pipeline.strategies.ensemble_manager import EnsembleManager
from utils.pipeline.utils.logging import get_logger


class DocumentClassifier:
    """
    Classifies documents based on their structure and content patterns.

    This classifier uses multiple classification strategies and ensemble methods
    to identify document types such as proposals, quotations, specifications, etc.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the document classifier.

        Args:
            config: Configuration dictionary for the classifier
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Initialize factory and ensemble manager
        self.factory = ClassifierFactory()
        self.ensemble_manager = EnsembleManager(self.config.get("ensemble", {}))

        # Register default classifiers
        self._register_default_classifiers()

    def _register_default_classifiers(self) -> None:
        """Register the default set of classifiers."""
        # Import default classifiers
        from utils.pipeline.processors.classifiers.ml_based import MLBasedClassifier
        from utils.pipeline.processors.classifiers.pattern_matcher import (
            PatternMatcherClassifier,
        )
        from utils.pipeline.processors.classifiers.rule_based import RuleBasedClassifier

        # Register with default configs from main config
        classifier_configs = self.config.get("classifiers", {})

        self.factory.register_classifier(
            "rule_based",
            RuleBasedClassifier,
            classifier_configs.get("rule_based", {}),
        )

        self.factory.register_classifier(
            "pattern_matcher",
            PatternMatcherClassifier,
            classifier_configs.get("pattern_matcher", {}),
        )

        self.factory.register_classifier(
            "ml_based",
            MLBasedClassifier,
            classifier_configs.get("ml_based", {}),
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
            # Extract common features
            features = self._extract_features(document_data)

            # Get all registered classifiers
            classifier_info = self.factory.get_available_classifiers()

            # Collect results from all classifiers
            classification_results = []
            for info in classifier_info:
                try:
                    classifier = self.factory.create_classifier(info["name"])
                    result = classifier.classify(document_data, features)

                    # Add classifier name to result
                    result["classifier_name"] = info["name"]
                    classification_results.append(result)

                    self.logger.info(
                        f"Classifier {info['name']} result: {result['document_type']} "
                        f"(confidence: {result['confidence']})"
                    )
                except Exception as e:
                    self.logger.error(
                        f"Error using classifier {info['name']}: {str(e)}",
                        exc_info=True,
                    )

            # Combine results using ensemble manager
            final_result = self.ensemble_manager.combine_results(classification_results)

            self.logger.info(
                f"Final classification: {final_result['document_type']} "
                f"(confidence: {final_result['confidence']})"
            )
            return final_result

        except Exception as e:
            self.logger.error(f"Error classifying document: {str(e)}", exc_info=True)
            # Return unknown classification on error
            return {
                "document_type": "UNKNOWN",
                "confidence": 0.0,
                "schema_pattern": "unknown",
                "key_features": [],
                "classifiers": [],
                "error": str(e),
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

        # Check for dollar amounts in content and tables
        has_dollar_in_content = "$" in all_content

        # Check tables for dollar amounts
        has_dollar_in_tables = False
        tables = document_data.get("tables", [])
        for table in tables:
            for row in table.get("rows", []):
                for cell in row:
                    if isinstance(cell, str) and "$" in cell:
                        has_dollar_in_tables = True
                        break

        features["has_dollar_amounts"] = has_dollar_in_content or has_dollar_in_tables
        features["has_quantities"] = any(word.isdigit() for word in all_content.split())

        # Check for tables
        tables = document_data.get("tables", [])
        features["table_count"] = len(tables)

        return features

    def add_classifier(
        self, name: str, classifier_class: Any, config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a new classifier to the system.

        Args:
            name: Unique identifier for the classifier
            classifier_class: The classifier class to add
            config: Optional configuration for the classifier
        """
        self.factory.register_classifier(name, classifier_class, config)
        self.logger.info(f"Added classifier: {name}")

    def remove_classifier(self, name: str) -> None:
        """
        Remove a classifier from the system.

        Args:
            name: Name of the classifier to remove
        """
        self.factory.remove_classifier(name)
        self.logger.info(f"Removed classifier: {name}")

    def update_classifier_config(self, name: str, config: Dict[str, Any]) -> None:
        """
        Update the configuration for a classifier.

        Args:
            name: Name of the classifier to update
            config: New configuration dictionary
        """
        self.factory.update_classifier_config(name, config)
        self.logger.info(f"Updated configuration for classifier: {name}")

    def get_available_classifiers(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered classifiers.

        Returns:
            List of classifier information dictionaries
        """
        return self.factory.get_available_classifiers()
