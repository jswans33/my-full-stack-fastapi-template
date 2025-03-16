# Enhanced Configuration System

This directory contains the enhanced configuration management system for the document processing pipeline.

## Overview

The enhanced configuration system provides a flexible, modular approach to managing configuration settings for the document processing pipeline. It supports:

- Loading configuration from multiple sources (files, environment variables, etc.)
- Validating configuration using Pydantic models
- Merging configuration from different sources with priority handling
- Environment-specific configuration overrides
- Schema versioning and migration
- Runtime configuration updates

## Directory Structure

```
config/
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

## Quick Start

```python
from utils.pipeline.config import load_config, DocumentTypeConfig

# Load document type configuration
invoice_config = load_config("document_types/invoice")

# Validate using Pydantic model
document_type = DocumentTypeConfig(**invoice_config)

# Access validated fields
print(f"Document type: {document_type.name}")
print(f"Fields: {len(document_type.fields)}")
```

## Documentation

For more detailed information, see the following documentation:

- [Configuration System Guide](../docs/configuration_system.md): Comprehensive guide to the configuration system
- [Configuration Enhancement Checklist](../docs/configuration_enhancement_checklist.md): Implementation checklist
- [Configuration Enhancement Summary](../docs/configuration_enhancement_summary.md): Summary of completed and remaining work

## Examples

See the [config_example.py](../examples/config_example.py) script for examples of using the configuration system.

## Configuration Files Overview

The configuration directory contains several types of configuration files:

### Example Configurations
These files demonstrate available options and serve as templates:
- **example_config.yaml**: Comprehensive example of pipeline configuration options
- **example_classifier_config.yaml**: Example classifier configuration with standard document types

### Domain-Specific Configurations
These files are specialized for specific domains:
- **hvac_config.yaml**: Pipeline configuration optimized for HVAC documents
- **hvac_classifier_config.yaml**: Classifier configuration with HVAC-specific rules and patterns

### Output Format Configurations
These files control output formatting:
- **enhanced_markdown_config_v2.json**: Current configuration for enhanced markdown output

### System Configurations
These files configure system components:
- **schema_registry.yaml**: Configuration for the schema registry component

For a complete reference of all configuration files, see [CONFIG_FILES.md](CONFIG_FILES.md).
