"""
Schema visualizer module.

This module provides functionality for visualizing document schemas.
"""

import os
from typing import Any, Dict, List, Optional, Union

from utils.pipeline.utils.logging import get_logger


class SchemaVisualizer:
    """
    Visualizes document schemas.

    This class provides functionality for:
    1. Generating visualizations of schema patterns
    2. Creating cluster visualizations using dimensionality reduction
    3. Visualizing schema structure and features
    """

    def __init__(self, registry, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the schema visualizer.

        Args:
            registry: Schema registry instance
            config: Configuration dictionary for the visualizer
        """
        self.registry = registry
        self.config = config or {}
        self.logger = get_logger(__name__)

    def visualize(
        self,
        visualization_type: str = "clusters",
        schema_ids: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
    ) -> Union[str, List[str]]:
        """
        Generate visualizations for schemas.

        Args:
            visualization_type: Type of visualization to generate
                - "clusters": Cluster visualization using dimensionality reduction
                - "features": Feature heatmap comparison
                - "structure": Hierarchical structure visualization
                - "tables": Table pattern visualization
            schema_ids: List of schema IDs to visualize, or None for all/automatic
            output_dir: Directory to save visualizations, or None for default

        Returns:
            Path(s) to the generated visualization(s)
        """
        # Set up output directory
        if not output_dir:
            # Use a default directory relative to the schema storage directory
            try:
                from utils.pipeline.schema.registry import SchemaRegistry

                registry_instance = SchemaRegistry()
                base_dir = os.path.dirname(registry_instance.storage_dir)
                output_dir = os.path.join(base_dir, "visualizations")
            except Exception:
                # Fallback to a relative path
                output_dir = os.path.join(
                    "utils", "pipeline", "schema", "data", "visualizations"
                )

        os.makedirs(output_dir, exist_ok=True)

        # Generate visualization based on type
        try:
            if visualization_type == "clusters":
                output_path = os.path.join(output_dir, "schema_clusters.png")
                return self.visualize_schema_clusters(output_path)

            elif visualization_type == "features":
                output_path = os.path.join(output_dir, "schema_features.png")
                return self.visualize_schema_features(schema_ids, output_path)

            elif visualization_type == "structure":
                if not schema_ids or len(schema_ids) == 0:
                    # Use first schema if none specified
                    schemas = self.registry.list_schemas()
                    if not schemas:
                        return "No schemas available for visualization"
                    schema_ids = [schemas[0]["id"]]

                # Generate structure visualization for each schema
                output_paths = []
                for schema_id in schema_ids:
                    output_path = os.path.join(output_dir, f"structure_{schema_id}.png")
                    result = self.visualize_schema_structure(schema_id, output_path)
                    output_paths.append(result)

                return output_paths

            elif visualization_type == "tables":
                if not schema_ids or len(schema_ids) == 0:
                    # Use first schema if none specified
                    schemas = self.registry.list_schemas()
                    if not schemas:
                        return "No schemas available for visualization"
                    schema_ids = [schemas[0]["id"]]

                # Generate table visualization for each schema
                output_paths = []
                for schema_id in schema_ids:
                    output_path = os.path.join(output_dir, f"tables_{schema_id}.png")
                    result = self.visualize_table_patterns(schema_id, output_path)
                    output_paths.append(result)

                return output_paths

            else:
                return f"Unknown visualization type: {visualization_type}"
        except ImportError as e:
            return f"Error: Missing dependency - {str(e)}"
        except Exception as e:
            self.logger.error(
                f"Error generating visualization: {str(e)}", exc_info=True
            )
            return f"Error generating visualization: {str(e)}"

    def visualize_schema_clusters(self, output_path: str) -> str:
        """
        Visualize schema clusters using dimensionality reduction.

        Args:
            output_path: Path to save the visualization

        Returns:
            Path to the saved visualization
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            # Check if we have scikit-learn for dimensionality reduction
            try:
                from sklearn.manifold import TSNE
            except ImportError:
                return "Error: scikit-learn is required for cluster visualization. Please install it with 'pip install scikit-learn'."

            # Get all schemas
            schemas = self.registry.list_schemas()
            if len(schemas) < 2:
                return "Not enough schemas for cluster visualization (need at least 2)"

            # Extract schema IDs and document types
            schema_ids = [
                schema.get("id", f"schema_{i}") for i, schema in enumerate(schemas)
            ]
            doc_types = [schema.get("document_type", "UNKNOWN") for schema in schemas]

            # Vectorize schemas
            from utils.pipeline.schema.vectorizer import SchemaVectorizer

            vectorizer = SchemaVectorizer()
            vectors = [vectorizer.vectorize_schema(schema) for schema in schemas]

            # Convert to numpy array
            vectors = np.array(vectors)

            # Apply t-SNE for dimensionality reduction
            # Use a lower perplexity value (default is 30) that's less than n_samples
            perplexity = min(5, len(vectors) - 1)  # Ensure perplexity < n_samples
            tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
            vectors_2d = tsne.fit_transform(vectors)

            # Create plot
            plt.figure(figsize=(12, 8))

            # Get unique document types for coloring
            unique_types = list(set(doc_types))
            # Create colors for each document type
            color_indices = np.linspace(0, 1, len(unique_types))

            # Plot each schema with different colors by document type

            # Plot each schema
            for i, (x, y) in enumerate(vectors_2d):
                doc_type = doc_types[i]
                color_idx = unique_types.index(doc_type)
                # Use a basic color cycle with simple colors
                colors = [
                    "red",
                    "blue",
                    "green",
                    "orange",
                    "purple",
                    "cyan",
                    "magenta",
                    "yellow",
                ]
                color = colors[color_idx % len(colors)]
                plt.scatter(x, y, color=color, s=100, alpha=0.7)
                plt.text(x, y, schema_ids[i], fontsize=9)

            # Define colors for legend
            colors = [
                "red",
                "blue",
                "green",
                "orange",
                "purple",
                "cyan",
                "magenta",
                "yellow",
            ]
            for i, doc_type in enumerate(unique_types):
                plt.scatter([], [], color=colors[i % len(colors)], label=doc_type)
            plt.legend()

            plt.title("Schema Similarity Map")
            plt.xlabel("Dimension 1")
            plt.ylabel("Dimension 2")
            plt.tight_layout()

            # Save figure
            plt.savefig(output_path, dpi=300)
            plt.close()

            return output_path
        except Exception as e:
            self.logger.error(
                f"Error visualizing schema clusters: {str(e)}", exc_info=True
            )
            return f"Error visualizing schema clusters: {str(e)}"

    def visualize_schema_features(
        self,
        schema_ids: Optional[List[str]] = None,
        output_path: str = "schema_features.png",
    ) -> str:
        """
        Visualize schema features as a heatmap.

        Args:
            schema_ids: List of schema IDs to visualize, or None for all schemas
            output_path: Path to save the visualization

        Returns:
            Path to the saved visualization
        """
        try:
            import matplotlib.pyplot as plt

            # Check if we have seaborn for heatmap
            try:
                import seaborn as sns
            except ImportError:
                return "Error: seaborn is required for feature visualization. Please install it with 'pip install seaborn'."

            # Get schemas to visualize
            if schema_ids:
                schemas = [
                    self.registry.get_schema(schema_id) for schema_id in schema_ids
                ]
                schemas = [s for s in schemas if s]  # Filter out None values
            else:
                schemas = self.registry.list_schemas()

            if not schemas:
                return "No schemas found for visualization"

            # Define features to extract
            features = [
                ("Metadata Fields", lambda s: len(s.get("metadata_fields", []))),
                ("Section Count", lambda s: s.get("section_count", 0)),
                ("Table Count", lambda s: s.get("table_count", 0)),
                (
                    "Avg Rows/Table",
                    lambda s: sum(
                        t.get("row_count", 0) for t in s.get("table_structure", [])
                    )
                    / max(1, s.get("table_count", 0)),
                ),
                (
                    "Max Depth",
                    lambda s: self._calculate_max_depth(s.get("content_structure", [])),
                ),
                (
                    "Tables with Headers",
                    lambda s: sum(
                        1
                        for t in s.get("table_structure", [])
                        if t.get("has_headers", False)
                    ),
                ),
            ]

            # Extract feature values
            feature_names = [f[0] for f in features]
            data = []

            for schema in schemas:
                schema_id = schema.get("id", "unknown")
                row = [schema_id]
                for _, feature_func in features:
                    row.append(feature_func(schema))
                data.append(row)

            # Create DataFrame
            try:
                import pandas as pd

                df = pd.DataFrame(data, columns=["Schema ID"] + feature_names)
                df = df.set_index("Schema ID")

                # Normalize data for heatmap
                df_norm = (df - df.min()) / (df.max() - df.min())

                # Create plot
                plt.figure(figsize=(12, max(8, len(schemas) * 0.4)))
                sns.heatmap(
                    df_norm,
                    annot=df.round(1),
                    fmt=".1f",
                    cmap="YlGnBu",
                    linewidths=0.5,
                    cbar_kws={"label": "Normalized Value"},
                )

                plt.title("Schema Feature Comparison")
                plt.tight_layout()

                # Save figure
                plt.savefig(output_path, dpi=300, bbox_inches="tight")
                plt.close()

                return output_path
            except ImportError:
                return "Error: pandas is required for feature visualization. Please install it with 'pip install pandas'."
        except Exception as e:
            self.logger.error(
                f"Error visualizing schema features: {str(e)}", exc_info=True
            )
            return f"Error visualizing schema features: {str(e)}"

    def visualize_schema_structure(self, schema_id: str, output_path: str) -> str:
        """
        Visualize the hierarchical structure of a schema.

        Args:
            schema_id: ID of the schema to visualize
            output_path: Path to save the visualization

        Returns:
            Path to the saved visualization
        """
        try:
            import matplotlib.pyplot as plt

            # Check if we have networkx for graph visualization
            try:
                import networkx as nx
            except ImportError:
                return "Error: networkx is required for structure visualization. Please install it with 'pip install networkx'."

            schema = self.registry.get_schema(schema_id)
            if not schema:
                return f"Schema {schema_id} not found"

            # Create directed graph
            G = nx.DiGraph()

            # Add root node
            root_name = f"{schema_id}\n({schema.get('document_type', 'UNKNOWN')})"
            G.add_node(root_name)

            # Add metadata node
            metadata_fields = schema.get("metadata_fields", [])
            if metadata_fields:
                metadata_name = f"Metadata\n({len(metadata_fields)} fields)"
                G.add_node(metadata_name)
                G.add_edge(root_name, metadata_name)

            # Add content structure
            content_structure = schema.get("content_structure", [])
            if content_structure:
                self._add_structure_to_graph(G, root_name, content_structure, "Section")

            # Add tables
            table_structure = schema.get("table_structure", [])
            if table_structure:
                tables_name = f"Tables\n({len(table_structure)} tables)"
                G.add_node(tables_name)
                G.add_edge(root_name, tables_name)

                # Add individual tables (limit to first 10 to avoid overcrowding)
                for i, table in enumerate(table_structure[:10]):
                    table_name = f"Table {i + 1}\n({table.get('row_count', 0)} rows)"
                    G.add_node(table_name)
                    G.add_edge(tables_name, table_name)

                # Add ellipsis if more tables
                if len(table_structure) > 10:
                    G.add_node("...")
                    G.add_edge(tables_name, "...")

            # Create plot
            plt.figure(figsize=(12, 8))

            # Check if we have pygraphviz for better layout
            try:
                pos = nx.drawing.nx_agraph.graphviz_layout(G, prog="dot")
            except (ImportError, Exception):
                # Fall back to spring layout
                pos = nx.spring_layout(G, seed=42)

            # Draw nodes and edges
            nx.draw(
                G,
                pos,
                with_labels=True,
                node_size=3000,
                node_color="lightblue",
                font_size=10,
                font_weight="bold",
                arrows=True,
            )

            plt.title(f"Schema Structure: {schema_id}")
            plt.tight_layout()

            # Save figure
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()

            return output_path
        except Exception as e:
            self.logger.error(
                f"Error visualizing schema structure: {str(e)}", exc_info=True
            )
            return f"Error visualizing schema structure: {str(e)}"

    def visualize_table_patterns(
        self, schema_id: str, output_path: str
    ) -> Union[str, List[str]]:
        """
        Visualize table patterns in a schema with enhanced information.

        Args:
            schema_id: ID of the schema to visualize
            output_path: Path to save the visualization

        Returns:
            Path(s) to the saved visualization(s)
        """
        try:
            from collections import Counter

            import matplotlib.pyplot as plt
            import numpy as np

            schema = self.registry.get_schema(schema_id)
            if not schema:
                return f"Schema {schema_id} not found"

            # Check if we have the enhanced schema structure with table_samples
            table_samples = schema.get("table_samples", [])
            if table_samples:
                # Use enhanced table samples
                tables_to_visualize = table_samples
                self.logger.info(f"Using enhanced table samples for schema {schema_id}")
            else:
                # Fall back to old structure
                table_structure = schema.get("table_structure", [])
                if not table_structure:
                    return f"No tables found in schema {schema_id}"
                tables_to_visualize = table_structure
                self.logger.info(f"Using legacy table structure for schema {schema_id}")

            if not tables_to_visualize:
                return f"No tables found in schema {schema_id}"

            # Extract row counts
            row_counts = [table.get("row_count", 0) for table in tables_to_visualize]

            # Create base directory for visualizations
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)

            # List to store all output paths
            output_paths = [output_path]

            # Create histogram
            plt.figure(figsize=(12, 6))

            # Plot histogram of row counts
            plt.subplot(1, 2, 1)
            plt.hist(row_counts, bins=10, color="skyblue", edgecolor="black")
            plt.title("Distribution of Table Sizes")
            plt.xlabel("Rows per Table")
            plt.ylabel("Number of Tables")

            # Plot table size categories
            plt.subplot(1, 2, 2)
            categories = ["Small (<5 rows)", "Medium (5-15 rows)", "Large (>15 rows)"]
            counts = [
                sum(1 for rc in row_counts if rc < 5),
                sum(1 for rc in row_counts if 5 <= rc <= 15),
                sum(1 for rc in row_counts if rc > 15),
            ]

            plt.bar(categories, counts, color=["lightblue", "skyblue", "steelblue"])
            plt.title("Table Size Categories")
            plt.ylabel("Number of Tables")
            plt.xticks(rotation=45, ha="right")

            plt.suptitle(f"Table Patterns in Schema: {schema_id}")
            plt.tight_layout()

            # Save figure
            plt.savefig(output_path, dpi=300)
            plt.close()

            # Create additional visualizations if enhanced data is available

            # 1. Table Headers Visualization
            if any(
                "headers" in table and table["headers"] for table in tables_to_visualize
            ):
                # Collect all headers
                all_headers = []
                for table in tables_to_visualize:
                    if "headers" in table and table["headers"]:
                        all_headers.extend(table["headers"])

                if all_headers:
                    # Count header frequency
                    header_counts = Counter(all_headers)

                    # Plot top 15 headers (or fewer if less available)
                    top_headers = header_counts.most_common(min(15, len(header_counts)))

                    plt.figure(figsize=(14, 8))
                    plt.bar(
                        [h[0] for h in top_headers],
                        [h[1] for h in top_headers],
                        color="skyblue",
                    )
                    plt.title(f"Common Table Headers in Schema: {schema_id}")
                    plt.xticks(rotation=45, ha="right")
                    plt.tight_layout()

                    # Save additional visualization
                    headers_path = os.path.join(output_dir, f"headers_{schema_id}.png")
                    plt.savefig(headers_path, dpi=300)
                    plt.close()
                    output_paths.append(headers_path)

            # 2. Column Count Visualization
            column_counts = [
                table.get("column_count", 0)
                for table in tables_to_visualize
                if "column_count" in table
            ]
            if column_counts:
                plt.figure(figsize=(10, 6))
                plt.hist(
                    column_counts,
                    bins=max(5, min(10, max(column_counts))),
                    color="lightgreen",
                    edgecolor="black",
                )
                plt.title(f"Distribution of Table Column Counts in Schema: {schema_id}")
                plt.xlabel("Columns per Table")
                plt.ylabel("Number of Tables")
                plt.tight_layout()

                # Save additional visualization
                columns_path = os.path.join(output_dir, f"columns_{schema_id}.png")
                plt.savefig(columns_path, dpi=300)
                plt.close()
                output_paths.append(columns_path)

            # 3. Detection Method Visualization
            detection_methods = [
                table.get("detection_method", "unknown")
                for table in tables_to_visualize
                if "detection_method" in table
            ]
            if detection_methods:
                # Count detection methods
                method_counts = Counter(detection_methods)

                plt.figure(figsize=(10, 6))
                plt.bar(
                    list(method_counts.keys()),
                    list(method_counts.values()),
                    color="lightcoral",
                )
                plt.title(f"Table Detection Methods in Schema: {schema_id}")
                plt.xlabel("Detection Method")
                plt.ylabel("Number of Tables")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()

                # Save additional visualization
                methods_path = os.path.join(output_dir, f"methods_{schema_id}.png")
                plt.savefig(methods_path, dpi=300)
                plt.close()
                output_paths.append(methods_path)

            # 4. Table Data Sample Visualization (if available)
            tables_with_samples = [
                table
                for table in tables_to_visualize
                if ("data_sample" in table and table["data_sample"])
                or ("data" in table and table["data"])
            ]
            if tables_with_samples:
                # Create sample table visualizations (up to 3 tables)
                for i, sample_table in enumerate(tables_with_samples[:3]):
                    headers = sample_table.get("headers", [])
                    # Check both data_sample and data fields
                    data_sample = sample_table.get(
                        "data_sample", sample_table.get("data", [])
                    )

                    if data_sample:
                        plt.figure(figsize=(14, 8))

                        # Create a table visualization
                        table_data = data_sample[
                            : min(5, len(data_sample))
                        ]  # Limit to 5 rows

                        # If we have headers, add them as the first row
                        if headers:
                            table_data = [headers] + table_data

                        # Create the table
                        table = plt.table(
                            cellText=table_data,
                            loc="center",
                            cellLoc="center",
                            colWidths=[0.2] * len(table_data[0])
                            if table_data and table_data[0]
                            else None,
                        )

                        # Style the table
                        table.auto_set_font_size(False)
                        table.set_fontsize(9)
                        table.scale(1, 1.5)

                        # Hide axes
                        plt.axis("off")

                        # Add table metadata
                        detection_method = sample_table.get(
                            "detection_method", "unknown"
                        )
                        page = sample_table.get("page", "unknown")
                        row_count = sample_table.get("row_count", 0)
                        column_count = sample_table.get("column_count", 0)

                        plt.title(
                            f"Table {i + 1} from Schema: {schema_id}\n"
                            f"Method: {detection_method}, Page: {page}, "
                            f"Rows: {row_count}, Columns: {column_count}"
                        )
                        plt.tight_layout()

                        # Save additional visualization
                        sample_path = os.path.join(
                            output_dir, f"sample_{i + 1}_{schema_id}.png"
                        )
                        plt.savefig(sample_path, dpi=300, bbox_inches="tight")
                        plt.close()
                        output_paths.append(sample_path)

            # 5. Border Information Visualization (if available)
            tables_with_borders = [
                table
                for table in tables_to_visualize
                if "border_info" in table and table["border_info"]
            ]
            if tables_with_borders:
                # Create border visualization for the first table with border info
                border_table = tables_with_borders[0]
                border_info = border_table.get("border_info", {})

                if border_info:
                    plt.figure(figsize=(10, 8))

                    # Extract border coordinates
                    x0 = border_info.get("x0", 0)
                    y0 = border_info.get("y0", 0)
                    x1 = border_info.get("x1", 100)
                    y1 = border_info.get("y1", 100)
                    rows = border_info.get("rows", 0)
                    cols = border_info.get("cols", 0)

                    # Create a simple visualization of the table grid
                    # Draw outer border
                    plt.plot(
                        [x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], "k-", linewidth=2
                    )

                    # Draw row lines (if we have row information)
                    if rows > 0:
                        row_positions = np.linspace(y0, y1, rows + 1)
                        for y in row_positions:
                            plt.plot([x0, x1], [y, y], "k-", linewidth=1)

                    # Draw column lines (if we have column information)
                    if cols > 0:
                        col_positions = np.linspace(x0, x1, cols + 1)
                        for x in col_positions:
                            plt.plot([x, x], [y0, y1], "k-", linewidth=1)

                    plt.title(
                        f"Table Border Structure (Page {border_table.get('page', 'unknown')})"
                    )
                    plt.xlabel("X Position")
                    plt.ylabel("Y Position")
                    plt.grid(True, linestyle="--", alpha=0.7)
                    plt.tight_layout()

                    # Save additional visualization
                    border_path = os.path.join(output_dir, f"border_{schema_id}.png")
                    plt.savefig(border_path, dpi=300)
                    plt.close()
                    output_paths.append(border_path)

            return output_paths
        except Exception as e:
            self.logger.error(
                f"Error visualizing table patterns: {str(e)}", exc_info=True
            )
            return f"Error visualizing table patterns: {str(e)}"

    def _add_structure_to_graph(self, G, parent_name, structure, prefix, level=1):
        """Add hierarchical structure to graph recursively."""
        for i, section in enumerate(structure):
            has_title = section.get("has_title", False)
            has_content = section.get("has_content", False)
            has_children = section.get("has_children", False)

            # Create node name
            node_name = f"{prefix} {level}.{i + 1}"
            if has_title:
                node_name += "\n(with title)"
            if has_content:
                node_name += "\n(with content)"

            G.add_node(node_name)
            G.add_edge(parent_name, node_name)

            # Add children recursively
            if has_children and "children" in section:
                self._add_structure_to_graph(
                    G, node_name, section["children"], prefix, level + 1
                )

    def _calculate_max_depth(self, structure, current_depth=1):
        """Calculate maximum depth of the section hierarchy."""
        if not structure:
            return current_depth - 1

        max_depth = current_depth
        for section in structure:
            if "children" in section and section["children"]:
                child_depth = self._calculate_max_depth(
                    section["children"], current_depth + 1
                )
                max_depth = max(max_depth, child_depth)

        return max_depth
