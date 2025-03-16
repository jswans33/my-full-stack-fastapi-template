# Pipeline Component Diagrams

This file contains detailed diagrams for key components of the pipeline system.

## Document Classifier Component

### Class Diagram

```

### Data Flow Diagram

```plantuml
' Configure PlantUML server
!define PLANTUML_SERVER_URL https://www.plantuml.com/plantuml

@startuml DocumentClassifier_DataFlow
!include <archimate/Archimate>

' Define components
rectangle "Document Data" as DocData
rectangle "Feature Extraction" as FeatureExtraction
rectangle "ClassifierFactory" as Factory
rectangle "Individual Classifiers" as Classifiers
rectangle "Rule-Based" as RuleBased
rectangle "Pattern Matcher" as PatternMatcher
rectangle "ML-Based" as MLBased
rectangle "Ensemble Manager" as Ensemble
rectangle "Classification Result" as Result

' Define data flow
DocData --> FeatureExtraction : "Raw document data"
FeatureExtraction --> Classifiers : "Extracted features"

Factory --> Classifiers : "Creates"

Classifiers --> RuleBased
Classifiers --> PatternMatcher
Classifiers --> MLBased

RuleBased --> Ensemble : "Rule classification result"
PatternMatcher --> Ensemble : "Pattern classification result"
MLBased --> Ensemble : "ML classification result"

Ensemble --> Result : "Final classification"

@enduml
```

## Formatter Component

### Class Diagram

```plantuml
' Configure PlantUML server
!define PLANTUML_SERVER_URL https://www.plantuml.com/plantuml

@startuml Formatter_ClassDiagram
skinparam classAttributeIconSize 0

enum OutputFormat {
  JSON
  MARKDOWN
  ENHANCED_MARKDOWN
}

class FormatterFactory {
  +{static} create_formatter(format: OutputFormat, config: Dict): Formatter
}

interface Formatter {
  {abstract} +format(data: Dict): Dict
  {abstract} +write(data: Dict, path: str)
}

class JSONFormatter {
  -config: Dict
  -logger: Logger
  +__init__(config: Dict)
  +format(data: Dict): Dict
  +write(data: Dict, path: str)
  -_prepare_json(data: Dict): Dict
}

class MarkdownFormatter {
  -config: Dict
  -logger: Logger
  +__init__(config: Dict)
  +format(data: Dict): Dict
  +write(data: Dict, path: str)
  -_generate_toc(data: Dict): str
  -_format_section(section: Dict, level: int): str
  -_format_table(table: Dict): str
}

class EnhancedMarkdownFormatter {
  -config: Dict
  -logger: Logger
  +__init__(config: Dict)
  +format(data: Dict): Dict
  +write(data: Dict, path: str)
  -_apply_templates(data: Dict): Dict
  -_format_enhanced_table(table: Dict): str
  -_add_metadata_section(data: Dict): str
}

FormatterFactory --> OutputFormat
FormatterFactory --> Formatter
Formatter <|-- JSONFormatter
Formatter <|-- MarkdownFormatter
MarkdownFormatter <|-- EnhancedMarkdownFormatter

@enduml
```

### Data Flow Diagram

```plantuml


## Verifier Component

### Class Diagram

```plantuml
' Configure PlantUML server
!define PLANTUML_SERVER_URL https://www.plantuml.com/plantuml

@startuml Verifier_ClassDiagram
skinparam classAttributeIconSize 0

enum VerifierType {
  JSON_TREE
  MARKDOWN
}

class VerifierFactory {
  +{static} create_verifier(type: VerifierType): Verifier
}

interface Verifier {
  {abstract} +verify(data: Dict): Tuple[bool, List, List]
}

class JSONTreeVerifier {
  -config: Dict
  -logger: Logger
  +__init__(config: Dict)
  +verify(data: Dict): Tuple[bool, List, List]
  -_verify_structure(data: Dict): List
  -_check_required_fields(data: Dict): List
  -_validate_types(data: Dict): List
}

class MarkdownVerifier {
  -config: Dict
  -logger: Logger
  +__init__(config: Dict)
  +verify(data: Dict): Tuple[bool, List, List]
  -_verify_markdown_structure(data: Dict): List
  -_check_headers(content: str): List
  -_validate_tables(content: str): List
}

VerifierFactory --> VerifierType
VerifierFactory --> Verifier
Verifier <|-- JSONTreeVerifier
Verifier <|-- MarkdownVerifier

@enduml
```

### Data Flow Diagram

```plantuml
' Configure PlantUML server
!define PLANTUML_SERVER_URL https://www.plantuml.com/plantuml

@startuml Verifier_DataFlow
!include <archimate/Archimate>

' Define components
rectangle "Formatted Output" as FormattedData
rectangle "Output Format" as Format
rectangle "VerifierFactory" as Factory
rectangle "Verifier Selection" as Selection
rectangle "JSON Tree Verifier" as JSONVerifier
rectangle "Markdown Verifier" as MDVerifier
rectangle "Verification Result" as Result
rectangle "Error Handling" as Error
rectangle "Final Output" as Output

' Define data flow
FormattedData --> Factory
Format --> Factory : "verifier_type"
Factory --> Selection

Selection --> JSONVerifier : "if JSON"
Selection --> MDVerifier : "if MARKDOWN/ENHANCED_MARKDOWN"

JSONVerifier --> Result : "verify()"
MDVerifier --> Result : "verify()"

Result --> Error : "if not valid"
Result --> Output : "if valid"

Error --> Output : "with error info"

@enduml
```

