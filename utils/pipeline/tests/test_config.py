"""
Tests for the configuration module.

This file demonstrates TDD approach for the configuration module.
"""

import os

import pytest
import yaml

from config.config import DEFAULT_CONFIG, load_config


def test_default_config():
    """Test that the default configuration is returned when no config file is provided."""
    config = load_config()
    assert config == DEFAULT_CONFIG
    assert config is not DEFAULT_CONFIG  # Should be a copy, not the same object


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
    assert config == test_config


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

    with pytest.raises(ValueError, match="output_dir"):
        load_config(config_dict=invalid_config)

    # Test with None value
    invalid_config2 = {
        "input_dir": "test/input",
        "output_dir": None,  # None output_dir should fail validation
    }

    with pytest.raises(ValueError, match="output_dir"):
        load_config(config_dict=invalid_config2)


def test_config_with_environment_variables(monkeypatch):
    """Test that environment variables can override configuration values."""
    # Set environment variables
    monkeypatch.setenv("PIPELINE_INPUT_DIR", "/env/input")
    monkeypatch.setenv("PIPELINE_LOG_LEVEL", "ERROR")

    # Load configuration with environment variable support
    config = load_config(use_env=True)

    # Verify that environment variables override default values
    assert config["input_dir"] == "/env/input"
    assert config["log_level"] == "ERROR"

    # Verify that other values are still from the default config
    assert config["output_format"] == DEFAULT_CONFIG["output_format"]


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
    assert merged_config["input_dir"] == "override/input"  # Overridden
    assert merged_config["output_dir"] == "base/output"  # Not overridden
    assert merged_config["log_level"] == "DEBUG"  # Overridden

    # Verify that nested dictionaries are merged correctly
    assert merged_config["strategies"]["pdf"] == "override.pdf_strategy"  # Overridden
    assert (
        merged_config["strategies"]["excel"] == "base.excel_strategy"
    )  # Not overridden
    assert merged_config["strategies"]["word"] == "override.word_strategy"  # Added
