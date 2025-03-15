# Pipeline Tool Usage Guide

This guide provides detailed instructions on how to use the Document Pipeline Tool for processing various document formats and extracting structured data.

## Overview

The Document Pipeline Tool is a modular, pipeline-based Python tool for extracting structured data from various document formats (PDF, Excel, Word) into structured formats. The pipeline follows a structured approach:

1. **Analyze Document Structure**: Extract metadata and identify document structure
2. **Clean and Normalize Content**: Standardize formatting and prepare data
3. **Extract Structured Data**: Parse and structure document data
4. **Validate Extracted Data**: Ensure data meets expected schema
5. **Classify Document Type** (optional): Identify document type and schema pattern
6. **Format Output**: Serialize structured data into the desired format
7. **Verify Output Structure**: Validate the final output structure

## Prerequisites

Before using the pipeline tool, ensure you have:

- Python 3.8 or higher
- UV package manager (recommended)
- Required dependencies installed (see Setup section)

## Setup

### Creating a Virtual Environment

```bash
# Navigate to the pipeline directory
cd utils/pipeline

# Create a virtual environment with UV
uv venv

# Activate the virtual environment (Windows)
.venv\Scripts\activate

# Activate the virtual environment (Unix/Linux/Mac)
# source .venv/bin/activate
```

### Installing Dependencies

The project uses optional dependency groups to manage different document format processors:

```bash
# Install base dependencies only
uv pip install -e .

# Install specific document format processors
uv pip install -e ".[pdf]"     # PDF processing
uv pip install -e ".[excel]"   # Excel processing
uv pip install -e ".[word]"    # Word processing

# Install text analysis tools
uv pip install -e ".[analysis]"

# Install development tools
uv pip install -e ".[dev]"

# Install a minimal set of all document processors
uv pip install -e ".[all]"

# Install everything
uv pip install -e ".[pdf,excel,word,analysis,dev]"
```

If you encounter issues with the editable install syntax, you can install dependencies directly:

```bash
# Install base dependencies
uv pip install pyyaml typing-extensions

# Install document processors
uv pip install PyPDF2 pdfminer.six pymupdf pandas openpyxl python-docx
```

## Basic Usage

### Processing a Document

The simplest way to process a document is to use the `Pipeline` class directly:

```python
from utils.pipeline.pipeline import Pipeline

# Initialize pipeline with default configuration
pipeline = Pipeline()

# Process a document
result = pipeline.run("path/to/document.pdf")

# Save the result to a file
pipeline.save_output(result, "output.json")
```

### Using the Command-Line Interface

For convenience, you can also use the command-line interface:

```bash
# Process a document
python run_pipeline.py path/to/document.pdf

# Process a document and save output to a specific file
python run_pipeline.py path/to/document.pdf --output output.json

# Process a document with a specific configuration
python run_pipeline.py path/to/document.pdf --config config/custom_config.yaml
```

## Configuration Options

The pipeline can be configured using a dictionary or a YAML configuration file. Here's an example configuration:

```yaml
# Example configuration
output_format: json  # or markdown
enable_classification: true
record_schemas: true
match_schemas: true

# Strategy configuration
strategies:
  pdf:
    analyzer: utils.pipeline.analyzer.pdf.PDFAnalyzer
    cleaner: utils.pipeline.cleaner.pdf.PDFCleaner
    extractor: utils.pipeline.processors.pdf_extractor.PDFExtractor
    validator: utils.pipeline.processors.pdf_validator.PDFValidator
  excel:
    analyzer: utils.pipeline.analyzer.excel.ExcelAnalyzer
    cleaner: utils.pipeline.cleaner.excel.ExcelCleaner
    extractor: utils.pipeline.processors.excel_extractor.ExcelExtractor
    validator: utils.pipeline.processors.excel_validator.ExcelValidator
  word:
    analyzer: utils.pipeline.analyzer.word.WordAnalyzer
    cleaner: utils.pipeline.cleaner.word.WordCleaner
    extractor: utils.pipeline.processors.word_extractor.WordExtractor
    validator: utils.pipeline.processors.word_validator.WordValidator

# Classification configuration
classification:
  type: rule_based  # or ml_based
  confidence_threshold: 0.7
```

To use a configuration file:

```python
import yaml
from utils.pipeline.pipeline import Pipeline

# Load configuration from file
with open("config/custom_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize pipeline with configuration
pipeline = Pipeline(config)

# Process a document
result = pipeline.run("path/to/document.pdf")
```

## Processing Different Document Types

The pipeline automatically detects the document type based on the file extension:

- `.pdf` - PDF documents
- `.xlsx`, `.xls` - Excel documents
- `.docx`, `.doc` - Word documents
- `.txt` - Text documents

### PDF Documents

PDF documents are processed using the PDF-specific strategies:

```python
from utils.pipeline.pipeline import Pipeline

pipeline = Pipeline()
result = pipeline.run("path/to/document.pdf")
```

