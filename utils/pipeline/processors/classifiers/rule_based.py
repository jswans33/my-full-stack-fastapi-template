"""
Rule-based document classifier.

This module provides a rule-based approach to document classification.
"""

from typing import Any, Dict, List, Optional, Tuple

from utils.pipeline.utils.logging import get_logger


class RuleBasedClassifier:
    """
    Classifies documents using a rule-based approach.

    This classifier uses a set of predefined rules to identify document types
    based on their structure, content, and metadata.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the rule-based classifier.

        Args:
            config: Configuration dictionary for the classifier
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Define document type rules
        self.rules = [
            self._is_proposal,
            self._is_quotation,
            self._is_specification,
            self._is_invoice,
            self._is_terms_and_conditions,
        ]

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
        # Apply each rule and get the best match
        best_match = self._get_best_match(document_data, features)

        if best_match[0] == "UNKNOWN":
            # If no specific type matched, try to determine a generic type
            return self._classify_generic(document_data, features)

        return {
            "document_type": best_match[0],
            "confidence": best_match[1],
            "schema_pattern": best_match[2],
            "key_features": best_match[3],
        }

    def _get_best_match(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Tuple[str, float, str, List[str]]:
        """
        Apply all rules and get the best matching document type.

        Args:
            document_data: Processed document data
            features: Extracted features from the document

        Returns:
            Tuple of (document_type, confidence, schema_pattern, key_features)
        """
        best_match = ("UNKNOWN", 0.0, "unknown", [])

        for rule in self.rules:
            result = rule(document_data, features)
            if result[1] > best_match[1]:
                best_match = result

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
            "confidence": 0.3,
            "schema_pattern": "unknown",
            "key_features": [],
        }

    def _is_proposal(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Tuple[str, float, str, List[str]]:
        """Check if document is a proposal."""
        confidence = 0.0
        key_features = []

        # Check for proposal indicators in section titles
        section_titles = features.get("section_titles", [])
        if any("proposal" in title for title in section_titles):
            confidence += 0.4
            key_features.append("proposal_in_title")

        # Check for common proposal sections
        if features.get("has_payment_terms", False):
            confidence += 0.2
            key_features.append("has_payment_terms")

        if features.get("has_delivery_terms", False):
            confidence += 0.2
            key_features.append("has_delivery_terms")

        # Check for "regarding" section which is common in proposals
        if any("regarding" in title for title in section_titles):
            confidence += 0.2
            key_features.append("has_regarding_section")

        # Check for company information
        if any("company" in title for title in section_titles):
            confidence += 0.1
            key_features.append("has_company_section")

        # Determine schema pattern
        schema_pattern = "standard_proposal"
        if "has_payment_terms" in key_features and "has_delivery_terms" in key_features:
            schema_pattern = "detailed_proposal"

        return ("PROPOSAL", confidence, schema_pattern, key_features)

    def _is_quotation(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Tuple[str, float, str, List[str]]:
        """Check if document is a quotation."""
        confidence = 0.0
        key_features = []

        # Check for quotation indicators in section titles
        section_titles = features.get("section_titles", [])
        if any(title in ["quote", "quotation", "estimate"] for title in section_titles):
            confidence += 0.4
            key_features.append("quote_in_title")

        # Check for pricing indicators
        if features.get("has_dollar_amounts", False):
            confidence += 0.2
            key_features.append("has_pricing")

        if features.get("has_subtotal", False) or features.get("has_total", False):
            confidence += 0.3
            key_features.append("has_totals")

        # Check for line items with quantities
        if features.get("has_quantities", False):
            confidence += 0.2
            key_features.append("has_quantities")

        # Determine schema pattern
        schema_pattern = "basic_quotation"
        if "has_totals" in key_features and "has_quantities" in key_features:
            schema_pattern = "detailed_quotation"
        if features.get("table_count", 0) > 0:
            schema_pattern = "tabular_quotation"

        return ("QUOTATION", confidence, schema_pattern, key_features)

    def _is_specification(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Tuple[str, float, str, List[str]]:
        """Check if document is a technical specification."""
        confidence = 0.0
        key_features = []

        # Check for specification indicators in section titles
        section_titles = features.get("section_titles", [])
        if any(
            word in " ".join(section_titles)
            for word in ["specification", "spec", "technical", "requirements"]
        ):
            confidence += 0.3
            key_features.append("spec_in_title")

        # Check for technical terms in content
        content = document_data.get("content", [])
        all_content = " ".join([section.get("content", "") for section in content])

        technical_terms = [
            "dimensions",
            "capacity",
            "performance",
            "material",
            "compliance",
            "standard",
        ]
        if any(term in all_content.lower() for term in technical_terms):
            confidence += 0.3
            key_features.append("has_technical_terms")

        # Check for measurements and units
        measurement_patterns = [
            "mm",
            "cm",
            "m",
            "kg",
            "lb",
            "°c",
            "°f",
            "hz",
            "mhz",
            "ghz",
            "kw",
            "hp",
        ]
        if any(pattern in all_content.lower() for pattern in measurement_patterns):
            confidence += 0.3
            key_features.append("has_measurements")

        # Determine schema pattern
        schema_pattern = "basic_specification"
        if "has_technical_terms" in key_features and "has_measurements" in key_features:
            schema_pattern = "detailed_specification"
        if features.get("table_count", 0) > 2:
            schema_pattern = "tabular_specification"

        return ("SPECIFICATION", confidence, schema_pattern, key_features)

    def _is_invoice(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Tuple[str, float, str, List[str]]:
        """Check if document is an invoice."""
        confidence = 0.0
        key_features = []

        # Check for invoice indicators in section titles
        section_titles = features.get("section_titles", [])
        if any(title in ["invoice", "bill", "receipt"] for title in section_titles):
            confidence += 0.4
            key_features.append("invoice_in_title")

        # Check for invoice number
        all_content = " ".join(
            [section.get("content", "") for section in document_data.get("content", [])]
        )
        if "invoice #" in all_content.lower() or "invoice no" in all_content.lower():
            confidence += 0.3
            key_features.append("has_invoice_number")

        # Check for pricing and totals
        if features.get("has_dollar_amounts", False):
            confidence += 0.2
            key_features.append("has_pricing")

        if features.get("has_subtotal", False) or features.get("has_total", False):
            confidence += 0.2
            key_features.append("has_totals")

        # Determine schema pattern
        schema_pattern = "basic_invoice"
        if "has_invoice_number" in key_features and "has_totals" in key_features:
            schema_pattern = "detailed_invoice"
        if features.get("table_count", 0) > 0:
            schema_pattern = "tabular_invoice"

        return ("INVOICE", confidence, schema_pattern, key_features)

    def _is_terms_and_conditions(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Tuple[str, float, str, List[str]]:
        """Check if document is terms and conditions."""
        confidence = 0.0
        key_features = []

        # Check for terms indicators in section titles
        section_titles = features.get("section_titles", [])
        if any(
            term in " ".join(section_titles).lower()
            for term in ["terms", "conditions", "agreement", "contract"]
        ):
            confidence += 0.4
            key_features.append("terms_in_title")

        # Check for legal language
        content = document_data.get("content", [])
        all_content = " ".join([section.get("content", "") for section in content])

        legal_terms = [
            "shall",
            "herein",
            "pursuant",
            "liability",
            "warranty",
            "indemnify",
            "jurisdiction",
        ]
        legal_term_count = sum(1 for term in legal_terms if term in all_content.lower())

        if legal_term_count >= 3:
            confidence += 0.4
            key_features.append("has_legal_language")
        elif legal_term_count >= 1:
            confidence += 0.2
            key_features.append("has_some_legal_terms")

        # Check for all-caps sections (common in legal documents)
        caps_sections = sum(
            1 for section in content if section.get("title", "").isupper()
        )
        if caps_sections >= 3:
            confidence += 0.2
            key_features.append("has_caps_sections")

        # Determine schema pattern
        schema_pattern = "basic_terms"
        if "has_legal_language" in key_features:
            schema_pattern = "detailed_terms"
        if "has_caps_sections" in key_features:
            schema_pattern = "formal_terms"

        return ("TERMS_AND_CONDITIONS", confidence, schema_pattern, key_features)
