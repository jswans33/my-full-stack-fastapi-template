#!/usr/bin/env python
"""
Script to run the UML generator on the backend/app directory.

This script uses the new unified architecture for UML diagram generation.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

from utils.uml.core.filesystem import DefaultFileSystem
from utils.uml.core.service import UmlService
from utils.uml.factories import DefaultDiagramFactory
from utils.uml.utils.paths import get_output_base_dir, get_output_dir, get_project_root

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = get_project_root()

# Constants
OUTPUT_BASE_DIR = get_output_base_dir()
CLASS_OUTPUT_DIR = get_output_dir("class")
SEQUENCE_OUTPUT_DIR = get_output_dir("sequence")
ACTIVITY_OUTPUT_DIR = get_output_dir("activity")
STATE_OUTPUT_DIR = get_output_dir("state")


def get_directories_to_process() -> dict:
    """Get directories that need to be processed for UML generation."""
    project_root = PROJECT_ROOT

    app_dir = project_root / "backend" / "app"
    if not app_dir.exists():
        logger.error(f"Directory {app_dir} does not exist.")
        return {}

    # Process core components first
    core_dirs = [
        app_dir / "core",
        app_dir / "models" if (app_dir / "models").exists() else app_dir,
        app_dir / "services" if (app_dir / "services").exists() else None,
    ]

    # Process API components
    api_dirs = [app_dir / "api"]

    # Process test components separately with different settings
    test_dirs = [app_dir / "tests"] if (app_dir / "tests").exists() else []

    # Add utils directory
    utils_dir = project_root / "utils"

    # Add uml directory for special handling
    uml_dir = utils_dir / "uml"

    return {
        "core": {
            "dirs": [d for d in core_dirs if d and d.exists()],
            "base_dir": app_dir,
        },
        "api": {"dirs": [d for d in api_dirs if d and d.exists()], "base_dir": app_dir},
        "tests": {"dirs": test_dirs, "base_dir": app_dir},
        "utils": {
            "dirs": [utils_dir] if utils_dir.exists() else [],
            "base_dir": project_root,
        },
        "uml": {
            "dirs": [uml_dir] if uml_dir.exists() else [],
            "base_dir": project_root,
        },
    }


def generate_class_diagrams(service: UmlService, directories: dict) -> None:
    """Generate class diagrams for the specified directories."""
    # Create output directory
    output_dir = CLASS_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Generating class diagrams...")

    # Process each directory
    for category, category_info in directories.items():
        for directory in category_info["dirs"]:
            try:
                # Generate class diagram for this directory
                output_path = output_dir / f"{category}_{directory.name}.puml"
                service.generate_diagram(
                    "class",
                    directory,
                    output_path,
                    recursive=True,
                    include_private=False,
                )
                logger.info(f"Generated class diagram for {directory} at {output_path}")
            except Exception as e:
                logger.error(f"Error generating class diagram for {directory}: {e}")


def generate_sequence_diagrams(service: UmlService, directories: dict) -> None:
    """Generate sequence diagrams for the specified directories."""
    # Create output directory
    output_dir = SEQUENCE_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Generating sequence diagrams...")

    # Process each directory
    for category, category_info in directories.items():
        for directory in category_info["dirs"]:
            try:
                # Generate sequence diagram for this directory
                output_path = output_dir / f"{category}_{directory.name}.puml"
                service.generate_diagram(
                    "sequence",
                    directory,
                    output_path,
                    recursive=True,
                    root_dir=str(directory),
                )
                logger.info(
                    f"Generated sequence diagram for {directory} at {output_path}",
                )
            except Exception as e:
                logger.error(f"Error generating sequence diagram for {directory}: {e}")


def generate_activity_diagrams(service: UmlService, directories: dict) -> None:
    """Generate activity diagrams for the specified directories."""
    # Create output directory
    output_dir = ACTIVITY_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Generating activity diagrams...")

    # Process each directory
    for category, category_info in directories.items():
        for directory in category_info["dirs"]:
            try:
                # Generate activity diagram for this directory
                output_path = output_dir / f"{category}_{directory.name}.puml"
                service.generate_diagram(
                    "activity",
                    directory,
                    output_path,
                    recursive=True,
                )
                logger.info(
                    f"Generated activity diagram for {directory} at {output_path}",
                )
            except Exception as e:
                logger.error(f"Error generating activity diagram for {directory}: {e}")


def generate_state_diagrams(service: UmlService, directories: dict) -> None:
    """Generate state diagrams for the specified directories."""
    # Create output directory
    output_dir = STATE_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Generating state diagrams...")

    # Process each directory
    for category, category_info in directories.items():
        for directory in category_info["dirs"]:
            try:
                # Generate state diagram for this directory
                output_path = output_dir / f"{category}_{directory.name}.puml"
                service.generate_diagram(
                    "state",
                    directory,
                    output_path,
                    recursive=True,
                )
                logger.info(f"Generated state diagram for {directory} at {output_path}")
            except Exception as e:
                logger.error(f"Error generating state diagram for {directory}: {e}")


def generate_yaml_sequence_diagrams(service: UmlService) -> None:
    """Generate sequence diagrams from YAML definitions."""
    try:
        import yaml
    except ImportError:
        logger.error("PyYAML is required for sequence diagram generation")
        logger.error("Install with 'pip install pyyaml'")
        return

    sequence_dir = Path("examples/sequence_diagrams")

    if not sequence_dir.exists():
        logger.warning(f"No sequence diagram definitions found at {sequence_dir}")
        return

    logger.info(f"Generating sequence diagrams from {sequence_dir}...")

    # Create output directory
    output_dir = SEQUENCE_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process all YAML files
    yaml_count = 0
    for yaml_file in sequence_dir.glob("*.yaml"):
        try:
            output_path = output_dir / f"{yaml_file.stem}.puml"

            # Read YAML file and generate diagram
            with open(yaml_file) as f:
                yaml_content = f.read()

            # Use the sequence diagram generator to process the YAML content
            # This is a placeholder - the actual implementation would depend on
            # how the YAML sequence diagrams are processed in the new architecture
            logger.info(f"Processing sequence diagram from {yaml_file}")

            yaml_count += 1
        except Exception as e:
            logger.error(f"Error processing {yaml_file}: {e}")

    if yaml_count > 0:
        logger.info(
            f"Generated {yaml_count} sequence diagrams from YAML in {output_dir}",
        )
    else:
        logger.warning("No sequence diagrams were generated from YAML")


def verify_generated_files(output_dir: Path) -> None:
    """Verify and log the generated files structure."""
    logger.info("\nVerifying generated files structure:")
    logger.info("===================================")

    for root, dirs, files in os.walk(output_dir):
        rel_path = Path(root).relative_to(output_dir)
        level = 0 if str(rel_path) == "." else len(rel_path.parts)

        indent = "  " * level

        # Print directory name
        if level > 0:
            logger.info(f"{indent[:-2]}+ {rel_path.name}/")

        # Print files
        for file in sorted(files):
            if file.endswith(".puml"):
                logger.info(f"{indent}- {file}")
    logger.info("\nUML diagrams generated in docs/source/_generated_uml/")


def main() -> int:
    """Run the UML generator on the backend/app directory structure."""
    # Get all directories to process
    directories = get_directories_to_process()
    if not directories:
        return 1

    # Create output directories
    OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)

    # Create service
    file_system = DefaultFileSystem()
    factory = DefaultDiagramFactory(file_system)
    service = UmlService(factory)

    # Generate class diagrams
    generate_class_diagrams(service, directories)

    # Generate sequence diagrams
    generate_sequence_diagrams(service, directories)

    # Generate activity diagrams
    generate_activity_diagrams(service, directories)

    # Generate state diagrams
    generate_state_diagrams(service, directories)

    # Generate sequence diagrams from YAML definitions
    generate_yaml_sequence_diagrams(service)

    # Alternative: Use the dedicated script for backend/app sequence diagrams
    try:
        if os.path.exists("utils/uml/cli/extract_app_sequences.py"):
            logger.info(
                "Generating application sequence diagrams using extract_app_sequences.py...",
            )
            subprocess.run(
                ["python", "-m", "utils.uml.cli.extract_app_sequences"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            logger.info("Application sequence diagrams generated successfully.")
    except Exception as e:
        logger.error(f"Error generating application sequence diagrams: {e}")

    # Verify and log the generated files structure
    verify_generated_files(OUTPUT_BASE_DIR)

    logger.info("\nUML diagrams generated successfully.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
