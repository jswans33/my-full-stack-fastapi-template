"""
Test Code Analyzer

This script tests the code analyzer by analyzing the code_analyzer.py file itself
and generating a class diagram from it.
"""

import logging
import os
import sys

from utils.puml.code_analyzer import analyze_file, generate_class_diagram, save_diagram
from utils.puml.config import OUTPUT_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("test_code_analyzer")


def test_code_analyzer():
    """Test the code analyzer by analyzing itself."""
    # Get the path to the code_analyzer.py file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    code_analyzer_path = os.path.join(script_dir, "code_analyzer.py")

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
    os.makedirs(code_analysis_dir, exist_ok=True)

    # Save the diagram
    output_file = os.path.join(code_analysis_dir, "code_analyzer_class_diagram.puml")
    save_diagram(diagram, output_file)

    logger.info(f"Saved diagram to {output_file}")
    logger.info(
        "You can render it using: python -m utils.puml.cli render --file=code_analysis/code_analyzer_class_diagram.puml"
    )

    return 0


if __name__ == "__main__":
    sys.exit(test_code_analyzer())
