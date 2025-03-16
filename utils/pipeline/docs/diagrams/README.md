# Classification System Diagrams

This directory contains PlantUML diagrams that document the classification system architecture and workflow.

## Viewing the Diagrams

You can view these diagrams in several ways:

1. **VSCode Extension**:
   - Install the "PlantUML" extension in VSCode
   - Open any .puml file
   - Use Alt+D to preview the diagram

2. **Online PlantUML Server**:
   - Visit [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
   - Copy and paste the diagram content

3. **Command Line**:
   ```bash
   # Install PlantUML (requires Java)
   # On Windows with Chocolatey:
   choco install plantuml
   
   # On macOS with Homebrew:
   brew install plantuml
   
   # Generate PNG images
   plantuml *.puml
   ```

## Available Diagrams

### 1. C4 Diagram (classification_c4.puml)
Shows the high-level architecture of the classification system using the C4 model:
- System boundaries
- Key components
- Component relationships
- Responsibilities

### 2. Class Diagram (classification_class.puml)
Details the object-oriented design:
- Class hierarchy
- Methods and attributes
- Relationships between classes
- Implementation of design patterns

### 3. Workflow Diagram (classification_workflow.puml)
Illustrates the classification process:
- Step-by-step flow
- Parallel classifier execution
- Decision points
- Ensemble voting process

### 4. ER Diagram (classification_er.puml)
Shows the configuration data model:
- Configuration entities
- Relationships
- Required and optional fields
- Data types

## Updating Diagrams

When updating these diagrams:
1. Follow PlantUML syntax and conventions
2. Maintain consistent styling
3. Update this README if adding new diagrams
4. Regenerate images after changes
