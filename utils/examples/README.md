# UML Generator Examples

This directory contains examples demonstrating how to use the UML generator.

## Files

- `uml_structure.puml`: A PlantUML diagram showing the architecture of the UML generator itself
- `generate_uml_diagram.py`: A Python script demonstrating how to generate UML diagrams from code

## Using the UML Generator

The UML generator can be used in several ways:

### 1. Using the individual extraction scripts

```bash
# Generate class diagrams
python utils/extract_class.py --source path/to/source --output path/to/output

# Generate sequence diagrams
python utils/extract_sequence.py --source path/to/source --output path/to/output

# Generate activity diagrams
python utils/extract_activity.py --source path/to/source --output path/to/output

# Generate state diagrams
python utils/extract_state.py --source path/to/source --output path/to/output
```

### 2. Using the unified entry point

```bash
# Generate all diagram types
python utils/uml/run.py --type all --source path/to/source --output path/to/output

# Generate a specific diagram type
python utils/uml/run.py --type class --source path/to/source --output path/to/output
```

### 3. Using the run_uml.py script (with virtual environment)

First, set up the virtual environment:

```bash
python utils/install_dev.py
```

Then run the UML generator using the run_uml.py script:

```bash
python utils/run_uml.py extract_class.py --source path/to/source --output path/to/output
```

### 4. Using the main run_uml_generator.py script

This script generates diagrams for the entire project structure:

```bash
python utils/run_uml_generator.py
```

## Viewing the Generated Diagrams

The generated diagrams are in PlantUML format (.puml files). To view them, you can:

1. Use the PlantUML extension in VSCode
2. Use the PlantUML server at http://www.plantuml.com/plantuml/
3. Convert them to images using the PlantUML jar

## Example: Generate a UML Diagram of the UML Generator

To generate a UML diagram of the UML generator itself, run:

```bash
python utils/examples/generate_uml_diagram.py
```

This will generate class diagrams of the UML generator code in the `docs/source/_generated_uml/examples` directory.

## Example: View the UML Structure Diagram

The `uml_structure.puml` file contains a pre-created diagram showing the architecture of the UML generator. You can view this file using any PlantUML viewer.
