"""
Example script demonstrating PDF extraction pipeline usage.
"""

from pathlib import Path

from utils.pipeline.pipeline import Pipeline
from utils.pipeline.utils.progress import PipelineProgress


def main():
    """Run PDF extraction example."""
    progress = PipelineProgress()

    try:
        # Get the current directory
        current_dir = Path(__file__).parent.parent

        # TODO: Setup a runner for PDF extraction picking files and running the pipeline

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

        # Initialize pipeline with configuration
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
        }

        pipeline = Pipeline(config)

        # Process the PDF with JSON output
        progress.display_success("Starting JSON output processing")
        output_data = pipeline.run(str(input_file))

        # Save JSON output
        json_output = output_dir / "sample_output.json"
        pipeline.save_output(output_data, str(json_output))
        progress.display_success(f"JSON output saved to: {json_output.name}")

        # Process the PDF with Markdown output
        progress.display_success("Starting Markdown output processing")
        pipeline.config["output_format"] = "markdown"
        output_data = pipeline.run(str(input_file))

        # Save Markdown output
        md_output = output_dir / "sample_output.md"
        pipeline.save_output(output_data, str(md_output))
        progress.display_success(f"Markdown output saved to: {md_output.name}")

        # Display final summary
        progress.display_summary(
            {
                "JSON": {"path": str(json_output), "status": "Complete"},
                "Markdown": {"path": str(md_output), "status": "Complete"},
            }
        )

    except Exception as e:
        progress.display_error(f"Error processing PDF: {e}")
        raise


if __name__ == "__main__":
    main()
