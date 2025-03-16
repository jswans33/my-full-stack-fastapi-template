"""
Base configuration provider.

This module defines the base class for configuration providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ConfigurationProvider(ABC):
    """
    Abstract base class for configuration providers.

    Configuration providers are responsible for loading configuration
    from different sources (files, environment variables, databases, etc.).
    """

    @abstractmethod
    def get_config(self, config_name: str) -> Dict[str, Any]:
        """
        Get configuration by name.

        Args:
            config_name: Name of the configuration to load

        Returns:
            Configuration dictionary or empty dict if not found
        """
        pass

    @abstractmethod
    def supports_config(self, config_name: str) -> bool:
        """
        Check if provider supports this configuration.

        Args:
            config_name: Name of the configuration to check

        Returns:
            True if provider supports this configuration, False otherwise
        """
        pass

    @abstractmethod
    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """
        Save configuration.

        Args:
            config_name: Name of the configuration to save
            config_data: Configuration data to save

        Returns:
            True if successful, False otherwise
        """
        pass
