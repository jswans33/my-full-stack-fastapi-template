
# Pipeline Architecture Diagrams

This folder contains architectural diagrams for the utils/pipeline system. Each diagram is stored in its own file for better organization and usability.

## Documentation Overview

To understand the pipeline architecture, consult these documentation files:

- **[ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)**: Comprehensive overview of the pipeline architecture and its components
- **[DOCUMENT_FLOW_GUIDE.md](DOCUMENT_FLOW_GUIDE.md)**: Detailed explanation of how documents flow through the pipeline
- **[DIAGRAM_NAVIGATION_GUIDE.md](DIAGRAM_NAVIGATION_GUIDE.md)**: Guide for navigating between related diagrams based on your goals

## Diagram Numbering System

The diagrams follow a structured numbering system to indicate their place in the overall architecture:

- **01-XX**: Overall pipeline architecture diagrams
- **02-XX**: Document classifier component diagrams
- **03-XX**: Formatter component diagrams
- **04-XX**: Verifier component diagrams
- **05-XX**: Schema registry component diagrams
- **06-XX**: PDF document processing diagrams
- **07-XX**: Schema analysis and visualization diagrams

Within each category, the numbering further breaks down by diagram type:
- **XX-01**: Class/component structure diagrams
- **XX-02**: Flow/sequence diagrams
- **XX-03, XX-04, etc.**: Additional specialized diagrams

## Diagram Files

### 1. Overall Architecture

- **[01-01-pipeline-architecture.puml](01-01-pipeline-architecture.puml)**: High-level component diagram showing the main components of the pipeline and their relationships
- **[01-02-complete-pipeline-flow.puml](01-02-complete-pipeline-flow.puml)**: Data flow diagram showing how data moves through the entire pipeline process

### 2. Document Classifier Component

- **[02-01-classifier-diagram.puml](02-01-classifier-diagram.puml)**: Class diagram showing the structure of the document classification system
- **[02-02-document-classifier-flow.puml](02-02-document-classifier-flow.puml)**: Data flow diagram showing how documents are classified
- **[02-03-document-classifier-diagram.puml](02-03-document-classifier-diagram.puml)**: Simple component diagram showing document classifier architecture

### 3. Formatter Component

- **[03-01-formatter-class.puml](03-01-formatter-class.puml)**: Class diagram showing the structure of the output formatting system
- **[03-02-formatter-flow.puml](03-02-formatter-flow.puml)**: Data flow diagram showing how data is formatted into different output formats

### 4. Verifier Component

- **[04-01-verifier-class.puml](04-01-verifier-class.puml)**: Class diagram showing the structure of the output verification system
- **[04-02-verifier-flow.puml](04-02-verifier-flow.puml)**: Data flow diagram showing how output is verified

### 5. Schema Registry Component

- **[05-01-schema-registry-class.puml](05-01-schema-registry-class.puml)**: Class diagram showing the structure of the schema registry system
- **[05-02-schema-registry-flow.puml](05-02-schema-registry-flow.puml)**: Data flow diagram showing schema matching and recording

### 6. PDF Document Processing

- **[06-01-pdf-processing-usecase.puml](06-01-pdf-processing-usecase.puml)**: Use case diagram showing the various ways users interact with the PDF processing pipeline
- **[06-02-pdf-processing-sequence.puml](06-02-pdf-processing-sequence.puml)**: Sequence diagram illustrating the step-by-step process of PDF document extraction and classification
- **[06-03-pdf-classifier-components.puml](06-03-pdf-classifier-components.puml)**: Component diagram showing the detailed architecture of the PDF document classifier
- **[06-04-pdf-classification-decision.puml](06-04-pdf-classification-decision.puml)**: Activity diagram depicting the decision logic used in PDF document classification

### 7. Schema Analysis and Visualization

- **[07-01-schema-analyzer-class.puml](07-01-schema-analyzer-class.puml)**: Class diagram showing the structure of the schema analyzer system
- **[07-02-schema-analyzer-flow.puml](07-02-schema-analyzer-flow.puml)**: Data flow diagram showing how schema analysis works
- **[07-03-schema-visualizer-class.puml](07-03-schema-visualizer-class.puml)**: Class diagram showing the structure of the schema visualizer system
- **[07-04-schema-visualizer-flow.puml](07-04-schema-visualizer-flow.puml)**: Data flow diagram showing how schema visualization works
- **[07-05-complete-analysis-visualization-flow.puml](07-05-complete-analysis-visualization-flow.puml)**: End-to-end workflow showing how analysis and visualization components interact
- **[07-06-schema-analysis-usage.puml](07-06-schema-analysis-usage.puml)**: Use case diagram showing how different users interact with the schema analysis system
- **[07-07-schema-visualization-usage.puml](07-07-schema-visualization-usage.puml)**: Use case diagram showing how different users interact with the visualization system

## How to View the Diagrams

### Using VS Code with PlantUML Extension

1. Install the PlantUML extension for VS Code
2. Configure the PlantUML server in your VS Code settings:
   ```json
   {
     "plantuml.server": "https://www.plantuml.com/plantuml",
     "plantuml.render": "PlantUMLServer"
   }
   ```
3. Open a diagram file
4. Right-click and select "PlantUML: Preview Current Diagram" or use Alt+D

### Using Online PlantUML Server

1. Copy the content of any diagram file
2. Visit [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
3. Paste the content and view the rendered diagram

## Architectural Patterns

The diagrams illustrate the consistent use of several design patterns across the pipeline components:

1. **Strategy Pattern**: Different interchangeable algorithms for document processing
2. **Factory Pattern**: Creation of concrete implementations without tight coupling
3. **Dependency Injection**: Components receive their dependencies rather than create them
4. **Abstract Interfaces**: Components program to interfaces, not implementations

This architecture allows the system to be easily extended with new document types, processing strategies, classifiers, formatters, and verifiers.

## Diagram Update Guidelines

When updating the architecture:

1. Follow the existing numbering convention for any new diagrams
2. Update cross-references in related diagrams
3. Maintain consistent styling and notation
4. Update the documentation files to reflect architectural changes
5. Add cross-references to related diagrams in comments or notes
