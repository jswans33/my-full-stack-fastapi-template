"""Configuration loader for UML Generator.

This module handles loading and merging configuration from multiple sources:
1. Command line arguments (highest priority)
2. Environment variables (UML_GENERATOR_*)
3. User config file (~/.config/uml-generator/config.toml)
4. Project config file (.uml-generator.toml)
5. Default config file (lowest priority)
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomli


@dataclass
class GeneratorConfig:
    """PlantUML generator configuration."""

    format: str = "plantuml"
    plantuml_start: str = "@startuml"
    plantuml_end: str = "@enduml"
    plantuml_settings: list[str] = field(
        default_factory=lambda: [
            "skinparam classAttributeIconSize 0",
        ]
    )


@dataclass
class ParserConfig:
    """Parser configuration."""

    patterns: list[str] = field(default_factory=lambda: ["*.py"])
    exclude_dirs: list[str] = field(
        default_factory=lambda: [
            "__pycache__",
            "*.egg-info",
            "build",
            "dist",
        ]
    )
    show_imports: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "info"
    file: str | None = None


@dataclass
class Config:
    """Complete UML generator configuration."""

    output_dir: Path = Path("docs/source/_generated_uml")
    generator: GeneratorConfig = field(default_factory=GeneratorConfig)
    parser: ParserConfig = field(default_factory=ParserConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


class ConfigLoader:
    """Configuration loader handling multiple sources."""

    def __init__(self):
        self.config = Config()
        self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default configuration."""
        default_config = Path(__file__).parent / "defaults.toml"
        if default_config.exists():
            self._load_toml(default_config)

    def _load_toml(self, path: Path) -> None:
        """Load configuration from TOML file."""
        try:
            with open(path, "rb") as f:
                data = tomli.load(f)
                self._update_config(data)
        except Exception as e:
            print(f"Warning: Failed to load config from {path}: {e}")

    def _load_env_vars(self) -> None:
        """Load configuration from environment variables."""
        prefix = "UML_GENERATOR_"
        env_map = {
            "OUTPUT_DIR": ("output_dir", str),
            "FORMAT": ("generator.format", str),
            "SHOW_IMPORTS": ("parser.show_imports", bool),
            "LOG_LEVEL": ("logging.level", str),
            "LOG_FILE": ("logging.file", str),
        }

        for env_key, (config_key, type_) in env_map.items():
            full_key = prefix + env_key
            if full_key in os.environ:
                value = os.environ[full_key]
                if type_ == bool:
                    value = value.lower() in ("true", "1", "yes")
                self._set_nested_value(config_key.split("."), value)

    def _set_nested_value(self, keys: list[str], value: Any) -> None:
        """Set a nested configuration value."""
        target = self.config
        for key in keys[:-1]:
            target = getattr(target, key)
        setattr(target, keys[-1], value)

    def _update_config(self, data: dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        if "paths" in data:
            if "output_dir" in data["paths"]:
                self.config.output_dir = Path(data["paths"]["output_dir"])

        if "generator" in data:
            gen_data = data["generator"]
            if "format" in gen_data:
                self.config.generator.format = gen_data["format"]
            if "plantuml" in gen_data:
                plantuml = gen_data["plantuml"]
                if "start" in plantuml:
                    self.config.generator.plantuml_start = plantuml["start"]
                if "end" in plantuml:
                    self.config.generator.plantuml_end = plantuml["end"]
                if "settings" in plantuml:
                    self.config.generator.plantuml_settings = plantuml["settings"]

        if "parser" in data:
            parser_data = data["parser"]
            if "patterns" in parser_data:
                self.config.parser.patterns = parser_data["patterns"]
            if "exclude_dirs" in parser_data:
                self.config.parser.exclude_dirs = parser_data["exclude_dirs"]
            if "show_imports" in parser_data:
                self.config.parser.show_imports = parser_data["show_imports"]

        if "logging" in data:
            log_data = data["logging"]
            if "level" in log_data:
                self.config.logging.level = log_data["level"]
            if "file" in log_data:
                self.config.logging.file = log_data["file"]

    def load(self, cli_args: dict[str, Any] | None = None) -> Config:
        """Load configuration from all sources."""
        # Load project config if exists
        project_config = Path(".uml-generator.toml")
        if project_config.exists():
            self._load_toml(project_config)

        # Load user config if exists
        user_config = Path.home() / ".config" / "uml-generator" / "config.toml"
        if user_config.exists():
            self._load_toml(user_config)

        # Load environment variables
        self._load_env_vars()

        # Apply CLI arguments (highest priority)
        if cli_args:
            self._update_config(cli_args)

        return self.config


def load_config(cli_args: dict[str, Any] | None = None) -> Config:
    """Load configuration from all sources."""
    loader = ConfigLoader()
    return loader.load(cli_args)
