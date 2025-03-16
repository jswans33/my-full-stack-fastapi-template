"""
Configuration manager.

This module provides the central configuration management service.
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from utils.pipeline.config.models.change_event import (
    ConfigurationChangeEvent,
    ConfigurationChangeListener,
)
from utils.pipeline.config.providers.base import ConfigurationProvider
from utils.pipeline.config.providers.file import FileConfigurationProvider


class ConfigurationManager:
    """
    Configuration manager.

    Manages configuration providers and provides access to configuration.
    """

    def __init__(self, max_history: int = 100, auto_reload: bool = False):
        """
        Initialize the configuration manager.

        Args:
            max_history: Maximum number of change events to keep in history
        """
        self.providers: List[Tuple[ConfigurationProvider, int]] = []
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.listeners: List[ConfigurationChangeListener] = []
        self.change_history: List[ConfigurationChangeEvent] = []
        self.max_history = max_history
        self.auto_reload = auto_reload

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

    def enable_auto_reload(self) -> None:
        """Enable hot-reloading for all providers that support it."""
        self.auto_reload = True
        for provider, _ in self.providers:
            if isinstance(provider, FileConfigurationProvider):
                provider.enable_hot_reload = True
                # Set up hot-reloading
                provider.register_change_callback(self._handle_config_reload)
                provider.start_watching()

    def disable_auto_reload(self) -> None:
        """Disable hot-reloading for all providers."""
        self.auto_reload = False
        for provider, _ in self.providers:
            if isinstance(provider, FileConfigurationProvider):
                provider.stop_watching()
                provider.enable_hot_reload = False

    def _handle_config_reload(self, config_name: str) -> None:
        """
        Handle configuration reload events.

        Args:
            config_name: Name of the configuration that changed
        """
        try:
            # Get current config before reload
            old_config = self.get_config(config_name, use_cache=True)

            # Clear cache to force reload
            if config_name in self.cache:
                del self.cache[config_name]

            # Load new configuration
            new_config = self.get_config(config_name, use_cache=False)

            # Track change
            event = self._track_change(
                config_name=config_name,
                old_config=old_config,
                new_config=new_config,
                change_type="reload",
            )

            # Notify listeners
            self._notify_listeners(event)

        except Exception as e:
            print(f"Error handling configuration reload: {str(e)}")

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

    def update_configuration(
        self,
        config_name: str,
        updates: Dict[str, Any],
        change_type: str = "update",
        provider_id: Optional[str] = None,
        user: Optional[str] = None,
    ) -> bool:
        """
        Update configuration at runtime.

        Args:
            config_name: Name of the configuration to update
            updates: Configuration updates
            change_type: Type of change being made
            provider_id: ID of the provider triggering the change
            user: User making the change

        Returns:
            True if successful, False otherwise
        """
        # Get current configuration
        old_config = self.get_config(config_name, use_cache=False)

        # Apply updates
        updated_config = self._deep_merge(old_config, updates)

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

        if success:
            # Track change
            event = self._track_change(
                config_name=config_name,
                old_config=old_config,
                new_config=updated_config,
                change_type=change_type,
                provider_id=provider_id,
                user=user,
            )

            # Notify listeners
            self._notify_listeners(event)

        return success

    def register_listener(
        self,
        callback: Callable[[ConfigurationChangeEvent], None],
        config_patterns: Optional[List[str]] = None,
        change_types: Optional[List[str]] = None,
    ) -> None:
        """
        Register a listener for configuration changes.

        Args:
            callback: Function to call when configuration changes
            config_patterns: List of configuration name patterns to listen for
            change_types: List of change types to listen for
        """
        listener = ConfigurationChangeListener(
            callback=callback,
            config_patterns=config_patterns or [],
            change_types=change_types or [],
        )
        self.listeners.append(listener)

    def unregister_listener(
        self, callback: Callable[[ConfigurationChangeEvent], None]
    ) -> None:
        """
        Unregister a configuration change listener.

        Args:
            callback: Callback function to unregister
        """
        self.listeners = [l for l in self.listeners if l.callback != callback]

    def get_change_history(
        self,
        config_name: Optional[str] = None,
        change_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[ConfigurationChangeEvent]:
        """
        Get configuration change history.

        Args:
            config_name: Filter by configuration name
            change_type: Filter by change type
            limit: Maximum number of events to return

        Returns:
            List of configuration change events
        """
        events = self.change_history

        if config_name:
            events = [e for e in events if e.config_name == config_name]
        if change_type:
            events = [e for e in events if e.change_type == change_type]
        if limit:
            events = events[-limit:]

        return events

    def _track_change(
        self,
        config_name: str,
        old_config: Dict[str, Any],
        new_config: Dict[str, Any],
        change_type: str,
        provider_id: Optional[str] = None,
        user: Optional[str] = None,
    ) -> ConfigurationChangeEvent:
        """
        Track a configuration change.

        Args:
            config_name: Name of the configuration that changed
            old_config: Previous configuration
            new_config: New configuration
            change_type: Type of change
            provider_id: ID of the provider that triggered the change
            user: User who made the change

        Returns:
            Configuration change event
        """
        event = ConfigurationChangeEvent(
            timestamp=datetime.now(),
            config_name=config_name,
            provider_id=provider_id or "unknown",
            old_value=old_config,
            new_value=new_config,
            change_type=change_type,
            user=user,
        )

        self.change_history.append(event)
        if len(self.change_history) > self.max_history:
            self.change_history.pop(0)

        return event

    def _notify_listeners(self, event: ConfigurationChangeEvent) -> None:
        """
        Notify listeners of configuration changes.

        Args:
            event: Configuration change event
        """
        for listener in self.listeners:
            if listener.matches(event):
                try:
                    listener.notify(event)
                except Exception as e:
                    # Log error but don't propagate
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
