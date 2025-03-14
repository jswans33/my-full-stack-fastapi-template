"""
Configuration module for the pipeline.

This module provides functions for loading and managing configuration settings.
"""

from .config import PipelineConfig, load_config

__all__ = ["load_config", "PipelineConfig"]
