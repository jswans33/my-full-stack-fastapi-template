"""
Tests for the models module.

This file tests the base data models used in the pipeline.
"""

from models.models import PipelineData


def test_pipeline_data_init_with_data():
    """Test PipelineData initialization with data."""
    test_data = {"key": "value", "nested": {"inner": "data"}}
    data = PipelineData(test_data)
    assert data.data == test_data
    assert data.data is not test_data  # Should be a copy


def test_pipeline_data_init_without_data():
    """Test PipelineData initialization without data."""
    data = PipelineData()
    assert data.data == {}
    assert isinstance(data.data, dict)


def test_pipeline_data_init_with_none():
    """Test PipelineData initialization with None."""
    data = PipelineData(None)
    assert data.data == {}
    assert isinstance(data.data, dict)
