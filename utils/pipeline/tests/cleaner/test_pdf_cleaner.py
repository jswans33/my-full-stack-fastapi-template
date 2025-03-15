"""
Tests for the PDF cleaner component.
"""

import pytest

from utils.pipeline.cleaner import PDFCleaner


@pytest.fixture
def sample_analysis_result():
    """Fixture to provide a sample analysis result."""
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
                "content": "This is sample content for section 1.\n",
                "level": 0,
            },
            {
                "title": "SECTION 2",
                "content": "This is sample content for section 2.\n",
                "level": 0,
            },
            {
                "title": "SECTION 3",
                "content": "This is sample content for section 3.\n",
                "level": 0,
            },
            {
                "title": "SECTION 4",
                "content": "This is sample content for section 4.\n",
                "level": 0,
            },
        ],
    }


def test_pdf_cleaner_initialization():
    """Test PDF cleaner initialization."""
    cleaner = PDFCleaner()
    assert cleaner is not None
    assert hasattr(cleaner, "clean")


def test_pdf_cleaner_with_sample_data(sample_analysis_result):
    """Test PDF cleaner with sample analysis result."""
    cleaner = PDFCleaner()
    result = cleaner.clean(sample_analysis_result)

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
    assert (
        result["pages"][0]["content"]
        == "SECTION 1 This is sample content for section 1. SECTION 2 This is sample content for section 2."
    )

    # Verify sections
    assert len(result["sections"]) == 4
    assert result["sections"][0]["title"] == "SECTION 1"
    assert "This is sample content for section 1" in result["sections"][0]["content"]


def test_pdf_cleaner_with_empty_sections(sample_analysis_result):
    """Test PDF cleaner with empty sections."""
    # Modify the sample data to include an empty section
    sample_analysis_result["sections"].append(
        {"title": "EMPTY SECTION", "content": "", "level": 0}
    )

    cleaner = PDFCleaner()
    result = cleaner.clean(sample_analysis_result)

    # Verify that empty sections are filtered out
    assert len(result["sections"]) == 4  # Still 4, not 5
    assert not any(
        section["title"] == "EMPTY SECTION" for section in result["sections"]
    )


def test_pdf_cleaner_error_handling():
    """Test PDF cleaner error handling."""
    cleaner = PDFCleaner()

    # Test with invalid input
    invalid_input = {"path": "sample.pdf"}  # Missing required fields
    result = cleaner.clean(invalid_input)

    # Should return the original data on error
    assert result == invalid_input


def test_clean_section():
    """Test the _clean_section method."""
    cleaner = PDFCleaner()

    # Test with various content formats
    section = {
        "title": "  TEST SECTION  ",
        "content": "  This is a test.\n\n  With multiple lines.  \n  And extra spaces.  ",
        "level": 0,
    }

    result = cleaner._clean_section(section)

    # Verify cleaning
    assert result["title"] == "TEST SECTION"
    assert "This is a test." in result["content"]
    assert "With multiple lines." in result["content"]
    assert "And extra spaces." in result["content"]
    assert result["level"] == 0


def test_clean_metadata():
    """Test the _clean_metadata method."""
    cleaner = PDFCleaner()

    # Test with various metadata formats
    metadata = {
        "title": "  Test Title  ",
        "author": "  Test Author  ",
        "subject": "Test\nSubject",
        "keywords": ["keyword1", "keyword2"],
        "non_printable": "Test\x00With\x01Non\x02Printable\x03Chars",
    }

    result = cleaner._clean_metadata(metadata)

    # Verify cleaning
    assert result["title"] == "Test Title"
    assert result["author"] == "Test Author"
    assert result["subject"] == "Test Subject"
    assert result["keywords"] == ["keyword1", "keyword2"]  # Lists should be preserved
    assert "Non" in result["non_printable"]
    assert "\x00" not in result["non_printable"]  # Non-printable chars removed
