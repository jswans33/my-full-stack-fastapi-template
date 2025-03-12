# PlantUML Utilities

This package provides utilities for working with PlantUML diagrams in the project.

## Features

- Render PlantUML diagrams to PNG or SVG images
- View rendered diagrams in a React-based viewer
- Command-line interface for rendering and viewing diagrams

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
├── __init__.py          # Package initialization
├── config.py            # Configuration settings
├── cli.py               # Command-line interface
├── render_diagrams.py   # Diagram rendering functions
├── test_puml.py         # Test script
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

## Troubleshooting

- If the diagrams are not rendering, check your internet connection. The PlantUML server requires an internet connection to render diagrams.
- If the viewer is not showing the diagrams, make sure you have rendered the diagrams first using `make render-diagrams`.
