import logging
import os
from typing import Any, Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Pipeline:
    """
    Main pipeline orchestrator that manages the flow of document processing.

    The pipeline follows these steps:
    1. Analyze document structure
    2. Clean and normalize content
    3. Extract structured data
    4. Validate extracted data
    5. Format output
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the pipeline with configuration.

        Args:
            config: Configuration dictionary with pipeline settings
        """
        self.config = config or {}
        self.logger = logger

        # Initialize strategy selector
        self.strategy_selector = StrategySelector(self.config)

        self.logger.info("Pipeline initialized with config: %s", self.config)

    def run(self, input_path: str) -> Dict[str, Any]:
        """
        Run the pipeline on the input document.

        Args:
            input_path: Path to the input document

        Returns:
            Processed output data as a dictionary
        """
        self.logger.info("Starting pipeline processing for: %s", input_path)

        try:
            # Determine document type and select appropriate strategies
            doc_type = self._detect_document_type(input_path)
            self.logger.info("Detected document type: %s", doc_type)

            strategies = self.strategy_selector.get_strategies(doc_type)

            # 1. Analyze document structure
            self.logger.info("Step 1: Analyzing document structure")
            analysis_result = self._analyze_document(input_path, strategies.analyzer)

            # 2. Clean and normalize content
            self.logger.info("Step 2: Cleaning and normalizing content")
            cleaned_data = self._clean_content(analysis_result, strategies.cleaner)

            # 3. Extract structured data
            self.logger.info("Step 3: Extracting structured data")
            extracted_data = self._extract_data(cleaned_data, strategies.extractor)

            # 4. Validate extracted data
            self.logger.info("Step 4: Validating extracted data")
            validated_data = self._validate_data(extracted_data, strategies.validator)

            # 5. Format output
            self.logger.info("Step 5: Formatting output")
            output_data = self._format_output(validated_data, strategies.formatter)

            self.logger.info("Pipeline processing completed successfully")
            return output_data

        except Exception as e:
            self.logger.error("Pipeline processing failed: %s", str(e), exc_info=True)
            raise PipelineError(f"Pipeline processing failed: {str(e)}") from e

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
        self, validated_data: Dict[str, Any], formatter
    ) -> Dict[str, Any]:
        """Format validated data for output."""
        return formatter.format(validated_data)

    def save_output(self, output_data: Dict[str, Any], output_path: str) -> None:
        """Save the output data to a file."""
        self.logger.info("Saving output to: %s", output_path)

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Determine output format based on file extension
        _, ext = os.path.splitext(output_path)
        ext = ext.lower()

        if ext == ".yaml" or ext == ".yml":
            self._save_yaml(output_data, output_path)
        elif ext == ".json":
            self._save_json(output_data, output_path)
        else:
            # Default to YAML
            self._save_yaml(output_data, output_path)

    def _save_yaml(self, data: Dict[str, Any], path: str) -> None:
        """Save data as YAML."""
        import yaml

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

    def _save_json(self, data: Dict[str, Any], path: str) -> None:
        """Save data as JSON."""
        import json

        with open(path, "w") as f:
            json.dump(data, f, indent=2)


class StrategySelector:
    """Selects appropriate processing strategies based on document type."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__ + ".StrategySelector")

    def get_strategies(self, doc_type: str) -> "StrategySet":
        """Get the set of strategies for a document type."""
        self.logger.info("Selecting strategies for document type: %s", doc_type)

        # Import strategies dynamically based on document type
        try:
            # This would be replaced with actual dynamic imports in a real implementation
            if doc_type == "pdf":
                from strategies.pdf import (
                    PDFAnalyzer,
                    PDFCleaner,
                    PDFExtractor,
                    PDFFormatter,
                    PDFValidator,
                )

                return StrategySet(
                    analyzer=PDFAnalyzer(),
                    cleaner=PDFCleaner(),
                    extractor=PDFExtractor(),
                    validator=PDFValidator(),
                    formatter=PDFFormatter(),
                )
            elif doc_type == "excel":
                from strategies.excel import (
                    ExcelAnalyzer,
                    ExcelCleaner,
                    ExcelExtractor,
                    ExcelFormatter,
                    ExcelValidator,
                )

                return StrategySet(
                    analyzer=ExcelAnalyzer(),
                    cleaner=ExcelCleaner(),
                    extractor=ExcelExtractor(),
                    validator=ExcelValidator(),
                    formatter=ExcelFormatter(),
                )
            elif doc_type == "word":
                from strategies.word import (
                    WordAnalyzer,
                    WordCleaner,
                    WordExtractor,
                    WordFormatter,
                    WordValidator,
                )

                return StrategySet(
                    analyzer=WordAnalyzer(),
                    cleaner=WordCleaner(),
                    extractor=WordExtractor(),
                    validator=WordValidator(),
                    formatter=WordFormatter(),
                )
            else:
                # Default to generic strategies
                from strategies.generic import (
                    GenericAnalyzer,
                    GenericCleaner,
                    GenericExtractor,
                    GenericFormatter,
                    GenericValidator,
                )

                return StrategySet(
                    analyzer=GenericAnalyzer(),
                    cleaner=GenericCleaner(),
                    extractor=GenericExtractor(),
                    validator=GenericValidator(),
                    formatter=GenericFormatter(),
                )
        except ImportError as e:
            self.logger.error(
                "Failed to import strategies for %s: %s", doc_type, str(e)
            )
            # Fall back to mock strategies for now
            return StrategySet(
                analyzer=MockStrategy(),
                cleaner=MockStrategy(),
                extractor=MockStrategy(),
                validator=MockStrategy(),
                formatter=MockStrategy(),
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
        return {"mock_analysis": True, "path": input_path}

    def clean(self, data):
        return {"mock_cleaned": True, "data": data}

    def extract(self, data):
        return {"mock_extracted": True, "data": data}

    def validate(self, data):
        return {"mock_validated": True, "data": data}

    def format(self, data):
        return {"mock_formatted": True, "data": data}


class PipelineError(Exception):
    """Exception raised for errors in the pipeline processing."""

    pass
