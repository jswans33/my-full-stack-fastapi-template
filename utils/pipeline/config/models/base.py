"""
Base configuration model.

This module provides the base configuration model with version tracking.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class BaseConfig(BaseModel):
    """
    Base configuration model.

    All configuration models should inherit from this class.
    """

    version: str = Field(default="1.0", description="Configuration version")
    description: Optional[str] = Field(
        default=None, description="Configuration description"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="Last update timestamp"
    )

    def update(self, updates: Dict[str, Any]) -> "BaseConfig":
        """
        Update configuration with new values.

        Args:
            updates: Dictionary with updates

        Returns:
            Updated configuration
        """
        # Create a copy of the current data
        data = self.model_dump()

        # Apply updates
        for key, value in updates.items():
            if key in data:
                data[key] = value

        # Update timestamp
        data["updated_at"] = datetime.now()

        # Create new instance
        return self.__class__(**data)

    @field_validator("version")
    def validate_version(cls, v: str) -> str:
        """
        Validate version format.

        Args:
            v: Version string

        Returns:
            Validated version string
        """
        # Check if version is in format x.y or x.y.z
        parts = v.split(".")
        if len(parts) not in [2, 3]:
            raise ValueError("Version must be in format x.y or x.y.z")

        # Check if all parts are integers
        for part in parts:
            try:
                int(part)
            except ValueError:
                raise ValueError("Version parts must be integers")

        return v
