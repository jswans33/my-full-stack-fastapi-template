"""
Tests for pipeline logging functionality.

This file tests that the pipeline correctly uses the logging system.
"""

import logging

import pytest

from ..pipeline import Pipeline, PipelineError
from ..utils.logging import get_logger, set_log_level


def test_pipeline_initialization_logging(caplog):
    """Test that pipeline initialization is properly logged."""
    caplog.set_level(logging.INFO)
    test_config = {"test_key": "test_value"}
    pipeline = Pipeline(test_config)

    # Check initialization log
    assert any(
        record.levelname == "INFO"
        and "Pipeline initialized with config" in record.message
        and str(test_config) in record.message
        for record in caplog.records
    )


def test_pipeline_processing_logging(caplog, tmp_path):
    """Test that pipeline processing steps are properly logged."""
    caplog.set_level(logging.INFO)
    pipeline = Pipeline()

    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Run pipeline and capture logs
    pipeline.run(str(test_file))

    # Expected log messages in order
    expected_messages = [
        "Starting pipeline processing for",
        "Detected document type",
        "Step 1: Analyzing document structure",
        "Step 2: Cleaning and normalizing content",
        "Step 3: Extracting structured data",
        "Step 4: Validating extracted data",
        "Step 5: Formatting output",
        "Pipeline processing completed successfully",
    ]

    # Check that all expected messages are present in order
    log_messages = [record.message for record in caplog.records]
    current_idx = 0
    for expected in expected_messages:
        matching_messages = [
            msg for msg in log_messages[current_idx:] if expected in msg
        ]
        assert matching_messages, f"Missing log message: {expected}"
        current_idx = log_messages.index(matching_messages[0]) + 1


def test_pipeline_error_logging(caplog, tmp_path):
    """Test that pipeline errors are properly logged."""
    caplog.set_level(logging.ERROR)
    pipeline = Pipeline()

    # Try to process a non-existent file
    non_existent_file = tmp_path / "does_not_exist.txt"

    with pytest.raises(PipelineError):
        pipeline.run(str(non_existent_file))

    # Check error log
    assert any(
        record.levelname == "ERROR" and "Pipeline processing failed" in record.message
        for record in caplog.records
    )


def test_strategy_selector_logging(caplog, tmp_path):
    """Test that strategy selection is properly logged."""
    caplog.set_level(logging.INFO)
    pipeline = Pipeline()

    # Create a test PDF file
    test_file = tmp_path / "test.pdf"
    test_file.write_text("test content")

    # Process a test document to trigger strategy selection
    result = pipeline.run(str(test_file))

    # Check strategy selection log
    assert any(
        record.levelname == "INFO"
        and "Selecting strategies for document type: pdf" in record.message
        for record in caplog.records
    )


def test_output_saving_logging(caplog, tmp_path):
    """Test that output saving is properly logged."""
    caplog.set_level(logging.INFO)
    pipeline = Pipeline()

    # Create some test output data
    output_data = {"test": "data"}
    output_file = tmp_path / "output.yaml"

    # Save output and check logs
    pipeline.save_output(output_data, str(output_file))

    assert any(
        record.levelname == "INFO"
        and "Saving output to:" in record.message
        and str(output_file) in record.message
        for record in caplog.records
    )


def test_log_level_propagation():
    """Test that log level changes are properly propagated to pipeline components."""
    # Create loggers for different components
    pipeline_logger = get_logger("pipeline")
    strategy_logger = get_logger("pipeline.strategy")
    processor_logger = get_logger("pipeline.processor")

    # Set different log levels
    levels_to_test = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]

    for level in levels_to_test:
        # Use set_log_level to properly propagate levels
        set_log_level(level)
        assert pipeline_logger.level == level
        assert strategy_logger.level == level
        assert processor_logger.level == level
