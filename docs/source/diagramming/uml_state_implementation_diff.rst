UML State Diagram Implementation Diff
================================

This file contains the implementation diff for adding state diagram support to the UML generator.

Implementation Diff
------------------

Below is a diff showing the changes needed to implement the state diagram extractor:

.. code-block:: diff

    # Create directories
    + mkdir -p utils/state_extractor
    + mkdir -p docs/source/_generated_uml/state

    # Create files
    + touch utils/state_extractor/__init__.py
    + touch utils/state_extractor/models.py
    + touch utils/state_extractor/analyzer.py
    + touch utils/state_extractor/generator.py
    + touch utils/extract_state.py
    + touch utils/state_decorators.py

    # Modify run_uml_generator.py
    diff --git a/utils/run_uml_generator.py b/utils/run_uml_generator.py
    index abcdefg..1234567 100644
    --- a/utils/run_uml_generator.py
    +++ b/utils/run_uml_generator.py
    @@ -11,6 +11,7 @@ from utils.uml_generator.factories import DefaultGeneratorFactory
     from utils.uml_generator.service import UmlGeneratorService
     from utils.sequence_extractor import SequenceAnalyzer, PlantUmlSequenceGenerator
     from utils.activity_extractor import ActivityAnalyzer, PlantUmlActivityGenerator
    +from utils.state_extractor import StateAnalyzer, PlantUmlStateGenerator
     
     
     def generate_class_diagrams(base_dir: Path, output_dir: Path) -> None:
    @@ -76,6 +77,36 @@ def generate_activity_diagrams(base_dir: Path, output_dir: Path) -> None:
                 print(f"Could not generate activity diagram for {class_name}.{method_name}: {e}")
     
     
    +def generate_state_diagrams(base_dir: Path, output_dir: Path) -> None:
    +    """Generate state diagrams from Python code."""
    +    print("Generating state diagrams...")
    +    
    +    # Define the source directory to analyze
    +    source_dir = base_dir / "backend" / "app"
    +    
    +    # Create the output directory
    +    state_output_dir = output_dir / "state"
    +    state_output_dir.mkdir(parents=True, exist_ok=True)
    +    
    +    # Create analyzer and analyze the source
    +    analyzer = StateAnalyzer(source_dir)
    +    analyzer.analyze_directory()
    +    
    +    # Define classes to generate diagrams for
    +    targets = [
    +        "Document",
    +        "Order",
    +        "User",
    +        # Add more targets as needed
    +    ]
    +    
    +    # Generate diagrams for each target
    +    for class_name in targets:
    +        try:
    +            diagram = analyzer.generate_state_diagram(class_name)
    +            generator = PlantUmlStateGenerator()
    +            output_file = state_output_dir / f"{class_name}_state.puml"
    +            generator.generate_file(diagram, output_file)
    +            print(f"Generated state diagram for {class_name}")
    +        except ValueError as e:
    +            print(f"Could not generate state diagram for {class_name}: {e}")
    +
     def main():
         """Run the UML generator."""
         base_dir = Path(__file__).parent.parent
    @@ -118,6 +149,9 @@ def main():
         # Generate activity diagrams
         generate_activity_diagrams(base_dir, output_dir)
         
    +    # Generate state diagrams
    +    generate_state_diagrams(base_dir, output_dir)
    +    
         print(f"UML diagrams generated in {output_dir}")
     
     
    # Update docs/source/uml_diagrams.rst
    diff --git a/docs/source/uml_diagrams.rst b/docs/source/uml_diagrams.rst
    index abcdefg..1234567 100644
    --- a/docs/source/uml_diagrams.rst
    +++ b/docs/source/uml_diagrams.rst
    @@ -30,3 +30,14 @@ Generate Sequence Diagram Flow
     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     
     .. uml:: ../_generated_uml/activity/SequenceAnalyzer_generate_sequence_diagram_activity.puml
    +
    +State Diagrams
    +-------------
    +
    +Document Lifecycle
    +~~~~~~~~~~~~~~~~
    +
    +.. uml:: ../_generated_uml/state/Document_state.puml
    +
    +Order Processing
    +~~~~~~~~~~~~~~~
    +
    +.. uml:: ../_generated_uml/state/Order_state.puml

Key files created:

- ``utils/state_extractor/models.py`` - Data models for state diagrams
- ``utils/state_extractor/analyzer.py`` - AST-based analyzer for state patterns
- ``utils/state_extractor/generator.py`` - PlantUML generator for state diagrams
- ``utils/state_extractor/__init__.py`` - Package initialization
- ``utils/extract_state.py`` - Command-line tool
- ``utils/state_decorators.py`` - Decorators for marking states and transitions

The state diagram extractor can analyze Python classes to extract state patterns, including:

- Explicit state field assignments
- State transition methods
- Decorator-based state definitions

The extracted diagrams show the states of objects or systems and the transitions between them, which is particularly useful for understanding object lifecycles and reactive systems.