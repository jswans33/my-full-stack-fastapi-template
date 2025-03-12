"""
Code Analyzer for PlantUML

This module provides the main entry point for analyzing Python code and generating
PlantUML diagrams based on the code structure. It coordinates between the analyzer
and diagram generator components.

Features:
- Analyze Python files and directories
- Generate class and module diagrams
- Support for filtering and customization
- Progress reporting for large codebases
- Caching of analysis results
"""

import hashlib
import time
from pathlib import Path

from utils.puml.analyzer import analyze_directory, analyze_file
from utils.puml.core import setup_logger
from utils.puml.diagram_generator import (
    generate_class_diagram,
    generate_module_diagram,
    save_diagram,
)
from utils.puml.exceptions import (
    AnalyzerError,
    InvalidPathError,
    NoFilesAnalyzedError,
)
from utils.puml.models import Module
from utils.puml.settings import settings

# Set up logger with debug level for detailed logging
logger = setup_logger("code_analyzer", verbose=True)

# Cache for analyzed modules
_module_cache: dict[str, tuple[float, Module]] = {}


def _get_file_hash(path: Path) -> str:
    """Calculate hash of file contents for cache key."""
    try:
        content = path.read_bytes()
        return hashlib.md5(content).hexdigest()
    except Exception as e:
        logger.debug(f"Failed to calculate file hash: {e}")
        return ""


def _get_cached_module(path: Path) -> Module | None:
    """Get cached module if file hasn't changed."""
    try:
        file_hash = _get_file_hash(path)
        if not file_hash:
            return None

        cached = _module_cache.get(file_hash)
        if cached:
            mtime = path.stat().st_mtime
            if mtime <= cached[0]:
                logger.debug(f"Using cached analysis for {path}")
                return cached[1]

        return None
    except Exception as e:
        logger.debug(f"Cache lookup failed: {e}")
        return None


def _cache_module(path: Path, module: Module) -> None:
    """Cache analyzed module."""
    try:
        file_hash = _get_file_hash(path)
        if file_hash:
            _module_cache[file_hash] = (time.time(), module)
    except Exception as e:
        logger.debug(f"Failed to cache module: {e}")


def analyze_and_generate_diagram(
    path: str | Path = ".",
    output: str | Path | None = None,
    modules: bool = False,
    functions: bool = False,
) -> Path:
    """
    Analyze code and generate a PlantUML diagram.

    This is the main entry point for code analysis functionality.

    Args:
        path: Path to the Python file or directory to analyze
        output: Output file for the PlantUML diagram
        modules: Whether to generate a module diagram instead of a class diagram
        functions: Whether to include standalone functions in the class diagram

    Returns:
        Path to the generated diagram file

    Raises:
        InvalidPathError: If the provided path is invalid
        NoFilesAnalyzedError: If no Python files were successfully analyzed
        AnalyzerError: If there is an error during analysis
    """
    try:
        input_path = Path(path)
        analyzed_modules: list[Module] = []

        # Analyze the code
        if input_path.is_dir():
            logger.info(f"Analyzing directory: {input_path}")
            analyzed_modules = analyze_directory(input_path)
        elif input_path.is_file() and input_path.suffix == ".py":
            logger.info(f"Analyzing file: {input_path}")
            module = analyze_file(input_path)
            analyzed_modules = [module]
        else:
            logger.error(f"Invalid path: {input_path}")
            raise InvalidPathError(str(input_path))

        if not analyzed_modules:
            logger.error("No Python files were successfully analyzed")
            raise NoFilesAnalyzedError()

        # Generate the appropriate diagram
        if modules:
            diagram = generate_module_diagram(analyzed_modules)
            diagram_type = "module"
        else:
            diagram = generate_class_diagram(analyzed_modules, functions)
            diagram_type = "class"

        # Determine output path
        if output:
            output_path = Path(output)
        else:
            # Use default output file based on input path
            base_name = input_path.stem if input_path.is_file() else input_path.name
            output_path = (
                settings.output_dir
                / "code_analysis"
                / f"{base_name}_{diagram_type}_diagram.puml"
            )

        # Save the diagram
        save_diagram(diagram, output_path)
        logger.info(f"Generated {diagram_type} diagram: {output_path}")

        return output_path

    except (InvalidPathError, NoFilesAnalyzedError):
        raise
    except Exception as e:
        raise AnalyzerError(f"Error analyzing and generating diagram: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        analyze_and_generate_diagram(sys.argv[1])
    else:
        analyze_and_generate_diagram()
