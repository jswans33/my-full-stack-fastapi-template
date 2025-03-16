# **CSI MasterFormat PDF Extraction Tool: Architectural and Implementation Plan**

## **1. Executive Summary**

This document outlines the design and implementation plan for a modular, pipeline-based Python tool for extracting structured data from CSI MasterFormat PDF files into a YAML schema. It adheres to SOLID principles and employs the Strategy pattern to ensure extensibility, maintainability, and clear separation of concerns. The tool dynamically handles multiple input types (PDF, CSV, Excel, text) with automated pre-flight validation and robust extraction strategies.

## **2. System Overview**

The tool follows a structured pipeline approach:

- **Preflight Validation:** Validates document structure and extracts initial metadata.
- **Preprocessing:** Normalizes formatting and initial data preparation.
- **Document Classification:** Identifies document types using multiple classification strategies.
- **Data Extraction:** Parses and structures document data based on identified type.
- **YAML Formatting & Output:** Serializes structured data into a YAML schema.
- **Verification & Reporting:** Validates extracted data accuracy, completeness, and generates reports.

The classification system employs multiple strategies and ensemble methods:
- Rule-based classification using configurable patterns and rules
- Pattern matching based on document structure and content
- Machine learning based classification (extensible)
- Weighted voting system for combining classifier results

## **3. System Architecture**

### **3.1 Core Modules**

- **Configuration Module:** Manages paths, file types, parsing patterns, and schema definitions.
- **Validation Module:** Ensures document integrity and extracts initial metadata.
- **Preprocessing Module:** Standardizes and normalizes input documents for extraction, without detailed table extraction.
- **Data Extraction Module:** Performs detailed content extraction including text sections, tables, adhering to CSI MasterFormat standards.
- **Output Module:** Converts structured data into YAML format.
- **Verification Module:** Confirms data integrity post-extraction.
- **Report Generator:** Logs results and errors encountered.
- **Utility Module:** Provides common functions for logging, file I/O, regex operations, and data transformations.

### **3.2 Strategy Pattern**

- **Extraction Strategies:** Format-specific extraction logic (e.g., PDF, CSV, Excel).
- **Cleaning Strategies:** Format-specific content normalization.

### **3.3 Error Handling and Logging**

- Errors at each stage (validation, preprocessing, extraction) are logged.
- Robust exception handling via `try-except` blocks ensures pipeline resilience.

## **4. Pipeline Flow**

1. **Configuration Load:** Initialize settings from a configuration file.
2. **Validation:** Validate documents for format and metadata.
3. **Preprocessing:** Normalize input to a consistent state for extraction.
4. **Strategy Selection:** Dynamically select appropriate extraction strategies.
5. **Data Extraction:** Perform structured content extraction.
6. **Structuring:** Assemble extracted text, tables, and metadata into a structured Document object.
7. **YAML Output:** Generate and save YAML-formatted output.
8. **Verification & Reporting:** Generate comprehensive extraction reports.

## **5. Dynamic Input Handling & Type Safety**

Utilizes Python's `mypy` for explicit type annotations:

```python
from typing import Literal, Union
from typing_extensions import TypedDict

InputType = Literal['pdf', 'csv', 'excel', 'text']

class RawData(TypedDict):
    content: Union[str, list, dict]
```

## **6. Detailed Class Diagram (Pseudo-Class Diagram)**

```plaintext
ExtractorPipeline
├── ConfigManager
│   ├─ load(config_path) -> ConfigManager
│
├── DocumentValidator (interface)
│   ├─ validate(file_path) -> bool
│   └─ get_errors() -> list[str]
│   ├─ PDFValidator
│   ├─ CSVValidator
│   ├─ ExcelValidator
│   └─ TextValidator
│
├── DocumentPreprocessor
│   └─ preprocess(file_path) -> PreprocessedDocument
│
├── ClassifierStrategy (interface)
│   ├─ classify(document_data, features) -> Dict[str, Any]
│   ├─ get_supported_types() -> List[str]
│   └─ get_classifier_info() -> Dict[str, Any]
│   ├── RuleBasedClassifier
│   ├── PatternMatcherClassifier
│   └── MLBasedClassifier
│
├── ClassifierFactory
│   ├─ register_classifier(name, classifier_class, config)
│   ├─ create_classifier(name, config) -> ClassifierStrategy
│   └─ get_available_classifiers() -> List[Dict[str, Any]]
│
├── EnsembleManager
│   ├─ combine_results(classifications) -> Dict[str, Any]
│   ├─ _weighted_average_vote(classifications) -> Dict[str, Any]
│   ├─ _majority_vote(classifications) -> Dict[str, Any]
│   └─ _consensus_vote(classifications) -> Dict[str, Any]
│
├── ExtractionStrategy (interface)
│   └─ extract(preprocessed_data) -> RawData
│   ├── PDFExtractionStrategy
│   ├── CSVExtractionStrategy
│   ├── ExcelExtractionStrategy
│   └── TextExtractionStrategy
│
├── CleanerStrategy (interface)
│   └─ clean(raw_data) -> StructuredData
│   ├── PDFCleanerStrategy
│   ├── CSVCleanerStrategy
│   ├── ExcelCleanerStrategy
│   └── TextCleanerStrategy
│
├── StructureBuilder
│   └─ build_document(structured_data, metadata) -> Document
│
├── YAMLFormatter
│   └─ format(document: Document) -> str
│
├── YAMLWriter
│   └─ write_file(yaml_content: str, file_path: str)
│
├── Verifier
│   └─ verify(document: Document) -> VerificationResult
│
├── ReportGenerator
│   ├─ record_error(file_path: str, error: str)
│   ├─ record_file_result(file_path: str, result: VerificationResult)
│   └─ generate_report() -> str
│
└── Utility
    ├─ log_error(msg: str)
    ├─ ensure_directory(path: str)
    ├─ save_file(path: str, content: str)
    └─ regex_helpers()
```

### **Class Responsibilities & Attributes**

- Each class maintains a clearly defined role and minimal coupling, supporting SOLID principles.
- Methods and attributes align explicitly with each class’s responsibility, promoting clear TDD practices.

## **6. Scalability and Future Considerations**

To scale effectively:

- Implement parallel processing for multiple documents.
- Optimize extraction algorithms and memory usage.

## **7. Test-Driven Development (TDD) Approach**

Employ unit tests developed incrementally for each module and class, beginning with tests to validate behaviors and outcomes.

## **8. Summary**

This plan ensures flexibility, clarity, and scalability, providing a robust basis for the CSI MasterFormat extraction tool’s effective and efficient development.
