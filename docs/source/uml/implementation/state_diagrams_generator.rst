UML State Diagram Generator
=========================

This section details the generator component for state diagram extraction. The generator converts state diagram models to PlantUML format.

Generator Overview
---------------

The state diagram generator is responsible for:

1. Converting state diagram models to PlantUML syntax
2. Formatting states, transitions, and other elements
3. Writing the generated PlantUML code to files

Implementation
------------

The following code shows the implementation of the state diagram generator in ``utils/state_extractor/generator.py``:

.. code-block:: python

    """Generator for converting state diagrams to PlantUML format."""
    
    from pathlib import Path
    
    from .models import State, StateDiagram, StateType, Transition
    
    
    class PlantUmlStateGenerator:
        """Generates PlantUML state diagrams from our state model."""
        
        def __init__(self):
            self.indentation = "  "
            self.current_indent = 0
        
        def _indent(self) -> str:
            """Get the current indentation string."""
            return self.indentation * self.current_indent
        
        def _increase_indent(self) -> None:
            """Increase indentation level."""
            self.current_indent += 1
        
        def _decrease_indent(self) -> None:
            """Decrease indentation level."""
            self.current_indent = max(0, self.current_indent - 1)
        
        def _format_state(self, state: State) -> str:
            """Format a state as PlantUML."""
            if state.type == StateType.INITIAL:
                return f"[*] --> {state.name}"
            elif state.type == StateType.FINAL:
                return f"{state.name} --> [*]"
            
            # Normal state
            lines = [f"state {state.name} {{"]
            self._increase_indent()
            
            # Add entry actions
            if state.entry_actions:
                lines.append(f"{self._indent()}entry / {'; '.join(state.entry_actions)}")
            
            # Add exit actions
            if state.exit_actions:
                lines.append(f"{self._indent()}exit / {'; '.join(state.exit_actions)}")
            
            # Add internal actions
            for event, action in state.internal_actions.items():
                lines.append(f"{self._indent()}{event} / {action}")
            
            self._decrease_indent()
            lines.append("}")
            
            return "\n".join(lines)
        
        def _format_transition(self, transition: Transition) -> str:
            """Format a transition as PlantUML."""
            # Get states by ID
            source_id = transition.source_id
            target_id = transition.target_id
            
            # Build the transition line
            parts = []
            
            if transition.event:
                parts.append(transition.event)
            
            if transition.guard:
                parts.append(f"[{transition.guard}]")
            
            if transition.action:
                parts.append(f"/ {transition.action}")
            
            if parts:
                label = " ".join(parts)
                return f"{source_id} --> {target_id} : {label}"
            else:
                return f"{source_id} --> {target_id}"
        
        def generate_plantuml(self, diagram: StateDiagram) -> str:
            """Generate PlantUML code from a state diagram model."""
            lines = ["@startuml", ""]
            
            # Add title
            if diagram.title:
                lines.append(f"title {diagram.title}")
                lines.append("")
            
            # Add skinparam settings
            lines.extend(
                [
                    "skinparam State {",
                    "  BackgroundColor white",
                    "  BorderColor black",
                    "  ArrowColor black",
                    "}",
                    "",
                ]
            )
            
            # Add states
            for state in diagram.states:
                if state.type != StateType.INITIAL and state.type != StateType.FINAL:
                    lines.append(self._format_state(state))
            
            lines.append("")
            
            # Add initial transitions if defined
            if diagram.initial_state_id:
                for state in diagram.states:
                    if state.id == diagram.initial_state_id:
                        lines.append(f"[*] --> {state.name}")
                        break
            
            # Add all other transitions
            for transition in diagram.transitions:
                # Get source and target states
                source_state = next(
                    (s for s in diagram.states if s.id == transition.source_id), None
                )
                target_state = next(
                    (s for s in diagram.states if s.id == transition.target_id), None
                )
                
                if source_state and target_state:
                    lines.append(
                        f"{source_state.name} --> {target_state.name} : {transition.event or ''}"
                        + (f" [{transition.guard}]" if transition.guard else "")
                        + (f" / {transition.action}" if transition.action else "")
                    )
            
            # End the diagram
            lines.append("")
            lines.append("@enduml")
            
            return "\n".join(lines)
        
        def generate_file(
            self,
            diagram: StateDiagram,
            output_path: str | Path,
        ) -> None:
            """Generate a PlantUML file from a state diagram model."""
            plantuml_code = self.generate_plantuml(diagram)
            
            # Ensure output directory exists
            output_path = Path(output_path) if isinstance(output_path, str) else output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(plantuml_code)

How the Generator Works
--------------------

The state diagram generator works by:

1. **Formatting States**: It formats each state in the diagram, including entry/exit actions and internal actions.

2. **Formatting Transitions**: It formats transitions between states, including events, guards, and actions.

3. **Generating PlantUML Code**: It combines the formatted states and transitions into a complete PlantUML diagram.

4. **Writing to File**: It writes the generated PlantUML code to a file.

The generator uses a simple indentation system to format the PlantUML code, making it easy to read and maintain.

PlantUML Syntax for State Diagrams
--------------------------------

The generator produces PlantUML code that follows the standard syntax for state diagrams:

- **States**: `state StateName { ... }`
- **Initial State**: `[*] --> StateName`
- **Final State**: `StateName --> [*]`
- **Transitions**: `StateA --> StateB : event [guard] / action`
- **Entry Actions**: `entry / action`
- **Exit Actions**: `exit / action`

Example PlantUML Output
--------------------

Here's an example of the PlantUML code generated for a simple document state machine:

.. code-block:: text

    @startuml
    
    title Document State Diagram
    
    skinparam State {
      BackgroundColor white
      BorderColor black
      ArrowColor black
    }
    
    state draft {
      entry / create empty document
    }
    
    state review {
      entry / notify reviewers
    }
    
    state approved {
      entry / notify author
    }
    
    state published {
      entry / update timestamp; generate public link
    }
    
    [*] --> draft
    
    draft --> review : submit
    review --> draft : request_changes
    review --> approved : approve [all_reviewers_approved]
    approved --> published : publish
    
    @enduml

This PlantUML code can be rendered to produce a visual state diagram.

Usage Example
-----------

Here's an example of how to use the state diagram generator:

.. code-block:: python

    from pathlib import Path
    from utils.state_extractor import StateAnalyzer, PlantUmlStateGenerator
    
    # Create analyzer and analyze source code
    analyzer = StateAnalyzer("./backend/app")
    analyzer.analyze_directory()
    
    # Generate state diagram for a specific class
    diagram = analyzer.generate_state_diagram("Document")
    
    # Create generator and generate PlantUML file
    generator = PlantUmlStateGenerator()
    output_path = Path("docs/source/_generated_uml/state/Document_state.puml")
    generator.generate_file(diagram, output_path)

This will generate a PlantUML file for the Document class's state diagram.

Module Initialization
------------------

The state extractor package is initialized in ``utils/state_extractor/__init__.py``:

.. code-block:: python

    """State diagram extractor for Python code.
    
    This module provides functionality to extract state diagrams from Python code
    through static analysis of state patterns and state transitions.
    """
    
    from .analyzer import StateAnalyzer
    from .generator import PlantUmlStateGenerator
    from .models import State, StateDiagram, StateType, Transition
    
    __all__ = [
        "State",
        "StateAnalyzer",
        "StateDiagram",
        "StateType",
        "Transition",
        "PlantUmlStateGenerator",
    ]

This makes it easy to import the necessary classes and functions for state diagram extraction.