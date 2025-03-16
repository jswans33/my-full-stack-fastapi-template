"""
Pattern matcher document classifier.

This module provides a pattern matching approach to document classification.
"""

from typing import Any, Dict, List, Optional

from utils.pipeline.strategies.classifier_strategy import BaseClassifier


class PatternMatcherClassifier(BaseClassifier):
    """
    Classifies documents using pattern matching.

    This classifier uses predefined patterns to identify document types
    based on their structure, content, and metadata.
    """

    def __init__(self, *, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the pattern matcher classifier.

        Args:
            config: Configuration dictionary for the classifier
        """
        super().__init__(config=config)

        # Define document patterns
        self.patterns = self._load_patterns()

    def classify(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify the document using pattern matching.

        Args:
            document_data: Processed document data
            features: Extracted features from the document

        Returns:
            Classification result with document type, confidence, and schema pattern
        """
        self.logger.info("Classifying document using pattern matching")

        try:
            # Find best matching pattern
            best_match = self._find_best_match(document_data, features)

            self.logger.info(
                f"Document classified as: {best_match['document_type']} with confidence: {best_match['confidence']}"
            )
            return best_match

        except Exception as e:
            self.logger.error(f"Error classifying document: {str(e)}", exc_info=True)
            # Return unknown classification on error
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
        return [pattern["name"] for pattern in self.patterns]

    def _load_patterns(self) -> List[Dict[str, Any]]:
        """
        Load document patterns from configuration or use defaults.

        Returns:
            List of document patterns
        """
        # Use patterns from config if available
        if "patterns" in self.config:
            return self.config["patterns"]

        # Default patterns
        return [
            {
                "name": "PROPOSAL",
                "schema_pattern": "standard_proposal",
                "required_features": ["has_payment_terms", "has_delivery_terms"],
                "optional_features": ["proposal_in_title", "has_regarding_section"],
                "section_patterns": [
                    "proposal",
                    "regarding",
                    "company",
                    "payment",
                    "delivery",
                ],
                "content_patterns": ["proposal", "offer", "proposed", "scope of work"],
            },
            {
                "name": "QUOTATION",
                "schema_pattern": "standard_quotation",
                "required_features": ["has_dollar_amounts"],
                "optional_features": ["has_subtotal", "has_total", "has_quantities"],
                "section_patterns": [
                    "quote",
                    "quotation",
                    "estimate",
                    "pricing",
                    "subtotal",
                    "total",
                ],
                "content_patterns": [
                    "quote",
                    "price",
                    "cost",
                    "amount",
                    "total",
                    "subtotal",
                    "$",
                ],
            },
            {
                "name": "SPECIFICATION",
                "schema_pattern": "technical_specification",
                "required_features": ["has_technical_terms", "has_measurements"],
                "optional_features": ["spec_in_title"],
                "section_patterns": [
                    "specification",
                    "spec",
                    "technical",
                    "requirements",
                    "dimensions",
                ],
                "content_patterns": [
                    "specification",
                    "technical",
                    "dimensions",
                    "performance",
                    "material",
                ],
            },
            {
                "name": "INVOICE",
                "schema_pattern": "standard_invoice",
                "required_features": ["has_dollar_amounts"],
                "optional_features": ["has_subtotal", "has_total", "invoice_in_title"],
                "section_patterns": [
                    "invoice",
                    "bill",
                    "receipt",
                    "payment",
                    "due date",
                ],
                "content_patterns": [
                    "invoice",
                    "bill",
                    "amount due",
                    "payment",
                    "total",
                    "$",
                ],
            },
            {
                "name": "TERMS_AND_CONDITIONS",
                "schema_pattern": "legal_terms",
                "required_features": ["has_legal_language"],
                "optional_features": ["has_caps_sections", "terms_in_title"],
                "section_patterns": [
                    "terms",
                    "conditions",
                    "agreement",
                    "contract",
                    "warranty",
                    "liability",
                ],
                "content_patterns": [
                    "shall",
                    "herein",
                    "pursuant",
                    "liability",
                    "warranty",
                    "indemnify",
                ],
            },
        ]

    def _find_best_match(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Find the best matching pattern for the document.

        Args:
            document_data: Processed document data
            features: Extracted features from the document

        Returns:
            Classification result with document type, confidence, and schema pattern
        """
        best_match = {
            "document_type": "UNKNOWN",
            "confidence": 0.0,
            "schema_pattern": "unknown",
            "key_features": [],
        }

        # Extract content for pattern matching
        content = document_data.get("content", [])
        all_content = " ".join(
            [section.get("content", "").lower() for section in content]
        )
        section_titles = features.get("section_titles", [])

        # Check each pattern
        for pattern in self.patterns:
            confidence = 0.0
            matched_features = []

            # Check required features
            required_count = len(pattern["required_features"])
            matched_required = 0

            for feature in pattern["required_features"]:
                if features.get(feature, False):
                    matched_required += 1
                    matched_features.append(feature)

            # If not all required features match, skip this pattern
            if matched_required < required_count:
                continue

            # Add confidence for required features
            confidence += 0.5 * (matched_required / max(1, required_count))

            # Check optional features
            optional_count = len(pattern["optional_features"])
            matched_optional = 0

            for feature in pattern["optional_features"]:
                if features.get(feature, False):
                    matched_optional += 1
                    matched_features.append(feature)

            # Add confidence for optional features
            if optional_count > 0:
                confidence += 0.3 * (matched_optional / optional_count)

            # Check section patterns
            section_matches = 0
            for section_pattern in pattern["section_patterns"]:
                if any(section_pattern in title for title in section_titles):
                    section_matches += 1
                    matched_features.append(f"section_contains_{section_pattern}")

            # Add confidence for section patterns
            if len(pattern["section_patterns"]) > 0:
                confidence += 0.1 * (section_matches / len(pattern["section_patterns"]))

            # Check content patterns
            content_matches = 0
            for content_pattern in pattern["content_patterns"]:
                if content_pattern in all_content:
                    content_matches += 1
                    matched_features.append(f"content_contains_{content_pattern}")

            # Add confidence for content patterns
            if len(pattern["content_patterns"]) > 0:
                confidence += 0.1 * (content_matches / len(pattern["content_patterns"]))

            # Update best match if this pattern has higher confidence
            if confidence > best_match["confidence"]:
                best_match = {
                    "document_type": pattern["name"],
                    "confidence": min(1.0, confidence),  # Cap at 1.0
                    "schema_pattern": pattern["schema_pattern"],
                    "key_features": matched_features,
                }

        return best_match
