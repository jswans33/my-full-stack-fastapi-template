"""Models for state diagrams.

This module provides models for representing state diagrams.
"""

from utils.uml.diagrams.base import BaseDiagramModel


class StateDiagram(BaseDiagramModel):
    """Model for a state diagram."""

    def __init__(self, name: str):
        """Initialize a state diagram.

        Args:
            name: The name of the diagram
        """
        super().__init__(name, "state")
        self.states: list[StateModel] = []
        self.transitions: list[TransitionModel] = []
        self.start_states: list[StartStateModel] = []
        self.end_states: list[EndStateModel] = []
        self.composite_states: list[CompositeStateModel] = []

    def add_state(self, state: "StateModel") -> None:
        """Add a state to the diagram.

        Args:
            state: The state to add
        """
        self.states.append(state)

    def add_transition(self, transition: "TransitionModel") -> None:
        """Add a transition to the diagram.

        Args:
            transition: The transition to add
        """
        self.transitions.append(transition)

    def add_start_state(self, start_state: "StartStateModel") -> None:
        """Add a start state to the diagram.

        Args:
            start_state: The start state to add
        """
        self.start_states.append(start_state)

    def add_end_state(self, end_state: "EndStateModel") -> None:
        """Add an end state to the diagram.

        Args:
            end_state: The end state to add
        """
        self.end_states.append(end_state)

    def add_composite_state(self, composite_state: "CompositeStateModel") -> None:
        """Add a composite state to the diagram.

        Args:
            composite_state: The composite state to add
        """
        self.composite_states.append(composite_state)


class StateModel:
    """Model for a state."""

    def __init__(
        self, id: str, name: str | None = None, description: str | None = None
    ):
        """Initialize a state.

        Args:
            id: The unique identifier for the state
            name: The name of the state
            description: The description of the state
        """
        self.id = id
        self.name = name or id
        self.description = description
        self.entry_actions: list[str] = []
        self.exit_actions: list[str] = []
        self.internal_actions: list[str] = []

    def add_entry_action(self, action: str) -> None:
        """Add an entry action to the state.

        Args:
            action: The entry action to add
        """
        self.entry_actions.append(action)

    def add_exit_action(self, action: str) -> None:
        """Add an exit action to the state.

        Args:
            action: The exit action to add
        """
        self.exit_actions.append(action)

    def add_internal_action(self, action: str) -> None:
        """Add an internal action to the state.

        Args:
            action: The internal action to add
        """
        self.internal_actions.append(action)


class TransitionModel:
    """Model for a transition between states."""

    def __init__(
        self,
        source_id: str,
        target_id: str,
        event: str | None = None,
        guard: str | None = None,
        action: str | None = None,
    ):
        """Initialize a transition.

        Args:
            source_id: The ID of the source state
            target_id: The ID of the target state
            event: The event that triggers the transition
            guard: The guard condition for the transition
            action: The action performed during the transition
        """
        self.source_id = source_id
        self.target_id = target_id
        self.event = event
        self.guard = guard
        self.action = action


class StartStateModel:
    """Model for a start state."""

    def __init__(self, id: str):
        """Initialize a start state.

        Args:
            id: The unique identifier for the state
        """
        self.id = id


class EndStateModel:
    """Model for an end state."""

    def __init__(self, id: str):
        """Initialize an end state.

        Args:
            id: The unique identifier for the state
        """
        self.id = id


class CompositeStateModel(StateModel):
    """Model for a composite state."""

    def __init__(
        self,
        id: str,
        name: str | None = None,
        description: str | None = None,
    ):
        """Initialize a composite state.

        Args:
            id: The unique identifier for the state
            name: The name of the state
            description: The description of the state
        """
        super().__init__(id, name, description)
        self.substates: list[StateModel] = []
        self.internal_transitions: list[TransitionModel] = []
        self.internal_start_states: list[StartStateModel] = []
        self.internal_end_states: list[EndStateModel] = []

    def add_substate(self, state: StateModel) -> None:
        """Add a substate to the composite state.

        Args:
            state: The substate to add
        """
        self.substates.append(state)

    def add_internal_transition(self, transition: TransitionModel) -> None:
        """Add an internal transition to the composite state.

        Args:
            transition: The internal transition to add
        """
        self.internal_transitions.append(transition)

    def add_internal_start_state(self, start_state: StartStateModel) -> None:
        """Add an internal start state to the composite state.

        Args:
            start_state: The internal start state to add
        """
        self.internal_start_states.append(start_state)

    def add_internal_end_state(self, end_state: EndStateModel) -> None:
        """Add an internal end state to the composite state.

        Args:
            end_state: The internal end state to add
        """
        self.internal_end_states.append(end_state)
