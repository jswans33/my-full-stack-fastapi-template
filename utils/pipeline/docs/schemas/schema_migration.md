# Schema Migration System

The schema migration system provides a robust way to manage schema evolution over time. It supports:
- Versioned schema configurations
- Field additions, removals, and renames
- Custom field transformations
- Data migration between versions

## Migration Configuration

Migration configurations are YAML files stored in `config/migrations/` with the naming pattern `{schema_name}_{source_version}_to_{target_version}.yaml`.

Example migration configuration:
```yaml
name: invoice_v1_to_v1_1
source_version: "1.0.0"
target_version: "1.1.0"
description: "Update invoice schema to support additional payment fields"

# Fields to add
add_fields:
  - name: payment_method
    path: payment.method
    type: string
    required: true
    description: "Method of payment"
    validation: "value in ['credit_card', 'bank_transfer', 'cash', 'check']"

# Fields to remove
remove_fields:
  - payment_type  # Old field being replaced

# Fields to rename
rename_fields:
  transaction_id: payment_reference_id

# Field transformations
transform_fields:
  amount: "convert_to_decimal"
  currency: "normalize_currency_code"
```

## Field Transformations

The system supports custom field transformers for data migration. Transformers are Python functions that convert field values from one format to another.

Example transformer registration:
```python
def normalize_currency_code(code: str) -> str:
    code = code.upper().strip()
    if len(code) != 3:
        raise ValueError(f"Invalid currency code: {code}")
    return code

# Register the transformer
migrator.register_field_transformer("normalize_currency_code", normalize_currency_code)
```

## Usage Example

```python
# Initialize components
config_manager = ConfigurationManager()
registry = EnhancedSchemaRegistry(config_manager)
migrator = registry.migrator

# Register field transformers
migrator.register_field_transformer("convert_to_decimal", convert_to_decimal)

# Migrate schema
success = registry.migrate_schema("invoice", "1.0.0", "1.1.0")

# Transform data
old_data = {"amount": "99.99", "currency": "usd"}
new_data = migrator.transform_data(old_data, "invoice", "1.0.0", "1.1.0")
```

## Migration Process

1. **Configuration Loading**
   - Migration configurations are loaded from YAML files
   - Configurations are validated against the SchemaMigration model

2. **Schema Migration**
   - Source schema is loaded and validated
   - New fields are added
   - Specified fields are removed
   - Fields are renamed as configured
   - Migration is recorded in history

3. **Data Transformation**
   - Data is copied to prevent modification of source
   - Fields are removed/renamed according to configuration
   - Field transformers are applied to specified fields
   - Transformed data is validated against new schema

## Best Practices

1. **Version Naming**
   - Use semantic versioning (MAJOR.MINOR.PATCH)
   - Increment MAJOR for breaking changes
   - Increment MINOR for backwards-compatible additions
   - Increment PATCH for backwards-compatible fixes

2. **Field Transformers**
   - Keep transformers simple and focused
   - Handle edge cases and invalid inputs
   - Add validation where appropriate
   - Document expected input/output formats

3. **Testing**
   - Test migrations with sample data
   - Verify field transformations
   - Check edge cases and error conditions
   - Validate final data against new schema

4. **Documentation**
   - Document reasons for schema changes
   - Describe field transformations
   - Note any special handling requirements
   - Keep migration history for reference
