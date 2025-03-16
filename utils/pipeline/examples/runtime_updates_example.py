"""
Example demonstrating runtime configuration updates and hot-reloading.

This script shows how to:
1. Set up configuration with hot-reloading
2. Register change listeners
3. Update configuration at runtime
4. Monitor configuration changes
"""

import time
from pathlib import Path

from utils.pipeline.config.manager import ConfigurationManager
from utils.pipeline.config.models.change_event import ConfigurationChangeEvent
from utils.pipeline.config.providers.file import FileConfigurationProvider

# Example configuration files
CONFIG_DIR = Path(__file__).parent / "config"
CONFIG_DIR.mkdir(exist_ok=True)

# Create example configuration file
APP_CONFIG = CONFIG_DIR / "app_config.yaml"
APP_CONFIG.write_text("""
feature_flags:
  dark_mode: false
  beta_features: false
  
logging:
  level: info
  format: json
""")


def print_config_changes(event: ConfigurationChangeEvent) -> None:
    """Print configuration changes."""
    print(f"\nConfiguration changed: {event.config_name}")
    print(f"Change type: {event.change_type}")
    print(f"Timestamp: {event.timestamp}")

    changes = event.get_changes()
    if changes["added"]:
        print("\nAdded:")
        for key, value in changes["added"].items():
            print(f"  {key}: {value}")

    if changes["modified"]:
        print("\nModified:")
        for key, changes in changes["modified"].items():
            print(f"  {key}:")
            print(f"    From: {changes['old']}")
            print(f"    To:   {changes['new']}")

    if changes["removed"]:
        print("\nRemoved:")
        for key, value in changes["removed"].items():
            print(f"  {key}: {value}")


def main() -> None:
    """Run the example."""
    # Create configuration manager with hot-reloading enabled
    config_manager = ConfigurationManager(auto_reload=True)

    # Create file provider with hot-reloading
    file_provider = FileConfigurationProvider(
        base_dirs=[str(CONFIG_DIR)], enable_hot_reload=True
    )

    # Register provider
    config_manager.register_provider(file_provider)

    # Register change listener for all YAML files
    config_manager.register_listener(
        callback=print_config_changes,
        config_patterns=["*.yaml"],
        change_types=["update", "reload"],
    )

    # Load initial configuration
    config = config_manager.get_config("app_config.yaml")
    print("\nInitial configuration:")
    print(config)

    # Update configuration
    print("\nUpdating configuration...")
    config_manager.update_configuration(
        config_name="app_config.yaml",
        updates={"feature_flags": {"dark_mode": True, "new_feature": True}},
        change_type="update",
        user="admin",
    )

    # Get updated configuration
    config = config_manager.get_config("app_config.yaml")
    print("\nUpdated configuration:")
    print(config)

    # Show change history
    print("\nChange history:")
    history = config_manager.get_change_history(config_name="app_config.yaml", limit=5)
    for event in history:
        print(f"\n{event.timestamp}: {event.change_type}")
        print(f"Changed by: {event.user or 'unknown'}")
        changes = event.get_changes()
        if changes["modified"]:
            print("Modified values:")
            for key, change in changes["modified"].items():
                print(f"  {key}: {change['old']} -> {change['new']}")

    print(
        "\nWatching for file changes. Edit app_config.yaml to see hot-reloading in action."
    )
    print("Press Ctrl+C to exit.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping configuration manager...")
        config_manager.disable_auto_reload()


if __name__ == "__main__":
    main()
