# Utils Package

This directory contains utility scripts for sequence diagram generation and UML tools.

## Setup

The utils package is designed to work with the backend code while maintaining its own virtual environment. This allows you to run the utils scripts independently while still having access to all the backend code and dependencies.

### Creating the Virtual Environment

To set up the virtual environment for utils:

```bash
# From the project root
python utils/setup_venv.py
```

To clean up an existing virtual environment and create a fresh one:

```bash
# From the project root
python utils/setup_venv.py --clean
```

This script will:
1. Create a virtual environment in `utils/.venv/` (or remove the existing one if --clean is used)
2. Install UV package manager (a faster alternative to pip)
3. Install the backend as an editable package using UV
4. Install any utils-specific dependencies

### Activating the Virtual Environment

After setup, you can activate the virtual environment:

**Windows CMD:**
```
utils\.venv\Scripts\activate
```

**Windows Git Bash:**
```
source utils/.venv/Scripts/activate
```

**Unix/Linux/Mac:**
```
source utils/.venv/bin/activate
```

## Running Utils Scripts

Once the virtual environment is activated, you can run the utils scripts:

```bash
# Run with the module syntax
python -m utils.extract_sequence --help

# Or directly (if the script is executable)
python utils/extract_sequence.py --help
```

### Example Usage

Extract a sequence diagram for a class method:
```bash
python -m utils.extract_sequence --dir backend/app --class UserService --method create_user
```

Extract a sequence diagram for a FastAPI router function:
```bash
python -m utils.extract_sequence --dir backend/app --module api.routes.login --function login_access_token
```

## Development

If you need to add new dependencies specific to the utils package, add them to the `utils/pyproject.toml` file and rerun the setup script. The setup script uses UV for package management, which is faster and more reliable than pip.