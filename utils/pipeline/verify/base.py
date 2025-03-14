"""
Base verifier module.

This module provides the base verifier interface for output verification.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from utils.pipeline.utils.logging import get_logger


class BaseVerifier(ABC):
    """Base class for output verifiers."""

    def __init__(self):
        self.logger = get_logger(__name__)

    @abstractmethod
    def verify(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Verify output data structure and content.

        Args:
            data: Output data to verify

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        pass
