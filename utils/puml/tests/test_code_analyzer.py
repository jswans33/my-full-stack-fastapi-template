"""
Test Code Analyzer

This script tests the code analyzer by analyzing the code_analyzer.py file itself
and generating a class diagram from it.
"""

import os
import sys

# Add the project root to sys.path to ensure imports work correctly
project_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Add the parent directory to path to allow relative imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the puml modules - try different import strategies
try:
    # First try relative imports (when running as a module)
    from ..code_analyzer import analyze_file, generate_class_diagram, save_diagram
    from ..config import OUTPUT_DIR
    from ..core import ensure_dir_exists, setup_logger
except (ImportError, ValueError):
    try:
        # Then try direct imports (when running from the utils/puml directory)
        from code_analyzer import analyze_file, generate_class_diagram, save_diagram
        from config import OUTPUT_DIR
        from core import ensure_dir_exists, setup_logger
    except ImportError:
        # Finally fall back to absolute imports (when running from project root)
        from utils.puml.code_analyzer import (
            analyze_file,
            generate_class_diagram,
            save_diagram,
        )
        from utils.puml.config import OUTPUT_DIR
        from utils.puml.core import ensure_dir_exists, setup_logger

# Configure logging
logger = setup_logger("test_code_analyzer", verbose=True)


def test_code_analyzer():
    """Test the code analyzer by analyzing itself."""
    # Get the path to the code_analyzer.py file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    code_analyzer_path = os.path.join(parent_dir, "code_analyzer.py")

    # Make sure the file exists
    if not os.path.exists(code_analyzer_path):
        logger.error(f"Code analyzer file not found: {code_analyzer_path}")
        return 1

    # Analyze the file
    logger.info(f"Analyzing file: {code_analyzer_path}")
    visitor = analyze_file(code_analyzer_path)
    if not visitor:
        logger.error("Failed to analyze the file")
        return 1

    # Generate a class diagram
    logger.info("Generating class diagram")
    diagram = generate_class_diagram([visitor], include_functions=True)

    # Create the output directory if it doesn't exist
    code_analysis_dir = os.path.join(OUTPUT_DIR, "code_analysis")
    ensure_dir_exists(code_analysis_dir)

    # Save the diagram
    output_file = os.path.join(code_analysis_dir, "code_analyzer_class_diagram.puml")
    save_diagram(diagram, output_file)

    logger.info(f"Saved diagram to {output_file}")
    logger.info(
        "You can render it using: python -m utils.puml.cli render --file=code_analysis/code_analyzer_class_diagram.puml",
    )

    return 0


if __name__ == "__main__":
    sys.exit(test_code_analyzer())
