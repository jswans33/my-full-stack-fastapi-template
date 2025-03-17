# Configuration System Migration Guide

This guide explains how to migrate from the legacy configuration system to the new ConfigurationManager-based system.

## Why Migrate?

The new configuration system offers several advantages:

1. **Hot-reloading**: Configuration changes are automatically detected and applied
2. **Validation**: Strong type checking and validation through Pydantic models
3. **Flexibility**: Multiple configuration providers with priority-based merging
4. **Change Tracking**: Track and audit configuration changes
5. **Event System**: Subscribe to configuration changes

## Migration Steps

### 1. Update Imports

```python
# Before
from utils.pipeline.config.config import load_config

# After - Use type-specific helpers
from utils.pipeline.config import get_pipeline_config  # For pipeline config
from utils.pipeline.config import get_document_type_config  # For document type config
# ... or for generic configs:
from utils.pipeline.config import load_config
```

### 2. Update Configuration Loading

```python
# Before
config = load_config(
    config_path="path/to/config.yaml",
    use_env=True
)

# After - Using type-specific helpers
config = get_pipeline_config()  # Returns PipelineConfig instance

# Or for generic configs
config = load_config("pipeline", as_model=True)  # Returns validated model
```

### 3. Working with Configuration Values

```python
# Before
config = load_config("config.yaml")
input_dir = config.input_dir
validation_level = config.validation_level

# After - Type-safe access with IDE support
config = get_pipeline_config()
input_dir = config.input_dir  # IDE autocomplete works
validation_level = config.validation_level  # Type checking works
```

### 4. Subscribing to Configuration Changes

```python
from utils.pipeline.config import config_manager

def on_config_changed(event):
    print(f"Configuration {event.config_name} changed")
    print(f"Old value: {event.old_value}")
    print(f"New value: {event.new_value}")

# Register for all pipeline config changes
config_manager.register_listener(
    on_config_changed,
    config_patterns=["pipeline"]
)

# Register for specific change types
config_manager.register_listener(
    on_config_changed,
    config_patterns=["pipeline"],
    change_types=["update", "reload"]
)
```

### 5. Environment Variables

Environment variables are now handled through a dedicated provider:

```python
# Before - Manual environment variable handling
config = load_config(use_env=True)

# After - Automatic through EnvironmentConfigurationProvider
# Environment variables with prefix PIPELINE_ are automatically loaded
# Example: PIPELINE_INPUT_DIR sets input_dir
# No code changes needed - handled by configuration manager
```

### 6. Custom Configuration Types

```python
from pydantic import BaseModel
from utils.pipeline.config import config_manager

class MyCustomConfig(BaseModel):
    name: str
    value: int
    enabled: bool = False

# Register your model
config_manager.register_model("my_custom", MyCustomConfig)

# Use it
config = config_manager.get_config("my_custom", as_model=True)
```

## Best Practices

1. **Use Type-Specific Helpers**: Prefer `get_pipeline_config()`, `get_document_type_config()`, etc. over generic `load_config()` when possible.

2. **Validate Early**: Register models for all your configuration types to ensure validation at load time.

3. **Handle Changes**: Use the event system to react to configuration changes instead of polling or manual reloading.

4. **Environment Variables**: Use the standard PIPELINE_ prefix for environment variables to ensure they're picked up automatically.

## Example: Complete Migration

```python
# Before
from utils.pipeline.config.config import load_config

class DocumentProcessor:
    def __init__(self, config_path=None):
        self.config = load_config(
            config_path=config_path,
            use_env=True
        )
        self.input_dir = self.config.input_dir
        self.validation_level = self.config.validation_level

# After
from utils.pipeline.config import get_pipeline_config, config_manager

class DocumentProcessor:
    def __init__(self):
        # Get typed configuration
        self.config = get_pipeline_config()
        self.input_dir = self.config.input_dir
        self.validation_level = self.config.validation_level
        
        # Subscribe to changes
        config_manager.register_listener(
            self._on_config_changed,
            config_patterns=["pipeline"]
        )
    
    def _on_config_changed(self, event):
        # Update configuration when it changes
        self.config = get_pipeline_config()
        self.input_dir = self.config.input_dir
        self.validation_level = self.config.validation_level
```

## Deprecation Timeline

1. The legacy `load_config` function is marked as deprecated but still available for backward compatibility.
2. It will be removed in a future version (estimated: Q4 2025).
3. New code should use the ConfigurationManager system.

## Need Help?

If you encounter any issues during migration:

1. Check the test suite in `utils/pipeline/tests/test_config_manager.py` for examples
2. Review the configuration models in `utils/pipeline/config/models/`
3. File an issue with the tag `config-migration` if you need assistance
