"""
File processor module for handling batch processing of files through the pipeline.

This module provides functionality for discovering input files, processing them
through the pipeline, and generating output files in various formats.
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from utils.pipeline.pipeline import Pipeline
from utils.pipeline.utils.logging import get_logger
from utils.pipeline.utils.progress import PipelineProgress

# Default configuration
DEFAULT_CONFIG = {
    "file_processing": {
        "input": {
            "patterns": ["*.pdf"],
            "recursive": False,
            "exclude_patterns": [],
            "max_files": 0,
        },
        "output": {
            "formats": ["json"],
            "directory": "output",
            "structure": "flat",
            "naming": {
                "template": "{original_name}_{format}",
                "preserve_extension": False,
                "timestamp": False,
            },
            "overwrite": True,
        },
        "processing": {
            "batch_size": 10,
            "parallel": False,
            "continue_on_error": True,
            "error_handling": {
                "log_level": "error",
                "retry_count": 0,
                "retry_delay": 1,
            },
        },
        "reporting": {
            "summary": True,
            "detailed": True,
            "format": "json",
            "save_path": "processing_report.json",
        },
    }
}


class FileProcessor:
    """
    Handles batch processing of files through the pipeline.

    This class provides functionality for:
    1. Discovering input files based on patterns
    2. Processing files through the pipeline
    3. Generating output files in various formats
    4. Tracking progress and reporting results
    """

    def __init__(
        self,
        input_dir: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the file processor.

        Args:
            input_dir: Directory containing input files
            output_dir: Directory for output files (defaults to input_dir/output)
            config: Configuration dictionary
        """
        # Load and merge configuration
        self.config = self._load_config(config)

        # Set up directories
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir) if output_dir else self._get_output_dir()

        # Initialize pipeline with relevant config subset
        pipeline_config = self._extract_pipeline_config()
        self.pipeline = Pipeline(pipeline_config)

        # Set up logging
        self.logger = get_logger(__name__)

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(
            f"FileProcessor initialized with input_dir={self.input_dir}, "
            f"output_dir={self.output_dir}"
        )

    def _load_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Load and validate configuration."""
        # Start with defaults
        merged_config = DEFAULT_CONFIG.copy()

        # Merge with provided config
        if config:
            self._deep_update(merged_config, config)

        # Validate critical settings
        self._validate_config(merged_config)

        return merged_config

    def _deep_update(self, d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively update a dictionary."""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
        return d

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration settings."""
        # Check for required settings
        if not config.get("file_processing", {}).get("input", {}).get("patterns"):
            config["file_processing"]["input"]["patterns"] = ["*.pdf"]
            self.logger.warning("No input patterns specified, defaulting to '*.pdf'")

        # Validate output formats
        valid_formats = ["json", "markdown"]
        formats = config.get("file_processing", {}).get("output", {}).get("formats", [])

        valid_output_formats = []
        for fmt in formats:
            if fmt.lower() not in valid_formats:
                self.logger.warning(f"Unsupported format '{fmt}', will be ignored")
            else:
                valid_output_formats.append(fmt.lower())

        if not valid_output_formats:
            valid_output_formats = ["json"]
            config["file_processing"]["output"]["formats"] = valid_output_formats
            self.logger.warning(
                "No valid output formats specified, defaulting to 'json'"
            )

    def _extract_pipeline_config(self) -> Dict[str, Any]:
        """Extract pipeline-specific configuration."""
        pipeline_config = {}

        # TODO : Extract relevant keys from config and put in central pipeline config file or file processigning config

        # Copy relevant top-level keys
        for key in [
            "output_format",
            "strategies",
            "classification",
            "use_enhanced_markdown",
            "markdown_options",
        ]:
            if key in self.config:
                pipeline_config[key] = self.config[key]

        return pipeline_config

    def _get_output_dir(self) -> Path:
        """Get output directory from configuration or default."""
        output_config = self.config.get("file_processing", {}).get("output", {})
        output_dir = output_config.get("directory", "output")

        # If relative path, make it relative to input_dir
        if not os.path.isabs(output_dir):
            return self.input_dir / output_dir

        return Path(output_dir)

    def discover_files(self) -> List[Path]:
        """
        Discover input files based on configuration.

        Returns:
            List of file paths matching the configured patterns
        """
        input_config = self.config.get("file_processing", {}).get("input", {})

        # Get patterns and exclusions
        patterns = input_config.get("patterns", ["*.pdf"])
        exclude_patterns = input_config.get("exclude_patterns", [])
        recursive = input_config.get("recursive", False)
        max_files = input_config.get("max_files", 0)

        # Collect all matching files
        all_files = []

        for pattern in patterns:
            # Handle recursive vs non-recursive
            if recursive:
                glob_pattern = f"**/{pattern}"
            else:
                glob_pattern = pattern

            # Find matching files
            matches = list(self.input_dir.glob(glob_pattern))
            all_files.extend(matches)

        # Filter out directories and excluded patterns
        files = []
        for file_path in all_files:
            if not file_path.is_file():
                continue

            # Check exclusions
            excluded = False
            for exclude in exclude_patterns:
                if file_path.match(exclude):
                    excluded = True
                    break

            if not excluded:
                files.append(file_path)

        # Sort files for consistent processing order
        files.sort()

        # Apply max_files limit if specified
        if max_files > 0 and len(files) > max_files:
            self.logger.warning(
                f"Found {len(files)} files, limiting to {max_files} as configured"
            )
            files = files[:max_files]

        self.logger.info(f"Discovered {len(files)} files for processing")
        return files

    def create_output_path(self, input_file: Path, format_name: str) -> Path:
        """
        Create output path based on configuration.

        Args:
            input_file: Input file path
            format_name: Output format name (e.g., 'json', 'markdown')

        Returns:
            Path object for the output file
        """
        output_config = self.config.get("file_processing", {}).get("output", {})

        # Get naming configuration
        naming = output_config.get("naming", {})
        template = naming.get("template", "{original_name}_{format}")
        preserve_ext = naming.get("preserve_extension", False)
        add_timestamp = naming.get("timestamp", False)

        # Get structure type
        structure = output_config.get("structure", "flat")

        # Prepare filename components
        original_name = input_file.stem
        if preserve_ext:
            original_name = input_file.name

        # Add timestamp if configured
        timestamp = ""
        if add_timestamp:
            timestamp = datetime.now().strftime("_%Y%m%d%H%M%S")

        # Format the filename using template
        filename = template.format(
            original_name=original_name,
            format=format_name,
            timestamp=timestamp,
            type=self._detect_document_type(input_file),
        )

        # Add appropriate extension
        if format_name == "json":
            filename = f"{filename}.json"
        elif format_name == "markdown":
            filename = f"{filename}.md"

        # Determine directory based on structure
        if structure == "flat":
            # All files in the output directory
            output_path = self.output_dir / filename

        elif structure == "hierarchical":
            # Organize by document type and format
            doc_type = self._detect_document_type(input_file)
            output_path = self.output_dir / doc_type / format_name / filename

        elif structure == "mirror":
            # Mirror the input directory structure
            try:
                rel_path = input_file.relative_to(self.input_dir)
                output_path = self.output_dir / rel_path.parent / filename
            except ValueError:
                # If input_file is not relative to input_dir, use flat structure
                output_path = self.output_dir / filename

        else:
            # Default to flat structure
            output_path = self.output_dir / filename

        # Create parent directories
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle existing files
        if output_path.exists() and not output_config.get("overwrite", True):
            # Add numeric suffix if overwrite is disabled
            counter = 1
            while output_path.exists():
                stem = output_path.stem
                suffix = output_path.suffix
                output_path = output_path.with_name(f"{stem}_{counter}{suffix}")
                counter += 1

        return output_path

    def _detect_document_type(self, file_path: Path) -> str:
        """
        Detect document type based on file extension.

        Args:
            file_path: Path to the file

        Returns:
            Document type string (e.g., 'pdf', 'excel')
        """
        ext = file_path.suffix.lower()

        if ext == ".pdf":
            return "pdf"
        elif ext in [".xlsx", ".xls"]:
            return "excel"
        elif ext in [".docx", ".doc"]:
            return "word"
        elif ext == ".txt":
            return "text"
        else:
            return "generic"

    def generate_outputs(
        self, input_file: Path, output_data: Dict[str, Any]
    ) -> List[str]:
        """
        Generate output files in all configured formats.

        Args:
            input_file: Input file path
            output_data: Processed data from pipeline

        Returns:
            List of output file paths
        """
        formats = (
            self.config.get("file_processing", {})
            .get("output", {})
            .get("formats", ["json"])
        )
        output_paths = []

        for format_name in formats:
            # Save original output format
            original_format = self.pipeline.config.get("output_format")

            try:
                # Set pipeline output format
                self.pipeline.config["output_format"] = format_name.upper()

                # Create output path
                output_path = self.create_output_path(input_file, format_name)

                # Save output
                self.pipeline.save_output(output_data, str(output_path))
                output_paths.append(str(output_path))

                self.logger.info(f"Generated {format_name} output: {output_path}")

            except Exception as e:
                self.logger.error(f"Failed to generate {format_name} output: {str(e)}")

            finally:
                # Restore original output format
                self.pipeline.config["output_format"] = original_format

        return output_paths

    def process_all_files(self) -> List[Dict[str, Any]]:
        """
        Process all discovered files according to configuration.

        Returns:
            List of result dictionaries with processing status and outputs
        """
        # Get processing configuration
        proc_config = self.config.get("file_processing", {}).get("processing", {})
        continue_on_error = proc_config.get("continue_on_error", True)

        # Discover files
        files = self.discover_files()
        if not files:
            self.logger.warning("No matching files found")
            return []

        # Initialize progress tracking
        progress = PipelineProgress()
        results = []

        with progress:
            # Add overall progress tracking
            overall_task = progress.add_task(
                f"Processing {len(files)} files", total=len(files)
            )

            # Process each file
            for file in files:
                try:
                    progress.display_success(f"Processing {file.name}")

                    # Process the file without progress display
                    output_data = self.pipeline.run(str(file), show_progress=False)

                    # Generate outputs in all configured formats
                    output_paths = self.generate_outputs(file, output_data)

                    # Record result
                    results.append(
                        {
                            "file": str(file),
                            "status": "success",
                            "outputs": output_paths,
                        }
                    )

                    progress.display_success(f"Successfully processed {file.name}")

                except Exception as e:
                    error_msg = f"Error processing {file.name}: {str(e)}"
                    self.logger.error(error_msg, exc_info=True)
                    progress.display_error(error_msg)

                    # Record failure
                    results.append(
                        {"file": str(file), "status": "error", "error": str(e)}
                    )

                    # Stop processing if configured to do so
                    if not continue_on_error:
                        progress.display_error(
                            "Stopping due to error (continue_on_error=False)"
                        )
                        break

                finally:
                    # Update overall progress
                    progress.update(overall_task, advance=1)

        # Generate report if configured
        if (
            self.config.get("file_processing", {})
            .get("reporting", {})
            .get("summary", True)
        ):
            self.generate_report(results)

        return results

    def process_single_file(
        self, input_file: Union[str, Path], output_format: Optional[str] = None
    ) -> Tuple[Dict[str, Any], str]:
        """
        Process a single file (for backward compatibility).

        Args:
            input_file: Path to input file
            output_format: Optional output format override

        Returns:
            Tuple of (output_data, output_path)
        """
        input_path = Path(input_file)

        # Override output format if specified
        original_format = self.pipeline.config.get("output_format")
        if output_format:
            self.pipeline.config["output_format"] = output_format.upper()

        try:
            # Process the file without progress display
            output_data = self.pipeline.run(str(input_path), show_progress=False)

            # Generate output with specified format
            format_name = (
                output_format.lower()
                if output_format
                else (original_format.lower() if original_format else "json")
            )
            output_path = self.create_output_path(input_path, format_name)
            self.pipeline.save_output(output_data, str(output_path))

            return output_data, str(output_path)

        finally:
            # Restore original format
            if output_format:
                self.pipeline.config["output_format"] = original_format

    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate processing report based on configuration.

        Args:
            results: List of processing results

        Returns:
            Path to the generated report
        """
        report_config = self.config.get("file_processing", {}).get("reporting", {})

        # Skip if reporting is disabled
        if not report_config.get("summary", True) and not report_config.get(
            "detailed", False
        ):
            return ""

        # Prepare report data
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": len(results),
                "successful": sum(1 for r in results if r["status"] == "success"),
                "failed": sum(1 for r in results if r["status"] == "error"),
            },
        }

        # Add detailed information if configured
        if report_config.get("detailed", False):
            report["details"] = results

        # Determine report format and path
        format_name = report_config.get("format", "json")
        save_path = report_config.get("save_path", "processing_report.json")

        # Ensure path is absolute
        if not os.path.isabs(save_path):
            save_path = os.path.join(str(self.output_dir), save_path)

        # Create directory if needed
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

        # Save report
        with open(save_path, "w") as f:
            if format_name == "json":
                json.dump(report, f, indent=2)
            elif format_name == "csv" and report_config.get("detailed", False):
                # Simple CSV export for detailed reports
                writer = csv.writer(f)
                writer.writerow(["file", "status", "outputs", "error"])
                for item in results:
                    writer.writerow(
                        [
                            item["file"],
                            item["status"],
                            ",".join(item.get("outputs", [])),
                            item.get("error", ""),
                        ]
                    )
            else:
                # Default to simple text format
                f.write("Processing Report\n")
                f.write(f"Timestamp: {report['timestamp']}\n")
                f.write(f"Total Files: {report['summary']['total_files']}\n")
                f.write(f"Successful: {report['summary']['successful']}\n")
                f.write(f"Failed: {report['summary']['failed']}\n")

        self.logger.info(f"Report saved to {save_path}")
        return save_path
