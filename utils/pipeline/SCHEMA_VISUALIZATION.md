# Schema Visualization Guide

This guide explains how to use the schema visualization functionality in the Document Pipeline Tool. The schema visualization features allow you to generate visual representations of document schemas, helping you understand document structures, compare schemas, and identify patterns.

## Overview

The schema visualization system provides several types of visualizations:

1. **Clusters**: Visualizes schema similarity using dimensionality reduction (t-SNE)
2. **Features**: Generates a heatmap comparing features across schemas
3. **Structure**: Creates a hierarchical graph visualization of a schema's structure
4. **Tables**: Visualizes table patterns and distributions within a schema

These visualizations help you:
- Understand document structure patterns
- Compare different document types
- Identify similarities between schemas
- Analyze table usage patterns
- Explore document hierarchies

## Prerequisites

The visualization functionality requires several Python packages:

```bash
# Basic visualization dependencies
uv pip install matplotlib

# For cluster visualization
uv pip install scikit-learn

# For feature visualization
uv pip install seaborn pandas

# For structure visualization
uv pip install networkx

# For better structure layout (optional but recommended)
uv pip install pygraphviz

# Install all visualization dependencies
uv pip install matplotlib scikit-learn seaborn pandas networkx pygraphviz
```

Note: Installing `pygraphviz` requires system-level dependencies:
- On Windows: Install Graphviz using Chocolatey: `choco install graphviz`
- On macOS: Install Graphviz using Homebrew: `brew install graphviz`
- On Linux: Install Graphviz using your package manager: `apt-get install graphviz` or `yum install graphviz`

## Using the Visualization Script

The `visualize_schema.py` script provides a command-line interface for generating visualizations:

```bash
python visualize_schema.py <visualization_type> <schema_id>
```

Where:
- `<visualization_type>`: One of `clusters`, `features`, `structure`, or `tables`
- `<schema_id>`: ID of the schema to visualize (not required for `clusters` visualization)

### Output Location

Visualizations are saved to:
```
utils/pipeline/schema/data/visualizations/
```

The script will create this directory if it doesn't exist.

## Visualization Types

### Cluster Visualization

The cluster visualization uses t-SNE dimensionality reduction to plot schemas in a 2D space, showing similarities between schemas. Similar schemas appear closer together.

```bash
# Visualize all schemas as clusters
python visualize_schema.py clusters all
```

This visualization is useful for:
- Identifying groups of similar documents
- Finding outliers in your document collection
- Visualizing document type distributions

### Feature Visualization

The feature visualization creates a heatmap comparing various features across schemas, such as metadata field count, section count, table count, etc.

```bash
# Visualize features for all schemas
python visualize_schema.py features all

# Visualize features for specific schemas
python visualize_schema.py features invoice_20250314
```

This visualization is useful for:
- Comparing schema characteristics
- Identifying patterns across document types
- Analyzing feature distributions

### Structure Visualization

The structure visualization creates a hierarchical graph showing the structure of a specific schema, including sections, subsections, and tables.

```bash
# Visualize the structure of a specific schema
python visualize_schema.py structure invoice_20250314
```

This visualization is useful for:
- Understanding document hierarchies
- Analyzing section relationships
- Exploring document organization

### Table Visualization

The table visualization shows patterns in table usage within a schema, including distributions of table sizes and row counts.

```bash
# Visualize table patterns for a specific schema
python visualize_schema.py tables invoice_20250314
```

This visualization is useful for:
- Analyzing table size distributions
- Understanding table usage patterns
- Identifying complex tables

## Examples

### Example 1: Visualizing Schema Clusters

To visualize how your schemas relate to each other:

```bash
python visualize_schema.py clusters all
```

This will generate a 2D plot where each point represents a schema. Schemas with similar structures will appear closer together. Different document types are represented by different colors.

The output will be saved to:
```
utils/pipeline/schema/data/visualizations/schema_clusters.png
```

### Example 2: Comparing Schema Features

To compare features across multiple schemas:

```bash
python visualize_schema.py features all
```

This will generate a heatmap showing various features for each schema, such as metadata field count, section count, table count, etc.

