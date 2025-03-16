# Pipeline Usage Guide

This document provides instructions for using the document processing pipeline.

## Overview

The pipeline processes documents through several stages:
1. **Analysis**: Extract raw content and metadata from documents
2. **Cleaning**: Clean and normalize the extracted content
3. **Extraction**: Extract structured data from the cleaned content
4. **Classification**: Classify the document based on its content
5. **Schema Recording**: Record the document schema for future reference

## Installation

### Prerequisites

- Python 3.8 or higher
- Required packages:
  ```bash
  pip install -r requirements.txt
  ```

### Optional Dependencies

For PDF processing:
```bash
pip install pymupdf
```

For Excel processing:
```bash
pip install openpyxl
```

For Word processing:
```bash
pip install python-docx
```

## Basic Usage

### Command-Line Interface

Process a single file:
```bash
python -m utils.pipeline.run_pipeline --file path/to/document.pdf --output path/to/output
```

Process all files in a directory:
```bash
python -m utils.pipeline.run_pipeline --input path/to/input_dir --output path/to/output_dir
```

### Output Formats

Specify output formats:
```bash
python -m utils.pipeline.run_pipeline --input path/to/input_dir --output path/to/output_dir --formats json,markdown
```

### Recursive Processing

Process files in subdirectories:
```bash
python -m utils.pipeline.run_pipeline --input path/to/input_dir --output path/to/output_dir --recursive
```

### File Patterns

Process only specific file types:
```bash
python -m utils.pipeline.run_pipeline --input path/to/input_dir --output path/to/output_dir --pattern "*.pdf"
```

## Configuration

### Configuration File

Create a YAML configuration file:

```yaml
# pipeline_config.yaml
input_dir: "data/input"
output_dir: "data/output"
output_format: "json"
log_level: "INFO"
validation_level: "basic"

strategies:
  pdf:
    analyzer: "utils.pipeline.analyzer.pdf.PDFAnalyzer"
    cleaner: "utils.pipeline.cleaner.pdf.PDFCleaner"
    extractor: "utils.pipeline.processors.pdf_extractor.PDFExtractor"
    validator: "utils.pipeline.processors.pdf_validator.PDFValidator"

classification:
  enabled: true
  method: "rule_based"
  default_threshold: 0.3
  
  # Document type rules
  rules:
    SPECIFICATION:
      title_keywords: ["specification", "spec", "technical", "requirements"]
      content_keywords: ["dimensions", "capacity", "performance", "material", "compliance", "standard"]
      patterns: ["mm", "cm", "m", "kg", "lb", "°c", "°f", "hz", "mhz", "ghz", "kw", "hp"]
      weights:
        title_match: 0.4
        content_match: 0.3
        pattern_match: 0.3
      threshold: 0.4
      schema_pattern: "detailed_specification"
    
    INVOICE:
      title_keywords: ["invoice", "bill", "receipt"]
      content_keywords: ["invoice #", "invoice no", "payment", "due date"]
      patterns: ["\\$\\d+\\.\\d{2}", "total", "subtotal"]
      threshold: 0.5
      schema_pattern: "detailed_invoice"
  
  # Filename pattern matching
  filename_patterns:
    SPECIFICATION: "(?i)spec|specification"
    INVOICE: "(?i)invoice|bill"
```

Use the configuration file:
```bash
python -m utils.pipeline.run_pipeline --input path/to/input_dir --output path/to/output_dir --config pipeline_config.yaml
```

### Configuration Files

The pipeline includes several pre-defined configuration files:

#### Example Configurations
- **example_config.yaml**: Use this as a starting point for custom configurations
  ```bash
  python -m utils.pipeline.run_pipeline --config utils/pipeline/config/example_config.yaml
  ```

#### Domain-Specific Configurations
- **hvac_config.yaml**: Optimized for HVAC document processing
  ```bash
  python -m utils.pipeline.run_pipeline --config utils/pipeline/config/hvac_config.yaml
  ```

#### Output Format Configurations
To use enhanced markdown formatting:
```bash
python -m utils.pipeline.run_pipeline --config utils/pipeline/config/enhanced_markdown_config_v2.json
```

