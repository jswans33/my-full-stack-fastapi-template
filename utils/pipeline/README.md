# Document Pipeline Tool

A modular, pipeline-based Python tool for extracting structured data from various document formats (PDF, Excel, Word) into structured formats. This tool adheres to SOLID principles and employs the Strategy pattern to ensure extensibility, maintainability, and clear separation of concerns.

## Overview

The pipeline tool follows a structured approach:

- **Validation:** Validates document structure and extracts initial metadata
- **Preprocessing:** Normalizes formatting and prepares data
- **Data Extraction:** Parses and structures document data
- **Output Formatting:** Serializes structured data into the desired format
- **Verification & Reporting:** Validates extraction accuracy and generates reports

## Directory Structure

```
utils/pipeline/
├── __init__.py                # Package initialization
├── pipeline.py                # Core pipeline orchestration
├── pyproject.toml             # Project dependencies and configuration
├── config/                    # Configuration settings
├── data/                      # Sample data and output files
├── docs/                      # Documentation
│   └── pipeline-plan.md       # Architectural plan
├── models/                    # Data models and type definitions
├── processors/                # Core processing components
│   ├── validator.py           # Input validation
│   ├── extractor.py           # Data extraction
│   └── formatter.py           # Output formatting
├── strategies/                # Strategy pattern implementations
│   └── base.py                # Base strategy interfaces
└── utils/                     # Utility functions
    └── helpers.py             # Common helper functions
```

## Setup

### Prerequisites

- Python 3.8 or higher
- UV package manager (recommended)

### Creating a Virtual Environment

```bash
# Navigate to the pipeline directory
cd utils/pipeline

# Create a virtual environment with UV
uv venv

# Activate the virtual environment (Windows)
.venv\Scripts\activate

# Activate the virtual environment (Unix/Linux/Mac)
# source .venv/bin/activate
```

### Installing Dependencies

The project uses optional dependency groups to manage different document format processors:

```bash
# Install base dependencies only
uv pip install -e .

# Install specific document format processors
uv pip install -e ".[pdf]"     # PDF processing
uv pip install -e ".[excel]"   # Excel processing
uv pip install -e ".[word]"    # Word processing

# Install text analysis tools
uv pip install -e ".[analysis]"

# Install development tools
uv pip install -e ".[dev]"

# Install a minimal set of all document processors
uv pip install -e ".[all]"

# Install everything
uv pip install -e ".[pdf,excel,word,analysis,dev]"
```

If you encounter issues with the editable install syntax, you can install dependencies directly:

```bash
# Install base dependencies
uv pip install pyyaml typing-extensions

# Install document processors
uv pip install PyPDF2 pdfminer.six pymupdf pandas openpyxl python-docx
```

## Basic Usage

```python
from pipeline import Pipeline
from config import load_config

# Load configuration
config = load_config()

# Initialize pipeline
pipeline = Pipeline(config)

# Process a document
result = pipeline.run("path/to/document.pdf")

# Save the result
result.save("output.yaml")
```

## Extending the Pipeline

### Adding a New Document Format

1. Create a new strategy in the `strategies` directory
2. Implement the required interfaces (validation, extraction, formatting)
3. Register the strategy in the configuration

Example:

```python
# strategies/json_strategy.py
from strategies.base import ExtractionStrategy

class JSONExtractionStrategy(ExtractionStrategy):
    def extract(self, preprocessed_data):
        # Implementation for JSON extraction
        pass

# In your configuration
config = {
    "strategies": {
        "json": "strategies.json_strategy.JSONExtractionStrategy"
    }
}
```

## Development

### Testing

The project follows a Test-Driven Development (TDD) approach. Tests are organized in the `tests/` directory and mirror the structure of the main codebase.

#### Setting Up the Test Environment with UV

We recommend using UV for managing the Python environment and dependencies:

```bash
# Install UV if you don't have it already
# On Windows:
pip install uv
# On Unix/Linux/Mac:
# pip install uv

# Navigate to the pipeline directory
cd utils/pipeline

# Install pytest and dependencies
uv pip install pytest pytest-cov pytest-mock

# Install the pipeline package in development mode
uv pip install -e .
```

#### Running Tests with UV

After setting up the environment with UV, you can run the tests:

```bash
# Run all tests
uv run python -m pytest

# Run specific test files
uv run python -m pytest tests/test_config.py

# Run tests with specific markers
uv run python -m pytest -m "unit"
uv run python -m pytest -m "integration"

# Run tests with verbose output
uv run python -m pytest -v

# Run tests with coverage reporting
uv run python -m pytest --cov=.
```

#### Alternative: Using Traditional Virtual Environment

If you prefer using a traditional virtual environment approach:

```bash
# Set up the pytest environment
python setup_pytest_env.py

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix/Linux/Mac:
# source .venv/bin/activate

# Run all tests
pytest

# Run specific test files
pytest tests/test_config.py
```

For convenience, we also provide a `run_tests.py` script that handles activating the virtual environment:

```bash
# Run all tests with coverage reporting
python run_tests.py

# Run specific test files
python run_tests.py tests/test_config.py
```

#### Test Data

Sample test data files are located in the `data/tests/` directory, organized by document type:

- `data/tests/pdf/`: Sample PDF files
- `data/tests/excel/`: Sample Excel files
- `data/tests/word/`: Sample Word files
- `data/tests/text/`: Sample text files

#### Test Coverage

The test runner generates a coverage report showing which parts of the codebase are covered by tests:

```bash
# Run tests with coverage reporting
python run_tests.py

# View detailed HTML coverage report
# This will be generated in the coverage_html/ directory
```

#### Test Configuration

The pytest configuration is defined in `pytest.ini` and includes:

- Test discovery patterns
- Test markers for categorizing tests
- Command-line options

### Code Style

The project uses ruff for linting and formatting:

```bash
# Check code style
ruff check .

# Format code
ruff format .
```

### Type Checking

The project uses mypy for static type checking:

```bash
# Run type checking
mypy .
```

## Architecture

For detailed information about the architecture and design principles, see [pipeline-plan.md](docs/pipeline-plan.md).

### Architecture Diagrams

#### Pipeline Flow Diagram

A visual representation of the pipeline architecture is available as a PlantUML diagram at [pipeline_diagram.puml](docs/pipeline_diagram.puml).

This diagram shows the high-level flow: Input → Analyzer → Cleaner → Extractor → Validator → Output, along with the relationships between all modules in the system.

#### C4 Architecture Diagram

A more detailed C4 model architecture diagram is available at [pipeline_c4_diagram.puml](docs/pipeline_c4_diagram.puml).

The C4 diagram provides multiple levels of abstraction:
1. **Context Level**: Shows how the pipeline tool interacts with users and external systems
2. **Container Level**: Shows the high-level components of the pipeline tool
3. **Component Level**: Shows the internal components of the Pipeline Core and Strategy Engine

### Visualizing the Diagrams

You can visualize these diagrams in several ways:

1. **VSCode Extension**: Install the "PlantUML" extension in VSCode, then open the .puml file and use Alt+D to preview.

2. **Online PlantUML Server**: Copy the content of the .puml file and paste it into the [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/).

3. **Command Line**:
   ```bash
   # Install PlantUML (requires Java)
   # On Windows with Chocolatey
   choco install plantuml
   
   # On macOS with Homebrew
   brew install plantuml
   
   # Generate PNG image
   plantuml docs/pipeline_diagram.puml
   plantuml docs/pipeline_c4_diagram.puml
   ```

Note: The C4 diagram requires internet access during rendering to fetch the C4 PlantUML standard library.
