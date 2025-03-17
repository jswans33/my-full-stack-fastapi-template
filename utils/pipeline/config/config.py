"""
Configuration module for the pipeline.

This module handles loading, validating, and merging configuration settings using Pydantic.
Includes enhanced validation for strategy paths, cross-field relationships, and schema validation.
"""

import os
from enum import Enum
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

# Environment variable prefix
ENV_PREFIX = "PIPELINE_"


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


class ComponentConfig(BaseModel):
    """Configuration for individual document processing components."""

    analyzer: str
    cleaner: str
    extractor: str
    validator: str
    formatter: str


class StrategyConfig(BaseModel):
    """Configuration for document processing strategies."""

    pdf: Union[str, ComponentConfig] = "strategies.pdf"
    excel: Union[str, ComponentConfig] = "strategies.excel"
    word: Union[str, ComponentConfig] = "strategies.word"
    text: Union[str, ComponentConfig] = "strategies.text"


class DocumentTypeRule(BaseModel):
    """Configuration for a single document type rule."""

    # Keywords to look for in section titles
    title_keywords: List[str] = Field(default_factory=list)

    # Keywords to look for in document content
    content_keywords: List[str] = Field(default_factory=list)

    # Patterns to match (e.g., invoice numbers, measurements)
    patterns: List[str] = Field(default_factory=list)

    # Confidence weights for different features
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "title_match": 0.4,
            "content_match": 0.3,
            "pattern_match": 0.3,
        }
    )

    # Minimum confidence threshold to classify as this type
    threshold: float = 0.5

    # Schema pattern to use for this document type
    schema_pattern: str = "standard"

    @model_validator(mode="after")
    def validate_weights(self) -> "DocumentTypeRule":
        """Validate that weights sum to 1.0."""
        total = sum(self.weights.values())
        if not (0.99 <= total <= 1.01):  # Allow for floating point imprecision
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        return self


class ClassificationConfig(BaseModel):
    """Configuration for document classification."""

    # Enable/disable classification
    enabled: bool = True

    # Default confidence threshold
    default_threshold: float = 0.3

    # Classification method (rule_based, pattern_matcher, etc.)
    method: str = "rule_based"

    # Document type rules
    rules: Dict[str, DocumentTypeRule] = Field(
        default_factory=lambda: {
            "SPECIFICATION": DocumentTypeRule(
                title_keywords=["specification", "spec", "technical", "requirements"],
                content_keywords=[
                    "dimensions",
                    "capacity",
                    "performance",
                    "material",
                    "compliance",
                    "standard",
                ],
                patterns=[
                    "mm",
                    "cm",
                    "m",
                    "kg",
                    "lb",
                    "°c",
                    "°f",
                    "hz",
                    "mhz",
                    "ghz",
                    "kw",
                    "hp",
                ],
                threshold=0.4,
                schema_pattern="detailed_specification",
            ),
            "INVOICE": DocumentTypeRule(
                title_keywords=["invoice", "bill", "receipt"],
                content_keywords=["invoice #", "invoice no", "payment", "due date"],
                patterns=["\\$\\d+\\.\\d{2}", "total", "subtotal"],
                threshold=0.5,
                schema_pattern="detailed_invoice",
            ),
            "PROPOSAL": DocumentTypeRule(
                title_keywords=["proposal", "offer", "quote"],
                content_keywords=["proposed", "offer", "scope of work", "timeline"],
                patterns=["proposed by", "submitted to", "valid for"],
                threshold=0.5,
                schema_pattern="detailed_proposal",
            ),
            "TERMS_AND_CONDITIONS": DocumentTypeRule(
                title_keywords=["terms", "conditions", "agreement", "contract"],
                content_keywords=[
                    "shall",
                    "herein",
                    "pursuant",
                    "liability",
                    "warranty",
                    "indemnify",
                ],
                patterns=["party", "parties", "agree", "clause", "section"],
                threshold=0.5,
                schema_pattern="formal_terms",
            ),
        }
    )

    # Filename pattern matching (optional)
    filename_patterns: Dict[str, str] = Field(
        default_factory=lambda: {
            "SPECIFICATION": r"(?i)spec|specification",
            "INVOICE": r"(?i)invoice|bill",
            "PROPOSAL": r"(?i)proposal|offer",
            "TERMS_AND_CONDITIONS": r"(?i)terms|conditions|agreement",
        }
    )


