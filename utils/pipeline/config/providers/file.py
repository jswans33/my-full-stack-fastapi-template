"""
File configuration provider.

This module provides a configuration provider that loads configuration from files.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from utils.pipeline.config.providers.base import ConfigurationProvider


class FileConfigurationProvider(ConfigurationProvider):
    """
    File-based configuration provider.

    Loads configuration from YAML or JSON files.
    """

    def __init__(
        self, base_dirs: List[str], file_extensions: Optional[List[str]] = None
    ):
        """
        Initialize the provider.

        Args:
            base_dirs: List of base directories to search for configuration files
            file_extensions: List of file extensions to consider (default: ['.yaml', '.yml', '.json'])
        """
        self.base_dirs = [Path(d) for d in base_dirs]
        self.file_extensions = file_extensions or [".yaml", ".yml", ".json"]

        # Ensure base directories exist
        for base_dir in self.base_dirs:
            os.makedirs(base_dir, exist_ok=True)

    def _resolve_lookup_paths(self, config_name: str) -> List[Path]:
        """
        Resolve configuration paths, supporting glob patterns.

        Args:
            config_name: Name of the configuration to resolve

        Returns:
            List of resolved paths
        """
        config_path = Path(config_name)
        resolved_paths = []

        # Check if config_name contains glob pattern
        if any(c in config_name for c in "*?[]"):
            # Handle glob pattern
            for base_dir in self.base_dirs:
                try:
                    # Use glob to find matching files
                    pattern_path = base_dir / config_path
                    resolved_paths.extend(
                        Path(p) for p in pattern_path.parent.glob(pattern_path.name)
                    )
                except Exception:
                    continue
        else:
            # Handle regular path
            if config_path.is_absolute():
                if config_path.exists():
                    resolved_paths.append(config_path)
            else:
                # Try each base directory
                for base_dir in self.base_dirs:
                    # Try with provided name
                    candidate = base_dir / config_path
                    if candidate.exists():
                        resolved_paths.append(candidate)
                        continue

                    # Try with extensions if no extension provided
                    if not config_path.suffix:
                        for ext in self.file_extensions:
                            candidate = base_dir / f"{config_name}{ext}"
                            if candidate.exists():
                                resolved_paths.append(candidate)
                                break

        return resolved_paths

    def get_config(self, config_name: str) -> Dict[str, Any]:
        """
        Get configuration by name.

        Args:
            config_name: Name of the configuration to load. Can be a relative path
                         or a full path that includes one of the base directories.
                         Supports glob patterns for loading multiple configurations.

        Returns:
            Configuration dictionary or empty dict if not found
        """
        paths = self._resolve_lookup_paths(config_name)

        if not paths:
            # If no paths found and no extension provided, try default path
            if not Path(config_name).suffix:
                default_path = (
                    self.base_dirs[0] / f"{config_name}{self.file_extensions[0]}"
                )
                paths = [default_path]

        # For glob patterns, merge all matching configurations
        merged_config = {}
        for path in paths:
            if path.exists():
                config_data = self._load_file(path)
                # Use filename without extension as the key for the configuration
                config_key = path.stem
                if config_data:
                    merged_config[config_key] = config_data

        # If not a glob pattern, return the single configuration directly
        if not any(c in config_name for c in "*?[]"):
            return next(iter(merged_config.values())) if merged_config else {}

        return merged_config

    def supports_config(self, config_name: str) -> bool:
        """
        Check if provider supports this configuration.

        Args:
            config_name: Name of the configuration to check. Can be a relative path
                         or a full path that includes one of the base directories.
                         Supports glob patterns.

        Returns:
            True if provider supports this configuration, False otherwise
        """
        paths = self._resolve_lookup_paths(config_name)
        return bool(paths and any(p.exists() for p in paths))

    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """
        Save configuration.

        Args:
            config_name: Name of the configuration to save. Can be a relative path
                         or a full path that includes one of the base directories.
            config_data: Configuration data to save

        Returns:
            True if successful, False otherwise
        """
        paths = self._resolve_lookup_paths(config_name)
        if paths:
            file_path = paths[0]  # Use first matching path
        else:
            # Use default path if no matches found
            file_path = self.base_dirs[0] / f"{config_name}{self.file_extensions[0]}"

        # Ensure directory exists
        os.makedirs(file_path.parent, exist_ok=True)

        try:
            # Save configuration
            self._save_file(file_path, config_data)
            return True
        except Exception as e:
            # Log error
            print(f"Error saving configuration: {str(e)}")
            return False

    def _load_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load configuration from file.

        Args:
            file_path: Path to the configuration file

        Returns:
            Configuration dictionary
        """
        # Open file
        with open(file_path, "r", encoding="utf-8") as f:
            # Check file extension
            if file_path.suffix in [".yaml", ".yml"]:
                # Load YAML
                return yaml.safe_load(f) or {}
            elif file_path.suffix == ".json":
                # Load JSON
                return json.load(f)
            else:
                # Unsupported file extension
                return {}

    def _save_file(self, file_path: Path, config_data: Dict[str, Any]) -> None:
        """
        Save configuration to file.

        Args:
            file_path: Path to the configuration file
            config_data: Configuration data to save
        """
        # Open file
        with open(file_path, "w", encoding="utf-8") as f:
            # Check file extension
            if file_path.suffix in [".yaml", ".yml"]:
                # Save YAML
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
            elif file_path.suffix == ".json":
                # Save JSON
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            else:
                # Unsupported file extension
                raise ValueError(f"Unsupported file extension: {file_path.suffix}")