#### Creating Custom Configurations
You can create custom configurations by copying and modifying the example files:
```bash
# Copy example configuration
cp utils/pipeline/config/example_config.yaml my_custom_config.yaml

# Edit the configuration
# ...

# Use custom configuration
python -m utils.pipeline.run_pipeline --config my_custom_config.yaml
```

For a complete reference of all configuration files, see the [Configuration Files Reference](utils/pipeline/config/CONFIG_FILES.md).

### Environment Variables

You can also configure the pipeline using environment variables:

```bash
export PIPELINE_LOG_LEVEL=DEBUG
export PIPELINE_OUTPUT_FORMAT=json
python -m utils.pipeline.run_pipeline --input path/to/input_dir --output path/to/output_dir
```

## Document Classification

The pipeline includes an advanced document classification system that uses multiple strategies and ensemble methods to categorize documents. This classification is used to organize schemas and can be customized through configuration.

### Classification Configuration

The classification system can be configured in the pipeline configuration file:

```yaml
# Global classification settings
enable_classification: true
record_schemas: true
match_schemas: true

# Ensemble configuration
ensemble:
  voting_method: weighted_average  # weighted_average, majority, consensus
  minimum_confidence: 0.45
  classifier_weights:
    rule_based: 0.45
    pattern_matcher: 0.45
    ml_based: 0.1
  default_weight: 0.3

# Individual classifier configurations
classifiers:
  rule_based:
    name: "Rule-Based Classifier"
    version: "1.0.0"
    description: "Classifies documents using predefined rules"
    classification:
      rules:
        SPECIFICATION:
          title_keywords: ["specification", "spec", "technical"]
          content_keywords: ["dimensions", "performance", "material"]
          patterns: ["mm", "cm", "°c", "hz"]
          weights:
            title_match: 0.4
            content_match: 0.3
            pattern_match: 0.3
          threshold: 0.4
          schema_pattern: "detailed_specification"

  pattern_matcher:
    name: "Pattern Matcher"
    version: "1.0.0"
    description: "Classifies documents using pattern matching"
    patterns:
      - name: "SPECIFICATION"
        schema_pattern: "detailed_specification"
        required_features: ["has_measurements", "has_technical_terms"]
        optional_features: ["has_tables", "has_diagrams"]
        section_patterns: ["specifications", "requirements", "standards"]
        content_patterns: ["dimensions", "material", "performance"]

  ml_based:
    name: "ML-Based Classifier"
    version: "1.0.0"
    description: "Classifies documents using machine learning"
    model:
      confidence_threshold: 0.7
      feature_weights:
        section_density: 0.3
        table_density: 0.2
        avg_section_length: 0.2
        metadata_completeness: 0.3
```

### Adding Custom Document Types

You can add custom document types by defining rules for them in the configuration:

```yaml
classification:
  rules:
    HVAC_SPECIFICATION:
      title_keywords: ["hvac", "heating", "ventilation", "air conditioning"]
      content_keywords: ["temperature", "humidity", "airflow", "ductwork", "refrigerant"]
      patterns: ["°f", "°c", "cfm", "btu"]
      threshold: 0.4
      schema_pattern: "hvac_specification"
```

### Filename Pattern Matching

The classification system can also use filename patterns to help classify documents:

```yaml
classification:
  filename_patterns:
    HVAC_SPECIFICATION: "(?i)hvac|heating|ventilation"
    ELECTRICAL_SPECIFICATION: "(?i)electrical|wiring|circuit"
```

## Schema Management

### Analyzing Schemas

Analyze existing schemas:
```bash
python -m utils.pipeline.run_pipeline --analyze-schemas
```

Filter by document type:
```bash
python -m utils.pipeline.run_pipeline --analyze-schemas --document-type SPECIFICATION
```

### Comparing Schemas

Compare two schemas:
```bash
python -m utils.pipeline.run_pipeline --compare-schemas schema1_id schema2_id
```

### Visualizing Schemas

Visualize schemas:
```bash
python -m utils.pipeline.run_pipeline --visualize-schemas clusters
```

For more detailed information on schema visualization, see [SCHEMA_VISUALIZATION.md](SCHEMA_VISUALIZATION.md).

