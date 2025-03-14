"""Core service for UML diagram generation.

This module provides the core service for UML diagram generation, including
the main entry point for generating diagrams.
"""

import logging
from pathlib import Path
from typing import Any

from utils.uml.core.exceptions import DiagramTypeError, GeneratorError, ParserError
from utils.uml.core.interfaces import DiagramFactory


class UmlService:
    """Core service for UML diagram generation."""

    def __init__(
        self,
        factory: DiagramFactory,
        settings: dict[str, Any] | None = None,
    ):
        """Initialize the UML service.

        Args:
            factory: The diagram factory to use
            settings: Optional settings for the service
        """
        self.factory = factory
        self.settings = settings or {}
        self.logger = logging.getLogger(__name__)

    def generate_diagram(
        self,
        diagram_type: str,
        source_path: str | Path,
        output_path: str | Path,
        **kwargs,
    ) -> None:
        """Generate a UML diagram from the given source path.

        Args:
            diagram_type: The type of diagram to generate (class, sequence, etc.)
            source_path: The path to the source code or definition file
            output_path: The path to write the diagram to
            **kwargs: Additional diagram-specific arguments

        Raises:
            DiagramTypeError: If the diagram type is not supported
            ParserError: If the source code cannot be parsed
            GeneratorError: If the diagram cannot be generated
        """
        try:
            # Create analyzer and generator
            analyzer = self.factory.create_analyzer(diagram_type, **kwargs)
            generator = self.factory.create_generator(diagram_type, **kwargs)

            # Analyze the source code
            model = analyzer.analyze(source_path, **kwargs)

            # Generate the diagram
            generator.generate_diagram(model, output_path, **kwargs)

            self.logger.info(f"Generated {diagram_type} diagram at {output_path}")
        except (DiagramTypeError, ParserError, GeneratorError) as e:
            self.logger.error(f"Failed to generate {diagram_type} diagram: {e}")
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error generating {diagram_type} diagram: {e}"
            )
            raise GeneratorError(f"Unexpected error: {e}", cause=e)

    def generate_diagrams(
        self,
        diagram_type: str,
        source_paths: list[str | Path],
        output_dir: str | Path,
        **kwargs,
    ) -> list[Path]:
        """Generate UML diagrams from the given source paths.

        Args:
            diagram_type: The type of diagram to generate (class, sequence, etc.)
            source_paths: The paths to the source code or definition files
            output_dir: The directory to write the diagrams to
            **kwargs: Additional diagram-specific arguments

        Returns:
            A list of paths to the generated diagrams

        Raises:
            DiagramTypeError: If the diagram type is not supported
        """
        output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
        generated_diagrams: list[Path] = []

        # Create analyzer and generator
        analyzer = self.factory.create_analyzer(diagram_type, **kwargs)
        generator = self.factory.create_generator(diagram_type, **kwargs)

        # Process each source path
        for source_path in source_paths:
            source_path = (
                Path(source_path) if isinstance(source_path, str) else source_path
            )

            try:
                # Determine output path
                if source_path.is_file():
                    output_path = output_dir / f"{source_path.stem}.puml"
                else:
                    # For directories, use the directory name
                    output_path = output_dir / f"{source_path.name}.puml"

                # Analyze the source code
                model = analyzer.analyze(source_path, **kwargs)

                # Generate the diagram
                generator.generate_diagram(model, output_path, **kwargs)

                generated_diagrams.append(output_path)
                self.logger.info(f"Generated {diagram_type} diagram at {output_path}")
            except Exception as e:
                self.logger.error(f"Error processing {source_path}: {e}")
                # Continue with other source paths

        # Generate index file
        if generated_diagrams:
            try:
                generator.generate_index(output_dir, generated_diagrams, **kwargs)
                self.logger.info(f"Generated index file at {output_dir}")
            except Exception as e:
                self.logger.error(f"Error generating index file: {e}")

        return generated_diagrams

    def generate_all_diagrams(
        self,
        source_paths: dict[str, list[str | Path]],
        output_dir: str | Path,
        **kwargs,
    ) -> dict[str, list[Path]]:
        """Generate all types of UML diagrams from the given source paths.

        Args:
            source_paths: A dictionary mapping diagram types to source paths
            output_dir: The directory to write the diagrams to
            **kwargs: Additional diagram-specific arguments

        Returns:
            A dictionary mapping diagram types to lists of generated diagram paths
        """
        output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
        results: dict[str, list[Path]] = {}

        for diagram_type, paths in source_paths.items():
            try:
                # Create type-specific output directory
                type_output_dir = output_dir / diagram_type
                type_output_dir.mkdir(parents=True, exist_ok=True)

                # Generate diagrams for this type
                diagrams = self.generate_diagrams(
                    diagram_type,
                    paths,
                    type_output_dir,
                    **kwargs,
                )
                results[diagram_type] = diagrams
            except DiagramTypeError as e:
                self.logger.error(f"Unsupported diagram type {diagram_type}: {e}")
            except Exception as e:
                self.logger.error(f"Error generating {diagram_type} diagrams: {e}")

        return results
