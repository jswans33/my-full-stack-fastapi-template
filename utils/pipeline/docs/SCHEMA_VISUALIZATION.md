# Schema Visualization

This document explains how to use the schema visualization tools to explore and understand document schemas.

## Overview

The schema visualization tools allow you to:

1. Visualize the structure of document schemas
2. Compare schemas across different document types
3. Explore table patterns and structures
4. Analyze common features across schemas

## Prerequisites

The visualization tools require several Python packages:

```bash
pip install matplotlib numpy networkx scikit-learn seaborn pandas
```

For improved graph layouts, you may also want to install:

```bash
pip install pygraphviz
```

## Command-Line Usage

The `visualize_schema.py` script provides a command-line interface for schema visualization:

```bash
# List all available schemas
python -m utils.pipeline.visualize_schema list

# Generate cluster visualization (all schemas)
python -m utils.pipeline.visualize_schema clusters

# Generate feature comparison (all schemas)
python -m utils.pipeline.visualize_schema features

# Generate structure visualization for a specific schema
python -m utils.pipeline.visualize_schema structure <schema_id>

# Generate table pattern visualization for a specific schema
python -m utils.pipeline.visualize_schema tables <schema_id>

# Show help
python -m utils.pipeline.visualize_schema help
```

## Visualization Types

### Cluster Visualization

The cluster visualization uses t-SNE dimensionality reduction to plot schemas in a 2D space based on their similarity. Schemas that are more similar will appear closer together. This can help identify patterns and groupings across document types.

![Cluster Visualization Example](schema/data/visualizations/schema_clusters.png)

### Feature Comparison

The feature comparison creates a heatmap showing key features across schemas, such as:
- Number of metadata fields
- Section count
- Table count
- Average rows per table
- Maximum depth of section hierarchy
- Number of tables with headers

This visualization helps identify similarities and differences in schema structure.

![Feature Comparison Example](schema/data/visualizations/schema_features.png)

### Structure Visualization

The structure visualization creates a hierarchical graph showing the structure of a specific schema, including:
- Metadata fields
- Section hierarchy
- Table information

This visualization helps understand the organization of a specific document.

![Structure Visualization Example](schema/data/visualizations/structure_example.png)

### Table Pattern Visualization

The table pattern visualization provides insights into table structures within a schema:

1. **Table Size Distribution**: Shows the distribution of table sizes (rows per table)
2. **Table Size Categories**: Categorizes tables as small, medium, or large
3. **Common Headers**: Shows the most common table headers (if available)
4. **Column Count Distribution**: Shows the distribution of column counts
5. **Sample Table Data**: Displays a sample of actual table data (if available)

![Table Pattern Example](schema/data/visualizations/tables_example.png)

## Programmatic Usage

You can also use the visualization tools programmatically:

```python
from utils.pipeline.schema.extended_registry import ExtendedSchemaRegistry

# Initialize registry
registry = ExtendedSchemaRegistry()

# Generate visualizations
output_dir = "path/to/output/directory"

# Cluster visualization
registry.visualize("clusters", output_dir=output_dir)

# Feature comparison
registry.visualize("features", output_dir=output_dir)

# Structure visualization for a specific schema
registry.visualize("structure", ["schema_id"], output_dir=output_dir)

# Table pattern visualization for a specific schema
registry.visualize("tables", ["schema_id"], output_dir=output_dir)
```

## Enhanced Schema Data

The visualizations now take advantage of enhanced schema data, including:

- Actual metadata values (not just field names)
- Content samples from document sections
- Table headers and sample data
- Column counts and structure

This enhanced data provides more detailed and informative visualizations, especially for table patterns.

## Customizing Visualizations

You can customize the visualizations by modifying the `SchemaVisualizer` class in `utils/pipeline/schema/visualizer.py`. For example, you can:

- Change color schemes
- Adjust figure sizes
- Add new visualization types
- Modify existing visualizations

## Troubleshooting

If you encounter issues with the visualizations:

1. **Missing dependencies**: Ensure you have installed all required packages
2. **No schemas found**: Run the pipeline on some documents to generate schemas
3. **Visualization errors**: Check the error message for specific issues
4. **Empty visualizations**: Ensure the schemas contain the necessary data

## Configuration

The schema visualization tools use the same configuration as the pipeline. You can customize the visualization behavior by modifying the pipeline configuration.
