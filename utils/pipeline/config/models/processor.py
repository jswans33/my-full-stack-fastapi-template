"""
Processor configuration model.

This module provides the processor configuration model for document processing components.
"""

from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator

from utils.pipeline.config.models.base import BaseConfig


class ProcessorComponentConfig(BaseConfig):
    """Configuration for a processor component."""

    name: str = Field(..., description="Component name")
    class_path: str = Field(..., description="Component class path")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Component parameters"
    )

    @field_validator("class_path")
    def validate_class_path(cls, v: str) -> str:
        """
        Validate component class path.

        Args:
            v: Component class path

        Returns:
            Validated component class path
        """
        # Check if class path is not empty
        if not v.strip():
            raise ValueError("Component class path cannot be empty")

        # Check if class path contains at least one dot
        if "." not in v:
            raise ValueError("Component class path must be in format 'module.class'")

        return v


class ProcessorConfig(BaseConfig):
    """Configuration for a document processor."""

    name: str = Field(..., description="Processor name")
    description: Optional[str] = Field(
        default=None, description="Processor description"
    )
    document_types: List[str] = Field(
        default_factory=list, description="Supported document types"
    )
    components: Dict[str, ProcessorComponentConfig] = Field(
        default_factory=dict, description="Processor components"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Processor parameters"
    )

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """
        Validate processor name.

        Args:
            v: Processor name

        Returns:
            Validated processor name
        """
        # Check if name is not empty
        if not v.strip():
            raise ValueError("Processor name cannot be empty")

        # Check if name contains only allowed characters
        if not all(c.isalnum() or c in "_-" for c in v):
            raise ValueError(
                "Processor name can only contain alphanumeric characters, underscores, and hyphens"
            )

        return v
