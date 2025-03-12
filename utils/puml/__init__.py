"""
PlantUML Utilities Package

This package provides utilities for working with PlantUML diagrams.
It includes tools for rendering diagrams, viewing them in a browser, and analyzing code to generate diagrams.

Available modules:
- config: Configuration settings for the PlantUML utilities
- render_diagrams: Functions for rendering PlantUML diagrams to PNG or SVG images
- code_analyzer: Functions for analyzing code and generating PlantUML diagrams
- cli: Command-line interface for working with PlantUML diagrams
- test_puml: Test script for the PlantUML utilities

Usage:
    # Render diagrams to PNG
    from utils.puml import render_diagram, render_all_diagrams
    render_diagram('docs/diagrams/classifier/classifier_model_diagram.puml',
                   output_dir='output',
                   format='png')

    # Render diagrams to SVG
    render_all_diagrams('docs/diagrams',
                        output_dir='output',
                        format='svg')

    # Analyze code and generate diagrams
    from utils.puml import analyze_directory, generate_class_diagram, save_diagram
    visitors = analyze_directory('path/to/code')
    diagram = generate_class_diagram(visitors)
    save_diagram(diagram, 'docs/diagrams/code_analysis/class_diagram.puml')

    # Use the CLI
    python -m utils.puml.cli render --format=svg
    python -m utils.puml.cli view
    python -m utils.puml.cli analyze --path=path/to/code
"""

__version__ = "0.1.0"

from .code_analyzer import (
    analyze_directory,
    analyze_file,
    generate_class_diagram,
    generate_module_diagram,
    save_diagram,
)

# Import key functions and constants for easier access
from .config import DEFAULT_FORMAT, FORMATS, OUTPUT_DIR, SOURCE_DIR
from .render_diagrams import render_all_diagrams, render_diagram
