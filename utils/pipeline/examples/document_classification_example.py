"""
Example script demonstrating document classification functionality.
"""

from pathlib import Path

from utils.pipeline.pipeline import Pipeline
from utils.pipeline.utils.progress import PipelineProgress


def main():
    """Run document classification example."""
    progress = PipelineProgress()

    try:
        # Get the current directory
        current_dir = Path(__file__).parent.parent

        # Set up paths
        input_dir = current_dir / "data" / "input"
        output_dir = current_dir / "data" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Display minimal setup info
        progress.display_success(f"Processing files from {input_dir}")

        # Initialize pipeline with configuration
        config = {
            "output_format": "json",  # Default format
            "enable_classification": True,  # Enable document classification
            "record_schemas": True,  # Record schemas for future matching
            "match_schemas": True,  # Match against known schemas
            "classification": {
                "type": "rule_based",  # Use rule-based classifier
                "confidence_threshold": 0.6,  # Minimum confidence threshold
            },
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

        # Process all PDF files in the input directory
        for pdf_file in input_dir.glob("*.pdf"):
            progress.display_success(f"Processing {pdf_file.name}")

            # Process the PDF with JSON output
            output_data = pipeline.run(str(pdf_file))

            # Save JSON output
            json_output = output_dir / f"{pdf_file.stem}.json"
            pipeline.save_output(output_data, str(json_output))
            progress.display_success(f"JSON output saved to: {json_output.name}")

            # Process the PDF with Markdown output
            pipeline.config["output_format"] = "markdown"
            output_data = pipeline.run(str(pdf_file))

            # Save Markdown output
            md_output = output_dir / f"{pdf_file.stem}.md"
            pipeline.save_output(output_data, str(md_output))
            progress.display_success(f"Markdown output saved to: {md_output.name}")

            # Display classification results
            if "classification" in output_data:
                classification = output_data["classification"]
                progress.display_success(
                    f"Document classified as: {classification['document_type']} "
                    f"(confidence: {classification['confidence']:.2f})"
                )
                progress.display_success(
                    f"Schema pattern: {classification['schema_pattern']}"
                )
                progress.display_success(
                    f"Key features: {', '.join(classification['key_features'])}"
                )

            # Reset output format for next file
            pipeline.config["output_format"] = "json"

        # Display final summary
        progress.display_success("Processing complete!")
        progress.display_success(
            f"Files Processed: {len(list(input_dir.glob('*.pdf')))}"
        )
        progress.display_success(
            f"Outputs Generated: {len(list(output_dir.glob('*.*')))}"
        )
        progress.display_success("Classification: Enabled")
        progress.display_success("Schema Recording: Enabled")

    except Exception as e:
        progress.display_error(f"Error processing documents: {e}")
        raise


if __name__ == "__main__":
    main()
