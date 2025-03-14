UML State Diagram Usage
=====================

This section details how to use the state diagram extraction tools, including the command-line interface, integration with the main UML generator, and state decorators for explicit state machine definitions.

Command-Line Interface
-------------------

The state diagram extractor provides a command-line interface for generating state diagrams from Python code. The CLI tool is implemented in ``utils/extract_state.py``:

.. code-block:: python

    #!/usr/bin/env python
    """Extract state diagrams from Python code."""
    
    import argparse
    from pathlib import Path
    
    from utils.state_extractor import StateAnalyzer, PlantUmlStateGenerator
    
    
    def main():
        """Run the state diagram extractor."""
        parser = argparse.ArgumentParser(
            description="Extract state diagrams from Python code"
        )
        parser.add_argument(
            "--source",
            "-s",
            required=True,
            help="Source directory or file to analyze",
        )
        parser.add_argument(
            "--output",
            "-o",
            required=True,
            help="Output directory for generated diagrams",
        )
        parser.add_argument(
            "--class",
            "-c",
            dest="class_name",
            required=True,
            help="Class to generate state diagram for",
        )
        
        args = parser.parse_args()
        
        # Create output directory if it doesn't exist
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create analyzer and analyze the source
        analyzer = StateAnalyzer(args.source)
        
        source_path = Path(args.source)
        if source_path.is_file():
            analyzer.analyze_file(source_path)
        else:
            analyzer.analyze_directory(source_path)
        
        # Generate the diagram
        try:
            diagram = analyzer.generate_state_diagram(args.class_name)
            
            # Create generator and generate the diagram
            generator = PlantUmlStateGenerator()
            
            output_file = output_dir / f"{args.class_name}_state.puml"
            generator.generate_file(diagram, output_file)
            
            print(f"State diagram generated at {output_file}")
            
        except ValueError as e:
            print(f"Error: {e}")
            return 1
        
        return 0
    
    
    if __name__ == "__main__":
        exit(main())

Using the CLI Tool
---------------

To use the CLI tool, run:

.. code-block:: bash

    # Extract a state diagram for a specific class
    python -m utils.extract_state --source ./backend/app --output ./docs/source/_generated_uml/state --class Document

This will:

1. Analyze the Python code in the `./backend/app` directory
2. Extract state patterns from the `Document` class
3. Generate a state diagram in PlantUML format
4. Save the diagram to `./docs/source/_generated_uml/state/Document_state.puml`

Integration with Main UML Generator
--------------------------------

The state diagram extractor is integrated with the main UML generator in ``utils/run_uml_generator.py``:

.. code-block:: python

    # Add import for state extractor
    from utils.state_extractor import StateAnalyzer, PlantUmlStateGenerator
    
    # Add a function to generate state diagrams
    def generate_state_diagrams(base_dir: Path, output_dir: Path) -> None:
        """Generate state diagrams from Python code."""
        print("Generating state diagrams...")
        
        # Define the source directory to analyze
        source_dir = base_dir / "backend" / "app"
        
        # Create the output directory
        state_output_dir = output_dir / "state"
        state_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create analyzer and analyze the source
        analyzer = StateAnalyzer(source_dir)
        analyzer.analyze_directory()
        
        # Define classes to generate diagrams for
        # This could be read from a configuration file
        targets = [
            "Document",
            "Order",
            "User",
            # Add more targets as needed
        ]
        
        # Generate diagrams for each target
        for class_name in targets:
            try:
                diagram = analyzer.generate_state_diagram(class_name)
                
                # Create generator and generate the diagram
                generator = PlantUmlStateGenerator()
                
                output_file = state_output_dir / f"{class_name}_state.puml"
                generator.generate_file(diagram, output_file)
                
                print(f"Generated state diagram for {class_name}")
                
            except ValueError as e:
                print(f"Could not generate state diagram for {class_name}: {e}")
    
    # Update the main function to include state diagram generation
    def main():
        # ... existing code ...
        
        # Generate activity diagrams
        generate_activity_diagrams(base_dir, output_dir)
        
        # Generate state diagrams
        generate_state_diagrams(base_dir, output_dir)
        
        # ... existing code ...

This integration allows state diagrams to be generated automatically when running the main UML generator:

.. code-block:: bash

    python -m utils.run_uml_generator

State Decorators
-------------

To help annotate state patterns in code, the implementation includes state and transition decorators in ``utils/state_decorators.py``:

