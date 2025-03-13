#!/usr/bin/env python
"""
Script to run the UML generator on the backend/app directory.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from utils.uml_generator.config.loader import load_config
from utils.uml_generator.factories import DefaultGeneratorFactory, DefaultParserFactory
from utils.uml_generator.filesystem import DefaultFileSystem
from utils.uml_generator.service import UmlGeneratorService


def get_component_path(file_path: Path, base_dir: Path) -> str:
    """Get the component path for a file."""
    rel_path = file_path.relative_to(base_dir)
    parts = rel_path.parts

    # Handle special cases
    if "tests" in parts:
        return "tests"
    if "api" in parts:
        return "api"
    if "core" in parts:
        return "core"
    if "models" in parts or "models.py" in str(file_path):
        return "models"
    if "examples" in parts:
        return "examples"
    return "utils"  # Default category for other files


def process_directory(directory: Path, base_dir: Path) -> None:
    """Process a specific directory and generate UML diagrams."""
    if not directory.exists():
        print(f"Error: Directory {directory} does not exist.")
        return

    # Create configuration with directory-specific settings
    dir_config = load_config(
        {
            "paths": {
                "source_dir": str(base_dir),
                "output_dir": "docs/source/_generated_uml",  # Base output directory
            },
            "generator": {
                "format": "plantuml",
                "plantuml_settings": {
                    "PLANTUML_START": "@startuml",
                    "PLANTUML_END": "@enduml",
                    "PLANTUML_SETTINGS": [
                        "skinparam classAttributeIconSize 0",
                        "skinparam packageStyle folder",
                        "skinparam monochrome true",
                        "skinparam shadowing false",
                        "left to right direction",
                        "skinparam linetype ortho",
                        "skinparam groupInheritance 3",
                        "skinparam class {",
                        "   BackgroundColor White",
                        "   ArrowColor Black",
                        "   BorderColor Black",
                        "}",
                        "hide empty members",
                    ],
                },
            },
            "parser": {
                "patterns": ["[!_]*.py"],  # Exclude files starting with underscore
                "show_imports": True,
                "recursive": True,
                "exclude_dirs": [
                    "__pycache__",
                    "*.egg-info",
                    "migrations",
                ],
            },
            "logging": {
                "level": "info",
            },
        },
    )

    # Create dependencies
    file_system = DefaultFileSystem()
    parser_factory = DefaultParserFactory(file_system)
    generator_factory = DefaultGeneratorFactory(
        file_system,
        {
            "format": dir_config.generator.format,
            "plantuml_settings": dir_config.generator.plantuml_settings,
        },
    )

    # Create and run service
    service = UmlGeneratorService(
        config=dir_config,
        file_system=file_system,
        parser_factory=parser_factory,
        generator_factory=generator_factory,
    )

    print(f"Generating UML diagrams for {directory}...")

    # Process files and organize by component
    for root, _, files in os.walk(directory):
        root_path = Path(root)
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                file_path = root_path / file
                component = get_component_path(file_path, base_dir)

                # Get clean component path without duplicates
                rel_path = file_path.relative_to(base_dir)
                parts = list(rel_path.parts)

                # Remove duplicate directory names (e.g., api/api/routes -> api/routes)
                clean_parts = []
                for part in parts:
                    if not clean_parts or part != clean_parts[-1]:
                        clean_parts.append(part)

                # Process the file
                file_model = parser_factory.create_parser(".py").parse_file(file_path)
                if file_model.classes or file_model.functions:
                    # Put all diagrams in one file
                    output_dir = Path("docs/source/_generated_uml")
                    file_system.ensure_directory(output_dir)
                    output_path = output_dir / "all.puml"
                    generator = generator_factory.create_generator("plantuml")
                    generator.generate_diagram(file_model, output_path)


def main():
    """Run the UML generator on the backend/app directory structure."""
    os.chdir(Path(__file__).parent.parent)  # Change to project root

    # Define the main app directory and its important subdirectories
    app_dir = Path("backend/app")
    if not app_dir.exists():
        print(f"Error: Directory {app_dir} does not exist.")
        return 1

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

    # Process each group with appropriate settings
    for directory in [d for d in core_dirs if d and d.exists()]:
        process_directory(directory, app_dir)

    for directory in [d for d in api_dirs if d and d.exists()]:
        process_directory(directory, app_dir)

    # Process tests with different exclude rules
    for directory in test_dirs:
        process_directory(directory, app_dir)

    # Generate index file with all diagrams
    output_dir = Path("docs/source/_generated_uml")
    file_system = DefaultFileSystem()

    # Use recursive search to find all PUML files
    diagrams = []
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".puml"):
                diagrams.append(Path(root) / file)

    # Create generator with same settings as used for diagrams
    generator_factory = DefaultGeneratorFactory(
        file_system,
        {
            "format": "plantuml",
            "plantuml_settings": {
                "PLANTUML_START": "@startuml",
                "PLANTUML_END": "@enduml",
                "PLANTUML_SETTINGS": [
                    "skinparam classAttributeIconSize 0",
                    "skinparam packageStyle folder",
                    "skinparam monochrome true",
                    "skinparam shadowing false",
                    "left to right direction",
                    "skinparam linetype ortho",
                    "skinparam groupInheritance 3",
                    "skinparam class {",
                    "   BackgroundColor White",
                    "   ArrowColor Black",
                    "   BorderColor Black",
                    "}",
                    "hide empty members",
                ],
            },
        },
    )

    # Generate index with all found diagrams
    generator = generator_factory.create_generator("plantuml")
    generator.generate_index(output_dir, sorted(diagrams))

    # List all generated files
    output_dir = Path("docs/source/_generated_uml")
    print("\nVerifying generated files structure:")
    print("===================================")
    for root, dirs, files in os.walk(output_dir):
        rel_path = Path(root).relative_to(output_dir)
        if str(rel_path) == ".":
            level = 0
        else:
            level = len(rel_path.parts)
        indent = "  " * level

        # Print directory name
        if level > 0:
            print(f"{indent[:-2]}+ {rel_path.name}/")

        # Print files
        for file in sorted(files):
            if file.endswith(".puml"):
                print(f"{indent}- {file}")

    print("\nUML diagrams generated in docs/source/_generated_uml/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
