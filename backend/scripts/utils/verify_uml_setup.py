#!/usr/bin/env python3
"""Verify UML directory structure and file paths."""

import logging
import os
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def verify_directory_structure():
    """Verify the required directories exist and have correct permissions."""
    # Get the project root directory
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent
    docs_dir = project_root / "docs"
    source_dir = docs_dir / "source"
    uml_dir = source_dir / "_generated_uml"

    # Check each directory exists
    directories = {
        "Project Root": project_root,
        "Docs Directory": docs_dir,
        "Source Directory": source_dir,
        "UML Directory": uml_dir,
    }

    # Print absolute paths
    logger.info("\nAbsolute paths:")
    for name, path in directories.items():
        logger.info(f"{name}: {path.absolute()}")
        if path.exists():
            logger.info(
                f"  - Contents: {[f.name for f in path.iterdir() if f.is_file()]}"
            )

    # Print relative paths from project root
    logger.info("\nRelative paths from project root:")
    for name, path in directories.items():
        try:
            rel_path = path.relative_to(project_root)
            logger.info(f"{name}: {rel_path}")
        except ValueError:
            logger.warning(f"Could not get relative path for {name}")

    # Check directory permissions
    logger.info("\nVerifying directory permissions...")
    for name, path in directories.items():
        if path.exists():
            logger.info(f"✓ {name} exists: {path}")
            if os.access(path, os.W_OK):
                logger.info(f"✓ {name} is writable")
            else:
                logger.error(f"✗ {name} is not writable")
        else:
            logger.error(f"✗ {name} does not exist: {path}")

    return directories


def verify_uml_files(uml_dir: Path):
    """Verify UML files exist and are readable."""
    logger.info("\nVerifying UML files...")
    if not uml_dir.exists():
        logger.error(f"UML directory does not exist: {uml_dir}")
        return

    puml_files = list(uml_dir.glob("*.puml"))
    if not puml_files:
        logger.error("No .puml files found in UML directory")
    else:
        logger.info(f"Found {len(puml_files)} .puml files:")
        for file in puml_files:
            if file.is_file():
                if os.access(file, os.R_OK):
                    logger.info(f"✓ {file.name} exists and is readable")
                    # Check file content
                    try:
                        content = file.read_text()
                        if "@startuml" in content and "@enduml" in content:
                            logger.info(f"✓ {file.name} has valid PlantUML syntax")
                        else:
                            logger.warning(
                                f"✗ {file.name} may have invalid PlantUML syntax"
                            )
                    except Exception as e:
                        logger.error(f"✗ Error reading {file.name}: {e}")
                else:
                    logger.error(f"✗ {file.name} exists but is not readable")


def verify_sphinx_config():
    """Verify Sphinx configuration."""
    logger.info("\nVerifying Sphinx configuration...")
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent
    conf_py = project_root / "docs" / "source" / "conf.py"

    if not conf_py.exists():
        logger.error(f"conf.py not found at {conf_py}")
        return

    try:
        content = conf_py.read_text()
        if "sphinxcontrib.plantuml" in content:
            logger.info("✓ PlantUML extension is configured in conf.py")
        else:
            logger.error("✗ PlantUML extension not found in conf.py")

        if "plantuml =" in content:
            logger.info("✓ PlantUML path is configured")
            # Extract and verify the plantuml path
            for line in content.splitlines():
                if line.strip().startswith("plantuml ="):
                    logger.info(f"  PlantUML path: {line.strip()}")
        else:
            logger.error("✗ PlantUML path not configured")

        # Check for plantuml_output_format
        if "plantuml_output_format" in content:
            logger.info("✓ PlantUML output format is configured")
        else:
            logger.warning("✗ PlantUML output format not configured")
    except Exception as e:
        logger.error(f"Error reading conf.py: {e}")


def main():
    """Run all verifications."""
    logger.info("Starting UML setup verification...")
    directories = verify_directory_structure()
    if directories:
        verify_uml_files(directories["UML Directory"])
    verify_sphinx_config()


if __name__ == "__main__":
    main()
