# Schema Analysis and Visualization

The pipeline now includes schema analysis and visualization capabilities that can help you understand document patterns and relationships.

## Overview

Schema analysis examines the structure and patterns of document schemas to:

1. Identify common patterns across document types
2. Compare schemas to find similarities and differences
3. Visualize relationships between schemas
4. Extract insights about document structures

## Components

The schema analysis system consists of the following components:

### 1. Schema Analyzer

Located in `utils/pipeline/schema/analyzer.py`, this component:
- Analyzes schemas to extract patterns and insights
- Compares schemas to identify similarities and differences
- Clusters similar schemas together

### 2. Schema Vectorizer

Located in `utils/pipeline/schema/vectorizer.py`, this component:
- Converts schemas to numerical feature vectors
- Extracts features from schema structure and content
- Enables mathematical comparison of schemas

### 3. Schema Visualizer

Located in `utils/pipeline/schema/visualizer.py`, this component:
- Generates visualizations of schema patterns
- Creates cluster visualizations using dimensionality reduction
- Visualizes schema structure and features

### 4. Extended Schema Registry

Located in `utils/pipeline/schema/extended_registry.py`, this component:
- Extends the base SchemaRegistry with analysis capabilities
- Provides a unified interface for schema analysis and visualization

## Usage

### Example Script

The easiest way to use the schema analysis functionality is through the example script:

```bash
python -m utils.pipeline.examples.schema_analysis_example
```

This script will:
1. Load all available schemas
2. Analyze schema patterns
3. Display analysis results
4. Generate visualizations
5. Compare schemas

### Programmatic Usage

You can also use the schema analysis functionality programmatically:

```python
from utils.pipeline.schema.extended_registry import ExtendedSchemaRegistry

# Initialize registry
registry = ExtendedSchemaRegistry()

# Analyze schemas
analysis = registry.analyze()
print(f"Found {analysis['schema_count']} schemas")

# Compare schemas
schema_id1 = "form_20250314221847"
schema_id2 = "form_20250314221900"
comparison = registry.compare(schema_id1, schema_id2)
print(f"Similarity: {comparison['overall_similarity']:.2f}")

# Generate visualizations
viz_path = registry.visualize("clusters")
print(f"Visualization saved to: {viz_path}")
```

## Visualization Types

The system supports several types of visualizations:

1. **Clusters**: Visualizes relationships between schemas using dimensionality reduction
2. **Features**: Creates a heatmap comparing features across schemas
3. **Structure**: Visualizes the hierarchical structure of a schema
4. **Tables**: Visualizes table patterns in a schema

## Analysis Results

The schema analysis provides the following information:

1. **Document Types**: Distribution of document types in the registry
2. **Common Metadata**: Frequency of metadata fields across schemas
3. **Table Patterns**: Statistics about table usage and structure
4. **Section Patterns**: Statistics about section usage and structure

## Dependencies

The schema analysis functionality requires the following dependencies:

- **matplotlib**: For creating visualizations
- **numpy**: For numerical operations
- **scikit-learn**: For dimensionality reduction (optional, for cluster visualization)
- **networkx**: For graph visualization (optional, for structure visualization)
- **seaborn**: For enhanced visualizations (optional, for feature visualization)
- **pandas**: For data manipulation (optional, for feature visualization)

You can install these dependencies with:

```bash
pip install matplotlib numpy scikit-learn networkx seaborn pandas
```

## Extending the System

### Adding New Features

To add new features to the vectorization:

1. Update `SchemaVectorizer.vectorize_schema()` to extract the new features
2. Update `SchemaVectorizer.get_feature_names()` to include the new feature names

### Adding New Visualizations

To add new visualization types:

1. Add a new method to `SchemaVisualizer` for the visualization
2. Update `SchemaVisualizer.visualize()` to support the new visualization type
