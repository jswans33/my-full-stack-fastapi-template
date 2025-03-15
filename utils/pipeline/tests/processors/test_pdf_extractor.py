"""
Tests for the PDF extractor component.
"""

from unittest.mock import MagicMock, patch

import pytest

from utils.pipeline.processors.pdf_extractor import PDFExtractor


@pytest.fixture
def sample_cleaned_data():
    """Fixture to provide sample cleaned data."""
    return {
        "path": "sample.pdf",
        "type": "pdf",
        "metadata": {
            "title": "Sample PDF",
            "author": "Test Author",
            "subject": "Test Subject",
            "creator": "Test Creator",
            "producer": "Test Producer",
            "creation_date": "D:20250315000000",
            "modification_date": "D:20250315000000",
        },
        "pages": [
            {
                "number": 1,
                "size": [0, 0, 612, 792],
                "rotation": 0,
                "content": "SECTION 1\nThis is sample content for section 1.\n\nSECTION 2\nThis is sample content for section 2.",
            },
            {
                "number": 2,
                "size": [0, 0, 612, 792],
                "rotation": 0,
                "content": "SECTION 3\nThis is sample content for section 3.\n\nSECTION 4\nThis is sample content for section 4.",
            },
        ],
        "sections": [
            {
                "title": "SECTION 1",
                "content": "This is sample content for section 1.",
                "level": 0,
            },
            {
                "title": "SECTION 2",
                "content": "This is sample content for section 2.",
                "level": 0,
            },
            {
                "title": "SECTION 3",
                "content": "This is sample content for section 3.",
                "level": 0,
            },
            {
                "title": "SECTION 4",
                "content": "This is sample content for section 4.",
                "level": 0,
            },
        ],
    }


def test_pdf_extractor_initialization():
    """Test PDF extractor initialization."""
    extractor = PDFExtractor()
    assert extractor is not None
    assert hasattr(extractor, "extract")


@patch("fitz.open")
def test_pdf_extractor_with_sample_data(mock_fitz_open, sample_cleaned_data):
    """Test PDF extractor with sample cleaned data."""
    # Create mock document and page
    mock_doc = MagicMock()
    mock_page = MagicMock()

    # Configure mock page to return text
    mock_page.get_text.return_value = "A1 GENERAL INFORMATION\nThis is general information.\n\nA2 SPECIFICATIONS\nThese are specifications."

    # Configure mock document to return pages
    mock_doc.__iter__.return_value = [mock_page, mock_page]

    # Configure mock page to return blocks for table detection
    mock_blocks = {
        "blocks": [
            {
                "lines": [
                    {"spans": [{"text": "Header 1"}, {"text": "Header 2"}]},
                    {"spans": [{"text": "Data 1"}, {"text": "Data 2"}]},
                    {"spans": [{"text": "Data 3"}, {"text": "Data 4"}]},
                ]
            }
        ]
    }
    mock_page.get_text.side_effect = (
        lambda format_type: mock_blocks if format_type == "dict" else "Sample text"
    )

    # Configure mock fitz.open to return mock document
    mock_fitz_open.return_value = mock_doc

    # Test the extractor
    extractor = PDFExtractor()
    result = extractor.extract(sample_cleaned_data)

    # Verify the result structure
    assert result is not None
    assert "metadata" in result
    assert "sections" in result
    assert "tables" in result
    assert "schema" in result
    assert "path" in result

    # Verify metadata
    assert result["metadata"] == sample_cleaned_data["metadata"]

    # Verify sections
    assert len(result["sections"]) > 0

    # Verify tables
    assert len(result["tables"]) > 0
    assert "headers" in result["tables"][0]
    assert "data" in result["tables"][0]
    assert "column_count" in result["tables"][0]
    assert "row_count" in result["tables"][0]

    # Verify schema
    assert "type" in result["schema"]
    assert "properties" in result["schema"]
    assert "required" in result["schema"]


