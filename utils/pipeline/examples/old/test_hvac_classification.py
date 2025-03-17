"""
Test script for HVAC document classification.

This script demonstrates how to use the keyword analyzer classifier
to classify HVAC documents, using the same approach as the debug script.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow relative imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import yaml

from utils.pipeline.pipeline import Pipeline
from utils.pipeline.processors.classifiers.keyword_analyzer import (
    KeywordAnalyzerClassifier,
)
from utils.pipeline.utils.progress import PipelineProgress


def load_config():
    """Load configuration from YAML files."""
    current_dir = Path(__file__).parent.parent

    # Load base configuration for pipeline processing only
    config_path = current_dir / "config" / "example_config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Load HVAC-specific configuration
    hvac_config_path = current_dir / "config" / "hvac_classifier_config.yaml"
    with open(hvac_config_path, "r") as f:
        hvac_config = yaml.safe_load(f)

    # Update paths for this specific test
    config["input_dir"] = str(current_dir / "data" / "tests" / "pdf")
    config["output_dir"] = str(current_dir / "data" / "output")

    # Disable classification in the pipeline - we'll do it manually
    config["enable_classification"] = False

    return config, hvac_config


def debug_classifier(document_data, config, progress):
    """Debug the keyword analyzer classifier."""
    # Create an instance of the KeywordAnalyzerClassifier
    classifier = KeywordAnalyzerClassifier(config=config)

    progress.display_success("\n=== Document Text Analysis ===")
    content_text = classifier._extract_all_text(document_data)
    progress.display_success(f"Total text length: {len(content_text)} characters")

    # Analyze keyword frequencies
    progress.display_success("\n=== Keyword Frequency Analysis ===")
    keyword_frequencies = classifier._analyze_keyword_frequencies(content_text)
    if keyword_frequencies:
        progress.display_success("Found keywords in these groups:")
        for group_name, keywords in keyword_frequencies.items():
            progress.display_success(f"  {group_name}: {len(keywords)} matches")
    else:
        progress.display_success("No keyword matches found!")

    # Match phrase patterns
    progress.display_success("\n=== Phrase Pattern Analysis ===")
    phrase_matches = classifier._match_phrase_patterns(content_text)
    if phrase_matches:
        progress.display_success("Found phrase pattern matches:")
        for pattern_type, matches in phrase_matches.items():
            progress.display_success(f"  {pattern_type}: {len(matches)} matches")
    else:
        progress.display_success("No phrase pattern matches found!")

    # Analyze keyword context
    progress.display_success("\n=== Contextual Analysis ===")
    contextual_matches = classifier._analyze_keyword_context(document_data)
    if contextual_matches:
        progress.display_success("Found contextual matches:")
        for context_type, matches in contextual_matches.items():
            progress.display_success(f"  {context_type}: {len(matches)} matches")
    else:
        progress.display_success("No contextual matches found!")

    # Calculate scores for each document type
    progress.display_success("\n=== Document Type Scores ===")
    type_scores = classifier._calculate_type_scores(
        keyword_frequencies, phrase_matches, contextual_matches
    )
    if type_scores:
        progress.display_success("Document type scores:")
        for doc_type, (score, features) in type_scores.items():
            progress.display_success(f"  {doc_type}: {score:.4f}")
    else:
        progress.display_success("No document type scores calculated!")

    # Get best matching document type
    progress.display_success("\n=== Best Match ===")
    best_match = classifier._get_best_match(type_scores)
    progress.display_success(f"Best match: {best_match[0]}")
    progress.display_success(f"Confidence: {best_match[1]:.4f}")

    # Check if confidence exceeds threshold
    progress.display_success(f"\nThreshold: {classifier.threshold:.4f}")
    if best_match[1] >= classifier.threshold:
        progress.display_success(f"RESULT: Document classified as {best_match[0]}")
    else:
        progress.display_success(
            "RESULT: Document classified as UNKNOWN (confidence below threshold)"
        )

    # Return the classification result
    return classifier.classify(document_data, {})


def main():
    """Run HVAC document classification test."""
    progress = PipelineProgress()

    try:
        # Get the current directory
        current_dir = Path(__file__).parent.parent

        # Set up paths
        input_file = current_dir / "data" / "tests" / "pdf" / "sample.pdf"
        output_dir = current_dir / "data" / "output"
        json_path = output_dir / f"{input_file.stem}_hvac.json"

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Display setup info
        progress.display_success(f"Processing {input_file.name}")
        progress.display_success(f"Input file path: {input_file}")
        progress.display_success(f"Output directory: {output_dir}")

        # Load configurations
        config, hvac_config = load_config()
        progress.display_success("Configuration loaded")

        # Initialize pipeline for document processing only (no classification)
        pipeline = Pipeline(config)
        progress.display_success("Pipeline initialized for document processing")

        # Process the PDF to extract content
        progress.display_success("Processing document...")
        document_data = pipeline.run(str(input_file))

        # Save the processed data
        pipeline.save_output(document_data, str(json_path))
        progress.display_success(f"Processed document saved to: {json_path}")

        # Now directly use the KeywordAnalyzerClassifier like in the debug script
        progress.display_success("\nPerforming HVAC classification...")

        # Get the keyword analyzer configuration
        keyword_analyzer_config = hvac_config.get("classifiers", {}).get(
            "keyword_analyzer", {}
        )

        # Debug and classify the document
        classification_result = debug_classifier(
            document_data, keyword_analyzer_config, progress
        )

        # Update the document data with classification results
        document_data.update(classification_result)

        # Save the updated data with classification results
        json_path = output_dir / f"{input_file.stem}_hvac.json"
        with open(json_path, "w") as f:
            import json

            json.dump(document_data, f, indent=2)
        progress.display_success(f"Classification results saved to: {json_path}")

        # Display classification results
        progress.display_success("\nClassification Results:")
        progress.display_success(
            f"Document Type: {classification_result['document_type']}"
        )
        progress.display_success(
            f"Confidence: {classification_result.get('confidence', 0):.2f}"
        )
        progress.display_success(
            f"Schema Pattern: {classification_result.get('schema_pattern', 'N/A')}"
        )

        if "key_features" in classification_result:
            progress.display_success("\nKey Features:")
            for feature in classification_result["key_features"]:
                progress.display_success(f"- {feature}")

        # Display summary
        progress.display_summary(
            {
                "Input File": {"path": str(input_file), "status": "Processed"},
                "JSON Output": {"path": str(json_path), "status": "Complete"},
                "Classification": {
                    "document_type": classification_result.get(
                        "document_type", "Unknown"
                    ),
                    "confidence": f"{classification_result.get('confidence', 0):.2f}",
                    "schema_pattern": classification_result.get(
                        "schema_pattern", "N/A"
                    ),
                },
            }
        )

    except Exception as e:
        progress.display_error(f"Error processing PDF: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
