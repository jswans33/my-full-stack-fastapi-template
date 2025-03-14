#!/usr/bin/env python
"""
Script to extract state diagrams from Python code.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import the modules
from utils.uml.core.filesystem import FileSystem
from utils.uml.core.service import UmlService
from utils.uml.factories import DefaultDiagramFactory

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Constants
OUTPUT_BASE_DIR = Path("docs/source/_generated_uml/state")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate state diagrams from Python code.",
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
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def main() -> int:
    """Run the state diagram generator."""
    args = parse_arguments()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create service
    file_system = FileSystem()
    factory = DefaultDiagramFactory(file_system)
    service = UmlService(factory)

    # Generate state diagrams
    try:
        # Run the UML generator with the state diagram type
        source_path = Path(args.source)

        # Create analyzer-specific settings
        settings = {
            "recursive": args.recursive,
            "exclude_patterns": args.exclude,
        }

        # Generate the diagram
        service.generate_diagram(
            "state",
            source_path,
            output_dir / f"{source_path.stem}.puml",
            **settings,
        )

        logger.info(f"State diagram generated successfully in {output_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error generating state diagram: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
