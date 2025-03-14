"""
Configuration module for the pipeline.

This module provides functions for loading and managing configuration settings.
"""

from .config import DEFAULT_CONFIG, load_config

__all__ = ["load_config", "DEFAULT_CONFIG"]
