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
            # Deep merge configs
            for key, value in file_config.items():
                if isinstance(value, dict) and key in config:
                    config[key].update(value)
                else:
                    config[key] = value

    return config


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
""",
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-i",
        "--input",
        type=Path,
        help="Input directory containing files to process",
    )
    input_group.add_argument("-f", "--file", type=Path, help="Single file to process")

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
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

        # Load and update configuration
        config = load_config(args.config)
        config = update_config_from_args(config, args)

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
