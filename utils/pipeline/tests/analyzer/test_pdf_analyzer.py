"""
Tests for the PDF analyzer component.
"""

import os
from pathlib import Path

import pytest

from utils.pipeline.analyzer import PDFAnalyzer


@pytest.fixture
def sample_pdf_path():
    """Fixture to provide a sample PDF path."""
    # Get the path to the test data directory
    test_dir = Path(__file__).parent.parent
    data_dir = test_dir / "data"

    # Create the data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)

    # Return a path to a sample PDF file
    # In a real test, this would be a path to an actual PDF file
    return str(data_dir / "sample.pdf")


def test_pdf_analyzer_initialization():
    """Test PDF analyzer initialization."""
    analyzer = PDFAnalyzer()
    assert analyzer is not None
    assert hasattr(analyzer, "analyze")


def test_pdf_analyzer_with_sample_pdf(sample_pdf_path, monkeypatch):
    """Test PDF analyzer with a sample PDF file."""

    # Mock the open function to avoid actually opening a file
    class MockPdfReader:
        def __init__(self, *args, **kwargs):
            self.metadata = {
                "/Title": "Sample PDF",
                "/Author": "Test Author",
                "/Subject": "Test Subject",
                "/Creator": "Test Creator",
                "/Producer": "Test Producer",
                "/CreationDate": "D:20250315000000",
                "/ModDate": "D:20250315000000",
            }
            self.pages = [MockPage(), MockPage()]

    class MockPage:
        def __init__(self):
            self.mediabox = [0, 0, 612, 792]

        def get(self, key, default=None):
            if key == "/Rotate":
                return 0
            return default

        def extract_text(self):
            return "SECTION 1\nThis is sample content for section 1.\n\nSECTION 2\nThis is sample content for section 2."

    # Apply the monkeypatch
    monkeypatch.setattr("pypdf.PdfReader", MockPdfReader)

    # Create a mock file to avoid FileNotFoundError
    if not os.path.exists(sample_pdf_path):
        os.makedirs(os.path.dirname(sample_pdf_path), exist_ok=True)
        with open(sample_pdf_path, "w") as f:
            f.write("Mock PDF content")

    # Test the analyzer
    analyzer = PDFAnalyzer()
    result = analyzer.analyze(sample_pdf_path)

    # Verify the result structure
    assert result is not None
    assert "path" in result
    assert "type" in result
    assert "metadata" in result
    assert "pages" in result
    assert "sections" in result

    # Verify metadata
    assert result["metadata"]["title"] == "Sample PDF"
    assert result["metadata"]["author"] == "Test Author"

    # Verify pages
    assert len(result["pages"]) == 2

    # Verify sections
    assert len(result["sections"]) > 0
    assert "title" in result["sections"][0]
    assert "content" in result["sections"][0]
    assert "level" in result["sections"][0]


def test_pdf_analyzer_error_handling(sample_pdf_path, monkeypatch):
    """Test PDF analyzer error handling."""

    # Mock the open function to raise an exception
    def mock_open(*args, **kwargs):
        raise Exception("Test exception")

    # Apply the monkeypatch
    monkeypatch.setattr("builtins.open", mock_open)

    # Test the analyzer
    analyzer = PDFAnalyzer()
    result = analyzer.analyze(sample_pdf_path)

    # Verify the result structure for error case
    assert result is not None
    assert "path" in result
    assert "type" in result
    assert "metadata" in result
    assert "sections" in result

    # Verify error section
    assert len(result["sections"]) == 1
    assert result["sections"][0]["title"] == "Error"
    assert "Failed to analyze PDF" in result["sections"][0]["content"]
