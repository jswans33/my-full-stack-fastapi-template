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


def main():
    """Run the UML generator on the backend/app directory."""
    # Get the app directory path
    app_dir = Path("backend/app")
    if not app_dir.exists():
        print(f"Error: Directory {app_dir} does not exist.")
        return 1

    # Create configuration
    config = load_config(
        {
            "paths": {
                "output_dir": "docs/source/_generated_uml",
            },
            "generator": {
                "format": "plantuml",
            },
            "parser": {
                "patterns": ["*.py"],
                "show_imports": True,
                "recursive": True,
            },
            "logging": {
                "level": "info",
            },
        },
    )

    # Create file system
    file_system = DefaultFileSystem()

    # Create factories
    parser_factory = DefaultParserFactory(file_system)
    generator_factory = DefaultGeneratorFactory(
        file_system,
        {
            "format": config.generator.format,
            "plantuml_settings": config.generator.plantuml_settings,
        },
    )

    # Create service
    service = UmlGeneratorService(
        config=config,
        file_system=file_system,
        parser_factory=parser_factory,
        generator_factory=generator_factory,
    )

    # Run the service
    print(f"Generating UML diagrams for {app_dir}...")
    os.chdir(Path(__file__).parent.parent)  # Change to project root

    # Process the app directory directly
    total_processed = service.process_directory(app_dir)

    # Generate index file
    generator = generator_factory.create_generator(config.generator.format)
    if hasattr(generator, "generate_index"):
        output_extension = generator.get_output_extension()
        diagrams = file_system.find_files(
            config.output_dir,
            f"*{output_extension}",
        )
        generator.generate_index(config.output_dir, diagrams)

    print(f"Processed {total_processed} files")
    print(f"UML diagrams generated in {config.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
