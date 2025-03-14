"""
Verifier factory implementation.

This module provides a factory for creating different output verifiers.
"""

from enum import Enum, auto
from typing import Dict, Type

from utils.pipeline.utils.logging import get_logger
from utils.pipeline.verify.base import BaseVerifier
from utils.pipeline.verify.json_tree import JSONTreeVerifier
from utils.pipeline.verify.markdown import MarkdownVerifier


class VerifierType(Enum):
    """Supported verifier types."""

    JSON_TREE = auto()
    MARKDOWN = auto()  # Future implementation


class VerifierFactory:
    """Factory for creating verifier instances."""

    _verifiers: Dict[VerifierType, Type[BaseVerifier]] = {
        VerifierType.JSON_TREE: JSONTreeVerifier,
        VerifierType.MARKDOWN: MarkdownVerifier,
    }

    @classmethod
    def create_verifier(cls, verifier_type: VerifierType) -> BaseVerifier:
        """
        Create a verifier instance for the specified type.

        Args:
            verifier_type: Type of verifier to create

        Returns:
            Verifier instance

        Raises:
            ValueError: If verifier type is not supported
        """
        logger = get_logger(__name__)

        try:
            verifier_class = cls._verifiers[verifier_type]
            return verifier_class()
        except KeyError:
            logger.error(f"Unsupported verifier type: {verifier_type}")
            raise ValueError(f"Unsupported verifier type: {verifier_type}")

    @classmethod
    def register_verifier(
        cls, verifier_type: VerifierType, verifier_class: Type[BaseVerifier]
    ) -> None:
        """
        Register a new verifier type.

        Args:
            verifier_type: Verifier type to register
            verifier_class: Verifier class to use for this type
        """
        logger = get_logger(__name__)
        logger.info(
            f"Registering verifier for {verifier_type}: {verifier_class.__name__}"
        )
        cls._verifiers[verifier_type] = verifier_class
