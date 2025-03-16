# Diagram Navigation Guide

This guide provides a map of how the architecture diagrams are related to each other and how to navigate between them based on what you're trying to understand.

## Diagram Relationships Map

```
                                         ┌─────────────────────┐
                                         │    Overall System   │
                                         │   Architecture (01) │
                                         └─────────┬───────────┘
                                                   │
                                                   ▼
                  ┌───────────────────────────────┬─────────────────────────────┬─────────────────────────────┐
                  │                               │                             │                             │
       ┌──────────▼──────────┐        ┌──────────▼──────────┐        ┌─────────▼────────────┐      ┌─────────▼────────────┐
       │  Document Classifier │        │  Formatter Component │        │  Verifier Component │      │ Schema Registry      │
       │    Component (02)    │        │        (03)          │        │        (04)         │      │   Component (05)     │
       └──────────┬──────────┘        └──────────┬──────────┘        └─────────┬────────────┘      └─────────┬────────────┘
                  │                               │                             │                             │
                  │                               │                             │                             │
                  │                               │                             │                             │
                  │           ┌───────────────────┴─────────────────────────────┴─────────────────┐           │
                  │           │                                                                   │           │
                  │           │                                                                   │           │
                  └───────────▶                   PDF Document Processing (06)                    ◀───────────┘
                              │                                                                   │
                              └───────────────────────────────────────────────────────────────────┘
```

## How to Navigate Diagrams by Purpose

### Understanding Overall Architecture
**Start with**: [01-01-pipeline-architecture.puml](01-01-pipeline-architecture.puml)
* Shows all major components and their relationships
* Contains cross-references to other detailed diagrams
* Follow with [01-02-complete-pipeline-flow.puml](01-02-complete-pipeline-flow.puml) for data flow

### Understanding Document Classification
**Start with**: [02-01-classifier-diagram.puml](02-01-classifier-diagram.puml)
* Shows the class structure of the classifier system
* For classifier flow, see [02-02-document-classifier-flow.puml](02-02-document-classifier-flow.puml)
* For component view, see [02-03-document-classifier-diagram.puml](02-03-document-classifier-diagram.puml)
* For PDF-specific classification, see section below

### Understanding Formatting System
**Start with**: [03-01-formatter-class.puml](03-01-formatter-class.puml)
* Shows the class structure of the formatter system
* For formatting flow, see [03-02-formatter-flow.puml](03-02-formatter-flow.puml)

### Understanding Verification System
**Start with**: [04-01-verifier-class.puml](04-01-verifier-class.puml)
* Shows the class structure of the verification system
* For verification flow, see [04-02-verifier-flow.puml](04-02-verifier-flow.puml)

### Understanding Schema Registry
**Start with**: [05-01-schema-registry-class.puml](05-01-schema-registry-class.puml)
* Shows the class structure of the schema registry
* For schema validation flow, see [05-02-schema-registry-flow.puml](05-02-schema-registry-flow.puml)

### Understanding PDF Document Processing
**Start with**: [06-01-pdf-processing-usecase.puml](06-01-pdf-processing-usecase.puml)
* Shows user interaction with the PDF processing system
* For sequence of operations, see [06-02-pdf-processing-sequence.puml](06-02-pdf-processing-sequence.puml)
* For component architecture, see [06-03-pdf-classifier-components.puml](06-03-pdf-classifier-components.puml)
* For classification decision logic, see [06-04-pdf-classification-decision.puml](06-04-pdf-classification-decision.puml)

## Navigation by Diagram Type

### Class/Component Structure Diagrams
* [01-01-pipeline-architecture.puml](01-01-pipeline-architecture.puml) - Overall architecture
* [02-01-classifier-diagram.puml](02-01-classifier-diagram.puml) - Classifier classes
* [03-01-formatter-class.puml](03-01-formatter-class.puml) - Formatter classes
* [04-01-verifier-class.puml](04-01-verifier-class.puml) - Verifier classes
* [05-01-schema-registry-class.puml](05-01-schema-registry-class.puml) - Schema registry classes
* [06-03-pdf-classifier-components.puml](06-03-pdf-classifier-components.puml) - PDF classifier components

### Flow Diagrams
* [01-02-complete-pipeline-flow.puml](01-02-complete-pipeline-flow.puml) - Overall flow
* [02-02-document-classifier-flow.puml](02-02-document-classifier-flow.puml) - Classification flow
* [03-02-formatter-flow.puml](03-02-formatter-flow.puml) - Formatting flow
* [04-02-verifier-flow.puml](04-02-verifier-flow.puml) - Verification flow
* [05-02-schema-registry-flow.puml](05-02-schema-registry-flow.puml) - Schema validation flow
* [06-04-pdf-classification-decision.puml](06-04-pdf-classification-decision.puml) - PDF classification decision flow

### Sequence Diagrams
* [06-02-pdf-processing-sequence.puml](06-02-pdf-processing-sequence.puml) - PDF processing sequence

### Use Case Diagrams
* [06-01-pdf-processing-usecase.puml](06-01-pdf-processing-usecase.puml) - PDF processing use cases

## Common Navigation Paths

### Development Focus
If you're developing or modifying code, follow these paths:

1. **New Component Development**:
   * Start with [01-01-pipeline-architecture.puml](01-01-pipeline-architecture.puml) to understand where your component fits
   * Look at similar component class diagrams (02-01, 03-01, 04-01, 05-01)
   * Review flow diagrams to understand runtime behavior

2. **Document Type Support**:
   * Start with [02-01-classifier-diagram.puml](02-01-classifier-diagram.puml) to understand classifier extension
   * Review [05-01-schema-registry-class.puml](05-01-schema-registry-class.puml) for schema registration
   * Check [06-04-pdf-classification-decision.puml](06-04-pdf-classification-decision.puml) for classification logic

### Operations Focus
If you're operating or configuring the system:

1. **System Configuration**:
   * Start with [01-01-pipeline-architecture.puml](01-01-pipeline-architecture.puml) for component overview
   * Look at [06-01-pdf-processing-usecase.puml](06-01-pdf-processing-usecase.puml) for user interactions
   
2. **Troubleshooting Issues**:
   * Start with [01-02-complete-pipeline-flow.puml](01-02-complete-pipeline-flow.puml) to see overall flow
   * Identify the problematic stage and refer to component-specific flow diagrams
   * For classification issues, check [06-04-pdf-classification-decision.puml](06-04-pdf-classification-decision.puml)

## Keeping the Diagrams Updated

When modifying the system architecture:

1. Identify the affected components and their corresponding diagrams
2. Update the diagrams to reflect the changes
3. Ensure cross-references in the diagrams remain accurate
4. Update this navigation guide if new diagrams are added or relationships change