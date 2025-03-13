#!/usr/bin/env python
"""
Script to run the UML generator on the backend/app directory.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any

from utils.uml_generator.config.loader import load_config
from utils.uml_generator.factories import DefaultGeneratorFactory, DefaultParserFactory
from utils.uml_generator.filesystem import DefaultFileSystem
from utils.uml_generator.generator.sequence_generator import SequenceDiagramGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Constants

OUTPUT_BASE_DIR = Path("docs/source/_generated_uml")
SEQUENCE_OUTPUT_DIR = OUTPUT_BASE_DIR / "sequence"
DEFAULT_PLANTUML_SETTINGS = [
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
]

UML_GENERATOR_PLANTUML_SETTINGS = [
    "skinparam classAttributeIconSize 0",
    "skinparam monochrome true",
    "skinparam shadowing false",
    "left to right direction",
    "hide empty members",
]


def get_component_path(file_path: Path, base_dir: Path) -> str | None:
    """Get the component path for a file."""
    rel_path = file_path.relative_to(base_dir)
    parts = rel_path.parts

    component_map = {
        "uml_generator": "uml_generator",
        "utils": "utils",
        "tests": "tests",
        "api": "api",
        "core": "core",
        "models": "models",
        "examples": "examples",
    }

    return next(
        (
            value
            for key, value in component_map.items()
            if key in str(file_path) or key in parts
        ),
        None,
    )


def create_standard_config(base_dir: Path) -> Any:
    """Create a standard configuration for UML generation."""
    return load_config(
        {
            "paths": {
                "source_dir": str(base_dir),
                "output_dir": str(OUTPUT_BASE_DIR),
            },
            "generator": {
                "format": "plantuml",
                "plantuml_settings": {
                    "PLANTUML_START": "@startuml",
                    "PLANTUML_END": "@enduml",
                    "PLANTUML_SETTINGS": DEFAULT_PLANTUML_SETTINGS,
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


def create_uml_generator_config(project_root: Path) -> Any:
    """Create a configuration specific for the UML generator package."""
    return load_config(
        {
            "paths": {
                "source_dir": str(project_root),
                "output_dir": str(OUTPUT_BASE_DIR),
            },
            "generator": {
                "format": "plantuml",
                "plantuml_settings": {
                    "PLANTUML_START": "@startuml",
                    "PLANTUML_END": "@enduml",
                    "PLANTUML_SETTINGS": UML_GENERATOR_PLANTUML_SETTINGS,
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


def create_service_components(config: Any) -> tuple:
    """Create and return service components based on configuration."""
    file_system = DefaultFileSystem()
    parser_factory = DefaultParserFactory(file_system)
    generator_factory = DefaultGeneratorFactory(
        file_system,
        {
            "format": config.generator.format,
            "plantuml_settings": config.generator.plantuml_settings,
        },
    )
    return file_system, parser_factory, generator_factory


def process_directory(directory: Path, base_dir: Path) -> None:
    """Process a specific directory and generate UML diagrams."""
    if not directory.exists():
        logger.error(f"Directory {directory} does not exist.")
        return

    config = create_standard_config(base_dir)
    file_system, parser_factory, generator_factory = create_service_components(config)

    logger.info(f"Generating UML diagrams for {directory}...")

    # Process files and organize by component
    for root, _, files in os.walk(directory):
        root_path = Path(root)
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                file_path = root_path / file
                process_python_file(
                    file_path,
                    base_dir,
                    file_system,
                    parser_factory,
                    generator_factory,
                )


def process_python_file(
    file_path: Path,
    base_dir: Path,
    file_system: DefaultFileSystem,
    parser_factory: DefaultParserFactory,
    generator_factory: DefaultGeneratorFactory,
) -> None:
    """Process a single Python file and generate UML diagram if it contains classes or functions."""
    # Process the file
    file_model = parser_factory.create_parser(".py").parse_file(file_path)
    if file_model.classes or file_model.functions:
        # Put all diagrams in one file
        file_system.ensure_directory(OUTPUT_BASE_DIR)
        output_path = OUTPUT_BASE_DIR / "all.puml"
        generator = generator_factory.create_generator("plantuml")
        generator.generate_diagram(file_model, output_path)


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

    # Add uml_generator directory for special handling
    uml_generator_dir = utils_dir / "uml_generator"

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
        "uml_generator": {
            "dirs": [uml_generator_dir] if uml_generator_dir.exists() else [],
            "base_dir": project_root,
        },
    }


def process_uml_generator_files(uml_generator_dir: Path, project_root: Path) -> None:
    """Process UML generator files with specific handling."""
    if not uml_generator_dir.exists():
        return

    uml_gen_config = create_uml_generator_config(project_root)
    file_system, parser_factory, generator_factory = create_service_components(
        uml_gen_config,
    )

    logger.info(
        f"Generating UML diagrams for {uml_generator_dir} (with special handling)...",
    )

    # Create a dedicated UML diagram for the UML generator package itself
    for root, _, files in os.walk(uml_generator_dir):
        root_path = Path(root)
        for file in files:
            if file.endswith(".py"):  # Include all .py files
                file_path = root_path / file
                process_uml_generator_file(
                    file_path,
                    uml_generator_dir,
                    file_system,
                    parser_factory,
                    generator_factory,
                )


def process_uml_generator_file(
    file_path: Path,
    uml_generator_dir: Path,
    file_system: DefaultFileSystem,
    parser_factory: DefaultParserFactory,
    generator_factory: DefaultGeneratorFactory,
) -> None:
    """Process a single UML generator file with special handling."""
    try:
        file_model = parser_factory.create_parser(".py").parse_file(file_path)
        if not (file_model.classes or file_model.functions):
            return

        # Output to a dedicated folder
        output_dir = OUTPUT_BASE_DIR / "uml_generator"
        file_system.ensure_directory(output_dir)

        # Create component-specific folders
        rel_path = file_path.relative_to(uml_generator_dir)
        if len(rel_path.parts) > 1:  # It's in a subdirectory
            # For deeper nesting, create subdirectories for all parts except the filename
            if len(rel_path.parts) > 2:
                sub_dir_parts = rel_path.parts[:-1]
                sub_output_dir = output_dir.joinpath(*sub_dir_parts)
            else:
                # For single level of nesting, use the first part
                sub_output_dir = output_dir / rel_path.parts[0]

            file_system.ensure_directory(sub_output_dir)
            output_path = sub_output_dir / f"{file_path.stem}.puml"
        else:
            output_path = output_dir / f"{file_path.stem}.puml"

        generator = generator_factory.create_generator("plantuml")
        generator.generate_diagram(file_model, output_path)
    except Exception as e:
        logger.exception(f"Error processing {file_path}: {e}")


def generate_and_fix_index() -> None:
    """Generate index file for all diagrams and fix path separators."""
    output_dir = OUTPUT_BASE_DIR
    file_system = DefaultFileSystem()

    # Use recursive search to find all PUML files
    diagrams = find_all_puml_diagrams(output_dir)

    # Create generator with same settings as used for diagrams
    generator_factory = DefaultGeneratorFactory(
        file_system,
        {
            "format": "plantuml",
            "plantuml_settings": {
                "PLANTUML_START": "@startuml",
                "PLANTUML_END": "@enduml",
                "PLANTUML_SETTINGS": DEFAULT_PLANTUML_SETTINGS,
            },
        },
    )

    # Generate index with all found diagrams
    generator = generator_factory.create_generator("plantuml")
    generator.generate_index(output_dir, sorted(diagrams))

    # Fix path separators in index.rst for cross-platform compatibility
    fix_index_path_separators(output_dir / "index.rst")


def find_all_puml_diagrams(output_dir: Path) -> list:
    """Find all PUML diagrams recursively in the output directory."""
    diagrams = []
    for root, _, files in os.walk(output_dir):
        diagrams.extend(Path(root) / file for file in files if file.endswith(".puml"))
    return diagrams


def generate_sequence_diagrams() -> None:
    """Generate sequence diagrams from YAML definitions."""
    try:
        import yaml
    except ImportError:
        logger.error("PyYAML is required for sequence diagram generation")
        logger.error("Install with 'pip install pyyaml'")
        return

    sequence_dir = Path("examples/sequence_diagrams")
    file_system = DefaultFileSystem()

    if not sequence_dir.exists():
        logger.warning(f"No sequence diagram definitions found at {sequence_dir}")
        return

    logger.info(f"Generating sequence diagrams from {sequence_dir}...")

    # Create output directory
    file_system.ensure_directory(SEQUENCE_OUTPUT_DIR)

    # Create generator factory
    generator_factory = DefaultGeneratorFactory(
        file_system,
        {
            "sequence_settings": {
                "HIDE_FOOTBOXES": True,
                "AUTONUMBER": True,
            },
        },
    )

    try:
        # Get the sequence diagram generator
        sequence_generator = generator_factory.create_generator("sequence")

        # Check if it's actually a SequenceDiagramGenerator
        if not isinstance(sequence_generator, SequenceDiagramGenerator):
            logger.error(
                f"Expected SequenceDiagramGenerator but got {type(sequence_generator)}"
            )
            return

        # Process all YAML files
        yaml_count = 0
        for yaml_file in sequence_dir.glob("*.yaml"):
            output_file = SEQUENCE_OUTPUT_DIR / f"{yaml_file.stem}.puml"
            logger.info(f"Processing sequence diagram from {yaml_file}")

            try:
                # Read and parse the YAML file
                yaml_content = file_system.read_file(yaml_file)
                diagram_def = yaml.safe_load(yaml_content)

                # Create the model and generate the diagram
                sequence_model = sequence_generator._create_model_from_yaml(diagram_def)
                sequence_generator.generate_diagram(sequence_model, output_file)

                yaml_count += 1
            except Exception as yaml_error:
                logger.error(f"Error processing {yaml_file}: {yaml_error}")
                continue

        if yaml_count > 0:
            logger.info(
                f"Generated {yaml_count} sequence diagrams in {SEQUENCE_OUTPUT_DIR}"
            )
        else:
            logger.warning("No sequence diagrams were generated")

    except Exception as e:
        logger.error(f"Error generating sequence diagrams: {e}")


def generate_static_sequence_diagrams() -> None:
    """Generate sequence diagrams from code analysis."""
    try:
        from utils.sequence_extractor.analyzer import SequenceAnalyzer
        from utils.sequence_extractor.generator import PlantUmlSequenceGenerator
    except ImportError as e:
        logger.error(f"Error importing sequence extractor: {e}")
        logger.info(
            "Sequence extractor may not be installed. Skipping static sequence diagram generation."
        )
        return

    # Directories to analyze
    app_dir = PROJECT_ROOT / "backend" / "app"
    if not app_dir.exists():
        logger.warning(
            f"App directory {app_dir} not found. Skipping static sequence diagram generation."
        )
        return

    # Create output directory
    file_system = DefaultFileSystem()
    file_system.ensure_directory(SEQUENCE_OUTPUT_DIR)

    logger.info(f"Analyzing code in {app_dir} for sequence diagrams...")

    # Create analyzer and analyze directories
    analyzer = SequenceAnalyzer(app_dir)
    analyzer.analyze_directory()

    # Get key entry points to analyze (could be configured or detected)
    # These would be entry points that are relevant for your application
    entry_points = [
        # Example entry points - replace with actual ones from your app
        ("UserController", "create_user"),
        ("AuthController", "login"),
    ]

    # Generate diagrams for each entry point
    generator = PlantUmlSequenceGenerator()
    for class_name, method_name in entry_points:
        try:
            logger.info(
                f"Generating sequence diagram for {class_name}.{method_name}..."
            )
            diagram = analyzer.generate_sequence_diagram(class_name, method_name)
            output_path = SEQUENCE_OUTPUT_DIR / f"{class_name}_{method_name}.puml"
            generator.generate_file(diagram, output_path)
            logger.info(f"Generated sequence diagram at {output_path}")
        except Exception as e:
            logger.error(
                f"Error generating sequence for {class_name}.{method_name}: {e}"
            )


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


def main():
    """Run the UML generator on the backend/app directory structure."""
    # Get all directories to process
    directories = get_directories_to_process()
    if not directories:
        return 1

    # Process regular directories
    for category, category_info in directories.items():
        if category != "uml_generator":  # Special handling for UML generator
            for directory in category_info["dirs"]:
                process_directory(directory, category_info["base_dir"])

    # Special processing for UML generator files
    if directories.get("uml_generator", {}).get("dirs"):
        uml_generator_dir = directories["uml_generator"]["dirs"][0]
        process_uml_generator_files(uml_generator_dir, PROJECT_ROOT)

    # Generate index file with all diagrams
    generate_and_fix_index()

    # Generate sequence diagrams if available
    generate_sequence_diagrams()

    # Generate sequence diagrams from code analysis
    generate_static_sequence_diagrams()

    # Verify and log the generated files structure
    verify_generated_files(OUTPUT_BASE_DIR)

    logger.info("\nUML diagrams generated successfully.")

    return 0


def fix_index_path_separators(index_path):
    """Fix path separators in index.rst to use forward slashes for cross-platform compatibility."""
    if not index_path.exists():
        logger.warning(f"Index file not found at {index_path}")
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

            modified_line = f"{prefix}.. uml:: {fixed_path}"
            modified_lines.append(modified_line)
        else:
            modified_lines.append(line)

    index_path.write_text("\n".join(modified_lines))
    logger.info(f"Fixed path separators in {index_path.name}")


if __name__ == "__main__":
    sys.exit(main())
