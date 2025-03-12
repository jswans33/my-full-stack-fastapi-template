#!/usr/bin/env python
"""
PlantUML Command Line Interface

This script provides a command-line interface for working with PlantUML diagrams.

Usage:
    python -m utils.puml.cli render [--format=<format>] [--source=<source_dir>] [--output=<output_dir>] [--file=<file>]
    python -m utils.puml.cli view
    python -m utils.puml.cli analyze [--path=<path>] [--output=<output_file>] [--modules] [--functions] [--verbose]
    python -m utils.puml.cli help
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .code_analyzer import analyze_and_generate_diagram
from .core import setup_logger
from .exceptions import (
    AnalyzerError,
    PlantUMLError,
    RenderError,
)
from .render_diagrams import launch_viewer, render_all_diagrams, render_diagram
from .settings import settings

# Set up logger
logger = setup_logger("cli")


class CommandError(PlantUMLError):
    """Base exception for command-line interface errors."""

    pass


class InvalidCommandError(CommandError):
    """Raised when an invalid command is provided."""

    pass


class CommandArgumentError(CommandError):
    """Raised when invalid command arguments are provided."""

    pass


def show_help() -> None:
    """Show the help message."""
    print(__doc__)


def path_type(value: str) -> Path:
    """Convert string argument to Path object."""
    return Path(value)


def render_command(args: Sequence[str]) -> int:
    """
    Handle the render command.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)

    Raises:
        CommandArgumentError: If invalid arguments are provided
        RenderError: If there is an error rendering diagrams
    """
    try:
        # Parse arguments
        parser = argparse.ArgumentParser(
            description="Render PlantUML diagrams to images"
        )
        parser.add_argument(
            "--format",
            choices=settings.supported_formats,
            default=settings.default_format,
            help=f"Output format ({' or '.join(settings.supported_formats)})",
        )
        parser.add_argument(
            "--source",
            type=path_type,
            default=settings.source_dir,
            help="Source directory for PlantUML files",
        )
        parser.add_argument(
            "--output",
            type=path_type,
            default=settings.output_dir,
            help="Output directory for rendered images",
        )
        parser.add_argument(
            "--file",
            type=path_type,
            help="Specific .puml file to render",
        )

        # Parse the arguments
        parsed_args = parser.parse_args(args)

        # Render the diagrams
        if parsed_args.file:
            # Render a specific file
            file_path = (
                parsed_args.source / parsed_args.file
                if not parsed_args.file.is_absolute()
                else parsed_args.file
            )
            if not file_path.exists():
                raise CommandArgumentError(f"File not found: {file_path}")

            success = render_diagram(file_path, parsed_args.output, parsed_args.format)
            return 0 if success else 1

        # Render all diagrams
        success_count, total_count = render_all_diagrams(
            parsed_args.source,
            parsed_args.output,
            parsed_args.format,
        )
        return 0 if success_count > 0 else 1

    except (CommandArgumentError, RenderError) as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def view_command() -> int:
    """
    Handle the view command.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        success = launch_viewer()
        return 0 if success else 1
    except RenderError as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def analyze_command(args: Sequence[str]) -> int:
    """
    Handle the analyze command.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)

    Raises:
        CommandArgumentError: If invalid arguments are provided
        AnalyzerError: If there is an error analyzing code
    """
    try:
        # Parse arguments
        parser = argparse.ArgumentParser(
            description="Analyze code and generate PlantUML diagrams",
        )
        parser.add_argument(
            "--path",
            type=path_type,
            default=Path("."),
            help="Path to the Python file or directory to analyze",
        )
        parser.add_argument(
            "--output",
            type=path_type,
            default=None,
            help="Output file for the PlantUML diagram",
        )
        parser.add_argument(
            "--modules",
            action="store_true",
            help="Generate a module diagram instead of a class diagram",
        )
        parser.add_argument(
            "--functions",
            action="store_true",
            help="Include standalone functions in the class diagram",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose logging",
        )

        # Parse the arguments
        parsed_args = parser.parse_args(args)

        # Set up verbose logging if requested
        if parsed_args.verbose:
            setup_logger("code_analyzer", verbose=True)
            setup_logger("cli", verbose=True)

        # Analyze the code and generate the diagram
        output_file = analyze_and_generate_diagram(
            path=parsed_args.path,
            output=parsed_args.output,
            modules=parsed_args.modules,
            functions=parsed_args.functions,
        )

        logger.info(f"\nGenerated diagram: {output_file}")
        logger.info(
            "You can render it using: python -m utils.puml.cli render --file="
            + f"code_analysis/{output_file.name}",
        )
        return 0

    except AnalyzerError as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def main() -> int:
    """
    Main function.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Parse command-line arguments
        if len(sys.argv) < 2:
            show_help()
            return 1

        command = sys.argv[1].lower()
        args = sys.argv[2:]

        # Handle commands
        if command == "render":
            return render_command(args)
        if command == "view":
            return view_command()
        if command == "analyze":
            return analyze_command(args)
        if command == "help":
            show_help()
            return 0

        raise InvalidCommandError(f"Unknown command: {command}")

    except InvalidCommandError as e:
        logger.error(str(e))
        show_help()
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
