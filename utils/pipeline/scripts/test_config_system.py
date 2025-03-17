"""Manual test script for configuration system."""

import os
import sys
import tempfile
import time

import yaml

# Add the project root to the Python path for imports
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

# Now we can import from utils module
from utils.pipeline.config import (
    ConfigurationManager,
    EnvironmentConfigurationProvider,
    FileConfigurationProvider,
    PipelineConfig,
    get_pipeline_config,
)

# Create a default configuration manager
config_manager = ConfigurationManager()

# Register file provider (highest priority)
file_provider = FileConfigurationProvider(base_dirs=["utils/pipeline/config", "config"])
config_manager.register_provider(file_provider, priority=100)

# Register environment provider (lower priority)
env_provider = EnvironmentConfigurationProvider(prefix="PIPELINE_")
config_manager.register_provider(env_provider, priority=50)

# Register models
config_manager.register_model("pipeline", PipelineConfig)


def main():
    """Run manual configuration system test."""
    print("\n=== Configuration System Test ===\n")

    # Create a temporary config file
    initial_config = {
        "input_dir": "test_input",
        "output_dir": "test_output",
        "output_format": "yaml",
        "validation_level": "basic",
        "strategies": {
            "pdf": "strategies.pdf",
            "excel": "strategies.excel",
            "word": "strategies.word",
            "text": "strategies.text",
        },
    }

    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        yaml.dump(initial_config, f)
        config_path = f.name

    try:
        print(f"Created test configuration file: {config_path}")

        # Register for config changes
        def on_change(event):
            print("\nConfiguration changed:")
            print(f"  Config: {event.config_name}")
            print(f"  Old input_dir: {event.old_value.get('input_dir')}")
            print(f"  New input_dir: {event.new_value.get('input_dir')}")

        config_manager.register_listener(on_change, config_patterns=["pipeline"])

        # Get current config
        config = get_pipeline_config()
        print("\nInitial configuration:")
        print(f"  input_dir = {config.input_dir}")
        print(f"  output_dir = {config.output_dir}")
        print(f"  validation_level = {config.validation_level}")

        # Enable hot-reloading
        config_manager.enable_auto_reload()

        print("\nHot-reloading enabled. You can now modify the config file:")
        print(f"  {config_path}")
        print("\nTry changing the input_dir value and watch for updates.")
        print("Press Ctrl+C to exit...")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")

    finally:
        # Clean up
        config_manager.disable_auto_reload()
        if os.path.exists(config_path):
            os.unlink(config_path)
        print("\nTest complete. Configuration file removed.")


if __name__ == "__main__":
    main()
