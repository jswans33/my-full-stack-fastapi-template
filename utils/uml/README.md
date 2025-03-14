# UML Diagram Generation Package

This package provides tools for generating UML diagrams from Python code. It supports class, sequence, activity, and state diagrams.

## Installation

The package is designed to be installed as a Python package. To install it in development mode:

```bash
# From the project root directory
pip install -e utils/uml
```

This will install the package in "editable" mode, allowing you to make changes to the code without reinstalling.

## Usage

### Command Line Interface

The package provides several command-line scripts for generating UML diagrams:

```bash
# Generate all diagram types
python -m utils.uml.run --source path/to/source --output path/to/output

# Generate class diagrams
python -m utils.uml.cli.extract_class --source path/to/source

# Generate sequence diagrams
python -m utils.uml.cli.extract_sequence --source path/to/source

# Generate activity diagrams
python -m utils.uml.cli.extract_activity --source path/to/source

# Generate state diagrams
python -m utils.uml.cli.extract_state --source path/to/source

# Run the UML generator on the backend/app directory
python -m utils.uml.cli.run_uml_generator

# Extract sequence diagrams from key entry points in the application
python -m utils.uml.cli.extract_app_sequences
```

### Programmatic Usage

You can also use the package programmatically:

```python
from utils.uml import DefaultFileSystem, UmlService, DefaultDiagramFactory

# Create service
file_system = DefaultFileSystem()
factory = DefaultDiagramFactory(file_system)
service = UmlService(factory)

# Generate a diagram
service.generate_diagram(
    "class",                  # Diagram type: "class", "sequence", "activity", "state"
    "path/to/source",         # Source file or directory
    "path/to/output.puml",    # Output file
    recursive=True,           # Recursively analyze directories
    include_private=False,    # Include private members in diagrams
)
```

## Architecture

The package follows a modular architecture:

- **Core**: Core interfaces and implementations
  - `filesystem.py`: File system abstraction
  - `service.py`: Main service for generating diagrams
  - `interfaces.py`: Interfaces for analyzers and generators
  - `exceptions.py`: Custom exceptions

- **Diagrams**: Diagram-specific implementations
  - `class_diagram/`: Class diagram analyzer and generator
  - `sequence_diagram/`: Sequence diagram analyzer and generator
  - `activity_diagram/`: Activity diagram analyzer and generator
  - `state_diagram/`: State diagram analyzer and generator

- **CLI**: Command-line interfaces
  - `extract_class.py`: Extract class diagrams
  - `extract_sequence.py`: Extract sequence diagrams
  - `extract_activity.py`: Extract activity diagrams
  - `extract_state.py`: Extract state diagrams
  - `extract_app_sequences.py`: Extract sequence diagrams from key entry points
  - `run_uml_generator.py`: Run the UML generator on the backend/app directory

- **Utils**: Utility functions
  - `paths.py`: Path utilities

- **Factories**: Factory classes for creating analyzers and generators
  - `factories.py`: Default factory implementation

## Development

### Adding a New Diagram Type

To add a new diagram type:

1. Create a new directory under `diagrams/` for the new diagram type
2. Implement an analyzer and generator for the new diagram type
3. Register the new diagram type in `factories.py`
4. Add a new CLI script for the new diagram type

### Testing

To test the package:

```bash
# Run tests
pytest utils/uml/tests
