#!/usr/bin/env bash

set -e
set -x

# Run mypy for type checking
mypy app

# Run Ruff linter with all rules enabled
ruff check app --select=ALL

# Run Ruff formatter in check mode (no changes)
ruff format app --check
