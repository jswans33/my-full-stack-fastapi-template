#!/usr/bin/env python
"""Command-line tool for extracting sequence diagrams from Python code.

This script analyzes Python code and generates sequence diagrams in PlantUML format
based on the static analysis of method calls.

Usage:
    # For class method analysis
    python -m utils.extract_sequence --dir path/to/code --class ClassName --method methodName

    # For FastAPI router analysis
    python -m utils.extract_sequence --dir backend/app --module api.routes.login --function login_access_token

Example:
    python -m utils.extract_sequence --dir backend/app --class UserService --method create_user
"""

import argparse
import importlib
import os
import sys
from pathlib import Path

from utils.sequence_extractor.analyzer import SequenceAnalyzer
from utils.sequence_extractor.generator import PlantUmlSequenceGenerator


def main() -> int:
    """Run the sequence diagram extractor."""
    parser = argparse.ArgumentParser(
        description="Extract sequence diagrams from Python code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract sequence diagram for a class method
  python -m utils.extract_sequence --dir backend/app --class UserService --method create_user

  # Extract sequence diagram for a FastAPI router function
  python -m utils.extract_sequence --dir backend/app --module api.routes.login --function login_access_token
  
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
        help="Entry point class name (required for class method analysis)",
    )
    parser.add_argument(
        "--method",
        "-m",
        help="Entry point method name (required for class method analysis)",
    )
    parser.add_argument(
        "--module",
        help="Module path for direct import (e.g., api.routes.login)",
    )
    parser.add_argument(
        "--function",
        "-f",
        help="Function name for analyzing standalone functions or router endpoints",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: {class}_{method}.puml or {function}.puml)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum call depth to analyze (default: 5)",
    )
    parser.add_argument(
        "--analyze-imports",
        action="store_true",
        help="Analyze imported modules as well",
    )

    args = parser.parse_args()

    # Validate arguments
    if not ((args.class_name and args.method) or (args.module and args.function)):
        parser.error(
            "You must specify either:\n"
            "  1. --class and --method for class method analysis, or\n"
            "  2. --module and --function for function/router analysis"
        )

    # Create output path if not specified
    if not args.output:
        if args.function:
            args.output = f"{args.function}.puml"
        else:
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
    if args.module and args.function:
        # Try the module import approach first
        if args.verbose:
            print(f"Analyzing module {args.module} function {args.function}")

        try:
            # Add the directory to sys.path to enable imports
            dir_path = Path(args.dir).resolve()
            sys.path.insert(0, str(dir_path.parent))

            # Import the module
            module_obj = importlib.import_module(args.module, package=dir_path.name)

            # For now, just fall back to the static analysis
            # In the future, we could add dynamic analysis of the imported module
            if args.verbose:
                print("Note: Module import successful, but still using static analysis")
        except Exception as e:
            if args.verbose:
                print(f"Module import failed: {e}")

        # Use router as the class name for FastAPI router functions
        if "routes" in args.module:
            class_name = "router"
        else:
            class_name = args.function.split("_")[0].capitalize()

        # Fall back to static analysis
        diagram = analyzer.generate_sequence_diagram(class_name, args.function)
    else:
        # Standard static analysis
        diagram = analyzer.generate_sequence_diagram(args.class_name, args.method)

    if args.verbose:
        print(
            f"Generated sequence diagram with {len(diagram.participants)} participants and {len(diagram.messages)} messages"
        )

    # Generate the PlantUML file
    generator = PlantUmlSequenceGenerator()

    # Create directory if it doesn't exist
    output_path = Path(args.output)
    os.makedirs(output_path.parent, exist_ok=True)

    generator.generate_file(diagram, args.output)

    print(f"Sequence diagram generated: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
