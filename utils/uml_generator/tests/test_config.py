"""Tests for configuration loading."""

import os
import tempfile
from pathlib import Path

import pytest

from ..config.loader import Config, ConfigLoader, load_config


@pytest.fixture
def temp_config_file():
    """Create a temporary config file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("""
[paths]
output_dir = "custom/output"

[generator]
format = "plantuml"

[generator.plantuml]
settings = [
    "skinparam monochrome true",
    "skinparam shadowing false"
]

[parser]
show_imports = true
patterns = ["*.py", "*.pyi"]
""")
        f.flush()
        yield Path(f.name)
        os.unlink(f.name)


def test_default_config():
    """Test default configuration values."""
    config = Config()
    assert config.output_dir == Path("docs/source/_generated_uml")
    assert config.generator.format == "plantuml"
    assert not config.parser.show_imports
    assert config.logging.level == "info"


def test_load_toml_config(temp_config_file):
    """Test loading configuration from TOML file."""
    loader = ConfigLoader()
    loader._load_toml(temp_config_file)
    config = loader.config

    assert config.output_dir == Path("custom/output")
    assert config.generator.format == "plantuml"
    assert config.parser.show_imports is True
    assert "*.pyi" in config.parser.patterns


def test_load_env_vars():
    """Test loading configuration from environment variables."""
    os.environ["UML_GENERATOR_OUTPUT_DIR"] = "env/output"
    os.environ["UML_GENERATOR_SHOW_IMPORTS"] = "true"
    os.environ["UML_GENERATOR_LOG_LEVEL"] = "debug"

    try:
        config = load_config()
        assert config.output_dir == Path("env/output")
        assert config.parser.show_imports is True
        assert config.logging.level == "debug"
    finally:
        # Clean up environment
        del os.environ["UML_GENERATOR_OUTPUT_DIR"]
        del os.environ["UML_GENERATOR_SHOW_IMPORTS"]
        del os.environ["UML_GENERATOR_LOG_LEVEL"]


def test_cli_args_override():
    """Test CLI arguments override other sources."""
    os.environ["UML_GENERATOR_OUTPUT_DIR"] = "env/output"

    cli_args = {
        "paths": {"output_dir": "cli/output"},
        "parser": {"show_imports": True},
    }

    try:
        config = load_config(cli_args)
        assert config.output_dir == Path("cli/output")  # CLI args take precedence
        assert config.parser.show_imports is True
    finally:
        del os.environ["UML_GENERATOR_OUTPUT_DIR"]


def test_config_precedence(temp_config_file):
    """Test configuration source precedence."""
    # Set up environment variables
    os.environ["UML_GENERATOR_OUTPUT_DIR"] = "env/output"
    os.environ["UML_GENERATOR_FORMAT"] = "env_format"

    # Set up CLI arguments
    cli_args = {
        "paths": {"output_dir": "cli/output"},
    }

    try:
        # Create loader and load config file
        loader = ConfigLoader()
        loader._load_toml(temp_config_file)

        # Load environment variables and CLI args
        config = loader.load(cli_args)

        # CLI args should take precedence over env vars and file
        assert config.output_dir == Path("cli/output")

        # Env vars should take precedence over file
        assert config.generator.format == "env_format"

        # File values should be loaded
        assert config.parser.show_imports is True
        assert "*.pyi" in config.parser.patterns
    finally:
        del os.environ["UML_GENERATOR_OUTPUT_DIR"]
        del os.environ["UML_GENERATOR_FORMAT"]


def test_invalid_config_file():
    """Test handling of invalid configuration file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("invalid toml content")
        f.flush()

        loader = ConfigLoader()
        loader._load_toml(Path(f.name))

        # Should fall back to defaults
        assert loader.config.output_dir == Path("docs/source/_generated_uml")
        assert loader.config.generator.format == "plantuml"

        os.unlink(f.name)


def test_missing_config_file():
    """Test handling of missing configuration file."""
    loader = ConfigLoader()
    loader._load_toml(Path("nonexistent.toml"))

    # Should use defaults
    assert loader.config.output_dir == Path("docs/source/_generated_uml")
    assert loader.config.generator.format == "plantuml"


def test_boolean_env_vars():
    """Test parsing of boolean environment variables."""
    test_values = [
        ("true", True),
        ("True", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("False", False),
        ("0", False),
        ("no", False),
    ]

    for value, expected in test_values:
        os.environ["UML_GENERATOR_SHOW_IMPORTS"] = value
        try:
            config = load_config()
            assert config.parser.show_imports is expected
        finally:
            del os.environ["UML_GENERATOR_SHOW_IMPORTS"]
