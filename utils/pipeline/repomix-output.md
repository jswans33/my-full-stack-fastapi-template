This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.
The content has been processed where content has been formatted for parsing in markdown style.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: **/*
- Files matching these patterns are excluded: uv.lock, data, *.md, tests/**, docs/**, reports/**, build/**, dist/**, node_modules/**, **/node_modules/*, **/bower_components/**
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Content has been formatted for parsing in markdown style

## Additional Info

# Directory Structure
```
.repomixignore
analyzer/__init__.py
analyzer/pdf.py
cleaner/__init__.py
cleaner/pdf.py
config/__init__.py
config/config.py
config/example_config.yaml
config/hvac_config.json
config/hvac_config.yaml
core/file_processor.py
examples/batch_processing_example.py
examples/config.yaml
examples/document_classification_example.py
examples/pdf_extraction_example.py
examples/schema_analysis_example.py
models/models.py
pipeline.py
processors/classifiers/__init__.py
processors/classifiers/pattern_matcher.py
processors/classifiers/rule_based.py
processors/document_classifier.py
processors/formatters/factory.py
processors/formatters/json_formatter.py
processors/formatters/markdown_formatter.py
processors/pdf_extractor.py
processors/pdf_formatter.py
processors/pdf_validator.py
pyproject.toml
pytest.ini
rename_input_files.py
repomix.config.json
requirements-dev.txt
run_pipeline.py
run_tests.py
schema/__init__.py
schema/analyzer.py
schema/data/schemas/test_document_20250315153312.json
schema/extended_registry.py
schema/matchers.py
schema/registry.py
schema/templates/__init__.py
schema/vectorizer.py
schema/visualizer.py
setup_pytest_env.py
strategies/__init__.py
strategies/base.py
strategies/formatter.py
utils/logging.py
utils/progress.py
verify/base.py
verify/factory.py
verify/json_tree.py
verify/markdown.py
visualize_schema.py
```

# Files

## File: .repomixignore
```
# Add patterns to ignore here, one per line
# Example:
# *.log
# tmp/
```

## File: analyzer/__init__.py
```python
"""
Analyzer package.

This package provides document analysis functionality.
"""

from .pdf import PDFAnalyzer

__all__ = ["PDFAnalyzer"]
```

## File: analyzer/pdf.py
```python
"""
PDF analyzer implementation.

This module provides functionality for analyzing PDF document structure.
"""

from typing import Any, Dict

import pypdf

from utils.pipeline.strategies.base import AnalyzerStrategy
from utils.pipeline.utils.logging import get_logger


class PDFAnalyzer(AnalyzerStrategy):
    """Analyzes PDF document structure and content."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def analyze(self, input_path: str) -> Dict[str, Any]:
        """
        Analyze PDF document structure.

        Args:
            input_path: Path to PDF file

        Returns:
            Dictionary containing analysis results
        """
        self.logger.info("Analyzing PDF: %s", input_path)

        try:
            with open(input_path, "rb") as f:
                pdf = pypdf.PdfReader(f)

                # Extract basic metadata
                metadata = {}
                if pdf.metadata:
                    metadata = {
                        "title": pdf.metadata.get("/Title", ""),
                        "author": pdf.metadata.get("/Author", ""),
                        "subject": pdf.metadata.get("/Subject", ""),
                        "creator": pdf.metadata.get("/Creator", ""),
                        "producer": pdf.metadata.get("/Producer", ""),
                        "creation_date": pdf.metadata.get("/CreationDate", ""),
                        "modification_date": pdf.metadata.get("/ModDate", ""),
                    }

                # Extract page information
                pages = []
                for i, page in enumerate(pdf.pages):
                    page_info = {
                        "number": i + 1,
                        "size": page.mediabox,
                        "rotation": page.get("/Rotate", 0),
                        "content": page.extract_text(),
                    }
                    pages.append(page_info)

                # Build sections from content
                sections = []
                current_section = None

                for page in pages:
                    content = page["content"]
                    lines = content.split("\n")

                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue

                        # Simple heuristic for section detection
                        if line.isupper() or line.startswith(
                            ("#", "Chapter", "Section")
                        ):
                            # New section
                            if current_section:
                                sections.append(current_section)
                            current_section = {
                                "title": line,
                                "content": "",
                                "level": 0 if line.isupper() else 1,
                            }
                        elif current_section:
                            current_section["content"] += line + "\n"
                        else:
                            # Text before first section
                            current_section = {
                                "title": "Introduction",
                                "content": line + "\n",
                                "level": 0,
                            }

                # Add last section
                if current_section:
                    sections.append(current_section)

                return {
                    "path": input_path,
                    "type": "pdf",
                    "metadata": metadata,
                    "pages": pages,
                    "sections": sections,
                }

        except Exception as e:
            self.logger.error("Failed to analyze PDF: %s", str(e), exc_info=True)
            # Return minimal structure for error case
            return {
                "path": input_path,
                "type": "pdf",
                "metadata": {},
                "sections": [
                    {
                        "title": "Error",
                        "content": f"Failed to analyze PDF: {str(e)}",
                        "level": 0,
                    }
                ],
            }
```

## File: cleaner/__init__.py
```python
"""
Cleaner package.

This package provides document content cleaning and normalization functionality.
"""

from .pdf import PDFCleaner

__all__ = ["PDFCleaner"]
```

## File: cleaner/pdf.py
```python
"""
PDF cleaner implementation.

This module provides functionality for cleaning and normalizing PDF content.
"""

import re
from typing import Any, Dict

from utils.pipeline.strategies.base import CleanerStrategy
from utils.pipeline.utils.logging import get_logger


class PDFCleaner(CleanerStrategy):
    """Cleans and normalizes PDF content."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def clean(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize PDF content.

        Args:
            analysis_result: Analysis results from PDFAnalyzer

        Returns:
            Dictionary containing cleaned data
        """
        self.logger.info("Cleaning PDF content for: %s", analysis_result.get("path"))

        try:
            # Clean sections
            cleaned_sections = []
            for section in analysis_result.get("sections", []):
                cleaned_section = self._clean_section(section)
                if cleaned_section["content"].strip():  # Only keep non-empty sections
                    cleaned_sections.append(cleaned_section)

            # Clean metadata
            cleaned_metadata = self._clean_metadata(analysis_result.get("metadata", {}))

            # Clean page content
            cleaned_pages = []
            for page in analysis_result.get("pages", []):
                cleaned_page = self._clean_page(page)
                cleaned_pages.append(cleaned_page)

            return {
                "path": analysis_result.get("path"),
                "type": analysis_result.get("type"),
                "metadata": cleaned_metadata,
                "pages": cleaned_pages,
                "sections": cleaned_sections,
            }

        except Exception as e:
            self.logger.error("Failed to clean PDF content: %s", str(e), exc_info=True)
            return analysis_result  # Return original data on error

    def _clean_section(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a single section."""
        content = section.get("content", "")

        # Remove excessive whitespace
        content = re.sub(r"\s+", " ", content)
        content = re.sub(r"\n\s*\n", "\n\n", content)
        content = content.strip()

        # Clean up common OCR artifacts
        content = re.sub(
            r"[^\S\n]+", " ", content
        )  # Replace multiple spaces with single
        content = re.sub(r"(?<=[.!?])\s+", "\n", content)  # Line break after sentences
        content = re.sub(r"[^\x00-\x7F]+", "", content)  # Remove non-ASCII characters

        return {
            "title": section.get("title", "").strip(),
            "content": content,
            "level": section.get("level", 0),
        }

    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata fields."""
        cleaned = {}
        for key, value in metadata.items():
            if isinstance(value, str):
                # Remove non-printable characters and normalize whitespace
                value = "".join(char for char in value if char.isprintable())
                value = re.sub(r"\s+", " ", value).strip()
            cleaned[key] = value
        return cleaned

    def _clean_page(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Clean page content."""
        content = page.get("content", "")

        # Basic content cleaning
        content = re.sub(r"\s+", " ", content)  # Normalize whitespace
        content = re.sub(r"[^\x00-\x7F]+", "", content)  # Remove non-ASCII
        content = content.strip()

        return {
            "number": page.get("number"),
            "size": page.get("size"),
            "rotation": page.get("rotation", 0),
            "content": content,
        }
```

## File: config/__init__.py
```python
"""
Configuration module for the pipeline.

This module provides functions for loading and managing configuration settings.
"""

from .config import PipelineConfig, load_config

__all__ = ["load_config", "PipelineConfig"]
```

## File: config/config.py
```python
"""
Configuration module for the pipeline.

This module handles loading, validating, and merging configuration settings using Pydantic.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

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
        """Validate strategy paths are not empty."""
        for strategy_type, strategy in self.strategies.model_dump().items():
            if isinstance(strategy, str):
                if not strategy.strip():
                    raise ValueError(
                        f"Invalid strategy path for {strategy_type}: {strategy}"
                    )
            elif isinstance(strategy, dict):
                for component, path in strategy.items():
                    if not isinstance(path, str) or not path.strip():
                        raise ValueError(
                            f"Invalid {component} path for {strategy_type}: {path}"
                        )
        return self


def load_config(
    config_path: Optional[str] = None,
    config_dict: Optional[dict] = None,
    override_dict: Optional[dict] = None,
    use_env: bool = False,
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
    return PipelineConfig(**config_data)


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

    # Print environment variables for debugging
    print(f"Environment variables: {config}")

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
```

## File: config/example_config.yaml
```yaml
# Example Pipeline Configuration
# This file demonstrates the available configuration options for the pipeline

# Basic settings
input_dir: "data/input"
output_dir: "data/output"
output_format: "json"  # Options: json, yaml, markdown
log_level: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
validation_level: "basic"  # Options: basic, strict, custom

# Document processing strategies
strategies:
  pdf:
    analyzer: "utils.pipeline.analyzer.pdf.PDFAnalyzer"
    cleaner: "utils.pipeline.cleaner.pdf.PDFCleaner"
    extractor: "utils.pipeline.processors.pdf_extractor.PDFExtractor"
    validator: "utils.pipeline.processors.pdf_validator.PDFValidator"
  excel:
    analyzer: "utils.pipeline.analyzer.excel.ExcelAnalyzer"
    cleaner: "utils.pipeline.cleaner.excel.ExcelCleaner"
    extractor: "utils.pipeline.processors.excel_extractor.ExcelExtractor"
    validator: "utils.pipeline.processors.excel_validator.ExcelValidator"
  word:
    analyzer: "utils.pipeline.analyzer.word.WordAnalyzer"
    cleaner: "utils.pipeline.cleaner.word.WordCleaner"
    extractor: "utils.pipeline.processors.word_extractor.WordExtractor"
    validator: "utils.pipeline.processors.word_validator.WordValidator"
  text:
    analyzer: "utils.pipeline.analyzer.text.TextAnalyzer"
    cleaner: "utils.pipeline.cleaner.text.TextCleaner"
    extractor: "utils.pipeline.processors.text_extractor.TextExtractor"
    validator: "utils.pipeline.processors.text_validator.TextValidator"

# Document classification configuration
classification:
  # Enable/disable classification
  enabled: true
  
  # Default confidence threshold
  default_threshold: 0.3
  
  # Classification method (rule_based, pattern_matcher, etc.)
  method: "rule_based"
  
  # Document type rules
  rules:
    # Specification document type
    SPECIFICATION:
      # Keywords to look for in section titles
      title_keywords: 
        - "specification"
        - "spec"
        - "technical"
        - "requirements"
        - "section"
      
      # Keywords to look for in document content
      content_keywords: 
        - "dimensions"
        - "capacity"
        - "performance"
        - "material"
        - "compliance"
        - "standard"
        - "installation"
        - "quality"
      
      # Patterns to match (e.g., measurements)
      patterns: 
        - "mm"
        - "cm"
        - "m"
        - "kg"
        - "lb"
        - "°c"
        - "°f"
        - "hz"
        - "mhz"
        - "ghz"
        - "kw"
        - "hp"
      
      # Confidence weights for different features
      weights:
        title_match: 0.4
        content_match: 0.3
        pattern_match: 0.3
      
      # Minimum confidence threshold to classify as this type
      threshold: 0.4
      
      # Schema pattern to use for this document type
      schema_pattern: "detailed_specification"
    
    # HVAC Specification document type
    HVAC_SPECIFICATION:
      title_keywords: 
        - "hvac"
        - "heating"
        - "ventilation"
        - "air conditioning"
        - "mechanical"
      content_keywords: 
        - "temperature"
        - "humidity"
        - "airflow"
        - "ductwork"
        - "refrigerant"
        - "cooling"
        - "heating"
      patterns: 
        - "°f"
        - "°c"
        - "cfm"
        - "btu"
      threshold: 0.4
      schema_pattern: "hvac_specification"
    
    # Invoice document type
    INVOICE:
      title_keywords: 
        - "invoice"
        - "bill"
        - "receipt"
      content_keywords: 
        - "invoice #"
        - "invoice no"
        - "payment"
        - "due date"
        - "amount due"
        - "bill to"
      patterns: 
        - "\\$\\d+\\.\\d{2}"
        - "total"
        - "subtotal"
        - "tax"
      weights:
        title_match: 0.4
        content_match: 0.4
        pattern_match: 0.2
      threshold: 0.5
      schema_pattern: "detailed_invoice"
    
    # Proposal document type
    PROPOSAL:
      title_keywords: 
        - "proposal"
        - "offer"
        - "quote"
      content_keywords: 
        - "proposed"
        - "offer"
        - "scope of work"
        - "timeline"
        - "project"
      patterns: 
        - "proposed by"
        - "submitted to"
        - "valid for"
        - "\\$\\d+\\.\\d{2}"
      threshold: 0.5
      schema_pattern: "detailed_proposal"
    
    # Terms and Conditions document type
    TERMS_AND_CONDITIONS:
      title_keywords: 
        - "terms"
        - "conditions"
        - "agreement"
        - "contract"
      content_keywords: 
        - "shall"
        - "herein"
        - "pursuant"
        - "liability"
        - "warranty"
        - "indemnify"
        - "jurisdiction"
      patterns: 
        - "party"
        - "parties"
        - "agree"
        - "clause"
        - "section"
      threshold: 0.5
      schema_pattern: "formal_terms"
  
  # Filename pattern matching (optional)
  filename_patterns:
    SPECIFICATION: "(?i)spec|specification"
    HVAC_SPECIFICATION: "(?i)hvac|heating|ventilation"
    INVOICE: "(?i)invoice|bill|receipt"
    PROPOSAL: "(?i)proposal|offer|quote"
    TERMS_AND_CONDITIONS: "(?i)terms|conditions|agreement|contract"

# File processing configuration
file_processing:
  # Input configuration
  input:
    patterns: ["*.pdf", "*.docx", "*.xlsx", "*.txt"]
    recursive: false
    exclude_patterns: ["*_temp*", "*_backup*"]
    max_files: 0  # 0 means no limit
  
  # Output configuration
  output:
    formats: ["json", "markdown"]
    structure: "flat"  # Options: flat, hierarchical, mirror
    naming:
      template: "{original_name}_{format}"
      preserve_extension: false
      timestamp: false
    overwrite: true
  
  # Processing configuration
  processing:
    batch_size: 10
    parallel: false
    continue_on_error: true
    error_handling:
      log_level: "error"
      retry_count: 0
      retry_delay: 1
  
  # Reporting configuration
  reporting:
    summary: true
    detailed: true
    format: "json"
    save_path: "processing_report.json"
```

## File: config/hvac_config.json
```json
{
  "input_dir": "data/input",
  "output_dir": "data/output",
  "output_format": "json",
  "log_level": "INFO",
  "validation_level": "basic",

  "strategies": {
    "pdf": {
      "analyzer": "utils.pipeline.analyzer.pdf.PDFAnalyzer",
      "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
      "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
      "validator": "utils.pipeline.processors.pdf_validator.PDFValidator"
    }
  },

  "classification": {
    "enabled": true,
    "default_threshold": 0.3,
    "method": "rule_based",

    "rules": {
      "HVAC_SPECIFICATION": {
        "title_keywords": [
          "hvac",
          "heating",
          "ventilation",
          "air conditioning",
          "mechanical",
          "air handling",
          "ductwork",
          "refrigeration",
          "cooling",
          "thermal"
        ],
        "content_keywords": [
          "temperature",
          "humidity",
          "airflow",
          "ductwork",
          "refrigerant",
          "cooling",
          "heating",
          "ventilation",
          "air handling unit",
          "ahu",
          "vav",
          "chiller",
          "boiler",
          "condenser",
          "evaporator",
          "thermostat",
          "diffuser",
          "damper",
          "plenum",
          "insulation",
          "filter",
          "air quality",
          "ashrae"
        ],
        "patterns": [
          "°f",
          "°c",
          "cfm",
          "btu",
          "btuh",
          "ton",
          "kw",
          "hp",
          "psi",
          "inWC",
          "inH2O",
          "fpm",
          "rpm",
          "db",
          "wb",
          "rh%",
          "merv"
        ],
        "weights": {
          "title_match": 0.4,
          "content_match": 0.4,
          "pattern_match": 0.2
        },
        "threshold": 0.3,
        "schema_pattern": "hvac_specification"
      },
      "MECHANICAL_SPECIFICATION": {
        "title_keywords": [
          "mechanical",
          "plumbing",
          "piping",
          "equipment",
          "system"
        ],
        "content_keywords": [
          "mechanical",
          "equipment",
          "system",
          "installation",
          "pipe",
          "duct",
          "valve",
          "pump",
          "fan",
          "motor",
          "control",
          "sensor"
        ],
        "patterns": ["psi", "gpm", "rpm", "hp", "kw", "in\\.", "ft\\."],
        "threshold": 0.4,
        "schema_pattern": "mechanical_specification"
      },
      "ELECTRICAL_SPECIFICATION": {
        "title_keywords": [
          "electrical",
          "power",
          "wiring",
          "circuit",
          "control"
        ],
        "content_keywords": [
          "electrical",
          "power",
          "voltage",
          "current",
          "wire",
          "conduit",
          "circuit",
          "breaker",
          "panel",
          "motor",
          "controller",
          "disconnect",
          "transformer"
        ],
        "patterns": ["v", "kv", "a", "ma", "kva", "kw", "hz", "ohm", "awg"],
        "threshold": 0.4,
        "schema_pattern": "electrical_specification"
      }
    },

    "filename_patterns": {
      "HVAC_SPECIFICATION": "(?i)hvac|heating|ventilation|air.?conditioning|mechanical|ahu|vav|cooling",
      "MECHANICAL_SPECIFICATION": "(?i)mechanical|plumbing|piping|equipment",
      "ELECTRICAL_SPECIFICATION": "(?i)electrical|power|wiring|circuit|control"
    }
  },

  "file_processing": {
    "input": {
      "patterns": ["*.pdf"],
      "recursive": true,
      "exclude_patterns": ["*_temp*", "*_backup*"]
    },
    "output": {
      "formats": ["json", "markdown"],
      "structure": "hierarchical",
      "naming": {
        "template": "{original_name}",
        "preserve_extension": false,
        "timestamp": true
      },
      "overwrite": true
    },
    "reporting": {
      "summary": true,
      "detailed": true,
      "format": "json",
      "save_path": "hvac_processing_report.json"
    }
  }
}
```

## File: config/hvac_config.yaml
```yaml
# HVAC Specification Pipeline Configuration
# This configuration is optimized for processing HVAC specification documents

# Basic settings
input_dir: "data/input"
output_dir: "data/output"
output_format: "json"
log_level: "INFO"
validation_level: "basic"

# Document processing strategies
strategies:
  pdf:
    analyzer: "utils.pipeline.analyzer.pdf.PDFAnalyzer"
    cleaner: "utils.pipeline.cleaner.pdf.PDFCleaner"
    extractor: "utils.pipeline.processors.pdf_extractor.PDFExtractor"
    validator: "utils.pipeline.processors.pdf_validator.PDFValidator"

# Document classification configuration
classification:
  enabled: true
  default_threshold: 0.3
  method: "rule_based"
  
  # Document type rules
  rules:
    # HVAC Specification document type with enhanced keywords and patterns
    HVAC_SPECIFICATION:
      title_keywords: 
        - "hvac"
        - "heating"
        - "ventilation"
        - "air conditioning"
        - "mechanical"
        - "air handling"
        - "ductwork"
        - "refrigeration"
        - "cooling"
        - "thermal"
      
      content_keywords: 
        - "temperature"
        - "humidity"
        - "airflow"
        - "ductwork"
        - "refrigerant"
        - "cooling"
        - "heating"
        - "ventilation"
        - "air handling unit"
        - "ahu"
        - "vav"
        - "chiller"
        - "boiler"
        - "condenser"
        - "evaporator"
        - "thermostat"
        - "diffuser"
        - "damper"
        - "plenum"
        - "insulation"
        - "filter"
        - "air quality"
        - "ashrae"
      
      patterns: 
        - "°f"
        - "°c"
        - "cfm"
        - "btu"
        - "btuh"
        - "ton"
        - "kw"
        - "hp"
        - "psi"
        - "inWC"
        - "inH2O"
        - "fpm"
        - "rpm"
        - "db"
        - "wb"
        - "rh%"
        - "merv"
      
      weights:
        title_match: 0.4
        content_match: 0.4
        pattern_match: 0.2
      
      threshold: 0.3  # Lower threshold to catch more HVAC documents
      schema_pattern: "hvac_specification"
    
    # Mechanical Specification (broader category that includes HVAC)
    MECHANICAL_SPECIFICATION:
      title_keywords: 
        - "mechanical"
        - "plumbing"
        - "piping"
        - "equipment"
        - "system"
      
      content_keywords: 
        - "mechanical"
        - "equipment"
        - "system"
        - "installation"
        - "pipe"
        - "duct"
        - "valve"
        - "pump"
        - "fan"
        - "motor"
        - "control"
        - "sensor"
      
      patterns: 
        - "psi"
        - "gpm"
        - "rpm"
        - "hp"
        - "kw"
        - "in\\."
        - "ft\\."
      
      threshold: 0.4
      schema_pattern: "mechanical_specification"
    
    # Electrical Specification (often related to HVAC)
    ELECTRICAL_SPECIFICATION:
      title_keywords: 
        - "electrical"
        - "power"
        - "wiring"
        - "circuit"
        - "control"
      
      content_keywords: 
        - "electrical"
        - "power"
        - "voltage"
        - "current"
        - "wire"
        - "conduit"
        - "circuit"
        - "breaker"
        - "panel"
        - "motor"
        - "controller"
        - "disconnect"
        - "transformer"
      
      patterns: 
        - "v"
        - "kv"
        - "a"
        - "ma"
        - "kva"
        - "kw"
        - "hz"
        - "ohm"
        - "awg"
      
      threshold: 0.4
      schema_pattern: "electrical_specification"
  
  # Filename pattern matching
  filename_patterns:
    HVAC_SPECIFICATION: "(?i)hvac|heating|ventilation|air.?conditioning|mechanical|ahu|vav|cooling"
    MECHANICAL_SPECIFICATION: "(?i)mechanical|plumbing|piping|equipment"
    ELECTRICAL_SPECIFICATION: "(?i)electrical|power|wiring|circuit|control"

# File processing configuration
file_processing:
  input:
    patterns: ["*.pdf"]
    recursive: true
    exclude_patterns: ["*_temp*", "*_backup*"]
  
  output:
    formats: ["json", "markdown"]
    structure: "hierarchical"  # Organize by document type
    naming:
      template: "{original_name}"
      preserve_extension: false
      timestamp: true
    overwrite: true
  
  reporting:
    summary: true
    detailed: true
    format: "json"
    save_path: "hvac_processing_report.json"
```

## File: core/file_processor.py
```python
"""
File processor module for handling batch processing of files through the pipeline.

This module provides functionality for discovering input files, processing them
through the pipeline, and generating output files in various formats.
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from utils.pipeline.pipeline import Pipeline
from utils.pipeline.utils.logging import get_logger
from utils.pipeline.utils.progress import PipelineProgress

# Default configuration
DEFAULT_CONFIG = {
    "file_processing": {
        "input": {
            "patterns": ["*.pdf"],
            "recursive": False,
            "exclude_patterns": [],
            "max_files": 0,
        },
        "output": {
            "formats": ["json"],
            "directory": "output",
            "structure": "flat",
            "naming": {
                "template": "{original_name}_{format}",
                "preserve_extension": False,
                "timestamp": False,
            },
            "overwrite": True,
        },
        "processing": {
            "batch_size": 10,
            "parallel": False,
            "continue_on_error": True,
            "error_handling": {
                "log_level": "error",
                "retry_count": 0,
                "retry_delay": 1,
            },
        },
        "reporting": {
            "summary": True,
            "detailed": True,
            "format": "json",
            "save_path": "processing_report.json",
        },
    }
}


class FileProcessor:
    """
    Handles batch processing of files through the pipeline.

    This class provides functionality for:
    1. Discovering input files based on patterns
    2. Processing files through the pipeline
    3. Generating output files in various formats
    4. Tracking progress and reporting results
    """

    def __init__(
        self,
        input_dir: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the file processor.

        Args:
            input_dir: Directory containing input files
            output_dir: Directory for output files (defaults to input_dir/output)
            config: Configuration dictionary
        """
        # Load and merge configuration
        self.config = self._load_config(config)

        # Set up directories
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir) if output_dir else self._get_output_dir()

        # Initialize pipeline with relevant config subset
        pipeline_config = self._extract_pipeline_config()
        self.pipeline = Pipeline(pipeline_config)

        # Set up logging
        self.logger = get_logger(__name__)

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(
            f"FileProcessor initialized with input_dir={self.input_dir}, "
            f"output_dir={self.output_dir}"
        )

    def _load_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Load and validate configuration."""
        # Start with defaults
        merged_config = DEFAULT_CONFIG.copy()

        # Merge with provided config
        if config:
            self._deep_update(merged_config, config)

        # Validate critical settings
        self._validate_config(merged_config)

        return merged_config

    def _deep_update(self, d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively update a dictionary."""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
        return d

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration settings."""
        # Check for required settings
        if not config.get("file_processing", {}).get("input", {}).get("patterns"):
            config["file_processing"]["input"]["patterns"] = ["*.pdf"]
            self.logger.warning("No input patterns specified, defaulting to '*.pdf'")

        # Validate output formats
        valid_formats = ["json", "markdown"]
        formats = config.get("file_processing", {}).get("output", {}).get("formats", [])

        valid_output_formats = []
        for fmt in formats:
            if fmt.lower() not in valid_formats:
                self.logger.warning(f"Unsupported format '{fmt}', will be ignored")
            else:
                valid_output_formats.append(fmt.lower())

        if not valid_output_formats:
            valid_output_formats = ["json"]
            config["file_processing"]["output"]["formats"] = valid_output_formats
            self.logger.warning(
                "No valid output formats specified, defaulting to 'json'"
            )

    def _extract_pipeline_config(self) -> Dict[str, Any]:
        """Extract pipeline-specific configuration."""
        pipeline_config = {}

        # Copy relevant top-level keys
        for key in ["output_format", "strategies"]:
            if key in self.config:
                pipeline_config[key] = self.config[key]

        return pipeline_config

    def _get_output_dir(self) -> Path:
        """Get output directory from configuration or default."""
        output_config = self.config.get("file_processing", {}).get("output", {})
        output_dir = output_config.get("directory", "output")

        # If relative path, make it relative to input_dir
        if not os.path.isabs(output_dir):
            return self.input_dir / output_dir

        return Path(output_dir)

    def discover_files(self) -> List[Path]:
        """
        Discover input files based on configuration.

        Returns:
            List of file paths matching the configured patterns
        """
        input_config = self.config.get("file_processing", {}).get("input", {})

        # Get patterns and exclusions
        patterns = input_config.get("patterns", ["*.pdf"])
        exclude_patterns = input_config.get("exclude_patterns", [])
        recursive = input_config.get("recursive", False)
        max_files = input_config.get("max_files", 0)

        # Collect all matching files
        all_files = []

        for pattern in patterns:
            # Handle recursive vs non-recursive
            if recursive:
                glob_pattern = f"**/{pattern}"
            else:
                glob_pattern = pattern

            # Find matching files
            matches = list(self.input_dir.glob(glob_pattern))
            all_files.extend(matches)

        # Filter out directories and excluded patterns
        files = []
        for file_path in all_files:
            if not file_path.is_file():
                continue

            # Check exclusions
            excluded = False
            for exclude in exclude_patterns:
                if file_path.match(exclude):
                    excluded = True
                    break

            if not excluded:
                files.append(file_path)

        # Sort files for consistent processing order
        files.sort()

        # Apply max_files limit if specified
        if max_files > 0 and len(files) > max_files:
            self.logger.warning(
                f"Found {len(files)} files, limiting to {max_files} as configured"
            )
            files = files[:max_files]

        self.logger.info(f"Discovered {len(files)} files for processing")
        return files

    def create_output_path(self, input_file: Path, format_name: str) -> Path:
        """
        Create output path based on configuration.

        Args:
            input_file: Input file path
            format_name: Output format name (e.g., 'json', 'markdown')

        Returns:
            Path object for the output file
        """
        output_config = self.config.get("file_processing", {}).get("output", {})

        # Get naming configuration
        naming = output_config.get("naming", {})
        template = naming.get("template", "{original_name}_{format}")
        preserve_ext = naming.get("preserve_extension", False)
        add_timestamp = naming.get("timestamp", False)

        # Get structure type
        structure = output_config.get("structure", "flat")

        # Prepare filename components
        original_name = input_file.stem
        if preserve_ext:
            original_name = input_file.name

        # Add timestamp if configured
        timestamp = ""
        if add_timestamp:
            timestamp = datetime.now().strftime("_%Y%m%d%H%M%S")

        # Format the filename using template
        filename = template.format(
            original_name=original_name,
            format=format_name,
            timestamp=timestamp,
            type=self._detect_document_type(input_file),
        )

        # Add appropriate extension
        if format_name == "json":
            filename = f"{filename}.json"
        elif format_name == "markdown":
            filename = f"{filename}.md"

        # Determine directory based on structure
        if structure == "flat":
            # All files in the output directory
            output_path = self.output_dir / filename

        elif structure == "hierarchical":
            # Organize by document type and format
            doc_type = self._detect_document_type(input_file)
            output_path = self.output_dir / doc_type / format_name / filename

        elif structure == "mirror":
            # Mirror the input directory structure
            try:
                rel_path = input_file.relative_to(self.input_dir)
                output_path = self.output_dir / rel_path.parent / filename
            except ValueError:
                # If input_file is not relative to input_dir, use flat structure
                output_path = self.output_dir / filename

        else:
            # Default to flat structure
            output_path = self.output_dir / filename

        # Create parent directories
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle existing files
        if output_path.exists() and not output_config.get("overwrite", True):
            # Add numeric suffix if overwrite is disabled
            counter = 1
            while output_path.exists():
                stem = output_path.stem
                suffix = output_path.suffix
                output_path = output_path.with_name(f"{stem}_{counter}{suffix}")
                counter += 1

        return output_path

    def _detect_document_type(self, file_path: Path) -> str:
        """
        Detect document type based on file extension.

        Args:
            file_path: Path to the file

        Returns:
            Document type string (e.g., 'pdf', 'excel')
        """
        ext = file_path.suffix.lower()

        if ext == ".pdf":
            return "pdf"
        elif ext in [".xlsx", ".xls"]:
            return "excel"
        elif ext in [".docx", ".doc"]:
            return "word"
        elif ext == ".txt":
            return "text"
        else:
            return "generic"

    def generate_outputs(
        self, input_file: Path, output_data: Dict[str, Any]
    ) -> List[str]:
        """
        Generate output files in all configured formats.

        Args:
            input_file: Input file path
            output_data: Processed data from pipeline

        Returns:
            List of output file paths
        """
        formats = (
            self.config.get("file_processing", {})
            .get("output", {})
            .get("formats", ["json"])
        )
        output_paths = []

        for format_name in formats:
            # Save original output format
            original_format = self.pipeline.config.get("output_format")

            try:
                # Set pipeline output format
                self.pipeline.config["output_format"] = format_name.upper()

                # Create output path
                output_path = self.create_output_path(input_file, format_name)

                # Save output
                self.pipeline.save_output(output_data, str(output_path))
                output_paths.append(str(output_path))

                self.logger.info(f"Generated {format_name} output: {output_path}")

            except Exception as e:
                self.logger.error(f"Failed to generate {format_name} output: {str(e)}")

            finally:
                # Restore original output format
                self.pipeline.config["output_format"] = original_format

        return output_paths

    def process_all_files(self) -> List[Dict[str, Any]]:
        """
        Process all discovered files according to configuration.

        Returns:
            List of result dictionaries with processing status and outputs
        """
        # Get processing configuration
        proc_config = self.config.get("file_processing", {}).get("processing", {})
        continue_on_error = proc_config.get("continue_on_error", True)

        # Discover files
        files = self.discover_files()
        if not files:
            self.logger.warning("No matching files found")
            return []

        # Initialize progress tracking
        progress = PipelineProgress()
        results = []

        with progress:
            # Add overall progress tracking
            overall_task = progress.add_task(
                f"Processing {len(files)} files", total=len(files)
            )

            # Process each file
            for file in files:
                try:
                    progress.display_success(f"Processing {file.name}")

                    # Process the file without progress display
                    output_data = self.pipeline.run(str(file), show_progress=False)

                    # Generate outputs in all configured formats
                    output_paths = self.generate_outputs(file, output_data)

                    # Record result
                    results.append(
                        {
                            "file": str(file),
                            "status": "success",
                            "outputs": output_paths,
                        }
                    )

                    progress.display_success(f"Successfully processed {file.name}")

                except Exception as e:
                    error_msg = f"Error processing {file.name}: {str(e)}"
                    self.logger.error(error_msg, exc_info=True)
                    progress.display_error(error_msg)

                    # Record failure
                    results.append(
                        {"file": str(file), "status": "error", "error": str(e)}
                    )

                    # Stop processing if configured to do so
                    if not continue_on_error:
                        progress.display_error(
                            "Stopping due to error (continue_on_error=False)"
                        )
                        break

                finally:
                    # Update overall progress
                    progress.update(overall_task, advance=1)

        # Generate report if configured
        if (
            self.config.get("file_processing", {})
            .get("reporting", {})
            .get("summary", True)
        ):
            self.generate_report(results)

        return results

    def process_single_file(
        self, input_file: Union[str, Path], output_format: Optional[str] = None
    ) -> Tuple[Dict[str, Any], str]:
        """
        Process a single file (for backward compatibility).

        Args:
            input_file: Path to input file
            output_format: Optional output format override

        Returns:
            Tuple of (output_data, output_path)
        """
        input_path = Path(input_file)

        # Override output format if specified
        original_format = self.pipeline.config.get("output_format")
        if output_format:
            self.pipeline.config["output_format"] = output_format.upper()

        try:
            # Process the file without progress display
            output_data = self.pipeline.run(str(input_path), show_progress=False)

            # Generate output with specified format
            format_name = (
                output_format.lower()
                if output_format
                else (original_format.lower() if original_format else "json")
            )
            output_path = self.create_output_path(input_path, format_name)
            self.pipeline.save_output(output_data, str(output_path))

            return output_data, str(output_path)

        finally:
            # Restore original format
            if output_format:
                self.pipeline.config["output_format"] = original_format

    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate processing report based on configuration.

        Args:
            results: List of processing results

        Returns:
            Path to the generated report
        """
        report_config = self.config.get("file_processing", {}).get("reporting", {})

        # Skip if reporting is disabled
        if not report_config.get("summary", True) and not report_config.get(
            "detailed", False
        ):
            return ""

        # Prepare report data
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": len(results),
                "successful": sum(1 for r in results if r["status"] == "success"),
                "failed": sum(1 for r in results if r["status"] == "error"),
            },
        }

        # Add detailed information if configured
        if report_config.get("detailed", False):
            report["details"] = results

        # Determine report format and path
        format_name = report_config.get("format", "json")
        save_path = report_config.get("save_path", "processing_report.json")

        # Ensure path is absolute
        if not os.path.isabs(save_path):
            save_path = os.path.join(str(self.output_dir), save_path)

        # Create directory if needed
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

        # Save report
        with open(save_path, "w") as f:
            if format_name == "json":
                json.dump(report, f, indent=2)
            elif format_name == "csv" and report_config.get("detailed", False):
                # Simple CSV export for detailed reports
                writer = csv.writer(f)
                writer.writerow(["file", "status", "outputs", "error"])
                for item in results:
                    writer.writerow(
                        [
                            item["file"],
                            item["status"],
                            ",".join(item.get("outputs", [])),
                            item.get("error", ""),
                        ]
                    )
            else:
                # Default to simple text format
                f.write("Processing Report\n")
                f.write(f"Timestamp: {report['timestamp']}\n")
                f.write(f"Total Files: {report['summary']['total_files']}\n")
                f.write(f"Successful: {report['summary']['successful']}\n")
                f.write(f"Failed: {report['summary']['failed']}\n")

        self.logger.info(f"Report saved to {save_path}")
        return save_path
```

## File: examples/batch_processing_example.py
```python
"""
Example script demonstrating batch PDF extraction using the FileProcessor.

