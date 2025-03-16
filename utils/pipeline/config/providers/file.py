"""
File configuration provider.

This module provides a configuration provider that loads configuration from files.
"""

import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

from utils.pipeline.config.providers.base import ConfigurationProvider
from utils.pipeline.config.providers.file_watcher import FileSystemWatcher


class FileConfigurationProvider(ConfigurationProvider):
    """
    File-based configuration provider.

    Loads configuration from YAML or JSON files.
    """

    def __init__(
        self,
        base_dirs: List[str],
        file_extensions: Optional[List[str]] = None,
        enable_hot_reload: bool = False,
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

        # Initialize file watcher
        self.enable_hot_reload = enable_hot_reload
        self.file_watcher = FileSystemWatcher() if enable_hot_reload else None
        self.change_callbacks: List[Callable[[str], None]] = []

    def start_watching(self) -> None:
        """Start watching for configuration file changes."""
        if self.enable_hot_reload and self.file_watcher:
            self.file_watcher.start(self._on_file_changed)

    def stop_watching(self) -> None:
        """Stop watching for configuration file changes."""
        if self.file_watcher:
            self.file_watcher.stop()

    def register_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Register a callback for configuration changes.

        Args:
            callback: Function to call when a configuration changes
        """
        self.change_callbacks.append(callback)

    def _on_file_changed(self, file_path: str) -> None:
        """
        Handle configuration file changes.

        Args:
            file_path: Path to the changed file
        """
        # Get config name from file path
        config_name = str(Path(file_path).relative_to(self.base_dirs[0]))

        # Notify callbacks
        for callback in self.change_callbacks:
            try:
                callback(config_name)
            except Exception as e:
                print(f"Error in configuration change callback: {str(e)}")

    def _resolve_lookup_path(self, config_name: str) -> Optional[Path]:
        """
        Resolve configuration path.

        Args:
            config_name: Name of the configuration to resolve

        Returns:
            Resolved path if found, None otherwise
        """
        config_path = Path(config_name)

        # If already absolute or includes base_dir
        if config_path.is_absolute():
            return config_path if config_path.exists() else None

        # Try each base_dir and extension combination
        for base_dir in self.base_dirs:
            base_dir = Path(base_dir)
            # Try with provided name
            candidate = base_dir / config_path
            if candidate.exists():
                return candidate

            # Try with extensions if no extension provided
            if not config_path.suffix:
                for ext in self.file_extensions:
                    candidate = base_dir / f"{config_name}{ext}"
                    if candidate.exists():
                        return candidate

        return None

    def get_config(self, config_name: str) -> Dict[str, Any]:
        """
        Get configuration by name.

        Args:
            config_name: Name of the configuration to load

        Returns:
            Configuration dictionary or empty dict if not found
        """
        # Handle glob patterns
        if any(c in config_name for c in "*?[]"):
            merged_config = {}
            for base_dir in self.base_dirs:
                base_dir = Path(base_dir)
                try:
                    # Split path into directory and pattern
                    config_path = Path(config_name.replace("/", os.sep))
                    search_dir = base_dir / config_path.parent
                    pattern = config_path.name

                    # Search for files matching pattern
                    if search_dir.exists():
                        print(f"Searching in {search_dir} for {pattern}")
                        for path in search_dir.glob(pattern):
                            print(f"Found file: {path}")
                            if path.is_file():
                                config_data = self._load_file(path)
                                if config_data:
                                    print(f"Loaded config: {config_data}")
                                    merged_config[path.stem] = config_data
                except Exception as e:
                    print(f"Error searching for {config_name} in {base_dir}: {e}")
                    continue
            return merged_config

        # Handle single file
        file_path = self._resolve_lookup_path(config_name)
        if file_path and file_path.exists():
            # Add file to watcher if hot reload is enabled
            if self.enable_hot_reload and self.file_watcher:
                self.file_watcher.watch_file(str(file_path))
            return self._load_file(file_path) or {}

        return {}

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
        file_path = self._resolve_lookup_path(config_name)
        return file_path is not None and file_path.exists()

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
        file_path = self._resolve_lookup_path(config_name)
        if not file_path:
            # Use default path if no matches found
            file_path = self.base_dirs[0] / f"{config_name}{self.file_extensions[0]}"
            # Add new file to watcher if hot reload is enabled
            if self.enable_hot_reload and self.file_watcher:
                self.file_watcher.watch_file(str(file_path))

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
