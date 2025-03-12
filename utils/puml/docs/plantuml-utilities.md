# SOP-004: Using PlantUML Utilities

## Purpose

This procedure describes how to use the PlantUML utilities to create, render,
and view diagrams for the project. PlantUML is a tool that allows
you to create diagrams from text-based descriptions, making it easier to version
control and maintain diagrams.

## Scope

This procedure covers:

- Creating PlantUML diagram files
- Rendering diagrams to SVG or PNG format
- Viewing rendered diagrams with the React viewer
- Adding new diagrams to the project

This procedure does not cover:

- Installing PlantUML server
- Advanced PlantUML syntax and features

## Prerequisites

- Access to the project repository
- Python 3.6 or higher
- Virtual environment set up (optional but recommended)
- Basic understanding of PlantUML syntax

## Procedure

### 1. Install Required Dependencies

1. Activate the virtual environment (if using one):

   ```bash
   # For Windows Command Prompt/PowerShell
   .\.venv\Scripts\activate

   # For Git Bash/MINGW (Windows)
   source .venv/Scripts/activate

   # For macOS/Linux
   source .venv/bin/activate
   ```

2. Install the plantuml package:

   ```bash
   pip install plantuml
   ```

### 2. Create or Modify PlantUML Diagrams

1. Navigate to the `docs/diagrams` directory:

   ```bash
   cd docs/diagrams
   ```

2. Create a new directory for your diagrams if needed:

   ```bash
   mkdir -p your-category
   ```

3. Create or edit a PlantUML file (with `.puml` extension):

   ```bash
   # Example: Create a new diagram
   touch your-category/your-diagram.puml
   ```

4. Edit the file with your PlantUML code:

   ```plantuml
   @startuml "Your Diagram Title"

   ' Your PlantUML code here
   class Example {
     +attribute: Type
     +method(): ReturnType
   }

   @enduml
   ```

### 3. Render Diagrams

1. Return to the project root directory:

   ```bash
   cd /c/Repos/my-full-stack-fastapi-template  # For Git Bash
   # OR
   cd c:\Repos\my-full-stack-fastapi-template  # For Windows Command Prompt
   ```

2. Render all diagrams to SVG format (default):

   ```bash
   python -m utils.puml.cli render
   ```

3. Alternatively, render to PNG format:

   ```bash
   python -m utils.puml.cli render --format=png
   ```

4. To render a specific diagram:

   ```bash
   python -m utils.puml.cli render --file=your-category/your-diagram.puml
   ```

5. For best results, render both SVG and PNG formats:

   ```bash
   python -m utils.puml.cli render
   python -m utils.puml.cli render --format=png
   ```

### 4. View Diagrams with the React Viewer

1. Open the React viewer in your default browser:

   ```bash
   python -m utils.puml.cli view
   ```

   Or use the Make command:

   ```bash
   make view-diagrams
   ```

2. The React viewer will:

   - Automatically detect all diagram folders
   - Display all diagrams in each folder
   - Allow switching between SVG and PNG formats
   - Provide zoom controls for each diagram

3. Using the viewer interface:
   - Click on folder tabs in the sidebar to switch between diagram categories
   - Use the PNG/SVG buttons to switch formats
   - Use the zoom controls to zoom in, zoom out, or reset the zoom
   - Diagrams are displayed with formatted titles

### 5. Adding New Diagram Categories

1. To add a new diagram category:

   - Create a new directory under `docs/diagrams/`
   - Add your `.puml` files to this directory
   - Render the diagrams as described in section 3
   - The new category will automatically appear in the React viewer **if it's one of the known folders**

2. The React viewer automatically detects diagrams in the following folders:
   - `architecture`
   - `classifier`
   - `database`

3. If you add a new diagram to one of these folders, it will be automatically detected.
   However, if you add a new folder, you'll need to update the `knownFolders` array in
   `utils/puml/viewer/index.html`.

### 6. Using Make Commands (Recommended)

1. From the project root directory, use Make commands:

   ```bash
   # Render all diagrams to SVG
   make render-diagrams

   # Render all diagrams to PNG
   make render-diagrams-png

   # View diagrams
   make view-diagrams
   ```

## Verification

To verify that the procedure was completed successfully:

1. Check that the rendered diagrams exist in the `docs/diagrams/output`
   directory
2. Verify that the diagrams are displayed correctly in the React viewer
3. Confirm that both SVG and PNG formats can be viewed
4. Verify that all diagram categories appear in the sidebar
5. Confirm that all diagrams within each category are displayed

## Troubleshooting

### Common Issues

1. **Module not found error: `plantuml`**

   - Solution: Install the plantuml package with `pip install plantuml`

2. **Path issues in Git Bash**

   - Solution: Use forward slashes for paths and ensure the virtual environment
     is activated with `source .venv/Scripts/activate`

3. **Diagrams not rendering**

   - Solution: Check that the PlantUML syntax is correct and that the file has a
     `.puml` extension

4. **React viewer not showing diagrams**

   - Solution: Ensure that diagrams have been rendered first with
     `python -m utils.puml.cli render`
   - Check browser console for any JavaScript errors
   - Verify that both SVG and PNG files exist in the output directory

5. **New diagrams not appearing in the viewer**

   - Solution: Refresh the browser page after rendering new diagrams
   - Check that the diagrams were rendered successfully
   - Verify the diagram files exist in the correct output subdirectory

6. **Configuration issues**
   - Solution: Check the `utils/puml/config.py` file for correct paths and settings

## References

- [PlantUML Official Documentation](https://plantuml.com/en/guide)
- [PlantUML Syntax Guide](https://plantuml.com/en/guide)
- [Project PlantUML Utilities README](../../utils/puml/README.md)

## Revision History

| Version | Date       | Author | Changes                                |
| ------- | ---------- | ------ | -------------------------------------- |
| 1.0     | 2025-03-04 | Roo    | Initial version                        |
| 1.1     | 2025-03-05 | Roo    | Updated for dynamic HTML viewer        |
| 1.2     | 2025-03-11 | Roo    | Updated for React viewer and refactoring |
