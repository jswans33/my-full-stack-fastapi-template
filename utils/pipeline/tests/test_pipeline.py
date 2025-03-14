"""
Tests for the pipeline module.

This file demonstrates TDD approach for the pipeline orchestrator.
"""

import os
from unittest.mock import MagicMock

import pytest

from pipeline import (
    MockStrategy,
    Pipeline,
    PipelineError,
    StrategySelector,
    StrategySet,
)


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
def test_pipeline_save_output_yaml(temp_dir):
    """Test that the pipeline can save output to a YAML file."""
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

    # Test both .yaml and .yml extensions
    for ext in [".yaml", ".yml"]:
        output_path = os.path.join(temp_dir, f"output{ext}")
        pipeline.save_output(output_data, output_path)

        # Verify that the file was created
        assert os.path.exists(output_path)

        # Verify the content of the file
        import yaml

        with open(output_path, "r") as f:
            loaded_data = yaml.safe_load(f)

        assert loaded_data == output_data


def test_pipeline_save_output_json(temp_dir):
    """Test that the pipeline can save output to a JSON file."""
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

    # Save the output to a JSON file
    output_path = os.path.join(temp_dir, "output.json")
    pipeline.save_output(output_data, output_path)

    # Verify that the file was created
    assert os.path.exists(output_path)

    # Verify the content of the file
    import json

    with open(output_path, "r") as f:
        loaded_data = json.load(f)

    assert loaded_data == output_data


def test_pipeline_save_output_default_yaml(temp_dir):
    """Test that the pipeline defaults to YAML for unknown extensions."""
    pipeline = Pipeline()

    # Create a sample output
    output_data = {
        "title": "Test Document",
        "content": "This is a test document.",
    }

    # Save with unknown extension
    output_path = os.path.join(temp_dir, "output.unknown")
    pipeline.save_output(output_data, output_path)

    # Verify that the file was created
    assert os.path.exists(output_path)

    # Verify the content is YAML
    import yaml

    with open(output_path, "r") as f:
        loaded_data = yaml.safe_load(f)

    assert loaded_data == output_data


def test_strategy_selector_import_paths():
    """Test strategy selector's import paths for different document types."""
    selector = StrategySelector({})

    # Test each document type
    for doc_type in ["pdf", "excel", "word", "generic"]:
        strategy_set = selector.get_strategies(doc_type)
        assert isinstance(strategy_set, StrategySet)
        assert hasattr(strategy_set, "analyzer")
        assert hasattr(strategy_set, "cleaner")
        assert hasattr(strategy_set, "extractor")
        assert hasattr(strategy_set, "validator")
        assert hasattr(strategy_set, "formatter")


def test_strategy_selector_import_error():
    """Test strategy selector's fallback to mock strategies on import error."""
    selector = StrategySelector({})

    # Test with a non-existent strategy type
    strategy_set = selector.get_strategies("nonexistent")

    # Verify that mock strategies are used
    assert isinstance(strategy_set.analyzer, MockStrategy)
    assert isinstance(strategy_set.cleaner, MockStrategy)
    assert isinstance(strategy_set.extractor, MockStrategy)
    assert isinstance(strategy_set.validator, MockStrategy)
    assert isinstance(strategy_set.formatter, MockStrategy)


def test_mock_strategy_methods(tmp_path):
    """Test all methods of the MockStrategy class."""
    strategy = MockStrategy()

    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Test analyze method
    result = strategy.analyze(str(test_file))
    assert result == {"mock_analysis": True, "path": str(test_file)}

    # Test analyze with non-existent file
    with pytest.raises(FileNotFoundError):
        strategy.analyze("nonexistent/file.txt")

    # Test clean method
    data = {"test": "data"}
    result = strategy.clean(data)
    assert result == {"mock_cleaned": True, "data": data}

    # Test extract method
    result = strategy.extract(data)
    assert result == {"mock_extracted": True, "data": data}

    # Test validate method
    result = strategy.validate(data)
    assert result == {"mock_validated": True, "data": data}

    # Test format method
    result = strategy.format(data)
    assert result == {"mock_formatted": True, "data": data}


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
