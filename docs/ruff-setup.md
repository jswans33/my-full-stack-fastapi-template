# Ruff Setup Guide

This document provides comprehensive guidance on using Ruff as the primary formatter and linter in our development environment.

## What is Ruff?

[Ruff](https://github.com/astral-sh/ruff) is an extremely fast Python linter and formatter, written in Rust. It aims to replace multiple Python tools including:

- Black (formatting)
- isort (import sorting)
- Flake8 and its plugins (linting)
- pyupgrade (automatic Python upgrades)
- autopep8 (PEP 8 compliance)
- And many more

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

> **Note:** The legacy Ruff server (ruff-lsp) has been deprecated. Some settings that were only supported by the legacy server have also been deprecated, including:
>
> - `ruff.lint.run`
> - `ruff.format.args`
>
> If you encounter these settings in your configuration, you should remove them.

## Configuration

### Global Configuration

Our global Ruff configuration is in `backend/pyproject.toml`. This includes:

- Target Python version
- Line length
- Formatting rules
- Linting rules and rule selection
- Import sorting configuration
- Per-file rule exceptions

### Workspace-Specific Configuration

For workspace-specific settings, we use `.ruff.toml` files. These can be placed in any subdirectory to override the global settings for that specific part of the project.

Example `.ruff.toml`:

```toml
# Override line length for a specific module
line-length = 100

# Add additional rules for this module
[lint]
select = ["E", "F", "I", "N"]
```

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
- `COM`: flake8-commas
- `C90`: mccabe complexity
- `T20`: flake8-print
- `PT`: flake8-pytest-style
- `RET`: flake8-return
- `SIM`: flake8-simplify
- `ARG`: flake8-unused-arguments
- `ERA`: eradicate (commented out code)
- `PL`: pylint
- `TRY`: tryceratops
- `RUF`: ruff-specific rules

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
