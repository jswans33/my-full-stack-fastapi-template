from typing import Dict, Any, List, Union

class PipelineData:
    """Base data model for pipeline data"""
    def __init__(self, data: Dict[str, Any] = None):
        self.data = data or {}
