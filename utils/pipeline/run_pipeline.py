#!/usr/bin/env python3
"""
Pipeline command-line entry point.

This script provides a command-line interface for running the pipeline on input files.
It supports both single file and batch processing modes.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional

from utils.pipeline.core.file_processor import FileProcessor
from utils.pipeline.utils.logging import get_logger
from utils.pipeline.utils.progress import PipelineProgress

# Default configuration
DEFAULT_CONFIG = {
    "output_format": "json",
    "strategies": {
        "pdf": {
            "analyzer": "utils.pipeline.analyzer.pdf.PDFAnalyzer",
            "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
            "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
            "validator": "utils.pipeline.processors.pdf_validator.PDFValidator",
        },
    },
    "file_processing": {
        "input": {
            "patterns": ["*.pdf"],
            "recursive": False,
        },
        "output": {
            "formats": ["json"],
            "structure": "flat",
            "naming": {
                "template": "{original_name}",
            },
            "overwrite": True,
        },
        "reporting": {
            "summary": True,
            "detailed": True,
            "format": "json",
            "save_path": "processing_report.json",
        },
    },
}


def load_config(config_path: Optional[Path] = None) -> Dict:
    """
    Load configuration from file or use defaults.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()

    if config_path and config_path.exists():
        with open(config_path) as f:
            file_config = json.load(f)
            # Deep merge configs (improved to handle nested dictionaries)
            for key, value in file_config.items():
                if (
                    isinstance(value, dict)
                    and key in config
                    and isinstance(config[key], dict)
                ):
                    # Recursively merge nested dictionaries
                    config[key] = deep_merge(config[key], value)
                else:
                    config[key] = value

    return config


def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """
    Recursively merge two dictionaries.

    Args:
        dict1: First dictionary
        dict2: Second dictionary (values from this dict override dict1)

    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = deep_merge(result[key], value)
        else:
            # Override or add the value
            result[key] = value
    return result


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process documents using the pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all PDFs in input directory
  python -m utils.pipeline.run_pipeline --input data/input --output data/output

  # Process specific file
  python -m utils.pipeline.run_pipeline --file document.pdf --output output/

  # Use custom config file
  python -m utils.pipeline.run_pipeline --input data/input --config pipeline_config.json

  # Specify output formats
  python -m utils.pipeline.run_pipeline --input data/input --formats json,markdown
  
  # Analyze schemas
  python -m utils.pipeline.run_pipeline --analyze-schemas
  
  # Compare schemas
  python -m utils.pipeline.run_pipeline --compare-schemas schema1_id schema2_id
  
  # Visualize schemas
  python -m utils.pipeline.run_pipeline --visualize-schemas clusters
""",
    )

    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "-i",
        "--input",
        type=Path,
        help="Input directory containing files to process",
    )
    input_group.add_argument("-f", "--file", type=Path, help="Single file to process")

    # Schema analysis arguments
    input_group.add_argument(
        "--analyze-schemas", action="store_true", help="Analyze existing schemas"
    )
    input_group.add_argument(
        "--compare-schemas",
        nargs=2,
        metavar=("SCHEMA1", "SCHEMA2"),
        help="Compare two schemas",
    )
    input_group.add_argument(
        "--visualize-schemas",
        choices=["clusters", "features", "structure", "tables"],
        help="Visualize schemas",
    )

    parser.add_argument("--document-type", help="Filter schemas by document type")

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output directory for processed files",
    )
    parser.add_argument("-c", "--config", type=Path, help="Path to configuration file")
    parser.add_argument(
        "--formats",
        help="Comma-separated list of output formats (e.g., json,markdown)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively process subdirectories",
    )
    parser.add_argument(
        "-p",
        "--pattern",
        help="File pattern to match (e.g., '*.pdf', defaults to all PDFs)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Path to save processing report (defaults to output_dir/processing_report.json)",
    )

    return parser.parse_args()


def update_config_from_args(config: Dict, args: argparse.Namespace) -> Dict:
    """
    Update configuration with command line arguments.

    Args:
        config: Base configuration dictionary
        args: Parsed command line arguments

    Returns:
        Updated configuration dictionary
    """
    # Update formats if specified
    if args.formats:
        formats = [fmt.strip().lower() for fmt in args.formats.split(",")]
        config["file_processing"]["output"]["formats"] = formats

    # Update input settings
    if args.pattern:
        config["file_processing"]["input"]["patterns"] = [args.pattern]
    config["file_processing"]["input"]["recursive"] = args.recursive

    # Update report path if specified
    if args.report:
        config["file_processing"]["reporting"]["save_path"] = str(args.report)

    return config


