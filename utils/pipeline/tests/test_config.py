"""
Tests for the configuration module.

This file demonstrates TDD approach for the configuration module.
"""

import os
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from config.config import LogLevel, PipelineConfig, load_config


def test_default_config():
    """Test that the default configuration is returned when no config file is provided."""
    config = load_config()
    default = PipelineConfig.get_default()
    assert config == default
    assert config is not default  # Should be a different instance


def test_load_config_from_file(temp_dir):
    """Test loading configuration from a YAML file."""
    # Create a test configuration
    test_config = {
        "input_dir": "test/input",
        "output_dir": "test/output",
        "log_level": "DEBUG",
        "strategies": {
            "pdf": "custom.pdf_strategy",
            "excel": "custom.excel_strategy",
        },
    }

    # Write the test configuration to a temporary file
    config_path = os.path.join(temp_dir, "test_config.yaml")
    with open(config_path, "w") as f:
        yaml.dump(test_config, f)

    # Load the configuration from the file
    config = load_config(config_path)

    # Verify the loaded configuration
    assert config.input_dir == "test/input"
    assert config.output_dir == "test/output"
    assert config.log_level == "DEBUG"
    assert config.strategies.pdf == "custom.pdf_strategy"
    assert config.strategies.excel == "custom.excel_strategy"


def test_load_config_with_invalid_file():
    """Test that an error is raised when an invalid config file is provided."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent_file.yaml")


def test_load_config_with_invalid_yaml(temp_dir):
    """Test that an error is raised when the config file contains invalid YAML."""
    # Create an invalid YAML file
    config_path = os.path.join(temp_dir, "invalid_config.yaml")
    with open(config_path, "w") as f:
        f.write("invalid: yaml: content: - [")

    with pytest.raises(yaml.YAMLError):
        load_config(config_path)


def test_config_validation():
    """Test that the configuration is validated."""
    # Create an invalid configuration (empty required field)
    invalid_config = {
        "input_dir": "test/input",
        "output_dir": "",  # Empty output_dir should fail validation
    }

    with pytest.raises(ValueError, match="Output directory cannot be empty"):
        load_config(config_dict=invalid_config)

    # Test with None value
    invalid_config2 = {
        "input_dir": "test/input",
        "output_dir": None,  # None output_dir should fail validation
    }

    with pytest.raises(ValidationError):
        load_config(config_dict=invalid_config2)


def test_config_with_environment_variables(temp_dir):
    """Test that environment variables can override configuration values."""
    # Create a temporary directory for the test
    env_input_dir = Path(temp_dir) / "env_input"
    env_input_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Set environment variables with valid paths
        os.environ["PIPELINE_INPUT_DIR"] = str(env_input_dir)
        os.environ["PIPELINE_LOG_LEVEL"] = "ERROR"

        # Load configuration with environment variable support
        config = load_config(use_env=True)

        # Verify that environment variables override default values
        # Convert both paths to forward slashes for comparison
        expected_path = str(env_input_dir).replace("\\", "/")
        assert config.input_dir == expected_path
        assert config.log_level == "ERROR"

        # Verify that other values are still defaults
        default = PipelineConfig.get_default()
        assert config.output_format == default.output_format

    finally:
        # Clean up environment variables
        if "PIPELINE_INPUT_DIR" in os.environ:
            del os.environ["PIPELINE_INPUT_DIR"]
        if "PIPELINE_LOG_LEVEL" in os.environ:
            del os.environ["PIPELINE_LOG_LEVEL"]


def test_merge_configs():
    """Test that configurations can be merged."""
    base_config = {
        "input_dir": "base/input",
        "output_dir": "base/output",
        "log_level": "INFO",
        "strategies": {
            "pdf": "base.pdf_strategy",
            "excel": "base.excel_strategy",
        },
    }

    override_config = {
        "input_dir": "override/input",
        "log_level": "DEBUG",
        "strategies": {
            "pdf": "override.pdf_strategy",
            "word": "override.word_strategy",
        },
    }

    # Merge the configurations
    merged_config = load_config(config_dict=base_config, override_dict=override_config)

    # Verify the merged configuration
    assert merged_config.input_dir == "override/input"  # Overridden
    assert merged_config.output_dir == "base/output"  # Not overridden
    assert merged_config.log_level == "DEBUG"  # Overridden

    # Verify that nested dictionaries are merged correctly
    assert merged_config.strategies.pdf == "override.pdf_strategy"  # Overridden
    assert merged_config.strategies.excel == "base.excel_strategy"  # Not overridden
    assert merged_config.strategies.word == "override.word_strategy"  # Added


def test_config_dictionary_access():
    """Test that configuration can be accessed like a dictionary."""
    config = PipelineConfig(
        input_dir="test/input",
        output_dir="test/output",
        log_level=LogLevel.DEBUG,
    )

    # Test dictionary-like access
    assert config["input_dir"] == "test/input"
    assert config["output_dir"] == "test/output"
    assert config["log_level"] == LogLevel.DEBUG

    # Test equality with dictionary
    assert config == {
        "input_dir": "test/input",
        "output_dir": "test/output",
        "log_level": "DEBUG",
        "output_format": "yaml",
        "validation_level": "basic",
        "strategies": {
            "pdf": "strategies.pdf",
            "excel": "strategies.excel",
            "word": "strategies.word",
            "text": "strategies.text",
        },
    }