.. code-block:: python

    """Decorators for defining state machines in Python classes."""
    
    from functools import wraps
    from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union, cast
    
    
    T = TypeVar("T")
    
    
    def state(
        state_name: str,
        *,
        initial: bool = False,
        final: bool = False,
        entry_actions: Optional[List[str]] = None,
        exit_actions: Optional[List[str]] = None,
    ) -> Callable[[T], T]:
        """Decorator to mark a method as a state handler.
        
        Args:
            state_name: Name of the state
            initial: Whether this is the initial state
            final: Whether this is a final state
            entry_actions: Actions to perform when entering this state
            exit_actions: Actions to perform when exiting this state
        
        Returns:
            Decorated method
        """
        
        def decorator(method: T) -> T:
            # Store state information on the method
            setattr(method, "_state_info", {
                "name": state_name,
                "initial": initial,
                "final": final,
                "entry_actions": entry_actions or [],
                "exit_actions": exit_actions or [],
            })
            
            return method
        
        return decorator
    
    
    def transition(
        *,
        source: str,
        target: str,
        event: Optional[str] = None,
        guard: Optional[str] = None,
        action: Optional[str] = None,
    ) -> Callable[[T], T]:
        """Decorator to mark a method as a state transition.
        
        Args:
            source: Source state name
            target: Target state name
            event: Event triggering the transition
            guard: Guard condition for the transition
            action: Action to perform during the transition
        
        Returns:
            Decorated method
        """
        
        def decorator(method: T) -> T:
            # Store transition information on the method
            setattr(method, "_transition_info", {
                "source": source,
                "target": target,
                "event": event,
                "guard": guard,
                "action": action,
            })
            
            @wraps(method)
            def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
                # Check if guard condition is met
                if guard and not eval(f"self.{guard}"):
                    return None
                
                # Execute the transition method
                result = method(self, *args, **kwargs)
                
                # Update the state
                if hasattr(self, "state"):
                    self.state = target
                
                return result
            
            return cast(T, wrapper)
        
        return decorator

Using State Decorators
-------------------

Here's an example of how to use the state decorators to define a state machine:

.. code-block:: python

    from utils.state_decorators import state, transition
    
    class Document:
        def __init__(self):
            self.state = "draft"
            self.content = ""
            self.reviewers = []
        
        @state("draft", initial=True, entry_actions=["create empty document"])
        def handle_draft(self):
            """Handle draft state."""
            # Draft state behavior
            pass
        
        @transition(source="draft", target="review", event="submit")
        def submit_for_review(self):
            """Submit document for review."""
            self.notify_reviewers()
            return True
        
        @state("review", entry_actions=["notify reviewers"])
        def handle_review(self):
            """Handle review state."""
            # Review state behavior
            pass
        
        @transition(source="review", target="draft", event="request_changes")
        def request_changes(self, comments):
            """Request changes to the document."""
            self.add_comments(comments)
            return True
        
        @transition(source="review", target="approved", event="approve", guard="all_reviewers_approved")
        def approve(self):
            """Approve the document."""
            return True
        
        @state("approved", entry_actions=["notify author"])
        def handle_approved(self):
            """Handle approved state."""
            # Approved state behavior
            pass
        
        @transition(source="approved", target="published", event="publish")
        def publish(self):
            """Publish the document."""
            self.generate_public_link()
            return True
        
        @state("published", entry_actions=["update timestamp", "generate public link"])
        def handle_published(self):
            """Handle published state."""
            # Published state behavior
            pass
        
        def all_reviewers_approved(self):
            """Check if all reviewers have approved."""
            return all(reviewer.has_approved for reviewer in self.reviewers)
        
        def notify_reviewers(self):
            """Notify reviewers."""
            pass
        
        def add_comments(self, comments):
            """Add comments to the document."""
            pass
        
        def generate_public_link(self):
            """Generate a public link for the document."""
            pass

The state analyzer can extract this explicit state machine definition and generate a state diagram from it.

Updating Documentation
-------------------

To include state diagrams in the documentation, update the UML diagrams documentation:

.. code-block:: rst

    State Diagrams
    --------------
    
    Document Lifecycle
    ~~~~~~~~~~~~~~~~
    
    .. uml:: ../_generated_uml/state/Document_state.puml
    
    Order Processing
    ~~~~~~~~~~~~~~~
    
    .. uml:: ../_generated_uml/state/Order_state.puml

This will include the generated state diagrams in the documentation.

Complete Usage Example
-------------------

Here's a complete example of how to use the state diagram extractor:

1. **Define a class with state pattern**:

   ```python
   class Order:
       def __init__(self):
           self.state = "new"
           self.items = []
           self.customer = None
       
       def add_item(self, item):
           if self.state == "new":
               self.items.append(item)
               return True
           return False
       
       def submit(self):
           if self.state == "new" and self.items and self.customer:
               self.state = "submitted"
               return True
           return False
       
       def process(self):
           if self.state == "submitted":
               # Process the order
               self.state = "processing"
               return True
           return False
       
       def ship(self):
           if self.state == "processing":
               # Ship the order
               self.state = "shipped"
               return True
           return False
       
       def deliver(self):
           if self.state == "shipped":
               # Mark as delivered
               self.state = "delivered"
               return True
           return False
       
       def cancel(self):
           if self.state in ["new", "submitted", "processing"]:
               self.state = "cancelled"
               return True
           return False
   ```

2. **Extract the state diagram**:

   ```bash
   python -m utils.extract_state --source ./path/to/order.py --output ./docs/source/_generated_uml/state --class Order
   ```

3. **Include in documentation**:

   ```rst
   Order Processing
   ~~~~~~~~~~~~~~~
   
   .. uml:: ../_generated_uml/state/Order_state.puml
   ```

This will generate a state diagram showing the Order class's state machine, with states like "new", "submitted", "processing", "shipped", "delivered", and "cancelled", and transitions between them.