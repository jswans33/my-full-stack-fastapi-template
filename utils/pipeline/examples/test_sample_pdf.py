"""
Test script for processing the sample.pdf file.

This script demonstrates how to process the sample PDF file using the existing
configuration files and the pipeline's run_pipeline module.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow relative imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import yaml

from utils.pipeline.pipeline import Pipeline
from utils.pipeline.utils.progress import PipelineProgress


def load_config():
    """Load configuration from example config files."""
    current_dir = Path(__file__).parent.parent

    # Load base configuration
    config_path = current_dir / "config" / "example_config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Load classifier configuration
    classifier_config_path = current_dir / "config" / "example_classifier_config.yaml"
    with open(classifier_config_path, "r") as f:
        classifier_config = yaml.safe_load(f)

    # Merge configurations
    config.update(classifier_config)

    # Update paths for this specific test
    config["input_dir"] = str(current_dir / "data" / "tests" / "pdf")
    config["output_dir"] = str(current_dir / "data" / "output")

    return config


def main():
    """Run sample PDF test."""
    progress = PipelineProgress()

    try:
        # Get the current directory
        current_dir = Path(__file__).parent.parent

        # Set up paths
        input_file = current_dir / "data" / "tests" / "pdf" / "sample.pdf"
        output_dir = current_dir / "data" / "output"

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Display setup info
        progress.display_success(f"Processing {input_file.name}")
        progress.display_success(f"Input file path: {input_file}")
        progress.display_success(f"Output directory: {output_dir}")

        # Load configuration
        config = load_config()
        progress.display_success("Configuration loaded")

        # Initialize pipeline
        pipeline = Pipeline(config)
        progress.display_success("Pipeline initialized")

        # Process the PDF
        progress.display_success("Starting pipeline processing...")
        result = pipeline.run(str(input_file))

        # Save output in different formats
        json_path = output_dir / f"{input_file.stem}.json"
        pipeline.save_output(result, str(json_path))
        progress.display_success(f"JSON output saved to: {json_path.name}")

        # For Markdown output, we need to use the run_pipeline.py script directly
        # since there's an issue with the Markdown formatter
        try:
            import subprocess

            md_path = output_dir / f"{input_file.stem}.md"
            cmd = [
                "python",
                "-m",
                "utils.pipeline.run_pipeline",
                "--file",
                str(input_file),
                "--output",
                str(output_dir),
                "--formats",
                "markdown",
            ]

            subprocess_result = subprocess.run(cmd, capture_output=True, text=True)
            if subprocess_result.returncode == 0:
                progress.display_success(f"Markdown output saved to: {md_path.name}")
            else:
                progress.display_error(
                    f"Error saving Markdown output: {subprocess_result.stderr}"
                )
        except Exception as e:
            progress.display_error(f"Error saving Markdown output: {str(e)}")
            progress.display_error("This is a known issue with the Markdown formatter.")
            progress.display_error("You can use the pipeline_test.bat script instead.")

        # Display classification results
        if "document_type" in result:
            progress.display_success("\nClassification Results:")
            progress.display_success(f"Document Type: {result['document_type']}")
            progress.display_success(f"Confidence: {result.get('confidence', 0):.2f}")
            progress.display_success(
                f"Schema Pattern: {result.get('schema_pattern', 'N/A')}"
            )

            if "key_features" in result:
                progress.display_success("\nKey Features:")
                for feature in result["key_features"]:
                    progress.display_success(f"- {feature}")

            if "classifiers" in result:
                progress.display_success("\nClassifiers Used:")
                for classifier in result["classifiers"]:
                    progress.display_success(f"- {classifier}")

        # Display summary
        progress.display_summary(
            {
                "Input File": {"path": str(input_file), "status": "Processed"},
                "JSON Output": {"path": str(json_path), "status": "Complete"},
                "Markdown Output": {"path": str(md_path), "status": "Complete"},
                "Classification": {
                    "document_type": result.get("document_type", "Unknown"),
                    "confidence": f"{result.get('confidence', 0):.2f}",
                    "schema_pattern": result.get("schema_pattern", "N/A"),
                },
            }
        )

    except Exception as e:
        progress.display_error(f"Error processing PDF: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