def main():
    """Main entry point for the pipeline."""
    # Add parent directory to path to allow imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    # Set up logging
    logger = get_logger(__name__)
    progress = PipelineProgress()

    try:
        # Parse arguments
        args = parse_args()

        # Handle schema analysis commands
        if args.analyze_schemas or args.compare_schemas or args.visualize_schemas:
            from utils.pipeline.schema.extended_registry import ExtendedSchemaRegistry

            registry = ExtendedSchemaRegistry()

            if args.analyze_schemas:
                progress.display_success("Analyzing schemas...")
                analysis = registry.analyze(args.document_type)

                # Display analysis results
                progress.display_success("\nSchema Analysis Results:")
                progress.display_success(
                    f"Total Schemas: {analysis.get('schema_count', 0)}"
                )

                doc_types = analysis.get("document_types", {})
                if doc_types:
                    progress.display_success("\nDocument Types:")
                    for doc_type, count in doc_types.items():
                        progress.display_success(f"  {doc_type}: {count}")

                # Display common metadata fields
                common_metadata = analysis.get("common_metadata", {})
                if common_metadata:
                    progress.display_success("\nCommon Metadata Fields:")
                    for field, frequency in sorted(
                        common_metadata.items(), key=lambda x: x[1], reverse=True
                    ):
                        progress.display_success(f"  {field}: {frequency:.2f}")

                return

            elif args.compare_schemas:
                schema_id1, schema_id2 = args.compare_schemas
                progress.display_success(
                    f"Comparing schemas: {schema_id1} vs {schema_id2}"
                )

                comparison = registry.compare(schema_id1, schema_id2)

                progress.display_success(
                    f"Overall Similarity: {comparison.get('overall_similarity', 0):.2f}"
                )
                progress.display_success(
                    f"Same Document Type: {comparison.get('same_document_type', False)}"
                )

                # Display metadata comparison
                metadata_comparison = comparison.get("metadata_comparison", {})
                if metadata_comparison:
                    progress.display_success("\nMetadata Comparison:")
                    progress.display_success(
                        f"  Similarity: {metadata_comparison.get('similarity', 0):.2f}"
                    )
                    progress.display_success(
                        f"  Common Fields: {len(metadata_comparison.get('common_fields', []))}"
                    )

                return

            elif args.visualize_schemas:
                viz_type = args.visualize_schemas
                progress.display_success(f"Generating {viz_type} visualization...")

                # Create visualizations directory
                import os

                viz_dir = os.path.join(
                    "utils", "pipeline", "schema", "data", "visualizations"
                )
                os.makedirs(viz_dir, exist_ok=True)

                viz_path = registry.visualize(viz_type, output_dir=viz_dir)
                progress.display_success(f"Visualization saved to: {viz_path}")
                return

        # Load and update configuration
        config = load_config(args.config)

        # Debug output to check if classification configuration is loaded
        if "classification" in config:
            print("Classification configuration found:")
            print(json.dumps(config["classification"], indent=2))
        else:
            print("No classification configuration found in config")

        config = update_config_from_args(config, args)

        # Check if required arguments are provided for document processing
        if not args.input and not args.file:
            progress.display_error(
                "Error: Either --input or --file is required for document processing"
            )
            sys.exit(1)

        if not args.output:
            progress.display_error(
                "Error: --output is required for document processing"
            )
            sys.exit(1)

        # Create output directory
        args.output.mkdir(parents=True, exist_ok=True)

        # Initialize processor
        if args.file:
            # Single file mode
            processor = FileProcessor(args.file.parent, args.output, config)
            progress.display_success(f"Processing single file: {args.file.name}")
            data, path = processor.process_single_file(args.file)
            progress.display_success(f"Output saved to: {Path(path).name}")

        else:
            # Batch mode
            processor = FileProcessor(args.input, args.output, config)
            progress.display_success(f"Processing files from: {args.input}")
            results = processor.process_all_files()

            # Display summary
            summary = {
                f"{r['file']}": {
                    "status": r["status"],
                    "outputs": r.get("outputs", []),
                }
                for r in results
            }
            progress.display_summary(summary)

    except Exception as e:
        logger.error(f"Pipeline processing failed: {str(e)}", exc_info=True)
        progress.display_error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
