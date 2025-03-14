"""
Configuration module for the pipeline.

This module handles loading, validating, and merging configuration settings using Pydantic.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Optional, Union

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

# Environment variable prefix
ENV_PREFIX = "PIPELINE_"


class LogLevel(str, Enum):
    """Valid log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ValidationLevel(str, Enum):
    """Validation levels for document processing."""

    BASIC = "basic"
    STRICT = "strict"
    CUSTOM = "custom"


class ComponentConfig(BaseModel):
    """Configuration for individual document processing components."""

    analyzer: str
    cleaner: str
    extractor: str
    validator: str
    formatter: str


class StrategyConfig(BaseModel):
    """Configuration for document processing strategies."""

    pdf: Union[str, ComponentConfig] = "strategies.pdf"
    excel: Union[str, ComponentConfig] = "strategies.excel"
    word: Union[str, ComponentConfig] = "strategies.word"
    text: Union[str, ComponentConfig] = "strategies.text"


class PipelineConfig(BaseModel):
    """Pipeline configuration model with validation."""

    input_dir: str = Field(
        default="data/input", description="Directory for input documents"
    )
    output_dir: str = Field(
        default="data/output", description="Directory for processed output"
    )
    output_format: str = Field(default="yaml", description="Output format (yaml/json)")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    validation_level: ValidationLevel = Field(
        default=ValidationLevel.BASIC, description="Validation strictness"
    )
    strategies: StrategyConfig = Field(
        default_factory=StrategyConfig, description="Document processing strategies"
    )

    def __getitem__(self, key: str):
        """Enable dictionary-like access to configuration values."""
        return getattr(self, key)

    def __eq__(self, other):
        """Enable equality comparison with dictionaries."""
        if isinstance(other, dict):
            return self.model_dump() == other
        return super().__eq__(other)

    @classmethod
    def get_default(cls) -> "PipelineConfig":
        """Get a new instance with default values."""
        return cls()

    @field_validator("input_dir")
    def validate_input_dir(cls, v: str) -> str:
        """Validate input directory exists if absolute path."""
        path = Path(v)
        if path.is_absolute() and not path.exists():
            # Create the directory if it doesn't exist
            path.mkdir(parents=True, exist_ok=True)
        # Always return forward slashes for cross-platform compatibility
        return str(path).replace("\\", "/")

    @field_validator("output_dir")
    def validate_output_dir(cls, v: str) -> str:
        """Validate output directory exists."""
        if not v.strip():
            raise ValueError("Output directory cannot be empty")
        path = Path(v)
        # Create the directory if it doesn't exist
        path.mkdir(parents=True, exist_ok=True)
        # Always return forward slashes for cross-platform compatibility
        return str(path).replace("\\", "/")

    @model_validator(mode="after")
    def validate_strategy_paths(self) -> "PipelineConfig":
        """Validate strategy paths are not empty."""
        for strategy_type, strategy in self.strategies.model_dump().items():
            if isinstance(strategy, str):
                if not strategy.strip():
                    raise ValueError(
                        f"Invalid strategy path for {strategy_type}: {strategy}"
                    )
            elif isinstance(strategy, dict):
                for component, path in strategy.items():
                    if not isinstance(path, str) or not path.strip():
                        raise ValueError(
                            f"Invalid {component} path for {strategy_type}: {path}"
                        )
        return self


def load_config(
    config_path: Optional[str] = None,
    config_dict: Optional[dict] = None,
    override_dict: Optional[dict] = None,
    use_env: bool = False,
) -> PipelineConfig:
    """
    Load configuration from various sources and merge them.

    The configuration is loaded in the following order (later sources override earlier ones):
    1. Default configuration (from PipelineConfig defaults)
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
        A validated PipelineConfig instance

    Raises:
        FileNotFoundError: If the configuration file does not exist
        yaml.YAMLError: If the configuration file contains invalid YAML
        ValidationError: If the configuration is invalid
    """
    # Start with empty config to be filled
    config_data = {}

    # Load from file if provided
    if config_path:
        config_data = _load_from_file(config_path)
    else:
        # Use config_dict if provided
        if config_dict:
            config_data = config_dict.copy()

        # Apply overrides if provided
        if override_dict:
            config_data = _merge_configs(config_data, override_dict)

    # Apply environment variables if requested
    if use_env:
        env_config = _load_from_env()
        config_data = _merge_configs(config_data, env_config)

    # Create and validate the configuration
    return PipelineConfig(**config_data)


def _load_from_file(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        return yaml.safe_load(f) or {}


def _load_from_env() -> dict:
    """Load configuration from environment variables."""
    config = {}

    for key, value in os.environ.items():
        if key.startswith(ENV_PREFIX):
            # Convert PIPELINE_INPUT_DIR to input_dir
            config_key = key[len(ENV_PREFIX) :].lower()

            # Handle nested keys (e.g., PIPELINE_STRATEGIES_PDF)
            if config_key.startswith("strategies_"):
                strategy_type = config_key[len("strategies_") :]
                if "strategies" not in config:
                    config["strategies"] = {}
                config["strategies"][strategy_type] = value
            else:
                # For any other keys, use as-is
                config[config_key] = value

    # Print environment variables for debugging
    print(f"Environment variables: {config}")

    return config


def _merge_configs(base: dict, override: dict) -> dict:
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
