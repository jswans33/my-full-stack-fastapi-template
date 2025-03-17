"""
Configuration module for the pipeline.
"""


from .config import (
    PipelineConfig,
)
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
    """Create a new configuration manager with default providers."""
    manager = ConfigurationManager()

    file_provider = FileConfigurationProvider(
        base_dirs=["utils/pipeline/config", "config"]
    )
    manager.register_provider(file_provider, priority=100)

    env_provider = EnvironmentConfigurationProvider(prefix="PIPELINE_")
    manager.register_provider(env_provider, priority=50)

    return manager


# Create and configure the default configuration manager
def create_default_manager() -> ConfigurationManager:
    """Create and configure the default configuration manager."""
    manager = ConfigurationManager()

    # Register file provider (highest priority)
    file_provider = FileConfigurationProvider(
        base_dirs=["utils/pipeline/config", "config"]
    )
    manager.register_provider(file_provider, priority=100)

    # Register environment provider (lower priority)
    env_provider = EnvironmentConfigurationProvider(prefix="PIPELINE_")
    manager.register_provider(env_provider, priority=50)

    # Register models
    manager.register_model("pipeline", PipelineConfig)
    manager.register_model("document_type", DocumentTypeConfig)
    manager.register_model("environment", EnvironmentConfig)
    manager.register_model("processor", ProcessorConfig)
    manager.register_model("schema", SchemaConfig)

    return manager


# Default configuration manager instance
config_manager = create_default_manager()


def get_pipeline_config() -> PipelineConfig:
    """Get validated pipeline configuration."""
    config = config_manager.get_config("pipeline", as_model=True)
    assert isinstance(config, PipelineConfig)
    return config


def get_document_type_config() -> DocumentTypeConfig:
    """Get validated document type configuration."""
    config = config_manager.get_config("document_type", as_model=True)
    assert isinstance(config, DocumentTypeConfig)
    return config


def get_environment_config() -> EnvironmentConfig:
    """Get validated environment configuration."""
    config = config_manager.get_config("environment", as_model=True)
    assert isinstance(config, EnvironmentConfig)
    return config


def get_processor_config() -> ProcessorConfig:
    """Get validated processor configuration."""
    config = config_manager.get_config("processor", as_model=True)
    assert isinstance(config, ProcessorConfig)
    return config


def get_schema_config() -> SchemaConfig:
    """Get validated schema configuration."""
    config = config_manager.get_config("schema", as_model=True)
    assert isinstance(config, SchemaConfig)
    return config


__all__ = [
    # Configuration manager
    "ConfigurationManager",
    "config_manager",
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
    # Helper functions
    "get_pipeline_config",
    "get_document_type_config",
    "get_environment_config",
    "get_processor_config",
    "get_schema_config",
]
