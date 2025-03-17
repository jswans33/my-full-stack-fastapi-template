"""
Example demonstrating schema migration functionality.

This example shows how to:
1. Define migration configurations
2. Register custom field transformers
3. Execute schema migrations
4. Transform data between schema versions
"""

from decimal import Decimal
from pathlib import Path
from typing import Any

from utils.pipeline.config import config_manager
from utils.pipeline.config.providers.file import FileConfigurationProvider
from utils.pipeline.schema.enhanced_registry import EnhancedSchemaRegistry


def convert_to_decimal(value: Any) -> Decimal:
    """Convert a value to Decimal."""
    return Decimal(str(value))


def normalize_currency_code(code: str) -> str:
    """Normalize currency code to uppercase 3-letter code."""
    code = code.upper().strip()
    if len(code) != 3:
        raise ValueError(f"Invalid currency code: {code}")
    return code


def main():
    """Run the schema migration example."""
    # Use the default configuration manager

    # Initialize schema registry
    registry = EnhancedSchemaRegistry(config_manager)

    # Get the migrator instance
    migrator = registry.migrator

    # Register custom field transformers
    migrator.register_field_transformer("convert_to_decimal", convert_to_decimal)
    migrator.register_field_transformer(
        "normalize_currency_code", normalize_currency_code
    )

    # Example invoice data in version 1.0.0
    invoice_v1 = {
        "invoice_number": "INV-001",
        "payment_type": "credit",  # Old field to be removed
        "transaction_id": "TXN123",  # Field to be renamed
        "amount": "99.99",  # Field to be transformed to Decimal
        "currency": "usd",  # Field to be normalized
    }

    print("\nOriginal invoice data (v1.0.0):")
    print(invoice_v1)

    # Print available schemas
    print("\nAvailable schemas:")
    for schema_name, versions in registry.schema_versions.items():
        print(f"  {schema_name}: {list(versions.keys())}")

    # Print loaded schemas
    print("\nLoaded schemas:")
    for schema_id, schema in registry.schemas.items():
        print(f"  {schema_id}: {schema.get('name')} v{schema.get('schema_version')}")

    # Print registry config
    print("\nRegistry config:")
    print(f"  Config: {registry.config}")
    print(f"  Discovery paths: {registry.config.get('discovery', {}).get('paths', [])}")
    print(f"  Storage path: {registry.config.get('storage', {}).get('path', '')}")

    # Try to discover schemas
    print("\nTrying to discover schemas:")
    for path in registry.config.get("discovery", {}).get("paths", []):
        print(f"\nChecking path: {path}")
        patterns = registry.config.get("discovery", {}).get(
            "patterns", ["*.yaml", "*.yml", "*.json"]
        )
        for pattern in patterns:
            print(f"  Pattern: {pattern}")
            pattern_path = f"{path}/{pattern}"
            print(f"  Looking for: {pattern_path}")
            # Try to list files directly
            search_dir = Path(path)
            if search_dir.exists():
                print(f"  Directory exists: {search_dir}")
                for file_path in search_dir.glob(pattern):
                    print(f"  Found file: {file_path}")
                    if file_path.is_file():
                        print(f"  Loading file: {file_path}")
                        # Load the file
                        schema_data = config_manager.get_config(
                            str(file_path.relative_to(search_dir.parent))
                        )
                        print(f"  Data: {schema_data}")
                        if schema_data:
                            # Add to version history if it's a schema
                            schema_name = schema_data.get("name")
                            schema_version = schema_data.get("schema_version")
                            if schema_name and schema_version:
                                if schema_name not in registry.schema_versions:
                                    registry.schema_versions[schema_name] = {}
                                registry.schema_versions[schema_name][
                                    schema_version
                                ] = schema_data
                                print(
                                    f"  Added to version history: {schema_name} v{schema_version}"
                                )

                            # Test migration configuration if it's a migration
                            if (
                                "source_version" in schema_data
                                and "target_version" in schema_data
                                and "name" in schema_data
                            ):
                                migration_name = schema_data["name"]
                                print(
                                    f"  Found migration configuration: {migration_name}"
                                )
                                # Extract schema name from migration name
                                if migration_name.startswith("invoice_"):
                                    schema_name = "invoice"
                                    # Try to load it through the migrator
                                    migration_config = (
                                        registry.migrator.get_migration_config(
                                            schema_name,
                                            schema_data["source_version"],
                                            schema_data["target_version"],
                                        )
                                    )
                                    if migration_config:
                                        print("  Migration config loaded successfully")
                                    else:
                                        print("  Failed to load migration config")
                                        # Try to add the migration configuration directly
                                        # Save the migration configuration with the correct name
                                        migration_path = f"migrations/{schema_name}_{schema_data['source_version']}_to_{schema_data['target_version']}"
                                        print(
                                            f"  Adding migration config at: {migration_path}"
                                        )
                                        provider = next(
                                            provider
                                            for provider, _ in config_manager.providers
                                            if isinstance(
                                                provider, FileConfigurationProvider
                                            )
                                        )
                                        # Update the name to match the path
                                        schema_data["name"] = (
                                            f"{schema_name}_{schema_data['source_version']}_to_{schema_data['target_version']}"
                                        )
                                        provider.save_config(
                                            migration_path, schema_data
                                        )

    # Try to load the schema directly
    print("\nTrying to load schema directly:")
    file_provider = next(
        provider
        for provider, _ in config_manager.providers
        if isinstance(provider, FileConfigurationProvider)
    )
    for base_dir in file_provider.base_dirs:
        print(f"  Checking base dir: {base_dir}")
        schema_path = base_dir / "schemas" / "invoice_v1.yaml"
        print(f"  Looking for: {schema_path}")
        if schema_path.exists():
            print(f"  Found schema at: {schema_path}")
            schema_data = config_manager.get_config("schemas/invoice_v1")
            if schema_data:
                print(
                    f"  Schema loaded: {schema_data.get('name')} v{schema_data.get('schema_version')}"
                )
            else:
                print("  Failed to load schema")
        else:
            print("  Schema not found")

    # Migrate schema from v1.0.0 to v1.1.0
    success = registry.migrate_schema("invoice", "1.0.0", "1.1.0")
    if not success:
        print("Schema migration failed!")
        return

    # Transform data using the migrated schema
    transformed_data = migrator.transform_data(invoice_v1, "invoice", "1.0.0", "1.1.0")

    if transformed_data:
        print("\nTransformed invoice data (v1.1.0):")
        print(transformed_data)

        # Verify transformations
        assert "payment_type" not in transformed_data  # Removed field
        assert transformed_data["payment_reference_id"] == "TXN123"  # Renamed field
        assert isinstance(transformed_data["amount"], Decimal)  # Transformed to Decimal
        assert transformed_data["currency"] == "USD"  # Normalized currency code
    else:
        print("Data transformation failed!")


if __name__ == "__main__":
    main()
