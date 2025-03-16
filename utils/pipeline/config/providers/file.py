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

    def get_config(self, config_name: str) -> Dict[str, Any]:
        """
        Get configuration by name.

        Args:
            config_name: Name of the configuration to load

        Returns:
            Configuration dictionary or empty dict if not found
        """
        # Try each base directory
        for base_dir in self.base_dirs:
            # Try each file extension
            for ext in self.file_extensions:
                # Construct file path
                file_path = base_dir / f"{config_name}{ext}"

                # Check if file exists
                if file_path.exists():
                    return self._load_file(file_path)

        # Configuration not found
        return {}

    def supports_config(self, config_name: str) -> bool:
        """
        Check if provider supports this configuration.

        Args:
            config_name: Name of the configuration to check

        Returns:
            True if provider supports this configuration, False otherwise
        """
        # Try each base directory
        for base_dir in self.base_dirs:
            # Try each file extension
            for ext in self.file_extensions:
                # Construct file path
                file_path = base_dir / f"{config_name}{ext}"

                # Check if file exists
                if file_path.exists():
                    return True

        # Configuration not found
        return False

    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """
        Save configuration.

        Args:
            config_name: Name of the configuration to save
            config_data: Configuration data to save

        Returns:
            True if successful, False otherwise
        """
        # Use the first base directory for saving
        base_dir = self.base_dirs[0]

        # Use the first file extension for saving
        ext = self.file_extensions[0]

        # Construct file path
        file_path = base_dir / f"{config_name}{ext}"

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
