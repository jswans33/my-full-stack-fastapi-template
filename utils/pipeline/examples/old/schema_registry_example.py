"""
Enhanced schema registry example.

This script demonstrates how to use the enhanced schema registry.
"""

from typing import Any, Dict, Optional

from utils.pipeline.config import config_manager
from utils.pipeline.schema.enhanced_registry import EnhancedSchemaRegistry


def print_separator(title: str) -> None:
    """Print a separator with a title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def print_schema(schema: Optional[Dict[str, Any]]) -> None:
    """Print a schema in a readable format."""
    if not schema:
        print("Schema not found")
        return

    print(f"Name: {schema.get('name')}")
    print(f"Document Type: {schema.get('document_type')}")
    print(f"Version: {schema.get('schema_version')}")

    if schema.get("inherits"):
        print(f"Inherits: {schema.get('inherits')}")

    print(f"Fields: {len(schema.get('fields', []))}")
    print(f"Validations: {len(schema.get('validations', []))}")

    print("\nFields:")
    for field in schema.get("fields", []):
        print(
            f"  - {field.get('name')} ({field.get('type')}): {field.get('description')}"
        )

    print("\nValidations:")
    for validation in schema.get("validations", []):
        print(
            f"  - {validation.get('name')}: {validation.get('message')} ({validation.get('level')})"
        )


def example_load_schemas() -> None:
    """Example of loading schemas from configuration."""
    print_separator("Loading Schemas")

    # Create enhanced schema registry with configuration manager
    registry = EnhancedSchemaRegistry(config_manager)

    # List all schemas
    schemas = registry.list_schemas()
    print(f"Loaded {len(schemas)} schemas:")

    for schema in schemas:
        print(f"- {schema.get('name')} (version {schema.get('schema_version')})")


def example_schema_versions() -> None:
    """Example of accessing schema versions."""
    print_separator("Schema Versions")

    # Create enhanced schema registry with configuration manager
    registry = EnhancedSchemaRegistry(config_manager)

    # Get schema by name and version
    schema_name = "invoice_standard"

    # Get latest version
    latest_schema = registry.get_schema_version(schema_name, "latest")
    print(f"Latest version of {schema_name}:")
    print_schema(latest_schema)

    # Get specific version
    version = "1.0"
    specific_schema = registry.get_schema_version(schema_name, version)
    print(f"\nVersion {version} of {schema_name}:")
    print_schema(specific_schema)


def example_schema_inheritance() -> None:
    """Example of schema inheritance."""
    print_separator("Schema Inheritance")

    # Create enhanced schema registry with configuration manager
    registry = EnhancedSchemaRegistry(config_manager)

    # Get parent schema
    parent_name = "financial_document"
    parent_schema = registry.get_schema_version(parent_name, "latest")
    print(f"Parent schema {parent_name}:")
    print_schema(parent_schema)

    # Get child schema
    child_name = "invoice_standard"
    child_schema = registry.get_schema_version(child_name, "latest")
    print(f"\nChild schema {child_name} (inherits from {parent_name}):")
    print_schema(child_schema)


def example_schema_migration() -> None:
    """Example of schema migration."""
    print_separator("Schema Migration")

    # Create enhanced schema registry with configuration manager
    registry = EnhancedSchemaRegistry(config_manager)

    # Get schema to migrate
    schema_name = "invoice_standard"
    source_version = "1.0"
    target_version = "2.0"

    # Get source schema
    source_schema = registry.get_schema_version(schema_name, source_version)
    print(f"Source schema {schema_name} version {source_version}:")
    print_schema(source_schema)

    # Migrate schema
    success = registry.migrate_schema(schema_name, source_version, target_version)

    if success:
        print(
            f"\nSuccessfully migrated {schema_name} from {source_version} to {target_version}"
        )

        # Get target schema
        target_schema = registry.get_schema_version(schema_name, target_version)
        print(f"\nTarget schema {schema_name} version {target_version}:")
        print_schema(target_schema)
    else:
        print(
            f"\nFailed to migrate {schema_name} from {source_version} to {target_version}"
        )


def example_save_schema() -> None:
    """Example of saving a schema configuration."""
    print_separator("Saving Schema")

    # Create enhanced schema registry with configuration manager
    registry = EnhancedSchemaRegistry(config_manager)

    # Create a new schema
    schema = {
        "name": "purchase_order",
        "document_type": "PURCHASE_ORDER",
        "schema_version": "1.0",
        "inherits": "financial_document",
        "description": "Purchase order schema",
        "fields": [
            {
                "name": "po_number",
                "path": "metadata.po_number",
                "type": "string",
                "required": True,
                "description": "Purchase order number",
            },
            {
                "name": "order_date",
                "path": "metadata.order_date",
                "type": "date",
                "required": True,
                "description": "Order date",
            },
        ],
        "validations": [
            {
                "name": "validate_po_number",
                "condition": "po_number.startswith('PO-')",
                "message": "Purchase order number must start with 'PO-'",
                "level": "error",
            }
        ],
    }

    # Save schema
    success = registry.save_schema_config(schema)

    if success:
        print(f"Successfully saved schema {schema['name']}")

        # Get saved schema
        saved_schema = registry.get_schema_version(
            schema["name"], schema["schema_version"]
        )
        print("\nSaved schema:")
        print_schema(saved_schema)
    else:
        print(f"Failed to save schema {schema['name']}")


def main() -> None:
    """Run the schema registry examples."""
    print_separator("Enhanced Schema Registry Examples")

    # Run examples
    example_load_schemas()
    example_schema_versions()
    example_schema_inheritance()
    example_schema_migration()
    example_save_schema()


if __name__ == "__main__":
    main()