The PDF processor extracts:
- Metadata (title, author, subject, etc.)
- Page information (size, rotation, content)
- Sections (based on text formatting and structure)
- Tables (if present)

### Excel Documents

Excel documents are processed using the Excel-specific strategies:

```python
from utils.pipeline.pipeline import Pipeline

pipeline = Pipeline()
result = pipeline.run("path/to/spreadsheet.xlsx")
```

The Excel processor extracts:
- Worksheet information
- Cell data
- Tables and ranges
- Named ranges

### Word Documents

Word documents are processed using the Word-specific strategies:

```python
from utils.pipeline.pipeline import Pipeline

pipeline = Pipeline()
result = pipeline.run("path/to/document.docx")
```

The Word processor extracts:
- Document properties
- Paragraphs and formatting
- Tables
- Lists and headings

## Advanced Usage

### Customizing the Pipeline

You can customize the pipeline by providing a configuration dictionary:

```python
from utils.pipeline.pipeline import Pipeline

# Custom configuration
config = {
    "output_format": "json",
    "enable_classification": True,
    "record_schemas": True,
    "strategies": {
        "pdf": {
            "analyzer": "utils.pipeline.analyzer.pdf.PDFAnalyzer",
            "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
            "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
            "validator": "utils.pipeline.processors.pdf_validator.PDFValidator",
        }
    }
}

# Initialize pipeline with custom configuration
pipeline = Pipeline(config)

# Process a document
result = pipeline.run("path/to/document.pdf")
```

### Batch Processing

To process multiple documents in batch:

```python
import os
from utils.pipeline.pipeline import Pipeline

# Initialize pipeline
pipeline = Pipeline()

# Process all PDF files in a directory
input_dir = "path/to/documents"
output_dir = "path/to/output"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Process each PDF file
for filename in os.listdir(input_dir):
    if filename.lower().endswith(".pdf"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
        
        try:
            # Process document
            result = pipeline.run(input_path)
            
            # Save output
            pipeline.save_output(result, output_path)
            print(f"Processed: {filename} -> {output_path}")
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
```

### Document Classification

The pipeline can classify documents based on their content and structure:

```python
from utils.pipeline.pipeline import Pipeline

# Enable classification in configuration
config = {
    "enable_classification": True,
    "classification": {
        "type": "rule_based",
        "confidence_threshold": 0.7
    }
}

# Initialize pipeline with classification enabled
pipeline = Pipeline(config)

# Process a document
result = pipeline.run("path/to/document.pdf")

# Access classification results
if "classification" in result:
    document_type = result["classification"]["document_type"]
    confidence = result["classification"]["confidence"]
    print(f"Document classified as: {document_type} (confidence: {confidence})")
```

### Schema Recording and Matching

The pipeline can record document schemas and match new documents against known schemas:

```python
from utils.pipeline.pipeline import Pipeline

# Enable schema recording and matching in configuration
config = {
    "record_schemas": True,
    "match_schemas": True
}

# Initialize pipeline with schema features enabled
pipeline = Pipeline(config)

# Process a document and record its schema
result = pipeline.run("path/to/document.pdf")

# Process another document and match against known schemas
result2 = pipeline.run("path/to/another_document.pdf")

# Access schema matching results
if "classification" in result2 and "schema_id" in result2["classification"]:
    schema_id = result2["classification"]["schema_id"]
    confidence = result2["classification"]["schema_match_confidence"]
    print(f"Document matched schema: {schema_id} (confidence: {confidence})")
```

## Extending the Pipeline

### Adding a New Document Format

To add support for a new document format:

1. Create analyzer, cleaner, extractor, and validator classes for the new format
2. Register the new strategies in the configuration

Example for adding support for a new format:

```python
# Create analyzer class (my_format_analyzer.py)
class MyFormatAnalyzer:
    def analyze(self, input_path):
        # Implementation for analyzing the new format
        pass

# Create cleaner class (my_format_cleaner.py)
class MyFormatCleaner:
    def clean(self, analysis_result):
        # Implementation for cleaning the new format
        pass

# Create extractor class (my_format_extractor.py)
class MyFormatExtractor:
    def extract(self, cleaned_data):
        # Implementation for extracting data from the new format
        pass

# Create validator class (my_format_validator.py)
class MyFormatValidator:
    def validate(self, extracted_data):
        # Implementation for validating data from the new format
        pass

# Register the new format in configuration
config = {
    "strategies": {
        "myformat": {
            "analyzer": "path.to.my_format_analyzer.MyFormatAnalyzer",
            "cleaner": "path.to.my_format_cleaner.MyFormatCleaner",
            "extractor": "path.to.my_format_extractor.MyFormatExtractor",
            "validator": "path.to.my_format_validator.MyFormatValidator",
        }
    }
}

# Initialize pipeline with the new format support
pipeline = Pipeline(config)
```

### Customizing Output Formats

To add a new output format:

1. Create a new formatter class that implements the required interface
2. Register the formatter with the FormatterFactory

