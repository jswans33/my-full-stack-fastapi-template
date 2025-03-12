"""
PlantUML Utilities Settings

This module provides a centralized configuration system using Pydantic.
"""

import sys
from pathlib import Path
from typing import Union

from pydantic import BaseModel, Field, validator

from .exceptions import ProjectRootError

PathLike = Union[str, Path]


class PlantUMLSettings(BaseModel):
    """PlantUML utilities configuration settings."""

    # Project structure
    project_root: Path = Field(description="Project root directory")
    source_dir: Path = Field(description="Source directory for PlantUML files")
    output_dir: Path = Field(description="Output directory for rendered diagrams")

    # Analysis settings
    default_exclude_patterns: set[str] = Field(
        default={"__pycache__", ".git", "venv", ".venv", "node_modules"},
        description="Default patterns to exclude from analysis",
    )

    # PlantUML server configuration
    plantuml_server_svg: str = Field(
        default="http://www.plantuml.com/plantuml/svg/",
        description="PlantUML server URL for SVG format",
    )
    plantuml_server_png: str = Field(
        default="http://www.plantuml.com/plantuml/img/",
        description="PlantUML server URL for PNG format",
    )

    # Output formats
    supported_formats: list[str] = Field(
        default=["svg", "png"],
        description="Supported output formats",
    )
    default_format: str = Field(
        default="svg",
        description="Default output format",
    )

    # Logging configuration
    verbose: bool = Field(
        default=False,
        description="Enable verbose logging",
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Logging format string",
    )

    @validator("project_root", pre=True)
    def validate_project_root(cls, v: PathLike | None) -> Path:
        """Validate and set the project root directory."""
        if v is None:
            v = cls._find_project_root()
        return Path(str(v)).resolve()

    @validator("source_dir", pre=True)
    def validate_source_dir(cls, v: PathLike | None, values: dict) -> Path:
        """Validate and set the source directory."""
        if v is None:
            project_root = values.get("project_root")
            if project_root is None:
                raise ProjectRootError(
                    "Project root must be set before source directory",
                )
            v = project_root / "docs" / "diagrams"

        path = Path(str(v)).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    @validator("output_dir", pre=True)
    def validate_output_dir(cls, v: PathLike | None, values: dict) -> Path:
        """Validate and set the output directory."""
        if v is None:
            source_dir = values.get("source_dir")
            if source_dir is None:
                raise ProjectRootError(
                    "Source directory must be set before output directory",
                )
            v = source_dir / "output"

        path = Path(str(v)).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    @validator("default_format")
    def validate_default_format(cls, v: str, values: dict) -> str:
        """Validate the default format is supported."""
        if v not in values["supported_formats"]:
            raise ValueError(
                f"Default format '{v}' must be one of {values['supported_formats']}",
            )
        return v

    @classmethod
    def _find_project_root(cls) -> Path:
        """Find the project root directory by looking for key markers."""
        current_dir = Path(__file__).parent

        for _ in range(10):  # Limit search depth
            if (current_dir / "docs").is_dir() and (current_dir / "utils").is_dir():
                return current_dir

            parent = current_dir.parent
            if parent == current_dir:  # Reached filesystem root
                break
            current_dir = parent

        raise ProjectRootError("Could not determine project root directory")

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            Path: str,
        }


def get_settings() -> PlantUMLSettings:
    """Get the global settings instance."""
    project_root = PlantUMLSettings._find_project_root()
    source_dir = project_root / "docs" / "diagrams"
    output_dir = source_dir / "output"

    settings = PlantUMLSettings(
        project_root=project_root,
        source_dir=source_dir,
        output_dir=output_dir,
    )

    # Add project root to Python path
    if str(settings.project_root) not in sys.path:
        sys.path.insert(0, str(settings.project_root))

    return settings


# Create a global settings instance
settings = get_settings()
