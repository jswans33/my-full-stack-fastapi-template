"""Tests for configuration validation examples."""

import os
import sys
from io import StringIO
from pathlib import Path

import pytest
import yaml

from utils.pipeline.config.config import (
    ComponentConfig,
    DocumentTypeRule,
    PipelineConfig,
    ValidationLevel,
    load_config,
    StrategyConfig,
    ClassificationConfig,
)
from utils.pipeline.examples.config_validation_example import main


def test_valid_configuration():
    """Test Example 1: Creating a valid configuration."""
    config = PipelineConfig(
        input_dir="data/input",
        output_dir="data/output",
        output_format="yaml",
        validation_level=ValidationLevel.BASIC,
        strategies=StrategyConfig(
            pdf=ComponentConfig(
                analyzer="utils.pipeline.analyzer.pdf.PDFAnalyzer",
                cleaner="utils.pipeline.cleaner.pdf.PDFCleaner",
                extractor="utils.pipeline.processors.pdf_extractor.PDFExtractor",
                validator="utils.pipeline.processors.pdf_validator.PDFValidator",
                formatter="utils.pipeline.processors.pdf_formatter.PDFFormatter",
            ),
            excel=ComponentConfig(
                analyzer="utils.pipeline.analyzer.pdf.PDFAnalyzer",
                cleaner="utils.pipeline.cleaner.pdf.PDFCleaner",
                extractor="utils.pipeline.processors.pdf_extractor.PDFExtractor",
                validator="utils.pipeline.processors.pdf_validator.PDFValidator",
                formatter="utils.pipeline.processors.pdf_formatter.PDFFormatter",
            ),
            word=ComponentConfig(
                analyzer="utils.pipeline.analyzer.pdf.PDFAnalyzer",
                cleaner="utils.pipeline.cleaner.pdf.PDFCleaner",
                extractor="utils.pipeline.processors.pdf_extractor.PDFExtractor",
                validator="utils.pipeline.processors.pdf_validator.PDFValidator",
                formatter="utils.pipeline.processors.pdf_formatter.PDFFormatter",
            ),
            text=ComponentConfig(
                analyzer="utils.pipeline.analyzer.pdf.PDFAnalyzer",
                cleaner="utils.pipeline.cleaner.pdf.PDFCleaner",
                extractor="utils.pipeline.processors.pdf_extractor.PDFExtractor",
                validator="utils.pipeline.processors.pdf_validator.PDFValidator",
                formatter="utils.pipeline.processors.pdf_formatter.PDFFormatter",
            )
        )
    )
    assert config is not None
    assert config.input_dir == "data/input"
    assert config.output_format == "yaml"
    assert config.validation_level == ValidationLevel.BASIC


def test_invalid_strategy_path():
    """Test Example 2: Invalid strategy path validation."""
    with pytest.raises(ValueError) as exc_info:
        PipelineConfig(
            strategies=StrategyConfig(
                pdf=ComponentConfig(
                    analyzer="nonexistent.module.Analyzer",
                    cleaner="utils.pipeline.cleaner.pdf.PDFCleaner",
                    extractor="utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    validator="utils.pipeline.processors.pdf_validator.PDFValidator",
                    formatter="utils.pipeline.processors.pdf_formatter.PDFFormatter",
                )
            )
        )
    assert "Module not found" in str(exc_info.value)


def test_invalid_weight_distribution():
    """Test Example 3: Invalid weight distribution."""
    with pytest.raises(ValueError) as exc_info:
        DocumentTypeRule(
            title_keywords=["test"],
            content_keywords=["test"],
            patterns=["test"],
            weights={
                "title_match": 0.5,
                "content_match": 0.6,  # Total > 1.0
                "pattern_match": 0.3,
            }
        )
    assert "Weights must sum to 1.0" in str(exc_info.value)


def test_strict_validation_level_with_low_threshold():
    """Test Example 4: Strict validation level with low threshold."""
    with pytest.raises(ValueError) as exc_info:
        PipelineConfig(
            validation_level=ValidationLevel.STRICT,
            strategies=StrategyConfig(
                pdf=ComponentConfig(
                    analyzer="utils.pipeline.analyzer.pdf.PDFAnalyzer",
                    cleaner="utils.pipeline.cleaner.pdf.PDFCleaner",
                    extractor="utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    validator="utils.pipeline.processors.pdf_validator.PDFValidator",
                    formatter="utils.pipeline.processors.pdf_formatter.PDFFormatter",
                ),
                excel=ComponentConfig(
                    analyzer="utils.pipeline.analyzer.pdf.PDFAnalyzer",
                    cleaner="utils.pipeline.cleaner.pdf.PDFCleaner",
                    extractor="utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    validator="utils.pipeline.processors.pdf_validator.PDFValidator",
                    formatter="utils.pipeline.processors.pdf_formatter.PDFFormatter",
                ),
                word=ComponentConfig(
                    analyzer="utils.pipeline.analyzer.pdf.PDFAnalyzer",
                    cleaner="utils.pipeline.cleaner.pdf.PDFCleaner",
                    extractor="utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    validator="utils.pipeline.processors.pdf_validator.PDFValidator",
                    formatter="utils.pipeline.processors.pdf_formatter.PDFFormatter",
                ),
                text=ComponentConfig(
                    analyzer="utils.pipeline.analyzer.pdf.PDFAnalyzer",
                    cleaner="utils.pipeline.cleaner.pdf.PDFCleaner",
                    extractor="utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    validator="utils.pipeline.processors.pdf_validator.PDFValidator",
                    formatter="utils.pipeline.processors.pdf_formatter.PDFFormatter",
                )
            ),
            classification=ClassificationConfig(
                rules={
                    "TEST": DocumentTypeRule(
                        title_keywords=["test"],
                        content_keywords=["test"],
                        patterns=["test"],
                        threshold=0.3  # Too low for STRICT mode
                    )
                }
            )
        )
    assert "threshold" in str(exc_info.value) and "too low" in str(exc_info.value)


