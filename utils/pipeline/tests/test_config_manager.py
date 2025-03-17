"""Tests for configuration manager."""

import os
import tempfile

import pytest
import yaml
from pydantic import BaseModel, ValidationError

from utils.pipeline.config import (
    ConfigurationManager,
    PipelineConfig,
    config_manager,
)
from utils.pipeline.config.providers.file import FileConfigurationProvider


class TestConfigModel(BaseModel):
    """Test configuration model."""

    name: str
    value: int


@pytest.fixture
def test_manager():
    """Create a test configuration manager."""
    manager = ConfigurationManager()
    return manager


@pytest.fixture
def test_config_file():
    """Create a temporary test configuration file."""
    config = {
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
        yaml.dump(config, f)
        config_path = f.name

    yield config_path

    if os.path.exists(config_path):
        os.unlink(config_path)


def test_register_model(test_manager):
    """Test registering a model with the configuration manager."""
    # Arrange
    config_name = "test_config"

    # Act
    config_manager.register_model(config_name, TestConfigModel)

    # Assert
    assert config_name in config_manager.model_registry
    assert config_manager.model_registry[config_name] == TestConfigModel


def test_get_config_as_model(test_manager):
    """Test getting configuration as a Pydantic model."""
    # Arrange
    config_name = "test_config"
    config_dict = {"name": "test", "value": 42}
    test_manager.register_model(config_name, TestConfigModel)
    test_manager.update_configuration(config_name, config_dict)

    # Act
    config = test_manager.get_config(config_name, as_model=True)

    # Assert
    assert isinstance(config, TestConfigModel)
    assert config.name == "test"
    assert config.value == 42


def test_get_config_invalid_model(test_manager):
    """Test error when getting configuration with invalid model."""
    # Arrange
    config_name = "test_config"
    config_dict = {"invalid": "data"}
    test_manager.register_model(config_name, TestConfigModel)

    # Act/Assert
    with pytest.raises(ValidationError):
        test_manager.update_configuration(config_name, config_dict)
        test_manager.get_config(config_name, as_model=True)


def test_get_config_unregistered_model(test_manager):
    """Test error when getting configuration with unregistered model."""
    # Arrange
    config_name = "unregistered"
    config_dict = {"name": "test", "value": 42}
    test_manager.update_configuration(config_name, config_dict)

    # Act/Assert
    with pytest.raises(ValueError, match="No model registered"):
        test_manager.get_config(config_name, as_model=True)


def test_helper_functions(test_config_file):
    """Test configuration helper functions."""
    # Set up a new manager with the test config
    manager = ConfigurationManager()
    provider = FileConfigurationProvider(base_dirs=[os.path.dirname(test_config_file)])
    provider.add_config_file("pipeline", os.path.basename(test_config_file))
    manager.register_provider(provider)
    manager.register_model("pipeline", PipelineConfig)

    # Act
    config = manager.get_config("pipeline", as_model=True)

    # Assert
    assert isinstance(config, PipelineConfig)
    assert config.input_dir == "test_input"
    assert config.output_dir == "test_output"
    assert config.output_format == "yaml"
    assert config.validation_level.value == "basic"


def test_config_hot_reload(test_manager):
    """Test configuration hot-reloading."""
    # Arrange
    config_name = "test_config"
    initial_config = {"name": "test", "value": 42}
    updated_config = {"name": "updated", "value": 100}
    changes_detected = []

    def on_change(event):
        changes_detected.append(event)

    test_manager.register_model(config_name, TestConfigModel)
    test_manager.register_listener(on_change, config_patterns=[config_name])
    test_manager.enable_auto_reload()  # Enable hot-reloading
    test_manager.update_configuration(config_name, initial_config)

    # Act
    test_manager.update_configuration(config_name, updated_config)

    # Assert
    assert len(changes_detected) == 2  # Two events: initial config and update
    # Check the second event (the update)
    event = changes_detected[1]
    assert event.config_name == config_name
    assert event.old_value["name"] == "test"
    assert event.new_value["name"] == "updated"

    # Cleanup
    test_manager.disable_auto_reload()


def test_config_validation(test_manager):
    """Test configuration validation with Pydantic models."""
    # Arrange
    config_name = "test_config"

    test_manager.register_model(config_name, TestConfigModel)

    # Act/Assert
    with pytest.raises(ValidationError):
        test_manager.get_config(config_name, as_model=True)


def test_config_merge(test_manager):
    """Test configuration merging from multiple providers."""
    # Arrange
    config_name = "test_config"
    base_config = {"name": "test", "value": 42}
    override_config = {"value": 100}

    test_manager.register_model(config_name, TestConfigModel)
    test_manager.update_configuration(config_name, base_config)

    # Act
    test_manager.update_configuration(config_name, override_config)
    config = test_manager.get_config(config_name, as_model=True)

    # Assert
    assert isinstance(config, TestConfigModel)
    assert config.name == "test"  # Preserved from base
    assert config.value == 100  # Updated from override
