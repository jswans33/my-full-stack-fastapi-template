# Document Flow Guide

This guide outlines how documents flow through the pipeline architecture from ingestion to final output, referencing the relevant architecture diagrams at each stage.

## Complete Document Processing Flow

A document flows through the following key stages in the pipeline system:

### 1. Document Ingestion
Entry point where the document enters the system.

**Relevant Diagrams:**
- [01-01-pipeline-architecture.puml](01-01-pipeline-architecture.puml) - Shows entry points (CLI and API)
- [06-01-pdf-processing-usecase.puml](06-01-pdf-processing-usecase.puml) - Use cases for document upload

**Key Components:**
- CLI Interface
- API Interface
- FileProcessor

### 2. Document Classification
The system analyzes and determines the type of document.

**Relevant Diagrams:**
- [02-01-classifier-diagram.puml](02-01-classifier-diagram.puml) - Class structure for classification
- [02-02-document-classifier-flow.puml](02-02-document-classifier-flow.puml) - Flow diagram
- [06-03-pdf-classifier-components.puml](06-03-pdf-classifier-components.puml) - PDF-specific components
- [06-04-pdf-classification-decision.puml](06-04-pdf-classification-decision.puml) - Decision logic

**Key Components:**
- DocumentClassifier
- Feature Extractor
- Classification Strategies (Template, Keyword, ML, etc.)
- Ensemble Manager

**Process:**
1. Document features are extracted (text, layout, metadata)
2. Multiple classification strategies analyze the document
3. Results are combined through ensemble techniques
4. Most likely classification is selected with confidence score

### 3. Schema Validation
The classified document is validated against registered schemas.

**Relevant Diagrams:**
- [05-01-schema-registry-class.puml](05-01-schema-registry-class.puml) - Schema registry structure
- [05-02-schema-registry-flow.puml](05-02-schema-registry-flow.puml) - Validation flow

**Key Components:**
- SchemaRegistry
- Schema Validator
- Document Types Database

**Process:**
1. System looks up the schema for the classified document type
2. Document structure is validated against the schema
3. Validation results determine next processing steps

### 4. Data Normalization
Document data is extracted and normalized based on the document type.

**Relevant Diagrams:**
- [06-03-pdf-classifier-components.puml](06-03-pdf-classifier-components.puml) - Shows Normalizer component

**Key Components:**
- Data Normalizer
- Type-specific Extractors

**Process:**
1. Raw document data is extracted based on document type
2. Data is normalized to standard formats
3. Structured data is prepared for formatting

### 5. Formatting
The normalized data is formatted for output.

**Relevant Diagrams:**
- [03-01-formatter-class.puml](03-01-formatter-class.puml) - Formatter class structure
- [03-02-formatter-flow.puml](03-02-formatter-flow.puml) - Formatting process flow

**Key Components:**
- FormatterFactory
- Specific Formatters (JSON, Markdown, etc.)

**Process:**
1. Appropriate formatter is selected based on requirements
2. Normalized data is formatted into the desired output format
3. Formatted output is prepared for verification

### 6. Verification
The formatted output is verified for correctness and completeness.

**Relevant Diagrams:**
- [04-01-verifier-class.puml](04-01-verifier-class.puml) - Verifier class structure
- [04-02-verifier-flow.puml](04-02-verifier-flow.puml) - Verification process flow

**Key Components:**
- VerifierFactory
- Specific Verifiers (JSON, Markdown, etc.)

**Process:**
1. Appropriate verifier is selected based on output format
2. Output is checked for structural integrity
3. Content validation is performed
4. Verification results determine if output is accepted

### 7. Final Output Generation
The verified output is delivered to the user or downstream systems.

**Relevant Diagrams:**
- [01-02-complete-pipeline-flow.puml](01-02-complete-pipeline-flow.puml) - Overall data flow
- [06-01-pdf-processing-usecase.puml](06-01-pdf-processing-usecase.puml) - Output use cases

**Key Components:**
- Pipeline (final output generation)
- Export Mechanisms

## Example: PDF Document Flow

Here's a specific example of how a PDF document flows through the system:

1. **Ingestion**: PDF document is uploaded via API or CLI
   *(See 01-01, 06-01)*

2. **Feature Extraction**: Text, layout, metadata and images are extracted
   *(See 06-03)*

3. **Classification**:
   * Template matching attempted first
   * If unsuccessful, form fields analysis
   * If unsuccessful, official letterhead/logo detection
   * If unsuccessful, financial data analysis
   * If unsuccessful, ML classification
   * If unsuccessful, keyword matching
   * If all fail, marked for manual review
   *(See 06-04 for detailed decision flow)*

4. **Schema Validation**: Classified document validated against schema registry
   *(See 05-01, 05-02)*

5. **Data Extraction**: Structured data extracted based on document type
   *(See 06-03)*

6. **Formatting**: Data formatted to JSON or structured text
   *(See 03-01, 03-02)*

7. **Verification**: Output verified for correctness
   *(See 04-01, 04-02)*

8. **Delivery**: Verified output delivered as final result
   *(See 01-02)*

## Error Handling Flow

The system includes error handling at various stages:

1. **Classification Fallbacks**: Multiple strategies with priority ordering
   *(See 06-04)*

2. **Validation Failures**: Schema validation errors trigger alternative processing
   *(See 05-02)*

3. **Manual Review**: Documents that can't be automatically processed are flagged
   *(See 06-04)*

This document flow guide helps understand how the various architectural components interact during document processing. Use the referenced diagrams to explore specific aspects in greater detail.