Example for adding a new output format:

```python
from enum import auto
from utils.pipeline.processors.formatters.factory import FormatterFactory, OutputFormat
from utils.pipeline.processors.formatters.base import BaseFormatter

# Add new format to OutputFormat enum
OutputFormat.XML = auto()

# Create XML formatter class
class XMLFormatter(BaseFormatter):
    def format(self, data):
        # Implementation for formatting data as XML
        pass
    
    def write(self, data, output_path):
        # Implementation for writing XML to file
        pass

# Register the new formatter
FormatterFactory.register_formatter(OutputFormat.XML, XMLFormatter)

# Use the new formatter
config = {
    "output_format": "XML"
}
pipeline = Pipeline(config)
result = pipeline.run("path/to/document.pdf")
pipeline.save_output(result, "output.xml")
```

## Troubleshooting

### Common Issues

#### Missing Dependencies

If you encounter errors about missing modules:

```
ImportError: No module named 'pypdf'
```

Install the required dependencies:

```bash
uv pip install pypdf
```

#### File Not Found

If you get a "File not found" error:

```
FileNotFoundError: [Errno 2] No such file or directory: 'path/to/document.pdf'
```

Check that the file path is correct and the file exists.

#### Strategy Import Error

If you see an error importing strategies:

```
ImportError: Failed to import strategy utils.pipeline.analyzer.pdf.PDFAnalyzer
```

Ensure that the strategy module exists and is correctly specified in the configuration.

#### Output Directory Not Found

If you get an error saving the output:

```
FileNotFoundError: [Errno 2] No such file or directory: 'path/to/output/result.json'
```

Ensure that the output directory exists:

```python
import os
os.makedirs(os.path.dirname(output_path), exist_ok=True)
```

### Debugging

To enable debug logging:

```python
import logging
from utils.pipeline.utils.logging import setup_logging

# Set up logging with debug level
setup_logging(level=logging.DEBUG)

# Initialize pipeline
pipeline = Pipeline()
```

### Error Handling

To handle errors gracefully:

```python
from utils.pipeline.pipeline import Pipeline, PipelineError

pipeline = Pipeline()

try:
    result = pipeline.run("path/to/document.pdf")
    pipeline.save_output(result, "output.json")
    print("Document processed successfully")
except PipelineError as e:
    print(f"Pipeline error: {str(e)}")
except FileNotFoundError as e:
    print(f"File not found: {str(e)}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

## Examples

### Basic Example

```python
from utils.pipeline.pipeline import Pipeline

# Initialize pipeline
pipeline = Pipeline()

# Process a PDF document
result = pipeline.run("path/to/document.pdf")

# Save the result as JSON
pipeline.save_output(result, "output.json")
```

### Custom Configuration Example

```python
import yaml
from utils.pipeline.pipeline import Pipeline

# Load configuration from file
with open("config/custom_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize pipeline with configuration
pipeline = Pipeline(config)

# Process a document with progress display
result = pipeline.run("path/to/document.pdf", show_progress=True)

# Save the result as Markdown
pipeline.save_output(result, "output.md")
```

### Batch Processing Example

```python
import os
import json
from utils.pipeline.pipeline import Pipeline

# Initialize pipeline
pipeline = Pipeline()

# Process all documents in a directory
input_dir = "path/to/documents"
output_dir = "path/to/output"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Process each document
for filename in os.listdir(input_dir):
    input_path = os.path.join(input_dir, filename)
    
    # Skip directories
    if os.path.isdir(input_path):
        continue
    
    # Determine output format based on input file
    _, ext = os.path.splitext(filename)
    if ext.lower() in [".pdf", ".docx", ".xlsx"]:
        output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
        
        try:
            # Process document
            result = pipeline.run(input_path)
            
            # Save output
            pipeline.save_output(result, output_path)
            print(f"Processed: {filename} -> {output_path}")
            
            # Save summary
            summary_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_summary.json")
            with open(summary_path, "w") as f:
                summary = {
                    "filename": filename,
                    "sections": len(result.get("content", [])),
                    "tables": len(result.get("tables", [])),
                }
                if "classification" in result:
                    summary["document_type"] = result["classification"]["document_type"]
                    summary["confidence"] = result["classification"]["confidence"]
                json.dump(summary, f, indent=2)
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
```

## Further Reading

For more information about the pipeline architecture and design principles, see:

- [Pipeline Architecture](docs/pipeline-plan.md)
- [Schema Visualization Guide](SCHEMA_VISUALIZATION.md)

For API documentation, see the docstrings in the source code:

- `utils/pipeline/pipeline.py`: Main pipeline orchestrator
- `utils/pipeline/analyzer/`: Document analyzers
- `utils/pipeline/cleaner/`: Content cleaners
- `utils/pipeline/processors/`: Data extractors and validators
- `utils/pipeline/schema/`: Schema registry and visualization
- `utils/pipeline/verify/`: Output verification
