"""
Main pipeline orchestrator module.

This module provides the core pipeline functionality for document processing.
"""

import importlib
import os
from typing import Any, Dict, Optional

from utils.pipeline.processors.formatters.factory import FormatterFactory, OutputFormat
from utils.pipeline.utils.logging import get_logger
from utils.pipeline.utils.progress import PipelineProgress
from utils.pipeline.verify.factory import VerifierFactory, VerifierType


class Pipeline:
    """
    Main pipeline orchestrator that manages the flow of document processing.

    The pipeline follows these steps:
    1. Analyze document structure
    2. Clean and normalize content
    3. Extract structured data
    4. Validate extracted data
    5. Format output
    6. Verify output structure
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the pipeline with configuration.

        Args:
            config: Configuration dictionary with pipeline settings
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Initialize strategy selector
        self.strategy_selector = StrategySelector(self.config)

        self.logger.info("Pipeline initialized with config: %s", self.config)

    def run(self, input_path: str, show_progress: bool = True) -> Dict[str, Any]:
        """
        Run the pipeline on the input document.

        Args:
            input_path: Path to the input document
            show_progress: Whether to display progress bars (default: True)

        Returns:
            Processed output data as a dictionary
        """
        self.logger.info("Starting pipeline processing for: %s", input_path)
        progress = PipelineProgress()

        try:
            if not show_progress:
                # Process without progress display
                doc_type = self._detect_document_type(input_path)
                strategies = self.strategy_selector.get_strategies(doc_type)

                # Track stage outputs
                stages_data = {}
                stages_data["setup"] = {"path": input_path, "type": doc_type}

                # 1. Analyze document structure
                analysis_result = self._analyze_document(
                    input_path, strategies.analyzer
                )
                stages_data["analyze"] = analysis_result

                # 2. Clean and normalize content
                cleaned_data = self._clean_content(analysis_result, strategies.cleaner)
                stages_data["clean"] = cleaned_data

                # 3. Extract structured data
                extracted_data = self._extract_data(cleaned_data, strategies.extractor)
                stages_data["extract"] = extracted_data

                # 4. Validate extracted data
                validated_data = self._validate_data(
                    extracted_data, strategies.validator
                )
                stages_data["validate"] = validated_data

                # 5. Format output
                output_format = self._get_output_format()
                output_data = self._format_output(validated_data, output_format)
                stages_data["format"] = output_data

                # 6. Verify output structure
                self._verify_output_structure(output_data, output_format)

                return output_data

            # Process with progress display
            with progress:
                progress.start()
                overall_task = progress.add_task("Processing document", total=6)

                # Determine document type and select appropriate strategies
                doc_type = self._detect_document_type(input_path)
                self.logger.info("Detected document type: %s", doc_type)
                strategies = self.strategy_selector.get_strategies(doc_type)

                # Track stage outputs
                stages_data = {}

                # Initial document info
                stages_data["setup"] = {"path": input_path, "type": doc_type}
                progress.display_success(f"Processing {os.path.basename(input_path)}")

                # 1. Analyze document structure
                analyze_task = progress.add_task("Step 1: Analyzing document structure")
                analysis_result = self._analyze_document(
                    input_path, strategies.analyzer
                )
                stages_data["analyze"] = analysis_result
                progress.update(analyze_task, advance=1)
                progress.update(overall_task, advance=1)
                progress.display_success("Document structure analyzed")

                # 2. Clean and normalize content
                clean_task = progress.add_task(
                    "Step 2: Cleaning and normalizing content"
                )
                cleaned_data = self._clean_content(analysis_result, strategies.cleaner)
                stages_data["clean"] = cleaned_data
                progress.update(clean_task, advance=1)
                progress.update(overall_task, advance=1)
                progress.display_success("Content cleaned and normalized")

                # 3. Extract structured data
                extract_task = progress.add_task("Step 3: Extracting structured data")
                extracted_data = self._extract_data(cleaned_data, strategies.extractor)
                stages_data["extract"] = extracted_data
                progress.update(extract_task, advance=1)
                progress.update(overall_task, advance=1)
                progress.display_success("Data extracted")

                # 4. Validate extracted data
                validate_task = progress.add_task("Step 4: Validating extracted data")
                validated_data = self._validate_data(
                    extracted_data, strategies.validator
                )
                stages_data["validate"] = validated_data
                progress.update(validate_task, advance=1)
                progress.update(overall_task, advance=1)
                progress.display_success("Data validated")

                # 5. Format output
                format_task = progress.add_task("Step 5: Formatting output")
                output_format = self._get_output_format()
                output_data = self._format_output(validated_data, output_format)
                stages_data["format"] = output_data
                progress.update(format_task, advance=1)
                progress.update(overall_task, advance=1)
                progress.display_success("Output formatted")

                # 6. Verify output structure
                verify_task = progress.add_task("Step 6: Verifying output structure")
                self._verify_output_structure(output_data, output_format)
                progress.update(verify_task, advance=1)
                progress.update(overall_task, advance=1)

                # Show concise summary
                summary = {
                    "sections": len(output_data.get("content", [])),
                    "tables": len(output_data.get("tables", [])),
                    "validation": output_data.get("validation", {}),
                }
                progress.display_summary(summary)
                progress.display_success("Pipeline processing completed successfully")
                return output_data

        except Exception as e:
            error_msg = f"Pipeline processing failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            progress.display_error(error_msg)
            raise PipelineError(error_msg) from e

    def _detect_document_type(self, input_path: str) -> str:
        """Detect the document type based on file extension or content analysis."""
        _, ext = os.path.splitext(input_path)
        ext = ext.lower()

        if ext == ".pdf":
            return "pdf"
        elif ext in [".xlsx", ".xls"]:
            return "excel"
        elif ext in [".docx", ".doc"]:
            return "word"
        elif ext == ".txt":
            return "text"
        else:
            # Default to generic type
            return "generic"

    def _analyze_document(self, input_path: str, analyzer) -> Dict[str, Any]:
        """Analyze document structure and content."""
        return analyzer.analyze(input_path)

    def _clean_content(
        self, analysis_result: Dict[str, Any], cleaner
    ) -> Dict[str, Any]:
        """Clean and normalize document content."""
        return cleaner.clean(analysis_result)

    def _extract_data(self, cleaned_data: Dict[str, Any], extractor) -> Dict[str, Any]:
        """Extract structured data from cleaned content."""
        return extractor.extract(cleaned_data)

    def _validate_data(
        self, extracted_data: Dict[str, Any], validator
    ) -> Dict[str, Any]:
        """Validate extracted data against schemas."""
        return validator.validate(extracted_data)

    def _format_output(
        self, validated_data: Dict[str, Any], output_format: OutputFormat
    ) -> Dict[str, Any]:
        """Format validated data using the specified formatter."""
        formatter = FormatterFactory.create_formatter(output_format)
        return formatter.format(validated_data)

    def _verify_output_structure(
        self, output_data: Dict[str, Any], output_format: OutputFormat
    ) -> None:
        """
        Verify the structure of formatted output.

        Args:
            output_data: Formatted output data to verify
            output_format: Format type of the output

        Raises:
            PipelineError: If verification fails
        """
        # Map output format to verifier type
        verifier_map = {
            OutputFormat.JSON: VerifierType.JSON_TREE,
            OutputFormat.MARKDOWN: VerifierType.MARKDOWN,
        }

        verifier_type = verifier_map.get(output_format)
        if not verifier_type:
            self.logger.warning(f"No verifier available for format: {output_format}")
            return

        try:
            verifier = VerifierFactory.create_verifier(verifier_type)
            is_valid, errors, warnings = verifier.verify(output_data)

            # Log warnings
            for warning in warnings:
                self.logger.warning(f"Structure warning: {warning}")

            # Raise error if validation failed
            if not is_valid:
                error_msg = "\n".join(errors)
                raise PipelineError(
                    f"Output structure verification failed:\n{error_msg}"
                )

        except ValueError as e:
            self.logger.warning(f"Verification skipped: {str(e)}")

    def _get_output_format(self) -> OutputFormat:
        """Get output format from config or use default."""
        format_name = self.config.get("output_format", "json").upper()
        try:
            return OutputFormat[format_name]
        except KeyError:
            self.logger.warning(f"Unsupported output format: {format_name}, using JSON")
            return OutputFormat.JSON

    def save_output(self, output_data: Dict[str, Any], output_path: str) -> None:
        """Save the output data to a file."""
        self.logger.info("Saving output to: %s", output_path)

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Get formatter based on file extension
        output_format = self._get_format_from_path(output_path)
        formatter = FormatterFactory.create_formatter(output_format)

        # Format and write the data
        formatter.write(output_data, output_path)

    def _get_format_from_path(self, path: str) -> OutputFormat:
        """Determine output format from file extension."""
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        format_map = {
            ".json": OutputFormat.JSON,
            ".md": OutputFormat.MARKDOWN,
            ".markdown": OutputFormat.MARKDOWN,
        }

        return format_map.get(ext, OutputFormat.JSON)


class StrategySelector:
    """Selects appropriate processing strategies based on document type."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(__name__ + ".StrategySelector")

    def get_strategies(self, doc_type: str) -> "StrategySet":
        """Get the set of strategies for a document type."""
        self.logger.info("Selecting strategies for document type: %s", doc_type)

        try:
            # Get strategy paths from config
            strategy_paths = self.config.get("strategies", {})
            if not strategy_paths:
                raise ImportError("No strategy paths configured")

            # Get the strategy paths for this document type
            doc_strategies = strategy_paths.get(doc_type)
            if not doc_strategies:
                raise ImportError(f"No strategy paths configured for {doc_type}")

            # If the strategy is a string, use it as a legacy format
            if isinstance(doc_strategies, str):
                return self._get_legacy_strategies(doc_strategies)

            # Import each strategy component
            analyzer = self._import_strategy(doc_strategies.get("analyzer"))
            cleaner = self._import_strategy(doc_strategies.get("cleaner"))
            extractor = self._import_strategy(doc_strategies.get("extractor"))
            validator = self._import_strategy(doc_strategies.get("validator"))

            return StrategySet(
                analyzer=analyzer,
                cleaner=cleaner,
                extractor=extractor,
                validator=validator,
                formatter=None,  # Formatter now handled by factory
            )

        except (ImportError, AttributeError) as e:
            self.logger.error(
                "Failed to import strategies for %s: %s", doc_type, str(e)
            )
            # Fall back to mock strategies for now
            return StrategySet(
                analyzer=MockStrategy(),
                cleaner=MockStrategy(),
                extractor=MockStrategy(),
                validator=MockStrategy(),
                formatter=None,
            )

    def _import_strategy(self, strategy_path: Optional[str]) -> Any:
        """Import a strategy class and create an instance."""
        if not strategy_path:
            return MockStrategy()

        try:
            module_path, class_name = strategy_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            strategy_class = getattr(module, class_name)
            return strategy_class()
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to import strategy {strategy_path}: {str(e)}")
            return MockStrategy()

    def _get_legacy_strategies(self, strategy_path: str) -> "StrategySet":
        """Handle legacy format where all strategies come from one module."""
        try:
            module_path = strategy_path
            module = importlib.import_module(module_path)

            return StrategySet(
                analyzer=module.Analyzer(),
                cleaner=module.Cleaner(),
                extractor=module.Extractor(),
                validator=module.Validator(),
                formatter=None,
            )
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to import legacy strategies: {str(e)}")
            return StrategySet(
                analyzer=MockStrategy(),
                cleaner=MockStrategy(),
                extractor=MockStrategy(),
                validator=MockStrategy(),
                formatter=None,
            )


class StrategySet:
    """A set of strategies for processing a document."""

    def __init__(self, analyzer, cleaner, extractor, validator, formatter):
        self.analyzer = analyzer
        self.cleaner = cleaner
        self.extractor = extractor
        self.validator = validator
        self.formatter = formatter


class MockStrategy:
    """A mock strategy for testing or when real strategies are not available."""

    def analyze(self, input_path):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File not found: {input_path}")
        return {"mock_analysis": True, "path": input_path}

    def clean(self, data):
        return {"mock_cleaned": True, "data": data}

    def extract(self, data):
        return {"mock_extracted": True, "data": data}

    def validate(self, data):
        return {"mock_validated": True, "data": data}


class PipelineError(Exception):
    """Exception raised for errors in the pipeline processing."""

    pass
