"""
Pipeline configuration model.

This module provides the configuration model for the pipeline settings.
"""

from enum import Enum
from typing import Dict, Union

from pydantic import Field, field_validator

from .base import BaseConfig


class LogLevel(str, Enum):
    """Valid log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ValidationLevel(str, Enum):
    """Validation levels for document processing."""

    BASIC = "basic"
    STRICT = "strict"
    CUSTOM = "custom"


class ComponentConfig(BaseConfig):
    """Configuration for individual document processing components."""

    analyzer: str = Field(..., description="Analyzer module path")
    cleaner: str = Field(..., description="Cleaner module path")
    extractor: str = Field(..., description="Extractor module path")
    validator: str = Field(..., description="Validator module path")
    formatter: str = Field(..., description="Formatter module path")


class PipelineConfig(BaseConfig):
    """Pipeline configuration model with validation."""

    input_dir: str = Field(
        default="data/input", description="Directory for input documents"
    )
    output_dir: str = Field(
        default="data/output", description="Directory for processed output"
    )
    output_format: str = Field(default="yaml", description="Output format (yaml/json)")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    validation_level: ValidationLevel = Field(
        default=ValidationLevel.BASIC, description="Validation strictness"
    )
    strategies: Dict[str, Union[str, ComponentConfig]] = Field(
        default_factory=dict, description="Document processing strategies"
    )

    @field_validator("output_format")
    def validate_output_format(cls, v: str) -> str:
        """Validate output format."""
        if v not in ["yaml", "json"]:
            raise ValueError(f"Unsupported output format: {v}")
        return v

    @field_validator("strategies")
    def validate_strategies(
        cls, v: Dict[str, Union[str, ComponentConfig]]
    ) -> Dict[str, Union[str, ComponentConfig]]:
        """Validate strategy configuration."""
        required_types = ["pdf", "excel", "word", "text"]
        for required in required_types:
            if required not in v:
                v[required] = f"strategies.{required}"  # Default strategy path

        # No additional validation on strategy paths for now
        # This allows both "strategies.pdf" and "utils.pipeline.processors.pdf.PDFProcessor" formats
        return v
