# Standard Operating Procedure: Testing Environment Setup and Test Execution

## 1. Environment Setup Verification

### 1.1 Virtual Environment

#### Windows (Git Bash)
```bash
# Check if virtual environment exists
ls .venv  # Should show directories like Scripts/, Lib/, etc.

# Verify Python version in virtual environment
"$(pwd)/.venv/Scripts/python.exe" --version  # Should match project requirements (>=3.9)
```

#### Unix/Linux/macOS
```bash
# Check if virtual environment exists
ls .venv  # Should show directories like bin/, lib/, etc.

# Verify Python version in virtual environment
./.venv/bin/python --version  # Should match project requirements (>=3.9)
```

### 1.2 Dependencies Verification

#### Windows (Git Bash)
```bash
# First ensure you're in the correct directory
cd /c/Repos/FCA-dashboard3/my-full-stack-fastapi-template/utils/pipeline

# List installed packages
"$(pwd)/.venv/Scripts/python.exe" -m pip list
```

#### Unix/Linux/macOS
```bash
# List installed packages
./.venv/bin/python -m pip list

# Key packages that should be present:
# - pytest (test framework)
# - pytest-cov (coverage reporting)
# - pydantic (data validation)
# - watchdog (file monitoring)
# - PyYAML (YAML support)
# - All packages from pyproject.toml and requirements-dev.txt
```

### 1.3 Project Installation

#### Windows (Git Bash)
```bash
# First ensure you're in the correct directory
cd /c/Repos/FCA-dashboard3/my-full-stack-fastapi-template/utils/pipeline

# Install development dependencies and project in editable mode
"$(pwd)/.venv/Scripts/python.exe" -m pip install -r requirements-dev.txt -e .
```

#### Unix/Linux/macOS
```bash
# Install development dependencies and project in editable mode
./.venv/bin/python -m pip install -r requirements-dev.txt -e .
```

## 2. Running Tests

### 2.1 Working Directory
All tests should be run from the pipeline root directory:
```bash
cd /path/to/FCA-dashboard3/my-full-stack-fastapi-template/utils/pipeline
```

### 2.2 Test Execution Methods

#### Using run_tests.py (Recommended)

##### Windows (Git Bash)
```bash
# First ensure you're in the correct directory
cd /c/Repos/FCA-dashboard3/my-full-stack-fastapi-template/utils/pipeline

# Run specific test file
"$(pwd)/.venv/Scripts/python.exe" run_tests.py tests/path/to/test_file.py

# Run with verbosity
"$(pwd)/.venv/Scripts/python.exe" run_tests.py tests/path/to/test_file.py -v

# Run all tests
"$(pwd)/.venv/Scripts/python.exe" run_tests.py
```

##### Unix/Linux/macOS
```bash
# Run specific test file
./.venv/bin/python run_tests.py tests/path/to/test_file.py

# Run with verbosity
./.venv/bin/python run_tests.py tests/path/to/test_file.py -v

# Run all tests
./.venv/bin/python run_tests.py
```

#### Using pytest directly

##### Windows (Git Bash)
```bash
# First ensure you're in the correct directory
cd /c/Repos/FCA-dashboard3/my-full-stack-fastapi-template/utils/pipeline

# Run specific test file
"$(pwd)/.venv/Scripts/python.exe" -m pytest tests/path/to/test_file.py

# Run with coverage
"$(pwd)/.venv/Scripts/python.exe" -m pytest --cov=. tests/path/to/test_file.py

# Run with verbose output
"$(pwd)/.venv/Scripts/python.exe" -m pytest -v tests/path/to/test_file.py
```

##### Unix/Linux/macOS
```bash
# Run specific test file
./.venv/bin/python -m pytest tests/path/to/test_file.py

# Run with coverage
./.venv/bin/python -m pytest --cov=. tests/path/to/test_file.py

# Run with verbose output
./.venv/bin/python -m pytest -v tests/path/to/test_file.py
```

### 2.3 Coverage Reports
- HTML coverage report is automatically generated in `coverage_html/` directory
- Open `coverage_html/index.html` in a browser to view detailed coverage information

## 3. Troubleshooting

### 3.1 Common Issues

#### Missing Dependencies
If you encounter ModuleNotFoundError:
```bash
# Reinstall all dependencies
./.venv/Scripts/python -m pip install -r requirements-dev.txt -e .
```

#### Import Errors
If you encounter import errors:
- Verify you're running tests from the pipeline root directory
- Check that the project is installed in editable mode (-e .)
- Verify PYTHONPATH includes the project root

### 3.2 Environment Reset
If you need to reset the environment:
```bash
# Remove virtual environment
rm -rf .venv

# Create new virtual environment
python -m venv .venv

# Install dependencies
./.venv/Scripts/python -m pip install -r requirements-dev.txt -e .
```

## 4. Best Practices

### 4.1 Test Organization
- Keep test files in the `tests/` directory
- Mirror the project structure in the tests directory
- Name test files with `test_` prefix
- Name test functions with `test_` prefix

### 4.2 Test Coverage
- Aim for 100% coverage of new code
- Use coverage reports to identify untested code
- Write tests for both success and failure cases

### 4.3 Test Isolation
- Each test should be independent
- Use pytest fixtures for common setup
- Clean up any test artifacts in teardown

## 5. Shell Setup

### 5.1 Setting up Zsh

#### macOS
Zsh is the default shell on macOS Catalina and later.

#### Linux
```bash
# Install zsh
sudo apt-get update
sudo apt-get install zsh

# Make zsh the default shell
chsh -s $(which zsh)

# Install Oh My Zsh (recommended)
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

#### Windows
1. Install Windows Subsystem for Linux (WSL):
```powershell
# Run in PowerShell as Administrator
wsl --install
```

2. Install Ubuntu from Microsoft Store

3. Set up Zsh in Ubuntu:
```bash
# Update package list
sudo apt update

# Install zsh
sudo apt install zsh

# Install Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Make zsh default shell
chsh -s $(which zsh)
```

### 5.2 Zsh Configuration
1. Edit ~/.zshrc to customize your environment:
```bash
# Open .zshrc in your preferred editor
nano ~/.zshrc

# Common configurations:
export PATH=$HOME/bin:/usr/local/bin:$PATH
export ZSH="$HOME/.oh-my-zsh"

# Python virtual environment support
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

# Set theme (if using Oh My Zsh)
ZSH_THEME="robbyrussell"

# Useful aliases for Python development
alias py="python"
alias ipy="ipython"
alias pytest="python -m pytest"
alias pip="python -m pip"
```

2. Apply changes:
```bash
source ~/.zshrc
```

### 5.3 Recommended Zsh Plugins
Add these to your plugins list in ~/.zshrc:
```bash
plugins=(
    git
    python
    pip
    virtualenv
    virtualenvwrapper
    docker
    docker-compose
)
```

## 6. Continuous Integration
- All tests should pass locally before pushing
- Review coverage reports before submitting changes
- Address any test failures promptly
