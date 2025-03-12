# UML Generator Usage Guide

This utility generates PlantUML class diagrams from Python source code. It analyzes Python files, extracts class definitions, methods, attributes, and relationships, and generates PlantUML diagrams.

## Features

- **File-by-File UML Generation**: Each Python file gets its own UML diagram
- **Visual File Grouping**: Classes are grouped by source file in packages
- **Method Parameter Parsing**: Support for complex type annotations, default values, \*args, \*\*kwargs
- **Visibility Indicators**: Public/private/protected indicators for attributes and methods
- **Relationship Detection**: Detects associations, compositions, and inheritance from type annotations
- **Import Tracking**: Identifies and displays imports (classes, functions, and types) between modules
- **Comprehensive CLI**: Multiple input options, configurable output directory, verbosity control

## Installation

No additional installation is required beyond the standard Python libraries. The script uses the `ast` module for parsing Python code.

## Usage

### Basic Usage

```bash
# Process a single file
python backend/scripts/utils/generate_uml.py -f path/to/file.py

# Process a directory
python backend/scripts/utils/generate_uml.py -d path/to/directory

# Process the app directory
python backend/scripts/utils/generate_uml.py --app-dir
```

### Command-Line Options

```
usage: generate_uml.py [-h] (-f FILE | -d DIRECTORY | --app-dir) [-o OUTPUT]
                      [--subdirs SUBDIRS [SUBDIRS ...]] [--recursive]
                      [--list-only] [--show-imports]
                      [-v | -q | --debug]

Generate PlantUML class diagrams from Python source code.

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Process a single Python file (default: None)
  -d DIRECTORY, --directory DIRECTORY
                        Process a directory containing Python files (default: None)
  --app-dir             Process the app directory (default: False)
  -o OUTPUT, --output OUTPUT
                        Output directory for PlantUML files (default: docs/source/_generated_uml)
  --subdirs SUBDIRS [SUBDIRS ...]
                        List of subdirectories to process (only with --directory or --app-dir) (default: ['models', 'services'])
  --recursive           Recursively process directories (default: False)
  --list-only           Only list Python files without generating UML diagrams (for troubleshooting) (default: False)
  --show-imports        Show imports (classes, functions, and types) in the UML diagrams (default: False)
  --generate-report     Generate a report of files processed and the number of classes and functions found (default: False)
  -v, --verbose         Enable verbose output (default: False)
  -q, --quiet           Suppress all output except errors (default: False)
  --debug               Enable debug logging (default: False)
```

### Examples

#### Process a Single File

```bash
python backend/scripts/utils/generate_uml.py -f backend/app/models.py
```

This will generate a UML diagram for the `models.py` file and save it to `docs/source/_generated_uml/models.puml`.

#### Process a Directory

```bash
python backend/scripts/utils/generate_uml.py -d backend/app
```

This will process all Python files in the `backend/app` directory and generate UML diagrams for each file.

#### Process the App Directory with Specific Subdirectories

```bash
python backend/scripts/utils/generate_uml.py --app-dir --subdirs models api core
```

This will process the app directory and the specified subdirectories (`models`, `api`, `core`).

#### Process a Directory Recursively

```bash
python backend/scripts/utils/generate_uml.py -d backend/app --recursive
```

This will recursively process all Python files in the `backend/app` directory and its subdirectories.

#### Specify a Custom Output Directory

```bash
python backend/scripts/utils/generate_uml.py -d backend/app -o custom/output/path
```

This will save the generated UML diagrams to the specified output directory.

#### Show Imports in UML Diagrams

```bash
python backend/scripts/utils/generate_uml.py -d backend/app --show-imports
```

This will include import relationships in the UML diagrams, showing which classes import other classes, functions, and types. This is particularly useful for understanding dependencies between modules.

#### List Files Without Generating UML Diagrams

```bash
python backend/scripts/utils/generate_uml.py -d backend/app --list-only
```

This will only list the Python files found in the directory without generating UML diagrams. This is useful for troubleshooting when you want to see which files would be processed.

#### Enable Verbose Logging

```bash
python backend/scripts/utils/generate_uml.py -d backend/app -v
```

This will enable verbose logging, showing more information about the processing.

## Output

The script generates PlantUML files (`.puml`) in the specified output directory. Each Python file gets its own UML diagram.

The UML diagrams include:

- Classes with their attributes and methods
- Visibility indicators for attributes and methods
- Inheritance relationships
- Associations and compositions detected from type annotations
- Classes grouped by source file in packages
- Import relationships (when using the `--show-imports` option)

## Sphinx Integration

The script automatically generates an `index.rst` file in the output directory, which can be used to integrate the UML diagrams into Sphinx documentation.

### Setup

1. Install the required dependencies:

```bash
pip install sphinxcontrib-plantuml
```

2. Configure Sphinx in your `docs/source/conf.py` file:

```python
extensions = [
    # existing extensions...
    'sphinxcontrib.plantuml',
]

plantuml = 'java -jar /path/to/plantuml.jar'
plantuml_output_format = 'svg'  # or png
```

3. Include the generated UML diagrams in your Sphinx documentation by creating a file like `docs/source/uml_diagrams.rst`:

```rst
UML Diagrams
============

.. include:: _generated_uml/index.rst
```

4. Add this file to your main `docs/source/index.rst`:

```rst
Welcome to My Project Docs
==========================

.. toctree::
   :maxdepth: 2

   uml_diagrams
   other_sections...
```

### Automation

You can automate the documentation generation by adding the following to your `Makefile`:

```makefile
docs-uml:
 python backend/scripts/utils/generate_uml.py --app-dir --output docs/source/_generated_uml

docs:
 make docs-uml
 cd docs && make html

docs-open:
 make docs
 open docs/build/html/index.html
```

## Viewing UML Diagrams

To view the generated UML diagrams directly, you need a PlantUML viewer. You can use:

- [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
- [PlantUML Extension for VS Code](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml)
- [PlantUML Viewer for JetBrains IDEs](https://plugins.jetbrains.com/plugin/7017-plantuml-integration)

## Troubleshooting

### No Classes Found

If the script reports "No classes found in file", make sure the file contains class definitions.

### File Not Found

If the script reports "File not found", check the file path and make sure it exists.

### Not a Python File

If the script reports "Not a Python file", make sure the file has a `.py` extension.

### Directory Not Found

If the script reports "Directory not found", check the directory path and make sure it exists.

## Contributing

Feel free to contribute to this utility by:

- Adding new features
- Fixing bugs
- Improving documentation
- Adding tests

## License

This utility is provided as-is, without any warranty or support.

python backend/scripts/utils/generate_uml.py -d backend/app --recursive