This example shows how to process multiple PDF files from an input directory
and generate output files in various formats.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow relative imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from utils.pipeline.core.file_processor import FileProcessor
from utils.pipeline.utils.progress import PipelineProgress


def main():
    """Run batch PDF extraction example."""
    progress = PipelineProgress()

    try:
        # Get the current directory
        current_dir = Path(__file__).parent.parent

        # Set up paths
        input_dir = current_dir / "data" / "input"
        output_dir = current_dir / "data" / "output"

        # Display setup info
        progress.display_success(f"Processing files from {input_dir}")

        # Initialize configuration
        config = {
            "output_format": "json",  # Default format
            "strategies": {
                "pdf": {
                    "analyzer": "utils.pipeline.analyzer.pdf.PDFAnalyzer",
                    "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
                    "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    "validator": "utils.pipeline.processors.pdf_validator.PDFValidator",
                },
            },
            "file_processing": {
                "input": {
                    "patterns": ["*.pdf"],  # Process all PDF files
                    "recursive": False,  # Don't search subdirectories
                },
                "output": {
                    "formats": ["json", "markdown"],  # Generate both formats
                    "directory": str(output_dir),
                    "structure": "flat",  # All files in the same directory
                    "naming": {
                        "template": "{original_name}",  # Use original filename
                    },
                    "overwrite": True,  # Overwrite existing files
                },
                "reporting": {
                    "summary": True,
                    "detailed": True,
                    "format": "json",
                    "save_path": "processing_report.json",
                },
            },
        }

        # Initialize file processor
        processor = FileProcessor(input_dir, output_dir, config)

        # Process all files
        results = processor.process_all_files()

        # Display final summary
        summary = {
            f"{r['file']}": {
                "status": r["status"],
                "outputs": r.get("outputs", []),
            }
            for r in results
        }
        progress.display_summary(summary)

    except Exception as e:
        progress.display_error(f"Error processing files: {e}")
        raise


if __name__ == "__main__":
    main()
```

## File: examples/config.yaml
```yaml
input_dir: data/tests/pdf
output_dir: data/output
output_format: yaml
log_level: INFO
validation_level: basic
strategies:
  pdf:
    analyzer: utils.pipeline.analyzer.pdf.PDFAnalyzer
    cleaner: utils.pipeline.cleaner.pdf.PDFCleaner
    extractor: utils.pipeline.processors.pdf_extractor.PDFExtractor
    validator: utils.pipeline.processors.pdf_validator.PDFValidator
    formatter: utils.pipeline.processors.pdf_formatter.PDFFormatter
  excel: strategies.excel
  word: strategies.word
  text: strategies.text
```

## File: examples/document_classification_example.py
```python
"""
Example script demonstrating document classification functionality.
"""

from pathlib import Path

from utils.pipeline.pipeline import Pipeline
from utils.pipeline.utils.progress import PipelineProgress


def main():
    """Run document classification example."""
    progress = PipelineProgress()

    try:
        # Get the current directory
        current_dir = Path(__file__).parent.parent

        # Set up paths
        input_dir = current_dir / "data" / "input"
        output_dir = current_dir / "data" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Display minimal setup info
        progress.display_success(f"Processing files from {input_dir}")

        # Initialize pipeline with configuration
        config = {
            "output_format": "json",  # Default format
            "enable_classification": True,  # Enable document classification
            "record_schemas": True,  # Record schemas for future matching
            "match_schemas": True,  # Match against known schemas
            "classification": {
                "type": "rule_based",  # Use rule-based classifier
                "confidence_threshold": 0.6,  # Minimum confidence threshold
            },
            "strategies": {
                "pdf": {
                    "analyzer": "utils.pipeline.analyzer.pdf.PDFAnalyzer",
                    "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
                    "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    "validator": "utils.pipeline.processors.pdf_validator.PDFValidator",
                },
            },
        }

        pipeline = Pipeline(config)

        # Process all PDF files in the input directory
        for pdf_file in input_dir.glob("*.pdf"):
            progress.display_success(f"Processing {pdf_file.name}")

            # Process the PDF with JSON output
            output_data = pipeline.run(str(pdf_file))

            # Save JSON output
            json_output = output_dir / f"{pdf_file.stem}.json"
            pipeline.save_output(output_data, str(json_output))
            progress.display_success(f"JSON output saved to: {json_output.name}")

            # Process the PDF with Markdown output
            pipeline.config["output_format"] = "markdown"
            output_data = pipeline.run(str(pdf_file))

            # Save Markdown output
            md_output = output_dir / f"{pdf_file.stem}.md"
            pipeline.save_output(output_data, str(md_output))
            progress.display_success(f"Markdown output saved to: {md_output.name}")

            # Display classification results
            if "classification" in output_data:
                classification = output_data["classification"]
                progress.display_success(
                    f"Document classified as: {classification['document_type']} "
                    f"(confidence: {classification['confidence']:.2f})"
                )
                progress.display_success(
                    f"Schema pattern: {classification['schema_pattern']}"
                )
                progress.display_success(
                    f"Key features: {', '.join(classification['key_features'])}"
                )

            # Reset output format for next file
            pipeline.config["output_format"] = "json"

        # Display final summary
        progress.display_success("Processing complete!")
        progress.display_success(
            f"Files Processed: {len(list(input_dir.glob('*.pdf')))}"
        )
        progress.display_success(
            f"Outputs Generated: {len(list(output_dir.glob('*.*')))}"
        )
        progress.display_success("Classification: Enabled")
        progress.display_success("Schema Recording: Enabled")

    except Exception as e:
        progress.display_error(f"Error processing documents: {e}")
        raise


if __name__ == "__main__":
    main()
```

## File: examples/pdf_extraction_example.py
```python
"""
Example script demonstrating PDF extraction pipeline usage.

This example shows how to process a single PDF file using the FileProcessor
for backward compatibility with the original example.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow relative imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from utils.pipeline.core.file_processor import FileProcessor
from utils.pipeline.utils.progress import PipelineProgress


def main():
    """Run PDF extraction example."""
    progress = PipelineProgress()

    try:
        # Get the current directory
        current_dir = Path(__file__).parent.parent

        # Set up paths
        input_file = (
            current_dir
            / "data"
            / "input"
            / "Quotation 79520-4 - Rocky Vista HS 100%CD (25-03-12).pdf"
        )
        output_dir = current_dir / "data" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Display minimal setup info
        progress.display_success(f"Processing {input_file.name}")

        # Initialize configuration
        config = {
            "output_format": "json",  # Default format
            "strategies": {
                "pdf": {
                    "analyzer": "utils.pipeline.analyzer.pdf.PDFAnalyzer",
                    "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
                    "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    "validator": "utils.pipeline.processors.pdf_validator.PDFValidator",
                },
            },
            "file_processing": {
                "output": {
                    "formats": ["json", "markdown"],  # Support both formats
                    "naming": {
                        "template": "sample_output",  # Use fixed name for backward compatibility
                    },
                    "overwrite": True,
                },
            },
        }

        # Initialize file processor
        processor = FileProcessor(current_dir, output_dir, config)

        # Process the PDF with JSON output
        progress.display_success("Starting JSON output processing")
        json_data, json_path = processor.process_single_file(input_file, "json")
        progress.display_success(f"JSON output saved to: {Path(json_path).name}")

        # Process the PDF with Markdown output
        progress.display_success("Starting Markdown output processing")
        md_data, md_path = processor.process_single_file(input_file, "markdown")
        progress.display_success(f"Markdown output saved to: {Path(md_path).name}")

        # Display final summary
        progress.display_summary(
            {
                "JSON": {"path": json_path, "status": "Complete"},
                "Markdown": {"path": md_path, "status": "Complete"},
            }
        )

    except Exception as e:
        progress.display_error(f"Error processing PDF: {e}")
        raise


if __name__ == "__main__":
    main()
```

## File: examples/schema_analysis_example.py
```python
"""
Example script demonstrating schema analysis and visualization.
"""

from utils.pipeline.schema.extended_registry import ExtendedSchemaRegistry
from utils.pipeline.utils.progress import PipelineProgress


def main():
    """Run schema analysis example."""
    progress = PipelineProgress()

    try:
        # Initialize extended schema registry
        registry = ExtendedSchemaRegistry()
        schemas = registry.list_schemas()

        if not schemas:
            progress.display_error("No schemas found. Process some documents first.")
            return

        progress.display_success(f"Found {len(schemas)} schemas")

        # Analyze schemas
        progress.display_success("Analyzing schemas...")
        analysis = registry.analyze()

        # Display analysis results
        progress.display_success("\nSchema Analysis Results:")
        progress.display_success(f"Total Schemas: {analysis.get('schema_count', 0)}")

        doc_types = analysis.get("document_types", {})
        if doc_types:
            progress.display_success("\nDocument Types:")
            for doc_type, count in doc_types.items():
                progress.display_success(f"  {doc_type}: {count}")

        # Display common metadata fields
        common_metadata = analysis.get("common_metadata", {})
        if common_metadata:
            progress.display_success("\nCommon Metadata Fields:")
            for field, frequency in sorted(
                common_metadata.items(), key=lambda x: x[1], reverse=True
            ):
                progress.display_success(f"  {field}: {frequency:.2f}")

        # Display table patterns
        table_patterns = analysis.get("table_patterns", {})
        if table_patterns:
            progress.display_success("\nTable Patterns:")
            progress.display_success(
                f"  Schemas with tables: {table_patterns.get('schemas_with_tables', 0)}"
            )
            progress.display_success(
                f"  Average tables per schema: {table_patterns.get('avg_tables_per_schema', 0):.2f}"
            )
            progress.display_success(
                f"  Average rows per table: {table_patterns.get('avg_rows_per_table', 0):.2f}"
            )

        # Generate visualizations if there are multiple schemas
        if len(schemas) >= 2:
            progress.display_success("\nGenerating visualizations...")

            # Create visualizations directory
            import os

            viz_dir = os.path.join(
                "utils", "pipeline", "schema", "data", "visualizations"
            )
            os.makedirs(viz_dir, exist_ok=True)

            # Generate cluster visualization
            try:
                cluster_viz = registry.visualize("clusters", output_dir=viz_dir)
                progress.display_success(
                    f"Cluster visualization saved to: {cluster_viz}"
                )
            except Exception as e:
                progress.display_error(
                    f"Error generating cluster visualization: {str(e)}"
                )

            # Generate feature visualization
            try:
                feature_viz = registry.visualize("features", output_dir=viz_dir)
                progress.display_success(
                    f"Feature visualization saved to: {feature_viz}"
                )
            except Exception as e:
                progress.display_error(
                    f"Error generating feature visualization: {str(e)}"
                )

            # Compare first two schemas
            schema_id1 = schemas[0]["id"]
            schema_id2 = schemas[1]["id"]

            progress.display_success(
                f"\nComparing schemas: {schema_id1} vs {schema_id2}"
            )
            comparison = registry.compare(schema_id1, schema_id2)

            progress.display_success(
                f"Overall Similarity: {comparison.get('overall_similarity', 0):.2f}"
            )
            progress.display_success(
                f"Same Document Type: {comparison.get('same_document_type', False)}"
            )

            # Generate structure visualizations
            try:
                structure_viz = registry.visualize(
                    "structure", [schema_id1, schema_id2], viz_dir
                )
                progress.display_success(
                    f"Structure visualizations saved to: {structure_viz}"
                )
            except Exception as e:
                progress.display_error(
                    f"Error generating structure visualization: {str(e)}"
                )

        progress.display_success("\nSchema analysis complete!")

    except Exception as e:
        progress.display_error(f"Error analyzing schemas: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
```

## File: models/models.py
```python
from typing import Any, Dict, Optional


class PipelineData:
    """Base data model for pipeline data."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """
        Initialize pipeline data.

        Args:
            data: Optional dictionary of data. If None, an empty dict is used.
        """
        self.data = data.copy() if data is not None else {}
```

## File: pipeline.py
```python
"""
Main pipeline orchestrator module.

