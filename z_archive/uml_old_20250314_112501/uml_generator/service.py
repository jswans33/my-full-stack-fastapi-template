"""Service for generating UML diagrams from source code."""

import logging
from pathlib import Path

from .config.loader import Config
from .interfaces import FileSystem, GeneratorFactory, ParserFactory


class UmlGeneratorService:
    """Service for generating UML diagrams from source code."""

    def __init__(
        self,
        config: Config,
        file_system: FileSystem,
        parser_factory: ParserFactory,
        generator_factory: GeneratorFactory,
        logger: logging.Logger | None = None,
    ):
        self.config = config
        self.file_system = file_system
        self.parser_factory = parser_factory
        self.generator_factory = generator_factory
        self.logger = logger or logging.getLogger(__name__)

    def process_file(self, file_path: Path) -> bool:
        """Process a single file and generate UML diagram.

        Returns True if processing was successful, False otherwise.
        """
        self.logger.info(f"Processing file: {file_path}")

        try:
            # Skip if this is just a listing operation
            if self.config.parser.list_only:
                self.logger.info(f"Listing file: {file_path}")
                return True

            # Skip files with unsupported extensions
            if not any(
                file_path.match(pattern) for pattern in self.config.parser.patterns
            ):
                self.logger.warning(f"Skipping unsupported file type: {file_path}")
                return False

            # Get appropriate parser
            parser = self.parser_factory.create_parser(file_path.suffix)

            # Parse the file
            file_model = parser.parse_file(file_path)

            if not file_model.classes and not file_model.functions:
                self.logger.warning(
                    f"No classes or functions found in file: {file_path}",
                )
                return False

            # Get appropriate generator
            generator = self.generator_factory.create_generator(
                self.config.generator.format,
            )

            # Generate the UML diagram
            output_extension = generator.get_output_extension()
            # Preserve directory structure in output
            relative_path = file_path.relative_to(self.config.source_dir)
            output_path = (
                self.config.output_dir
                / relative_path.parent
                / f"{file_path.stem}{output_extension}"
            )
            # Ensure output directory exists
            self.file_system.ensure_directory(output_path.parent)
            generator.generate_diagram(file_model, output_path)

            self.logger.info(
                f"Generated UML diagram for {file_path.stem}",
                extra={
                    "output_path": str(output_path),
                    "class_count": len(file_model.classes),
                    "function_count": len(file_model.functions),
                },
            )
            return True

        except Exception as e:
            self.logger.exception(
                f"Error processing file {file_path}",
                exc_info=e,
            )
            return False

    def process_directory(self, directory: Path) -> int:
        """Process all files in a directory.

        Returns the number of successfully processed files.
        """
        self.logger.info(f"Processing directory: {directory}")

        # Find all files matching the configured patterns in the directory
        files = []
        for pattern in self.config.parser.patterns:
            files.extend(self.file_system.find_files(directory, pattern))

        if not files:
            self.logger.warning(
                f"No files matching patterns {self.config.parser.patterns} found in {directory}",
            )
            return 0

        # Skip excluded directories
        files = [
            f
            for f in files
            if not any(
                part.startswith(".")
                or any(d in str(f) for d in self.config.parser.exclude_dirs)
                for part in f.parts
            )
        ]

        # Log the files found
        self.logger.info(f"Found {len(files)} files in {directory}")

        # Process each file
        success_count = 0
        for file_path in files:
            if self.process_file(file_path):
                success_count += 1

        # Process subdirectories if recursive flag is set
        if self.config.parser.recursive:
            for subdir in directory.iterdir():
                if subdir.is_dir():
                    success_count += self.process_directory(subdir)

        return success_count

    def run(self) -> None:
        """Run the UML generator service."""
        self.logger.info(
            "Starting UML generation",
            extra={
                "output_dir": str(self.config.output_dir),
            },
        )

        # Ensure output directory exists
        self.file_system.ensure_directory(self.config.output_dir)

        # Process the directory
        total_processed = self.process_directory(Path("."))

        # Generate index.rst for Sphinx integration if using PlantUML
        # Skip index generation in list_only mode
        if not self.config.parser.list_only:
            generator = self.generator_factory.create_generator(
                self.config.generator.format,
            )
            if hasattr(generator, "generate_index"):
                output_extension = generator.get_output_extension()
                diagrams = self.file_system.find_files(
                    self.config.output_dir,
                    f"*{output_extension}",
                )
                generator.generate_index(self.config.output_dir, diagrams)

        self.logger.info(
            f"UML generation completed - processed {total_processed} files",
        )
