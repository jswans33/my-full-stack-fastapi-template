#!/usr/bin/env python
"""
PlantUML Command Line Interface

This script provides a command-line interface for working with PlantUML diagrams.

Usage:
    python cli.py render [--format=<format>] [--source=<source_dir>] [--output=<output_dir>] [--file=<file>]
    python cli.py view
    python cli.py analyze [--path=<path>] [--output=<output_file>] [--include-modules] [--include-functions] [--verbose]
    python cli.py help

Commands:
    render      Render PlantUML diagrams to images
    view        Open the React viewer in the default web browser
    analyze     Analyze code and generate PlantUML diagrams
    help        Show this help message

Options:
    --format=<format>     Output format (svg or png, default: svg)
    --source=<source_dir> Source directory for PlantUML files (default: docs/diagrams)
    --output=<output_dir> Directory to save rendered images (default: docs/diagrams/output)
    --file=<file>         Specific .puml file to render (default: all .puml files)
    --path=<path>         Path to the Python file or directory to analyze (default: current directory)
    --include-modules     Generate a module diagram instead of a class diagram
    --include-functions   Include standalone functions in the class diagram
    --verbose             Enable verbose logging
"""

import argparse
import os
import sys
import webbrowser

from utils.puml.code_analyzer import (
    analyze_directory,
    analyze_file,
    generate_class_diagram,
    generate_module_diagram,
    save_diagram,
)

# Import the configuration and modules
from utils.puml.config import DEFAULT_FORMAT, FORMATS, OUTPUT_DIR, SOURCE_DIR
from utils.puml.render_diagrams import render_all_diagrams, render_diagram


def show_help():
    """Show the help message."""
    print(__doc__)


def render_command(args):
    """Handle the render command."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Render PlantUML diagrams to images")
    parser.add_argument(
        "--format",
        choices=FORMATS,
        default=DEFAULT_FORMAT,
        help=f"Output format ({' or '.join(FORMATS)})",
    )
    parser.add_argument(
        "--source",
        default=SOURCE_DIR,
        help="Source directory for PlantUML files",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_DIR,
        help="Output directory for rendered images",
    )
    parser.add_argument("--file", help="Specific .puml file to render")

    # Parse the arguments
    args = parser.parse_args(args)

    # Render the diagrams
    if args.file:
        # Render a specific file
        file_path = (
            os.path.join(args.source, args.file)
            if not os.path.isabs(args.file)
            else args.file
        )
        if os.path.exists(file_path):
            render_diagram(file_path, args.output, args.format)
        else:
            print(f"Error: File not found: {file_path}")
            return 1
    else:
        # Render all diagrams
        render_all_diagrams(args.source, args.output, args.format)

    return 0


def view_command():
    """Handle the view command."""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the path to the React HTML viewer
    viewer_path = os.path.join(script_dir, "viewer", "index.html")

    # Check if the viewer exists
    if not os.path.exists(viewer_path):
        print(f"Error: React HTML viewer not found: {viewer_path}")
        return 1

    # Check if the output directory exists
    if not os.path.exists(OUTPUT_DIR):
        print(f"Error: Output directory not found: {OUTPUT_DIR}")
        print("Please render the diagrams first using the 'render' command.")
        return 1

    # Open the viewer in the default web browser
    print(f"Opening React HTML viewer: {viewer_path}")
    webbrowser.open(f"file://{os.path.abspath(viewer_path)}")

    return 0


def analyze_command(args):
    """Handle the analyze command."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Analyze code and generate PlantUML diagrams"
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Path to the Python file or directory to analyze",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file for the PlantUML diagram",
    )
    parser.add_argument(
        "--include-modules",
        action="store_true",
        help="Generate a module diagram instead of a class diagram",
    )
    parser.add_argument(
        "--include-functions",
        action="store_true",
        help="Include standalone functions in the class diagram",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    # Parse the arguments
    args = parser.parse_args(args)

    # Set up logging
    import logging

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    logger = logging.getLogger("code_analyzer")
    logger.setLevel(log_level)

    # Analyze the code
    if os.path.isdir(args.path):
        print(f"Analyzing directory: {args.path}")
        visitors = analyze_directory(args.path)
    elif os.path.isfile(args.path) and args.path.endswith(".py"):
        print(f"Analyzing file: {args.path}")
        visitor = analyze_file(args.path)
        visitors = [visitor] if visitor else []
    else:
        print(f"Error: Invalid path: {args.path}")
        return 1

    if not visitors:
        print("Error: No Python files were successfully analyzed")
        return 1

    # Generate the diagram
    if args.include_modules:
        diagram = generate_module_diagram(visitors)
        diagram_type = "module"
    else:
        diagram = generate_class_diagram(visitors, args.include_functions)
        diagram_type = "class"

    # Determine the output file
    if args.output:
        output_file = args.output
    else:
        # Use a default output file based on the input path
        if os.path.isdir(args.path):
            base_name = os.path.basename(os.path.abspath(args.path))
        else:
            base_name = os.path.splitext(os.path.basename(args.path))[0]

        # Create the code_analysis directory in the output directory if it doesn't exist
        code_analysis_dir = os.path.join(OUTPUT_DIR, "code_analysis")
        os.makedirs(code_analysis_dir, exist_ok=True)

        output_file = os.path.join(
            code_analysis_dir,
            f"{base_name}_{diagram_type}_diagram.puml",
        )

    # Save the diagram
    save_diagram(diagram, output_file)

    print(f"\nGenerated {diagram_type} diagram: {output_file}")
    print(
        "You can render it using: python -m utils.puml.cli render --file=code_analysis/"
        + f"{os.path.basename(output_file)}"
    )

    return 0


def main():
    """Main function."""
    # Parse command-line arguments
    if len(sys.argv) < 2:
        show_help()
        return 1

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    # Handle commands
    if command == "render":
        return render_command(args)
    elif command == "view":
        return view_command()
    elif command == "analyze":
        return analyze_command(args)
    elif command == "help":
        show_help()
        return 0
    else:
        print(f"Error: Unknown command: {command}")
        show_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
    sys.exit(main())