def test_invalid_schema_pattern():
    """Test Example 5: Invalid schema pattern."""
    with pytest.raises(ValueError) as exc_info:
        PipelineConfig(
            strategies=StrategyConfig(
                pdf=ComponentConfig(
                    analyzer="utils.pipeline.analyzer.pdf.PDFAnalyzer",
                    cleaner="utils.pipeline.cleaner.pdf.PDFCleaner",
                    extractor="utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    validator="utils.pipeline.processors.pdf_validator.PDFValidator",
                    formatter="utils.pipeline.processors.pdf_formatter.PDFFormatter",
                ),
                excel=ComponentConfig(
                    analyzer="utils.pipeline.analyzer.pdf.PDFAnalyzer",
                    cleaner="utils.pipeline.cleaner.pdf.PDFCleaner",
                    extractor="utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    validator="utils.pipeline.processors.pdf_validator.PDFValidator",
                    formatter="utils.pipeline.processors.pdf_formatter.PDFFormatter",
                ),
                word=ComponentConfig(
                    analyzer="utils.pipeline.analyzer.pdf.PDFAnalyzer",
                    cleaner="utils.pipeline.cleaner.pdf.PDFCleaner",
                    extractor="utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    validator="utils.pipeline.processors.pdf_validator.PDFValidator",
                    formatter="utils.pipeline.processors.pdf_formatter.PDFFormatter",
                ),
                text=ComponentConfig(
                    analyzer="utils.pipeline.analyzer.pdf.PDFAnalyzer",
                    cleaner="utils.pipeline.cleaner.pdf.PDFCleaner",
                    extractor="utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    validator="utils.pipeline.processors.pdf_validator.PDFValidator",
                    formatter="utils.pipeline.processors.pdf_formatter.PDFFormatter",
                )
            ),
            classification=ClassificationConfig(
                rules={
                    "TEST": DocumentTypeRule(
                        title_keywords=["test"],
                        content_keywords=["test"],
                        patterns=["test"],
                        schema_pattern="nonexistent_pattern"
                    )
                }
            )
        )
    assert "Invalid schema_pattern" in str(exc_info.value)


def test_loading_from_yaml(tmp_path):
    """Test Example 6: Loading configuration from YAML."""
    # Create test config file
    example_config = {
        "input_dir": "data/input",
        "output_dir": "data/output",
        "output_format": "yaml",
        "validation_level": "basic",
        "strategies": {
            "pdf": {
                "analyzer": "utils.pipeline.analyzer.pdf.PDFAnalyzer",
                "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
                "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
                "validator": "utils.pipeline.processors.pdf_validator.PDFValidator",
                "formatter": "utils.pipeline.processors.pdf_formatter.PDFFormatter"
            },
            "excel": {
                "analyzer": "utils.pipeline.analyzer.pdf.PDFAnalyzer",
                "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
                "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
                "validator": "utils.pipeline.processors.pdf_validator.PDFValidator",
                "formatter": "utils.pipeline.processors.pdf_formatter.PDFFormatter"
            },
            "word": {
                "analyzer": "utils.pipeline.analyzer.pdf.PDFAnalyzer",
                "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
                "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
                "validator": "utils.pipeline.processors.pdf_validator.PDFValidator",
                "formatter": "utils.pipeline.processors.pdf_formatter.PDFFormatter"
            },
            "text": {
                "analyzer": "utils.pipeline.analyzer.pdf.PDFAnalyzer",
                "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
                "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
                "validator": "utils.pipeline.processors.pdf_validator.PDFValidator",
                "formatter": "utils.pipeline.processors.pdf_formatter.PDFFormatter"
            }
        }
    }
    
    config_path = tmp_path / "test_example_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(example_config, f)
    
    # Test loading the config
    config = load_config(str(config_path))
    assert config is not None
    assert config.input_dir == "data/input"
    assert config.validation_level == ValidationLevel.BASIC
    assert "pdf" in config.strategies.model_dump()


def test_main_function(monkeypatch, tmpdir):
    """Test the main function execution with console output capture."""
    # Mock sys.stdout to capture print statements
    captured_output = StringIO()
    monkeypatch.setattr(sys, "stdout", captured_output)
    
    # Create a temporary directory for the example config file
    monkeypatch.chdir(tmpdir)
    
    # Ensure the utils/pipeline/examples directory exists in the temporary directory
    examples_dir = tmpdir.join("utils", "pipeline", "examples")
    os.makedirs(examples_dir, exist_ok=True)
    
    # Run the main function
    main()
    
    # Check if output contains expected messages
    output = captured_output.getvalue()
    
    # Check Example 1 output
    assert "1. Creating a valid configuration..." in output
    assert "✓ Valid configuration created successfully" in output
    
    # Check Example 2 output
    assert "2. Testing invalid strategy path validation..." in output
    assert "✓ Caught expected error:" in output
    
    # Check Example 3 output
    assert "3. Testing weight validation..." in output
    assert "✓ Caught expected error:" in output
    
    # Check Example 4 output
    assert "4. Testing strict validation level constraints..." in output
    assert "✓ Caught expected error:" in output
    
    # Check Example 5 output
    assert "5. Testing schema pattern validation..." in output
    assert "✓ Caught expected error:" in output
    
    # Check Example 6 output
    assert "6. Testing configuration loading from YAML..." in output
    assert "✓ Successfully loaded configuration from YAML" in output