## Schema Registry Component

### Class Diagram

```plantuml
' Configure PlantUML server
!define PLANTUML_SERVER_URL https://www.plantuml.com/plantuml

@startuml SchemaRegistry_ClassDiagram
skinparam classAttributeIconSize 0

class SchemaRegistry {
  -config: Dict
  -logger: Logger
  -storage_dir: Path
  -schemas: Dict
  +__init__(config: Dict)
  +record(document_data: Dict, document_type: str, document_name: str): str
  +match(document_data: Dict): Tuple[str, float]
  +get_schema(schema_id: str): Dict
  +list_schemas(document_type: str): List[Dict]
  -_get_storage_dir(): Path
  -_ensure_storage_dir()
  -_load_schemas(): Dict
  -_save_schema(schema_id: str, schema: Dict)
  -_extract_schema(document_data: Dict): Dict
  -_extract_content_structure(content: List): List
  -_extract_enhanced_table_structure(tables: List): List
  -_generate_schema_id(document_type: str): str
  -_calculate_match_confidence(schema1: Dict, schema2: Dict): float
}

class ExtendedSchemaRegistry {
  +__init__(config: Dict)
  +analyze(document_type: str): Dict
  +compare(schema_id1: str, schema_id2: str): Dict
  +visualize(viz_type: str, output_dir: str): str
  -_analyze_schemas(schemas: List): Dict
  -_compare_schemas(schema1: Dict, schema2: Dict): Dict
  -_generate_visualization(schemas: List, viz_type: str): str
}

class SchemaVisualizer {
  -config: Dict
  -logger: Logger
  +__init__(config: Dict)
  +generate_cluster_visualization(schemas: List, output_path: str): str
  +generate_feature_visualization(schemas: List, output_path: str): str
  +generate_structure_visualization(schema: Dict, output_path: str): str
  +generate_tables_visualization(schema: Dict, output_path: str): str
}

class SchemaMigrator {
  -config: Dict
  -logger: Logger
  +__init__(config: Dict)
  +migrate_schema(schema: Dict, from_version: str, to_version: str): Dict
  +apply_migration(schema: Dict, migration: Dict): Dict
  +detect_schema_version(schema: Dict): str
  -_load_migration(from_version: str, to_version: str): Dict
}

SchemaRegistry <|-- ExtendedSchemaRegistry
ExtendedSchemaRegistry --> SchemaVisualizer
SchemaRegistry --> SchemaMigrator

@enduml
```

### Data Flow Diagram

```plantuml
' Configure PlantUML server
!define PLANTUML_SERVER_URL https://www.plantuml.com/plantuml

@startuml SchemaRegistry_DataFlow
!include <archimate/Archimate>

' Define components
rectangle "Document Data" as DocData
rectangle "Schema Registry" as Registry
rectangle "Schema Extraction" as Extraction
rectangle "Schema Storage" as Storage
database "Schema Database" as DB
rectangle "Schema Matching" as Matching
rectangle "Schema Visualization" as Visualization
rectangle "Schema Migration" as Migration
rectangle "Schema Analysis" as Analysis

' Define data flow paths
DocData --> Registry : "record()"
Registry --> Extraction : "extract schema"
Extraction --> Storage : "save schema"
Storage --> DB : "write to disk"

DocData --> Registry : "match()"
Registry --> DB : "load schemas"
DB --> Matching : "compare schemas"
Matching --> DocData : "match result"

Registry --> Analysis : "analyze()"
DB --> Analysis
Analysis --> Visualization : "visualize()"

DB --> Migration : "migrate schema"
Migration --> DB : "update schema"

@enduml
```

## Complete Pipeline Data Flow

```plantuml
' Configure PlantUML server
!define PLANTUML_SERVER_URL https://www.plantuml.com/plantuml

@startuml Pipeline_CompleteDataFlow
!include <archimate/Archimate>

rectangle "Input Document" as Input
rectangle "Pipeline" as Pipeline
rectangle "Document Type Detection" as TypeDetection
rectangle "Strategy Selection" as StrategySelection
rectangle "Document Analysis" as Analysis
rectangle "Content Cleaning" as Cleaning
rectangle "Data Extraction" as Extraction
rectangle "Data Validation" as Validation
rectangle "Document Classification" as Classification
rectangle "Schema Registry" as SchemaRegistry
rectangle "Output Formatting" as Formatting
rectangle "Output Verification" as Verification
rectangle "Output Generation" as Output

Input --> Pipeline
Pipeline --> TypeDetection
TypeDetection --> StrategySelection
StrategySelection --> Analysis
Analysis --> Cleaning
Cleaning --> Extraction
Extraction --> Validation
Validation --> Classification
Classification --> SchemaRegistry : "match/record schema"
SchemaRegistry --> Classification : "schema info"
Classification --> Formatting
Formatting --> Verification
Verification --> Output

@enduml
```

These diagrams provide a detailed view of the key components in the pipeline system, illustrating their structure and data flows. The class diagrams show the relationships between classes, while the data flow diagrams illustrate how data moves through each component.