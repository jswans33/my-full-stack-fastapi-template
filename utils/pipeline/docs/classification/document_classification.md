# Document Classification

The pipeline now includes document classification capabilities that can automatically identify document types and match them against known schemas.

## Overview

Document classification analyzes the structure and content of processed documents to determine their type (e.g., proposal, quotation, specification) and identify common patterns. This information can be used to:

1. Organize documents by type
2. Extract relevant information based on document type
3. Match new documents against known schemas
4. Build a knowledge base of document structures

## Components

The document classification system consists of the following components:

### 1. Document Classifier

Located in `utils/pipeline/processors/document_classifier.py`, this component:
- Extracts features from document data
- Applies classification strategies to identify document types
- Returns classification results with confidence scores

### 2. Classification Strategies

Located in `utils/pipeline/processors/classifiers/`, these implement different approaches to document classification:

- **Rule-Based Classifier**: Uses predefined rules to identify document types based on structure and content patterns
- **Pattern Matcher**: Matches documents against known patterns to identify their type

### 3. Schema Registry

Located in `utils/pipeline/schema/registry.py`, this component:
- Stores known document schemas
- Matches new documents against known schemas
- Records new schemas for future matching

### 4. Schema Matchers

Located in `utils/pipeline/schema/matchers.py`, these implement different approaches to schema matching:

- **Structure Matcher**: Matches schemas based on their structure (section hierarchy, table structure, etc.)
- **Content Matcher**: Matches schemas based on their content patterns (section titles, keywords, etc.)

## Integration with Pipeline

The document classification is integrated into the pipeline as a new step between validation and formatting:

1. Analyze document structure
2. Clean and normalize content
3. Extract structured data
4. Validate extracted data
5. **Classify document type and identify schema pattern**
6. Format output
7. Verify output structure

## Configuration

Document classification can be configured in the pipeline configuration:

```python
config = {
    "enable_classification": True,  # Enable document classification
    "record_schemas": True,  # Record schemas for future matching
    "match_schemas": True,  # Match against known schemas
    "classification": {
        "type": "rule_based",  # Classification strategy (rule_based, pattern_matcher)
        "confidence_threshold": 0.6,  # Minimum confidence threshold
    },
}
```

## Classification Results

Classification results are added to the document data and include:

```json
{
  "classification": {
    "document_type": "PROPOSAL",
    "confidence": 0.85,
    "schema_pattern": "detailed_proposal",
    "key_features": [
      "has_payment_terms",
      "has_delivery_terms",
      "proposal_in_title"
    ]
  }
}
```

When schema matching is enabled, additional information may be included:

```json
{
  "classification": {
    "document_type": "PROPOSAL",
    "confidence": 0.85,
    "schema_pattern": "detailed_proposal",
    "key_features": [...],
    "schema_id": "proposal_20250314220145",
    "schema_match_confidence": 0.92,
    "schema_document_type": "PROPOSAL"
  }
}
```

## Example Usage

See `utils/pipeline/examples/document_classification_example.py` for a complete example of using document classification.

## Extending the System

### Adding New Classification Strategies

1. Create a new classifier in `utils/pipeline/processors/classifiers/`
2. Implement the `classify()` method
3. Update `DocumentClassifier` to use the new strategy

### Adding New Schema Matchers

1. Create a new matcher in `utils/pipeline/schema/matchers.py`
2. Implement the `match()` method
3. Update `SchemaMatcherFactory` to use the new matcher

### Adding Known Schema Templates

1. Create a new template in `utils/pipeline/schema/templates/`
2. Implement the schema structure
3. Update the schema registry to use the template
