#!/usr/bin/env python
"""Main entry point for UML diagram generation.

This module provides the main entry point for generating UML diagrams using the
unified architecture.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Now import the modules
from utils.uml.core.exceptions import DiagramTypeError
from utils.uml.core.filesystem import FileSystem
from utils.uml.core.service import UmlService
from utils.uml.factories import DefaultDiagramFactory

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Constants
OUTPUT_BASE_DIR = Path("docs/source/_generated_uml")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate UML diagrams from source code.",
    )

    parser.add_argument(
        "--type",
        "-t",
        choices=["class", "sequence", "activity", "state", "all"],
        default="all",
        help="Type of diagram to generate (default: all)",
    )

    parser.add_argument(
        "--source",
        "-s",
        required=True,
        help="Source directory or file to analyze",
    )

    parser.add_argument(
        "--output",
        "-o",
        default=str(OUTPUT_BASE_DIR),
        help=f"Output directory for diagrams (default: {OUTPUT_BASE_DIR})",
    )

    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Recursively analyze directories",
    )

    parser.add_argument(
        "--exclude",
        "-e",
        action="append",
        default=[],
        help="Patterns to exclude (can be specified multiple times)",
    )

    parser.add_argument(
        "--include-private",
        "-p",
        action="store_true",
        help="Include private members in diagrams",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def create_service(settings: dict[str, Any] | None = None) -> UmlService:
    """Create and return a UML service with the given settings."""
    file_system = FileSystem()
    factory = DefaultDiagramFactory(file_system, settings)
    return UmlService(factory, settings)


def get_source_paths(
    source_path: str,
    recursive: bool = False,
    exclude_patterns: list[str] | None = None,
) -> list[Path]:
    """Get source paths to analyze.

    Args:
        source_path: The source path to analyze
        recursive: Whether to recursively analyze directories
        exclude_patterns: Patterns to exclude

    Returns:
        A list of paths to analyze
    """
    exclude_patterns = exclude_patterns or []
    source_path_obj = Path(source_path)
    paths = []

    if source_path_obj.is_file():
        # Single file
        paths.append(source_path_obj)
    elif source_path_obj.is_dir():
        # Directory
        if recursive:
            # Recursively walk the directory
            for root, dirs, files in os.walk(source_path_obj):
                # Skip directories matching exclude patterns
                dirs[:] = [
                    d for d in dirs if not any(pat in d for pat in exclude_patterns)
                ]

                # Process Python files
                for file in files:
                    if file.endswith(".py"):
                        file_path = Path(os.path.join(root, file))
                        # Skip files matching exclude patterns
                        if any(pat in str(file_path) for pat in exclude_patterns):
                            continue
                        paths.append(file_path)
        else:
            # Only process files in the top-level directory
            for file in source_path_obj.glob("*.py"):
                # Skip files matching exclude patterns
                if any(pat in str(file) for pat in exclude_patterns):
                    continue
                paths.append(file)

    return paths


def main() -> int:
    """Run the UML generator."""
    args = parse_arguments()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create service
    settings = {
        "include_private": args.include_private,
        "recursive": args.recursive,
        "exclude_patterns": args.exclude,
    }
    service = create_service(settings)

    # Get source paths
    source_paths = get_source_paths(
        args.source,
        args.recursive,
        args.exclude,
    )

    if not source_paths:
        logger.error(f"No source files found at {args.source}")
        return 1

    # Generate diagrams
    try:
        if args.type == "all":
            # Generate all diagram types
            # Convert Path objects to strings to match the expected type
            source_paths_str: list[str | Path] = [str(p) for p in source_paths]
            source_paths_dict = {
                "class": source_paths_str,
                "sequence": source_paths_str,
                "activity": source_paths_str,
                "state": source_paths_str,
            }
            results = service.generate_all_diagrams(source_paths_dict, output_dir)

            # Log results
            for diagram_type, diagrams in results.items():
                if diagrams:
                    logger.info(
                        f"Generated {len(diagrams)} {diagram_type} diagrams in {output_dir / diagram_type}",
                    )
        else:
            # Generate a specific diagram type
            try:
                type_output_dir = output_dir / args.type
                type_output_dir.mkdir(parents=True, exist_ok=True)

                # Convert Path objects to strings to match the expected type
                source_paths_str: list[str | Path] = [str(p) for p in source_paths]
                diagrams = service.generate_diagrams(
                    args.type,
                    source_paths_str,
                    type_output_dir,
                )

                if diagrams:
                    logger.info(
                        f"Generated {len(diagrams)} {args.type} diagrams in {type_output_dir}",
                    )
            except DiagramTypeError as e:
                logger.error(f"Error: {e}")
                return 1

        logger.info(f"UML diagrams generated successfully in {output_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error generating diagrams: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
