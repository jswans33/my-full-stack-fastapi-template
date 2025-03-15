"""
Formatter factory implementation.

This module provides a factory for creating different output formatters.
"""

from enum import Enum, auto
from typing import Any, Dict, Optional, Type

from utils.pipeline.processors.formatters.enhanced_markdown_formatter import (
    EnhancedMarkdownFormatter,
)
from utils.pipeline.processors.formatters.json_formatter import JSONFormatter
from utils.pipeline.processors.formatters.markdown_formatter import MarkdownFormatter
from utils.pipeline.strategies.formatter import FormatterStrategy
from utils.pipeline.utils.logging import get_logger


class OutputFormat(Enum):
    """Supported output formats."""

    JSON = auto()
    MARKDOWN = auto()
    ENHANCED_MARKDOWN = auto()


class FormatterFactory:
    """Factory for creating formatter instances."""

    _formatters: Dict[OutputFormat, Type[FormatterStrategy]] = {
        OutputFormat.JSON: JSONFormatter,
        OutputFormat.MARKDOWN: MarkdownFormatter,
        OutputFormat.ENHANCED_MARKDOWN: EnhancedMarkdownFormatter,
    }

    @classmethod
    def create_formatter(
        cls, format_type: OutputFormat, config: Optional[Dict[str, Any]] = None
    ) -> FormatterStrategy:
        """
        Create a formatter instance for the specified format.

        Args:
            format_type: Type of formatter to create
            config: Optional configuration dictionary for the formatter

        Returns:
            Formatter instance

        Raises:
            ValueError: If format type is not supported
        """
        logger = get_logger(__name__)

        try:
            formatter_class = cls._formatters[format_type]

            # Pass config to formatters that accept it
            if formatter_class == EnhancedMarkdownFormatter and config is not None:
                return formatter_class(config)
            else:
                return formatter_class()

        except KeyError:
            logger.error(f"Unsupported format type: {format_type}")
            raise ValueError(f"Unsupported format type: {format_type}")

    @classmethod
    def register_formatter(
        cls, format_type: OutputFormat, formatter_class: Type[FormatterStrategy]
    ) -> None:
        """
        Register a new formatter type.

        Args:
            format_type: Format type to register
            formatter_class: Formatter class to use for this format
        """
        logger = get_logger(__name__)
        logger.info(
            f"Registering formatter for {format_type}: {formatter_class.__name__}"
        )
        cls._formatters[format_type] = formatter_class
