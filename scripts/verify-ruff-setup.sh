#!/bin/bash
# Script to verify Ruff setup and configuration

set -e

echo "🔍 Verifying Ruff installation and configuration..."

# Check if Ruff is installed
if ! command -v ruff &> /dev/null; then
    echo "❌ Ruff is not installed. Please install it with 'pip install ruff' or 'uv pip install ruff'"
    exit 1
fi

echo "✅ Ruff is installed: $(ruff --version)"

# Check for configuration files
echo -n "🔍 Checking for Ruff configuration... "
CONFIG_FILES=()

if [ -f "pyproject.toml" ]; then
    if grep -q "\[tool.ruff\]" pyproject.toml; then
        CONFIG_FILES+=("pyproject.toml")
    fi
fi

if [ -f ".ruff.toml" ]; then
    CONFIG_FILES+=(".ruff.toml")
fi

if [ ${#CONFIG_FILES[@]} -eq 0 ]; then
    echo "❌ No Ruff configuration found in pyproject.toml or .ruff.toml"
    exit 1
else
    echo "✅ Found configuration in: ${CONFIG_FILES[*]}"
fi

# Check VS Code settings
echo -n "🔍 Checking VS Code settings... "
if [ -f ".vscode/settings.json" ]; then
    if grep -q "\"editor.defaultFormatter\": \"charliermarsh.ruff\"" .vscode/settings.json; then
        echo "✅ VS Code is configured to use Ruff as formatter"
    else
        echo "❌ VS Code is not configured to use Ruff as formatter"
    fi
    
    # Check for deprecated settings
    if grep -q "\"ruff.lint.run\"" .vscode/settings.json || grep -q "\"ruff.format.args\"" .vscode/settings.json; then
        echo "⚠️ Warning: Deprecated Ruff settings detected in .vscode/settings.json"
        echo "   The following settings are deprecated and should be removed:"
        echo "   - ruff.lint.run"
        echo "   - ruff.format.args"
    fi
else
    echo "⚠️ No VS Code settings found"
fi

# Check pre-commit configuration
echo -n "🔍 Checking pre-commit configuration... "
if [ -f ".pre-commit-config.yaml" ]; then
    if grep -q "ruff" .pre-commit-config.yaml; then
        echo "✅ pre-commit is configured with Ruff"
    else
        echo "❌ pre-commit is not configured with Ruff"
    fi
else
    echo "⚠️ No pre-commit configuration found"
fi

# Test Ruff on a Python file
echo "🔍 Testing Ruff on a Python file..."
if [ -d "backend/app" ]; then
    TEST_DIR="backend/app"
elif [ -d "app" ]; then
    TEST_DIR="app"
else
    # Find any Python file
    TEST_FILE=$(find . -name "*.py" -type f | head -n 1)
    if [ -z "$TEST_FILE" ]; then
        echo "❌ No Python files found to test Ruff on"
        exit 1
    fi
    TEST_DIR=$(dirname "$TEST_FILE")
fi

echo "   Running Ruff check on $TEST_DIR..."
ruff check "$TEST_DIR" --statistics

echo "   Running Ruff format check on $TEST_DIR..."
ruff format "$TEST_DIR" --check --diff || true

echo "✅ Ruff verification complete!"
echo ""
echo "📋 Summary:"
echo "   - Ruff is installed and configured"
echo "   - Configuration files: ${CONFIG_FILES[*]}"
echo "   - VS Code integration: $([ -f ".vscode/settings.json" ] && grep -q "\"editor.defaultFormatter\": \"charliermarsh.ruff\"" .vscode/settings.json && echo "Configured" || echo "Not configured")"
echo "   - Pre-commit hooks: $([ -f ".pre-commit-config.yaml" ] && grep -q "ruff" .pre-commit-config.yaml && echo "Configured" || echo "Not configured")"
echo ""
echo "🚀 Your Ruff setup is ready to use!"