@patch("fitz.open")
def test_pdf_extractor_section_extraction(mock_fitz_open, sample_cleaned_data):
    """Test section extraction functionality."""
    # Create mock document and page
    mock_doc = MagicMock()
    mock_page = MagicMock()

    # Configure mock page to return text with section headers
    mock_page.get_text.return_value = "A1 GENERAL INFORMATION\nThis is general information.\n\nA2 SPECIFICATIONS\nThese are specifications."

    # Configure mock document to return pages
    mock_doc.__iter__.return_value = [mock_page]

    # Configure mock fitz.open to return mock document
    mock_fitz_open.return_value = mock_doc

    # Test the extractor
    extractor = PDFExtractor()
    sections = extractor._extract_sections(mock_doc)

    # Verify sections
    assert len(sections) >= 2
    assert any(section["title"] == "A1 GENERAL INFORMATION" for section in sections)
    assert any(section["title"] == "A2 SPECIFICATIONS" for section in sections)
    assert any(
        "This is general information" in section["content"] for section in sections
    )
    assert any("These are specifications" in section["content"] for section in sections)


@patch("fitz.open")
def test_pdf_extractor_table_extraction(mock_fitz_open, sample_cleaned_data):
    """Test table extraction functionality."""
    # Create mock document and page
    mock_doc = MagicMock()
    mock_page = MagicMock()

    # Configure mock page to return text with table indicators
    mock_page.get_text.return_value = (
        "TABLE 1: Sample Table\nHeader 1\tHeader 2\nData 1\tData 2\nData 3\tData 4\n\n"
    )

    # Configure mock document to return pages
    mock_doc.__iter__.return_value = [mock_page]

    # Configure mock page to return blocks for table detection
    mock_blocks = {
        "blocks": [
            {
                "lines": [
                    {"spans": [{"text": "Header 1"}, {"text": "Header 2"}]},
                    {"spans": [{"text": "Data 1"}, {"text": "Data 2"}]},
                    {"spans": [{"text": "Data 3"}, {"text": "Data 4"}]},
                ]
            }
        ]
    }
    mock_page.get_text.side_effect = (
        lambda format_type: mock_blocks
        if format_type == "dict"
        else "TABLE 1: Sample Table\nHeader 1\tHeader 2\nData 1\tData 2\nData 3\tData 4\n\n"
    )

    # Test the extractor
    extractor = PDFExtractor()
    tables = extractor._extract_tables(mock_doc)

    # Verify tables
    assert len(tables) > 0
    assert tables[0]["page"] == 1
    assert tables[0]["table_number"] == 1
    assert len(tables[0]["headers"]) > 0
    assert len(tables[0]["data"]) > 0
    assert tables[0]["column_count"] > 0
    assert tables[0]["row_count"] > 0


@patch("fitz.open")
def test_pdf_extractor_schema_extraction(mock_fitz_open, sample_cleaned_data):
    """Test schema extraction functionality."""
    # Create sample sections with CSI-style section numbers
    sections = [
        {"title": "A1 GENERAL INFORMATION", "content": "This is general information."},
        {"title": "A2 SPECIFICATIONS", "content": "These are specifications."},
        {"title": "B1.1 MATERIALS", "content": "Material specifications."},
        {"title": "B1.2 EXECUTION", "content": "Execution requirements."},
    ]

    # Test the extractor
    extractor = PDFExtractor()
    schema = extractor._extract_schema(sections)

    # Verify schema structure
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "required" in schema

    # Verify schema properties
    assert "A1" in schema["properties"]
    assert "A2" in schema["properties"]
    assert "B1.1" in schema["properties"]
    assert "B1.2" in schema["properties"]

    # Verify property structure
    assert "title" in schema["properties"]["A1"]
    assert "properties" in schema["properties"]["A1"]
    assert "content" in schema["properties"]["A1"]["properties"]


@patch("fitz.open")
def test_pdf_extractor_error_handling(mock_fitz_open, sample_cleaned_data):
    """Test error handling in PDF extractor."""
    # Configure mock fitz.open to raise an exception
    mock_fitz_open.side_effect = Exception("Test exception")

    # Test the extractor
    extractor = PDFExtractor()

    # Verify that exception is propagated
    with pytest.raises(Exception) as excinfo:
        extractor.extract(sample_cleaned_data)

    # Verify exception message
    assert "Test exception" in str(excinfo.value)
