# UML Generator

A Python-based tool for automatically generating UML class diagrams from Python source code. This tool analyzes Python files and generates PlantUML diagrams representing the class structure, relationships, and module organization of your codebase.

## Features

- Generates UML class diagrams from Python source code
- Supports recursive directory processing
- Detects class relationships (inheritance, composition, associations)
- Handles module-level functions
- Supports visibility modifiers (public, private, protected)
- Generates comprehensive documentation index
- Configurable output formats (currently supports PlantUML)

## Requirements

- Python 3.8+
- PlantUML (for rendering diagrams)

## Installation

1. Ensure you have Python 3.8 or higher installed
2. Install PlantUML (required for rendering diagrams)
3. The tool is part of the project utilities and doesn't require separate installation

## Usage

### Basic Usage

Process a single file:
```bash
python utils/run_uml_generator.py -f path/to/file.py
```

Process a directory:
```bash
python utils/run_uml_generator.py -d path/to/directory
```

Process a directory recursively:
```bash
python utils/run_uml_generator.py -d path/to/directory --recursive
```

### Advanced Options

- `--output PATH` or `-o PATH`: Specify output directory (default: docs/source/_generated_uml)
- `--format FORMAT`: Specify output format (default: plantuml)
- `--verbose` or `-v`: Enable verbose output
- `--quiet` or `-q`: Suppress all output except errors
- `--debug`: Enable debug logging
- `--show-imports`: Include import relationships in diagrams
- `--list-only`: List files without generating diagrams (for troubleshooting)
- `--subdirs`: Specify subdirectories to process (e.g., "models services")

### Examples

Generate diagrams for the backend app:
```bash
python utils/run_uml_generator.py -d backend/app --recursive
```

Generate diagrams with import relationships:
```bash
python utils/run_uml_generator.py -d backend/app --recursive --show-imports
```

Process specific subdirectories:
```bash
python utils/run_uml_generator.py -d backend/app --subdirs "models services" --recursive
```

## Output Structure

The tool generates:
- PlantUML (.puml) files for each processed Python file
- An index.rst file for documentation integration
- Organized directory structure matching input

Output location: `docs/source/_generated_uml/` (configurable)

## Configuration

The tool supports configuration through multiple sources, with the following precedence (highest to lowest):
1. Command-line arguments
2. Environment variables
3. User config file (~/.config/uml-generator/config.toml)
4. Project config file (.uml-generator.toml)
5. Default configuration

### Configuration File

Create a `.uml-generator.toml` file in your project directory:

```toml
[paths]
output_dir = "docs/uml"

[generator]
format = "plantuml"

[generator.plantuml]
settings = [
    "skinparam classAttributeIconSize 0",
    "skinparam monochrome true",
    "skinparam shadowing false"
]

[parser]
patterns = ["*.py"]
exclude_dirs = ["__pycache__", "*.egg-info"]
show_imports = true

[logging]
level = "info"
file = "uml-generator.log"
```

### Environment Variables

The following environment variables are supported:

- `UML_GENERATOR_OUTPUT_DIR`: Output directory for UML files
- `UML_GENERATOR_FORMAT`: Output format (e.g., "plantuml")
- `UML_GENERATOR_SHOW_IMPORTS`: Show import relationships (true/false)
- `UML_GENERATOR_LOG_LEVEL`: Logging level (debug/info/warning/error)
- `UML_GENERATOR_LOG_FILE`: Log file path

Example:
```bash
export UML_GENERATOR_OUTPUT_DIR="custom/output"
export UML_GENERATOR_SHOW_IMPORTS=true
python utils/run_uml_generator.py -d src
```

## Development

### Setup Development Environment

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Project Structure

```
uml_generator/
├── README.md
├── __init__.py           # Package initialization
├── cli.py               # Command-line interface
├── config/              # Configuration management
│   ├── __init__.py
│   ├── defaults.toml    # Default settings
│   └── loader.py        # Config loader
├── models/              # Data models
│   ├── __init__.py
│   └── models.py
├── parsers/             # Code parsers
│   ├── __init__.py
│   └── python_parser.py
├── generators/          # Diagram generators
│   ├── __init__.py
│   └── plantuml_generator.py
├── factories.py         # Factory classes
├── filesystem.py        # File operations
├── interfaces.py        # Abstract interfaces
├── service.py          # Core service logic
└── tests/              # Test suite
    ├── __init__.py
    ├── conftest.py     # Test fixtures
    ├── test_cli.py     # CLI tests
    ├── test_config.py  # Config tests
    ├── test_generator.py # Generator tests
    ├── test_integration.py # Integration tests
    └── test_parser.py  # Parser tests
```

### Running Tests

Run the complete test suite:
```bash
pytest
```

Run specific test categories:
```bash
pytest tests/test_parser.py  # Parser tests only
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
```

Generate coverage report:
```bash
pytest --cov=uml_generator --cov-report=html
```

### Code Quality

The project uses several tools to maintain code quality:

1. **Type Checking**:
   ```bash
   mypy uml_generator
   ```

2. **Linting**:
   ```bash
   ruff check uml_generator
   ```

3. **Code Formatting**:
   ```bash
   black uml_generator
   ```

### Adding New Features

1. Parser Enhancements:
   - Add support for new relationship types
   - Enhance type annotation parsing
   - Support additional Python features

2. Generator Enhancements:
   - Add support for new output formats
   - Customize diagram styling
   - Add new visualization options

3. Configuration:
   - Add new configuration options
   - Add custom templates
   - Enhance environment variable support

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass and code quality checks succeed
5. Update documentation
6. Submit a pull request

## Future Improvements

- Support for additional output formats (e.g., Mermaid, DOT)
- Enhanced relationship detection
- Custom annotation support
- Integration with documentation tools
- Additional parser features
- Performance optimizations
- CI/CD pipeline