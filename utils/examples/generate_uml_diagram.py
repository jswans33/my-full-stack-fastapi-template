#!/usr/bin/env python
"""
Example script to generate a UML diagram of the UML generator itself.

This script demonstrates how to use the UML generator to analyze
the UML generator code structure and generate a class diagram.
"""

import os
import subprocess
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
UML_DIR = PROJECT_ROOT / "utils" / "uml"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "source" / "_generated_uml" / "examples"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Generating UML diagram of the UML generator itself...")
print(f"Source directory: {UML_DIR}")
print(f"Output directory: {OUTPUT_DIR}")

# Method 1: Using the extract_class.py script
print("\nMethod 1: Using extract_class.py")
try:
    subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "utils" / "extract_class.py"),
            "--source",
            str(UML_DIR),
            "--output",
            str(OUTPUT_DIR),
            "--recursive",
            "--verbose",
        ],
        check=True,
    )
    print(f"Class diagram generated at {OUTPUT_DIR}/uml.puml")
except subprocess.CalledProcessError as e:
    print(f"Error running extract_class.py: {e}")

# Method 2: Using the unified run.py entry point
print("\nMethod 2: Using the unified entry point (run.py)")
try:
    subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "utils" / "uml" / "run.py"),
            "--type",
            "class",
            "--source",
            str(UML_DIR),
            "--output",
            str(OUTPUT_DIR / "unified"),
            "--recursive",
            "--verbose",
        ],
        check=True,
    )
    print(f"Class diagram generated at {OUTPUT_DIR}/unified/class")
except subprocess.CalledProcessError as e:
    print(f"Error running run.py: {e}")

# Method 3: Using run_uml.py (which uses the virtual environment)
print("\nMethod 3: Using run_uml.py (requires virtual environment setup)")
print("To use this method, first run:")
print("  python utils/install_dev.py")
print("Then run:")
print(
    "  python utils/run_uml.py extract_class.py --source utils/uml --output docs/source/_generated_uml/examples --recursive",
)

print("\nTo view the generated diagrams, you need a PlantUML viewer or renderer.")
print(
    "You can use the PlantUML extension in VSCode or convert them to images using the PlantUML jar.",
)

# Instructions for installing the utils package
print("\nTo install the UML generator as a package:")
print("1. Run the installation script:")
print("   python utils/install_dev.py")
print("2. This will create a virtual environment in utils/.venv")
print("3. You can then use the UML generator scripts with the virtual environment")
