"""Example demonstrating enhanced configuration validation features."""

import os
from pathlib import Path

from utils.pipeline.config.config import (
    ComponentConfig,
    DocumentTypeRule,
    PipelineConfig,
    ValidationLevel,
    load_config,
)

def main():
    """Run configuration validation examples."""
    print("\n=== Configuration Validation Examples ===\n")

    # Example 1: Basic Valid Configuration
    print("1. Creating a valid configuration...")
    try:
        config = PipelineConfig(
            input_dir="data/input",
            output_dir="data/output",
            output_format="yaml",
            validation_level=ValidationLevel.BASIC,
            strategies={
                "pdf": {
                    "analyzer": "utils.pipeline.analyzer.pdf.PDFAnalyzer",
                    "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
                    "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    "validator": "utils.pipeline.processors.pdf_validator.PDFValidator",
                    "formatter": "utils.pipeline.formatters.pdf.PDFFormatter",
                }
            }
        )
        print("✓ Valid configuration created successfully")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

    # Example 2: Invalid Strategy Path
    print("\n2. Testing invalid strategy path validation...")
    try:
        config = PipelineConfig(
            strategies={
                "pdf": {
                    "analyzer": "nonexistent.module.Analyzer",
                    "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
                    "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    "validator": "utils.pipeline.processors.pdf_validator.PDFValidator",
                    "formatter": "utils.pipeline.formatters.pdf.PDFFormatter",
                }
            }
        )
        print("✗ Should have raised an error")
    except ValueError as e:
        print(f"✓ Caught expected error: {str(e)}")

    # Example 3: Invalid Weight Distribution
    print("\n3. Testing weight validation...")
    try:
        rule = DocumentTypeRule(
            title_keywords=["test"],
            content_keywords=["test"],
            patterns=["test"],
            weights={
                "title_match": 0.5,
                "content_match": 0.6,  # Total > 1.0
                "pattern_match": 0.3,
            }
        )
        print("✗ Should have raised an error")
    except ValueError as e:
        print(f"✓ Caught expected error: {str(e)}")

    # Example 4: Strict Validation Level with Low Threshold
    print("\n4. Testing strict validation level constraints...")
    try:
        config = PipelineConfig(
            validation_level=ValidationLevel.STRICT,
            classification={
                "rules": {
                    "TEST": DocumentTypeRule(
                        title_keywords=["test"],
                        content_keywords=["test"],
                        patterns=["test"],
                        threshold=0.3  # Too low for STRICT mode
                    )
                }
            }
        )
        print("✗ Should have raised an error")
    except ValueError as e:
        print(f"✓ Caught expected error: {str(e)}")

    # Example 5: Invalid Schema Pattern
    print("\n5. Testing schema pattern validation...")
    try:
        config = PipelineConfig(
            classification={
                "rules": {
                    "TEST": DocumentTypeRule(
                        title_keywords=["test"],
                        content_keywords=["test"],
                        patterns=["test"],
                        schema_pattern="nonexistent_pattern"
                    )
                }
            }
        )
        print("✗ Should have raised an error")
    except ValueError as e:
        print(f"✓ Caught expected error: {str(e)}")

    # Example 6: Loading from YAML
    print("\n6. Testing configuration loading from YAML...")
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
                "formatter": "utils.pipeline.formatters.pdf.PDFFormatter"
            }
        }
    }

    # Create example config file
    config_path = Path("utils/pipeline/examples/example_config.yaml")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    import yaml
    with open(config_path, "w") as f:
        yaml.dump(example_config, f)

    try:
        config = load_config(str(config_path))
        print("✓ Successfully loaded configuration from YAML")
    except Exception as e:
        print(f"✗ Error loading configuration: {str(e)}")
    finally:
        # Clean up example file
        os.remove(config_path)

if __name__ == "__main__":
    main()
