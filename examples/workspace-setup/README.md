# Ruff Setup Guide

This guide explains how to use Ruff as the primary formatter and linter in your development environment.

## What is Ruff?

[Ruff](https://github.com/astral-sh/ruff) is an extremely fast Python linter and formatter, written in Rust. It aims to replace multiple Python tools including:

- Black (formatting)
- isort (import sorting)
- Flake8 and its plugins (linting)
- pyupgrade (automatic Python upgrades)
- autopep8 (PEP 8 compliance)
- And many more

## Setup Overview

This project has been configured to use Ruff for all Python code formatting and linting. The setup includes:

1. **Global Configuration** in `backend/pyproject.toml`
2. **VS Code Integration** in `.vscode/settings.json`
3. **Pre-commit Hooks** in `.pre-commit-config.yaml`
4. **Workspace-specific Configuration** templates in `.ruff.toml` and `examples/workspace-setup/workspace-ruff.toml`
5. **Formatting and Linting Scripts** in `backend/scripts/format.sh` and `backend/scripts/lint.sh`
6. **Verification Script** in `scripts/verify-ruff-setup.sh`

## Installation

Ruff is already included in our development dependencies. To install it:

```bash
# Using pip
pip install ruff

# Using uv (recommended)
uv pip install ruff
```

## VS Code Integration

1. Install the [Ruff VS Code extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
2. Our workspace settings are already configured to use Ruff for formatting and linting

The key VS Code settings for Ruff are:

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  },
  "ruff.enable": true,
  "ruff.organizeImports": true,
  "ruff.fixAll": true
}
```

> **Important:** The legacy Ruff server (ruff-lsp) has been deprecated. The following settings were only supported by the legacy server and have been deprecated:
>
> - `ruff.lint.run`
> - `ruff.format.args`
>
> These settings should be removed from your configuration if present.

## Configuration Files

### Global Configuration (pyproject.toml)

The main Ruff configuration is in `backend/pyproject.toml`. This includes:

```toml
[tool.ruff]
# Target Python version
target-version = "py310"
# Exclude directories
exclude = [
    "alembic",
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".ruff_cache",
]
# Line length to match Black's default
line-length = 88

# Enable Ruff's formatter (replacement for Black)
[tool.ruff.format]
# Use double quotes for consistency
quote-style = "double"
# Indent with 4 spaces
indent-style = "space"
# Line ending style
line-ending = "auto"

[tool.ruff.lint]
# Enable all recommended rules + additional ones
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    # ... and many more
]
```

### Workspace-specific Configuration (.ruff.toml)

For workspace-specific settings, we use `.ruff.toml` files. These can be placed in any subdirectory to override the global settings for that specific part of the project.

A template is available in `examples/workspace-setup/workspace-ruff.toml`.

## Command Line Usage

### Formatting

To format Python files:

```bash
# Format a file or directory
ruff format path/to/file_or_dir

# Format and check for errors
ruff check path/to/file_or_dir --fix
```

### Linting

To lint Python files:

```bash
# Check for errors
ruff check path/to/file_or_dir

# Show error explanations
ruff check path/to/file_or_dir --explain
```

## Pre-commit Integration

We use pre-commit hooks to ensure code quality before commits. The configuration is in `.pre-commit-config.yaml`.

To run pre-commit manually:

```bash
pre-commit run --all-files
```

## Rule Selection

Our configuration enables a comprehensive set of rules, including:

- `E`, `W`: pycodestyle errors and warnings
- `F`: pyflakes
- `I`: isort
- `B`: flake8-bugbear
- `C4`: flake8-comprehensions
- `UP`: pyupgrade
- `N`: pep8-naming
- And many more

## Disabling Rules

### In-line Disabling

To disable a rule for a specific line:

```python
x = 1  # noqa: E731
```

To disable a rule for a block:

```python
# ruff: noqa: E731
def func():
    x = lambda: 1
# ruff: enable: E731
```

### File-level Disabling

In `pyproject.toml` or `.ruff.toml`:

```toml
[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Unused imports
"tests/**/*.py" = ["PLR2004", "S101"]  # Magic values and assert statements in tests
```

## Verification

To verify your Ruff setup is working correctly:

```bash
./scripts/verify-ruff-setup.sh
```

This script will:

- Check if Ruff is installed
- Verify configuration files exist
- Check VS Code settings
- Verify pre-commit hooks
- Test Ruff on a Python file

## Migrating from Other Tools

### From Black

Ruff's formatter is designed to be compatible with Black. The key differences:

- Ruff is much faster
- Ruff has fewer configuration options
- Ruff integrates formatting and linting in one tool

### From isort

Ruff includes import sorting functionality:

```bash
# Sort imports
ruff check --select I --fix
```

### From Flake8

Ruff implements most Flake8 rules and plugins:

```bash
# Run equivalent of Flake8
ruff check --select E,F,W
```

## Troubleshooting

### Common Issues

1. **Conflicts with other formatters/linters**: Ensure other tools (Black, isort, etc.) are disabled in your editor and pre-commit hooks.

2. **Unexpected formatting**: Check your `.ruff.toml` and `pyproject.toml` configurations for conflicting settings.

3. **Performance issues**: If Ruff is slow, check for large files or complex rules that might be causing the slowdown.

### Getting Help

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Ruff GitHub Issues](https://github.com/astral-sh/ruff/issues)
- [Ruff Discord](https://discord.gg/astral-sh)
