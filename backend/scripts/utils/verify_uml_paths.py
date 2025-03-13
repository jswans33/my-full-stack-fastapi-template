#!/usr/bin/env python3
"""Verify UML file paths and their references in documentation."""

import logging
import re
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_project_paths():
    """Get all relevant project paths."""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent
    docs_dir = project_root / "docs"
    source_dir = docs_dir / "source"
    uml_dir = source_dir / "_generated_uml"

    return {
        "project_root": project_root,
        "docs_dir": docs_dir,
        "source_dir": source_dir,
        "uml_dir": uml_dir,
    }


def verify_uml_files_and_references():
    """Verify UML files exist and are properly referenced."""
    paths = get_project_paths()
    uml_dir = paths["uml_dir"]

    # Get all .puml files
    puml_files = list(uml_dir.glob("*.puml"))
    logger.info(f"\nFound {len(puml_files)} .puml files in {uml_dir}")
    logger.info("Directory structure:")
    logger.info(f"  Project root: {paths['project_root']}")
    logger.info(f"  Docs dir: {paths['docs_dir']}")
    logger.info(f"  Source dir: {paths['source_dir']}")
    logger.info(f"  UML dir: {paths['uml_dir']}")

    # List all files in UML directory
    logger.info("\nFiles in UML directory:")
    for file in sorted(uml_dir.iterdir()):
        logger.info(f"  - {file.name}")

    # Create a set of file names for quick lookup
    puml_filenames = {f.name for f in puml_files}

    # Check each .puml file
    logger.info("\nVerifying .puml files:")
    for puml_file in puml_files:
        logger.info(f"\nChecking {puml_file.name}:")
        logger.info(f"  - Absolute path: {puml_file.absolute()}")
        logger.info(
            f"  - Relative to project root: {puml_file.relative_to(paths['project_root'])}",
        )

        # Verify file content
        try:
            content = puml_file.read_text()
            if "@startuml" in content and "@enduml" in content:
                logger.info("  - ✓ Valid PlantUML syntax")
            else:
                logger.warning("  - ✗ Missing @startuml/@enduml tags")
        except Exception as e:
            logger.error(f"  - ✗ Error reading file: {e}")

    # Check index.rst
    index_rst = uml_dir / "index.rst"
    if index_rst.exists():
        logger.info(f"\nChecking {index_rst.name}:")
        try:
            content = index_rst.read_text()
            referenced_files = re.findall(r"\.\.[\s]+uml::[\s]+([^\n]+)", content)

            # Check each referenced file
            for ref in referenced_files:
                ref = ref.strip()
                # Remove any path prefix
                ref_filename = Path(ref).name
                if ref_filename in puml_filenames:
                    logger.info(f"  - ✓ Found referenced file: {ref_filename}")
                else:
                    logger.error(f"  - ✗ Missing referenced file: {ref_filename}")

            # Check for unreferenced files
            referenced_filenames = {Path(ref.strip()).name for ref in referenced_files}
            unreferenced = puml_filenames - referenced_filenames
            if unreferenced:
                logger.warning("  - Unreferenced .puml files:")
                for filename in sorted(unreferenced):
                    logger.warning(f"    * {filename}")
        except Exception as e:
            logger.error(f"  - ✗ Error reading index.rst: {e}")
    else:
        logger.error(f"  - ✗ index.rst not found in {uml_dir}")

    # Check uml_diagrams.rst
    uml_diagrams_rst = paths["source_dir"] / "uml_diagrams.rst"
    if uml_diagrams_rst.exists():
        logger.info(f"\nChecking {uml_diagrams_rst.name}:")
        try:
            content = uml_diagrams_rst.read_text()
            if "_generated_uml/index" in content:
                logger.info("  - ✓ Found reference to _generated_uml/index")
            else:
                logger.warning("  - ✗ Missing reference to _generated_uml/index")
        except Exception as e:
            logger.error(f"  - ✗ Error reading uml_diagrams.rst: {e}")
    else:
        logger.error(f"  - ✗ uml_diagrams.rst not found in {paths['source_dir']}")


def main():
    """Run all verifications."""
    logger.info("Starting UML paths verification...")
    verify_uml_files_and_references()


if __name__ == "__main__":
    main()
