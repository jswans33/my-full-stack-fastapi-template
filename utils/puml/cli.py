#!/usr/bin/env python
"""
PlantUML Command Line Interface

This script provides a command-line interface for working with PlantUML diagrams.

Usage:
    python cli.py render [--format=<format>] [--source=<source_dir>] [--output=<output_dir>] [--file=<file>]
    python cli.py view
    python cli.py help

Commands:
    render      Render PlantUML diagrams to images
    view        Open the React viewer in the default web browser
    help        Show this help message

Options:
    --format=<format>     Output format (svg or png, default: svg)
    --source=<source_dir> Source directory for PlantUML files (default: docs/diagrams)
    --output=<output_dir> Directory to save rendered images (default: docs/diagrams/output)
    --file=<file>         Specific .puml file to render (default: all .puml files)
"""

import argparse
import os
import sys
import webbrowser

# Import the configuration and render_diagrams module
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
    elif command == "help":
        show_help()
        return 0
    else:
        print(f"Error: Unknown command: {command}")
        show_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
