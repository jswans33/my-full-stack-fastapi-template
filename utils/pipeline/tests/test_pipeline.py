"""
Tests for the pipeline module.

This file demonstrates TDD approach for the pipeline orchestrator.
"""

import os
from unittest.mock import MagicMock

import pytest

from pipeline import Pipeline, PipelineError


# Basic initialization tests
def test_pipeline_initialization(sample_config):
    """Test that the pipeline initializes correctly with a configuration."""
    pipeline = Pipeline(sample_config)
    assert pipeline.config == sample_config


def test_pipeline_default_config():
    """Test that the pipeline initializes with a default configuration if none is provided."""
    pipeline = Pipeline()
    assert isinstance(pipeline.config, dict)


# Document type detection tests
@pytest.mark.parametrize(
    "file_path,expected_type",
    [
        ("document.pdf", "pdf"),
        ("document.PDF", "pdf"),
        ("path/to/document.xlsx", "excel"),
        ("path/to/document.xls", "excel"),
        ("document.docx", "word"),
        ("document.doc", "word"),
        ("document.txt", "text"),
        ("document.unknown", "generic"),
    ],
)
def test_detect_document_type(file_path, expected_type):
    """Test that the pipeline correctly detects document types based on file extension."""
    pipeline = Pipeline()
    detected_type = pipeline._detect_document_type(file_path)
    assert detected_type == expected_type


# Pipeline flow tests
def test_pipeline_run_with_mocks(mock_strategy_set):
    """Test the pipeline run method with mocked strategy components."""
    pipeline = Pipeline()

    # Mock the strategy selector to return our mock strategy set
    pipeline.strategy_selector = MagicMock()
    pipeline.strategy_selector.get_strategies.return_value = mock_strategy_set

    # Run the pipeline with a dummy file path
    result = pipeline.run("dummy/path/to/document.pdf")

    # Verify that each strategy was called in the correct order
    mock_strategy_set.analyzer.analyze.assert_called_once()
    mock_strategy_set.cleaner.clean.assert_called_once()
    mock_strategy_set.extractor.extract.assert_called_once()
    mock_strategy_set.validator.validate.assert_called_once()
    mock_strategy_set.formatter.format.assert_called_once()

    # Verify that the result is the output from the formatter
    assert result == mock_strategy_set.formatter.format.return_value


def test_pipeline_error_handling():
    """Test that the pipeline handles errors correctly."""
    pipeline = Pipeline()

    # Mock the strategy selector to raise an exception
    pipeline.strategy_selector = MagicMock()
    pipeline.strategy_selector.get_strategies.side_effect = Exception("Test error")

    # Verify that the pipeline raises a PipelineError
    with pytest.raises(PipelineError, match="Test error"):
        pipeline.run("dummy/path/to/document.pdf")


# Integration test with file system
def test_pipeline_save_output(temp_dir):
    """Test that the pipeline can save output to a file."""
    pipeline = Pipeline()

    # Create a sample output
    output_data = {
        "title": "Test Document",
        "content": "This is a test document.",
        "metadata": {
            "author": "Test Author",
            "date": "2025-03-14",
        },
    }

    # Save the output to a YAML file
    output_path = os.path.join(temp_dir, "output.yaml")
    pipeline.save_output(output_data, output_path)

    # Verify that the file was created
    assert os.path.exists(output_path)

    # Verify the content of the file
    import yaml

    with open(output_path, "r") as f:
        loaded_data = yaml.safe_load(f)

    assert loaded_data == output_data


# Property-based testing for document type detection
@pytest.mark.parametrize(
    "extension",
    [
        "pdf",
        "xlsx",
        "docx",
        "txt",
        "csv",
        "json",
        "xml",
        "html",
        "md",
        "py",
        "js",
        "unknown",
    ],
)
def test_document_type_detection_property(extension, create_temp_file):
    """
    Property-based test for document type detection.

    For any file extension, the detected type should be consistent
    regardless of the file name or path.
    """
    pipeline = Pipeline()

    # Create multiple file paths with the same extension
    file_paths = [
        f"document.{extension}",
        f"path/to/document.{extension}",
        f"path/with spaces/to/document with spaces.{extension}",
        f"path/with-special-chars/to/document-with-special-chars.{extension}",
    ]

    # Get the expected type for the first file path
    expected_type = pipeline._detect_document_type(file_paths[0])

    # Verify that all file paths with the same extension have the same detected type
    for file_path in file_paths[1:]:
        detected_type = pipeline._detect_document_type(file_path)
        assert detected_type == expected_type, (
            f"Inconsistent type detection for {file_path}"
        )
