# PlantUML Diagram Viewer Guide

## Overview

This directory contains utilities for generating and viewing PlantUML diagrams. The system consists of:

1. A CLI tool for rendering diagrams
2. A FastAPI server for serving diagrams
3. An HTML viewer for displaying diagrams

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

## Detailed Steps

### 1. Rendering Diagrams

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

### 2. Starting the Server

- The FastAPI server must be running to view diagrams
- Server serves static files from docs/diagrams/output
- Uses default port 8000
- Hot reloading enabled for development

```bash
cd utils/puml
python -m uvicorn api:app --reload
```

### 3. Viewing Diagrams

- Access the viewer at <http://127.0.0.1:8000>
- Diagrams are organized by directory
- Supports both SVG and PNG formats
- Features:
  - Zoom controls
  - Pan support
  - Format switching

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

## Directory Structure

```
utils/puml/
├── api.py              # FastAPI server implementation
├── cli.py             # Command-line interface
├── render_diagrams.py # Diagram rendering logic
└── settings.py        # Configuration settings

docs/diagrams/
├── [source diagrams]  # .puml source files
└── output/           # Rendered diagrams and viewer
    ├── index.html    # Main viewer interface
    └── [diagrams]    # Rendered SVG/PNG files
```
