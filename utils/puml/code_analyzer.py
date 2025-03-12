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

import concurrent.futures
import hashlib
import time
from collections.abc import Callable
from pathlib import Path

from utils.puml.analyzer import analyze_file
from utils.puml.core import setup_logger
from utils.puml.diagram_generator import (
    generate_class_diagram,
    generate_module_diagram,
    save_diagram,
)
from utils.puml.exceptions import (
    AnalyzerError,
    CacheError,
    FilterError,
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
    exclude_patterns: set[str] | None = None,
    max_workers: int = 4,
    include_private: bool = False,
    progress_callback: Callable[[int, int], None] | None = None,
) -> Path:
    """
    Analyze code and generate a PlantUML diagram.

    This is the main entry point for code analysis functionality.

    Args:
        path: Path to the Python file or directory to analyze
        output: Output file for the PlantUML diagram
        modules: Whether to generate a module diagram instead of a class diagram
        functions: Whether to include standalone functions in the class diagram
        exclude_patterns: Set of glob patterns for files/dirs to exclude
        max_workers: Maximum number of worker threads for parallel processing
        include_private: Whether to include private classes/methods
        progress_callback: Optional callback for progress updates

    Returns:
        Path to the generated diagram file

    Raises:
        InvalidPathError: If the provided path is invalid
        NoFilesAnalyzedError: If no Python files were successfully analyzed
        FilterError: If there is an error applying filters
        CacheError: If there is an error with the caching system
        AnalyzerError: If there is an error during analysis
    """
    try:
        input_path = Path(path)
        analyzed_modules: list[Module] = []
        exclude_patterns = exclude_patterns or settings.default_exclude_patterns
        total_files = 0
        processed_files = 0

        def update_progress(current: int, total: int) -> None:
            """Update progress through callback if provided."""
            if progress_callback:
                try:
                    progress_callback(current, total)
                except Exception as e:
                    logger.warning(f"Progress callback failed: {e}")

        # Analyze the code
        if input_path.is_dir():
            logger.info(f"Analyzing directory: {input_path}")
            logger.debug(f"Using exclude patterns: {exclude_patterns}")

            # Get list of Python files
            python_files = [
                f
                for f in input_path.rglob("*.py")
                if not any(f.match(pattern) for pattern in exclude_patterns)
            ]
            total_files = len(python_files)
            logger.info(f"Found {total_files} Python files to analyze")

            # Process files in parallel
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:
                future_to_file = {
                    executor.submit(analyze_file, f): f for f in python_files
                }

                for future in concurrent.futures.as_completed(future_to_file):
                    file = future_to_file[future]
                    try:
                        # Check cache first
                        module = _get_cached_module(file)
                        if not module:
                            module = future.result()
                            _cache_module(file, module)

                        if module:
                            analyzed_modules.append(module)
                    except Exception as e:
                        logger.warning(f"Failed to analyze {file}: {e}")

                    processed_files += 1
                    update_progress(processed_files, total_files)

        elif input_path.is_file() and input_path.suffix == ".py":
            logger.info(f"Analyzing file: {input_path}")

            # Check cache first
            module = _get_cached_module(input_path)
            if not module:
                module = analyze_file(input_path)
                _cache_module(input_path, module)

            if module:
                analyzed_modules = [module]
            update_progress(1, 1)
        else:
            error_msg = f"Invalid path: {input_path}"
            logger.error(error_msg)
            raise InvalidPathError(str(input_path))

        if not analyzed_modules:
            error_msg = "No Python files were successfully analyzed"
            logger.error(error_msg)
            raise NoFilesAnalyzedError()

        # Filter private members if requested
        if not include_private:
            logger.debug("Filtering private members")
            for module in analyzed_modules:
                # Filter private classes
                module.classes = {
                    name: cls
                    for name, cls in module.classes.items()
                    if not name.startswith("_") or name.startswith("__")
                }
                # Filter private methods in remaining classes
                for cls in module.classes.values():
                    cls.methods = {
                        name: method
                        for name, method in cls.methods.items()
                        if not name.startswith("_") or name.startswith("__")
                    }

        # Generate the appropriate diagram
        logger.info("Generating diagram")
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
        logger.debug(f"Analysis complete: {len(analyzed_modules)} modules processed")

        return output_path

    except (InvalidPathError, NoFilesAnalyzedError, CacheError, FilterError):
        raise
    except Exception as e:
        error_msg = f"Error analyzing and generating diagram: {e!s}"
        logger.error(error_msg)
        raise AnalyzerError(error_msg)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        analyze_and_generate_diagram(sys.argv[1])
    else:
        analyze_and_generate_diagram()
