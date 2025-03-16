"""
Environment configuration model.

This module provides the environment configuration model for environment-specific settings.
"""

from typing import Any, Dict, Optional

from pydantic import Field, field_validator

from utils.pipeline.config.models.base import BaseConfig


class EnvironmentConfig(BaseConfig):
    """Configuration for an environment."""

    name: str = Field(..., description="Environment name")
    description: Optional[str] = Field(
        default=None, description="Environment description"
    )
    overrides: Dict[str, Any] = Field(
        default_factory=dict, description="Configuration overrides"
    )

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """
        Validate environment name.

        Args:
            v: Environment name

        Returns:
            Validated environment name
        """
        # Check if name is not empty
        if not v.strip():
            raise ValueError("Environment name cannot be empty")

        # Check if name contains only allowed characters
        if not all(c.isalnum() or c in "_-" for c in v):
            raise ValueError(
                "Environment name can only contain alphanumeric characters, underscores, and hyphens"
            )

        return v
