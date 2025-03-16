"""
Schema migration module.

This module provides functionality for migrating between schema versions.
"""

import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from utils.pipeline.config import ConfigurationManager
from utils.pipeline.config.models.schema import SchemaConfig, SchemaMigration


class SchemaMigrator:
    """
    Handles schema migrations between versions.

    This class provides functionality for:
    1. Loading and validating migration configurations
    2. Executing schema migrations
    3. Converting data between schema versions
    4. Tracking migration history
    """

    def __init__(self, config_manager: ConfigurationManager):
        """
        Initialize the schema migrator.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)

        # Migration history tracking
        self.migration_history: Dict[str, List[Dict[str, Any]]] = {}

        # Custom field transformers
        self.field_transformers: Dict[str, Callable] = {}

    def register_field_transformer(
        self, name: str, transformer: Callable[[Any], Any]
    ) -> None:
        """
        Register a custom field transformation function.

        Args:
            name: Name of the transformer
            transformer: Function that transforms field values
        """
        self.field_transformers[name] = transformer
        self.logger.info(f"Registered field transformer: {name}")

    def get_migration_config(
        self, schema_name: str, source_version: str, target_version: str
    ) -> Optional[SchemaMigration]:
        """
        Get migration configuration between versions.

        Args:
            schema_name: Name of the schema
            source_version: Source schema version
            target_version: Target schema version

        Returns:
            Migration configuration if found, None otherwise
        """
        try:
            # Construct migration config path
            config_path = (
                f"migrations/{schema_name}_{source_version}_to_{target_version}.yaml"
            )

            # Get migration configuration
            config_data = self.config_manager.get_config(config_path)

            if not config_data:
                self.logger.warning(f"Migration configuration not found: {config_path}")
                return None

            # Validate configuration
            return SchemaMigration(**config_data)

        except Exception as e:
            self.logger.error(f"Error loading migration configuration: {str(e)}")
            return None

    def migrate_schema(
        self,
        schema: SchemaConfig,
        target_version: str,
        migration_config: Optional[SchemaMigration] = None,
    ) -> Optional[SchemaConfig]:
        """
        Migrate a schema to a target version.

        Args:
            schema: Source schema configuration
            target_version: Target schema version
            migration_config: Optional pre-loaded migration configuration

        Returns:
            Migrated schema configuration if successful, None otherwise
        """
        try:
            # Get migration configuration if not provided
            if not migration_config:
                migration_config = self.get_migration_config(
                    schema.name,
                    schema.schema_version,
                    target_version,
                )

                if not migration_config:
                    return None

            # Create new schema based on source
            migrated_schema = SchemaConfig(
                **{
                    **schema.model_dump(),
                    "schema_version": target_version,
                }
            )

            # Apply field additions
            for field in migration_config.add_fields:
                if not any(f.name == field.name for f in migrated_schema.fields):
                    migrated_schema.fields.append(field)

            # Apply field removals
            if migration_config.remove_fields:
                migrated_schema.fields = [
                    field
                    for field in migrated_schema.fields
                    if field.name not in migration_config.remove_fields
                ]

            # Apply field renames
            if migration_config.rename_fields:
                for field in migrated_schema.fields:
                    if field.name in migration_config.rename_fields:
                        field.name = migration_config.rename_fields[field.name]

            # Track migration in history
            self._record_migration(
                schema.name,
                schema.schema_version,
                target_version,
            )

            return migrated_schema

        except Exception as e:
            self.logger.error(f"Error migrating schema: {str(e)}")
            return None

    def transform_data(
        self,
        data: Dict[str, Any],
        schema_name: str,
        source_version: str,
        target_version: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Transform data from source schema version to target version.

        Args:
            data: Source data to transform
            schema_name: Name of the schema
            source_version: Source schema version
            target_version: Target schema version

        Returns:
            Transformed data if successful, None otherwise
        """
        try:
            # Get migration configuration
            migration_config = self.get_migration_config(
                schema_name, source_version, target_version
            )

            if not migration_config:
                return None

            # Create copy of data for transformation
            transformed_data = data.copy()

            # Apply field removals
            for field in migration_config.remove_fields:
                transformed_data.pop(field, None)

            # Apply field renames
            for old_name, new_name in migration_config.rename_fields.items():
                if old_name in transformed_data:
                    transformed_data[new_name] = transformed_data.pop(old_name)

            # Apply field transformations
            for (
                field_name,
                transformer_name,
            ) in migration_config.transform_fields.items():
                if field_name in transformed_data:
                    transformer = self.field_transformers.get(transformer_name)
                    if transformer:
                        try:
                            transformed_data[field_name] = transformer(
                                transformed_data[field_name]
                            )
                        except Exception as e:
                            self.logger.error(
                                f"Error transforming field {field_name}: {str(e)}"
                            )
                            return None

            return transformed_data

        except Exception as e:
            self.logger.error(f"Error transforming data: {str(e)}")
            return None

    def _record_migration(
        self, schema_name: str, source_version: str, target_version: str
    ) -> None:
        """
        Record a migration in the history.

        Args:
            schema_name: Name of the schema
            source_version: Source schema version
            target_version: Target schema version
        """
        if schema_name not in self.migration_history:
            self.migration_history[schema_name] = []

        self.migration_history[schema_name].append(
            {
                "source_version": source_version,
                "target_version": target_version,
                "timestamp": datetime.now().isoformat(),
            }
        )
