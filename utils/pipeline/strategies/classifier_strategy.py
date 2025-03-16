"""
Classifier strategy interface and base implementation.

This module defines the interface for document classifiers and provides a base
implementation with common functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from utils.pipeline.utils.logging import get_logger


class ClassifierStrategy(ABC):
    """Interface defining the contract for document classifiers."""

    @abstractmethod
    def __init__(self, *, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the classifier.

        Args:
            config: Configuration dictionary for the classifier. Must be passed as a keyword argument.
        """
        pass

    @abstractmethod
    def classify(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify a document based on its data and features.

        Args:
            document_data: The document data to classify
            features: Extracted features from the document

        Returns:
            Classification result containing document type, confidence, etc.
        """
        pass

    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """
        Get the document types supported by this classifier.

        Returns:
            List of supported document type identifiers
        """
        pass

    @abstractmethod
    def get_classifier_info(self) -> Dict[str, Any]:
        """
        Get information about this classifier implementation.

        Returns:
            Dictionary containing classifier metadata
        """
        pass


class BaseClassifier(ClassifierStrategy):
    """
    Base implementation of the ClassifierStrategy interface.

    Provides common functionality for document classifiers including:
    - Configuration management
    - Feature extraction
    - Logging
    - Error handling
    """

    def __init__(self, *, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base classifier.

        Args:
            config: Configuration dictionary for the classifier. Must be passed as a keyword argument.
        """
        self.config = config or {}
        self.logger = get_logger(__name__)
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate the classifier configuration."""
        # Base configuration requirements
        required_fields = ["name", "version"]
        for field in required_fields:
            if field not in self.config:
                # Check if the field is in a nested config structure
                if (
                    "classification" in self.config
                    and field in self.config["classification"]
                ):
                    self.config[field] = self.config["classification"][field]
                else:
                    self.logger.warning(f"Missing required config field: {field}")
                    self.config[field] = "unknown"

    def _extract_features(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract common features from document data.

        Args:
            document_data: The document data to extract features from

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

        # Extract table information
        tables = document_data.get("tables", [])
        features["table_count"] = len(tables)

        return features

    def get_classifier_info(self) -> Dict[str, Any]:
        """
        Get information about this classifier implementation.

        Returns:
            Dictionary containing classifier metadata
        """
        return {
            "name": self.config.get("name", "unknown"),
            "version": self.config.get("version", "unknown"),
            "description": self.config.get("description", ""),
            "supported_types": self.get_supported_types(),
            "config_schema": self.config.get("config_schema", {}),
        }

    def get_supported_types(self) -> List[str]:
        """
        Get the document types supported by this classifier.

        Returns:
            List of supported document type identifiers
        """
        return self.config.get("supported_types", [])

    @abstractmethod
    def classify(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify a document based on its data and features.

        This method must be implemented by concrete classifier classes.

        Args:
            document_data: The document data to classify
            features: Extracted features from the document

        Returns:
            Classification result containing document type, confidence, etc.
        """
        pass
