"""
Document type configuration model.

This module provides the document type configuration model with inheritance support.
"""

from typing import Dict, List, Optional

from pydantic import Field, field_validator

from utils.pipeline.config.models.base import BaseConfig


class DocumentField(BaseConfig):
    """Configuration for a document field."""

    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Field type")
    required: bool = Field(default=False, description="Whether the field is required")
    description: Optional[str] = Field(default=None, description="Field description")
    default: Optional[str] = Field(default=None, description="Default value")
    patterns: List[str] = Field(
        default_factory=list, description="Regex patterns for validation"
    )
    min_length: Optional[int] = Field(default=None, description="Minimum length")
    max_length: Optional[int] = Field(default=None, description="Maximum length")
    min_value: Optional[float] = Field(default=None, description="Minimum value")
    max_value: Optional[float] = Field(default=None, description="Maximum value")
    enum_values: List[str] = Field(default_factory=list, description="Allowed values")


class DocumentRule(BaseConfig):
    """Configuration for a document rule."""

    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(default=None, description="Rule description")
    condition: str = Field(..., description="Rule condition")
    action: str = Field(..., description="Rule action")
    priority: int = Field(default=0, description="Rule priority")


class DocumentTypeConfig(BaseConfig):
    """Configuration for a document type."""

    name: str = Field(..., description="Document type name")
    inherits: Optional[str] = Field(default=None, description="Parent document type")
    fields: List[DocumentField] = Field(
        default_factory=list, description="Document fields"
    )
    rules: List[DocumentRule] = Field(
        default_factory=list, description="Document rules"
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Document metadata"
    )

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """
        Validate document type name.

        Args:
            v: Document type name

        Returns:
            Validated document type name
        """
        # Check if name is not empty
        if not v.strip():
            raise ValueError("Document type name cannot be empty")

        # Check if name contains only allowed characters
        if not all(c.isalnum() or c in "_-" for c in v):
            raise ValueError(
                "Document type name can only contain alphanumeric characters, underscores, and hyphens"
            )

        return v
