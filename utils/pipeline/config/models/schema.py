"""
Schema configuration model.

This module provides the schema configuration model with validation support.
"""

from typing import Dict, List, Optional

from pydantic import Field, field_validator

from utils.pipeline.config.models.base import BaseConfig


class SchemaField(BaseConfig):
    """Configuration for a schema field."""

    name: str = Field(..., description="Field name")
    path: str = Field(..., description="Field path in document")
    type: str = Field(..., description="Field type")
    required: bool = Field(default=False, description="Whether the field is required")
    description: Optional[str] = Field(default=None, description="Field description")
    default: Optional[str] = Field(default=None, description="Default value")
    validation: Optional[str] = Field(default=None, description="Validation expression")


class SchemaValidation(BaseConfig):
    """Configuration for schema validation."""

    name: str = Field(..., description="Validation name")
    description: Optional[str] = Field(
        default=None, description="Validation description"
    )
    condition: str = Field(..., description="Validation condition")
    message: str = Field(..., description="Validation message")
    level: str = Field(default="error", description="Validation level")


class SchemaConfig(BaseConfig):
    """Configuration for a schema."""

    name: str = Field(..., description="Schema name")
    document_type: str = Field(..., description="Document type")
    schema_version: str = Field(..., description="Schema version")
    inherits: Optional[str] = Field(default=None, description="Parent schema name")
    fields: List[SchemaField] = Field(default_factory=list, description="Schema fields")
    validations: List[SchemaValidation] = Field(
        default_factory=list, description="Schema validations"
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Schema metadata"
    )

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """
        Validate schema name.

        Args:
            v: Schema name

        Returns:
            Validated schema name
        """
        # Check if name is not empty
        if not v.strip():
            raise ValueError("Schema name cannot be empty")

        # Check if name contains only allowed characters
        if not all(c.isalnum() or c in "_-" for c in v):
            raise ValueError(
                "Schema name can only contain alphanumeric characters, underscores, and hyphens"
            )

        return v


class SchemaMigration(BaseConfig):
    """Configuration for schema migration."""

    source_version: str = Field(..., description="Source schema version")
    target_version: str = Field(..., description="Target schema version")
    add_fields: List[SchemaField] = Field(
        default_factory=list, description="Fields to add"
    )
    remove_fields: List[str] = Field(
        default_factory=list, description="Fields to remove"
    )
    rename_fields: Dict[str, str] = Field(
        default_factory=dict, description="Fields to rename"
    )
    transform_fields: Dict[str, str] = Field(
        default_factory=dict, description="Field transformations"
    )
