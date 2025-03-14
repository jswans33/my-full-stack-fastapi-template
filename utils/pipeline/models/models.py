from typing import Any, Dict, Optional


class PipelineData:
    """Base data model for pipeline data."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """
        Initialize pipeline data.

        Args:
            data: Optional dictionary of data. If None, an empty dict is used.
        """
        self.data = data.copy() if data is not None else {}
