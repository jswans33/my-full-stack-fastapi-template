"""
Configuration system example.

This script demonstrates how to use the enhanced configuration system.
"""

import json
from pathlib import Path

from ..config import (
    ConfigurationManager,
    DocumentTypeConfig,
    FileConfigurationProvider,
    config_manager,
    load_config,
)


def print_separator(title: str) -> None:
    """Print a separator with a title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def example_load_config() -> None:
    """Example of loading configuration using the default configuration manager."""
    print_separator("Loading Configuration")

    # Load document type configuration
    print("Loading document type configuration:")
    invoice_config = load_config("document_types/invoice")
    print(json.dumps(invoice_config, indent=2))

    # Load schema configuration
    print("\nLoading schema configuration:")
    schema_config = load_config("schemas/invoice_v1")
    print(json.dumps(schema_config, indent=2))

    # Load environment configuration
    print("\nLoading environment configuration:")
    env_config = load_config("environments/development")
    print(json.dumps(env_config, indent=2))

    # Load migration configuration
    print("\nLoading migration configuration:")
    migration_config = load_config("migrations/invoice_v1_to_v2")
    print(json.dumps(migration_config, indent=2))


def example_validate_config() -> None:
    """Example of validating configuration using Pydantic models."""
    print_separator("Validating Configuration")

    # Load document type configuration
    invoice_config = load_config("document_types/invoice")

    # Validate using Pydantic model
    try:
        document_type = DocumentTypeConfig(**invoice_config)
        print(f"Document type '{document_type.name}' is valid")
        print(f"Fields: {len(document_type.fields)}")
        print(f"Rules: {len(document_type.rules)}")

        # Access specific fields
        for field in document_type.fields:
            print(f"Field: {field.name} ({field.type}), Required: {field.required}")

    except Exception as e:
        print(f"Error validating document type: {str(e)}")


def example_environment_overrides() -> None:
    """Example of applying environment-specific overrides."""
    print_separator("Environment Overrides")

    # Load base configuration
    base_config = load_config("schemas/invoice_v1")
    print("Base configuration:")
    print(json.dumps(base_config, indent=2))

    # Load environment configuration
    env_config = load_config("environments/development")

    # Get schema overrides from environment
    schema_overrides = (
        env_config.get("overrides", {}).get("schemas", {}).get("invoice_standard", {})
    )
    print("\nEnvironment overrides:")
    print(json.dumps(schema_overrides, indent=2))

    # Apply overrides
    merged_config = config_manager._deep_merge(base_config, schema_overrides)
    print("\nMerged configuration:")
    print(json.dumps(merged_config, indent=2))


def example_custom_config_manager() -> None:
    """Example of creating a custom configuration manager."""
    print_separator("Custom Configuration Manager")

    # Create a custom configuration manager
    custom_manager = ConfigurationManager()

    # Register a file provider with a custom directory
    custom_dir = Path(__file__).parent.parent / "config"
    file_provider = FileConfigurationProvider(base_dirs=[str(custom_dir)])
    custom_manager.register_provider(file_provider)

    # Load configuration using the custom manager
    invoice_config = custom_manager.get_config("document_types/invoice")
    print("Invoice configuration loaded from custom manager:")
    print(json.dumps(invoice_config, indent=2))


def example_runtime_updates() -> None:
    """Example of updating configuration at runtime."""
    print_separator("Runtime Updates")

    # Load document type configuration
    invoice_config = load_config("document_types/invoice")
    print("Original configuration:")
    print(json.dumps(invoice_config, indent=2))

    # Update configuration at runtime
    updates = {
        "fields": [
            {
                "name": "payment_method",
                "type": "string",
                "required": False,
                "description": "Payment method",
            }
        ]
    }

    # Apply updates
    config_manager.update_configuration("document_types/invoice", updates)

    # Load updated configuration
    updated_config = load_config("document_types/invoice")
    print("\nUpdated configuration:")
    print(json.dumps(updated_config, indent=2))


def main() -> None:
    """Run the configuration examples."""
    print_separator("Configuration System Examples")

    # Run examples
    example_load_config()
    example_validate_config()
    example_environment_overrides()
    example_custom_config_manager()
    example_runtime_updates()


if __name__ == "__main__":
    main()
