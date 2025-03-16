"""
Factory for creating and managing document classifiers.

This module provides a factory class for registering, creating, and managing
document classifier implementations.
"""

from typing import Any, Dict, List, Optional, Type

from utils.pipeline.strategies.classifier_strategy import ClassifierStrategy
from utils.pipeline.utils.logging import get_logger


class ClassifierFactory:
    """
    Factory for creating and managing document classifiers.

    This factory:
    - Maintains registry of available classifiers
    - Handles classifier instantiation
    - Manages classifier configurations
    - Provides discovery of available classifiers
    """

    def __init__(self):
        """Initialize the classifier factory."""
        self._registered_classifiers: Dict[str, Type[ClassifierStrategy]] = {}
        self._classifier_configs: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger(__name__)

    def register_classifier(
        self,
        name: str,
        classifier_class: Type[ClassifierStrategy],
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a new classifier implementation.

        Args:
            name: Unique identifier for the classifier
            classifier_class: The classifier class to register
            config: Optional configuration for the classifier
        """
        if name in self._registered_classifiers:
            self.logger.warning(f"Overwriting existing classifier registration: {name}")

        self._registered_classifiers[name] = classifier_class
        if config:
            self._classifier_configs[name] = config

        self.logger.info(f"Registered classifier: {name}")

    def create_classifier(
        self, name: str, config: Optional[Dict[str, Any]] = None
    ) -> ClassifierStrategy:
        """
        Create an instance of a registered classifier.

        Args:
            name: Name of the classifier to create
            config: Optional configuration override

        Returns:
            Instance of the requested classifier

        Raises:
            ValueError: If classifier name is not registered
        """
        if name not in self._registered_classifiers:
            raise ValueError(f"No classifier registered with name: {name}")

        # Merge configs, with provided config taking precedence
        classifier_config = self._classifier_configs.get(name, {}).copy()
        if config:
            classifier_config.update(config)

        # Get and instantiate the classifier class with keyword-only arguments
        classifier_class = self._registered_classifiers[name]
        return classifier_class(config=classifier_config)

    def get_available_classifiers(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered classifiers.

        Returns:
            List of classifier information dictionaries
        """
        classifiers = []
        for name, classifier_class in self._registered_classifiers.items():
            try:
                # Get base config for this classifier
                config = self._classifier_configs.get(name, {})

                # Create classifier instance using the class
                classifier = self.create_classifier(name, config)

                # Get classifier metadata
                classifiers.append(
                    {
                        "name": name,
                        "info": classifier.get_classifier_info(),
                        "supported_types": classifier.get_supported_types(),
                        "has_config": name in self._classifier_configs,
                    }
                )
            except Exception as e:
                self.logger.error(f"Error getting classifier info for {name}: {str(e)}")
                # Add basic info for failed classifier
                classifiers.append(
                    {
                        "name": name,
                        "info": {"error": str(e)},
                        "supported_types": [],
                        "has_config": name in self._classifier_configs,
                    }
                )

        return classifiers

    def remove_classifier(self, name: str) -> None:
        """
        Remove a registered classifier.

        Args:
            name: Name of the classifier to remove
        """
        if name in self._registered_classifiers:
            del self._registered_classifiers[name]
            self._classifier_configs.pop(name, None)
            self.logger.info(f"Removed classifier registration: {name}")
        else:
            self.logger.warning(f"Attempted to remove unregistered classifier: {name}")

    def update_classifier_config(self, name: str, config: Dict[str, Any]) -> None:
        """
        Update the configuration for a registered classifier.

        Args:
            name: Name of the classifier to update
            config: New configuration dictionary

        Raises:
            ValueError: If classifier name is not registered
        """
        if name not in self._registered_classifiers:
            raise ValueError(f"No classifier registered with name: {name}")

        self._classifier_configs[name] = config
        self.logger.info(f"Updated configuration for classifier: {name}")
