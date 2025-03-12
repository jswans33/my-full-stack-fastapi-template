# PlantUML Utilities

This package provides utilities for working with PlantUML diagrams in the project.

## Features

- Render PlantUML diagrams to PNG or SVG images
- View rendered diagrams in a React-based viewer
- Analyze code and generate PlantUML diagrams automatically
- Command-line interface for rendering, viewing, and analyzing code

## Requirements

- Python 3.6+
- plantuml package (`pip install plantuml`)
- Internet connection (for the PlantUML server)

## Usage

### Command Line Interface

```bash
# Render all diagrams to SVG (default)
make render-diagrams

# Render all diagrams to PNG
make render-diagrams-png

# View diagrams in the React viewer
make view-diagrams
```

Or use the Python CLI directly:

```bash
# Render all diagrams to SVG (default)
python -m utils.puml.cli render

# Render all diagrams to PNG
python -m utils.puml.cli render --format=png

# Render a specific diagram
python -m utils.puml.cli render --file=classifier/classifier_model_diagram.puml

# View diagrams in the React viewer
python -m utils.puml.cli view

# Analyze code and generate a class diagram
python -m utils.puml.cli analyze --path=path/to/code

# Analyze code and generate a module diagram
python -m utils.puml.cli analyze --path=path/to/code --modules

# Analyze code and include standalone functions in the class diagram
python -m utils.puml.cli analyze --path=path/to/code --functions

# Analyze code with verbose logging
python -m utils.puml.cli analyze --path=path/to/code --verbose
```

### Python API

```python
from utils.puml import render_diagram, render_all_diagrams

# Render a specific diagram to PNG
render_diagram('docs/diagrams/classifier/classifier_model_diagram.puml',
               output_dir='docs/diagrams/output',
               format='png')

# Render all diagrams to SVG
render_all_diagrams('docs/diagrams',
                    output_dir='docs/diagrams/output',
                    format='svg')
```

### Code Analysis API

```python
from utils.puml import (
    analyze_directory, analyze_file,
    generate_class_diagram, generate_module_diagram,
    save_diagram, analyze_and_generate_diagram
)

# Quick way to analyze code and generate a diagram
output_file = analyze_and_generate_diagram(
    path='path/to/code',
    modules=False,  # Set to True for module diagram
    functions=True  # Include standalone functions
)

# Or use the individual functions for more control
visitors = analyze_directory('path/to/code')

# Generate a class diagram
class_diagram = generate_class_diagram(visitors, include_functions=True)

# Generate a module diagram
module_diagram = generate_module_diagram(visitors)

# Save the diagram to a file
save_diagram(class_diagram, 'docs/diagrams/code_analysis/class_diagram.puml')
```

## Configuration

Configuration settings are stored in `utils/puml/config.py`. You can modify these settings to change the default behavior of the utilities.

```python
# Default source directory for diagrams
SOURCE_DIR = os.path.join(PROJECT_ROOT, "docs", "diagrams")

# Default output directory for rendered diagrams
OUTPUT_DIR = os.path.join(SOURCE_DIR, "output")

# Default output format
DEFAULT_FORMAT = "svg"
```

## Directory Structure

```
utils/puml/
├── __init__.py          # Package initialization and public API
├── config.py            # Configuration settings
├── core.py              # Core utilities and shared functions
├── cli.py               # Command-line interface
├── render_diagrams.py   # Diagram rendering functions
├── code_analyzer.py     # Code analysis and diagram generation
├── test_puml.py         # Test script for rendering
├── test_code_analyzer.py # Test script for code analysis
├── viewer/              # React-based diagram viewer
│   └── index.html       # Viewer HTML file
└── README.md            # This file
```

## Adding New Diagrams

1. Create a new `.puml` file in the `docs/diagrams` directory
2. Run `make render-diagrams` to render the diagram
3. Run `make view-diagrams` to view the diagram in the React viewer

**Note:** The React viewer automatically detects diagrams in the following folders:

- `architecture`
- `classifier`
- `database`

If you add a new diagram to one of these folders, it will be automatically detected. However, if you add a new folder, you'll need to update the `knownFolders` array in `utils/puml/viewer/index.html`.

## Analyzing Code

The code analyzer can generate PlantUML diagrams from your Python code automatically. It analyzes the code structure and creates diagrams showing classes, functions, and their relationships.

### Class Diagrams

Class diagrams show the classes in your code, their attributes, methods, and inheritance relationships:

```bash
# Analyze a specific file
python -m utils.puml.cli analyze --path=path/to/file.py

# Analyze a directory (recursively)
python -m utils.puml.cli analyze --path=path/to/directory

# Include standalone functions in the diagram
python -m utils.puml.cli analyze --path=path/to/code --functions
```

### Module Diagrams

Module diagrams show the dependencies between modules in your code:

```bash
# Generate a module diagram
python -m utils.puml.cli analyze --path=path/to/code --modules
```

### Workflow

1. Analyze your code to generate a PlantUML diagram:

   ```bash
   python -m utils.puml.cli analyze --path=backend/app
   ```

2. Render the generated diagram:

   ```bash
   python -m utils.puml.cli render --file=code_analysis/app_class_diagram.puml
   ```

3. View the rendered diagram:

   ```bash
   python -m utils.puml.cli view
   ```

The generated diagrams will be saved in the `docs/diagrams/output/code_analysis` directory.

## Troubleshooting

- If the diagrams are not rendering, check your internet connection. The PlantUML server requires an internet connection to render diagrams.
- If the viewer is not showing the diagrams, make sure you have rendered the diagrams first using `make render-diagrams`.
- If the code analyzer is not finding all classes or relationships, try using the `--verbose` flag to see more detailed logging: `python -m utils.puml.cli analyze --path=path/to/code --verbose`
- If the generated diagrams are too complex or cluttered, try analyzing smaller portions of your codebase or specific files instead of entire directories.
- For large codebases, the module diagram (`--modules`) might be more readable than the class diagram.
