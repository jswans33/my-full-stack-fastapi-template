"""
Configuration manager.

This module provides the central configuration management service.
"""

from typing import Any, Callable, Dict, List, Tuple

from utils.pipeline.config.providers.base import ConfigurationProvider


class ConfigurationManager:
    """
    Configuration manager.

    Manages configuration providers and provides access to configuration.
    """

    def __init__(self):
        """Initialize the configuration manager."""
        self.providers: List[Tuple[ConfigurationProvider, int]] = []
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.listeners: Dict[str, List[Callable]] = {}

    def register_provider(
        self, provider: ConfigurationProvider, priority: int = 0
    ) -> None:
        """
        Register a configuration provider.

        Args:
            provider: Configuration provider to register
            priority: Provider priority (higher priority providers override lower priority ones)
        """
        self.providers.append((provider, priority))
        self.providers.sort(key=lambda x: x[1], reverse=True)

        # Clear cache
        self.cache = {}

    def get_config(self, config_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get configuration by name.

        Args:
            config_name: Name of the configuration to load
            use_cache: Whether to use cached configuration

        Returns:
            Configuration dictionary
        """
        # Check cache
        if use_cache and config_name in self.cache:
            return self.cache[config_name]

        # Check if configuration is already loaded
        if config_name in self.configs:
            config = self.configs[config_name]
        else:
            # Load configuration from providers
            config = self.load_configuration(config_name)

            # Store configuration
            self.configs[config_name] = config

        # Cache configuration
        self.cache[config_name] = config

        return config

    def load_configuration(self, config_name: str) -> Dict[str, Any]:
        """
        Load configuration from providers.

        Args:
            config_name: Name of the configuration to load

        Returns:
            Configuration dictionary
        """
        merged_config = {}

        # Load from providers in priority order
        for provider, _ in self.providers:
            # Check if provider supports this configuration
            if provider.supports_config(config_name):
                # Get configuration from provider
                provider_config = provider.get_config(config_name)

                # Merge with existing configuration
                merged_config = self._deep_merge(merged_config, provider_config)

        return merged_config

    def update_configuration(self, config_name: str, updates: Dict[str, Any]) -> bool:
        """
        Update configuration at runtime.

        Args:
            config_name: Name of the configuration to update
            updates: Configuration updates

        Returns:
            True if successful, False otherwise
        """
        # Get current configuration
        config = self.get_config(config_name, use_cache=False)

        # Apply updates
        updated_config = self._deep_merge(config, updates)

        # Store updated configuration
        self.configs[config_name] = updated_config

        # Clear cache
        if config_name in self.cache:
            del self.cache[config_name]

        # Save configuration to providers
        success = False
        for provider, _ in self.providers:
            # Try to save configuration
            if provider.save_config(config_name, updated_config):
                success = True

        # Notify listeners
        self._notify_listeners(config_name, updated_config)

        return success

    def register_listener(self, config_name: str, callback: Callable) -> None:
        """
        Register a listener for configuration changes.

        Args:
            config_name: Name of the configuration to listen for
            callback: Callback function to call when configuration changes
        """
        if config_name not in self.listeners:
            self.listeners[config_name] = []

        self.listeners[config_name].append(callback)

    def _notify_listeners(self, config_name: str, config: Dict[str, Any]) -> None:
        """
        Notify listeners of configuration changes.

        Args:
            config_name: Name of the configuration that changed
            config: New configuration
        """
        if config_name in self.listeners:
            for callback in self.listeners[config_name]:
                try:
                    callback(config_name, config)
                except Exception as e:
                    # Log error
                    print(f"Error notifying listener: {str(e)}")

    def _deep_merge(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.

        Args:
            base: Base dictionary
            override: Dictionary to override base

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively merge dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override or add value
                result[key] = value

        return result
