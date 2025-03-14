"""
Pytest configuration file for the pipeline package.

This file contains fixtures that can be used across multiple test files.
"""

import os
import shutil
import tempfile
from typing import Any, Callable, Dict, Generator, List
from unittest.mock import MagicMock

import pytest

# Define test data directory
TEST_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "tests"
)


# ---- Configuration Fixtures ----


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Return a sample configuration for testing."""
    return {
        "input_dir": "data/input",
        "output_dir": "data/output",
        "log_level": "INFO",
        "strategies": {
            "pdf": "strategies.pdf",
            "excel": "strategies.excel",
            "word": "strategies.word",
        },
    }


# ---- File System Fixtures ----


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def create_temp_file() -> Callable[[str, str], str]:
    """Return a function that creates a temporary file with given content."""

    def _create_temp_file(content: str, extension: str) -> str:
        fd, path = tempfile.mkstemp(suffix=extension)
        try:
            with os.fdopen(fd, "w") as f:
                f.write(content)
        except:
            os.close(fd)
            raise
        return path

    return _create_temp_file


# ---- Sample Document Fixtures ----


@pytest.fixture
def sample_pdf_path() -> str:
    """Return the path to a sample PDF file for testing."""
    return os.path.join(TEST_DATA_DIR, "pdf", "sample.pdf")


@pytest.fixture
def sample_excel_path() -> str:
    """Return the path to a sample Excel file for testing."""
    return os.path.join(TEST_DATA_DIR, "excel", "sample.xlsx")


@pytest.fixture
def sample_word_path() -> str:
    """Return the path to a sample Word file for testing."""
    return os.path.join(TEST_DATA_DIR, "word", "sample.docx")


@pytest.fixture
def sample_text_path() -> str:
    """Return the path to a sample text file for testing."""
    return os.path.join(TEST_DATA_DIR, "text", "sample.txt")


# ---- Mock Strategy Fixtures ----


@pytest.fixture
def mock_analyzer() -> MagicMock:
    """Return a mock analyzer strategy."""
    mock = MagicMock()
    mock.analyze.return_value = {
        "mock_analysis": True,
        "metadata": {"title": "Test Document"},
    }
    return mock


@pytest.fixture
def mock_cleaner() -> MagicMock:
    """Return a mock cleaner strategy."""
    mock = MagicMock()
    mock.clean.return_value = {"mock_cleaned": True, "content": "Cleaned content"}
    return mock


@pytest.fixture
def mock_extractor() -> MagicMock:
    """Return a mock extractor strategy."""
    mock = MagicMock()
    mock.extract.return_value = {"mock_extracted": True, "data": {"key": "value"}}
    return mock


@pytest.fixture
def mock_validator() -> MagicMock:
    """Return a mock validator strategy."""
    mock = MagicMock()
    mock.validate.return_value = {"mock_validated": True, "is_valid": True}
    return mock


@pytest.fixture
def mock_formatter() -> MagicMock:
    """Return a mock formatter strategy."""
    mock = MagicMock()
    mock.format.return_value = {"mock_formatted": True, "output": {"formatted": "data"}}
    return mock


@pytest.fixture
def mock_strategy_set(
    mock_analyzer, mock_cleaner, mock_extractor, mock_validator, mock_formatter
) -> MagicMock:
    """Return a mock strategy set with all components."""
    mock = MagicMock()
    mock.analyzer = mock_analyzer
    mock.cleaner = mock_cleaner
    mock.extractor = mock_extractor
    mock.validator = mock_validator
    mock.formatter = mock_formatter
    return mock


# ---- Parameterization Helpers ----


@pytest.fixture
def document_types() -> List[str]:
    """Return a list of document types for parameterized tests."""
    return ["pdf", "excel", "word", "text"]


@pytest.fixture
def document_paths(
    sample_pdf_path, sample_excel_path, sample_word_path, sample_text_path
) -> Dict[str, str]:
    """Return a dictionary mapping document types to sample paths."""
    return {
        "pdf": sample_pdf_path,
        "excel": sample_excel_path,
        "word": sample_word_path,
        "text": sample_text_path,
    }
