# Enhanced Configuration System

This document provides a comprehensive guide to the enhanced configuration management system for the document processing pipeline.

## Overview

The enhanced configuration system provides a flexible, modular approach to managing configuration settings for the document processing pipeline. It supports:

- Loading configuration from multiple sources (files, environment variables, etc.)
- Validating configuration using Pydantic models
- Merging configuration from different sources with priority handling
- Environment-specific configuration overrides
- Schema versioning and migration
- Runtime configuration updates

## Architecture

The configuration system is built around the following components:

- **ConfigurationManager**: Central service for loading and managing configurations
- **ConfigurationProvider**: Interface for loading configuration from different sources
- **Configuration Models**: Pydantic models for validating configuration
- **Schema Registry**: Enhanced registry for managing document schemas

### Directory Structure

```
utils/pipeline/config/
├── __init__.py                # Package initialization
├── manager.py                 # ConfigurationManager implementation
├── providers/                 # Configuration providers
│   ├── __init__.py
│   ├── base.py                # Provider base class
│   ├── file.py                # File-based provider
│   └── env.py                 # Environment provider
├── models/                    # Configuration models
│   ├── __init__.py
│   ├── base.py                # Base configuration model
│   ├── document_type.py       # Document type configuration
│   ├── schema.py              # Schema configuration
│   ├── processor.py           # Processor configuration
│   └── environment.py         # Environment configuration
├── document_types/            # Document type configurations
│   └── invoice.yaml           # Example invoice document type
├── schemas/                   # Schema configurations
│   └── invoice_v1.yaml        # Example invoice schema
├── environments/              # Environment-specific configurations
│   └── development.yaml       # Example development environment
└── migrations/                # Schema migration configurations
    └── invoice_v1_to_v2.yaml  # Example schema migration
```

## Configuration Files

The configuration system uses YAML or JSON files for storing configuration. The files are organized into the following directories:

