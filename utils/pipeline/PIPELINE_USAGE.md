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

### Environment Variables

You can also configure the pipeline using environment variables:

```bash
export PIPELINE_LOG_LEVEL=DEBUG
export PIPELINE_OUTPUT_FORMAT=json
python -m utils.pipeline.run_pipeline --input path/to/input_dir --output path/to/output_dir
```

## Document Classification

The pipeline includes a document classification system that categorizes documents based on their content and structure. This classification is used to organize schemas and can be customized through configuration.

### Classification Configuration

The classification system can be configured in the pipeline configuration file:

```yaml
classification:
  # Enable/disable classification
  enabled: true
  
  # Default confidence threshold
  default_threshold: 0.3
  
  # Classification method (rule_based, pattern_matcher, etc.)
  method: "rule_based"
  
  # Document type rules
  rules:
    SPECIFICATION:
      # Keywords to look for in section titles
      title_keywords: ["specification", "spec", "technical", "requirements"]
      
      # Keywords to look for in document content
      content_keywords: ["dimensions", "capacity", "performance", "material", "compliance", "standard"]
      
      # Patterns to match (e.g., measurements)
      patterns: ["mm", "cm", "m", "kg", "lb", "°c", "°f", "hz", "mhz", "ghz", "kw", "hp"]
      
      # Confidence weights for different features
      weights:
        title_match: 0.4
        content_match: 0.3
        pattern_match: 0.3
      
      # Minimum confidence threshold to classify as this type
      threshold: 0.4
      
      # Schema pattern to use for this document type
      schema_pattern: "detailed_specification"
  
  # Filename pattern matching (optional)
  filename_patterns:
    SPECIFICATION: "(?i)spec|specification"
    INVOICE: "(?i)invoice|bill"
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
