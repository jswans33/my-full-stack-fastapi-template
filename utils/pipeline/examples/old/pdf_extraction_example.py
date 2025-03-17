"""
Example script demonstrating PDF extraction pipeline usage.

This example shows how to process a single PDF file using the FileProcessor
for backward compatibility with the original example.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow relative imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from utils.pipeline.core.file_processor import FileProcessor
from utils.pipeline.utils.progress import PipelineProgress


def main():
    """Run PDF extraction example."""
    progress = PipelineProgress()

    try:
        # Get the current directory
        current_dir = Path(__file__).parent.parent

        # Set up paths
        input_file = (
            current_dir
            / "data"
            / "input"
            / "Quotation 79520-4 - Rocky Vista HS 100%CD (25-03-12).pdf"
        )
        output_dir = current_dir / "data" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Display minimal setup info
        progress.display_success(f"Processing {input_file.name}")

        # Initialize configuration
        config = {
            "output_format": "json",  # Default format
            "strategies": {
                "pdf": {
                    "analyzer": "utils.pipeline.analyzer.pdf.PDFAnalyzer",
                    "cleaner": "utils.pipeline.cleaner.pdf.PDFCleaner",
                    "extractor": "utils.pipeline.processors.pdf_extractor.PDFExtractor",
                    "validator": "utils.pipeline.processors.pdf_validator.PDFValidator",
                },
            },
            "file_processing": {
                "output": {
                    "formats": ["json", "markdown"],  # Support both formats
                    "naming": {
                        "template": "sample_output",  # Use fixed name for backward compatibility
                    },
                    "overwrite": True,
                },
            },
        }

        # Initialize file processor
        processor = FileProcessor(current_dir, output_dir, config)

        # Process the PDF with JSON output
        progress.display_success("Starting JSON output processing")
        json_data, json_path = processor.process_single_file(input_file, "json")
        progress.display_success(f"JSON output saved to: {Path(json_path).name}")

        # Process the PDF with Markdown output
        progress.display_success("Starting Markdown output processing")
        md_data, md_path = processor.process_single_file(input_file, "markdown")
        progress.display_success(f"Markdown output saved to: {Path(md_path).name}")

        # Display final summary
        progress.display_summary(
            {
                "JSON": {"path": json_path, "status": "Complete"},
                "Markdown": {"path": md_path, "status": "Complete"},
            }
        )

    except Exception as e:
        progress.display_error(f"Error processing PDF: {e}")
        raise


if __name__ == "__main__":
    main()
