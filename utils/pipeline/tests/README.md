# Classification System Testing Guide

This guide explains how to run and extend the end-to-end tests for the document classification system.

## Overview

The test suite provides comprehensive testing of the classification system, including:
- End-to-end pipeline flow
- Individual classifier behavior
- Ensemble classification
- Feature extraction
- Error handling

## Test Structure

The tests follow the sequence outlined in `docs/diagrams/e2e_sequence.puml`:

1. **Test Setup**
   - Pipeline initialization
   - Classifier registration
   - Test document preparation

2. **Document Processing**
   - Document type detection
   - Document analysis
   - Content cleaning

3. **Classification Flow**
   - Feature extraction
   - Rule-based classification
   - Pattern matching
   - ML-based classification
   - Ensemble combination

4. **Result Verification**
   - Document type verification
   - Confidence score validation
   - Schema pattern checking
   - Feature detection validation

## Running the Tests

### Basic Usage

```bash
# Run all tests
pytest utils/pipeline/tests/test_e2e_classification.py

# Run with verbose output
pytest -v utils/pipeline/tests/test_e2e_classification.py

# Run specific test
pytest utils/pipeline/tests/test_e2e_classification.py::test_end_to_end_classification
```

### Test Categories

1. **End-to-End Test**
   ```bash
   pytest utils/pipeline/tests/test_e2e_classification.py::test_end_to_end_classification
   ```
   Tests the complete pipeline flow from document input to final classification.

2. **Individual Classifier Tests**
   ```bash
   pytest utils/pipeline/tests/test_e2e_classification.py::test_classifier_individual_results
   ```
   Tests each classifier's behavior independently.

3. **Ensemble Tests**
   ```bash
   pytest utils/pipeline/tests/test_e2e_classification.py::test_ensemble_combination
   ```
   Tests the ensemble's combination of classifier results.

4. **Error Handling Tests**
   ```bash
   pytest utils/pipeline/tests/test_e2e_classification.py::test_error_handling
   ```
   Tests system behavior with invalid inputs.

5. **Feature Extraction Tests**
   ```bash
   pytest utils/pipeline/tests/test_e2e_classification.py::test_feature_extraction
   ```
   Tests the feature extraction process.

## Test Data

The tests use a sample proposal document with the following characteristics:
- Title indicating a project proposal
- Executive summary section
- Scope of work section
- Payment terms section
- Delivery schedule section
- Cost breakdown table

This document is designed to test all aspects of the classification system:
- Rule-based matching of keywords and patterns
- Pattern matching of document structure
- ML-based feature extraction and scoring

## Test Configuration

The test configuration includes:
- Ensemble settings with classifier weights
- Rule-based classifier patterns
- Pattern matcher requirements
- ML classifier feature weights

You can modify the configuration in the `test_config` fixture to test different scenarios.

## Adding New Tests

### 1. Test New Document Types

Create a new test document fixture:
```python
@pytest.fixture
def test_invoice_document() -> Dict[str, Any]:
    return {
        "metadata": {
            "title": "Invoice #12345",
            ...
        },
        ...
    }
```

### 2. Test New Classifiers

Add tests for your custom classifier:
```python
def test_custom_classifier_results(test_config, test_document):
    classifier = DocumentClassifier(test_config)
    custom = classifier.factory.create_classifier("custom")
    result = custom.classify(test_document, features)
    assert result["document_type"] == "EXPECTED_TYPE"
```

### 3. Test New Features

Add tests for new feature extraction:
```python
def test_custom_feature_extraction(test_config, test_document):
    classifier = DocumentClassifier(test_config)
    features = classifier._extract_features(test_document)
    assert features["new_feature"] == expected_value
```

## Troubleshooting Tests

### Common Issues

1. **Low Confidence Scores**
   - Check classifier weights in test_config
   - Verify document content matches patterns
   - Check feature extraction results

2. **Misclassification**
   - Review classifier patterns and rules
   - Check feature extraction
   - Verify ensemble weights

3. **Test Failures**
   - Check test document structure
   - Verify configuration settings
   - Review classifier thresholds

### Debug Output

Enable debug logging to see detailed classification process:
```python
import logging
logging.getLogger("utils.pipeline").setLevel(logging.DEBUG)
```

## Continuous Integration

The test suite is designed to run in CI environments:
```yaml
# Example GitHub Actions workflow
name: Classification Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest utils/pipeline/tests/test_e2e_classification.py
```

## Best Practices

1. **Test Data Management**
   - Keep test documents in version control
   - Use realistic document content
   - Cover edge cases and variations

2. **Configuration Testing**
   - Test different ensemble weights
   - Test various confidence thresholds
   - Test multiple classifier combinations

3. **Error Cases**
   - Test invalid documents
   - Test missing required fields
   - Test malformed content

4. **Performance Testing**
   - Test with large documents
   - Test with multiple documents
   - Monitor classification speed

## Related Documentation

- [Classification System Guide](../docs/document_classification_guide.md)
- [Configuration System](../docs/configuration_system.md)
- [Pipeline Usage Guide](../PIPELINE_USAGE.md)
- [System Diagrams](../docs/diagrams/README.md)