def _split_module_class_path(path: str) -> Tuple[str, str]:
    """Split path into module path and class name."""
    parts = path.rsplit(".", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid module.class path: {path}")
    return parts[0], parts[1]


def _is_valid_module_path(module_path: str) -> bool:
    """Check if module can be imported."""
    try:
        return find_spec(module_path) is not None
    except (ImportError, AttributeError):
        return False


def _class_exists_in_module(module_path: str, class_name: str) -> bool:
    """Check if class exists in module."""
    try:
        module = import_module(module_path)
        return hasattr(module, class_name)
    except (ImportError, AttributeError):
        return False


class PipelineConfig(BaseModel):
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
    strategies: StrategyConfig = Field(
        default_factory=StrategyConfig, description="Document processing strategies"
    )
    classification: ClassificationConfig = Field(
        default_factory=ClassificationConfig,
        description="Document classification settings",
    )

    def __getitem__(self, key: str):
        """Enable dictionary-like access to configuration values."""
        return getattr(self, key)

    def __eq__(self, other):
        """Enable equality comparison with dictionaries."""
        if isinstance(other, dict):
            return self.model_dump() == other
        return super().__eq__(other)

    @classmethod
    def get_default(cls) -> "PipelineConfig":
        """Get a new instance with default values."""
        return cls()

    @field_validator("input_dir")
    def validate_input_dir(cls, v: str) -> str:
        """Validate input directory exists if absolute path."""
        path = Path(v)
        if path.is_absolute() and not path.exists():
            # Create the directory if it doesn't exist
            path.mkdir(parents=True, exist_ok=True)
        # Always return forward slashes for cross-platform compatibility
        return str(path).replace("\\", "/")

    @field_validator("output_dir")
    def validate_output_dir(cls, v: str) -> str:
        """Validate output directory exists."""
        if not v.strip():
            raise ValueError("Output directory cannot be empty")
        path = Path(v)
        # Create the directory if it doesn't exist
        path.mkdir(parents=True, exist_ok=True)
        # Always return forward slashes for cross-platform compatibility
        return str(path).replace("\\", "/")

    @model_validator(mode="after")
    def validate_strategy_paths(self) -> "PipelineConfig":
        """Validate strategy paths point to valid modules and classes."""
        for strategy_type, strategy in self.strategies.model_dump().items():
            if isinstance(strategy, str):
                # Validate module path exists
                if not _is_valid_module_path(strategy):
                    raise ValueError(f"Invalid strategy module path for {strategy_type}: {strategy}")
            elif isinstance(strategy, dict):
                for component, path in strategy.items():
                    if not isinstance(path, str) or not path.strip():
                        raise ValueError(f"Invalid {component} path for {strategy_type}: {path}")
                    
                    # Validate module and class exist
                    module_path, class_name = _split_module_class_path(path)
                    if not _is_valid_module_path(module_path):
                        raise ValueError(f"Module not found: {module_path} for {strategy_type}.{component}")
                    
                    if not _class_exists_in_module(module_path, class_name):
                        raise ValueError(f"Class {class_name} not found in module {module_path}")
        return self

    @model_validator(mode="after")
    def validate_cross_field_relationships(self) -> "PipelineConfig":
        """Ensure consistency between related configuration settings."""
        # Validate output_format and formatter compatibility
        if self.output_format not in ["yaml", "json"]:
            raise ValueError(f"Unsupported output format: {self.output_format}")
        
        # Ensure validation_level and classification thresholds are compatible
        if self.validation_level == ValidationLevel.STRICT:
            # In strict mode, ensure thresholds are high enough
            for doc_type, rule in self.classification.rules.items():
                if rule.threshold < 0.5:
                    raise ValueError(
                        f"Document type {doc_type} has threshold {rule.threshold} which is too low "
                        f"for validation_level={self.validation_level}. Minimum is 0.5."
                    )
        
        # Check schema_pattern consistency with available schemas
        valid_schema_patterns = ["standard", "detailed_specification", "detailed_invoice", 
                               "detailed_proposal", "formal_terms"]
        for doc_type, rule in self.classification.rules.items():
            if rule.schema_pattern not in valid_schema_patterns:
                raise ValueError(f"Invalid schema_pattern '{rule.schema_pattern}' for {doc_type}")
        
        return self


def _validate_against_schema(config: PipelineConfig, schema_config: BaseModel) -> None:
    """Validate configuration against a schema configuration."""
    schema_dict = schema_config.model_dump()
    errors = []
    
    # Validate each field against schema
    for field_name, schema_value in schema_dict.items():
        if not hasattr(config, field_name):
            continue  # Skip fields that don't exist in config
            
        config_value = getattr(config, field_name)
        
        # Check field type compatibility
        expected_type = type(schema_value)
        if not isinstance(config_value, expected_type) and config_value is not None:
            errors.append(f"Field '{field_name}' has wrong type: expected {expected_type}, got {type(config_value)}")
            continue
            
        # Validate against schema constraints
        if hasattr(schema_config, f"validate_{field_name}"):
            validator = getattr(schema_config, f"validate_{field_name}")
            try:
                validator(config_value)
            except ValueError as e:
                errors.append(f"Validation failed for field '{field_name}': {str(e)}")
    
    if errors:
        raise ValueError(f"Configuration failed schema validation:\n" + "\n".join(errors))


def load_config(
    config_path: Optional[str] = None,
    config_dict: Optional[dict] = None,
    override_dict: Optional[dict] = None,
    use_env: bool = False,
    schema_config: Optional[BaseModel] = None,
) -> PipelineConfig:
    """
    Load configuration from various sources and merge them.

    The configuration is loaded in the following order (later sources override earlier ones):
    1. Default configuration (from PipelineConfig defaults)
    2. Configuration file (if provided)
    3. Configuration dictionary (if provided)
    4. Override dictionary (if provided)
    5. Environment variables (if use_env is True)

    Args:
        config_path: Path to a YAML configuration file
        config_dict: Configuration dictionary to use instead of loading from file
        override_dict: Dictionary with values that override the loaded configuration
        use_env: Whether to use environment variables to override configuration
        schema_config: Optional schema model to validate against

    Returns:
        A validated PipelineConfig instance

    Raises:
        FileNotFoundError: If the configuration file does not exist
        yaml.YAMLError: If the configuration file contains invalid YAML
        ValidationError: If the configuration is invalid
    """
    # Start with empty config to be filled
    config_data = {}

    # Load from file if provided
    if config_path:
        config_data = _load_from_file(config_path)
    else:
        # Use config_dict if provided
        if config_dict:
            config_data = config_dict.copy()

        # Apply overrides if provided
        if override_dict:
            config_data = _merge_configs(config_data, override_dict)

    # Apply environment variables if requested
    if use_env:
        env_config = _load_from_env()
        config_data = _merge_configs(config_data, env_config)

    # Create and validate the configuration
    config = PipelineConfig(**config_data)

    # Additional schema validation if provided
    if schema_config is not None:
        _validate_against_schema(config, schema_config)

    return config


def _load_from_file(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        return yaml.safe_load(f) or {}


def _load_from_env() -> dict:
    """Load configuration from environment variables."""
    config = {}

    for key, value in os.environ.items():
        if key.startswith(ENV_PREFIX):
            # Convert PIPELINE_INPUT_DIR to input_dir
            config_key = key[len(ENV_PREFIX) :].lower()

            # Handle nested keys (e.g., PIPELINE_STRATEGIES_PDF)
            if config_key.startswith("strategies_"):
                strategy_type = config_key[len("strategies_") :]
                if "strategies" not in config:
                    config["strategies"] = {}
                config["strategies"][strategy_type] = value
            else:
                # For any other keys, use as-is
                config[config_key] = value

    return config


def _merge_configs(base: dict, override: dict) -> dict:
    """
    Merge two configuration dictionaries.

    The override dictionary takes precedence over the base dictionary.
    For nested dictionaries, the merge is recursive.
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = _merge_configs(result[key], value)
        else:
            # Override or add the value
            result[key] = value

    return result
