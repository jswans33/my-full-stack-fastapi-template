"""Models for activity diagrams.

This module provides models for representing activity diagrams.
"""

from utils.uml.diagrams.base import BaseDiagramModel


class ActivityDiagram(BaseDiagramModel):
    """Model for an activity diagram."""

    def __init__(self, name: str):
        """Initialize an activity diagram.

        Args:
            name: The name of the diagram
        """
        super().__init__(name, "activity")
        self.activities: list[ActivityModel] = []
        self.transitions: list[TransitionModel] = []
        self.start_nodes: list[StartNodeModel] = []
        self.end_nodes: list[EndNodeModel] = []
        self.decision_nodes: list[DecisionNodeModel] = []
        self.merge_nodes: list[MergeNodeModel] = []
        self.fork_nodes: list[ForkNodeModel] = []
        self.join_nodes: list[JoinNodeModel] = []

    def add_activity(self, activity: "ActivityModel") -> None:
        """Add an activity to the diagram.

        Args:
            activity: The activity to add
        """
        self.activities.append(activity)

    def add_transition(self, transition: "TransitionModel") -> None:
        """Add a transition to the diagram.

        Args:
            transition: The transition to add
        """
        self.transitions.append(transition)

    def add_start_node(self, start_node: "StartNodeModel") -> None:
        """Add a start node to the diagram.

        Args:
            start_node: The start node to add
        """
        self.start_nodes.append(start_node)

    def add_end_node(self, end_node: "EndNodeModel") -> None:
        """Add an end node to the diagram.

        Args:
            end_node: The end node to add
        """
        self.end_nodes.append(end_node)

    def add_decision_node(self, decision_node: "DecisionNodeModel") -> None:
        """Add a decision node to the diagram.

        Args:
            decision_node: The decision node to add
        """
        self.decision_nodes.append(decision_node)

    def add_merge_node(self, merge_node: "MergeNodeModel") -> None:
        """Add a merge node to the diagram.

        Args:
            merge_node: The merge node to add
        """
        self.merge_nodes.append(merge_node)

    def add_fork_node(self, fork_node: "ForkNodeModel") -> None:
        """Add a fork node to the diagram.

        Args:
            fork_node: The fork node to add
        """
        self.fork_nodes.append(fork_node)

    def add_join_node(self, join_node: "JoinNodeModel") -> None:
        """Add a join node to the diagram.

        Args:
            join_node: The join node to add
        """
        self.join_nodes.append(join_node)


class ActivityNodeModel:
    """Base model for an activity node."""

    def __init__(self, id: str, name: str | None = None):
        """Initialize an activity node.

        Args:
            id: The unique identifier for the node
            name: The name of the node
        """
        self.id = id
        self.name = name or id


class ActivityModel(ActivityNodeModel):
    """Model for an activity."""

    def __init__(
        self, id: str, name: str | None = None, description: str | None = None
    ):
        """Initialize an activity.

        Args:
            id: The unique identifier for the activity
            name: The name of the activity
            description: The description of the activity
        """
        super().__init__(id, name)
        self.description = description


class TransitionModel:
    """Model for a transition between activity nodes."""

    def __init__(
        self,
        source_id: str,
        target_id: str,
        guard: str | None = None,
        label: str | None = None,
    ):
        """Initialize a transition.

        Args:
            source_id: The ID of the source node
            target_id: The ID of the target node
            guard: The guard condition for the transition
            label: The label for the transition
        """
        self.source_id = source_id
        self.target_id = target_id
        self.guard = guard
        self.label = label


class StartNodeModel(ActivityNodeModel):
    """Model for a start node."""

    def __init__(self, id: str):
        """Initialize a start node.

        Args:
            id: The unique identifier for the node
        """
        super().__init__(id, "start")


class EndNodeModel(ActivityNodeModel):
    """Model for an end node."""

    def __init__(self, id: str):
        """Initialize an end node.

        Args:
            id: The unique identifier for the node
        """
        super().__init__(id, "end")


class DecisionNodeModel(ActivityNodeModel):
    """Model for a decision node."""

    def __init__(self, id: str, name: str | None = None):
        """Initialize a decision node.

        Args:
            id: The unique identifier for the node
            name: The name of the node
        """
        super().__init__(id, name or "decision")


class MergeNodeModel(ActivityNodeModel):
    """Model for a merge node."""

    def __init__(self, id: str, name: str | None = None):
        """Initialize a merge node.

        Args:
            id: The unique identifier for the node
            name: The name of the node
        """
        super().__init__(id, name or "merge")


class ForkNodeModel(ActivityNodeModel):
    """Model for a fork node."""

    def __init__(self, id: str, name: str | None = None):
        """Initialize a fork node.

        Args:
            id: The unique identifier for the node
            name: The name of the node
        """
        super().__init__(id, name or "fork")


class JoinNodeModel(ActivityNodeModel):
    """Model for a join node."""

    def __init__(self, id: str, name: str | None = None):
        """Initialize a join node.

        Args:
            id: The unique identifier for the node
            name: The name of the node
        """
        super().__init__(id, name or "join")