- **document_types/**: Document type definitions
- **schemas/**: Schema definitions
- **environments/**: Environment-specific overrides
- **migrations/**: Schema migration definitions

### Document Type Configuration

Document type configurations define the structure and validation rules for document types. Example:

```yaml
name: INVOICE
version: "1.0"
description: "Invoice document type configuration"

fields:
  - name: invoice_number
    type: string
    required: true
    description: "Invoice number"
    patterns:
      - "INV-\\d+"
      - "Invoice #\\d+"

rules:
  - name: validate_total
    description: "Validate that total = subtotal + tax"
    condition: "total_amount == subtotal + tax_amount"
    action: "warn"
```

### Schema Configuration

Schema configurations define how to extract and validate data from documents. Example:

```yaml
name: invoice_standard
document_type: INVOICE
version: "1.0"
schema_version: "1.0"
description: "Standard invoice schema configuration"

fields:
  - name: invoice_number
    path: "metadata.invoice_number"
    type: string
    required: true
    validation: "regex('^(INV-\\d+|Invoice #\\d+)$')"

validations:
  - name: validate_total
    description: "Validate that total = subtotal + tax"
    condition: "abs(total_amount - (subtotal + tax_amount)) < 0.01"
    message: "Total amount does not match subtotal + tax"
    level: "warning"
```

### Environment Configuration

Environment configurations define environment-specific overrides. Example:

```yaml
name: development
version: "1.0"
description: "Development environment configuration"

overrides:
  # Override pipeline settings for development
  pipeline:
    log_level: "DEBUG"
    validation_level: "basic"
  
  # Override schema settings for development
  schemas:
    invoice_standard:
      validations:
        - name: validate_line_items
          level: "warning"  # Downgrade from error to warning
```

### Migration Configuration

Migration configurations define how to migrate from one schema version to another. Example:

```yaml
source_version: "1.0"
target_version: "2.0"
version: "1.0"
description: "Migration from invoice schema v1 to v2"

# Fields to add in v2
add_fields:
  - name: payment_terms
    path: "metadata.payment_terms"
    type: string
    required: false
    description: "Payment terms (e.g., Net 30)"

# Fields to rename in v2
rename_fields:
  subtotal: "subtotal_amount"  # More consistent naming
```

## Using the Configuration System

### Loading Configuration

The configuration system provides a simple interface for loading configuration:

```python
from utils.pipeline.config import load_config

# Load document type configuration
invoice_config = load_config("document_types/invoice")

# Load schema configuration
schema_config = load_config("schemas/invoice_v1")

# Load environment configuration
env_config = load_config("environments/development")
```

### Validating Configuration

The configuration system provides Pydantic models for validating configuration:

```python
from utils.pipeline.config import DocumentTypeConfig, SchemaConfig

# Load document type configuration
invoice_config = load_config("document_types/invoice")

# Validate using Pydantic model
document_type = DocumentTypeConfig(**invoice_config)

# Access validated fields
print(f"Document type: {document_type.name}")
print(f"Fields: {len(document_type.fields)}")
```

### Environment Overrides

The configuration system supports environment-specific overrides:

```python
from utils.pipeline.config import config_manager, load_config

# Load base configuration
base_config = load_config("schemas/invoice_v1")

# Load environment configuration
env_config = load_config("environments/development")

# Get schema overrides from environment
schema_overrides = env_config.get("overrides", {}).get("schemas", {}).get("invoice_standard", {})

# Apply overrides
merged_config = config_manager._deep_merge(base_config, schema_overrides)
```

### Custom Configuration Manager

You can create a custom configuration manager with specific providers:

```python
from pathlib import Path
from utils.pipeline.config import ConfigurationManager, FileConfigurationProvider

# Create a custom configuration manager
custom_manager = ConfigurationManager()

# Register a file provider with a custom directory
custom_dir = Path(__file__).parent.parent / "config"
file_provider = FileConfigurationProvider(base_dirs=[str(custom_dir)])
custom_manager.register_provider(file_provider)

# Load configuration using the custom manager
invoice_config = custom_manager.get_config("document_types/invoice")
```

### Runtime Updates

The configuration system supports updating configuration at runtime:

```python
from utils.pipeline.config import config_manager, load_config

# Load document type configuration
invoice_config = load_config("document_types/invoice")

# Update configuration at runtime
updates = {
    "fields": [
        {
            "name": "payment_method",
            "type": "string",
            "required": False,
            "description": "Payment method"
        }
    ]
}

# Apply updates
config_manager.update_configuration("document_types/invoice", updates)

# Load updated configuration
updated_config = load_config("document_types/invoice")
```

## Schema Registry Integration

The configuration system integrates with the schema registry to provide schema versioning and migration support:

```python
from utils.pipeline.schema.enhanced_registry import EnhancedSchemaRegistry
from utils.pipeline.config import config_manager

# Create enhanced schema registry
registry = EnhancedSchemaRegistry(config_manager)

# Load schemas from configuration
registry.load_schemas()

# Get schema by name and version
schema = registry.get_schema_version("invoice_standard", "1.0")

# Migrate schema to new version
registry.migrate_schema("invoice_standard", "1.0", "2.0")
```

## Best Practices

### Configuration Organization

- Use a consistent naming convention for configuration files
- Group related configurations in the same directory
- Use descriptive names for configuration files
- Include version information in configuration files

### Configuration Validation

- Always validate configuration using Pydantic models
- Define validation rules for all required fields
- Use default values for optional fields
- Include descriptive error messages for validation failures

### Environment Overrides

- Keep environment-specific overrides separate from base configuration
- Only override settings that need to be different in each environment
- Use a consistent structure for environment overrides
- Document environment-specific settings

### Schema Versioning

- Use semantic versioning for schema versions
- Document changes between schema versions
- Provide migration paths between schema versions
- Test schema migrations thoroughly

## Examples

See the `utils/pipeline/examples/config_example.py` script for examples of using the configuration system.

## Troubleshooting

### Common Issues

- **Configuration not found**: Check that the configuration file exists in the expected location and has the correct name.
- **Validation errors**: Check that the configuration file has the correct structure and all required fields.
- **Environment overrides not applied**: Check that the environment configuration file has the correct structure and the overrides are in the correct location.
- **Schema migration failures**: Check that the migration configuration is correct and the source and target schema versions exist.

### Debugging

- Set the log level to DEBUG to see more detailed information about configuration loading and validation.
- Use the `print_config` function to print the configuration that was loaded.
- Check the configuration files for syntax errors or missing fields.
- Validate configuration files using the Pydantic models directly.
