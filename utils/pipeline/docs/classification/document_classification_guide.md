# Document Classification System Guide

## Overview

The document classification system provides a flexible and extensible way to classify documents based on their content, structure, and metadata. It supports multiple classification strategies that can be combined using ensemble methods.

## Key Components

### 1. ClassifierStrategy Interface

The base interface that all classifiers must implement:

```python
class ClassifierStrategy(ABC):
    @abstractmethod
    def classify(self, document_data: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Classify a document based on its data and features."""
        pass

    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """Get supported document types."""
        pass

    @abstractmethod
    def get_classifier_info(self) -> Dict[str, Any]:
        """Get classifier metadata."""
        pass
```

### 2. BaseClassifier

Abstract base implementation providing common functionality:
- Configuration management
- Feature extraction
- Logging
- Error handling

### 3. ClassifierFactory

Manages classifier registration and instantiation:
```python
factory = ClassifierFactory()
factory.register_classifier("rule_based", RuleBasedClassifier, config)
classifier = factory.create_classifier("rule_based")
```

### 4. EnsembleManager

Combines results from multiple classifiers:
- Weighted voting system
- Multiple voting methods (weighted average, majority, consensus)
- Feature aggregation
- Confidence calculation

## Configuration

### 1. Global Settings

```yaml
enable_classification: true
record_schemas: true
match_schemas: true

ensemble:
  voting_method: weighted_average
  minimum_confidence: 0.45
  classifier_weights:
    rule_based: 0.45
    pattern_matcher: 0.45
    ml_based: 0.1
```

### 2. Classifier Configuration

```yaml
classifiers:
  rule_based:
    name: "Rule-Based Classifier"
    version: "1.0.0"
    description: "Classifies documents using predefined rules"
    classification:
      rules:
        PROPOSAL:
          title_keywords: ["proposal", "project"]
          content_keywords: ["scope", "phases"]
          patterns: ["payment terms", "delivery schedule"]
          weights:
            title_match: 0.4
            content_match: 0.3
            pattern_match: 0.3
          threshold: 0.4
```

## Usage Examples

### 1. Basic Usage

```python
from utils.pipeline.processors.document_classifier import DocumentClassifier

# Initialize with configuration
classifier = DocumentClassifier(config)

# Classify a document
result = classifier.classify(document_data)
print(f"Document Type: {result['document_type']}")
print(f"Confidence: {result['confidence']}")
```

### 2. Adding Custom Classifiers

```python
from utils.pipeline.strategies.classifier_strategy import BaseClassifier

class CustomClassifier(BaseClassifier):
    def classify(self, document_data, features):
        # Implement classification logic
        return {
            "document_type": "CUSTOM_TYPE",
            "confidence": 0.8,
            "schema_pattern": "custom_pattern",
            "key_features": ["feature1", "feature2"]
        }

# Register custom classifier
classifier.add_classifier("custom", CustomClassifier, custom_config)
```

### 3. Runtime Configuration Updates

```python
# Update classifier configuration
new_config = {
    "name": "Updated Classifier",
    "version": "1.1.0",
    "model": {
        "confidence_threshold": 0.8,
        "feature_weights": {
            "section_density": 0.4,
            "table_density": 0.3
        }
    }
}
classifier.update_classifier_config("custom", new_config)
```

## Document Data Format

The system expects document data in the following format:

```python
document_data = {
    "metadata": {
        "title": "Document Title",
        "author": "Author Name",
        "date": "2025-03-15"
    },
    "content": [
        {
            "title": "Section Title",
            "content": "Section content..."
        }
    ],
    "tables": [
        {
            "title": "Table Title",
            "headers": ["Column1", "Column2"],
            "rows": [["Data1", "Data2"]]
        }
    ]
}
```

## Classification Results

The system returns classification results in the following format:

```python
{
    "document_type": "PROPOSAL",
    "confidence": 0.85,
    "schema_pattern": "standard_proposal",
    "key_features": [
        "has_payment_terms",
        "has_delivery_terms",
        "section_contains_executive_summary"
    ],
    "classifiers": [
        "rule_based",
        "pattern_matcher",
        "ml_based"
    ]
}
```

## Best Practices

1. **Configuration Management**
   - Keep classifier configurations in separate YAML files
   - Use version control for configuration changes
   - Document configuration changes

2. **Custom Classifiers**
   - Inherit from BaseClassifier for common functionality
   - Implement all required interface methods
   - Include comprehensive classifier metadata
   - Add proper error handling and logging

3. **Performance**
   - Cache feature extraction results when possible
   - Use appropriate confidence thresholds
   - Monitor classification performance metrics

4. **Maintenance**
   - Regularly update classifier patterns and rules
   - Monitor classification accuracy
   - Keep configurations in sync with document types
   - Document custom implementations

## Troubleshooting

1. **Low Confidence Results**
   - Check classifier configurations
   - Verify pattern matching rules
   - Adjust confidence thresholds
   - Review feature extraction

2. **Misclassifications**
   - Review classifier weights
   - Update pattern matching rules
   - Add more specific patterns
   - Consider adding custom classifiers

3. **Performance Issues**
   - Optimize feature extraction
   - Cache common patterns
   - Review classifier complexity
   - Monitor resource usage