This module provides the core pipeline functionality for document processing.
"""

import importlib
import os
from typing import Any, Dict, Optional

from utils.pipeline.processors.formatters.factory import FormatterFactory, OutputFormat
from utils.pipeline.utils.logging import get_logger
from utils.pipeline.utils.progress import PipelineProgress
from utils.pipeline.verify.factory import VerifierFactory, VerifierType


class Pipeline:
    """
    Main pipeline orchestrator that manages the flow of document processing.

    The pipeline follows these steps:
    1. Analyze document structure
    2. Clean and normalize content
    3. Extract structured data
    4. Validate extracted data
    5. Format output
    6. Verify output structure
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the pipeline with configuration.

        Args:
            config: Configuration dictionary with pipeline settings
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Initialize strategy selector
        self.strategy_selector = StrategySelector(self.config)

        self.logger.info("Pipeline initialized with config: %s", self.config)

    def run(self, input_path: str, show_progress: bool = True) -> Dict[str, Any]:
        """
        Run the pipeline on the input document.

        Args:
            input_path: Path to the input document
            show_progress: Whether to display progress bars (default: True)

        Returns:
            Processed output data as a dictionary
        """
        self.logger.info("Starting pipeline processing for: %s", input_path)
        progress = PipelineProgress()

        try:
            if not show_progress:
                # Process without progress display
                doc_type = self._detect_document_type(input_path)
                strategies = self.strategy_selector.get_strategies(doc_type)

                # Track stage outputs
                stages_data = {}
                stages_data["setup"] = {"path": input_path, "type": doc_type}

                # 1. Analyze document structure
                analysis_result = self._analyze_document(
                    input_path, strategies.analyzer
                )
                stages_data["analyze"] = analysis_result

                # 2. Clean and normalize content
                cleaned_data = self._clean_content(analysis_result, strategies.cleaner)
                stages_data["clean"] = cleaned_data

                # 3. Extract structured data
                extracted_data = self._extract_data(cleaned_data, strategies.extractor)
                stages_data["extract"] = extracted_data

                # 4. Validate extracted data
                validated_data = self._validate_data(
                    extracted_data, strategies.validator
                )
                stages_data["validate"] = validated_data

                # 5. Classify document type and identify schema pattern
                if self.config.get("enable_classification", True):
                    classification_result = self._classify_document(validated_data)
                    validated_data["classification"] = classification_result

                    # Record schema if configured
                    if self.config.get("record_schemas", False):
                        self._record_schema(
                            validated_data, classification_result["document_type"]
                        )

                # 6. Format output
                output_format = self._get_output_format()
                output_data = self._format_output(validated_data, output_format)
                stages_data["format"] = output_data

                # 7. Verify output structure
                self._verify_output_structure(output_data, output_format)

                return output_data

            # Process with progress display
            with progress:
                progress.start()
                overall_task = progress.add_task(
                    "Processing document", total=7
                )  # Increased to 7 steps

                # Determine document type and select appropriate strategies
                doc_type = self._detect_document_type(input_path)
                self.logger.info("Detected document type: %s", doc_type)
                strategies = self.strategy_selector.get_strategies(doc_type)

                # Track stage outputs
                stages_data = {}

                # Initial document info
                stages_data["setup"] = {"path": input_path, "type": doc_type}
                progress.display_success(f"Processing {os.path.basename(input_path)}")

                # 1. Analyze document structure
                analyze_task = progress.add_task("Step 1: Analyzing document structure")
                analysis_result = self._analyze_document(
                    input_path, strategies.analyzer
                )
                stages_data["analyze"] = analysis_result
                progress.update(analyze_task, advance=1)
                progress.update(overall_task, advance=1)
                progress.display_success("Document structure analyzed")

                # 2. Clean and normalize content
                clean_task = progress.add_task(
                    "Step 2: Cleaning and normalizing content"
                )
                cleaned_data = self._clean_content(analysis_result, strategies.cleaner)
                stages_data["clean"] = cleaned_data
                progress.update(clean_task, advance=1)
                progress.update(overall_task, advance=1)
                progress.display_success("Content cleaned and normalized")

                # 3. Extract structured data
                extract_task = progress.add_task("Step 3: Extracting structured data")
                extracted_data = self._extract_data(cleaned_data, strategies.extractor)
                stages_data["extract"] = extracted_data
                progress.update(extract_task, advance=1)
                progress.update(overall_task, advance=1)
                progress.display_success("Data extracted")

                # 4. Validate extracted data
                validate_task = progress.add_task("Step 4: Validating extracted data")
                validated_data = self._validate_data(
                    extracted_data, strategies.validator
                )
                stages_data["validate"] = validated_data
                progress.update(validate_task, advance=1)
                progress.update(overall_task, advance=1)
                progress.display_success("Data validated")

                # 5. Classify document type and identify schema
                if self.config.get("enable_classification", True):
                    classify_task = progress.add_task(
                        "Step 5: Classifying document type"
                    )
                    classification_result = self._classify_document(validated_data)

                    # Add classification to the data
                    validated_data["classification"] = classification_result

                    # Record schema if configured
                    if self.config.get("record_schemas", False):
                        self._record_schema(
                            validated_data, classification_result["document_type"]
                        )

                    progress.update(classify_task, advance=1)
                    progress.update(overall_task, advance=1)
                    progress.display_success(
                        f"Document classified as: {classification_result['document_type']}"
                    )
                else:
                    # Skip classification but still advance overall progress
                    progress.update(overall_task, advance=1)

                # 6. Format output
                format_task = progress.add_task("Step 6: Formatting output")
                output_format = self._get_output_format()
                output_data = self._format_output(validated_data, output_format)
                stages_data["format"] = output_data
                progress.update(format_task, advance=1)
                progress.update(overall_task, advance=1)
                progress.display_success("Output formatted")

                # 7. Verify output structure
                verify_task = progress.add_task("Step 7: Verifying output structure")
                self._verify_output_structure(output_data, output_format)
                progress.update(verify_task, advance=1)
                progress.update(overall_task, advance=1)

                # Show concise summary
                summary = {
                    "sections": len(output_data.get("content", [])),
                    "tables": len(output_data.get("tables", [])),
                    "validation": output_data.get("validation", {}),
                }

                # Add classification to summary if available
                if "classification" in validated_data:
                    summary["classification"] = validated_data["classification"]

                progress.display_summary(summary)
                progress.display_success("Pipeline processing completed successfully")
                return output_data

        except Exception as e:
            error_msg = f"Pipeline processing failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            progress.display_error(error_msg)
            raise PipelineError(error_msg) from e

    def _classify_document(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify document type and identify schema pattern.

        Args:
            validated_data: Validated document data

        Returns:
            Classification result with document type, confidence, and schema pattern
        """
        # Get classifier configuration
        classifier_config = self.config.get("classification", {})
        classifier_type = classifier_config.get("type", "rule_based")

        # Import the document classifier
        from utils.pipeline.processors.document_classifier import DocumentClassifier

        classifier = DocumentClassifier(classifier_type, classifier_config)

        # Perform classification
        classification = classifier.classify(validated_data)

        # Check if we should match against known schemas
        if self.config.get("match_schemas", False):
            self._match_schema(validated_data, classification)

        return classification

    def _match_schema(
        self, document_data: Dict[str, Any], classification: Dict[str, Any]
    ) -> None:
        """

                Match document against known schemas and update classification.

        Args:
            document_data: Document data to match
            classification: Classification result to update
        """
        # Import the schema registry
        from utils.pipeline.schema.registry import SchemaRegistry

        registry = SchemaRegistry()

        # Match against known schemas
        schema_id, confidence = registry.match(document_data)

        if schema_id and confidence > 0.7:  # Only use if high confidence
            # Get the schema
            schema = registry.get_schema(schema_id)
            if schema:
                # Update classification with schema information
                classification["schema_id"] = schema_id
                classification["schema_match_confidence"] = confidence
                classification["schema_document_type"] = schema.get(
                    "document_type", "UNKNOWN"
                )

    def _record_schema(self, document_data: Dict[str, Any], document_type: str) -> None:
        """
        Record document schema in the registry.

        Args:
            document_data: Document data to record
            document_type: Type of the document
        """
        # Import the schema registry
        from utils.pipeline.schema.registry import SchemaRegistry

        registry = SchemaRegistry()

        # Get document name from metadata or path
        document_name = None
        if "metadata" in document_data and "title" in document_data["metadata"]:
            document_name = document_data["metadata"]["title"]
        elif "setup" in document_data and "path" in document_data["setup"]:
            document_name = os.path.basename(document_data["setup"]["path"])

        # Record the schema with document name
        registry.record(document_data, document_type, document_name)

    def _detect_document_type(self, input_path: str) -> str:
        """Detect the document type based on file extension or content analysis."""
        _, ext = os.path.splitext(input_path)
        ext = ext.lower()

        if ext == ".pdf":
            return "pdf"
        elif ext in [".xlsx", ".xls"]:
            return "excel"
        elif ext in [".docx", ".doc"]:
            return "word"
        elif ext == ".txt":
            return "text"
        else:
            # Default to generic type
            return "generic"

    def _analyze_document(self, input_path: str, analyzer) -> Dict[str, Any]:
        """Analyze document structure and content."""
        return analyzer.analyze(input_path)

    def _clean_content(
        self, analysis_result: Dict[str, Any], cleaner
    ) -> Dict[str, Any]:
        """Clean and normalize document content."""
        return cleaner.clean(analysis_result)

    def _extract_data(self, cleaned_data: Dict[str, Any], extractor) -> Dict[str, Any]:
        """Extract structured data from cleaned content."""
        return extractor.extract(cleaned_data)

    def _validate_data(
        self, extracted_data: Dict[str, Any], validator
    ) -> Dict[str, Any]:
        """Validate extracted data against schemas."""
        return validator.validate(extracted_data)

    def _format_output(
        self, validated_data: Dict[str, Any], output_format: OutputFormat
    ) -> Dict[str, Any]:
        """Format validated data using the specified formatter."""
        formatter = FormatterFactory.create_formatter(output_format)
        return formatter.format(validated_data)

    def _verify_output_structure(
        self, output_data: Dict[str, Any], output_format: OutputFormat
    ) -> None:
        """
        Verify the structure of formatted output.

        Args:
            output_data: Formatted output data to verify
            output_format: Format type of the output

        Raises:
            PipelineError: If verification fails
        """
        # Map output format to verifier type
        verifier_map = {
            OutputFormat.JSON: VerifierType.JSON_TREE,
            OutputFormat.MARKDOWN: VerifierType.MARKDOWN,
        }

        verifier_type = verifier_map.get(output_format)
        if not verifier_type:
            self.logger.warning(f"No verifier available for format: {output_format}")
            return

        try:
            verifier = VerifierFactory.create_verifier(verifier_type)
            is_valid, errors, warnings = verifier.verify(output_data)

            # Log warnings
            for warning in warnings:
                self.logger.warning(f"Structure warning: {warning}")

            # Raise error if validation failed
            if not is_valid:
                error_msg = "\n".join(errors)
                raise PipelineError(
                    f"Output structure verification failed:\n{error_msg}"
                )

        except ValueError as e:
            self.logger.warning(f"Verification skipped: {str(e)}")

    def _get_output_format(self) -> OutputFormat:
        """Get output format from config or use default."""
        format_name = self.config.get("output_format", "json").upper()
        try:
            return OutputFormat[format_name]
        except KeyError:
            self.logger.warning(f"Unsupported output format: {format_name}, using JSON")
            return OutputFormat.JSON

    def save_output(self, output_data: Dict[str, Any], output_path: str) -> None:
        """Save the output data to a file."""
        self.logger.info("Saving output to: %s", output_path)

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Get formatter based on file extension
        output_format = self._get_format_from_path(output_path)
        formatter = FormatterFactory.create_formatter(output_format)

        # Format and write the data
        formatter.write(output_data, output_path)

    def _get_format_from_path(self, path: str) -> OutputFormat:
        """Determine output format from file extension."""
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        format_map = {
            ".json": OutputFormat.JSON,
            ".md": OutputFormat.MARKDOWN,
            ".markdown": OutputFormat.MARKDOWN,
        }

        return format_map.get(ext, OutputFormat.JSON)


class StrategySelector:
    """Selects appropriate processing strategies based on document type."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(__name__ + ".StrategySelector")

    def get_strategies(self, doc_type: str) -> "StrategySet":
        """Get the set of strategies for a document type."""
        self.logger.info("Selecting strategies for document type: %s", doc_type)

        try:
            # Get strategy paths from config
            strategy_paths = self.config.get("strategies", {})
            if not strategy_paths:
                raise ImportError("No strategy paths configured")

            # Get the strategy paths for this document type
            doc_strategies = strategy_paths.get(doc_type)
            if not doc_strategies:
                raise ImportError(f"No strategy paths configured for {doc_type}")

            # If the strategy is a string, use it as a legacy format
            if isinstance(doc_strategies, str):
                return self._get_legacy_strategies(doc_strategies)

            # Import each strategy component
            analyzer = self._import_strategy(doc_strategies.get("analyzer"))
            cleaner = self._import_strategy(doc_strategies.get("cleaner"))
            extractor = self._import_strategy(doc_strategies.get("extractor"))
            validator = self._import_strategy(doc_strategies.get("validator"))

            return StrategySet(
                analyzer=analyzer,
                cleaner=cleaner,
                extractor=extractor,
                validator=validator,
                formatter=None,  # Formatter now handled by factory
            )

        except (ImportError, AttributeError) as e:
            self.logger.error(
                "Failed to import strategies for %s: %s", doc_type, str(e)
            )
            # Fall back to mock strategies for now
            return StrategySet(
                analyzer=MockStrategy(),
                cleaner=MockStrategy(),
                extractor=MockStrategy(),
                validator=MockStrategy(),
                formatter=None,
            )

    def _import_strategy(self, strategy_path: Optional[str]) -> Any:
        """Import a strategy class and create an instance."""
        if not strategy_path:
            return MockStrategy()

        try:
            module_path, class_name = strategy_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            strategy_class = getattr(module, class_name)
            return strategy_class()
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to import strategy {strategy_path}: {str(e)}")
            return MockStrategy()

    def _get_legacy_strategies(self, strategy_path: str) -> "StrategySet":
        """Handle legacy format where all strategies come from one module."""
        try:
            module_path = strategy_path
            module = importlib.import_module(module_path)

            return StrategySet(
                analyzer=module.Analyzer(),
                cleaner=module.Cleaner(),
                extractor=module.Extractor(),
                validator=module.Validator(),
                formatter=None,
            )
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to import legacy strategies: {str(e)}")
            return StrategySet(
                analyzer=MockStrategy(),
                cleaner=MockStrategy(),
                extractor=MockStrategy(),
                validator=MockStrategy(),
                formatter=None,
            )


class StrategySet:
    """A set of strategies for processing a document."""

    def __init__(self, analyzer, cleaner, extractor, validator, formatter):
        self.analyzer = analyzer
        self.cleaner = cleaner
        self.extractor = extractor
        self.validator = validator
        self.formatter = formatter


class MockStrategy:
    """A mock strategy for testing or when real strategies are not available."""

    def analyze(self, input_path):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File not found: {input_path}")
        return {"mock_analysis": True, "path": input_path}

    def clean(self, data):
        return {"mock_cleaned": True, "data": data}

    def extract(self, data):
        return {"mock_extracted": True, "data": data}

    def validate(self, data):
        return {"mock_validated": True, "data": data}


class PipelineError(Exception):
    """Exception raised for errors in the pipeline processing."""

    pass
```

## File: processors/classifiers/__init__.py
```python
"""
Document classifiers package.

This package contains various document classification strategies.
"""
```

## File: processors/classifiers/pattern_matcher.py
```python
"""
Pattern matcher document classifier.

This module provides a pattern matching approach to document classification.
"""

from typing import Any, Dict, List, Optional

from utils.pipeline.utils.logging import get_logger


class PatternMatcherClassifier:
    """
    Classifies documents using pattern matching.

    This classifier uses predefined patterns to identify document types
    based on their structure, content, and metadata.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the pattern matcher classifier.

        Args:
            config: Configuration dictionary for the classifier
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Define document patterns
        self.patterns = self._load_patterns()

    def classify(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify the document using pattern matching.

        Args:
            document_data: Processed document data
            features: Extracted features from the document

        Returns:
            Classification result with document type, confidence, and schema pattern
        """
        self.logger.info("Classifying document using pattern matching")

        try:
            # Find best matching pattern
            best_match = self._find_best_match(document_data, features)

            self.logger.info(
                f"Document classified as: {best_match['document_type']} with confidence: {best_match['confidence']}"
            )
            return best_match

        except Exception as e:
            self.logger.error(f"Error classifying document: {str(e)}", exc_info=True)
            # Return unknown classification on error
            return {
                "document_type": "UNKNOWN",
                "confidence": 0.0,
                "schema_pattern": "unknown",
                "key_features": [],
            }

    def _load_patterns(self) -> List[Dict[str, Any]]:
        """
        Load document patterns from configuration or use defaults.

        Returns:
            List of document patterns
        """
        # Use patterns from config if available
        if "patterns" in self.config:
            return self.config["patterns"]

        # Default patterns
        return [
            {
                "name": "PROPOSAL",
                "schema_pattern": "standard_proposal",
                "required_features": ["has_payment_terms", "has_delivery_terms"],
                "optional_features": ["proposal_in_title", "has_regarding_section"],
                "section_patterns": [
                    "proposal",
                    "regarding",
                    "company",
                    "payment",
                    "delivery",
                ],
                "content_patterns": ["proposal", "offer", "proposed", "scope of work"],
            },
            {
                "name": "QUOTATION",
                "schema_pattern": "standard_quotation",
                "required_features": ["has_dollar_amounts"],
                "optional_features": ["has_subtotal", "has_total", "has_quantities"],
                "section_patterns": [
                    "quote",
                    "quotation",
                    "estimate",
                    "pricing",
                    "subtotal",
                    "total",
                ],
                "content_patterns": [
                    "quote",
                    "price",
                    "cost",
                    "amount",
                    "total",
                    "subtotal",
                    "$",
                ],
            },
            {
                "name": "SPECIFICATION",
                "schema_pattern": "technical_specification",
                "required_features": ["has_technical_terms", "has_measurements"],
                "optional_features": ["spec_in_title"],
                "section_patterns": [
                    "specification",
                    "spec",
                    "technical",
                    "requirements",
                    "dimensions",
                ],
                "content_patterns": [
                    "specification",
                    "technical",
                    "dimensions",
                    "performance",
                    "material",
                ],
            },
            {
                "name": "INVOICE",
                "schema_pattern": "standard_invoice",
                "required_features": ["has_dollar_amounts"],
                "optional_features": ["has_subtotal", "has_total", "invoice_in_title"],
                "section_patterns": [
                    "invoice",
                    "bill",
                    "receipt",
                    "payment",
                    "due date",
                ],
                "content_patterns": [
                    "invoice",
                    "bill",
                    "amount due",
                    "payment",
                    "total",
                    "$",
                ],
            },
            {
                "name": "TERMS_AND_CONDITIONS",
                "schema_pattern": "legal_terms",
                "required_features": ["has_legal_language"],
                "optional_features": ["has_caps_sections", "terms_in_title"],
                "section_patterns": [
                    "terms",
                    "conditions",
                    "agreement",
                    "contract",
                    "warranty",
                    "liability",
                ],
                "content_patterns": [
                    "shall",
                    "herein",
                    "pursuant",
                    "liability",
                    "warranty",
                    "indemnify",
                ],
            },
        ]

    def _find_best_match(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Find the best matching pattern for the document.

        Args:
            document_data: Processed document data
            features: Extracted features from the document

        Returns:
            Classification result with document type, confidence, and schema pattern
        """
        best_match = {
            "document_type": "UNKNOWN",
            "confidence": 0.0,
            "schema_pattern": "unknown",
            "key_features": [],
        }

        # Extract content for pattern matching
        content = document_data.get("content", [])
        all_content = " ".join(
            [section.get("content", "").lower() for section in content]
        )
        section_titles = features.get("section_titles", [])

        # Check each pattern
        for pattern in self.patterns:
            confidence = 0.0
            matched_features = []

            # Check required features
            required_count = len(pattern["required_features"])
            matched_required = 0

            for feature in pattern["required_features"]:
                if features.get(feature, False):
                    matched_required += 1
                    matched_features.append(feature)

            # If not all required features match, skip this pattern
            if matched_required < required_count:
                continue

            # Add confidence for required features
            confidence += 0.5 * (matched_required / max(1, required_count))

            # Check optional features
            optional_count = len(pattern["optional_features"])
            matched_optional = 0

            for feature in pattern["optional_features"]:
                if features.get(feature, False):
                    matched_optional += 1
                    matched_features.append(feature)

            # Add confidence for optional features
            if optional_count > 0:
                confidence += 0.3 * (matched_optional / optional_count)

            # Check section patterns
            section_matches = 0
            for section_pattern in pattern["section_patterns"]:
                if any(section_pattern in title for title in section_titles):
                    section_matches += 1
                    matched_features.append(f"section_contains_{section_pattern}")

            # Add confidence for section patterns
            if len(pattern["section_patterns"]) > 0:
                confidence += 0.1 * (section_matches / len(pattern["section_patterns"]))

            # Check content patterns
            content_matches = 0
            for content_pattern in pattern["content_patterns"]:
                if content_pattern in all_content:
                    content_matches += 1
                    matched_features.append(f"content_contains_{content_pattern}")

            # Add confidence for content patterns
            if len(pattern["content_patterns"]) > 0:
                confidence += 0.1 * (content_matches / len(pattern["content_patterns"]))

            # Update best match if this pattern has higher confidence
            if confidence > best_match["confidence"]:
                best_match = {
                    "document_type": pattern["name"],
                    "confidence": min(1.0, confidence),  # Cap at 1.0
                    "schema_pattern": pattern["schema_pattern"],
                    "key_features": matched_features,
                }

        return best_match
```

## File: processors/classifiers/rule_based.py
```python
"""
Rule-based document classifier.

This module provides a rule-based approach to document classification.
"""

import os
import re
from typing import Any, Dict, List, Optional, Tuple

from utils.pipeline.utils.logging import get_logger


class RuleBasedClassifier:
    """
    Classifies documents using a rule-based approach.

    This classifier uses a set of predefined rules to identify document types
    based on their structure, content, and metadata.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the rule-based classifier.

        Args:
            config: Configuration dictionary for the classifier
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Get classification rules from config
        self.classification_config = self.config.get("classification", {})
        self.rules_config = self.classification_config.get("rules", {})
        self.default_threshold = self.classification_config.get(
            "default_threshold", 0.3
        )
        self.filename_patterns = self.classification_config.get("filename_patterns", {})

    def classify(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify the document using rule-based approach.

        Args:
            document_data: Processed document data
            features: Extracted features from the document

        Returns:
            Classification result with document type, confidence, and schema pattern
        """
        # Check filename patterns if path is available
        if "path" in document_data:
            filename = os.path.basename(document_data["path"])
            for doc_type, pattern in self.filename_patterns.items():
                if re.search(pattern, filename):
                    self.logger.info(
                        f"Matched filename pattern for {doc_type}: {filename}"
                    )
                    return {
                        "document_type": doc_type,
                        "confidence": 0.8,  # High confidence for filename match
                        "schema_pattern": self.rules_config.get(doc_type, {}).get(
                            "schema_pattern", "standard"
                        ),
                        "key_features": ["filename_match"],
                    }

        # Apply configured rules
        best_match = self._get_best_match(document_data, features)

        # Only use generic classification if confidence is very low
        if (
            best_match[0] == "UNKNOWN" or best_match[1] < 0.2
        ):  # Lower threshold for falling back to generic
            # If no specific type matched or confidence is very low, try to determine a generic type
            return self._classify_generic(document_data, features)

        return {
            "document_type": best_match[0],
            "confidence": best_match[1],
            "schema_pattern": best_match[2],
            "key_features": best_match[3],
        }

    def _get_best_match(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Tuple[str, float, str, List[str]]:
        """
        Apply all configured rules and get the best matching document type.

        Args:
            document_data: Processed document data
            features: Extracted features from the document

        Returns:
            Tuple of (document_type, confidence, schema_pattern, key_features)
        """
        best_match = ("UNKNOWN", 0.0, "unknown", [])

        # Apply each configured rule
        for doc_type, rule in self.rules_config.items():
            confidence = 0.0
            key_features = []

            # Check title keywords
            section_titles = features.get("section_titles", [])
            title_keywords = rule.get("title_keywords", [])
            if title_keywords:
                matches = sum(
                    1
                    for keyword in title_keywords
                    if any(keyword.lower() in title.lower() for title in section_titles)
                )
                if matches > 0:
                    title_weight = rule.get("weights", {}).get("title_match", 0.4)
                    confidence += title_weight * (matches / len(title_keywords))
                    key_features.append("title_match")

            # Check content keywords
            content = " ".join(
                [
                    section.get("content", "")
                    for section in document_data.get("content", [])
                ]
            )
            content_keywords = rule.get("content_keywords", [])
            if content_keywords:
                matches = sum(
                    1
                    for keyword in content_keywords
                    if keyword.lower() in content.lower()
                )
                if matches > 0:
                    content_weight = rule.get("weights", {}).get("content_match", 0.3)
                    confidence += content_weight * (matches / len(content_keywords))
                    key_features.append("content_match")

            # Check patterns
            patterns = rule.get("patterns", [])
            if patterns:
                matches = sum(
                    1 for pattern in patterns if pattern.lower() in content.lower()
                )
                if matches > 0:
                    pattern_weight = rule.get("weights", {}).get("pattern_match", 0.3)
                    confidence += pattern_weight * (matches / len(patterns))
                    key_features.append("pattern_match")

            # Check if confidence exceeds threshold
            threshold = rule.get("threshold", 0.5)
            if confidence > threshold and confidence > best_match[1]:
                schema_pattern = rule.get("schema_pattern", "standard")
                best_match = (doc_type, confidence, schema_pattern, key_features)

        return best_match

    def _classify_generic(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify document into generic categories when specific types don't match.

        Args:
            document_data: Processed document data
            features: Extracted features from the document

        Returns:
            Classification result with generic document type
        """
        # Check if it's a form
        if features.get("table_count", 0) > 3:
            return {
                "document_type": "FORM",
                "confidence": 0.6,
                "schema_pattern": "tabular_form",
                "key_features": ["multiple_tables", "structured_layout"],
            }

        # Check if it's a report
        if features.get("section_count", 0) > 10:
            return {
                "document_type": "REPORT",
                "confidence": 0.5,
                "schema_pattern": "sectioned_document",
                "key_features": ["multiple_sections", "hierarchical_structure"],
            }

        # Default to generic document
        return {
            "document_type": "GENERIC_DOCUMENT",
            "confidence": self.default_threshold,
            "schema_pattern": "unknown",
            "key_features": [],
        }
```

## File: processors/document_classifier.py
```python
"""
Document classifier module.

This module provides functionality for classifying documents based on their structure and content.
"""

from typing import Any, Dict, Optional

from utils.pipeline.utils.logging import get_logger


class DocumentClassifier:
    """
    Classifies documents based on their structure and content patterns.

    This classifier analyzes the document structure to identify patterns that match
    known document types such as proposals, quotations, specifications, etc.
    """

    def __init__(
        self,
        classifier_type: str = "rule_based",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the document classifier.

        Args:
            classifier_type: Type of classifier to use (rule_based, pattern_matcher, etc.)
            config: Configuration dictionary for the classifier
        """
        self.classifier_type = classifier_type
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Initialize classifier strategy based on type
        if classifier_type == "rule_based":
            from utils.pipeline.processors.classifiers.rule_based import (
                RuleBasedClassifier,
            )

            self.classifier_strategy = RuleBasedClassifier(self.config)
        elif classifier_type == "pattern_matcher":
            from utils.pipeline.processors.classifiers.pattern_matcher import (
                PatternMatcherClassifier,
            )

            self.classifier_strategy = PatternMatcherClassifier(self.config)
        else:
            # Default to rule-based
            from utils.pipeline.processors.classifiers.rule_based import (
                RuleBasedClassifier,
            )

            self.classifier_strategy = RuleBasedClassifier(self.config)
            self.logger.warning(
                f"Unknown classifier type: {classifier_type}, using rule_based"
            )

    def classify(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify the document based on its structure and content.

        Args:
            document_data: Processed document data

        Returns:
            Classification result with document type, confidence, and schema pattern
        """
        self.logger.info("Classifying document")

        try:
            # Extract features from document
            features = self._extract_features(document_data)

            # Classify document using strategy
            classification = self.classifier_strategy.classify(document_data, features)

            self.logger.info(
                f"Document classified as: {classification['document_type']} with confidence: {classification['confidence']}"
            )
            return classification

        except Exception as e:
            self.logger.error(f"Error classifying document: {str(e)}", exc_info=True)
            # Return unknown classification on error
            return {
                "document_type": "UNKNOWN",
                "confidence": 0.0,
                "schema_pattern": "unknown",
                "key_features": [],
            }

    def _extract_features(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from document data for classification.

        Args:
            document_data: Processed document data

        Returns:
            Dictionary of extracted features
        """
        features = {}

        # Extract metadata features
        metadata = document_data.get("metadata", {})
        features["has_title"] = bool(metadata.get("title"))
        features["has_author"] = bool(metadata.get("author"))
        features["creator"] = metadata.get("creator", "")
        features["producer"] = metadata.get("producer", "")

        # Extract content features
        content = document_data.get("content", [])
        features["section_count"] = len(content)

        # Extract section titles
        section_titles = [
            section.get("title", "").lower()
            for section in content
            if section.get("title")
        ]
        features["section_titles"] = section_titles

        # Check for common document patterns
        features["has_payment_terms"] = any(
            "payment" in title for title in section_titles
        )
        features["has_delivery_terms"] = any(
            "delivery" in title for title in section_titles
        )
        features["has_subtotal"] = any("subtotal" in title for title in section_titles)
        features["has_total"] = any("total" in title for title in section_titles)

        # Check for pricing patterns in content
        all_content = " ".join([section.get("content", "") for section in content])
        features["has_dollar_amounts"] = "$" in all_content
        features["has_quantities"] = any(word.isdigit() for word in all_content.split())

        # Check for tables
        tables = document_data.get("tables", [])
        features["table_count"] = len(tables)

        return features
```

## File: processors/formatters/factory.py
```python
"""
Formatter factory implementation.

This module provides a factory for creating different output formatters.
"""

from enum import Enum, auto
from typing import Dict, Type

from utils.pipeline.processors.formatters.json_formatter import JSONFormatter
from utils.pipeline.processors.formatters.markdown_formatter import MarkdownFormatter
from utils.pipeline.strategies.formatter import FormatterStrategy
from utils.pipeline.utils.logging import get_logger


class OutputFormat(Enum):
    """Supported output formats."""

    JSON = auto()
    MARKDOWN = auto()


class FormatterFactory:
    """Factory for creating formatter instances."""

    _formatters: Dict[OutputFormat, Type[FormatterStrategy]] = {
        OutputFormat.JSON: JSONFormatter,
        OutputFormat.MARKDOWN: MarkdownFormatter,
    }

    @classmethod
    def create_formatter(cls, format_type: OutputFormat) -> FormatterStrategy:
        """
        Create a formatter instance for the specified format.

        Args:
            format_type: Type of formatter to create

        Returns:
            Formatter instance

        Raises:
            ValueError: If format type is not supported
        """
        logger = get_logger(__name__)

        try:
            formatter_class = cls._formatters[format_type]
            return formatter_class()
        except KeyError:
            logger.error(f"Unsupported format type: {format_type}")
            raise ValueError(f"Unsupported format type: {format_type}")

    @classmethod
    def register_formatter(
        cls, format_type: OutputFormat, formatter_class: Type[FormatterStrategy]
    ) -> None:
        """
        Register a new formatter type.

        Args:
            format_type: Format type to register
            formatter_class: Formatter class to use for this format
        """
        logger = get_logger(__name__)
        logger.info(
            f"Registering formatter for {format_type}: {formatter_class.__name__}"
        )
        cls._formatters[format_type] = formatter_class
```

## File: processors/formatters/json_formatter.py
```python
"""
JSON formatter implementation.

This module provides functionality for formatting extracted PDF content into JSON.
"""

import json
from typing import Any, Dict, List

from utils.pipeline.strategies.formatter import FormatterStrategy
from utils.pipeline.utils.logging import get_logger


class JSONFormatter(FormatterStrategy):
    """Formats extracted PDF content into readable JSON with proper indentation."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def format(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the analyzed data into a hierarchical JSON structure.

        Args:
            analyzed_data: Data from the PDF analyzer

        Returns:
            Formatted JSON structure with proper indentation
        """
        self.logger.info("Formatting PDF content as JSON")

        try:
            # Build hierarchical structure
            formatted_data = {
                "document": {
                    "metadata": analyzed_data.get("metadata", {}),
                    "path": analyzed_data.get("path", ""),
                    "type": analyzed_data.get("type", ""),
                },
                "content": self._build_content_tree(analyzed_data.get("sections", [])),
                "tables": analyzed_data.get("tables", []),
                "summary": analyzed_data.get("summary", {}),
                "validation": analyzed_data.get("validation", {}),
            }

            return formatted_data

        except Exception as e:
            self.logger.error(f"Error formatting PDF content: {str(e)}", exc_info=True)
            raise

    def _build_content_tree(
        self, sections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Build a hierarchical tree structure from flat sections list.

        Args:
            sections: List of section dictionaries

        Returns:
            List of sections with hierarchical structure
        """
        if not sections:
            return []

        # Initialize with root level sections
        result = []
        current_section = None
        current_level = 0
        section_stack = []  # [(section, level)]

        for section in sections:
            title = section["title"]
            level = self._determine_section_level(title)

            new_section = {
                "title": title,
                "content": section.get("content", ""),
                "children": [],
                "level": level,
            }

            # Add any additional metadata
            if "font" in section:
                new_section["font"] = section["font"]

            # Handle section nesting
            if not current_section:
                # First section
                result.append(new_section)
                current_section = new_section
                current_level = level
                section_stack.append((current_section, current_level))
            else:
                if level > current_level:
                    # Child section
                    current_section["children"].append(new_section)
                    section_stack.append((current_section, current_level))
                    current_section = new_section
                    current_level = level
                else:
                    # Sibling or uncle section
                    while section_stack and section_stack[-1][1] >= level:
                        section_stack.pop()

                    if section_stack:
                        # Add as child to nearest parent
                        parent, _ = section_stack[-1]
                        parent["children"].append(new_section)
                    else:
                        # No parent found, add to root
                        result.append(new_section)

                    current_section = new_section
                    current_level = level
                    section_stack.append((current_section, current_level))

        return result

    def _determine_section_level(self, title: str) -> int:
        """
        Determine section level based on title format.

        Args:
            title: Section title

        Returns:
            Integer indicating section level (0 = top level)
        """
        # Main section headers (e.g., "HEATING SYSTEMS")
        if title.isupper() and len(title.split()) > 1:
            return 0

        # Numbered sections (e.g., "1.0", "2.1", etc.)
        if any(title.startswith(str(i) + ".") for i in range(1, 20)):
            return 1

        # Lettered subsections (e.g., "A.", "B.", etc.)
        if len(title) == 2 and title[0].isupper() and title[1] == ".":
            return 2

        # Numbered subsections (e.g., "1.", "2.", etc.)
        if title.rstrip(".").isdigit():
            return 2

        # Default to deepest level
        return 3

    def write(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Write formatted data to a JSON file with proper indentation.

        Args:
            data: Formatted data to write
            output_path: Path to output file
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
```

## File: processors/formatters/markdown_formatter.py
```python
"""
Markdown formatter implementation.

This module provides functionality for formatting extracted PDF content into Markdown.
"""

from typing import Any, Dict, List

from utils.pipeline.strategies.formatter import FormatterStrategy
from utils.pipeline.utils.logging import get_logger


class MarkdownFormatter(FormatterStrategy):
    """Formats extracted PDF content into readable Markdown."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def format(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the analyzed data into a Markdown structure.

        Args:
            analyzed_data: Data from the PDF analyzer

        Returns:
            Formatted data structure with Markdown content
        """
        self.logger.info("Formatting PDF content as Markdown")

        try:
            # Build hierarchical structure
            content_tree = self._build_content_tree(analyzed_data.get("sections", []))

            # Convert content tree to markdown string
            content_markdown = ""
            for section in content_tree:
                content_markdown += self._format_section_to_markdown(section)

            # Convert tables to markdown string
            tables_markdown = ""
            for table in analyzed_data.get("tables", []):
                tables_markdown += self._format_table_to_markdown(table)

            # Create formatted data with strings for content and tables
            formatted_data = {
                "document": {
                    "metadata": analyzed_data.get("metadata", {}),
                    "path": analyzed_data.get("path", ""),
                    "type": analyzed_data.get("type", ""),
                },
                "content": content_markdown,
                "tables": tables_markdown,
                "summary": analyzed_data.get("summary", {}),
                "validation": analyzed_data.get("validation", {}),
            }

            # Add classification if present
            if "classification" in analyzed_data:
                formatted_data["classification"] = analyzed_data["classification"]

            return formatted_data

        except Exception as e:
            self.logger.error(f"Error formatting PDF content: {str(e)}", exc_info=True)
            raise

    def _build_content_tree(
        self, sections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Build a hierarchical tree structure from flat sections list.
        This matches the structure returned by JSONFormatter._build_content_tree().

        Args:
            sections: List of section dictionaries

        Returns:
            List of sections with hierarchical structure
        """
        if not sections:
            return []

        # Initialize with root level sections
        result = []
        current_section = None
        current_level = 0
        section_stack = []  # [(section, level)]

        for section in sections:
            title = section.get("title", "")
            level = section.get("level", 0)
            content = section.get("content", "")

            new_section = {
                "title": title,
                "content": content,
                "children": [],
                "level": level,
            }

            # Add any additional metadata
            if "font" in section:
                new_section["font"] = section["font"]

            # Handle section nesting
            if not current_section:
                # First section
                result.append(new_section)
                current_section = new_section
                current_level = level
                section_stack.append((current_section, current_level))
            else:
                if level > current_level:
                    # Child section
                    current_section["children"].append(new_section)
                    section_stack.append((current_section, current_level))
                    current_section = new_section
                    current_level = level
                else:
                    # Sibling or uncle section
                    while section_stack and section_stack[-1][1] >= level:
                        section_stack.pop()

                    if section_stack:
                        # Add as child to nearest parent
                        parent, _ = section_stack[-1]
                        parent["children"].append(new_section)
                    else:
                        # No parent found, add to root
                        result.append(new_section)

                    current_section = new_section
                    current_level = level
                    section_stack.append((current_section, current_level))

        return result

    def _format_section_to_markdown(self, section: Dict[str, Any]) -> str:
        """
        Convert a section dictionary to markdown text.

        Args:
            section: Section dictionary with title, content, children, and level

        Returns:
            Markdown formatted string for the section
        """
        markdown_lines = []

        # Add section header with appropriate level
        if section.get("title"):
            level = section.get("level", 0)
            markdown_lines.append(f"{'#' * (level + 1)} {section['title']}\n")

        # Add section content
        if section.get("content"):
            markdown_lines.append(f"{section['content']}\n")

        # Process children recursively
        for child in section.get("children", []):
            markdown_lines.append(self._format_section_to_markdown(child))

        return "\n".join(markdown_lines)

    def _format_table_to_markdown(self, table: Dict[str, Any]) -> str:
        """
        Format a table dictionary to markdown.

        Args:
            table: Table dictionary with headers and data

        Returns:
            Markdown formatted table string
        """
        markdown_lines = []

        if "headers" in table and "data" in table:
            # Add table headers
            headers = table["headers"]
            markdown_lines.append("| " + " | ".join(headers) + " |")
            markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

            # Add table data
            for row in table["data"]:
                markdown_lines.append(
                    "| " + " | ".join(str(cell) for cell in row) + " |"
                )

            markdown_lines.append("")  # Add empty line after table

        return "\n".join(markdown_lines)

    def write(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Write formatted data to a Markdown file.

        Args:
            data: Formatted data to write
            output_path: Path to output file
        """
        with open(output_path, "w", encoding="utf-8") as f:
            # Write document metadata
            doc = data.get("document", {})
            f.write("# Document Information\n\n")
            f.write(f"- Path: {doc.get('path', '')}\n")
            f.write(f"- Type: {doc.get('type', '')}\n\n")

            # Write metadata
            metadata = doc.get("metadata", {})
            if metadata:
                f.write("## Metadata\n\n")
                for key, value in metadata.items():
                    f.write(f"- {key}: {value}\n")
                f.write("\n")

            # Write content
            content = data.get("content", "")
            if content:
                f.write("# Content\n\n")
                f.write(content)
                f.write("\n")

            # Write tables
            tables = data.get("tables", "")
            if tables:
                f.write("# Tables\n\n")
                f.write(tables)
                f.write("\n")

            # Write summary
            summary = data.get("summary", {})
            if summary:
                f.write("# Summary\n\n")
                for key, value in summary.items():
                    f.write(f"## {key}\n\n{value}\n\n")

            # Write classification if present
            classification = data.get("classification", {})
            if classification:
                f.write("# Classification\n\n")
                f.write(
                    f"- Document Type: {classification.get('document_type', 'Unknown')}\n"
                )
                f.write(f"- Confidence: {classification.get('confidence', 0.0):.2f}\n")
                f.write(
                    f"- Schema Pattern: {classification.get('schema_pattern', 'Unknown')}\n"
                )

                key_features = classification.get("key_features", [])
                if key_features:
                    f.write("- Key Features:\n")
                    for feature in key_features:
                        f.write(f"  - {feature}\n")
                f.write("\n")
```

## File: processors/pdf_extractor.py
```python
"""
PDF data extractor implementation.

This module provides functionality for extracting structured data from PDF content.
"""

import re
from typing import Any, Dict, List, Tuple

import fitz  # PyMuPDF

from utils.pipeline.strategies.base import ExtractorStrategy
from utils.pipeline.utils.logging import get_logger


class PDFExtractor(ExtractorStrategy):
    """Extracts structured data from PDF content."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def extract(self, cleaned_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from cleaned PDF content.

        Args:
            cleaned_data: Cleaned data from the PDF cleaner

        Returns:
            Extracted structured data including schema
        """
        self.logger.info(
            f"Extracting data from PDF: {cleaned_data.get('path', 'unknown')}"
        )

        try:
            # Extract sections and content
            doc = fitz.open(cleaned_data["path"])

            # Extract text by sections
            sections = self._extract_sections(doc)

            # Extract tables if present
            tables = self._extract_tables(doc)

            # Extract schema structure
            schema = self._extract_schema(sections)

            doc.close()

            # Return extracted data
            return {
                "metadata": cleaned_data["metadata"],
                "sections": sections,
                "tables": tables,
                "schema": schema,
                "path": cleaned_data["path"],
            }

        except Exception as e:
            self.logger.error(
                f"Error extracting data from PDF: {str(e)}", exc_info=True
            )
            raise

    def _extract_schema(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract schema structure from sections.

        Args:
            sections: List of extracted sections

        Returns:
            Schema structure
        """
        schema = {
            "type": "object",
            "title": "CSI Specification Schema",
            "properties": {},
            "required": [],
        }

        # Track section numbers and their hierarchy
        current_section = None
        section_pattern = re.compile(r"^([A-Z][0-9]+(?:\.[0-9]+)*)")

        for section in sections:
            title = section.get("title", "")
            match = section_pattern.match(title)

            if match:
                section_number = match.group(1)
                section_name = title.replace(section_number, "").strip()

                # Add to schema properties
                schema["properties"][section_number] = {
                    "type": "object",
                    "title": section_name,
                    "properties": {
                        "content": {"type": "string"},
                        "subsections": {"type": "object"},
                    },
                }

                # Track required fields
                schema["required"].append(section_number)

                # Handle subsections
                if "children" in section:
                    subsections_schema = self._extract_schema(section["children"])
                    schema["properties"][section_number]["properties"][
                        "subsections"
                    ] = subsections_schema

        return schema

    def _extract_sections(self, doc) -> List[Dict[str, Any]]:
        """
        Extract sections from the PDF document.

        Args:
            doc: PyMuPDF document

        Returns:
            List of sections with titles and content
        """
        sections = []
        current_section = {"title": "Introduction", "content": ""}

        for page in doc:
            text = page.get_text("text")

            # Split text into lines
            lines = text.split("\n")

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Heuristic for section headers (customize based on document)
                if (
                    re.match(r"^[0-9.]+\s+[A-Z]", line)
                    or line.isupper()
                    or len(line) < 50
                    and line.endswith(":")
                ):
                    # Save previous section if it has content
                    if current_section["content"]:
                        sections.append(current_section)

                    # Start new section
                    current_section = {"title": line, "content": ""}
                else:
                    # Add to current section content WITHOUT truncation
                    current_section["content"] += line + "\n"

        # Add the last section
        if current_section["content"]:
            sections.append(current_section)

        return sections

    def _contains_table_label(self, text: str) -> bool:
        """
        Check if text contains explicit table labels.
        Uses a regex pattern to find table labels anywhere in the text.

        Args:
            text: Text to check for table labels

        Returns:
            Boolean indicating if the text contains table labels
        """
        # Look for common table indicators like "TABLE X", "Table X", etc.
        # Using word boundary to find labels anywhere in text
        return bool(re.search(r"\b(TABLE|Table)\s+[A-Za-z0-9\-\._]+", text))

    def _is_likely_table(self, block: Dict[str, Any]) -> bool:
        """
        Determine if a block is likely to be a table based on structure.
        Uses stricter criteria to reduce false positives.

        Args:
            block: A block from PyMuPDF's layout analysis

        Returns:
            Boolean indicating if the block is likely a table
        """
        if "lines" not in block or len(block["lines"]) < 3:
            return False

        # Check for consistent number of spans across lines
        span_counts = [len(line.get("spans", [])) for line in block["lines"]]

        # Require at least 2 columns consistently across rows
        if min(span_counts) < 2:
            return False

        # Check for consistency in column count (allow some variation)
        if max(span_counts) - min(span_counts) > 1:
            return False

        # Check for consistent horizontal alignment of spans (column alignment)
        positions_per_column = {}
        for line in block["lines"]:
            for idx, span in enumerate(line.get("spans", [])):
                if idx < len(line.get("spans", [])):
                    x_pos = round(span["origin"][0], 1)
                    positions_per_column.setdefault(idx, []).append(x_pos)

        # Verify column alignment consistency
        for positions in positions_per_column.values():
            if (
                max(positions) - min(positions) > 20
            ):  # Slightly relaxed alignment tolerance
                return False

        # Check for explicit table indicators in text
        block_text = ""
        for line in block["lines"]:
            for span in line.get("spans", []):
                block_text += span.get("text", "") + " "

        if self._contains_table_label(block_text):
            return True

        # Check for grid-like structure (lines or borders)
        if "lines" in block and any("rect" in line for line in block["lines"]):
            return True

        # Must have at least 3 distinct column positions
        x_positions = []
        for line in block["lines"]:
            for span in line.get("spans", []):
                x_positions.append(span["origin"][0])

        unique_x = set(round(x, 1) for x in x_positions)
        if len(unique_x) < 3:  # Require at least 3 distinct column positions
            return False

        return True

    def _extract_table_data(
        self, block: Dict[str, Any]
    ) -> Tuple[List[List[str]], List[str], int]:
        """
        Extract structured data from a table block.

        Args:
            block: A block from PyMuPDF's layout analysis

        Returns:
            Tuple of (table_data, headers, column_count)
        """
        table_data = []
        headers = []

        # Identify potential column positions
        x_positions = []
        for line in block["lines"]:
            for span in line.get("spans", []):
                x_positions.append(span["origin"][0])

        # Group x-positions to identify column boundaries
        x_clusters = self._cluster_positions(x_positions)

        # Process rows
        for row_idx, line in enumerate(block["lines"]):
            if "spans" not in line:
                continue

            # Map spans to columns based on x-position
            row_data = [""] * len(x_clusters)
            for span in line["spans"]:
                col_idx = self._get_column_index(span["origin"][0], x_clusters)
                if col_idx >= 0:
                    row_data[col_idx] += span["text"] + " "

            # Clean up row data
            row_data = [cell.strip() for cell in row_data]

            # Skip empty rows
            if not any(cell for cell in row_data):
                continue

            # First row might be headers
            if row_idx == 0 and any(cell.isupper() for cell in row_data if cell):
                headers = row_data
            else:
                # Only add non-empty rows
                if any(cell for cell in row_data):
                    table_data.append(row_data)

        # Determine column count
        column_count = (
            len(headers)
            if headers
            else (max(len(row) for row in table_data) if table_data else 0)
        )

        return table_data, headers, column_count

    def _cluster_positions(
        self, positions: List[float], threshold: float = 10
    ) -> List[float]:
        """
        Cluster x-positions to identify column boundaries.

        Args:
            positions: List of x-positions
            threshold: Distance threshold for clustering

        Returns:
            List of average positions for each cluster
        """
        if not positions:
            return []

        # Sort positions
        sorted_pos = sorted(positions)

        # Initialize clusters
        clusters = [[sorted_pos[0]]]

        # Cluster positions
        for pos in sorted_pos[1:]:
            if pos - clusters[-1][-1] <= threshold:
                # Add to existing cluster
                clusters[-1].append(pos)
            else:
                # Start new cluster
                clusters.append([pos])

        # Get average position for each cluster
        return [sum(cluster) / len(cluster) for cluster in clusters]

    def _get_column_index(
        self, x_position: float, column_positions: List[float]
    ) -> int:
        """
        Determine which column a span belongs to based on its x-position.

        Args:
            x_position: X-position of the span
            column_positions: List of column positions

        Returns:
            Index of the column, or -1 if no match
        """
        for i, pos in enumerate(column_positions):
            if abs(x_position - pos) <= 20:  # Threshold for matching
                return i
        return -1

    def _detect_table_borders(self, page) -> List[Dict[str, Any]]:
        """
        Detect table borders in a page.

        Args:
            page: PyMuPDF page object

        Returns:
            List of dictionaries containing border information
        """
        border_info = []

        # Get the page's drawing commands which include lines and rectangles
        dl = page.get_drawings()

        # Filter for horizontal and vertical lines that might be table borders
        horizontal_lines = []
        vertical_lines = []

        for drawing in dl:
            if drawing["type"] == "l":  # Line
                # Get line coordinates
                x0, y0, x1, y1 = drawing["rect"]

                # Calculate line length and determine if horizontal or vertical
                width = abs(x1 - x0)
                height = abs(y1 - y0)

                # Lines with minimal curvature (nearly straight)
                if width > 20 and height < 2:  # Horizontal line
                    horizontal_lines.append(
                        {
                            "y": min(y0, y1),
                            "x0": min(x0, x1),
                            "x1": max(x0, x1),
                            "width": width,
                        }
                    )
                elif height > 20 and width < 2:  # Vertical line
                    vertical_lines.append(
                        {
                            "x": min(x0, x1),
                            "y0": min(y0, y1),
                            "y1": max(y0, y1),
                            "height": height,
                        }
                    )

            elif drawing["type"] == "re":  # Rectangle
                # Rectangles are often used for table cells or borders
                x0, y0, x1, y1 = drawing["rect"]

                # Add the four sides of the rectangle as lines
                # Top
                horizontal_lines.append(
                    {
                        "y": min(y0, y1),
                        "x0": min(x0, x1),
                        "x1": max(x0, x1),
                        "width": abs(x1 - x0),
                    }
                )
                # Bottom
                horizontal_lines.append(
                    {
                        "y": max(y0, y1),
                        "x0": min(x0, x1),
                        "x1": max(x0, x1),
                        "width": abs(x1 - x0),
                    }
                )
                # Left
                vertical_lines.append(
                    {
                        "x": min(x0, x1),
                        "y0": min(y0, y1),
                        "y1": max(y0, y1),
                        "height": abs(y1 - y0),
                    }
                )
                # Right
                vertical_lines.append(
                    {
                        "x": max(x0, x1),
                        "y0": min(y0, y1),
                        "y1": max(y0, y1),
                        "height": abs(y1 - y0),
                    }
                )

        # Group horizontal lines by similar y-coordinates (rows)
        y_threshold = 5  # Lines within 5 points are considered the same row
        horizontal_groups = self._group_lines_by_position(
            horizontal_lines, "y", y_threshold
        )

        # Group vertical lines by similar x-coordinates (columns)
        x_threshold = 5  # Lines within 5 points are considered the same column
        vertical_groups = self._group_lines_by_position(
            vertical_lines, "x", x_threshold
        )

        # If we have both horizontal and vertical lines forming a grid, it's likely a table
        if len(horizontal_groups) >= 3 and len(vertical_groups) >= 2:
            # Calculate table boundaries
            min_y = (
                min(group[0]["y"] for group in horizontal_groups)
                if horizontal_groups
                else 0
            )
            max_y = (
                max(group[0]["y"] for group in horizontal_groups)
                if horizontal_groups
                else 0
            )
            min_x = (
                min(group[0]["x"] for group in vertical_groups)
                if vertical_groups
                else 0
            )
            max_x = (
                max(group[0]["x"] for group in vertical_groups)
                if vertical_groups
                else 0
            )

            # Create border info
            border_info.append(
                {
                    "x0": min_x,
                    "y0": min_y,
                    "x1": max_x,
                    "y1": max_y,
                    "rows": len(horizontal_groups)
                    - 1,  # Number of rows (spaces between horizontal lines)
                    "cols": len(vertical_groups)
                    - 1,  # Number of columns (spaces between vertical lines)
                    "horizontal_lines": horizontal_groups,
                    "vertical_lines": vertical_groups,
                }
            )

        return border_info

    def _group_lines_by_position(
        self, lines: List[Dict[str, Any]], position_key: str, threshold: float
    ) -> List[List[Dict[str, Any]]]:
        """
        Group lines by their position (y for horizontal, x for vertical).

        Args:
            lines: List of line dictionaries
            position_key: Key to use for position ('x' or 'y')
            threshold: Distance threshold for grouping

        Returns:
            List of line groups
        """
        if not lines:
            return []

        # Sort lines by position
        sorted_lines = sorted(lines, key=lambda l: l[position_key])

        # Initialize groups
        groups = [[sorted_lines[0]]]

        # Group lines
        for line in sorted_lines[1:]:
            if abs(line[position_key] - groups[-1][0][position_key]) <= threshold:
                # Add to existing group
                groups[-1].append(line)
            else:
                # Start new group
                groups.append([line])

        return groups

    def _extract_labeled_tables(self, page, page_num) -> List[Dict[str, Any]]:
        """
        Extract tables that are explicitly labeled in the text.

        Args:
            page: PyMuPDF page object
            page_num: Page number

        Returns:
            List of tables extracted based on explicit labels
        """
        labeled_tables = []

        try:
            # Get page text
            text = page.get_text("text")

            # Find table labels
            table_matches = re.finditer(
                r"(TABLE\s+[A-Z0-9\-]+|Table\s+[A-Za-z0-9\-]+)", text
            )

            for match in table_matches:
                table_label = match.group(0)

                # Find the position of the table label
                label_pos = match.start()

                # Get text after the label to find the table content
                text_after_label = text[label_pos:]

                # Split into lines
                lines = text_after_label.split("\n")

                # Skip the label line
                table_lines = []
                table_start = False

                # Collect lines until we find an empty line or another table label
                for i, line in enumerate(lines):
                    if i == 0:  # This is the label line
                        continue

                    if not line.strip():
                        if table_start and len(table_lines) > 0:
                            # Empty line after table content - might be the end
                            break
                        continue

                    # Check if we've reached another table
                    if i > 1 and re.match(
                        r"(TABLE\s+[A-Z0-9\-]+|Table\s+[A-Za-z0-9\-]+)", line
                    ):
                        break

                    # Add line to table content
                    table_lines.append(line)
                    table_start = True

                # Process table lines to extract structure
                if len(table_lines) >= 2:  # Need at least header and one data row
                    # Try to identify headers and data
                    headers = []
                    data = []

                    # First line might be headers
                    header_line = table_lines[0]

                    # Split by common delimiters or multiple spaces
                    header_cells = re.split(r"\s{2,}|\t|\|", header_line)
                    header_cells = [
                        cell.strip() for cell in header_cells if cell.strip()
                    ]

                    if header_cells:
                        headers = header_cells

                    # Process data rows
                    for line in table_lines[1:]:
                        cells = re.split(r"\s{2,}|\t|\|", line)
                        cells = [cell.strip() for cell in cells if cell.strip()]

                        if cells:
                            data.append(cells)

                    # Only add if we have data
                    if data:
                        table_info = {
                            "page": page_num + 1,
                            "table_number": len(labeled_tables) + 1,
                            "table_label": table_label,
                            "headers": headers,
                            "data": data,
                            "column_count": len(headers)
                            if headers
                            else (max(len(row) for row in data) if data else 0),
                            "row_count": len(data),
                            "detection_method": "labeled_table",
                        }
                        labeled_tables.append(table_info)

                        # Enhanced logging for debugging
                        self.logger.debug(
                            f"Table found: page={page_num + 1}, method=labeled_table, "
                            f"label='{table_label}', rows={len(data)}, "
                            f"cols={table_info['column_count']}, headers={bool(headers)}"
                        )

        except Exception as e:
            self.logger.warning(f"Labeled table extraction failed: {str(e)}")

        return labeled_tables

    def _extract_tables(self, doc) -> List[Dict[str, Any]]:
        """
        Extract tables from the PDF document with improved structure detection.
        Uses a prioritized approach to reduce false positives.

        Args:
            doc: PyMuPDF document

        Returns:
            List of extracted tables with structure
        """
        tables = []

        try:
            # Use a prioritized approach to table detection
            for page_num, page in enumerate(doc):
                page_tables = []

                # STEP 1: First try to detect tables using border detection (most reliable)
                try:
                    border_info = self._detect_table_borders(page)

                    if border_info:
                        self.logger.info(
                            f"Found {len(border_info)} tables via border detection on page {page_num + 1}"
                        )

                        for table_border in border_info:
                            # Extract text within the table borders
                            table_rect = fitz.Rect(
                                table_border["x0"],
                                table_border["y0"],
                                table_border["x1"],
                                table_border["y1"],
                            )

                            # Get text within the table area
                            table_text = page.get_text("dict", clip=table_rect)

                            # Process text blocks within the table
                            table_data = []
                            headers = []

                            # Determine row boundaries from horizontal lines
                            row_boundaries = []
                            for group in table_border["horizontal_lines"]:
                                if group:  # Make sure the group is not empty
                                    row_boundaries.append(group[0]["y"])
                            row_boundaries.sort()

                            # Determine column boundaries from vertical lines
                            col_boundaries = []
                            for group in table_border["vertical_lines"]:
                                if group:  # Make sure the group is not empty
                                    col_boundaries.append(group[0]["x"])
                            col_boundaries.sort()

                            # Process text blocks and assign to cells based on position
                            for block in table_text.get("blocks", []):
                                if "lines" in block:
                                    for line in block["lines"]:
                                        if "spans" in line:
                                            for span in line["spans"]:
                                                # Find which row and column this text belongs to
                                                x, y = span["origin"]
                                                text = span["text"]

                                                # Find row index
                                                row_idx = -1
                                                for i in range(len(row_boundaries) - 1):
                                                    if (
                                                        row_boundaries[i]
                                                        <= y
                                                        < row_boundaries[i + 1]
                                                    ):
                                                        row_idx = i
                                                        break

                                                # Find column index
                                                col_idx = -1
                                                for i in range(len(col_boundaries) - 1):
                                                    if (
                                                        col_boundaries[i]
                                                        <= x
                                                        < col_boundaries[i + 1]
                                                    ):
                                                        col_idx = i
                                                        break

                                                # If we found a valid cell, add the text
                                                if row_idx >= 0 and col_idx >= 0:
                                                    # Ensure we have enough rows in table_data
                                                    while len(table_data) <= row_idx:
                                                        table_data.append(
                                                            [""]
                                                            * (len(col_boundaries) - 1)
                                                        )

                                                    # Ensure we have enough columns in this row
                                                    while (
                                                        len(table_data[row_idx])
                                                        <= col_idx
                                                    ):
                                                        table_data[row_idx].append("")

                                                    # Add text to the cell
                                                    table_data[row_idx][col_idx] += (
                                                        text + " "
                                                    )

                            # Clean up cell text
                            for row in table_data:
                                for i in range(len(row)):
                                    if i < len(row):  # Check to avoid index errors
                                        row[i] = row[i].strip()

                            # First row might be headers
                            if table_data and any(
                                cell.isupper() for cell in table_data[0] if cell
                            ):
                                headers = table_data[0]
                                table_data = table_data[1:]

                            # Only add if we have actual data
                            if table_data:
                                table_info = {
                                    "page": page_num + 1,
                                    "table_number": len(page_tables) + 1,
                                    "headers": headers,
                                    "data": table_data,
                                    "column_count": len(headers)
                                    if headers
                                    else (
                                        max(len(row) for row in table_data)
                                        if table_data
                                        else 0
                                    ),
                                    "row_count": len(table_data),
                                    "detection_method": "border_detection",
                                    "border_info": {
                                        "rows": table_border.get("rows", 0),
                                        "cols": table_border.get("cols", 0),
                                        "x0": table_border.get("x0", 0),
                                        "y0": table_border.get("y0", 0),
                                        "x1": table_border.get("x1", 0),
                                        "y1": table_border.get("y1", 0),
                                    },
                                }
                                page_tables.append(table_info)

                                # Enhanced logging for debugging
                                self.logger.debug(
                                    f"Table found: page={page_num + 1}, method=border_detection, "
                                    f"rows={len(table_data)}, cols={table_info['column_count']}, "
                                    f"headers={bool(headers)}"
                                )
                except Exception as border_error:
                    self.logger.warning(f"Border detection failed: {str(border_error)}")

                # STEP 2: Look for explicitly labeled tables if no tables found via borders
                if not page_tables:
                    try:
                        labeled_tables = self._extract_labeled_tables(page, page_num)
                        if labeled_tables:
                            self.logger.info(
                                f"Found {len(labeled_tables)} labeled tables on page {page_num + 1}"
                            )
                            page_tables.extend(labeled_tables)
                    except Exception as label_error:
                        self.logger.warning(
                            f"Labeled table extraction failed: {str(label_error)}"
                        )

                # STEP 3: Only if no tables found via borders or labels, try layout analysis with strict criteria
                if not page_tables:
                    try:
                        # Get blocks that might be tables
                        blocks = page.get_text("dict")["blocks"]

                        # Track how many potential tables we find
                        potential_tables = 0

                        # Identify potential table blocks based on multiple criteria
                        for block in blocks:
                            # Check if block has multiple lines (potential table)
                            if "lines" in block and len(block["lines"]) > 2:
                                # Additional checks for table-like structure with stricter criteria
                                is_table = self._is_likely_table(block)

                                if is_table:
                                    potential_tables += 1
                                    table_data, headers, column_count = (
                                        self._extract_table_data(block)
                                    )

                                    # Only add if we have actual data with at least 2 columns
                                    if table_data and column_count >= 2:
                                        # Add table with structure
                                        table_info = {
                                            "page": page_num + 1,
                                            "table_number": len(page_tables) + 1,
                                            "headers": headers,
                                            "data": table_data,
                                            "column_count": column_count,
                                            "row_count": len(table_data),
                                            "detection_method": "layout_analysis",
                                        }
                                        page_tables.append(table_info)

                                        # Enhanced logging for debugging
                                        self.logger.debug(
                                            f"Table found: page={page_num + 1}, method=layout_analysis, "
                                            f"rows={len(table_data)}, cols={column_count}, "
                                            f"headers={bool(headers)}"
                                        )

                        if potential_tables > 0:
                            self.logger.info(
                                f"Found {len(page_tables)} tables via layout analysis out of {potential_tables} potential tables on page {page_num + 1}"
                            )
                    except Exception as layout_error:
                        self.logger.warning(
                            f"Layout analysis failed: {str(layout_error)}"
                        )

                # STEP 4: Fallback to text-based table detection only if all other methods failed
                if not page_tables:
                    try:
                        text = page.get_text("text")

                        # Look for common table indicators
                        if any(
                            pattern in text for pattern in ["TABLE", "Table", "|", "+"]
                        ):
                            # Try to detect table structure from text
                            lines = text.split("\n")
                            table_start = -1
                            table_end = -1

                            # Find table boundaries
                            for i, line in enumerate(lines):
                                if "TABLE" in line.upper() and table_start == -1:
                                    table_start = i
                                elif table_start != -1 and not line.strip():
                                    # Empty line might indicate end of table
                                    if i > table_start + 2:  # At least 2 rows
                                        table_end = i
                                        break

                            # If we found a table
                            if table_start != -1 and table_end != -1:
                                table_lines = lines[table_start:table_end]

                                # Try to detect headers and data
                                headers = []
                                data = []

                                # First non-empty line after title might be headers
                                for i, line in enumerate(table_lines):
                                    if i > 0 and line.strip():  # Skip title
                                        # Split by common delimiters
                                        cells = re.split(r"\s{2,}|\t|\|", line)
                                        cells = [
                                            cell.strip()
                                            for cell in cells
                                            if cell.strip()
                                        ]

                                        if not headers and any(
                                            cell.isupper() for cell in cells
                                        ):
                                            headers = cells
                                        else:
                                            data.append(cells)

                                # Add table with structure
                                if (
                                    data and len(data[0]) >= 2
                                ):  # Only add if we have data with at least 2 columns
                                    table_info = {
                                        "page": page_num + 1,
                                        "table_number": len(page_tables) + 1,
                                        "headers": headers,
                                        "data": data,
                                        "column_count": len(headers)
                                        if headers
                                        else (
                                            max(len(row) for row in data) if data else 0
                                        ),
                                        "row_count": len(data),
                                        "detection_method": "text_analysis",
                                    }
                                    page_tables.append(table_info)

                                    # Enhanced logging for debugging
                                    self.logger.debug(
                                        f"Table found: page={page_num + 1}, method=text_analysis, "
                                        f"rows={len(data)}, cols={table_info['column_count']}, "
                                        f"headers={bool(headers)}"
                                    )
                    except Exception as text_error:
                        self.logger.warning(
                            f"Text-based detection failed: {str(text_error)}"
                        )

                # Add all tables from this page
                tables.extend(page_tables)

                # Log summary for this page
                if page_tables:
                    self.logger.info(
                        f"Extracted {len(page_tables)} tables from page {page_num + 1}"
                    )
                else:
                    self.logger.info(f"No tables found on page {page_num + 1}")

        except Exception as e:
            self.logger.warning(f"Error during table extraction: {str(e)}")

        # Filter out small, irrelevant tables
        filtered_tables = self._filter_tables(tables)

        if len(filtered_tables) < len(tables):
            self.logger.info(
                f"Filtered out {len(tables) - len(filtered_tables)} small or irrelevant tables"
            )

        return filtered_tables

    def _filter_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out small or irrelevant tables.

        Args:
            tables: List of extracted tables

        Returns:
            Filtered list of tables
        """
        # Keep tables that have at least 2 rows and 2 columns
        filtered = []

        # Log all tables before filtering for debugging
        for i, table in enumerate(tables):
            self.logger.info(
                f"Table {i + 1} before filtering: page={table['page']}, "
                f"method={table.get('detection_method', 'unknown')}, "
                f"rows={table.get('row_count', 0)}, cols={table.get('column_count', 0)}, "
                f"has_label={('table_label' in table)}, label={table.get('table_label', 'none')}"
            )

        for table in tables:
            # Always keep tables with explicit labels regardless of other criteria
            if table["detection_method"] == "labeled_table" and "table_label" in table:
                self.logger.info(
                    f"Keeping labeled table on page {table['page']}: {table.get('table_label', 'unknown')}"
                )
                filtered.append(table)
                continue

            # Skip tables with insufficient data
            if table["row_count"] < 2 or table["column_count"] < 2:
                self.logger.info(
                    f"Filtering out small table on page {table['page']}: {table['row_count']} rows, {table['column_count']} columns"
                )
                continue

            # Skip tables with empty data
            if not table.get("data"):
                self.logger.info(f"Filtering out empty table on page {table['page']}")
                continue

            # For other tables, ensure they have meaningful content
            has_content = False
            for row in table.get("data", []):
                # Check if any cell has substantial content (more than just a few characters)
                if any(len(cell) > 5 for cell in row if cell):
                    has_content = True
                    break

            if has_content:
                filtered.append(table)
            else:
                self.logger.info(
                    f"Filtering out table with minimal content on page {table['page']}"
                )

        return filtered
```

## File: processors/pdf_formatter.py
```python
"""
PDF formatter implementation.

This module provides functionality for formatting validated PDF data for output.
"""

from typing import Any, Dict

from utils.pipeline.strategies.base import FormatterStrategy
from utils.pipeline.utils.logging import get_logger


class PDFFormatter(FormatterStrategy):
    """Formats validated PDF data for output."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def format(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format validated PDF data for output.

        Args:
            validated_data: Validated data from the PDF validator

        Returns:
            Formatted output data
        """
        self.logger.info(
            f"Formatting output for: {validated_data.get('path', 'unknown')}"
        )

        # Create a clean output structure
        output = {
            "document": {
                "type": "pdf",
                "path": validated_data.get("path", ""),
                "metadata": self._format_metadata(validated_data.get("metadata", {})),
            },
            "content": {
                "sections": self._format_sections(validated_data.get("sections", [])),
                "tables": self._format_tables(validated_data.get("tables", [])),
            },
            "validation": validated_data.get("validation", {"is_valid": True}),
        }

        # Add summary information
        output["summary"] = self._create_summary(output)

        return output

    def _format_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format metadata section."""
        formatted_metadata = {}

        # Format standard metadata fields
        standard_fields = [
            "page_count",
            "title",
            "author",
            "subject",
            "keywords",
            "creator",
            "producer",
            "creation_date",
            "modification_date",
        ]

        for field in standard_fields:
            value = metadata.get(field)
            if value is not None:
                formatted_metadata[field] = value

        # Format any additional metadata fields
        for key, value in metadata.items():
            if key not in standard_fields and value is not None:
                formatted_metadata[key] = value

        return formatted_metadata

    def _format_sections(self, sections: list) -> list:
        """Format document sections."""
        formatted_sections = []

        for section in sections:
            if not isinstance(section, dict):
                continue

            formatted_section = {
                "title": section.get("title", "").strip(),
                "content": self._clean_content(section.get("content", "")),
            }

            # Add any additional section metadata if present
            for key, value in section.items():
                if key not in ["title", "content"] and value is not None:
                    formatted_section[key] = value

            formatted_sections.append(formatted_section)

        return formatted_sections

    def _format_tables(self, tables: list) -> list:
        """Format extracted tables."""
        formatted_tables = []

        for table in tables:
            if not isinstance(table, dict):
                continue

            formatted_table = {
                "page": table.get("page"),
                "table_number": table.get("table_number"),
                "data": table.get("data"),
            }

            # Add accuracy score if available
            accuracy = table.get("accuracy")
            if accuracy is not None:
                formatted_table["accuracy"] = accuracy

            # Add any additional table metadata if present
            for key, value in table.items():
                if (
                    key not in ["page", "table_number", "data", "accuracy"]
                    and value is not None
                ):
                    formatted_table[key] = value

            formatted_tables.append(formatted_table)

        return formatted_tables

    def _clean_content(self, content: str) -> str:
        """Clean and normalize content text."""
        if not content:
            return ""

        # Remove any trailing whitespace from lines while preserving intentional line breaks
        lines = [line.rstrip() for line in content.splitlines()]

        # Remove any empty lines at the start and end while preserving internal empty lines
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        return "\n".join(lines)

    def _create_summary(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the document content."""
        content = output["content"]
        validation = output["validation"]

        summary = {
            "title": output["document"]["metadata"].get("title", "Untitled"),
            "page_count": output["document"]["metadata"].get("page_count", 0),
            "section_count": len(content["sections"]),
            "table_count": len(content["tables"]),
            "is_valid": validation.get("is_valid", True),
            "has_errors": bool(validation.get("errors", [])),
            "has_warnings": bool(validation.get("warnings", [])),
        }

        # Add error and warning counts if present
        errors = validation.get("errors", [])
        warnings = validation.get("warnings", [])
        if errors:
            summary["error_count"] = len(errors)
        if warnings:
            summary["warning_count"] = len(warnings)

        return summary
```

## File: processors/pdf_validator.py
```python
"""
PDF validator implementation.

This module provides functionality for validating extracted PDF data.
"""

from typing import Any, Dict

from utils.pipeline.strategies.base import ValidatorStrategy
from utils.pipeline.utils.logging import get_logger


class PDFValidator(ValidatorStrategy):
    """Validates extracted PDF data."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def validate(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted PDF data.

        Args:
            extracted_data: Data extracted from the PDF

        Returns:
            Validated data with validation results
        """
        self.logger.info(
            f"Validating extracted data for: {extracted_data.get('path', 'unknown')}"
        )

        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }

        # Validate metadata
        self._validate_metadata(extracted_data, validation_results)

        # Validate sections
        self._validate_sections(extracted_data, validation_results)

        # Validate tables
        self._validate_tables(extracted_data, validation_results)

        # Update validation status
        if validation_results["errors"]:
            validation_results["is_valid"] = False

        # Return validated data
        return {
            **extracted_data,
            "validation": validation_results,
        }

    def _validate_metadata(
        self, extracted_data: Dict[str, Any], validation_results: Dict[str, Any]
    ) -> None:
        """Validate metadata section."""
        metadata = extracted_data.get("metadata", {})
        if not metadata:
            validation_results["warnings"].append("Missing or empty metadata")
            return

        # Check required metadata fields
        required_fields = ["page_count"]
        for field in required_fields:
            if field not in metadata:
                validation_results["errors"].append(
                    f"Missing required metadata: {field}"
                )

        # Check optional metadata fields
        optional_fields = ["title", "author", "subject", "keywords"]
        for field in optional_fields:
            if not metadata.get(field):
                validation_results["warnings"].append(
                    f"Missing optional metadata: {field}"
                )

    def _validate_sections(
        self, extracted_data: Dict[str, Any], validation_results: Dict[str, Any]
    ) -> None:
        """Validate sections content."""
        sections = extracted_data.get("sections", [])
        if not sections:
            validation_results["warnings"].append("No sections extracted")
            return

        for i, section in enumerate(sections):
            # Validate section structure
            if not isinstance(section, dict):
                validation_results["errors"].append(
                    f"Invalid section structure at index {i}"
                )
                continue

            # Validate section title
            if not section.get("title"):
                validation_results["errors"].append(f"Section {i + 1} missing title")

            # Validate section content
            if not section.get("content"):
                validation_results["warnings"].append(
                    f"Section '{section.get('title', f'Section {i + 1}')}' has no content"
                )

            # Check for reasonable content length
            content = section.get("content", "")
            if len(content) < 10:  # Arbitrary minimum length
                validation_results["warnings"].append(
                    f"Section '{section.get('title', f'Section {i + 1}')}' has very short content"
                )

    def _validate_tables(
        self, extracted_data: Dict[str, Any], validation_results: Dict[str, Any]
    ) -> None:
        """Validate extracted tables."""
        tables = extracted_data.get("tables", [])
        if not tables:
            validation_results["warnings"].append("No tables extracted")
            return

        for i, table in enumerate(tables):
            # Validate table structure
            if not isinstance(table, dict):
                validation_results["errors"].append(
                    f"Invalid table structure at index {i}"
                )
                continue

            # Validate required table fields
            required_fields = ["page", "table_number", "data"]
            for field in required_fields:
                if field not in table:
                    validation_results["errors"].append(
                        f"Table {i + 1} missing required field: {field}"
                    )

            # Validate table data
            data = table.get("data")
            if isinstance(data, str):
                # This is likely a fallback message when table extraction failed
                validation_results["warnings"].append(
                    f"Table {i + 1} contains placeholder data: {data}"
                )
            elif isinstance(data, list):
                if not data:
                    validation_results["warnings"].append(f"Table {i + 1} is empty")
```

## File: pyproject.toml
```toml
[project]
name = "pipeline"
version = "0.1.0"
description = "Document processing pipeline"
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
dependencies = [
    "pyyaml>=6.0.1",
    "rich>=13.7.0",
    "pypdf>=4.0.1",
    "python-docx>=1.1.0",
    "PyMuPDF>=1.23.8",  # fitz
    "camelot-py[cv]>=0.11.0",  # table extraction
    "opencv-python-headless>=4.9.0.80",  # for camelot
    "ghostscript>=0.7",  # for camelot
]
requires-python = ">=3.9"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88
target-version = "py39"

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
]
ignore = [
    "E501",  # line too long, handled by formatter
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

## File: pytest.ini
```
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: marks tests as unit tests
    integration: marks tests as integration tests
    slow: marks tests as slow (skipped by default)

addopts = --strict-markers -v

# Disable pytest-asyncio warnings
filterwarnings =
    ignore::DeprecationWarning:pytest_asyncio.*:
```

## File: rename_input_files.py
```python
"""
Script to rename input files with a QUOTE_ prefix.
"""

import shutil
from pathlib import Path


def rename_files_with_prefix(directory, prefix="QUOTE_"):
    """
    Rename all files in the directory with the given prefix.

    Args:
        directory: Directory containing files to rename
        prefix: Prefix to add to filenames
    """
    directory_path = Path(directory)

    if not directory_path.exists() or not directory_path.is_dir():
        print(f"Directory {directory} does not exist or is not a directory")
        return

    # Create a backup directory
    backup_dir = directory_path / "original_files_backup"
    backup_dir.mkdir(exist_ok=True)

    # Get all files in the directory
    files = [f for f in directory_path.iterdir() if f.is_file()]

    renamed_count = 0
    for file_path in files:
        # Skip files that already have the prefix
        if file_path.name.startswith(prefix):
            continue

        # Create backup
        backup_path = backup_dir / file_path.name
        shutil.copy2(file_path, backup_path)

        # Create new filename with prefix
        new_name = f"{prefix}{file_path.name}"
        new_path = file_path.parent / new_name

        # Rename file
        try:
            file_path.rename(new_path)
            renamed_count += 1
            print(f"Renamed: {file_path.name} -> {new_name}")
        except Exception as e:
            print(f"Error renaming {file_path.name}: {str(e)}")

    print(f"\nRenamed {renamed_count} files")
    print(f"Original files backed up to {backup_dir}")


if __name__ == "__main__":
    input_dir = Path(__file__).parent / "data" / "input"
    rename_files_with_prefix(input_dir, "QUOTE_")
```

## File: repomix.config.json
```json
{
  "output": {
    "filePath": "repomix-output.md",
    "style": "markdown",
    "parsableStyle": true,
    "fileSummary": true,
    "directoryStructure": true,
    "removeComments": false,
    "removeEmptyLines": false,
    "compress": false,
    "topFilesLength": 15,
    "showLineNumbers": false,
    "copyToClipboard": true
  },
  "include": ["**/*"],
  "ignore": {
    "useGitignore": true,
    "useDefaultPatterns": true,
    "customPatterns": [
      "uv.lock",
      "data",
      "*.md",
      "tests/**",
      "docs/**",
      "reports/**",
      "build/**",
      "dist/**",
      "node_modules/**",
      "**/node_modules/*",
      "**/bower_components/**"
    ]
  },
  "security": {
    "enableSecurityCheck": true
  },
  "tokenCount": {
    "encoding": "o200k_base"
  }
}
```

## File: requirements-dev.txt
```
# Development dependencies with specific versions to avoid compatibility issues
pytest==7.4.0
pytest-cov==4.1.0
pytest-mock==3.11.1
pytest-xdist==3.3.1
pytest-sugar==0.9.7

# Type checking
mypy==1.5.1
types-PyYAML==6.0.12.12

# Linting and formatting
ruff==0.0.292
black==23.7.0

# Documentation
sphinx==7.2.6
sphinx-rtd-theme==1.3.0

# Core dependencies
pyyaml>=6.0.1
typing-extensions>=4.7.1
```

## File: run_pipeline.py
```python
#!/usr/bin/env python3
"""
Pipeline command-line entry point.

This script provides a command-line interface for running the pipeline on input files.
It supports both single file and batch processing modes.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional

from utils.pipeline.core.file_processor import FileProcessor
from utils.pipeline.utils.logging import get_logger
from utils.pipeline.utils.progress import PipelineProgress

# Default configuration
DEFAULT_CONFIG = {
    "output_format": "json",
    "strategies": {
        "pdf": {
            "analyzer": "utils.pipeline.analyzer.pdf.PDFAnalyzer",
            "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
            "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
            "validator": "utils.pipeline.processors.pdf_validator.PDFValidator",
        },
    },
    "file_processing": {
        "input": {
            "patterns": ["*.pdf"],
            "recursive": False,
        },
        "output": {
            "formats": ["json"],
            "structure": "flat",
            "naming": {
                "template": "{original_name}",
            },
            "overwrite": True,
        },
        "reporting": {
            "summary": True,
            "detailed": True,
            "format": "json",
            "save_path": "processing_report.json",
        },
    },
}


def load_config(config_path: Optional[Path] = None) -> Dict:
    """
    Load configuration from file or use defaults.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()

    if config_path and config_path.exists():
        with open(config_path) as f:
            file_config = json.load(f)
            # Deep merge configs
            for key, value in file_config.items():
                if isinstance(value, dict) and key in config:
                    config[key].update(value)
                else:
                    config[key] = value

    return config


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process documents using the pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all PDFs in input directory
  python -m utils.pipeline.run_pipeline --input data/input --output data/output

  # Process specific file
  python -m utils.pipeline.run_pipeline --file document.pdf --output output/

  # Use custom config file
  python -m utils.pipeline.run_pipeline --input data/input --config pipeline_config.json

  # Specify output formats
  python -m utils.pipeline.run_pipeline --input data/input --formats json,markdown
  
  # Analyze schemas
  python -m utils.pipeline.run_pipeline --analyze-schemas
  
  # Compare schemas
  python -m utils.pipeline.run_pipeline --compare-schemas schema1_id schema2_id
  
  # Visualize schemas
  python -m utils.pipeline.run_pipeline --visualize-schemas clusters
""",
    )

    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "-i",
        "--input",
        type=Path,
        help="Input directory containing files to process",
    )
    input_group.add_argument("-f", "--file", type=Path, help="Single file to process")

    # Schema analysis arguments
    input_group.add_argument(
        "--analyze-schemas", action="store_true", help="Analyze existing schemas"
    )
    input_group.add_argument(
        "--compare-schemas",
        nargs=2,
        metavar=("SCHEMA1", "SCHEMA2"),
        help="Compare two schemas",
    )
    input_group.add_argument(
        "--visualize-schemas",
        choices=["clusters", "features", "structure", "tables"],
        help="Visualize schemas",
    )

    parser.add_argument("--document-type", help="Filter schemas by document type")

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output directory for processed files",
    )
    parser.add_argument("-c", "--config", type=Path, help="Path to configuration file")
    parser.add_argument(
        "--formats",
        help="Comma-separated list of output formats (e.g., json,markdown)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively process subdirectories",
    )
    parser.add_argument(
        "-p",
        "--pattern",
        help="File pattern to match (e.g., '*.pdf', defaults to all PDFs)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Path to save processing report (defaults to output_dir/processing_report.json)",
    )

    return parser.parse_args()


def update_config_from_args(config: Dict, args: argparse.Namespace) -> Dict:
    """
    Update configuration with command line arguments.

    Args:
        config: Base configuration dictionary
        args: Parsed command line arguments

    Returns:
        Updated configuration dictionary
    """
    # Update formats if specified
    if args.formats:
        formats = [fmt.strip().lower() for fmt in args.formats.split(",")]
        config["file_processing"]["output"]["formats"] = formats

    # Update input settings
    if args.pattern:
        config["file_processing"]["input"]["patterns"] = [args.pattern]
    config["file_processing"]["input"]["recursive"] = args.recursive

    # Update report path if specified
    if args.report:
        config["file_processing"]["reporting"]["save_path"] = str(args.report)

    return config


def main():
    """Main entry point for the pipeline."""
    # Add parent directory to path to allow imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    # Set up logging
    logger = get_logger(__name__)
    progress = PipelineProgress()

    try:
        # Parse arguments
        args = parse_args()

        # Handle schema analysis commands
        if args.analyze_schemas or args.compare_schemas or args.visualize_schemas:
            from utils.pipeline.schema.extended_registry import ExtendedSchemaRegistry

            registry = ExtendedSchemaRegistry()

            if args.analyze_schemas:
                progress.display_success("Analyzing schemas...")
                analysis = registry.analyze(args.document_type)

                # Display analysis results
                progress.display_success("\nSchema Analysis Results:")
                progress.display_success(
                    f"Total Schemas: {analysis.get('schema_count', 0)}"
                )

                doc_types = analysis.get("document_types", {})
                if doc_types:
                    progress.display_success("\nDocument Types:")
                    for doc_type, count in doc_types.items():
                        progress.display_success(f"  {doc_type}: {count}")

                # Display common metadata fields
                common_metadata = analysis.get("common_metadata", {})
                if common_metadata:
                    progress.display_success("\nCommon Metadata Fields:")
                    for field, frequency in sorted(
                        common_metadata.items(), key=lambda x: x[1], reverse=True
                    ):
                        progress.display_success(f"  {field}: {frequency:.2f}")

                return

            elif args.compare_schemas:
                schema_id1, schema_id2 = args.compare_schemas
                progress.display_success(
                    f"Comparing schemas: {schema_id1} vs {schema_id2}"
                )

                comparison = registry.compare(schema_id1, schema_id2)

                progress.display_success(
                    f"Overall Similarity: {comparison.get('overall_similarity', 0):.2f}"
                )
                progress.display_success(
                    f"Same Document Type: {comparison.get('same_document_type', False)}"
                )

                # Display metadata comparison
                metadata_comparison = comparison.get("metadata_comparison", {})
                if metadata_comparison:
                    progress.display_success("\nMetadata Comparison:")
                    progress.display_success(
                        f"  Similarity: {metadata_comparison.get('similarity', 0):.2f}"
                    )
                    progress.display_success(
                        f"  Common Fields: {len(metadata_comparison.get('common_fields', []))}"
                    )

                return

            elif args.visualize_schemas:
                viz_type = args.visualize_schemas
                progress.display_success(f"Generating {viz_type} visualization...")

                # Create visualizations directory
                import os

                viz_dir = os.path.join(
                    "utils", "pipeline", "schema", "data", "visualizations"
                )
                os.makedirs(viz_dir, exist_ok=True)

                viz_path = registry.visualize(viz_type, output_dir=viz_dir)
                progress.display_success(f"Visualization saved to: {viz_path}")
                return

        # Load and update configuration
        config = load_config(args.config)
        config = update_config_from_args(config, args)

        # Check if required arguments are provided for document processing
        if not args.input and not args.file:
            progress.display_error(
                "Error: Either --input or --file is required for document processing"
            )
            sys.exit(1)

        if not args.output:
            progress.display_error(
                "Error: --output is required for document processing"
            )
            sys.exit(1)

        # Create output directory
        args.output.mkdir(parents=True, exist_ok=True)

        # Initialize processor
        if args.file:
            # Single file mode
            processor = FileProcessor(args.file.parent, args.output, config)
            progress.display_success(f"Processing single file: {args.file.name}")
            data, path = processor.process_single_file(args.file)
            progress.display_success(f"Output saved to: {Path(path).name}")

        else:
            # Batch mode
            processor = FileProcessor(args.input, args.output, config)
            progress.display_success(f"Processing files from: {args.input}")
            results = processor.process_all_files()

            # Display summary
            summary = {
                f"{r['file']}": {
                    "status": r["status"],
                    "outputs": r.get("outputs", []),
                }
                for r in results
            }
            progress.display_summary(summary)

    except Exception as e:
        logger.error(f"Pipeline processing failed: {str(e)}", exc_info=True)
        progress.display_error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## File: run_tests.py
```python
#!/usr/bin/env python
"""
Script to run tests with the pytest environment.

This script:
1. Activates the virtual environment if it exists
2. Runs pytest with the specified arguments
3. Generates a coverage report
"""

import os
import subprocess
import sys
from pathlib import Path


def find_venv_python():
    """Find the Python executable in the virtual environment."""
    script_dir = Path(__file__).resolve().parent
    venv_dir = script_dir / ".venv"

    if sys.platform == "win32":
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"

    if python_exe.exists():
        return str(python_exe)

    return sys.executable


def run_tests(args=None):
    """Run tests with coverage reporting."""
    if args is None:
        args = []

    # Get the directory of this script
    script_dir = Path(__file__).resolve().parent

    # Change to the script directory
    os.chdir(script_dir)

    # Find the Python executable in the virtual environment
    python_exe = find_venv_python()

    # Build the command
    cmd = [
        python_exe,
        "-m",
        "pytest",
        "--cov=.",
        "--cov-report=term",
        "--cov-report=html:coverage_html",
    ]
    cmd.extend(args)

    print(f"Running: {' '.join(cmd)}")

    try:
        # Run the command
        result = subprocess.run(cmd, capture_output=False)

        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed.")

        print("\nCoverage report generated in coverage_html/index.html")
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def check_venv():
    """Check if the virtual environment is set up."""
    script_dir = Path(__file__).resolve().parent
    venv_dir = script_dir / ".venv"

    if not venv_dir.exists():
        print("Virtual environment not found.")
        print("Please run setup_pytest_env.py to create it:")
        print("  python setup_pytest_env.py")
        return False

    return True


def main():
    """Main entry point."""
    if not check_venv():
        return 1

    # Pass any command line arguments to pytest
    args = sys.argv[1:]
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())
```

## File: schema/__init__.py
```python
"""
Schema package for document classification.

This package provides functionality for managing document schemas.
"""
```

## File: schema/analyzer.py
```python
"""
Schema analyzer module.

This module provides functionality for analyzing and comparing document schemas.
"""

import json
from typing import Any, Dict, List, Optional

from utils.pipeline.utils.logging import get_logger


class SchemaAnalyzer:
    """
    Analyzes document schemas to extract patterns and insights.

    This class provides functionality for:
    1. Analyzing schemas to extract patterns and insights
    2. Comparing schemas to identify similarities and differences
    3. Clustering similar schemas together
    """

    def __init__(self, registry, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the schema analyzer.

        Args:
            registry: Schema registry instance
            config: Configuration dictionary for the analyzer
        """
        self.registry = registry
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Default configuration
        self.default_config = {
            "similarity_threshold": 0.7,
            "cluster_method": "hierarchical",
            "feature_weights": {"metadata": 0.3, "structure": 0.4, "tables": 0.3},
        }

        # Merge with provided config
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value

    def analyze_schemas(self, document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze schemas to extract patterns and insights.

        Args:
            document_type: Optional document type to filter by

        Returns:
            Analysis results
        """
        # Get schemas to analyze
        schemas = self.registry.list_schemas(document_type)

        if not schemas:
            return {"error": "No schemas found for analysis"}

        # Analyze document types
        doc_types = {}
        for schema in schemas:
            doc_type = schema.get("document_type", "UNKNOWN")
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

        # Analyze metadata fields
        common_metadata = self._find_common_metadata(schemas)

        # Analyze table patterns
        table_patterns = self._analyze_table_patterns(schemas)

        # Analyze section patterns
        section_patterns = self._analyze_section_patterns(schemas)

        return {
            "schema_count": len(schemas),
            "document_types": doc_types,
            "common_metadata": common_metadata,
            "table_patterns": table_patterns,
            "section_patterns": section_patterns,
        }

    def compare_schemas(self, schema_id1: str, schema_id2: str) -> Dict[str, Any]:
        """
        Compare two schemas and identify similarities and differences.

        Args:
            schema_id1: ID of first schema
            schema_id2: ID of second schema

        Returns:
            Comparison results
        """
        schema1 = self.registry.get_schema(schema_id1)
        schema2 = self.registry.get_schema(schema_id2)

        if not schema1:
            return {"error": f"Schema {schema_id1} not found"}
        if not schema2:
            return {"error": f"Schema {schema_id2} not found"}

        # Use existing matcher for comparison
        from utils.pipeline.schema.matchers import StructureMatcher

        matcher = StructureMatcher()
        similarity = matcher.match(schema1, schema2)

        # Detailed comparison
        comparison = {
            "overall_similarity": similarity,
            "same_document_type": schema1.get("document_type")
            == schema2.get("document_type"),
            "metadata_comparison": self._compare_metadata(schema1, schema2),
            "structure_comparison": self._compare_structure(schema1, schema2),
            "table_comparison": self._compare_tables(schema1, schema2),
        }

        return comparison

    def cluster_schemas(
        self, similarity_threshold: Optional[float] = None
    ) -> List[List[str]]:
        """
        Cluster schemas based on similarity.

        Args:
            similarity_threshold: Minimum similarity threshold for clustering

        Returns:
            List of clusters, where each cluster is a list of schema IDs
        """
        if similarity_threshold is None:
            similarity_threshold = self.config["similarity_threshold"]

        # Get all schemas
        schemas = self.registry.list_schemas()
        if not schemas:
            return []

        # Extract schema IDs
        schema_ids = [schema["id"] for schema in schemas]

        # Implement a simple hierarchical clustering
        clusters = []
        processed = set()

        for schema_id1 in schema_ids:
            if schema_id1 in processed:
                continue

            cluster = [schema_id1]
            processed.add(schema_id1)

            for schema_id2 in schema_ids:
                if schema_id2 in processed or schema_id1 == schema_id2:
                    continue

                comparison = self.compare_schemas(schema_id1, schema_id2)
                if (
                    "error" not in comparison
                    and comparison["overall_similarity"] >= similarity_threshold
                ):
                    cluster.append(schema_id2)
                    processed.add(schema_id2)

            clusters.append(cluster)

        return clusters

    def get_schema_summary(self, schema_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a summary of a schema or all schemas.

        Args:
            schema_id: ID of the schema to summarize, or None for all schemas

        Returns:
            Dictionary with schema summary information
        """
        if schema_id:
            schema = self.registry.get_schema(schema_id)
            if not schema:
                return {"error": f"Schema {schema_id} not found"}
            return self._summarize_schema(schema_id, schema)

        # Summarize all schemas
        summaries = {}
        for schema in self.registry.list_schemas():
            if "id" in schema:
                schema_id = schema["id"]
                summaries[schema_id] = self._summarize_schema(schema_id, schema)

        return summaries

    def export_analysis(
        self, analysis: Dict[str, Any], output_path: str, format: str = "json"
    ) -> str:
        """
        Export analysis results to file.

        Args:
            analysis: Analysis results to export
            output_path: Path to save the results
            format: Export format (json, csv)

        Returns:
            Path to the exported file
        """
        try:
            if format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(analysis, f, indent=2)
            elif format == "csv":
                # Convert to CSV format
                try:
                    import pandas as pd

                    # Convert analysis to DataFrame
                    # This is a simplified conversion - would need to be adapted for different analyses
                    if "document_types" in analysis:
                        df = pd.DataFrame(
                            list(analysis["document_types"].items()),
                            columns=["Document Type", "Count"],
                        )
                        df.to_csv(output_path, index=False)
                    else:
                        # Generic fallback
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write(
                                "Analysis results cannot be converted to CSV format\n"
                            )
                            f.write(
                                f"Please use JSON format instead: {json.dumps(analysis, indent=2)}"
                            )
                except ImportError:
                    return "Error: pandas is required for CSV export. Please install it or use JSON format."
            else:
                return f"Unsupported export format: {format}"

            return output_path
        except Exception as e:
            self.logger.error(f"Error exporting analysis: {str(e)}", exc_info=True)
            return f"Error exporting analysis: {str(e)}"

    def _find_common_metadata(self, schemas: List[Dict[str, Any]]) -> Dict[str, float]:
        """Find common metadata fields across schemas."""
        field_counts = {}

        for schema in schemas:
            metadata_fields = schema.get("metadata_fields", [])
            for field in metadata_fields:
                field_counts[field] = field_counts.get(field, 0) + 1

        # Calculate frequency (percentage of schemas with each field)
        total_schemas = len(schemas)
        return {field: count / total_schemas for field, count in field_counts.items()}

    def _analyze_table_patterns(self, schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze table patterns across schemas."""
        # Count schemas with tables
        schemas_with_tables = sum(
            1 for schema in schemas if schema.get("table_count", 0) > 0
        )

        # Calculate average tables per schema
        total_tables = sum(schema.get("table_count", 0) for schema in schemas)
        avg_tables = total_tables / len(schemas) if schemas else 0

        # Analyze table structures
        row_counts = []
        header_counts = []

        for schema in schemas:
            table_structures = schema.get("table_structure", [])
            for table in table_structures:
                row_counts.append(table.get("row_count", 0))
                header_counts.append(table.get("header_count", 0))

        return {
            "schemas_with_tables": schemas_with_tables,
            "schemas_with_tables_pct": schemas_with_tables / len(schemas)
            if schemas
            else 0,
            "avg_tables_per_schema": avg_tables,
            "avg_rows_per_table": sum(row_counts) / len(row_counts)
            if row_counts
            else 0,
            "avg_headers_per_table": sum(header_counts) / len(header_counts)
            if header_counts
            else 0,
            "tables_with_headers_pct": sum(1 for h in header_counts if h > 0)
            / len(header_counts)
            if header_counts
            else 0,
        }

    def _analyze_section_patterns(
        self, schemas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze section patterns across schemas."""
        # Count schemas with sections
        schemas_with_sections = sum(
            1 for schema in schemas if schema.get("section_count", 0) > 0
        )

        # Calculate average sections per schema
        total_sections = sum(schema.get("section_count", 0) for schema in schemas)
        avg_sections = total_sections / len(schemas) if schemas else 0

        return {
            "schemas_with_sections": schemas_with_sections,
            "schemas_with_sections_pct": schemas_with_sections / len(schemas)
            if schemas
            else 0,
            "avg_sections_per_schema": avg_sections,
        }

    def _summarize_schema(
        self, schema_id: Any, schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a summary for a single schema."""
        summary = {
            "schema_id": schema_id,
            "document_type": schema.get("document_type", "UNKNOWN"),
            "recorded_at": schema.get("recorded_at", "Unknown"),
            "metadata_fields": len(schema.get("metadata_fields", [])),
            "section_count": schema.get("section_count", 0),
            "table_count": schema.get("table_count", 0),
        }

        # Analyze table structure
        table_structure = schema.get("table_structure", [])
        if table_structure:
            summary["avg_rows_per_table"] = sum(
                t.get("row_count", 0) for t in table_structure
            ) / len(table_structure)
            summary["tables_with_headers"] = sum(
                1 for t in table_structure if t.get("has_headers", False)
            )

        # Analyze content structure
        content_structure = schema.get("content_structure", [])
        if content_structure:
            summary["max_section_depth"] = self._get_max_section_depth(
                content_structure
            )

        return summary

    def _get_max_section_depth(self, structure, current_depth=1):
        """Recursively find the maximum depth of nested sections."""
        if not structure:
            return current_depth - 1

        max_depth = current_depth
        for section in structure:
            if "children" in section and section["children"]:
                child_depth = self._get_max_section_depth(
                    section["children"], current_depth + 1
                )
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _compare_metadata(
        self, schema1: Dict[str, Any], schema2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare metadata fields between schemas."""
        fields1 = set(schema1.get("metadata_fields", []))
        fields2 = set(schema2.get("metadata_fields", []))

        common = fields1.intersection(fields2)
        only_in_1 = fields1 - fields2
        only_in_2 = fields2 - fields1

        return {
            "common_fields": list(common),
            "only_in_schema1": list(only_in_1),
            "only_in_schema2": list(only_in_2),
            "similarity": len(common) / len(fields1.union(fields2))
            if fields1 or fields2
            else 1.0,
        }

    def _compare_structure(
        self, schema1: Dict[str, Any], schema2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare content structure between schemas."""
        section_count1 = schema1.get("section_count", 0)
        section_count2 = schema2.get("section_count", 0)

        structure1 = schema1.get("content_structure", [])
        structure2 = schema2.get("content_structure", [])

        # Use a simplified structure comparison
        return {
            "section_count_1": section_count1,
            "section_count_2": section_count2,
            "section_count_diff": abs(section_count1 - section_count2),
            "similarity": min(section_count1, section_count2)
            / max(section_count1, section_count2)
            if max(section_count1, section_count2) > 0
            else 1.0,
        }

    def _compare_tables(
        self, schema1: Dict[str, Any], schema2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare table structure between schemas."""
        table_count1 = schema1.get("table_count", 0)
        table_count2 = schema2.get("table_count", 0)

        tables1 = schema1.get("table_structure", [])
        tables2 = schema2.get("table_structure", [])

        # Calculate average rows per table
        avg_rows1 = (
            sum(t.get("row_count", 0) for t in tables1) / table_count1
            if table_count1 > 0
            else 0
        )
        avg_rows2 = (
            sum(t.get("row_count", 0) for t in tables2) / table_count2
            if table_count2 > 0
            else 0
        )

        return {
            "table_count_1": table_count1,
            "table_count_2": table_count2,
            "table_count_diff": abs(table_count1 - table_count2),
            "avg_rows_1": avg_rows1,
            "avg_rows_2": avg_rows2,
            "avg_rows_diff": abs(avg_rows1 - avg_rows2),
            "count_similarity": min(table_count1, table_count2)
            / max(table_count1, table_count2)
            if max(table_count1, table_count2) > 0
            else 1.0,
        }
```

## File: schema/data/schemas/test_document_20250315153312.json
```json
{
  "id": "test_document_20250315153312",
  "document_type": "TEST_DOCUMENT",
  "document_name": "Test Document",
  "recorded_at": "2025-03-15T15:33:12.518932",
  "metadata": {
    "title": "Test Document",
    "author": "Test Author",
    "date": "2023-04-01",
    "version": "1.0",
    "keywords": "test, schema, storage, enhancement"
  },
  "content_samples": [
    {
      "title": "Section 1: Introduction",
      "content": "This is the introduction section with a detailed explanation of the document's purpose. This is the introduction section with a detailed explanation of the document's purpose. This is the introduction section with a detailed explanation of the document's purpose. This is the introduction section with a detailed explanation of the document's purpose. This is the introduction section with a detailed explanation of the document's purpose. ",
      "level": 1,
      "has_children": false,
      "child_count": 0
    },
    {
      "title": "Section 2: Methodology",
      "content": "This section describes the methodology used in the document. This section describes the methodology used in the document. This section describes the methodology used in the document. This section describes the methodology used in the document. This section describes the methodology used in the document. ",
      "level": 1,
      "has_children": true,
      "child_count": 2
    },
    {
      "title": "Section 3: Results",
      "content": "This section presents the results of the analysis. This section presents the results of the analysis. This section presents the results of the analysis. This section presents the results of the analysis. This section presents the results of the analysis. ",
      "level": 1,
      "has_children": false,
      "child_count": 0
    },
    {
      "title": "Section 4: Discussion",
      "content": "This section discusses the implications of the results. This section discusses the implications of the results. This section discusses the implications of the results. This section discusses the implications of the results. This section discusses the implications of the results. ",
      "level": 1,
      "has_children": false,
      "child_count": 0
    },
    {
      "title": "Section 5: Conclusion",
      "content": "This section concludes the document with a summary of findings. This section concludes the document with a summary of findings. This section concludes the document with a summary of findings. This section concludes the document with a summary of findings. This section concludes the document with a summary of findings. ",
      "level": 1,
      "has_children": false,
      "child_count": 0
    }
  ],
  "table_samples": [
    {
      "headers": [
        "ID",
        "Name",
        "Value",
        "Description"
      ],
      "column_count": 4,
      "row_count": 6,
      "data_sample": [
        [
          "1",
          "Item A",
          "10.5",
          "First item in the table"
        ],
        [
          "2",
          "Item B",
          "20.3",
          "Second item in the table"
        ],
        [
          "3",
          "Item C",
          "15.7",
          "Third item in the table"
        ],
        [
          "4",
          "Item D",
          "8.2",
          "Fourth item in the table"
        ],
        [
          "5",
          "Item E",
          "12.9",
          "Fifth item in the table"
        ]
      ],
      "detection_method": "border_detection",
      "page": 1,
      "border_info": {
        "x0": 50,
        "y0": 100,
        "x1": 550,
        "y1": 300,
        "rows": 6,
        "cols": 4
      }
    },
    {
      "headers": [
        "Category",
        "Subcategory",
        "Count",
        "Percentage"
      ],
      "column_count": 4,
      "row_count": 4,
      "data_sample": [
        [
          "A",
          "A1",
          "150",
          "30%"
        ],
        [
          "A",
          "A2",
          "100",
          "20%"
        ],
        [
          "B",
          "B1",
          "200",
          "40%"
        ],
        [
          "B",
          "B2",
          "50",
          "10%"
        ]
      ],
      "detection_method": "labeled_table",
      "page": 2,
      "border_info": {}
    },
    {
      "headers": [
        "Date",
        "Event",
        "Location",
        "Attendees"
      ],
      "column_count": 4,
      "row_count": 3,
      "data_sample": [
        [
          "2023-01-15",
          "Meeting A",
          "Room 101",
          "10"
        ],
        [
          "2023-02-20",
          "Meeting B",
          "Room 102",
          "15"
        ],
        [
          "2023-03-25",
          "Meeting C",
          "Room 103",
          "8"
        ]
      ],
      "detection_method": "layout_analysis",
      "page": 3,
      "border_info": {}
    }
  ],
  "section_count": 6,
  "table_count": 4,
  "document_path": "test_document.pdf"
}
```

## File: schema/extended_registry.py
```python
"""
Extended schema registry module.

This module extends the SchemaRegistry with analysis and visualization capabilities.
"""

from typing import Any, Dict, List, Optional, Union

from utils.pipeline.schema.registry import SchemaRegistry


class ExtendedSchemaRegistry(SchemaRegistry):
    """
    Extended registry for document schemas with analysis and visualization capabilities.

    This class extends SchemaRegistry with:
    1. Schema analysis functionality
    2. Schema comparison functionality
    3. Schema visualization functionality
    """

    def analyze(self, document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze schemas of the specified document type.

        Args:
            document_type: Optional document type to filter by

        Returns:
            Analysis results
        """
        from utils.pipeline.schema.analyzer import SchemaAnalyzer

        analyzer = SchemaAnalyzer(self)
        return analyzer.analyze_schemas(document_type)

    def compare(self, schema_id1: str, schema_id2: str) -> Dict[str, Any]:
        """
        Compare two schemas and identify similarities/differences.

        Args:
            schema_id1: ID of first schema
            schema_id2: ID of second schema

        Returns:
            Comparison results
        """
        from utils.pipeline.schema.analyzer import SchemaAnalyzer

        analyzer = SchemaAnalyzer(self)
        return analyzer.compare_schemas(schema_id1, schema_id2)

    def visualize(
        self,
        visualization_type: str = "clusters",
        schema_ids: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
    ) -> Union[str, List[str]]:
        """
        Generate visualizations for schemas.

        Args:
            visualization_type: Type of visualization to generate
            schema_ids: List of schema IDs to visualize, or None for all schemas
            output_dir: Directory to save visualizations, or None for default

        Returns:
            Path(s) to the generated visualization(s)
        """
        from utils.pipeline.schema.visualizer import SchemaVisualizer

        visualizer = SchemaVisualizer(self)
        return visualizer.visualize(visualization_type, schema_ids, output_dir)
```

## File: schema/matchers.py
```python
"""
Schema matchers module.

This module provides functionality for matching document schemas.
"""

from typing import Any, Dict, List, Optional

from utils.pipeline.utils.logging import get_logger


class SchemaMatcher:
    """
    Base class for schema matchers.

    Schema matchers are used to compare document schemas and determine
    if they match a known pattern.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the schema matcher.

        Args:
            config: Configuration dictionary for the matcher
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

    def match(self, schema: Dict[str, Any], known_schema: Dict[str, Any]) -> float:
        """
        Match a schema against a known schema.

        Args:
            schema: Schema to match
            known_schema: Known schema to match against

        Returns:
            Confidence score between 0.0 and 1.0
        """
        raise NotImplementedError("Subclasses must implement match()")


class StructureMatcher(SchemaMatcher):
    """
    Matches schemas based on their structure.

    This matcher compares the structure of documents, including:
    - Section hierarchy
    - Table structure
    - Metadata fields
    """

    def match(self, schema: Dict[str, Any], known_schema: Dict[str, Any]) -> float:
        """
        Match a schema against a known schema based on structure.

        Args:
            schema: Schema to match
            known_schema: Known schema to match against

        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0
        total_weight = 0.0

        # Compare metadata fields (weight: 0.2)
        weight = 0.2
        total_weight += weight

        metadata1 = set(schema.get("metadata_fields", []))
        metadata2 = set(known_schema.get("metadata_fields", []))

        if metadata1 and metadata2:
            common = len(metadata1.intersection(metadata2))
            total = len(metadata1.union(metadata2))
            score += weight * (common / total if total > 0 else 0.0)

        # Compare section counts (weight: 0.3)
        weight = 0.3
        total_weight += weight

        section_count1 = schema.get("section_count", 0)
        section_count2 = known_schema.get("section_count", 0)

        if section_count1 > 0 and section_count2 > 0:
            # Calculate similarity based on ratio
            ratio = min(section_count1, section_count2) / max(
                section_count1, section_count2
            )
            score += weight * ratio

        # Compare table counts (weight: 0.2)
        weight = 0.2
        total_weight += weight

        table_count1 = schema.get("table_count", 0)
        table_count2 = known_schema.get("table_count", 0)

        if table_count1 > 0 or table_count2 > 0:
            # Calculate similarity based on ratio
            max_count = max(table_count1, table_count2)
            min_count = min(table_count1, table_count2)
            ratio = min_count / max_count if max_count > 0 else 0.0
            score += weight * ratio
        elif table_count1 == 0 and table_count2 == 0:
            # Both have no tables, consider it a match
            score += weight

        # Compare content structure (weight: 0.3)
        weight = 0.3
        total_weight += weight

        # Compare structure recursively
        structure1 = schema.get("content_structure", [])
        structure2 = known_schema.get("content_structure", [])

        structure_sim = self._compare_structures(structure1, structure2)
        score += weight * structure_sim

        # Normalize score
        return score / total_weight if total_weight > 0 else 0.0

    def _compare_structures(
        self, structure1: List[Dict[str, Any]], structure2: List[Dict[str, Any]]
    ) -> float:
        """
        Compare two content structures recursively.

        Args:
            structure1: First structure
            structure2: Second structure

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not structure1 or not structure2:
            return 0.0 if structure1 or structure2 else 1.0  # Both empty = match

        # Compare counts
        count_sim = min(len(structure1), len(structure2)) / max(
            len(structure1), len(structure2)
        )

        # Compare levels
        levels1 = [s.get("level", 0) for s in structure1]
        levels2 = [s.get("level", 0) for s in structure2]

        avg_level1 = sum(levels1) / len(levels1) if levels1 else 0
        avg_level2 = sum(levels2) / len(levels2) if levels2 else 0

        level_diff = abs(avg_level1 - avg_level2)
        level_sim = 1.0 / (
            1.0 + level_diff
        )  # Similarity decreases as difference increases

        # Compare children
        child_sims = []
        for i in range(min(len(structure1), len(structure2))):
            s1 = structure1[i]
            s2 = structure2[i]

            # Compare basic properties
            prop_sim = 0.0
            prop_count = 0

            # Compare has_title
            if "has_title" in s1 and "has_title" in s2:
                prop_sim += 1.0 if s1["has_title"] == s2["has_title"] else 0.0
                prop_count += 1

            # Compare has_content
            if "has_content" in s1 and "has_content" in s2:
                prop_sim += 1.0 if s1["has_content"] == s2["has_content"] else 0.0
                prop_count += 1

            # Compare has_children
            if "has_children" in s1 and "has_children" in s2:
                prop_sim += 1.0 if s1["has_children"] == s2["has_children"] else 0.0
                prop_count += 1

            # Calculate property similarity
            prop_sim = prop_sim / prop_count if prop_count > 0 else 0.0

            # Compare children recursively
            children1 = s1.get("children", [])
            children2 = s2.get("children", [])

            child_sim = self._compare_structures(children1, children2)

            # Combine property and child similarity
            section_sim = 0.7 * prop_sim + 0.3 * child_sim
            child_sims.append(section_sim)

        # Calculate average child similarity
        avg_child_sim = sum(child_sims) / len(child_sims) if child_sims else 0.0

        # Combine all similarities
        return 0.4 * count_sim + 0.3 * level_sim + 0.3 * avg_child_sim


class ContentMatcher(SchemaMatcher):
    """
    Matches schemas based on their content patterns.

    This matcher compares the content patterns of documents, including:
    - Section titles
    - Content keywords
    - Table headers
    """

    def match(self, schema: Dict[str, Any], known_schema: Dict[str, Any]) -> float:
        """
        Match a schema against a known schema based on content patterns.

        Args:
            schema: Schema to match
            known_schema: Known schema to match against

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # This is a placeholder implementation
        # In a real implementation, we would extract and compare content patterns

        # For now, return a simple structural match
        structure_matcher = StructureMatcher(self.config)
        return structure_matcher.match(schema, known_schema)


class SchemaMatcherFactory:
    """Factory for creating schema matchers."""

    @staticmethod
    def create_matcher(
        matcher_type: str, config: Optional[Dict[str, Any]] = None
    ) -> SchemaMatcher:
        """
        Create a schema matcher of the specified type.

        Args:
            matcher_type: Type of matcher to create
            config: Configuration dictionary for the matcher

        Returns:
            Schema matcher instance
        """
        if matcher_type == "structure":
            return StructureMatcher(config)
        elif matcher_type == "content":
            return ContentMatcher(config)
        else:
            # Default to structure matcher
            return StructureMatcher(config)
```

## File: schema/registry.py
```python
"""
Schema registry module.

This module provides functionality for managing document schemas.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from utils.pipeline.utils.logging import get_logger


class SchemaRegistry:
    """
    Registry for document schemas.

    This class provides functionality for:
    1. Storing known document schemas
    2. Matching new documents against known schemas
    3. Recording new schemas
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the schema registry.

        Args:
            config: Configuration dictionary for the registry
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Set up registry storage
        self.storage_dir = self._get_storage_dir()
        self._ensure_storage_dir()

        # Load existing schemas
        self.schemas = self._load_schemas()

    def record(
        self,
        document_data: Dict[str, Any],
        document_type: str,
        document_name: Optional[str] = None,
    ) -> str:
        """
        Record a document schema in the registry with enhanced data storage.

        Args:
            document_data: Document data to record
            document_type: Type of the document
            document_name: Name of the document (optional)

        Returns:
            Schema ID if successful, empty string otherwise
        """
        try:
            # Generate schema ID
            schema_id = self._generate_schema_id(document_type)

            # Extract metadata
            metadata = document_data.get("metadata", {})

            # Extract content samples (up to 5 sections)
            content_samples = []
            for section in document_data.get("content", [])[:5]:
                # Store title and full content (no truncation)
                content_sample = {
                    "title": section.get("title", ""),
                    "content": section.get("content", ""),
                    "level": section.get("level", 0),
                    "has_children": bool(section.get("children")),
                    "child_count": len(section.get("children", [])),
                }
                content_samples.append(content_sample)

            # Extract table data samples (up to 3 tables)
            table_samples = []
            for table in document_data.get("tables", [])[:3]:
                # Store table structure and sample data
                table_sample = {
                    "headers": table.get("headers", []),
                    "column_count": table.get("column_count", 0),
                    "row_count": table.get("row_count", 0),
                    "data_sample": table.get("data", [])[:5],  # First 5 rows
                    "detection_method": table.get("detection_method", "unknown"),
                    "page": table.get("page", 0),
                    "border_info": table.get("border_info", {}),
                }
                table_samples.append(table_sample)

            # Create enhanced schema record
            schema = {
                "id": schema_id,
                "document_type": document_type,
                "document_name": document_name,
                "recorded_at": datetime.now().isoformat(),
                "metadata": metadata,
                "content_samples": content_samples,
                "table_samples": table_samples,
                "section_count": len(document_data.get("content", [])),
                "table_count": len(document_data.get("tables", [])),
                "document_path": document_data.get("path", ""),
            }

            # Save schema to registry
            self._save_schema(schema_id, schema)

            # Update in-memory schemas
            self.schemas[schema_id] = schema

            self.logger.info(
                f"Recorded enhanced schema {schema_id} for document type {document_type}"
            )
            return schema_id

        except Exception as e:
            self.logger.error(f"Error recording schema: {str(e)}", exc_info=True)
            return ""

    def match(self, document_data: Dict[str, Any]) -> Tuple[Optional[str], float]:
        """
        Match a document against known schemas.

        Args:
            document_data: Document data to match

        Returns:
            Tuple of (schema_id, confidence) for the best matching schema
        """
        if not self.schemas:
            return None, 0.0

        # Extract schema from document data
        schema = self._extract_schema(document_data)

        # Find best matching schema
        best_match = None
        best_confidence = 0.0

        for schema_id, known_schema in self.schemas.items():
            confidence = self._calculate_match_confidence(schema, known_schema)
            if confidence > best_confidence:
                best_match = schema_id
                best_confidence = confidence

        return best_match, best_confidence

    def get_schema(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a schema by ID.

        Args:
            schema_id: ID of the schema to get

        Returns:
            Schema dictionary or None if not found
        """
        return self.schemas.get(schema_id)

    def list_schemas(self, document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all schemas or schemas of a specific type.

        Args:
            document_type: Optional document type to filter by

        Returns:
            List of schema dictionaries
        """
        if document_type:
            return [
                {"id": schema_id, **schema}
                for schema_id, schema in self.schemas.items()
                if schema.get("document_type") == document_type
            ]

        return [
            {"id": schema_id, **schema} for schema_id, schema in self.schemas.items()
        ]

    def _get_storage_dir(self) -> Path:
        """Get the storage directory for schemas."""
        # Use configured directory if available
        if "storage_dir" in self.config:
            return Path(self.config["storage_dir"])

        # Default to package directory
        return Path(__file__).parent / "data" / "schemas"

    def _ensure_storage_dir(self) -> None:
        """Ensure the storage directory exists."""
        os.makedirs(self.storage_dir, exist_ok=True)

    def _load_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load existing schemas from storage."""
        schemas = {}

        try:
            # Load all JSON files in the storage directory
            for file_path in self.storage_dir.glob("*.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        schema = json.load(f)
                        schema_id = file_path.stem
                        schemas[schema_id] = schema
                except Exception as e:
                    self.logger.warning(f"Error loading schema {file_path}: {str(e)}")

            self.logger.info(f"Loaded {len(schemas)} schemas from storage")

        except Exception as e:
            self.logger.error(f"Error loading schemas: {str(e)}", exc_info=True)

        return schemas

    def _save_schema(self, schema_id: str, schema: Dict[str, Any]) -> None:
        """
        Save a schema to storage.

        Args:
            schema_id: ID of the schema
            schema: Schema dictionary
        """
        file_path = self.storage_dir / f"{schema_id}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

    def _extract_schema(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract enhanced schema from document data.

        Args:
            document_data: Document data to extract schema from

        Returns:
            Enhanced schema dictionary with more detailed information
        """
        # Extract metadata with values (not just field names)
        metadata = document_data.get("metadata", {})

        # Extract content structure with sample content
        content = document_data.get("content", [])
        content_structure = self._extract_content_structure(content)

        # Extract enhanced table structure with headers and sample data
        tables = document_data.get("tables", [])
        table_structure = self._extract_enhanced_table_structure(tables)

        # Build enhanced schema
        schema = {
            # Basic schema information
            "metadata_fields": list(metadata.keys()),
            "content_structure": content_structure,
            "table_structure": table_structure,
            "section_count": len(content),
            "table_count": len(tables),
            # Enhanced schema information
            "metadata_values": {
                k: str(v)[:500] for k, v in metadata.items()
            },  # Store actual values (truncated for very large values)
            # Content samples
            "content_samples": [
                {
                    "title": section.get("title", ""),
                    "content": section.get("content", ""),
                    "level": section.get("level", 0),
                    "has_children": bool(section.get("children")),
                    "child_count": len(section.get("children", [])),
                }
                for section in content[:5]  # First 5 sections
            ],
            # Document path for reference
            "document_path": document_data.get("path", ""),
        }

        return schema

    def _extract_content_structure(
        self, content: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract structure from content sections.

        Args:
            content: List of content sections

        Returns:
            List of section structures
        """
        structure = []

        for section in content:
            # Extract basic section structure
            section_structure = {
                "level": section.get("level", 0),
                "has_title": bool(section.get("title")),
                "has_content": bool(section.get("content")),
                "has_children": bool(section.get("children")),
                "child_count": len(section.get("children", [])),
            }

            # Add to structure
            structure.append(section_structure)

            # Process children recursively
            if section.get("children"):
                child_structure = self._extract_content_structure(section["children"])
                section_structure["children"] = child_structure

        return structure

    def _extract_enhanced_table_structure(
        self, tables: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract enhanced structure from tables with more detailed information.

        Args:
            tables: List of tables

        Returns:
            List of enhanced table structures with headers and sample data
        """
        structure = []

        for table in tables:
            # Extract enhanced table structure
            table_structure = {
                # Basic structure information
                "has_headers": "headers" in table and bool(table.get("headers")),
                "header_count": len(table.get("headers", [])),
                "row_count": len(table.get("data", [])),
                "column_count": table.get("column_count", 0),
                # Enhanced structure information
                "headers": table.get("headers", []),  # Store actual headers
                "data_sample": table.get("data", [])[
                    :5
                ],  # Store sample data (first 5 rows)
                "detection_method": table.get("detection_method", "unknown"),
                "page": table.get("page", 0),
                "border_info": table.get("border_info", {}),
            }

            structure.append(table_structure)

        return structure

    def _generate_schema_id(self, document_type: str) -> str:
        """
        Generate a unique schema ID.

        Args:
            document_type: Type of the document

        Returns:
            Unique schema ID
        """
        # Use timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Clean document type for use in filename
        clean_type = document_type.lower().replace(" ", "_")

        return f"{clean_type}_{timestamp}"

    def _calculate_match_confidence(
        self, schema1: Dict[str, Any], schema2: Dict[str, Any]
    ) -> float:
        """
        Calculate match confidence between two schemas.

        Args:
            schema1: First schema
            schema2: Second schema

        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0
        total_weight = 0.0

        # Compare metadata fields (weight: 0.2)
        weight = 0.2
        total_weight += weight

        metadata1 = set(schema1.get("metadata_fields", []))
        metadata2 = set(schema2.get("metadata_fields", []))

        if metadata1 and metadata2:
            common = len(metadata1.intersection(metadata2))
            total = len(metadata1.union(metadata2))
            score += weight * (common / total if total > 0 else 0.0)

        # Compare section counts (weight: 0.3)
        weight = 0.3
        total_weight += weight

        section_count1 = schema1.get("section_count", 0)
        section_count2 = schema2.get("section_count", 0)

        if section_count1 > 0 and section_count2 > 0:
            # Calculate similarity based on ratio
            ratio = min(section_count1, section_count2) / max(
                section_count1, section_count2
            )
            score += weight * ratio

        # Compare table counts (weight: 0.2)
        weight = 0.2
        total_weight += weight

        table_count1 = schema1.get("table_count", 0)
        table_count2 = schema2.get("table_count", 0)

        if table_count1 > 0 or table_count2 > 0:
            # Calculate similarity based on ratio
            max_count = max(table_count1, table_count2)
            min_count = min(table_count1, table_count2)
            ratio = min_count / max_count if max_count > 0 else 0.0
            score += weight * ratio
        elif table_count1 == 0 and table_count2 == 0:
            # Both have no tables, consider it a match
            score += weight

        # Compare content structure (weight: 0.3)
        weight = 0.3
        total_weight += weight

        # Simple structure comparison based on section levels
        structure1 = schema1.get("content_structure", [])
        structure2 = schema2.get("content_structure", [])

        if structure1 and structure2:
            # Compare level distributions
            levels1 = [s.get("level", 0) for s in structure1]
            levels2 = [s.get("level", 0) for s in structure2]

            # Calculate average level
            avg1 = sum(levels1) / len(levels1) if levels1 else 0
            avg2 = sum(levels2) / len(levels2) if levels2 else 0

            # Calculate similarity based on average level difference
            level_diff = abs(avg1 - avg2)
            level_sim = 1.0 / (
                1.0 + level_diff
            )  # Similarity decreases as difference increases

            score += weight * level_sim

        # Normalize score
        return score / total_weight if total_weight > 0 else 0.0
```

## File: schema/templates/__init__.py
```python
"""
Schema templates package.

This package contains templates for different document types.
"""
```

## File: schema/vectorizer.py
```python
"""
Schema vectorizer module.

This module provides functionality for converting document schemas to numerical vectors.
"""

from typing import Any, Dict, List, Optional

from utils.pipeline.utils.logging import get_logger


class SchemaVectorizer:
    """
    Converts document schemas to numerical feature vectors.

    This class provides functionality for:
    1. Converting schemas to numerical vectors for comparison
    2. Extracting features from schema structure and content
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the schema vectorizer.

        Args:
            config: Configuration dictionary for the vectorizer
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

    def vectorize_schema(self, schema: Dict[str, Any]) -> List[float]:
        """
        Convert a schema to a numerical feature vector.

        Args:
            schema: Schema to vectorize

        Returns:
            List representing the schema features
        """
        # Initialize feature vector components
        features = []

        # 1. Metadata features
        metadata_fields = schema.get("metadata_fields", [])
        features.append(float(len(metadata_fields)))

        # Common metadata fields (one-hot encoding)
        common_fields = [
            "title",
            "author",
            "subject",
            "creator",
            "producer",
            "creation_date",
        ]
        for field in common_fields:
            features.append(1.0 if field in metadata_fields else 0.0)

        # 2. Structure features
        features.append(float(schema.get("section_count", 0)))

        # Calculate hierarchy depth and distribution
        content_structure = schema.get("content_structure", [])
        max_depth = self._calculate_max_depth(content_structure)
        features.append(float(max_depth))

        # Level distribution (percentage of sections at each level, up to 5 levels)
        level_counts = self._count_sections_by_level(content_structure)
        total_sections = sum(level_counts.values())

        for level in range(1, 6):  # Levels 1-5
            if total_sections > 0:
                features.append(level_counts.get(level, 0) / total_sections)
            else:
                features.append(0.0)

        # 3. Table features
        table_count = schema.get("table_count", 0)
        features.append(float(table_count))

        table_structure = schema.get("table_structure", [])

        # Average rows per table
        if table_count > 0:
            avg_rows = (
                sum(table.get("row_count", 0) for table in table_structure)
                / table_count
            )
        else:
            avg_rows = 0.0
        features.append(avg_rows)

        # Average headers per table
        if table_count > 0:
            avg_headers = (
                sum(table.get("header_count", 0) for table in table_structure)
                / table_count
            )
        else:
            avg_headers = 0.0
        features.append(avg_headers)

        # Percentage of tables with headers
        if table_count > 0:
            tables_with_headers = sum(
                1 for table in table_structure if table.get("has_headers", False)
            )
            features.append(tables_with_headers / table_count)
        else:
            features.append(0.0)

        # Table size distribution (small: <5 rows, medium: 5-15 rows, large: >15 rows)
        small_tables = sum(
            1 for table in table_structure if table.get("row_count", 0) < 5
        )
        medium_tables = sum(
            1 for table in table_structure if 5 <= table.get("row_count", 0) <= 15
        )
        large_tables = sum(
            1 for table in table_structure if table.get("row_count", 0) > 15
        )

        if table_count > 0:
            features.append(small_tables / table_count)
            features.append(medium_tables / table_count)
            features.append(large_tables / table_count)
        else:
            features.append(0.0)
            features.append(0.0)
            features.append(0.0)

        return features

    def get_feature_names(self) -> List[str]:
        """
        Get names of features in the vector.

        Returns:
            List of feature names
        """
        feature_names = [
            "metadata_field_count",
        ]

        # Common metadata fields
        common_fields = [
            "title",
            "author",
            "subject",
            "creator",
            "producer",
            "creation_date",
        ]
        for field in common_fields:
            feature_names.append(f"has_{field}")

        # Structure features
        feature_names.extend(
            [
                "section_count",
                "max_depth",
            ]
        )

        # Level distribution
        for level in range(1, 6):
            feature_names.append(f"level_{level}_pct")

        # Table features
        feature_names.extend(
            [
                "table_count",
                "avg_rows_per_table",
                "avg_headers_per_table",
                "tables_with_headers_pct",
                "small_tables_pct",
                "medium_tables_pct",
                "large_tables_pct",
            ]
        )

        return feature_names

    def _calculate_max_depth(self, structure, current_depth=1):
        """Calculate maximum depth of the section hierarchy."""
        if not structure:
            return current_depth - 1

        max_depth = current_depth
        for section in structure:
            if "children" in section and section["children"]:
                child_depth = self._calculate_max_depth(
                    section["children"], current_depth + 1
                )
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _count_sections_by_level(self, structure, current_level=1, counts=None):
        """Count sections at each level of the hierarchy."""
        if counts is None:
            counts = {}

        if not structure:
            return counts

        # Count sections at this level
        counts[current_level] = counts.get(current_level, 0) + len(structure)

        # Count children
        for section in structure:
            if "children" in section and section["children"]:
                self._count_sections_by_level(
                    section["children"], current_level + 1, counts
                )

        return counts
```

## File: schema/visualizer.py
```python
"""
Schema visualizer module.

This module provides functionality for visualizing document schemas.
"""

import os
from typing import Any, Dict, List, Optional, Union

from utils.pipeline.utils.logging import get_logger


class SchemaVisualizer:
    """
    Visualizes document schemas.

    This class provides functionality for:
    1. Generating visualizations of schema patterns
    2. Creating cluster visualizations using dimensionality reduction
    3. Visualizing schema structure and features
    """

    def __init__(self, registry, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the schema visualizer.

        Args:
            registry: Schema registry instance
            config: Configuration dictionary for the visualizer
        """
        self.registry = registry
        self.config = config or {}
        self.logger = get_logger(__name__)

    def visualize(
        self,
        visualization_type: str = "clusters",
        schema_ids: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
    ) -> Union[str, List[str]]:
        """
        Generate visualizations for schemas.

        Args:
            visualization_type: Type of visualization to generate
                - "clusters": Cluster visualization using dimensionality reduction
                - "features": Feature heatmap comparison
                - "structure": Hierarchical structure visualization
                - "tables": Table pattern visualization
            schema_ids: List of schema IDs to visualize, or None for all/automatic
            output_dir: Directory to save visualizations, or None for default

        Returns:
            Path(s) to the generated visualization(s)
        """
        # Set up output directory
        if not output_dir:
            # Use a default directory relative to the schema storage directory
            try:
                from utils.pipeline.schema.registry import SchemaRegistry

                registry_instance = SchemaRegistry()
                base_dir = os.path.dirname(registry_instance.storage_dir)
                output_dir = os.path.join(base_dir, "visualizations")
            except Exception:
                # Fallback to a relative path
                output_dir = os.path.join(
                    "utils", "pipeline", "schema", "data", "visualizations"
                )

        os.makedirs(output_dir, exist_ok=True)

        # Generate visualization based on type
        try:
            if visualization_type == "clusters":
                output_path = os.path.join(output_dir, "schema_clusters.png")
                return self.visualize_schema_clusters(output_path)

            elif visualization_type == "features":
                output_path = os.path.join(output_dir, "schema_features.png")
                return self.visualize_schema_features(schema_ids, output_path)

            elif visualization_type == "structure":
                if not schema_ids or len(schema_ids) == 0:
                    # Use first schema if none specified
                    schemas = self.registry.list_schemas()
                    if not schemas:
                        return "No schemas available for visualization"
                    schema_ids = [schemas[0]["id"]]

                # Generate structure visualization for each schema
                output_paths = []
                for schema_id in schema_ids:
                    output_path = os.path.join(output_dir, f"structure_{schema_id}.png")
                    result = self.visualize_schema_structure(schema_id, output_path)
                    output_paths.append(result)

                return output_paths

            elif visualization_type == "tables":
                if not schema_ids or len(schema_ids) == 0:
                    # Use first schema if none specified
                    schemas = self.registry.list_schemas()
                    if not schemas:
                        return "No schemas available for visualization"
                    schema_ids = [schemas[0]["id"]]

                # Generate table visualization for each schema
                output_paths = []
                for schema_id in schema_ids:
                    output_path = os.path.join(output_dir, f"tables_{schema_id}.png")
                    result = self.visualize_table_patterns(schema_id, output_path)
                    output_paths.append(result)

                return output_paths

            else:
                return f"Unknown visualization type: {visualization_type}"
        except ImportError as e:
            return f"Error: Missing dependency - {str(e)}"
        except Exception as e:
            self.logger.error(
                f"Error generating visualization: {str(e)}", exc_info=True
            )
            return f"Error generating visualization: {str(e)}"

    def visualize_schema_clusters(self, output_path: str) -> str:
        """
        Visualize schema clusters using dimensionality reduction.

        Args:
            output_path: Path to save the visualization

        Returns:
            Path to the saved visualization
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            # Check if we have scikit-learn for dimensionality reduction
            try:
                from sklearn.manifold import TSNE
            except ImportError:
                return "Error: scikit-learn is required for cluster visualization. Please install it with 'pip install scikit-learn'."

            # Get all schemas
            schemas = self.registry.list_schemas()
            if len(schemas) < 2:
                return "Not enough schemas for cluster visualization (need at least 2)"

            # Extract schema IDs and document types
            schema_ids = [
                schema.get("id", f"schema_{i}") for i, schema in enumerate(schemas)
            ]
            doc_types = [schema.get("document_type", "UNKNOWN") for schema in schemas]

            # Vectorize schemas
            from utils.pipeline.schema.vectorizer import SchemaVectorizer

            vectorizer = SchemaVectorizer()
            vectors = [vectorizer.vectorize_schema(schema) for schema in schemas]

            # Convert to numpy array
            vectors = np.array(vectors)

            # Apply t-SNE for dimensionality reduction
            # Use a lower perplexity value (default is 30) that's less than n_samples
            perplexity = min(5, len(vectors) - 1)  # Ensure perplexity < n_samples
            tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
            vectors_2d = tsne.fit_transform(vectors)

            # Create plot
            plt.figure(figsize=(12, 8))

            # Get unique document types for coloring
            unique_types = list(set(doc_types))
            # Create colors for each document type
            color_indices = np.linspace(0, 1, len(unique_types))

            # Plot each schema with different colors by document type

            # Plot each schema
            for i, (x, y) in enumerate(vectors_2d):
                doc_type = doc_types[i]
                color_idx = unique_types.index(doc_type)
                # Use a basic color cycle with simple colors
                colors = [
                    "red",
                    "blue",
                    "green",
                    "orange",
                    "purple",
                    "cyan",
                    "magenta",
                    "yellow",
                ]
                color = colors[color_idx % len(colors)]
                plt.scatter(x, y, color=color, s=100, alpha=0.7)
                plt.text(x, y, schema_ids[i], fontsize=9)

            # Define colors for legend
            colors = [
                "red",
                "blue",
                "green",
                "orange",
                "purple",
                "cyan",
                "magenta",
                "yellow",
            ]
            for i, doc_type in enumerate(unique_types):
                plt.scatter([], [], color=colors[i % len(colors)], label=doc_type)
            plt.legend()

            plt.title("Schema Similarity Map")
            plt.xlabel("Dimension 1")
            plt.ylabel("Dimension 2")
            plt.tight_layout()

            # Save figure
            plt.savefig(output_path, dpi=300)
            plt.close()

            return output_path
        except Exception as e:
            self.logger.error(
                f"Error visualizing schema clusters: {str(e)}", exc_info=True
            )
            return f"Error visualizing schema clusters: {str(e)}"

    def visualize_schema_features(
        self,
        schema_ids: Optional[List[str]] = None,
        output_path: str = "schema_features.png",
    ) -> str:
        """
        Visualize schema features as a heatmap.

        Args:
            schema_ids: List of schema IDs to visualize, or None for all schemas
            output_path: Path to save the visualization

        Returns:
            Path to the saved visualization
        """
        try:
            import matplotlib.pyplot as plt

            # Check if we have seaborn for heatmap
            try:
                import seaborn as sns
            except ImportError:
                return "Error: seaborn is required for feature visualization. Please install it with 'pip install seaborn'."

            # Get schemas to visualize
            if schema_ids:
                schemas = [
                    self.registry.get_schema(schema_id) for schema_id in schema_ids
                ]
                schemas = [s for s in schemas if s]  # Filter out None values
            else:
                schemas = self.registry.list_schemas()

            if not schemas:
                return "No schemas found for visualization"

            # Define features to extract
            features = [
                ("Metadata Fields", lambda s: len(s.get("metadata_fields", []))),
                ("Section Count", lambda s: s.get("section_count", 0)),
                ("Table Count", lambda s: s.get("table_count", 0)),
                (
                    "Avg Rows/Table",
                    lambda s: sum(
                        t.get("row_count", 0) for t in s.get("table_structure", [])
                    )
                    / max(1, s.get("table_count", 0)),
                ),
                (
                    "Max Depth",
                    lambda s: self._calculate_max_depth(s.get("content_structure", [])),
                ),
                (
                    "Tables with Headers",
                    lambda s: sum(
                        1
                        for t in s.get("table_structure", [])
                        if t.get("has_headers", False)
                    ),
                ),
            ]

            # Extract feature values
            feature_names = [f[0] for f in features]
            data = []

            for schema in schemas:
                schema_id = schema.get("id", "unknown")
                row = [schema_id]
                for _, feature_func in features:
                    row.append(feature_func(schema))
                data.append(row)

            # Create DataFrame
            try:
                import pandas as pd

                df = pd.DataFrame(data, columns=["Schema ID"] + feature_names)
                df = df.set_index("Schema ID")

                # Normalize data for heatmap
                df_norm = (df - df.min()) / (df.max() - df.min())

                # Create plot
                plt.figure(figsize=(12, max(8, len(schemas) * 0.4)))
                sns.heatmap(
                    df_norm,
                    annot=df.round(1),
                    fmt=".1f",
                    cmap="YlGnBu",
                    linewidths=0.5,
                    cbar_kws={"label": "Normalized Value"},
                )

                plt.title("Schema Feature Comparison")
                plt.tight_layout()

                # Save figure
                plt.savefig(output_path, dpi=300, bbox_inches="tight")
                plt.close()

                return output_path
            except ImportError:
                return "Error: pandas is required for feature visualization. Please install it with 'pip install pandas'."
        except Exception as e:
            self.logger.error(
                f"Error visualizing schema features: {str(e)}", exc_info=True
            )
            return f"Error visualizing schema features: {str(e)}"

    def visualize_schema_structure(self, schema_id: str, output_path: str) -> str:
        """
        Visualize the hierarchical structure of a schema.

        Args:
            schema_id: ID of the schema to visualize
            output_path: Path to save the visualization

        Returns:
            Path to the saved visualization
        """
        try:
            import matplotlib.pyplot as plt

            # Check if we have networkx for graph visualization
            try:
                import networkx as nx
            except ImportError:
                return "Error: networkx is required for structure visualization. Please install it with 'pip install networkx'."

            schema = self.registry.get_schema(schema_id)
            if not schema:
                return f"Schema {schema_id} not found"

            # Create directed graph
            G = nx.DiGraph()

            # Add root node
            root_name = f"{schema_id}\n({schema.get('document_type', 'UNKNOWN')})"
            G.add_node(root_name)

            # Add metadata node
            metadata_fields = schema.get("metadata_fields", [])
            if metadata_fields:
                metadata_name = f"Metadata\n({len(metadata_fields)} fields)"
                G.add_node(metadata_name)
                G.add_edge(root_name, metadata_name)

            # Add content structure
            content_structure = schema.get("content_structure", [])
            if content_structure:
                self._add_structure_to_graph(G, root_name, content_structure, "Section")

            # Add tables
            table_structure = schema.get("table_structure", [])
            if table_structure:
                tables_name = f"Tables\n({len(table_structure)} tables)"
                G.add_node(tables_name)
                G.add_edge(root_name, tables_name)

                # Add individual tables (limit to first 10 to avoid overcrowding)
                for i, table in enumerate(table_structure[:10]):
                    table_name = f"Table {i + 1}\n({table.get('row_count', 0)} rows)"
                    G.add_node(table_name)
                    G.add_edge(tables_name, table_name)

                # Add ellipsis if more tables
                if len(table_structure) > 10:
                    G.add_node("...")
                    G.add_edge(tables_name, "...")

            # Create plot
            plt.figure(figsize=(12, 8))

            # Check if we have pygraphviz for better layout
            try:
                pos = nx.drawing.nx_agraph.graphviz_layout(G, prog="dot")
            except (ImportError, Exception):
                # Fall back to spring layout
                pos = nx.spring_layout(G, seed=42)

            # Draw nodes and edges
            nx.draw(
                G,
                pos,
                with_labels=True,
                node_size=3000,
                node_color="lightblue",
                font_size=10,
                font_weight="bold",
                arrows=True,
            )

            plt.title(f"Schema Structure: {schema_id}")
            plt.tight_layout()

            # Save figure
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()

            return output_path
        except Exception as e:
            self.logger.error(
                f"Error visualizing schema structure: {str(e)}", exc_info=True
            )
            return f"Error visualizing schema structure: {str(e)}"

    def visualize_table_patterns(
        self, schema_id: str, output_path: str
    ) -> Union[str, List[str]]:
        """
        Visualize table patterns in a schema with enhanced information.

        Args:
            schema_id: ID of the schema to visualize
            output_path: Path to save the visualization

        Returns:
            Path(s) to the saved visualization(s)
        """
        try:
            from collections import Counter

            import matplotlib.pyplot as plt
            import numpy as np

            schema = self.registry.get_schema(schema_id)
            if not schema:
                return f"Schema {schema_id} not found"

            # Check if we have the enhanced schema structure with table_samples
            table_samples = schema.get("table_samples", [])
            if table_samples:
                # Use enhanced table samples
                tables_to_visualize = table_samples
                self.logger.info(f"Using enhanced table samples for schema {schema_id}")
            else:
                # Fall back to old structure
                table_structure = schema.get("table_structure", [])
                if not table_structure:
                    return f"No tables found in schema {schema_id}"
                tables_to_visualize = table_structure
                self.logger.info(f"Using legacy table structure for schema {schema_id}")

            if not tables_to_visualize:
                return f"No tables found in schema {schema_id}"

            # Extract row counts
            row_counts = [table.get("row_count", 0) for table in tables_to_visualize]

            # Create base directory for visualizations
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)

            # List to store all output paths
            output_paths = [output_path]

            # Create histogram
            plt.figure(figsize=(12, 6))

            # Plot histogram of row counts
            plt.subplot(1, 2, 1)
            plt.hist(row_counts, bins=10, color="skyblue", edgecolor="black")
            plt.title("Distribution of Table Sizes")
            plt.xlabel("Rows per Table")
            plt.ylabel("Number of Tables")

            # Plot table size categories
            plt.subplot(1, 2, 2)
            categories = ["Small (<5 rows)", "Medium (5-15 rows)", "Large (>15 rows)"]
            counts = [
                sum(1 for rc in row_counts if rc < 5),
                sum(1 for rc in row_counts if 5 <= rc <= 15),
                sum(1 for rc in row_counts if rc > 15),
            ]

            plt.bar(categories, counts, color=["lightblue", "skyblue", "steelblue"])
            plt.title("Table Size Categories")
            plt.ylabel("Number of Tables")
            plt.xticks(rotation=45, ha="right")

            plt.suptitle(f"Table Patterns in Schema: {schema_id}")
            plt.tight_layout()

            # Save figure
            plt.savefig(output_path, dpi=300)
            plt.close()

            # Create additional visualizations if enhanced data is available

            # 1. Table Headers Visualization
            if any(
                "headers" in table and table["headers"] for table in tables_to_visualize
            ):
                # Collect all headers
                all_headers = []
                for table in tables_to_visualize:
                    if "headers" in table and table["headers"]:
                        all_headers.extend(table["headers"])

                if all_headers:
                    # Count header frequency
                    header_counts = Counter(all_headers)

                    # Plot top 15 headers (or fewer if less available)
                    top_headers = header_counts.most_common(min(15, len(header_counts)))

                    plt.figure(figsize=(14, 8))
                    plt.bar(
                        [h[0] for h in top_headers],
                        [h[1] for h in top_headers],
                        color="skyblue",
                    )
                    plt.title(f"Common Table Headers in Schema: {schema_id}")
                    plt.xticks(rotation=45, ha="right")
                    plt.tight_layout()

                    # Save additional visualization
                    headers_path = os.path.join(output_dir, f"headers_{schema_id}.png")
                    plt.savefig(headers_path, dpi=300)
                    plt.close()
                    output_paths.append(headers_path)

            # 2. Column Count Visualization
            column_counts = [
                table.get("column_count", 0)
                for table in tables_to_visualize
                if "column_count" in table
            ]
            if column_counts:
                plt.figure(figsize=(10, 6))
                plt.hist(
                    column_counts,
                    bins=max(5, min(10, max(column_counts))),
                    color="lightgreen",
                    edgecolor="black",
                )
                plt.title(f"Distribution of Table Column Counts in Schema: {schema_id}")
                plt.xlabel("Columns per Table")
                plt.ylabel("Number of Tables")
                plt.tight_layout()

                # Save additional visualization
                columns_path = os.path.join(output_dir, f"columns_{schema_id}.png")
                plt.savefig(columns_path, dpi=300)
                plt.close()
                output_paths.append(columns_path)

            # 3. Detection Method Visualization
            detection_methods = [
                table.get("detection_method", "unknown")
                for table in tables_to_visualize
                if "detection_method" in table
            ]
            if detection_methods:
                # Count detection methods
                method_counts = Counter(detection_methods)

                plt.figure(figsize=(10, 6))
                plt.bar(
                    list(method_counts.keys()),
                    list(method_counts.values()),
                    color="lightcoral",
                )
                plt.title(f"Table Detection Methods in Schema: {schema_id}")
                plt.xlabel("Detection Method")
                plt.ylabel("Number of Tables")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()

                # Save additional visualization
                methods_path = os.path.join(output_dir, f"methods_{schema_id}.png")
                plt.savefig(methods_path, dpi=300)
                plt.close()
                output_paths.append(methods_path)

            # 4. Table Data Sample Visualization (if available)
            tables_with_samples = [
                table
                for table in tables_to_visualize
                if ("data_sample" in table and table["data_sample"])
                or ("data" in table and table["data"])
            ]
            if tables_with_samples:
                # Create sample table visualizations (up to 3 tables)
                for i, sample_table in enumerate(tables_with_samples[:3]):
                    headers = sample_table.get("headers", [])
                    # Check both data_sample and data fields
                    data_sample = sample_table.get(
                        "data_sample", sample_table.get("data", [])
                    )

                    if data_sample:
                        plt.figure(figsize=(14, 8))

                        # Create a table visualization
                        table_data = data_sample[
                            : min(5, len(data_sample))
                        ]  # Limit to 5 rows

                        # If we have headers, add them as the first row
                        if headers:
                            table_data = [headers] + table_data

                        # Create the table
                        table = plt.table(
                            cellText=table_data,
                            loc="center",
                            cellLoc="center",
                            colWidths=[0.2] * len(table_data[0])
                            if table_data and table_data[0]
                            else None,
                        )

                        # Style the table
                        table.auto_set_font_size(False)
                        table.set_fontsize(9)
                        table.scale(1, 1.5)

                        # Hide axes
                        plt.axis("off")

                        # Add table metadata
                        detection_method = sample_table.get(
                            "detection_method", "unknown"
                        )
                        page = sample_table.get("page", "unknown")
                        row_count = sample_table.get("row_count", 0)
                        column_count = sample_table.get("column_count", 0)

                        plt.title(
                            f"Table {i + 1} from Schema: {schema_id}\n"
                            f"Method: {detection_method}, Page: {page}, "
                            f"Rows: {row_count}, Columns: {column_count}"
                        )
                        plt.tight_layout()

                        # Save additional visualization
                        sample_path = os.path.join(
                            output_dir, f"sample_{i + 1}_{schema_id}.png"
                        )
                        plt.savefig(sample_path, dpi=300, bbox_inches="tight")
                        plt.close()
                        output_paths.append(sample_path)

            # 5. Border Information Visualization (if available)
            tables_with_borders = [
                table
                for table in tables_to_visualize
                if "border_info" in table and table["border_info"]
            ]
            if tables_with_borders:
                # Create border visualization for the first table with border info
                border_table = tables_with_borders[0]
                border_info = border_table.get("border_info", {})

                if border_info:
                    plt.figure(figsize=(10, 8))

                    # Extract border coordinates
                    x0 = border_info.get("x0", 0)
                    y0 = border_info.get("y0", 0)
                    x1 = border_info.get("x1", 100)
                    y1 = border_info.get("y1", 100)
                    rows = border_info.get("rows", 0)
                    cols = border_info.get("cols", 0)

                    # Create a simple visualization of the table grid
                    # Draw outer border
                    plt.plot(
                        [x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], "k-", linewidth=2
                    )

                    # Draw row lines (if we have row information)
                    if rows > 0:
                        row_positions = np.linspace(y0, y1, rows + 1)
                        for y in row_positions:
                            plt.plot([x0, x1], [y, y], "k-", linewidth=1)

                    # Draw column lines (if we have column information)
                    if cols > 0:
                        col_positions = np.linspace(x0, x1, cols + 1)
                        for x in col_positions:
                            plt.plot([x, x], [y0, y1], "k-", linewidth=1)

                    plt.title(
                        f"Table Border Structure (Page {border_table.get('page', 'unknown')})"
                    )
                    plt.xlabel("X Position")
                    plt.ylabel("Y Position")
                    plt.grid(True, linestyle="--", alpha=0.7)
                    plt.tight_layout()

                    # Save additional visualization
                    border_path = os.path.join(output_dir, f"border_{schema_id}.png")
                    plt.savefig(border_path, dpi=300)
                    plt.close()
                    output_paths.append(border_path)

            return output_paths
        except Exception as e:
            self.logger.error(
                f"Error visualizing table patterns: {str(e)}", exc_info=True
            )
            return f"Error visualizing table patterns: {str(e)}"

    def _add_structure_to_graph(self, G, parent_name, structure, prefix, level=1):
        """Add hierarchical structure to graph recursively."""
        for i, section in enumerate(structure):
            has_title = section.get("has_title", False)
            has_content = section.get("has_content", False)
            has_children = section.get("has_children", False)

            # Create node name
            node_name = f"{prefix} {level}.{i + 1}"
            if has_title:
                node_name += "\n(with title)"
            if has_content:
                node_name += "\n(with content)"

            G.add_node(node_name)
            G.add_edge(parent_name, node_name)

            # Add children recursively
            if has_children and "children" in section:
                self._add_structure_to_graph(
                    G, node_name, section["children"], prefix, level + 1
                )

    def _calculate_max_depth(self, structure, current_depth=1):
        """Calculate maximum depth of the section hierarchy."""
        if not structure:
            return current_depth - 1

        max_depth = current_depth
        for section in structure:
            if "children" in section and section["children"]:
                child_depth = self._calculate_max_depth(
                    section["children"], current_depth + 1
                )
                max_depth = max(max_depth, child_depth)

        return max_depth
```

## File: setup_pytest_env.py
```python
#!/usr/bin/env python
"""
Script to set up a proper pytest environment for the pipeline project.

This script:
1. Creates a virtual environment if it doesn't exist
2. Installs the required dependencies
3. Installs the pipeline package in development mode
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return its output."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        print(result.stdout)
        return True
    except Exception as e:
        print(f"Error executing command: {e}")
        return False


def setup_env():
    """Set up the pytest environment."""
    # Get the directory of this script
    script_dir = Path(__file__).resolve().parent

    # Change to the script directory
    os.chdir(script_dir)

    # Check if virtual environment exists
    venv_dir = script_dir / ".venv"
    if not venv_dir.exists():
        print("Creating virtual environment...")
        if not run_command([sys.executable, "-m", "venv", str(venv_dir)]):
            return False

    # Determine the pip executable
    if sys.platform == "win32":
        pip_exe = venv_dir / "Scripts" / "pip"
    else:
        pip_exe = venv_dir / "bin" / "pip"

    # Upgrade pip
    print("Upgrading pip...")
    if not run_command([str(pip_exe), "install", "--upgrade", "pip"]):
        return False

    # Install pytest and related packages
    print("Installing pytest and related packages...")
    if not run_command([str(pip_exe), "install", "-r", "requirements-dev.txt"]):
        return False

    # Install the pipeline package in development mode
    print("Installing pipeline package in development mode...")
    if not run_command([str(pip_exe), "install", "-e", "."]):
        return False

    # Print success message
    print("\nPytest environment set up successfully!")
    print("\nTo activate the virtual environment:")
    if sys.platform == "win32":
        print(f"  {venv_dir}\\Scripts\\activate")
    else:
        print(f"  source {venv_dir}/bin/activate")

    print("\nTo run the tests:")
    print("  pytest")
    print("  pytest -v")
    print("  pytest --cov=.")

    return True


if __name__ == "__main__":
    if not setup_env():
        sys.exit(1)
```

## File: strategies/__init__.py
```python
"""
Strategy pattern implementations for document processing.
"""
```

## File: strategies/base.py
```python
"""
Base strategy interfaces for document processing.

This module defines the abstract base classes for the strategy pattern
used in the document processing pipeline.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class AnalyzerStrategy(ABC):
    """Base interface for document analyzer strategies."""

    @abstractmethod
    def analyze(self, input_path: str) -> Dict[str, Any]:
        """
        Analyze document structure and extract metadata.

        Args:
            input_path: Path to the document

        Returns:
            Dictionary with document structure and metadata
        """
        pass


class CleanerStrategy(ABC):
    """Base interface for document cleaner strategies."""

    @abstractmethod
    def clean(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize document content.

        Args:
            analysis_result: Result from the document analyzer

        Returns:
            Cleaned data dictionary
        """
        pass


class ExtractorStrategy(ABC):
    """Base interface for document extractor strategies."""

    @abstractmethod
    def extract(self, cleaned_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from cleaned content.

        Args:
            cleaned_data: Cleaned data from the document cleaner

        Returns:
            Extracted structured data
        """
        pass


class ValidatorStrategy(ABC):
    """Base interface for document validator strategies."""

    @abstractmethod
    def validate(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted document data.

        Args:
            extracted_data: Data extracted from the document

        Returns:
            Validated data with validation results
        """
        pass


class FormatterStrategy(ABC):
    """Base interface for document formatter strategies."""

    @abstractmethod
    def format(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format validated document data for output.

        Args:
            validated_data: Validated data from the document validator

        Returns:
            Formatted output data
        """
        pass
```

## File: strategies/formatter.py
```python
"""
Base formatter strategy.

This module provides the base strategy interface for formatters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class FormatterStrategy(ABC):
    """Base strategy for formatters."""

    @abstractmethod
    def format(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the analyzed data into a specific output structure.

        Args:
            analyzed_data: Data to format

        Returns:
            Formatted data structure
        """
        pass

    @abstractmethod
    def write(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Write formatted data to a file.

        Args:
            data: Formatted data to write
            output_path: Path to output file
        """
        pass
```

## File: utils/logging.py
```python
"""
Centralized logging configuration for the pipeline.

This module provides a consistent logging setup across all pipeline components.
"""

import logging
from pathlib import Path
from typing import Optional, Union

# Default log format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Default log level
DEFAULT_LEVEL = logging.INFO


def setup_logger(
    name: str,
    level: Optional[Union[str, int]] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Set up a logger with consistent formatting and optional file output.

    Args:
        name: Name of the logger (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string
        log_file: Path to log file (if file logging is desired)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Enable propagation to parent loggers
    logger.propagate = True

    # If this is a pipeline logger, inherit level from root pipeline logger
    if name.startswith("pipeline."):
        root_logger = logging.getLogger("pipeline")
        logger.setLevel(root_logger.level)
    else:
        # Set log level (default to INFO if not specified or invalid)
        if isinstance(level, str):
            level = getattr(logging, level.upper(), DEFAULT_LEVEL)
        logger.setLevel(level or DEFAULT_LEVEL)

    # Create formatter
    formatter = logging.Formatter(log_format or DEFAULT_FORMAT)

    # Always add console handler if none exists
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with default configuration.

    This is a convenience function for getting a logger with default settings.
    For custom configuration, use setup_logger directly.

    Args:
        name: Name of the logger (usually __name__)

    Returns:
        Configured logger instance
    """
    return setup_logger(name)


def set_log_level(level: Union[str, int]) -> None:
    """
    Set the log level for all pipeline loggers.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), DEFAULT_LEVEL)

    # Get the root pipeline logger
    root_logger = logging.getLogger("pipeline")
    root_logger.setLevel(level)

    # Update all child loggers
    for name, logger in logging.root.manager.loggerDict.items():
        if isinstance(logger, logging.Logger) and name.startswith("pipeline"):
            logger.setLevel(level)
            # Ensure child loggers inherit from parent
            logger.propagate = True


def enable_debug_logging() -> None:
    """Enable debug logging for all pipeline components."""
    set_log_level(logging.DEBUG)


def disable_logging() -> None:
    """Disable logging for all pipeline components."""
    set_log_level(logging.CRITICAL)
```

## File: utils/progress.py
```python
"""
Progress tracking utilities using Rich.

This module provides rich terminal output for pipeline progress.
"""

from typing import Any, Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.tree import Tree

console = Console()


class PipelineProgress:
    """Rich progress tracking for pipeline operations."""

    def __init__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=True,  # Hide completed tasks
            expand=True,
        )

    def __enter__(self):
        self.progress.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.__exit__(exc_type, exc_val, exc_tb)

    def start(self):
        """Start progress tracking."""
        self.progress.start()

    def stop(self):
        """Stop progress tracking."""
        self.progress.stop()

    def add_task(self, description: str, total: Optional[float] = None) -> TaskID:
        """Add a new task to track."""
        return self.progress.add_task(description, total=total)

    def update(self, task_id: TaskID, advance: float = 1):
        """Update task progress."""
        self.progress.update(task_id, advance=advance)

    def _create_tree_view(self, data: Dict[str, Any], title: str) -> Tree:
        """Create a tree view of nested data."""
        tree = Tree(f"[bold blue]{title}")

        def add_nodes(parent, content, depth=0, max_depth=2):
            if depth >= max_depth:
                return

            if isinstance(content, dict):
                for key, value in content.items():
                    # Skip content display
                    if key == "content":
                        parent.add(f"[cyan]{key}: [dim](content hidden)")
                        continue

                    if isinstance(value, (dict, list)):
                        branch = parent.add(f"[cyan]{key}")
                        add_nodes(branch, value, depth + 1, max_depth)
                    else:
                        # Truncate long values
                        str_value = str(value)
                        if len(str_value) > 30:
                            str_value = str_value[:27] + "..."
                        parent.add(f"[green]{key}: [yellow]{str_value}")
            elif isinstance(content, list):
                if not content:
                    parent.add("[dim]<empty>")
                else:
                    parent.add(f"[dim]{len(content)} items")

        add_nodes(tree, data)
        return tree

    def _update_display(self, content: Any) -> None:
        """Update display with new content."""
        console.print(content)

    def display_stage_output(
        self, stage_name: str, data: Dict[str, Any], show_details: bool = False
    ):
        """Display stage output in a concise tree view."""
        if show_details:
            self._update_display(
                Panel(
                    self._create_tree_view(data, stage_name),
                    title=f"[bold]{stage_name} Output",
                    border_style="blue",
                )
            )

    def display_summary(self, stages_data: Dict[str, Dict[str, Any]]):
        """Display final summary of all stages."""
        summary_tree = Tree("[bold blue]Pipeline Summary")
        for stage, data in stages_data.items():
            stage_branch = summary_tree.add(f"[cyan]{stage}")
            if isinstance(data, dict):
                # Show key statistics or counts
                stats = {
                    k: v
                    for k, v in data.items()
                    if isinstance(v, (int, float, str))
                    or (isinstance(v, (list, dict)) and len(v) > 0)
                }
                for key, value in stats.items():
                    if isinstance(value, (list, dict)):
                        stage_branch.add(f"[green]{key}: [yellow]{len(value)} items")
                    else:
                        stage_branch.add(f"[green]{key}: [yellow]{value}")

        self._update_display(
            Panel(
                summary_tree,
                title="[bold]Pipeline Execution Summary",
                border_style="green",
            )
        )

    def display_error(self, message: str):
        """Display error message."""
        self._update_display(
            Panel(f"[red]{message}", title="Error", border_style="red")
        )

    def display_warning(self, message: str):
        """Display warning message."""
        self._update_display(
            Panel(f"[yellow]{message}", title="Warning", border_style="yellow")
        )

    def display_success(self, message: str):
        """Display success message."""
        self._update_display(
            Panel(f"[green]{message}", title="Success", border_style="green")
        )
```

## File: verify/base.py
```python
"""
Base verifier module.

This module provides the base verifier interface for output verification.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from utils.pipeline.utils.logging import get_logger


class BaseVerifier(ABC):
    """Base class for output verifiers."""

    def __init__(self):
        self.logger = get_logger(__name__)

    @abstractmethod
    def verify(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Verify output data structure and content.

        Args:
            data: Output data to verify

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        pass
```

## File: verify/factory.py
```python
"""
Verifier factory implementation.

This module provides a factory for creating different output verifiers.
"""

from enum import Enum, auto
from typing import Dict, Type

from utils.pipeline.utils.logging import get_logger
from utils.pipeline.verify.base import BaseVerifier
from utils.pipeline.verify.json_tree import JSONTreeVerifier
from utils.pipeline.verify.markdown import MarkdownVerifier


class VerifierType(Enum):
    """Supported verifier types."""

    JSON_TREE = auto()
    MARKDOWN = auto()  # Future implementation


class VerifierFactory:
    """Factory for creating verifier instances."""

    _verifiers: Dict[VerifierType, Type[BaseVerifier]] = {
        VerifierType.JSON_TREE: JSONTreeVerifier,
        VerifierType.MARKDOWN: MarkdownVerifier,
    }

    @classmethod
    def create_verifier(cls, verifier_type: VerifierType) -> BaseVerifier:
        """
        Create a verifier instance for the specified type.

        Args:
            verifier_type: Type of verifier to create

        Returns:
            Verifier instance

        Raises:
            ValueError: If verifier type is not supported
        """
        logger = get_logger(__name__)

        try:
            verifier_class = cls._verifiers[verifier_type]
            return verifier_class()
        except KeyError:
            logger.error(f"Unsupported verifier type: {verifier_type}")
            raise ValueError(f"Unsupported verifier type: {verifier_type}")

    @classmethod
    def register_verifier(
        cls, verifier_type: VerifierType, verifier_class: Type[BaseVerifier]
    ) -> None:
        """
        Register a new verifier type.

        Args:
            verifier_type: Verifier type to register
            verifier_class: Verifier class to use for this type
        """
        logger = get_logger(__name__)
        logger.info(
            f"Registering verifier for {verifier_type}: {verifier_class.__name__}"
        )
        cls._verifiers[verifier_type] = verifier_class
```

## File: verify/json_tree.py
```python
"""
JSON tree structure verifier.

This module provides verification for JSON tree structure output.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from utils.pipeline.verify.base import BaseVerifier


class JSONTreeVerifier(BaseVerifier):
    """Verifies JSON tree structure output."""

    def verify(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Verify JSON tree structure and content.

        Args:
            data: JSON data to verify

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        try:
            # Verify required top-level keys
            required_keys = {"document", "content", "validation"}
            self._verify_required_keys(data, required_keys, "root", errors)

            # Verify document metadata
            if "document" in data:
                self._verify_document_metadata(data["document"], errors, warnings)

            # Verify content structure
            if "content" in data:
                self._verify_content_structure(data["content"], errors, warnings)

            # Check for circular references
            if "content" in data:
                self._check_circular_references(data["content"], errors)

            is_valid = len(errors) == 0
            return is_valid, errors, warnings

        except Exception as e:
            errors.append(f"Verification failed: {str(e)}")
            return False, errors, warnings

    def _verify_required_keys(
        self,
        data: Dict[str, Any],
        required_keys: Set[str],
        context: str,
        errors: List[str],
    ) -> None:
        """Verify all required keys are present."""
        missing_keys = required_keys - set(data.keys())
        if missing_keys:
            errors.append(
                f"Missing required keys in {context}: {', '.join(missing_keys)}"
            )

    def _verify_document_metadata(
        self, document: Dict[str, Any], errors: List[str], warnings: List[str]
    ) -> None:
        """Verify document metadata structure."""
        required_metadata = {"metadata", "path", "type"}
        self._verify_required_keys(document, required_metadata, "document", errors)

        metadata = document.get("metadata", {})
        if not isinstance(metadata, dict):
            errors.append("Document metadata must be a dictionary")

    def _verify_content_structure(
        self,
        content: List[Dict[str, Any]],
        errors: List[str],
        warnings: List[str],
        parent_level: Optional[int] = None,
    ) -> None:
        """Verify content structure recursively."""
        if not isinstance(content, list):
            errors.append("Content must be a list of sections")
            return

        for section in content:
            if not isinstance(section, dict):
                errors.append("Each section must be a dictionary")
                continue

            # Check required section keys
            required_keys = {"title", "content", "children", "level"}
            self._verify_required_keys(section, required_keys, "section", errors)

            # Verify level is valid
            level = section.get("level")
            if not isinstance(level, int) or level < 0:
                errors.append(
                    f"Invalid level {level} for section '{section.get('title')}'"
                )
                continue

            # Verify level is consistent with parent
            if parent_level is not None and isinstance(level, int):
                if level <= parent_level:
                    warnings.append(
                        f"Section '{section.get('title')}' level {level} is not greater than parent level {parent_level}"
                    )

            # Verify children recursively
            children = section.get("children", [])
            if children:
                self._verify_content_structure(children, errors, warnings, level)

    def _check_circular_references(
        self,
        content: List[Dict[str, Any]],
        errors: List[str],
        visited: Optional[Set[int]] = None,
    ) -> None:
        """Check for circular references in content structure."""
        if visited is None:
            visited = set()

        for section in content:
            section_id = id(section)
            if section_id in visited:
                errors.append(
                    f"Circular reference detected in section '{section.get('title')}'"
                )
                continue

            visited.add(section_id)
            children = section.get("children", [])
            if children:
                self._check_circular_references(children, errors, visited)
            visited.remove(section_id)
```

## File: verify/markdown.py
```python
"""
Markdown structure verifier.

This module provides verification for Markdown structure output.
"""

from typing import Any, Dict, List, Tuple

from utils.pipeline.verify.base import BaseVerifier


class MarkdownVerifier(BaseVerifier):
    """Verifies Markdown structure output."""

    def verify(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Verify Markdown structure and content.

        Args:
            data: Markdown data to verify

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        try:
            # Verify required top-level keys
            required_keys = {"document", "content", "validation"}
            self._verify_required_keys(data, required_keys, errors)

            # Verify document metadata
            if "document" in data:
                self._verify_document_metadata(data["document"], errors)

            # Verify content is a string
            if "content" in data:
                self._verify_content(data["content"], errors, warnings)

            # Verify tables format if present
            if "tables" in data:
                self._verify_tables(data["tables"], errors, warnings)

            is_valid = len(errors) == 0
            return is_valid, errors, warnings

        except Exception as e:
            errors.append(f"Verification failed: {str(e)}")
            return False, errors, warnings

    def _verify_required_keys(
        self, data: Dict[str, Any], required_keys: set, errors: List[str]
    ) -> None:
        """Verify all required keys are present."""
        missing_keys = required_keys - set(data.keys())
        if missing_keys:
            errors.append(f"Missing required keys: {', '.join(missing_keys)}")

    def _verify_document_metadata(
        self, document: Dict[str, Any], errors: List[str]
    ) -> None:
        """Verify document metadata structure."""
        required_metadata = {"metadata", "path", "type"}
        self._verify_required_keys(document, required_metadata, errors)

        metadata = document.get("metadata", {})
        if not isinstance(metadata, dict):
            errors.append("Document metadata must be a dictionary")

    def _verify_content(
        self, content: str, errors: List[str], warnings: List[str]
    ) -> None:
        """Verify markdown content structure."""
        if not isinstance(content, str):
            errors.append("Content must be a string")
            return

        # Check for basic markdown structure
        if not content.strip():
            warnings.append("Content is empty")
            return

        # Check for header hierarchy
        lines = content.split("\n")
        current_level = 0
        for line in lines:
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                if level > current_level + 1:
                    warnings.append(
                        f"Header level jump from {current_level} to {level}: {line.strip()}"
                    )
                current_level = level

    def _verify_tables(
        self, tables: str, errors: List[str], warnings: List[str]
    ) -> None:
        """Verify markdown tables structure."""
        if not isinstance(tables, str):
            errors.append("Tables must be a string")
            return

        if not tables.strip():
            return

        lines = tables.split("\n")
        in_table = False
        header_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                in_table = False
                continue

            if line.startswith("|"):
                if not in_table:
                    # New table started
                    in_table = True
                    header_count = line.count("|") - 1
                else:
                    # Check consistent column count
                    if line.count("|") - 1 != header_count:
                        errors.append(f"Inconsistent table column count: {line}")
```

## File: visualize_schema.py
```python
#!/usr/bin/env python3
"""
Script to visualize a specific schema.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.pipeline.schema.extended_registry import ExtendedSchemaRegistry
from utils.pipeline.utils.progress import PipelineProgress


def main():
    """Main entry point for schema visualization."""
    progress = PipelineProgress()

    # Check arguments
    if len(sys.argv) < 2:
        print_usage()
        return

    # Parse command
    command = sys.argv[1]

    if command == "list":
        # List available schemas
        list_schemas(progress)
        return
    elif command == "help":
        print_usage()
        return
    elif command in ["clusters", "features", "structure", "tables"]:
        # Visualization command
        visualization_type = command

        # Check if schema ID is provided
        if len(sys.argv) < 3 and visualization_type not in ["clusters", "features"]:
            print(
                f"Error: Schema ID is required for {visualization_type} visualization"
            )
            print_usage()
            return

        # Get schema ID (optional for clusters and features)
        schema_id = sys.argv[2] if len(sys.argv) >= 3 else "all"

        # Generate visualization
        generate_visualization(visualization_type, schema_id, progress)
    else:
        print(f"Unknown command: {command}")
        print_usage()


def print_usage():
    """Print usage information."""
    print("Usage:")
    print(
        "  python visualize_schema.py list                     - List available schemas"
    )
    print(
        "  python visualize_schema.py clusters [schema_id]     - Generate cluster visualization"
    )
    print(
        "  python visualize_schema.py features [schema_id]     - Generate feature visualization"
    )
    print(
        "  python visualize_schema.py structure <schema_id>    - Generate structure visualization"
    )
    print(
        "  python visualize_schema.py tables <schema_id>       - Generate table visualization"
    )
    print(
        "  python visualize_schema.py help                     - Show this help message"
    )


def list_schemas(progress):
    """List available schemas."""
    # Initialize registry
    registry = ExtendedSchemaRegistry()

    # Get all schemas
    schemas = registry.list_schemas()

    if not schemas:
        progress.display_error("No schemas found in registry")
        return

    # Display schemas
    progress.display_success(f"Found {len(schemas)} schemas:")

    # Group schemas by document type
    schemas_by_type = {}
    for schema in schemas:
        doc_type = schema.get("document_type", "UNKNOWN")
        if doc_type not in schemas_by_type:
            schemas_by_type[doc_type] = []
        schemas_by_type[doc_type].append(schema)

    # Display schemas by type
    for doc_type, type_schemas in schemas_by_type.items():
        progress.display_success(f"\n{doc_type} ({len(type_schemas)}):")
        for schema in type_schemas:
            schema_id = schema.get("id")
            recorded_at = schema.get("recorded_at", "Unknown")
            document_name = schema.get("document_name", "")
            progress.display_success(f"  - {schema_id} ({recorded_at}) {document_name}")


def generate_visualization(visualization_type, schema_id, progress):
    """Generate visualization for schema."""
    # Create visualizations directory
    viz_dir = os.path.join("utils", "pipeline", "schema", "data", "visualizations")
    os.makedirs(viz_dir, exist_ok=True)

    # Initialize registry
    registry = ExtendedSchemaRegistry()

    # Prepare schema IDs
    schema_ids = None
    if schema_id != "all":
        schema_ids = [schema_id]

    # Generate visualization
    progress.display_success(
        f"Generating {visualization_type} visualization for schema {schema_id}..."
    )
    viz_path = registry.visualize(visualization_type, schema_ids, viz_dir)

    # Handle multiple visualization paths
    if isinstance(viz_path, list):
        progress.display_success(f"Generated {len(viz_path)} visualizations:")
        for path in viz_path:
            progress.display_success(f"  - {path}")
    else:
        progress.display_success(f"Visualization saved to: {viz_path}")


if __name__ == "__main__":
    main()
```
