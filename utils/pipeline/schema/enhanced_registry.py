"""
Enhanced schema registry module.

This module extends the SchemaRegistry with configuration integration, versioning, and inheritance.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from utils.pipeline.config import ConfigurationManager, SchemaConfig
from utils.pipeline.schema.extended_registry import ExtendedSchemaRegistry


class EnhancedSchemaRegistry(ExtendedSchemaRegistry):
    """
    Enhanced registry for document schemas with configuration integration.

    This class extends ExtendedSchemaRegistry with:
    1. Configuration manager integration
    2. Schema versioning support
    3. Schema inheritance
    4. Schema discovery from configuration
    """

    def __init__(self, config_manager: ConfigurationManager):
        """
        Initialize the enhanced schema registry.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager

        # Get registry configuration
        registry_config = config_manager.get_config("schema_registry")

        # Initialize base registry
        super().__init__(registry_config)

        # Version history for schemas
        self.schema_versions: Dict[str, Dict[str, Dict[str, Any]]] = {}

        # Schema inheritance relationships
        self.schema_inheritance: Dict[str, str] = {}

        # Load schemas from configuration
        self.load_schemas_from_config()

    def load_schemas_from_config(self) -> None:
        """Load schemas from configuration."""
        # Get schema discovery paths from configuration
        discovery_paths = self.config.get("discovery", {}).get("paths", [])

        # Discover schemas in each path
        for path in discovery_paths:
            self._discover_schemas(path)

        # Process schema inheritance
        self._process_schema_inheritance()

    def _discover_schemas(self, path: str) -> None:
        """
        Discover schemas in the specified path.

        Args:
            path: Path to discover schemas in
        """
        # Get all schema configurations
        schema_configs = self.config_manager.get_config(path)

        if not schema_configs:
            self.logger.warning(f"No schema configurations found in path: {path}")
            return

        # Process each schema configuration
        for schema_name, schema_config in schema_configs.items():
            try:
                # Validate schema configuration
                schema = SchemaConfig(**schema_config)

                # Generate schema ID
                schema_id = self._generate_schema_id(schema.name)

                # Convert to dictionary
                schema_dict = schema.model_dump()

                # Add to schemas
                self.schemas[schema_id] = schema_dict

                # Add to version history
                if schema.name not in self.schema_versions:
                    self.schema_versions[schema.name] = {}

                self.schema_versions[schema.name][schema.schema_version] = schema_dict

                # Record inheritance relationship if specified
                if schema.inherits:
                    self.schema_inheritance[schema.name] = schema.inherits

                self.logger.info(
                    f"Loaded schema {schema.name} version {schema.schema_version}"
                )

            except Exception as e:
                self.logger.error(f"Error loading schema {schema_name}: {str(e)}")

    def _process_schema_inheritance(self) -> None:
        """Process schema inheritance relationships."""
        # Process each schema with inheritance
        for schema_name, parent_name in self.schema_inheritance.items():
            try:
                # Get latest versions of schema and parent
                schema = self.get_schema_version(schema_name, "latest")
                parent = self.get_schema_version(parent_name, "latest")

                if not schema or not parent:
                    self.logger.warning(
                        f"Cannot process inheritance for {schema_name}: "
                        f"schema or parent {parent_name} not found"
                    )
                    continue

                # Merge parent fields into schema
                self._merge_schema_fields(schema, parent)

                # Update schema in registry
                schema_id = next(
                    (
                        k
                        for k, v in self.schemas.items()
                        if v.get("name") == schema_name
                    ),
                    None,
                )

                if schema_id:
                    self.schemas[schema_id] = schema

                    # Update version history
                    self.schema_versions[schema_name][schema["schema_version"]] = schema

                self.logger.info(
                    f"Processed inheritance for {schema_name} from {parent_name}"
                )

            except Exception as e:
                self.logger.error(
                    f"Error processing inheritance for {schema_name}: {str(e)}"
                )

    def _merge_schema_fields(
        self, schema: Dict[str, Any], parent: Dict[str, Any]
    ) -> None:
        """
        Merge parent fields into schema.

        Args:
            schema: Schema to merge fields into
            parent: Parent schema to merge fields from
        """
        # Get existing field names in schema
        schema_field_names = {field["name"] for field in schema.get("fields", [])}

        # Add parent fields that don't exist in schema
        for parent_field in parent.get("fields", []):
            if parent_field["name"] not in schema_field_names:
                schema.setdefault("fields", []).append(parent_field.copy())

        # Get existing validation names in schema
        schema_validation_names = {
            validation["name"] for validation in schema.get("validations", [])
        }

        # Add parent validations that don't exist in schema
        for parent_validation in parent.get("validations", []):
            if parent_validation["name"] not in schema_validation_names:
                schema.setdefault("validations", []).append(parent_validation.copy())

    def get_schema_version(
        self, schema_name: str, version: str = "latest"
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific version of a schema.

        Args:
            schema_name: Name of the schema
            version: Version of the schema, or "latest" for the latest version

        Returns:
            Schema dictionary or None if not found
        """
        # Check if schema exists
        if schema_name not in self.schema_versions:
            return None

        # Get version history
        versions = self.schema_versions[schema_name]

        if not versions:
            return None

        # Get latest version if requested
        if version == "latest":
            # Sort versions by semantic version
            sorted_versions = sorted(
                versions.keys(),
                key=lambda v: [int(x) for x in v.split(".")],
                reverse=True,
            )

            if not sorted_versions:
                return None

            return versions[sorted_versions[0]]

        # Get specific version
        return versions.get(version)

    def migrate_schema(
        self, schema_name: str, source_version: str, target_version: str
    ) -> bool:
        """
        Migrate a schema from source version to target version.

        Args:
            schema_name: Name of the schema
            source_version: Source version
            target_version: Target version

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get migration configuration
            migration_config = self.config_manager.get_config(
                f"migrations/{schema_name}_{source_version}_to_{target_version}"
            )

            if not migration_config:
                self.logger.error(
                    f"Migration configuration not found for {schema_name} "
                    f"from {source_version} to {target_version}"
                )
                return False

            # Get source schema
            source_schema = self.get_schema_version(schema_name, source_version)

            if not source_schema:
                self.logger.error(
                    f"Source schema {schema_name} version {source_version} not found"
                )
                return False

            # Create new schema based on source schema
            target_schema = source_schema.copy()
            target_schema["schema_version"] = target_version
            target_schema["updated_at"] = datetime.now().isoformat()

            # Apply field additions
            for field in migration_config.get("add_fields", []):
                target_schema.setdefault("fields", []).append(field)

            # Apply field removals
            if "remove_fields" in migration_config:
                target_schema["fields"] = [
                    field
                    for field in target_schema.get("fields", [])
                    if field["name"] not in migration_config["remove_fields"]
                ]

            # Apply field renames
            if "rename_fields" in migration_config:
                for field in target_schema.get("fields", []):
                    if field["name"] in migration_config["rename_fields"]:
                        field["name"] = migration_config["rename_fields"][field["name"]]

            # Apply field transformations
            if "transform_fields" in migration_config:
                # Field transformations would require executing code from the configuration
                # This is a placeholder for a more complex implementation
                self.logger.warning(
                    "Field transformations are not fully implemented yet"
                )

            # Add to version history
            if schema_name not in self.schema_versions:
                self.schema_versions[schema_name] = {}

            self.schema_versions[schema_name][target_version] = target_schema

            # Generate schema ID
            schema_id = self._generate_schema_id(schema_name)

            # Add to schemas
            self.schemas[schema_id] = target_schema

            # Save schema to storage
            self._save_schema(schema_id, target_schema)

            self.logger.info(
                f"Migrated schema {schema_name} from {source_version} to {target_version}"
            )

            return True

        except Exception as e:
            self.logger.error(
                f"Error migrating schema {schema_name} from {source_version} "
                f"to {target_version}: {str(e)}",
                exc_info=True,
            )
            return False

    def save_schema_config(self, schema: Dict[str, Any]) -> bool:
        """
        Save schema configuration.

        Args:
            schema: Schema dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate schema
            schema_config = SchemaConfig(**schema)

            # Save to configuration
            result = self.config_manager.update_configuration(
                f"schemas/{schema_config.name}", schema_config.model_dump()
            )

            if result:
                self.logger.info(f"Saved schema configuration for {schema_config.name}")
            else:
                self.logger.error(
                    f"Failed to save schema configuration for {schema_config.name}"
                )

            return result

        except Exception as e:
            self.logger.error(f"Error saving schema configuration: {str(e)}")
            return False