The output will be saved to:
```
utils/pipeline/schema/data/visualizations/schema_features.png
```

### Example 3: Visualizing a Schema's Structure

To visualize the structure of a specific schema:

```bash
# First, list available schemas
python -c "from utils.pipeline.schema.registry import SchemaRegistry; print('\n'.join([s['id'] for s in SchemaRegistry().list_schemas()]))"

# Then visualize a specific schema
python visualize_schema.py structure invoice_20250314
```

This will generate a hierarchical graph showing the structure of the schema, including sections, subsections, and tables.

The output will be saved to:
```
utils/pipeline/schema/data/visualizations/structure_invoice_20250314.png
```

### Example 4: Analyzing Table Patterns

To analyze table patterns in a specific schema:

```bash
python visualize_schema.py tables invoice_20250314
```

This will generate visualizations showing table size distributions and patterns.

The output will be saved to:
```
utils/pipeline/schema/data/visualizations/tables_invoice_20250314.png
```

## Programmatic Usage

You can also use the visualization functionality programmatically in your Python code:

```python
from utils.pipeline.schema.extended_registry import ExtendedSchemaRegistry

# Initialize registry
registry = ExtendedSchemaRegistry()

# Generate visualization
viz_path = registry.visualize(
    visualization_type="clusters",  # or "features", "structure", "tables"
    schema_ids=["invoice_20250314"],  # Optional for "clusters" and "features"
    output_dir="path/to/output"  # Optional
)

print(f"Visualization saved to: {viz_path}")
```

## Troubleshooting

### Missing Dependencies

If you encounter errors about missing modules, install the required dependencies:

```bash
uv pip install matplotlib scikit-learn seaborn pandas networkx
```

### Low Perplexity Error in t-SNE

If you see an error about perplexity being too high for the number of samples:

```
ValueError: perplexity must be less than n_samples
```

This means you don't have enough schemas for the default perplexity value. The code should automatically adjust the perplexity, but if you encounter this error, you need to add more schemas before using the cluster visualization.

### Graphviz Not Found

If you see an error about Graphviz not being found:

```
ImportError: No module named 'pygraphviz'
```

or

```
GraphViz's executables not found
```

Install Graphviz and pygraphviz:

```bash
# Install system-level Graphviz
# Windows (with Chocolatey)
choco install graphviz

# macOS (with Homebrew)
brew install graphviz

# Linux
apt-get install graphviz  # Debian/Ubuntu
yum install graphviz      # CentOS/RHEL

# Then install pygraphviz
uv pip install pygraphviz
```

### No Schemas Available

If you see a message like:

```
No schemas available for visualization
```

You need to record some schemas first. Use the `SchemaRegistry.record()` method to record document schemas.

## Advanced Usage

### Customizing Visualizations

You can customize visualizations by modifying the `SchemaVisualizer` class in `utils/pipeline/schema/visualizer.py`. For example, you can change colors, plot sizes, or add additional visualization types.

### Adding New Visualization Types

To add a new visualization type:

1. Add a new method to the `SchemaVisualizer` class
2. Update the `visualize` method to handle the new type
3. Update the `visualize_schema.py` script to include the new type in the usage message

### Batch Processing

To generate visualizations for multiple schemas at once:

```python
from utils.pipeline.schema.extended_registry import ExtendedSchemaRegistry
import os

registry = ExtendedSchemaRegistry()
schemas = registry.list_schemas()
output_dir = os.path.join("utils", "pipeline", "schema", "data", "visualizations")

# Generate structure visualizations for all schemas
for schema in schemas:
    schema_id = schema["id"]
    registry.visualize("structure", [schema_id], output_dir)
    print(f"Generated structure visualization for {schema_id}")
```

## Further Reading

For more information about the schema registry and related functionality, see:

- `utils/pipeline/schema/registry.py`: Base schema registry implementation
- `utils/pipeline/schema/extended_registry.py`: Extended registry with visualization
- `utils/pipeline/schema/visualizer.py`: Schema visualization implementation
- `utils/pipeline/schema/vectorizer.py`: Schema vectorization for analysis
