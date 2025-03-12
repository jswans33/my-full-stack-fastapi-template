#!/bin/sh -e
set -x

# Run Ruff linter with auto-fix for all rules
ruff check app scripts --fix --exit-zero

# Run Ruff formatter
ruff format app scripts
