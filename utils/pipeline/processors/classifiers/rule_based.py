"""
Rule-based document classifier.

This module provides a rule-based approach to document classification.
"""

from typing import Any, Dict, List, Optional

from utils.pipeline.strategies.classifier_strategy import BaseClassifier


class RuleBasedClassifier(BaseClassifier):
    """
    Classifies documents using a rule-based approach.

    This classifier uses a set of predefined rules to identify document types
    based on their structure, content, and metadata.
    """

    def __init__(self, *, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the rule-based classifier.

        Args:
            config: Configuration dictionary for the classifier
        """
        super().__init__(config=config)

        # Get classification rules from config
        self.classification_config = self.config.get("classification", {})
        self.rules_config = self.classification_config.get("rules", {})
        self.default_threshold = self.classification_config.get(
            "default_threshold", 0.3
        )
        self.filename_patterns = self.classification_config.get("filename_patterns", {})

    def classify(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify the document using rule-based approach.

        Args:
            document_data: Processed document data
            features: Extracted features from the document

        Returns:
            Classification result with document type, confidence, and schema pattern
        """
        # Apply configured rules
        best_match = self._get_best_match(document_data, features)

        # Only use generic classification if confidence is very low
        if best_match[0] == "UNKNOWN" or best_match[1] < 0.2:
            # If no specific type matched or confidence is very low, try to determine a generic type
            self.logger.info("Using generic classification due to low confidence")
            return self._classify_generic(document_data, features)

        return {
            "document_type": best_match[0],
            "confidence": best_match[1],
            "schema_pattern": best_match[2],
            "key_features": best_match[3],
        }

    def get_supported_types(self) -> List[str]:
        """
        Get the document types supported by this classifier.

        Returns:
            List of supported document type identifiers
        """
        return list(self.rules_config.keys())

    def _get_best_match(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> tuple[str, float, str, List[str]]:
        """
        Apply all configured rules and get the best matching document type.

        Args:
            document_data: Processed document data
            features: Extracted features from the document

        Returns:
            Tuple of (document_type, confidence, schema_pattern, key_features)
        """
        best_match = ("UNKNOWN", 0.0, "unknown", [])

        # Apply each configured rule
        for doc_type, rule in self.rules_config.items():
            confidence = 0.0
            key_features = []

            # Check metadata for keywords
            metadata = document_data.get("metadata", {})
            metadata_text = " ".join([str(v).lower() for v in metadata.values()])

            # Check title keywords in metadata
            title_keywords = rule.get("title_keywords", [])
            if title_keywords:
                metadata_matches = sum(
                    1 for keyword in title_keywords if keyword.lower() in metadata_text
                )
                if metadata_matches > 0:
                    title_weight = rule.get("weights", {}).get("title_match", 0.4)
                    metadata_confidence = title_weight * (
                        metadata_matches / len(title_keywords)
                    )
                    confidence += metadata_confidence
                    key_features.append("metadata_match")

            # Check title keywords in section titles
            section_titles = features.get("section_titles", [])
            if title_keywords and section_titles:
                matches = sum(
                    1
                    for keyword in title_keywords
                    if any(keyword.lower() in title.lower() for title in section_titles)
                )
                if matches > 0:
                    title_weight = rule.get("weights", {}).get("title_match", 0.4)
                    confidence += title_weight * (matches / len(title_keywords))
                    key_features.append("title_match")

            # Check content keywords
            content = " ".join(
                [
                    section.get("content", "")
                    for section in document_data.get("content", [])
                ]
            )
            content_keywords = rule.get("content_keywords", [])
            if content_keywords:
                matches = sum(
                    1
                    for keyword in content_keywords
                    if keyword.lower() in content.lower()
                )
                if matches > 0:
                    content_weight = rule.get("weights", {}).get("content_match", 0.3)
                    confidence += content_weight * (matches / len(content_keywords))
                    key_features.append("content_match")

            # Check patterns
            patterns = rule.get("patterns", [])
            if patterns:
                matches = sum(
                    1 for pattern in patterns if pattern.lower() in content.lower()
                )
                if matches > 0:
                    pattern_weight = rule.get("weights", {}).get("pattern_match", 0.3)
                    confidence += pattern_weight * (matches / len(patterns))
                    key_features.append("pattern_match")

            # Check if confidence exceeds threshold
            threshold = rule.get("threshold", 0.5)
            if confidence > threshold and confidence > best_match[1]:
                schema_pattern = rule.get("schema_pattern", "standard")
                best_match = (doc_type, confidence, schema_pattern, key_features)

        return best_match

    def _classify_generic(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify document into generic categories when specific types don't match.

        Args:
            document_data: Processed document data
            features: Extracted features from the document

        Returns:
            Classification result with generic document type
        """
        # Check if it's a form
        if features.get("table_count", 0) > 3:
            return {
                "document_type": "FORM",
                "confidence": 0.6,
                "schema_pattern": "tabular_form",
                "key_features": ["multiple_tables", "structured_layout"],
            }

        # Check if it's a report
        if features.get("section_count", 0) > 10:
            return {
                "document_type": "REPORT",
                "confidence": 0.5,
                "schema_pattern": "sectioned_document",
                "key_features": ["multiple_sections", "hierarchical_structure"],
            }

        # Default to generic document
        return {
            "document_type": "GENERIC_DOCUMENT",
            "confidence": self.default_threshold,
            "schema_pattern": "unknown",
            "key_features": [],
        }
