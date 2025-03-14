"""Command-line interface for UML generator."""

import argparse
import logging
from pathlib import Path

from .config.loader import load_config
from .factories import DefaultGeneratorFactory, DefaultParserFactory
from .filesystem import DefaultFileSystem
from .service import UmlGeneratorService


def parse_args(args=None) -> argparse.Namespace:
    """Parse command line arguments."""
    # Get the script directory for default paths
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    default_output_dir = project_root.parent / "docs" / "source" / "_generated_uml"

    parser = argparse.ArgumentParser(
        description="Generate UML class diagrams from source code.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="""
Examples:
  # Process a single file
  python -m uml_generator -f backend/app/models.py
  
  # Process a directory
  python -m uml_generator -d backend/app
  
  # Process the app directory
  python -m uml_generator --app-dir
  
  # Process a directory recursively
  python -m uml_generator -d backend/app --recursive
  
  # Specify a custom output directory
  python -m uml_generator -d backend/app -o custom/output/path
  
  # Enable verbose logging
  python -m uml_generator -d backend/app -v
  
  # Generate a sequence diagram from YAML
  python -m uml_generator generate-sequence -f sequence.yaml -o sequence.puml
  
For more information, see the README.md file.
        """,
    )

    # Create a subcommand structure
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Main command arguments (default when no subcommand is specified)
    # Create a mutually exclusive group for input sources
    input_group = parser.add_mutually_exclusive_group(required=False)

    input_group.add_argument(
        "-f",
        "--file",
        help="Process a single source file",
    )

    input_group.add_argument(
        "-d",
        "--directory",
        help="Process a directory containing source files",
    )

    input_group.add_argument(
        "--app-dir",
        action="store_true",
        help="Process the app directory (default location)",
    )

    # Output options
    parser.add_argument(
        "-o",
        "--output",
        default=str(default_output_dir),
        help="Output directory for UML files",
    )

    parser.add_argument(
        "--format",
        choices=["plantuml", "sequence"],
        default="plantuml",
        help="Output format for UML diagrams",
    )

    # Processing options
    parser.add_argument(
        "--subdirs",
        nargs="+",
        default=["models", "services"],
        help="List of subdirectories to process (only with --directory or --app-dir)",
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively process directories",
    )

    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only list files without generating UML diagrams (for troubleshooting)",
    )

    parser.add_argument(
        "--show-imports",
        action="store_true",
        help="Show imports in the UML diagrams",
    )

    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Generate a report of files processed",
    )

    # Verbosity options
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    verbosity_group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress all output except errors",
    )

    verbosity_group.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    # Add sequence diagram command
    sequence_parser = subparsers.add_parser(
        "generate-sequence", help="Generate a sequence diagram from a YAML definition"
    )
    sequence_parser.add_argument(
        "--file", "-f", required=True, help="YAML file defining the sequence diagram"
    )
    sequence_parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output file path for the generated diagram",
    )

    # Pass the args parameter to parse_args
    return parser.parse_args(args)


def configure_logging(args: argparse.Namespace) -> logging.Logger:
    """Configure logging based on command line arguments."""
    logger = logging.getLogger("uml_generator")

    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO
    elif args.quiet:
        level = logging.ERROR
    else:
        level = logging.WARNING

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    return logger


def generate_sequence_diagram(args):
    """Generate a sequence diagram from a YAML definition file."""
    from pathlib import Path

    from .generator.sequence_generator import SequenceDiagramGenerator

    # Set up the generator
    file_system = DefaultFileSystem()
    factory = DefaultGeneratorFactory(file_system, {})
    diagram_generator = factory.create_generator("sequence")

    # Ensure we have a SequenceDiagramGenerator
    if not isinstance(diagram_generator, SequenceDiagramGenerator):
        print(
            f"Error: Generator is not a SequenceDiagramGenerator: {type(diagram_generator)}"
        )
        return

    # Generate the diagram
    diagram_generator.generate_from_yaml(Path(args.file), Path(args.output))
    print(f"Sequence diagram generated at {args.output}")


def main() -> None:
    """Main entry point for the UML generator."""
    # Parse command-line arguments
    args = parse_args()

    # Configure logging
    logger = configure_logging(args)

    # Handle subcommands
    if getattr(args, "command", None) == "generate-sequence":
        generate_sequence_diagram(args)
        return

    # Standard UML generation requires at least one input source
    if not any([args.file, args.directory, args.app_dir]):
        logger.error(
            "At least one input source (--file, --directory, --app-dir) is required"
        )
        return

    # Convert args to dict for config
    args_dict = {
        "paths": {
            "output_dir": args.output,
        },
        "generator": {
            "format": args.format,
        },
        "parser": {
            "show_imports": args.show_imports,
            "patterns": ["*.py"],
            "exclude_dirs": ["__pycache__", "*.egg-info"],
        },
        "logging": {
            "level": "debug"
            if args.debug
            else "info"
            if args.verbose
            else "error"
            if args.quiet
            else "warning",
        },
    }

    # Load configuration
    config = load_config(args_dict)

    # Create dependencies
    file_system = DefaultFileSystem()
    parser_factory = DefaultParserFactory(file_system)
    generator_factory = DefaultGeneratorFactory(
        file_system,
        {
            "plantuml_settings": config.generator.plantuml_settings,
            "format": config.generator.format,
        },
    )

    # Create and run the service
    service = UmlGeneratorService(
        config=config,
        file_system=file_system,
        parser_factory=parser_factory,
        generator_factory=generator_factory,
        logger=logger,
    )

    service.run()


if __name__ == "__main__":
    main()
