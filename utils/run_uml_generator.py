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

    # If the file is in the utils directory, treat differently
    if "uml_generator" in str(file_path):
        return "uml_generator"
    if "utils" in str(file_path):
        return "utils"

    # Handle app directory components
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

    project_root = Path.cwd()

    app_dir = project_root / "backend" / "app"
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

    # Add utils directory
    utils_dir = project_root / "utils"

    # Add uml_generator directory for special handling
    uml_generator_dir = utils_dir / "uml_generator"

    # Process each group with appropriate settings
    for directory in [d for d in core_dirs if d and d.exists()]:
        process_directory(directory, app_dir)

    for directory in [d for d in api_dirs if d and d.exists()]:
        process_directory(directory, app_dir)

    # Process tests with different exclude rules
    for directory in test_dirs:
        process_directory(directory, app_dir)

    # Process utils directory with same settings
    if utils_dir.exists():
        process_directory(utils_dir, project_root)

    # Process UML generator directory with modified settings to include all Python files
    if uml_generator_dir.exists():
        # Create UML generator-specific config
        uml_gen_config = load_config(
            {
                "paths": {
                    "source_dir": str(project_root),
                    "output_dir": "docs/source/_generated_uml",
                },
                "generator": {
                    "format": "plantuml",
                    "plantuml_settings": {
                        "PLANTUML_START": "@startuml",
                        "PLANTUML_END": "@enduml",
                        "PLANTUML_SETTINGS": [
                            "skinparam classAttributeIconSize 0",
                            "skinparam monochrome true",
                            "skinparam shadowing false",
                            "left to right direction",
                            "hide empty members",
                        ],
                    },
                },
                "parser": {
                    "patterns": ["*.py"],  # Include all Python files
                    "show_imports": True,
                    "recursive": True,
                    "exclude_dirs": ["__pycache__", "*.egg-info"],
                },
                "logging": {"level": "info"},
            },
        )

        # Create special service for UML generator
        file_system = DefaultFileSystem()
        parser_factory = DefaultParserFactory(file_system)
        generator_factory = DefaultGeneratorFactory(
            file_system,
            {
                "format": uml_gen_config.generator.format,
                "plantuml_settings": uml_gen_config.generator.plantuml_settings,
            },
        )

        # Process UML generator directory
        print(
            f"Generating UML diagrams for {uml_generator_dir} (with special handling)..."
        )

        # Create a dedicated UML diagram for the UML generator package itself
        for root, _, files in os.walk(uml_generator_dir):
            root_path = Path(root)
            for file in files:
                if file.endswith(".py"):  # Include all .py files
                    file_path = root_path / file

                    # Process the file
                    try:
                        file_model = parser_factory.create_parser(".py").parse_file(
                            file_path
                        )
                        if file_model.classes or file_model.functions:
                            # Output to a dedicated folder
                            output_dir = Path(
                                "docs/source/_generated_uml/uml_generator"
                            )
                            file_system.ensure_directory(output_dir)

                            # Create component-specific folders
                            rel_path = file_path.relative_to(uml_generator_dir)
                            if len(rel_path.parts) > 1:  # It's in a subdirectory
                                sub_output_dir = output_dir / rel_path.parts[0]
                                file_system.ensure_directory(sub_output_dir)
                                output_path = sub_output_dir / f"{file_path.stem}.puml"
                            else:
                                output_path = output_dir / f"{file_path.stem}.puml"

                            generator = generator_factory.create_generator("plantuml")
                            generator.generate_diagram(file_model, output_path)
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

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

    # Fix path separators in index.rst for cross-platform compatibility
    fix_index_path_separators(output_dir / "index.rst")

    output_dir = Path("docs/source/_generated_uml")

    # List all generated files
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


def fix_index_path_separators(index_path):
    """Fix path separators in index.rst to use forward slashes for cross-platform compatibility."""
    if not index_path.exists():
        print(f"Warning: Index file not found at {index_path}")
        return

    content = index_path.read_text()

    # Fix path references in the uml directive paths
    modified_lines = []
    for line in content.splitlines():
        if ".. uml:: " in line:
            # Extract the path part
            prefix, path = line.split(".. uml:: ", 1)
            # Replace backslashes with forward slashes
            fixed_path = path.replace("\\", "/")

            # Remove any "../" prefix - we want paths to be relative to the current directory
            if fixed_path.startswith("../"):
                fixed_path = fixed_path[3:]  # Remove the "../" prefix

            modified_lines.append(f"{prefix}.. uml:: {fixed_path}")
        else:
            modified_lines.append(line)

    index_path.write_text("\n".join(modified_lines))
    print(f"Fixed path separators in {index_path.name}")


if __name__ == "__main__":
    sys.exit(main())
