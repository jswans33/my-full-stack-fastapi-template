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

from utils.uml.core.exceptions import DiagramTypeError
from utils.uml.core.filesystem import DefaultFileSystem
from utils.uml.core.service import UmlService
from utils.uml.factories import DefaultDiagramFactory
from utils.uml.utils.paths import get_output_base_dir

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Constants
OUTPUT_BASE_DIR = get_output_base_dir()


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
    file_system = DefaultFileSystem()
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

    # Helper function to check if a path should be excluded
    def should_exclude(path: Path) -> bool:
        return any(pat in str(path) for pat in exclude_patterns)

    # Case 1: Single file
    if source_path_obj.is_file():
        paths.append(source_path_obj)
        return paths

    # Case 2: Directory with recursive search
    if source_path_obj.is_dir() and recursive:
        for root, dirs, files in os.walk(source_path_obj):
            # Filter directories in-place to skip excluded ones
            dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]

            # Add Python files that aren't excluded
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(os.path.join(root, file))
                    if not should_exclude(file_path):
                        paths.append(file_path)
        return paths

    # Case 3: Directory without recursion (top-level only)
    if source_path_obj.is_dir():
        for file in source_path_obj.glob("*.py"):
            if not should_exclude(file):
                paths.append(file)

    return paths


def generate_specific_diagram(
    service: UmlService,
    diagram_type: str,
    source_paths: list[Path],
    output_dir: Path,
) -> list[Path] | None:
    """Generate a specific type of diagram.

    Args:
        service: The UML service to use
        diagram_type: The type of diagram to generate
        source_paths: The source paths to analyze
        output_dir: The output directory

    Returns:
        A list of generated diagram paths, or None if an error occurred
    """
    try:
        type_output_dir = output_dir / diagram_type
        type_output_dir.mkdir(parents=True, exist_ok=True)

        # Convert Path objects to strings to match the expected type
        source_paths_str: list[str | Path] = [str(p) for p in source_paths]
        diagrams = service.generate_diagrams(
            diagram_type,
            source_paths_str,
            type_output_dir,
        )

        if diagrams:
            logger.info(
                f"Generated {len(diagrams)} {diagram_type} diagrams in {type_output_dir}",
            )
        return diagrams
    except DiagramTypeError as e:
        logger.error(f"Error generating {diagram_type} diagrams: {e}")
        return None


def main() -> int:
    """Run the UML generator."""
    try:
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
            diagrams = generate_specific_diagram(
                service, args.type, source_paths, output_dir
            )
            if diagrams is None:
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
