"""
ML-based document classifier.

This module provides a machine learning based approach to document classification.
This is an example implementation showing how to extend the classification system
with new classifier types.
"""

from typing import Any, Dict, List, Optional

import numpy as np

from utils.pipeline.strategies.classifier_strategy import BaseClassifier


class MLBasedClassifier(BaseClassifier):
    """
    Classifies documents using machine learning.

    This classifier uses a pre-trained model to identify document types
    based on their features and content. This is an example implementation
    showing how to integrate ML models into the classification system.
    """

    def __init__(self, *, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ML-based classifier.

        Args:
            config: Configuration dictionary for the classifier
        """
        super().__init__(config=config)

        # Load ML model configuration
        self.model_config = self.config.get("model", {})
        self.confidence_threshold = self.model_config.get("confidence_threshold", 0.7)
        self.feature_weights = self.model_config.get("feature_weights", {})

        # In a real implementation, you would load your trained model here
        # self.model = load_model(self.model_config.get("model_path"))

        # For this example, we'll use a simple feature-based approach
        self.document_types = [
            "PROPOSAL",
            "QUOTATION",
            "SPECIFICATION",
            "INVOICE",
            "TERMS_AND_CONDITIONS",
        ]

    def classify(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify the document using ML-based approach.

        Args:
            document_data: Processed document data
            features: Extracted features from the document

        Returns:
            Classification result with document type, confidence, and schema pattern
        """
        try:
            # Extract ML features
            ml_features = self._extract_ml_features(document_data, features)

            # In a real implementation, you would use your model to predict
            # prediction = self.model.predict(ml_features)

            # For this example, we'll use a simple scoring mechanism
            scores = self._calculate_scores(ml_features)

            # Normalize scores to [0,1] range
            scores = scores / np.sum(scores) if np.sum(scores) > 0 else scores

            # Get best matching type
            best_type_idx = np.argmax(scores)
            confidence = float(scores[best_type_idx])  # Convert from numpy float
            doc_type = self.document_types[best_type_idx]

            if confidence < self.confidence_threshold or np.sum(scores) == 0:
                return {
                    "document_type": "UNKNOWN",
                    "confidence": confidence,
                    "schema_pattern": "unknown",
                    "key_features": list(ml_features.keys()),
                }

            return {
                "document_type": doc_type,
                "confidence": confidence,
                "schema_pattern": f"ml_{doc_type.lower()}",
                "key_features": list(ml_features.keys()),
            }

        except Exception as e:
            self.logger.error(f"Error in ML classification: {str(e)}", exc_info=True)
            return {
                "document_type": "UNKNOWN",
                "confidence": 0.0,
                "schema_pattern": "unknown",
                "key_features": [],
            }

    def get_supported_types(self) -> List[str]:
        """
        Get the document types supported by this classifier.

        Returns:
            List of supported document type identifiers
        """
        return self.document_types

    def _extract_ml_features(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Extract features for ML classification.

        Args:
            document_data: Processed document data
            features: Base features from document

        Returns:
            Dictionary of ML-specific features
        """
        ml_features = {}

        # Structure features
        ml_features["section_density"] = features["section_count"] / max(
            len(
                " ".join(
                    [s.get("content", "") for s in document_data.get("content", [])]
                )
            ),
            1,
        )
        ml_features["table_density"] = features["table_count"] / max(
            features["section_count"], 1
        )

        # Content features
        all_content = " ".join(
            [s.get("content", "") for s in document_data.get("content", [])]
        )
        ml_features["avg_section_length"] = len(all_content) / max(
            features["section_count"], 1
        )

        # Metadata completeness
        metadata = document_data.get("metadata", {})
        ml_features["metadata_completeness"] = (
            len(metadata) / 10
        )  # Normalize by expected fields

        # Feature presence
        ml_features["has_payment_terms"] = float(
            features.get("has_payment_terms", False)
        )
        ml_features["has_delivery_terms"] = float(
            features.get("has_delivery_terms", False)
        )
        ml_features["has_dollar_amounts"] = float(
            features.get("has_dollar_amounts", False)
        )
        ml_features["has_quantities"] = float(features.get("has_quantities", False))

        return ml_features

    def _calculate_scores(self, features: Dict[str, float]) -> np.ndarray:
        """
        Calculate classification scores for each document type.

        Args:
            features: Extracted ML features

        Returns:
            Array of scores for each document type
        """
        scores = np.zeros(len(self.document_types))

        # Example scoring logic (in a real implementation, this would use a trained model)
        for i, doc_type in enumerate(self.document_types):
            if doc_type == "PROPOSAL":
                scores[i] = (
                    features["has_payment_terms"] * 0.3
                    + features["has_delivery_terms"] * 0.3
                    + features["section_density"] * 0.2
                    + features["metadata_completeness"] * 0.2
                )
            elif doc_type == "QUOTATION":
                scores[i] = (
                    features["has_dollar_amounts"] * 0.4
                    + features["has_quantities"] * 0.3
                    + features["table_density"] * 0.3
                )
            elif doc_type == "SPECIFICATION":
                scores[i] = (
                    features["section_density"] * 0.4
                    + features["avg_section_length"] * 0.3
                    + features["metadata_completeness"] * 0.3
                )
            elif doc_type == "INVOICE":
                scores[i] = (
                    features["has_dollar_amounts"] * 0.5
                    + features["table_density"] * 0.3
                    + features["metadata_completeness"] * 0.2
                )
            elif doc_type == "TERMS_AND_CONDITIONS":
                scores[i] = (
                    features["section_density"] * 0.3
                    + features["avg_section_length"] * 0.4
                    + features["metadata_completeness"] * 0.3
                )

        return scores
