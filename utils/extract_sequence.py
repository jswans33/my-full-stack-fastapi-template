#!/usr/bin/env python
"""Command-line tool for extracting sequence diagrams from Python code.

This script analyzes Python code and generates sequence diagrams in PlantUML format
based on the static analysis of method calls.

Usage:
    python -m utils.extract_sequence --dir path/to/code --class ClassName --method methodName

Example:
    python -m utils.extract_sequence --dir backend/app --class UserService --method create_user
"""

import argparse
import sys

from utils.sequence_extractor.analyzer import SequenceAnalyzer
from utils.sequence_extractor.generator import PlantUmlSequenceGenerator


def main() -> int:
    """Run the sequence diagram extractor."""
    parser = argparse.ArgumentParser(
        description="Extract sequence diagrams from Python code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract sequence diagram for UserService.create_user
  python -m utils.extract_sequence --dir backend/app --class UserService --method create_user

  # Extract sequence diagram with a custom output path
  python -m utils.extract_sequence --dir backend/app --class UserService --method create_user --output diagrams/create_user.puml
        """,
    )

    parser.add_argument(
        "--dir",
        "-d",
        default=".",
        help="Directory containing Python code to analyze (default: current directory)",
    )
    parser.add_argument(
        "--class",
        "-c",
        dest="class_name",
        required=True,
        help="Entry point class name",
    )
    parser.add_argument(
        "--method",
        "-m",
        required=True,
        help="Entry point method name",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: {class}_{method}.puml)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Create output path if not specified
    if not args.output:
        args.output = f"{args.class_name}_{args.method}.puml"

    # Create the analyzer
    analyzer = SequenceAnalyzer(args.dir)

    if args.verbose:
        print(f"Analyzing directory: {args.dir}")

    # Analyze the code
    analyzer.analyze_directory()

    if args.verbose:
        print(
            f"Found {len(analyzer.classes)} classes and {len(analyzer.function_calls)} function calls"
        )

    # Generate the sequence diagram
    diagram = analyzer.generate_sequence_diagram(args.class_name, args.method)

    if args.verbose:
        print(
            f"Generated sequence diagram with {len(diagram.participants)} participants and {len(diagram.messages)} messages"
        )

    # Generate the PlantUML file
    generator = PlantUmlSequenceGenerator()
    generator.generate_file(diagram, args.output)

    print(f"Sequence diagram generated: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
