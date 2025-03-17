"""
Debug script for HVAC document classifier.

This script helps troubleshoot the keyword analyzer classifier by providing
detailed debugging information about the classification process.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to allow relative imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import yaml

from utils.pipeline.processors.classifiers.keyword_analyzer import (
    KeywordAnalyzerClassifier,
)
from utils.pipeline.utils.progress import PipelineProgress


def load_config():
    """Load configuration from YAML files."""
    current_dir = Path(__file__).parent.parent

    # Load HVAC-specific configuration
    hvac_config_path = current_dir / "config" / "hvac_classifier_config.yaml"
    with open(hvac_config_path, "r") as f:
        hvac_config = yaml.safe_load(f)

    return hvac_config


def load_document_data(json_path):
    """Load document data from a JSON file."""
    encodings = ["utf-8", "utf-8-sig", "latin-1"]

    for encoding in encodings:
        try:
            with open(json_path, "r", encoding=encoding) as f:
                return json.load(f)
        except UnicodeDecodeError:
            # Try the next encoding
            continue

    # If all encodings fail, try a fallback approach
    with open(json_path, "rb") as f:
        content = f.read()
        # Replace problematic characters
        content = content.decode("ascii", errors="replace")
        return json.loads(content)


def debug_classifier(document_data, config, output_file):
    """Debug the keyword analyzer classifier."""
    # Create an instance of the KeywordAnalyzerClassifier
    classifier = KeywordAnalyzerClassifier(config=config)

    # Open the output file
    with open(output_file, "w") as f:
        # Extract all text content from the document
        f.write("\n=== Document Text Analysis ===\n")
        content_text = classifier._extract_all_text(document_data)
        f.write(f"Total text length: {len(content_text)} characters\n")
        f.write(f"First 200 characters: {content_text[:200]}...\n")

        # Analyze keyword frequencies
        f.write("\n=== Keyword Frequency Analysis ===\n")
        keyword_frequencies = classifier._analyze_keyword_frequencies(content_text)
        if keyword_frequencies:
            f.write("Found keywords in these groups:\n")
            for group_name, keywords in keyword_frequencies.items():
                f.write(f"  {group_name}: {len(keywords)} matches\n")
                for keyword, count in keywords.items():
                    f.write(f"    - '{keyword}': {count} occurrences\n")
        else:
            f.write("No keyword matches found!\n")

        # Match phrase patterns
        f.write("\n=== Phrase Pattern Analysis ===\n")
        phrase_matches = classifier._match_phrase_patterns(content_text)
        if phrase_matches:
            f.write("Found phrase pattern matches:\n")
            for pattern_type, matches in phrase_matches.items():
                f.write(f"  {pattern_type}: {len(matches)} matches\n")
                for match in matches[:5]:  # Show first 5 matches
                    f.write(f"    - '{match}'\n")
                if len(matches) > 5:
                    f.write(f"    - ... and {len(matches) - 5} more\n")
        else:
            f.write("No phrase pattern matches found!\n")

        # Analyze keyword context
        f.write("\n=== Contextual Analysis ===\n")
        contextual_matches = classifier._analyze_keyword_context(document_data)
        if contextual_matches:
            f.write("Found contextual matches:\n")
            for context_type, matches in contextual_matches.items():
                f.write(f"  {context_type}: {len(matches)} matches\n")
                for match in matches[:5]:  # Show first 5 matches
                    f.write(f"    - {match}\n")
                if len(matches) > 5:
                    f.write(f"    - ... and {len(matches) - 5} more\n")
        else:
            f.write("No contextual matches found!\n")

        # Calculate scores for each document type
        f.write("\n=== Document Type Scores ===\n")
        type_scores = classifier._calculate_type_scores(
            keyword_frequencies, phrase_matches, contextual_matches
        )
        if type_scores:
            f.write("Document type scores:\n")
            for doc_type, (score, features) in type_scores.items():
                f.write(f"  {doc_type}: {score:.4f}\n")
                f.write(f"    Features: {', '.join(features)}\n")
        else:
            f.write("No document type scores calculated!\n")

        # Get best matching document type
        f.write("\n=== Best Match ===\n")
        best_match = classifier._get_best_match(type_scores)
        f.write(f"Best match: {best_match[0]}\n")
        f.write(f"Confidence: {best_match[1]:.4f}\n")
        f.write(f"Features: {best_match[2]}\n")

        # Check if confidence exceeds threshold
        f.write(f"\nThreshold: {classifier.threshold:.4f}\n")
        if best_match[1] >= classifier.threshold:
            f.write(f"RESULT: Document classified as {best_match[0]}\n")
        else:
            f.write(
                "RESULT: Document classified as UNKNOWN (confidence below threshold)\n"
            )

    # Return the classification result
    return classifier.classify(document_data, {})


def main():
    """Run the debug script."""
    progress = PipelineProgress()

    try:
        # Get the current directory
        current_dir = Path(__file__).parent.parent

        # Set up paths
        input_file = current_dir / "data" / "tests" / "pdf" / "sample.pdf"
        output_dir = current_dir / "data" / "output"
        json_path = output_dir / f"{input_file.stem}_hvac.json"

        # Display setup info
        progress.display_success(f"Debugging classifier for: {input_file.name}")
        progress.display_success(f"Using JSON data from: {json_path}")

        # Load configuration
        config = load_config()
        progress.display_success("Configuration loaded")

        # Load document data
        document_data = load_document_data(json_path)
        progress.display_success("Document data loaded")

        # Set up debug output file
        debug_output_file = output_dir / f"{input_file.stem}_debug.txt"
        progress.display_success(
            f"Debug output will be written to: {debug_output_file}"
        )

        # Extract the keyword analyzer configuration
        keyword_analyzer_config = config.get("classifiers", {}).get(
            "keyword_analyzer", {}
        )
        progress.display_success("Using keyword analyzer configuration")

        # Debug the classifier
        result = debug_classifier(
            document_data, keyword_analyzer_config, debug_output_file
        )

        # Display classification results
        progress.display_success("\nFinal Classification Results:")
        progress.display_success(f"Document Type: {result['document_type']}")
        progress.display_success(f"Confidence: {result.get('confidence', 0):.4f}")
        progress.display_success(
            f"Schema Pattern: {result.get('schema_pattern', 'N/A')}"
        )

        if "key_features" in result and result["key_features"]:
            progress.display_success("\nKey Features:")
            for feature in result["key_features"]:
                progress.display_success(f"- {feature}")

    except Exception as e:
        progress.display_error(f"Error debugging classifier: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
