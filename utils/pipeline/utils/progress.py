"""
Progress tracking utilities using Rich.

This module provides rich terminal output for pipeline progress.
"""

from typing import Any, Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.tree import Tree

console = Console()


class PipelineProgress:
    """Rich progress tracking for pipeline operations."""

    def __init__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=True,  # Hide completed tasks
            expand=True,
        )

    def __enter__(self):
        self.progress.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.__exit__(exc_type, exc_val, exc_tb)

    def start(self):
        """Start progress tracking."""
        self.progress.start()

    def stop(self):
        """Stop progress tracking."""
        self.progress.stop()

    def add_task(self, description: str, total: Optional[float] = None) -> TaskID:
        """Add a new task to track."""
        return self.progress.add_task(description, total=total)

    def update(self, task_id: TaskID, advance: float = 1):
        """Update task progress."""
        self.progress.update(task_id, advance=advance)

    def _create_tree_view(self, data: Dict[str, Any], title: str) -> Tree:
        """Create a tree view of nested data."""
        tree = Tree(f"[bold blue]{title}")

        def add_nodes(parent, content, depth=0, max_depth=2):
            if depth >= max_depth:
                return

            if isinstance(content, dict):
                for key, value in content.items():
                    # Skip content display
                    if key == "content":
                        parent.add(f"[cyan]{key}: [dim](content hidden)")
                        continue

                    if isinstance(value, (dict, list)):
                        branch = parent.add(f"[cyan]{key}")
                        add_nodes(branch, value, depth + 1, max_depth)
                    else:
                        # Truncate long values
                        str_value = str(value)
                        if len(str_value) > 30:
                            str_value = str_value[:27] + "..."
                        parent.add(f"[green]{key}: [yellow]{str_value}")
            elif isinstance(content, list):
                if not content:
                    parent.add("[dim]<empty>")
                else:
                    parent.add(f"[dim]{len(content)} items")

        add_nodes(tree, data)
        return tree

    def _update_display(self, content: Any) -> None:
        """Update display with new content."""
        console.print(content)

    def display_stage_output(
        self, stage_name: str, data: Dict[str, Any], show_details: bool = False
    ):
        """Display stage output in a concise tree view."""
        if show_details:
            self._update_display(
                Panel(
                    self._create_tree_view(data, stage_name),
                    title=f"[bold]{stage_name} Output",
                    border_style="blue",
                )
            )

    def display_summary(self, stages_data: Dict[str, Dict[str, Any]]):
        """Display final summary of all stages."""
        summary_tree = Tree("[bold blue]Pipeline Summary")
        for stage, data in stages_data.items():
            stage_branch = summary_tree.add(f"[cyan]{stage}")
            if isinstance(data, dict):
                # Show key statistics or counts
                stats = {
                    k: v
                    for k, v in data.items()
                    if isinstance(v, (int, float, str))
                    or (isinstance(v, (list, dict)) and len(v) > 0)
                }
                for key, value in stats.items():
                    if isinstance(value, (list, dict)):
                        stage_branch.add(f"[green]{key}: [yellow]{len(value)} items")
                    else:
                        stage_branch.add(f"[green]{key}: [yellow]{value}")

        self._update_display(
            Panel(
                summary_tree,
                title="[bold]Pipeline Execution Summary",
                border_style="green",
            )
        )

    def display_error(self, message: str):
        """Display error message."""
        self._update_display(
            Panel(f"[red]{message}", title="Error", border_style="red")
        )

    def display_warning(self, message: str):
        """Display warning message."""
        self._update_display(
            Panel(f"[yellow]{message}", title="Warning", border_style="yellow")
        )

    def display_success(self, message: str):
        """Display success message."""
        self._update_display(
            Panel(f"[green]{message}", title="Success", border_style="green")
        )
