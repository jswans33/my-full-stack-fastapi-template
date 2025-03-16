"""
Configuration change event models.

This module provides models for tracking configuration changes.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Optional


@dataclass
class ConfigurationChangeEvent:
    """
    Represents a configuration change event.

    Attributes:
        timestamp: When the change occurred
        config_name: Name of the configuration that changed
        provider_id: ID of the provider that triggered the change
        old_value: Previous configuration value
        new_value: New configuration value
        change_type: Type of change (update, reload, etc.)
        user: User who made the change (if applicable)
    """

    timestamp: datetime
    config_name: str
    provider_id: str
    old_value: Dict[str, Any]
    new_value: Dict[str, Any]
    change_type: str
    user: Optional[str] = None

    def get_changes(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a dictionary of changes between old and new values.

        Returns:
            Dictionary with 'added', 'modified', and 'removed' keys
        """
        changes = {"added": {}, "modified": {}, "removed": {}}

        # Find added and modified keys
        for key, new_val in self.new_value.items():
            if key not in self.old_value:
                changes["added"][key] = new_val
            elif self.old_value[key] != new_val:
                changes["modified"][key] = {"old": self.old_value[key], "new": new_val}

        # Find removed keys
        for key in self.old_value:
            if key not in self.new_value:
                changes["removed"][key] = self.old_value[key]

        return changes


@dataclass
class ConfigurationChangeListener:
    """
    Configuration change listener interface.

    Attributes:
        callback: Function to call when configuration changes
        config_patterns: List of configuration name patterns to listen for
        change_types: List of change types to listen for
    """

    callback: Callable[[ConfigurationChangeEvent], None]
    config_patterns: list[str]
    change_types: list[str]

    def matches(self, event: ConfigurationChangeEvent) -> bool:
        """
        Check if this listener should handle the given event.

        Args:
            event: Configuration change event

        Returns:
            True if the listener should handle the event
        """
        # Check if change type matches
        if self.change_types and event.change_type not in self.change_types:
            return False

        # Check if config name matches any patterns
        if self.config_patterns:
            import fnmatch

            return any(
                fnmatch.fnmatch(event.config_name, pattern)
                for pattern in self.config_patterns
            )

        return True

    def notify(self, event: ConfigurationChangeEvent) -> None:
        """
        Notify the listener of a configuration change.

        Args:
            event: Configuration change event
        """
        try:
            self.callback(event)
        except Exception as e:
            # Log error but don't propagate
            print(f"Error in configuration change listener: {str(e)}")
