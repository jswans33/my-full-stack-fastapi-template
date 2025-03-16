"""
Keyword/Phrase Analyzer classifier.

This module provides advanced keyword and phrase analysis for document classification.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from utils.pipeline.strategies.classifier_strategy import BaseClassifier


class KeywordAnalyzerClassifier(BaseClassifier):
    """
    Classifies documents using advanced keyword and phrase analysis.

    This classifier extends beyond simple keyword matching to include:
    - Frequency analysis
    - Contextual keyword analysis
    - Phrase pattern matching
    - Semantic grouping of related terms
    """

    def __init__(self, *, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the keyword analyzer classifier.

        Args:
            config: Configuration dictionary for the classifier
        """
        super().__init__(config=config)

        # Get keyword analysis configuration
        self.keyword_config = self.config.get("keyword_analysis", {})
        self.document_types = self.keyword_config.get("document_types", {})
        self.threshold = self.keyword_config.get("threshold", 0.5)

        # Configure keyword groups (semantically related terms)
        self.keyword_groups = self.keyword_config.get("keyword_groups", {})

        # Configure phrase patterns (regular expressions)
        self.phrase_patterns = self.keyword_config.get("phrase_patterns", {})

        # Configure contextual rules
        self.contextual_rules = self.keyword_config.get("contextual_rules", {})

    def classify(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify the document using keyword/phrase analysis.

        Args:
            document_data: Processed document data
            features: Extracted features from the document

        Returns:
            Classification result with document type, confidence, and schema pattern
        """
        # Extract all text content from the document
        content_text = self._extract_all_text(document_data)

        # Analyze keyword frequencies
        keyword_frequencies = self._analyze_keyword_frequencies(content_text)

        # Match phrase patterns
        phrase_matches = self._match_phrase_patterns(content_text)

        # Analyze keyword context
        contextual_matches = self._analyze_keyword_context(document_data)

        # Calculate scores for each document type
        type_scores = self._calculate_type_scores(
            keyword_frequencies, phrase_matches, contextual_matches
        )

        # Get best matching document type
        best_match = self._get_best_match(type_scores)

        if best_match[1] < self.threshold:
            return {
                "document_type": "UNKNOWN",
                "confidence": best_match[1],
                "schema_pattern": "unknown",
                "key_features": [],
            }

        return {
            "document_type": best_match[0],
            "confidence": best_match[1],
            "schema_pattern": self.document_types.get(best_match[0], {}).get(
                "schema_pattern", "standard"
            ),
            "key_features": best_match[2],
        }

    def get_supported_types(self) -> List[str]:
        """
        Get the document types supported by this classifier.

        Returns:
            List of supported document type identifiers
        """
        return list(self.document_types.keys())

    def _extract_all_text(self, document_data: Dict[str, Any]) -> str:
        """
        Extract all text content from the document.

        Args:
            document_data: Processed document data

        Returns:
            Combined text content from all sections
        """
        # Extract metadata text
        metadata = document_data.get("metadata", {})
        metadata_text = " ".join([str(v) for v in metadata.values()])

        # Extract content text
        content_sections = document_data.get("content", [])
        content_text = " ".join(
            [
                section.get("title", "") + " " + section.get("content", "")
                for section in content_sections
            ]
        )

        # Extract table text
        tables = document_data.get("tables", [])
        table_text = ""
        for table in tables:
            table_text += table.get("title", "") + " "
            for row in table.get("rows", []):
                table_text += " ".join([str(cell) for cell in row]) + " "

        # Combine all text
        return (metadata_text + " " + content_text + " " + table_text).lower()

    def _analyze_keyword_frequencies(self, text: str) -> Dict[str, Dict[str, int]]:
        """
        Analyze keyword frequencies in the document.

        Args:
            text: Document text content

        Returns:
            Dictionary mapping keyword groups to frequency counts
        """
        results = {}

        # Check each keyword group
        for group_name, keywords in self.keyword_groups.items():
            group_counts = {}
            for keyword in keywords:
                # Count occurrences of the keyword
                count = len(
                    re.findall(r"\b" + re.escape(keyword.lower()) + r"\b", text)
                )
                if count > 0:
                    group_counts[keyword] = count

            if group_counts:
                results[group_name] = group_counts

        return results

    def _match_phrase_patterns(self, text: str) -> Dict[str, List[str]]:
        """
        Match phrase patterns in the document.

        Args:
            text: Document text content

        Returns:
            Dictionary mapping pattern types to matched phrases
        """
        results = {}

        # Check each phrase pattern
        for pattern_type, patterns in self.phrase_patterns.items():
            matches = []
            for pattern in patterns:
                # Find all matches for the pattern
                found = re.findall(pattern, text)
                matches.extend(found)

            if matches:
                results[pattern_type] = matches

        return results

    def _analyze_keyword_context(
        self, document_data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Analyze keyword context in the document.

        Args:
            document_data: Processed document data

        Returns:
            Dictionary mapping context types to matched contexts
        """
        results = {}

        # Extract section titles and content
        sections = document_data.get("content", [])

        # Check each contextual rule
        for context_type, rules in self.contextual_rules.items():
            matches = []

            for rule in rules:
                section_keyword = rule.get("section_keyword", "")
                content_keywords = rule.get("content_keywords", [])

                # Find sections matching the section keyword
                for section in sections:
                    title = section.get("title", "").lower()
                    content = section.get("content", "").lower()

                    # Check if section title contains the keyword
                    if section_keyword and section_keyword.lower() in title:
                        # Check if content contains any of the content keywords
                        for keyword in content_keywords:
                            if keyword.lower() in content:
                                matches.append(f"{title}: {keyword}")

            if matches:
                results[context_type] = matches

        return results

    def _calculate_type_scores(
        self,
        keyword_frequencies: Dict[str, Dict[str, int]],
        phrase_matches: Dict[str, List[str]],
        contextual_matches: Dict[str, List[str]],
    ) -> Dict[str, Tuple[float, List[str]]]:
        """
        Calculate scores for each document type.

        Args:
            keyword_frequencies: Keyword frequency analysis results
            phrase_matches: Phrase pattern matching results
            contextual_matches: Contextual analysis results

        Returns:
            Dictionary mapping document types to (score, features) tuples
        """
        type_scores = {}

        # Calculate score for each document type
        for doc_type, type_config in self.document_types.items():
            score = 0.0
            features = []

            # Score based on keyword groups
            keyword_groups = type_config.get("keyword_groups", [])
            keyword_weight = type_config.get("weights", {}).get("keywords", 0.4)

            for group in keyword_groups:
                if group in keyword_frequencies:
                    group_score = sum(keyword_frequencies[group].values()) / len(
                        self.keyword_groups[group]
                    )
                    score += keyword_weight * group_score
                    features.append(f"keyword_group_{group}")

            # Score based on phrase patterns
            phrase_patterns = type_config.get("phrase_patterns", [])
            phrase_weight = type_config.get("weights", {}).get("phrases", 0.3)

            for pattern in phrase_patterns:
                if pattern in phrase_matches:
                    pattern_score = len(phrase_matches[pattern]) / len(
                        self.phrase_patterns[pattern]
                    )
                    score += phrase_weight * pattern_score
                    features.append(f"phrase_pattern_{pattern}")

            # Score based on contextual rules
            context_rules = type_config.get("contextual_rules", [])
            context_weight = type_config.get("weights", {}).get("context", 0.3)

            for rule in context_rules:
                if rule in contextual_matches:
                    rule_score = len(contextual_matches[rule]) / len(
                        self.contextual_rules[rule]
                    )
                    score += context_weight * rule_score
                    features.append(f"context_rule_{rule}")

            # Store the score and features
            type_scores[doc_type] = (min(score, 1.0), features)

        return type_scores

    def _get_best_match(
        self, type_scores: Dict[str, Tuple[float, List[str]]]
    ) -> Tuple[str, float, List[str]]:
        """
        Get the best matching document type.

        Args:
            type_scores: Scores for each document type

        Returns:
            Tuple of (document_type, confidence, key_features)
        """
        if not type_scores:
            return ("UNKNOWN", 0.0, [])

        # Find the document type with the highest score
        best_type = max(type_scores.items(), key=lambda x: x[1][0])

        return (best_type[0], best_type[1][0], best_type[1][1])
