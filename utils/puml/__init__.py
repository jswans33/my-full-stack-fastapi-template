"""
PlantUML Utilities Package

This package provides utilities for working with PlantUML diagrams.
It includes tools for rendering diagrams and viewing them in a browser.

Available modules:
- config: Configuration settings for the PlantUML utilities
- render_diagrams: Functions for rendering PlantUML diagrams to PNG or SVG images
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

    # Use the CLI
    python -m utils.puml.cli render --format=svg
    python -m utils.puml.cli view
"""

__version__ = "0.1.0"

# Import key functions and constants for easier access
from .config import DEFAULT_FORMAT, FORMATS, OUTPUT_DIR, SOURCE_DIR
from .render_diagrams import render_all_diagrams, render_diagram
