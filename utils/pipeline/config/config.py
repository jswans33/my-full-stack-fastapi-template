"""
Configuration module for the pipeline.

This module handles loading, validating, and merging configuration settings.
"""

import os
from typing import Any, Dict, Optional

import yaml

# Default configuration
DEFAULT_CONFIG = {
    "input_dir": "data/input",
    "output_dir": "data/output",
    "output_format": "yaml",
    "log_level": "INFO",
    "validation_level": "basic",
    "strategies": {
        "pdf": "strategies.pdf",
        "excel": "strategies.excel",
        "word": "strategies.word",
        "text": "strategies.text",
    },
}

# Required configuration fields
REQUIRED_FIELDS = ["output_dir"]

# Environment variable prefix
ENV_PREFIX = "PIPELINE_"


def load_config(
    config_path: Optional[str] = None,
    config_dict: Optional[Dict[str, Any]] = None,
    override_dict: Optional[Dict[str, Any]] = None,
    use_env: bool = False,
) -> Dict[str, Any]:
    """
    Load configuration from various sources and merge them.

    The configuration is loaded in the following order (later sources override earlier ones):
    1. Default configuration
    2. Configuration file (if provided)
    3. Configuration dictionary (if provided)
    4. Override dictionary (if provided)
    5. Environment variables (if use_env is True)

    Args:
        config_path: Path to a YAML configuration file
        config_dict: Configuration dictionary to use instead of loading from file
        override_dict: Dictionary with values that override the loaded configuration
        use_env: Whether to use environment variables to override configuration

    Returns:
        The merged configuration dictionary

    Raises:
        FileNotFoundError: If the configuration file does not exist
        yaml.YAMLError: If the configuration file contains invalid YAML
        ValueError: If the configuration is invalid (missing required fields)
    """
    # Start with default configuration
    config = DEFAULT_CONFIG.copy()

    # Load from file if provided
    if config_path:
        file_config = _load_from_file(config_path)
        config = _merge_configs(config, file_config)

    # Use config_dict if provided
    if config_dict:
        config = _merge_configs(config, config_dict)

    # Apply overrides if provided
    if override_dict:
        config = _merge_configs(config, override_dict)

    # Apply environment variables if requested
    if use_env:
        env_config = _load_from_env()
        config = _merge_configs(config, env_config)

    # Validate the configuration
    _validate_config(config)

    return config


def _load_from_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def _load_from_env() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    config = {}

    for key, value in os.environ.items():
        if key.startswith(ENV_PREFIX):
            # Convert PIPELINE_INPUT_DIR to input_dir
            config_key = key[len(ENV_PREFIX) :].lower()

            # Handle nested keys (e.g., PIPELINE_STRATEGIES_PDF)
            if "_" in config_key:
                parts = config_key.split("_")
                current = config
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                config[config_key] = value

    return config


def _merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries.

    The override dictionary takes precedence over the base dictionary.
    For nested dictionaries, the merge is recursive.
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = _merge_configs(result[key], value)
        else:
            # Override or add the value
            result[key] = value

    return result


def _validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the configuration.

    Raises:
        ValueError: If the configuration is invalid
    """
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in config:
            raise ValueError(f"Missing required configuration field: {field}")

        # Check if the field has a value (not None or empty string)
        if config[field] is None or (
            isinstance(config[field], str) and not config[field].strip()
        ):
            raise ValueError(f"Required configuration field '{field}' cannot be empty")

    # Validate input_dir if present
    if "input_dir" in config and isinstance(config["input_dir"], str):
        # Ensure input_dir exists if it's an absolute path
        input_dir = config["input_dir"]
        if os.path.isabs(input_dir) and not os.path.exists(input_dir):
            raise ValueError(f"Input directory does not exist: {input_dir}")

    # Validate strategies if present
    if "strategies" in config and isinstance(config["strategies"], dict):
        for strategy_type, strategy_path in config["strategies"].items():
            if not isinstance(strategy_path, str) or not strategy_path:
                raise ValueError(
                    f"Invalid strategy path for {strategy_type}: {strategy_path}"
                )

    # Validate log_level if present
    if "log_level" in config and isinstance(config["log_level"], str):
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config["log_level"].upper() not in valid_log_levels:
            raise ValueError(
                f"Invalid log level: {config['log_level']}. "
                f"Must be one of {', '.join(valid_log_levels)}"
            )
