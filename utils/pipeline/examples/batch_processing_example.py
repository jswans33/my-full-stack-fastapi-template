"""
Example script demonstrating batch PDF extraction using the FileProcessor.

This example shows how to process multiple PDF files from an input directory
and generate output files in various formats.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow relative imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from utils.pipeline.core.file_processor import FileProcessor
from utils.pipeline.utils.progress import PipelineProgress


def main():
    """Run batch PDF extraction example."""
    progress = PipelineProgress()

    try:
        # Get the current directory
        current_dir = Path(__file__).parent.parent

        # Set up paths
        input_dir = current_dir / "data" / "input"
        output_dir = current_dir / "data" / "output"

        # Display setup info
        progress.display_success(f"Processing files from {input_dir}")

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
                "input": {
                    "patterns": ["*.pdf"],  # Process all PDF files
                    "recursive": False,  # Don't search subdirectories
                },
                "output": {
                    "formats": ["json", "markdown"],  # Generate both formats
                    "directory": str(output_dir),
                    "structure": "flat",  # All files in the same directory
                    "naming": {
                        "template": "{original_name}",  # Use original filename
                    },
                    "overwrite": True,  # Overwrite existing files
                },
                "reporting": {
                    "summary": True,
                    "detailed": True,
                    "format": "json",
                    "save_path": "processing_report.json",
                },
            },
        }

        # Initialize file processor
        processor = FileProcessor(input_dir, output_dir, config)

        # Process all files
        results = processor.process_all_files()

        # Display final summary
        summary = {
            f"{r['file']}": {
                "status": r["status"],
                "outputs": r.get("outputs", []),
            }
            for r in results
        }
        progress.display_summary(summary)

    except Exception as e:
        progress.display_error(f"Error processing files: {e}")
        raise


if __name__ == "__main__":
    main()
