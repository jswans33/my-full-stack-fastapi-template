# Architecture Implementation Guide

This guide helps developers understand how the architecture diagrams map to actual code implementation in the pipeline system. It provides practical guidance for working with the codebase based on the architecture.

## Mapping Diagrams to Code

The architecture diagrams represent the conceptual structure of the system. Here's how they map to actual code implementation:

### Core Pipeline Components

**Pipeline Architecture (01-01)**
- CLI Interface → `utils/pipeline/cli/` directory
- API Interface → `utils/pipeline/api/` directory
- FileProcessor → `utils/pipeline/processor/file_processor.py`
- Pipeline → `utils/pipeline/core/pipeline.py`
- StrategySelector → `utils/pipeline/core/strategy_selector.py`

### Document Classifier (02-01, 02-02, 02-03)

- DocumentClassifier → `utils/pipeline/classifier/document_classifier.py`
- ClassifierFactory → `utils/pipeline/classifier/factory.py`
- Class hierarchy:
  ```
  ClassifierStrategy (interface)
  └── BaseClassifier
      ├── RuleBasedClassifier
      ├── PatternMatcherClassifier
      └── MLBasedClassifier
  ```

- Implementation files:
  - `utils/pipeline/classifier/strategies/base.py`
  - `utils/pipeline/classifier/strategies/rule_based.py`
  - `utils/pipeline/classifier/strategies/pattern_matcher.py`
  - `utils/pipeline/classifier/strategies/ml_based.py`

### Formatter Components (03-01, 03-02)

- FormatterFactory → `utils/pipeline/formatters/factory.py`
- Formatter implementations:
  - JSONFormatter → `utils/pipeline/formatters/json_formatter.py`
  - MarkdownFormatter → `utils/pipeline/formatters/markdown_formatter.py`
  - EnhancedMarkdownFormatter → `utils/pipeline/formatters/enhanced_markdown.py`

### Verifier Components (04-01, 04-02)

- VerifierFactory → `utils/pipeline/verifiers/factory.py`
- Verifier implementations:
  - JSONTreeVerifier → `utils/pipeline/verifiers/json_verifier.py`
  - MarkdownVerifier → `utils/pipeline/verifiers/markdown_verifier.py`

### Schema Registry (05-01, 05-02)

- SchemaRegistry → `utils/pipeline/schema/registry.py`
- Schema management:
  - SchemaLoader → `utils/pipeline/schema/loader.py`
  - SchemaValidator → `utils/pipeline/schema/validator.py`
  - Document schemas stored in `utils/pipeline/schema/definitions/`

### PDF Processing (06-01, 06-02, 06-03, 06-04)

- Feature extractors:
  - TextAnalyzer → `utils/pipeline/pdf/extractors/text.py`
  - LayoutAnalyzer → `utils/pipeline/pdf/extractors/layout.py`
  - MetadataExtractor → `utils/pipeline/pdf/extractors/metadata.py`
  - ImageRecognizer → `utils/pipeline/pdf/extractors/image.py`

- Classification strategies:
  - TemplateMatcher → `utils/pipeline/pdf/classifiers/template.py`
  - KeywordClassifier → `utils/pipeline/pdf/classifiers/keyword.py`
  - HeaderFooterAnalyzer → `utils/pipeline/pdf/classifiers/header_footer.py`
  - MLDocumentClassifier → `utils/pipeline/pdf/classifiers/ml.py`
  - FormFieldDetector → `utils/pipeline/pdf/classifiers/form.py`

- EnsembleManager → `utils/pipeline/pdf/ensemble.py`
- ResultManager → `utils/pipeline/pdf/result_manager.py`

## Key Interfaces and Extension Points

The diagrams highlight several extension points in the system:

### Adding a New Classifier Strategy

1. Create a new class that extends `BaseClassifier` from `utils/pipeline/classifier/strategies/base.py`
2. Implement the required methods:
   ```python
   def is_applicable(self, document: Document) -> bool:
       # Determine if this classifier can handle the document
       pass
       
   def classify(self, document: Document) -> ClassificationResult:
       # Implement classification logic
       pass
   ```
3. Register the new classifier in `utils/pipeline/classifier/factory.py`

### Adding a New Formatter

1. Create a new class that implements the `Formatter` interface
2. Implement the required methods:
   ```python
   def format(self, data: Dict) -> str:
       # Transform data into formatted output
       pass
   ```
3. Register the new formatter in `utils/pipeline/formatters/factory.py`

### Adding a New Verifier

1. Create a new class that implements the `Verifier` interface
2. Implement the required methods:
   ```python
   def verify(self, formatted_output: str) -> VerificationResult:
       # Verify the formatted output
       pass
   ```
3. Register the new verifier in `utils/pipeline/verifiers/factory.py`

### Adding a New Document Schema

1. Create a new schema definition in `utils/pipeline/schema/definitions/`
2. Register the schema in the schema registry

## Common Implementation Patterns

The system uses several design patterns consistently:

### Factory Pattern

Example from FormatterFactory:
```python
class FormatterFactory:
    _formatters = {}
    
    @classmethod
    def register_formatter(cls, name: str, formatter_class: Type[Formatter]) -> None:
        cls._formatters[name] = formatter_class
    
    @classmethod
    def create_formatter(cls, name: str, **kwargs) -> Formatter:
        formatter_class = cls._formatters.get(name)
        if not formatter_class:
            raise ValueError(f"No formatter registered with name: {name}")
        return formatter_class(**kwargs)
```

### Strategy Pattern

Example from DocumentClassifier:
```python
class DocumentClassifier:
    def __init__(self, strategies: List[ClassifierStrategy]):
        self.strategies = strategies
    
    def classify(self, document: Document) -> ClassificationResult:
        for strategy in self.strategies:
            if strategy.is_applicable(document):
                result = strategy.classify(document)
                if result.confidence > CONFIDENCE_THRESHOLD:
                    return result
        
        return ClassificationResult(
            document_type="unknown",
            confidence=0.0
        )
```

### Dependency Injection

Example from Pipeline:
```python
class Pipeline:
    def __init__(
        self,
        classifier: DocumentClassifier,
        formatter_factory: FormatterFactory,
        verifier_factory: VerifierFactory,
        schema_registry: SchemaRegistry
    ):
        self.classifier = classifier
        self.formatter_factory = formatter_factory
        self.verifier_factory = verifier_factory
        self.schema_registry = schema_registry
    
    def process(self, document: Document) -> ProcessingResult:
        # Implementation
        pass
```

## Testing with the Architecture in Mind

The architecture diagrams guide testing strategy:

1. **Unit Testing**: Test individual components in isolation
   - Example: Test a specific classifier strategy

2. **Integration Testing**: Test component interactions
   - Example: Test classification followed by schema validation

3. **Flow Testing**: Test end-to-end document processing flows
   - Example: Test the complete PDF processing flow from 06-02

## Maintaining Architecture-Code Alignment

When making code changes:

1. Identify affected components in the architecture diagrams
2. Update implementation according to established patterns
3. If architecture changes, update diagrams first
4. Ensure tests verify the architectural constraints