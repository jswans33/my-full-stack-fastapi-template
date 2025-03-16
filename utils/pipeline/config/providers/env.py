"""
Environment configuration provider.

This module provides a configuration provider that loads configuration from environment variables.
"""

import os
from typing import Any, Dict

from utils.pipeline.config.providers.base import ConfigurationProvider


class EnvironmentConfigurationProvider(ConfigurationProvider):
    """
    Environment-based configuration provider.

    Loads configuration from environment variables.
    """

    def __init__(self, prefix: str = "PIPELINE_"):
        """
        Initialize the provider.

        Args:
            prefix: Prefix for environment variables (default: "PIPELINE_")
        """
        self.prefix = prefix

    def get_config(self, config_name: str) -> Dict[str, Any]:
        """
        Get configuration by name.

        Args:
            config_name: Name of the configuration to load

        Returns:
            Configuration dictionary or empty dict if not found
        """
        # Convert config_name to environment variable prefix
        env_prefix = (
            f"{self.prefix}{config_name.upper().replace('/', '_').replace('.', '_')}_"
        )

        # Get all environment variables with this prefix
        config = {}
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                # Remove prefix from key
                config_key = key[len(env_prefix) :].lower()

                # Add to configuration
                config[config_key] = self._parse_value(value)

        return config

    def supports_config(self, config_name: str) -> bool:
        """
        Check if provider supports this configuration.

        Args:
            config_name: Name of the configuration to check

        Returns:
            True if provider supports this configuration, False otherwise
        """
        # Convert config_name to environment variable prefix
        env_prefix = (
            f"{self.prefix}{config_name.upper().replace('/', '_').replace('.', '_')}_"
        )

        # Check if any environment variables have this prefix
        for key in os.environ:
            if key.startswith(env_prefix):
                return True

        return False

    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """
        Save configuration.

        Environment variables cannot be saved, so this always returns False.

        Args:
            config_name: Name of the configuration to save
            config_data: Configuration data to save

        Returns:
            Always False
        """
        # Environment variables cannot be saved
        return False

    def _parse_value(self, value: str) -> Any:
        """
        Parse environment variable value.

        Args:
            value: Value to parse

        Returns:
            Parsed value
        """
        # Try to parse as boolean
        if value.lower() in ["true", "yes", "1"]:
            return True
        elif value.lower() in ["false", "no", "0"]:
            return False

        # Try to parse as integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try to parse as float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value