## Programmatic Usage

You can also use the pipeline programmatically:

```python
from utils.pipeline.pipeline import Pipeline

# Initialize pipeline
pipeline = Pipeline()

# Process a document
output_data = pipeline.run("path/to/document.pdf")

# Save output
pipeline.save_output(output_data, "path/to/output.json")
```

## Customization

### Custom Analyzers

Create a custom analyzer:

```python
from utils.pipeline.analyzer.base import BaseAnalyzer

class CustomAnalyzer(BaseAnalyzer):
    def analyze(self, input_path):
        # Custom analysis logic
        return {
            "metadata": {...},
            "content": [...],
            "path": input_path
        }
```

### Custom Cleaners

Create a custom cleaner:

```python
from utils.pipeline.cleaner.base import BaseCleaner

class CustomCleaner(BaseCleaner):
    def clean(self, data):
        # Custom cleaning logic
        return {
            "metadata": data["metadata"],
            "content": [...],  # Cleaned content
            "path": data["path"]
        }
```

### Custom Extractors

Create a custom extractor:

```python
from utils.pipeline.processors.base import BaseExtractor

class CustomExtractor(BaseExtractor):
    def extract(self, cleaned_data):
        # Custom extraction logic
        return {
            "metadata": cleaned_data["metadata"],
            "sections": [...],
            "tables": [...],
            "path": cleaned_data["path"]
        }
```

### Custom Classifiers

Create a custom classifier:

```python
from utils.pipeline.strategies.classifier_strategy import BaseClassifier
from typing import Any, Dict, List, Optional

class CustomClassifier(BaseClassifier):
    def __init__(self, *, config: Optional[Dict[str, Any]] = None):
        super().__init__(config=config)
        # Initialize custom classifier (e.g., load ML model)
        self.model = self._load_model()

    def classify(
        self, document_data: Dict[str, Any], features: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Implement classification logic
        prediction = self.model.predict(features)
        return {
            "document_type": prediction.doc_type,
            "confidence": prediction.confidence,
            "schema_pattern": f"custom_{prediction.doc_type.lower()}",
            "key_features": prediction.features
        }

    def get_supported_types(self) -> List[str]:
        return ["TYPE_A", "TYPE_B", "TYPE_C"]

    def _load_model(self):
        # Load your custom model (e.g., from a file)
        model_path = self.config.get("model", {}).get("path")
        return YourModelClass.load(model_path)

# Register the classifier
from utils.pipeline.processors.document_classifier import DocumentClassifier

classifier = DocumentClassifier(config)
classifier.add_classifier(
    "custom",
    CustomClassifier,
    {
        "name": "Custom ML Classifier",
        "version": "1.0.0",
        "description": "Custom ML-based document classifier",
        "model": {
            "path": "path/to/model",
            "confidence_threshold": 0.7
        }
    }
)
```

Add the classifier to the ensemble configuration:

```yaml
ensemble:
  voting_method: weighted_average
  classifier_weights:
    rule_based: 0.3
    pattern_matcher: 0.3
    custom: 0.4  # Give more weight to your custom classifier
  minimum_confidence: 0.45
```

## Troubleshooting

### Common Issues

1. **File not found**: Ensure the input file or directory exists
2. **Permission denied**: Check file permissions
3. **Unsupported file type**: Ensure the file type is supported
4. **Missing dependencies**: Install required packages

### Debugging

Enable debug logging:
```bash
export PIPELINE_LOG_LEVEL=DEBUG
python -m utils.pipeline.run_pipeline --file path/to/document.pdf --output path/to/output
```

## Advanced Features

### Batch Processing

Process files in batches:
```bash
python -m utils.pipeline.run_pipeline --input path/to/input_dir --output path/to/output_dir --batch-size 10
```

### Error Handling

Continue processing on error:
```bash
python -m utils.pipeline.run_pipeline --input path/to/input_dir --output path/to/output_dir --continue-on-error
```

### Reporting

Generate a processing report:
```bash
python -m utils.pipeline.run_pipeline --input path/to/input_dir --output path/to/output_dir --report path/to/report.json
