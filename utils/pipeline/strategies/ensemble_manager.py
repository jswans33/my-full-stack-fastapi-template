"""
Ensemble manager for combining results from multiple classifiers.

This module provides functionality for weighted voting and result aggregation
from multiple document classifiers.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional

from utils.pipeline.utils.logging import get_logger


class EnsembleManager:
    """
    Manages ensemble classification by combining results from multiple classifiers.

    Features:
    - Weighted voting system
    - Multiple voting methods (weighted average, majority, consensus)
    - Feature aggregation
    - Confidence calculation
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ensemble manager.

        Args:
            config: Configuration dictionary for ensemble behavior
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Set default configuration
        self.voting_method = self.config.get("voting_method", "weighted_average")
        self.minimum_confidence = self.config.get("minimum_confidence", 0.65)
        self.classifier_weights = self.config.get("classifier_weights", {})
        self.default_weight = self.config.get("default_weight", 0.3)

    def combine_results(self, classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine classification results using the configured voting method.

        Args:
            classifications: List of classification results from different classifiers

        Returns:
            Combined classification result
        """
        if not classifications:
            return {
                "document_type": "UNKNOWN",
                "confidence": 0.0,
                "schema_pattern": "unknown",
                "key_features": [],
                "classifiers": [],
            }

        # Use appropriate voting method
        if self.voting_method == "weighted_average":
            return self._weighted_average_vote(classifications)
        elif self.voting_method == "majority":
            return self._majority_vote(classifications)
        elif self.voting_method == "consensus":
            return self._consensus_vote(classifications)
        else:
            self.logger.warning(
                f"Unknown voting method: {self.voting_method}, using weighted average"
            )
            return self._weighted_average_vote(classifications)

    def _weighted_average_vote(
        self, classifications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Combine results using weighted average voting.

        Args:
            classifications: List of classification results

        Returns:
            Combined classification result
        """
        # Track votes and confidences for each document type
        type_votes = defaultdict(float)
        type_features = defaultdict(set)
        type_schemas = defaultdict(set)
        classifiers_used = []

        # Calculate weighted votes
        total_weight = 0
        for result in classifications:
            doc_type = result["document_type"]
            confidence = result["confidence"]
            classifier_name = result.get("classifier_name", "unknown")

            # Get weight for this classifier
            weight = self.classifier_weights.get(classifier_name, self.default_weight)
            total_weight += weight

            # Add weighted vote
            type_votes[doc_type] += confidence * weight

            # Collect features and schema patterns
            type_features[doc_type].update(result.get("key_features", []))
            type_schemas[doc_type].add(result.get("schema_pattern", "unknown"))
            classifiers_used.append(classifier_name)

        if not total_weight:
            return {
                "document_type": "UNKNOWN",
                "confidence": 0.0,
                "schema_pattern": "unknown",
                "key_features": [],
                "classifiers": classifiers_used,
            }

        # Normalize votes and find winner
        best_type = max(type_votes.items(), key=lambda x: x[1])
        normalized_confidence = best_type[1] / total_weight

        # Only use type if confidence meets minimum threshold
        if normalized_confidence < self.minimum_confidence:
            return {
                "document_type": "UNKNOWN",
                "confidence": normalized_confidence,
                "schema_pattern": "unknown",
                "key_features": [],
                "classifiers": classifiers_used,
            }

        return {
            "document_type": best_type[0],
            "confidence": normalized_confidence,
            "schema_pattern": list(type_schemas[best_type[0]])[
                0
            ],  # Use first schema pattern
            "key_features": list(type_features[best_type[0]]),
            "classifiers": classifiers_used,
        }

    def _majority_vote(self, classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine results using simple majority voting.

        Args:
            classifications: List of classification results

        Returns:
            Combined classification result
        """
        # Count votes for each document type
        type_votes = defaultdict(int)
        type_confidences = defaultdict(list)
        type_features = defaultdict(set)
        type_schemas = defaultdict(set)
        classifiers_used = []

        for result in classifications:
            doc_type = result["document_type"]
            confidence = result["confidence"]
            classifier_name = result.get("classifier_name", "unknown")

            type_votes[doc_type] += 1
            type_confidences[doc_type].append(confidence)
            type_features[doc_type].update(result.get("key_features", []))
            type_schemas[doc_type].add(result.get("schema_pattern", "unknown"))
            classifiers_used.append(classifier_name)

        # Find type with most votes
        max_votes = max(type_votes.values())
        winners = [t for t, v in type_votes.items() if v == max_votes]

        if len(winners) > 1:
            # Break tie using average confidence
            winner = max(
                winners,
                key=lambda t: sum(type_confidences[t]) / len(type_confidences[t]),
            )
        else:
            winner = winners[0]

        # Calculate final confidence
        confidence = sum(type_confidences[winner]) / len(type_confidences[winner])

        if confidence < self.minimum_confidence:
            return {
                "document_type": "UNKNOWN",
                "confidence": confidence,
                "schema_pattern": "unknown",
                "key_features": [],
                "classifiers": classifiers_used,
            }

        return {
            "document_type": winner,
            "confidence": confidence,
            "schema_pattern": list(type_schemas[winner])[0],  # Use first schema pattern
            "key_features": list(type_features[winner]),
            "classifiers": classifiers_used,
        }

    def _consensus_vote(self, classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine results requiring full consensus.

        Args:
            classifications: List of classification results

        Returns:
            Combined classification result
        """
        # Check if all classifiers agree
        doc_types = {c["document_type"] for c in classifications}
        if len(doc_types) != 1:
            return {
                "document_type": "UNKNOWN",
                "confidence": 0.0,
                "schema_pattern": "unknown",
                "key_features": [],
                "classifiers": [
                    c.get("classifier_name", "unknown") for c in classifications
                ],
            }

        # Get agreed type
        doc_type = doc_types.pop()

        # Combine features and calculate average confidence
        all_features = set()
        total_confidence = 0
        schema_patterns = set()
        classifiers_used = []

        for result in classifications:
            all_features.update(result.get("key_features", []))
            total_confidence += result["confidence"]
            schema_patterns.add(result.get("schema_pattern", "unknown"))
            classifiers_used.append(result.get("classifier_name", "unknown"))

        confidence = total_confidence / len(classifications)

        if confidence < self.minimum_confidence:
            return {
                "document_type": "UNKNOWN",
                "confidence": confidence,
                "schema_pattern": "unknown",
                "key_features": [],
                "classifiers": classifiers_used,
            }

        return {
            "document_type": doc_type,
            "confidence": confidence,
            "schema_pattern": list(schema_patterns)[0],  # Use first schema pattern
            "key_features": list(all_features),
            "classifiers": classifiers_used,
        }
