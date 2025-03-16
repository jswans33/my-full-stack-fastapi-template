"""
Configuration module for the pipeline.

This module provides functions and classes for loading and managing configuration settings.
"""

# Legacy configuration (for backward compatibility)
from .config import PipelineConfig
from .config import load_config as load_legacy_config

# New configuration system
from .manager import ConfigurationManager
from .models.base import BaseConfig
from .models.document_type import DocumentField, DocumentRule, DocumentTypeConfig
from .models.environment import EnvironmentConfig
from .models.processor import ProcessorComponentConfig, ProcessorConfig
from .models.schema import SchemaConfig, SchemaField, SchemaMigration, SchemaValidation
from .providers.base import ConfigurationProvider
from .providers.env import EnvironmentConfigurationProvider
from .providers.file import FileConfigurationProvider


def create_configuration_manager() -> ConfigurationManager:
    """
    Create a new configuration manager with default providers.

    Returns:
        Configured ConfigurationManager instance
    """
    manager = ConfigurationManager()

    # Register file provider (highest priority)
    file_provider = FileConfigurationProvider(
        base_dirs=["utils/pipeline/config", "config"]
    )
    manager.register_provider(file_provider, priority=100)

    # Register environment provider (lower priority)
    env_provider = EnvironmentConfigurationProvider(prefix="PIPELINE_")
    manager.register_provider(env_provider, priority=50)

    return manager


# Default configuration manager instance
config_manager = create_configuration_manager()


def load_config(config_name: str) -> dict:
    """
    Load configuration by name using the default configuration manager.

    Args:
        config_name: Name of the configuration to load

    Returns:
        Configuration dictionary
    """
    return config_manager.get_config(config_name)


__all__ = [
    # Legacy configuration
    "PipelineConfig",
    "load_legacy_config",
    # Configuration manager
    "ConfigurationManager",
    "config_manager",
    "load_config",
    "create_configuration_manager",
    # Configuration providers
    "ConfigurationProvider",
    "FileConfigurationProvider",
    "EnvironmentConfigurationProvider",
    # Configuration models
    "BaseConfig",
    "DocumentField",
    "DocumentRule",
    "DocumentTypeConfig",
    "EnvironmentConfig",
    "ProcessorComponentConfig",
    "ProcessorConfig",
    "SchemaConfig",
    "SchemaField",
    "SchemaValidation",
    "SchemaMigration",
]
