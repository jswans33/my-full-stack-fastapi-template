# PlantUML Utilities Guide

## Overview

This directory contains utilities for generating and viewing PlantUML diagrams, as well as analyzing Python code structure. The system consists of:

1. A CLI tool for rendering diagrams and analyzing code
2. A FastAPI server for serving diagrams
3. An HTML viewer for displaying diagrams
4. A code analyzer for generating diagrams from Python code

## Quick Start

```bash
# From the project root directory:
cd c:/Repos/FCA-dashboard3/my-full-stack-fastapi-template

# 1. First, render all diagrams to SVG format
python -m utils.puml.cli render

# 2. Start the FastAPI server (keep this running)
cd utils/puml
python -m uvicorn api:app --reload

# 3. View the diagrams in your browser
# The viewer will automatically open at http://127.0.0.1:8000
```

## Features

### 1. Diagram Rendering

- The `render` command processes all .puml files in the docs/diagrams directory
- Diagrams are rendered to SVG format by default
- Output is saved to docs/diagrams/output
- The index.html viewer file is automatically updated

```bash
# Render all diagrams
python -m utils.puml.cli render

# Render specific diagram
python -m utils.puml.cli render --file=path/to/diagram.puml

# Render to PNG format
python -m utils.puml.cli render --format=png
```

### 2. Code Analysis

The code analyzer can generate PlantUML diagrams from your Python code:

```bash
# Generate class diagram
python -m utils.puml.cli analyze --path=path/to/code

# Generate module dependency diagram
python -m utils.puml.cli analyze --path=path/to/code --modules

# Include private members
python -m utils.puml.cli analyze --path=path/to/code --include-private

# Analyze with custom exclude patterns
python -m utils.puml.cli analyze --path=path/to/code --exclude="tests/*,examples/*"

# Show progress for large codebases
python -m utils.puml.cli analyze --path=path/to/code --progress
```

#### Analysis Features

1. Class Analysis:

   - Class definitions and inheritance
   - Methods and attributes with type hints
   - Method signatures and return types
   - Docstrings and documentation

2. Import Analysis:

   - Direct and indirect imports
   - Import aliases and usage tracking
   - Star imports detection
   - Relative import resolution
   - Unused import detection

3. Dependency Analysis:

   - Module dependencies
   - Package hierarchies
   - Import relationships
   - Used vs unused imports

4. Filtering Options:
   - Include/exclude private members
   - Custom exclude patterns
   - Package/module filtering

### 3. Diagram Viewing

- Access the viewer at <http://127.0.0.1:8000>
- Diagrams are organized by directory
- Supports both SVG and PNG formats
- Features:
  - Zoom controls
  - Pan support
  - Format switching

## Server Setup

- The FastAPI server must be running to view diagrams
- Server serves static files from docs/diagrams/output
- Uses default port 8000
- Hot reloading enabled for development

```bash
cd utils/puml
python -m uvicorn api:app --reload
```

## Troubleshooting

### Common Issues

1. **Diagrams not showing up**

   - Ensure diagrams are rendered first (`python -m utils.puml.cli render`)
   - Check server is running on correct port
   - Verify files exist in docs/diagrams/output

2. **Server won't start**

   - Check port 8000 is not in use
   - Ensure you're in utils/puml directory
   - Verify uvicorn is installed

3. **Viewer not loading**

   - Ensure server is running
   - Check browser console for errors
   - Try clearing browser cache

4. **Code analysis issues**
   - Check file permissions
   - Verify Python files are valid
   - Check exclude patterns
   - Enable verbose logging with --verbose

## Directory Structure

```
utils/puml/
├── __init__.py         # Package initialization
├── api.py             # FastAPI server implementation
├── cli.py            # Command-line interface
├── analyzer.py       # Code analysis implementation
├── code_analyzer.py  # Code analysis coordination
├── models.py        # Data models for analysis
├── diagram_generator.py # Diagram generation
├── render_diagrams.py # Diagram rendering logic
├── settings.py       # Configuration settings
└── exceptions.py    # Custom exceptions

docs/diagrams/
├── [source diagrams]  # .puml source files
└── output/           # Rendered diagrams and viewer
    ├── index.html    # Main viewer interface
    └── [diagrams]    # Rendered SVG/PNG files
```

## Configuration

The analyzer can be configured through settings in `settings.py`:

- Default exclude patterns
- Output directory structure
- Logging configuration
- Rendering options

## Contributing

When adding new features:

1. Update tests in the tests/ directory
2. Update documentation in this README
3. Add examples to the examples/ directory
4. Follow the existing code style and patterns
