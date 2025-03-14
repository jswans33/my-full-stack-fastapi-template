UML State Diagram Models
=====================

This section details the data models used for state diagram extraction. These models define the structure of state diagrams, states, and transitions.

State Diagram Models
------------------

The following models are defined in ``utils/state_extractor/models.py``:

.. code-block:: python

    """Data models for state diagram extraction."""
    
    from dataclasses import dataclass, field
    from enum import Enum
    from typing import Dict, List, Optional, Set
    
    
    class StateType(Enum):
        """Types of states in a state diagram."""
        
        INITIAL = "initial"
        NORMAL = "normal"
        FINAL = "final"
        CHOICE = "choice"
        FORK = "fork"
        JOIN = "join"
        HISTORY = "history"
    
    
    @dataclass
    class State:
        """Represents a state in a state diagram."""
        
        id: str
        name: str
        type: StateType = StateType.NORMAL
        
        # Actions
        entry_actions: List[str] = field(default_factory=list)
        exit_actions: List[str] = field(default_factory=list)
        internal_actions: Dict[str, str] = field(default_factory=dict)
        
        # Method that handles this state
        method_name: Optional[str] = None
        line_number: int = 0
        
        def __hash__(self):
            return hash(self.id)
    
    
    @dataclass
    class Transition:
        """Represents a transition between states."""
        
        source_id: str
        target_id: str
        
        # Transition metadata
        event: Optional[str] = None
        guard: Optional[str] = None
        action: Optional[str] = None
        
        # Method that triggers this transition
        method_name: Optional[str] = None
        line_number: int = 0
        
        def __hash__(self):
            return hash((self.source_id, self.target_id, self.event))
    
    
    @dataclass
    class StateDiagram:
        """Represents a state diagram."""
        
        title: str
        states: Set[State] = field(default_factory=set)
        transitions: Set[Transition] = field(default_factory=set)
        
        # Track the initial state
        initial_state_id: Optional[str] = None
        
        def add_state(self, state: State) -> None:
            """Add a state to the diagram."""
            self.states.add(state)
            
            # If this is the initial state, track it
            if state.type == StateType.INITIAL and self.initial_state_id is None:
                self.initial_state_id = state.id
        
        def add_transition(self, transition: Transition) -> None:
            """Add a transition to the diagram."""
            self.transitions.add(transition)
    
    
    @dataclass
    class StateInfo:
        """Information about a state found in code."""
        
        state_name: str
        state_id: str
        method_name: Optional[str] = None
        entry_actions: List[str] = field(default_factory=list)
        exit_actions: List[str] = field(default_factory=list)
        is_initial: bool = False
        is_final: bool = False
        line_number: int = 0
    
    
    @dataclass
    class TransitionInfo:
        """Information about a transition found in code."""
        
        source_state: str
        target_state: str
        event: Optional[str] = None
        guard: Optional[str] = None
        action: Optional[str] = None
        method_name: Optional[str] = None
        line_number: int = 0

Model Descriptions
----------------

StateType
~~~~~~~~

An enumeration of different types of states in a state diagram:

- **INITIAL**: The starting state of the state machine
- **NORMAL**: A regular state
- **FINAL**: An end state of the state machine
- **CHOICE**: A decision point
- **FORK**: A point where flow splits into parallel paths
- **JOIN**: A point where parallel paths converge
- **HISTORY**: A history state that remembers the last active substate

State
~~~~~

Represents a state in a state diagram:

- **id**: Unique identifier for the state
- **name**: Display name of the state
- **type**: Type of state (from StateType enum)
- **entry_actions**: Actions performed when entering the state
- **exit_actions**: Actions performed when exiting the state
- **internal_actions**: Internal actions that don't cause state transitions
- **method_name**: Name of the method that handles this state
- **line_number**: Line number in the source code

Transition
~~~~~~~~~

Represents a transition between states:

- **source_id**: ID of the source state
- **target_id**: ID of the target state
- **event**: Event that triggers the transition
- **guard**: Condition that must be true for the transition to occur
- **action**: Action performed during the transition
- **method_name**: Name of the method that triggers this transition
- **line_number**: Line number in the source code

StateDiagram
~~~~~~~~~~~

The main container for a state diagram:

- **title**: Title of the diagram
- **states**: Set of states in the diagram
- **transitions**: Set of transitions between states
- **initial_state_id**: ID of the initial state
- **add_state()**: Method to add a state to the diagram
- **add_transition()**: Method to add a transition to the diagram

StateInfo and TransitionInfo
~~~~~~~~~~~~~~~~~~~~~~~~~~

Helper classes used during the extraction process:

- **StateInfo**: Information about a state found in code
- **TransitionInfo**: Information about a transition found in code

These classes store intermediate information during the analysis phase before creating the final State and Transition objects.

Usage Example
-----------

Here's an example of how to create a state diagram model programmatically:

.. code-block:: python

    from utils.state_extractor.models import State, StateType, StateDiagram, Transition

    # Create a state diagram
    diagram = StateDiagram(title="Document Lifecycle")

    # Create states
    draft_state = State(id="state_0", name="draft", type=StateType.INITIAL)
    review_state = State(id="state_1", name="review")
    approved_state = State(id="state_2", name="approved")
    published_state = State(id="state_3", name="published", type=StateType.FINAL)

    # Add states to diagram
    diagram.add_state(draft_state)
    diagram.add_state(review_state)
    diagram.add_state(approved_state)
    diagram.add_state(published_state)

    # Create transitions
    submit_transition = Transition(
        source_id=draft_state.id,
        target_id=review_state.id,
        event="submit"
    )
    
    approve_transition = Transition(
        source_id=review_state.id,
        target_id=approved_state.id,
        event="approve"
    )
    
    publish_transition = Transition(
        source_id=approved_state.id,
        target_id=published_state.id,
        event="publish"
    )

    # Add transitions to diagram
    diagram.add_transition(submit_transition)
    diagram.add_transition(approve_transition)
    diagram.add_transition(publish_transition)

This creates a state diagram model that can then be converted to PlantUML using the state diagram generator.