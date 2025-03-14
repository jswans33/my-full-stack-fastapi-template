#!/usr/bin/env python
"""
Setup script for creating a virtual environment for utils that installs in the backend.

This script:
1. Creates a virtual environment for utils
2. Installs UV package manager
3. Installs the backend as an editable package
4. Installs any utils-specific dependencies

Usage:
    python utils/setup_venv.py [--clean]

Options:
    --clean    Remove existing virtual environment before creating a new one
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Get the absolute paths
CURRENT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = CURRENT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
VENV_DIR = CURRENT_DIR / ".venv"


def run_command(cmd, cwd=None):
    """Run a command and print its output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    return result


def main():
    """Set up the virtual environment."""
    # Check if --clean flag is provided
    clean = "--clean" in sys.argv

    # Remove existing virtual environment if --clean flag is provided
    if clean and VENV_DIR.exists():
        print(f"Removing existing virtual environment at {VENV_DIR}")
        shutil.rmtree(VENV_DIR)

    # Create virtual environment if it doesn't exist
    if not VENV_DIR.exists():
        print(f"Creating virtual environment in {VENV_DIR}")
        run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
    else:
        print(f"Virtual environment already exists at {VENV_DIR}")

    # Determine the Python executable in the virtual environment
    if os.name == "nt":  # Windows
        python_exe = VENV_DIR / "Scripts" / "python.exe"
        uv_path = VENV_DIR / "Scripts" / "uv.exe"
    else:  # Unix/Linux/Mac
        python_exe = VENV_DIR / "bin" / "python"
        uv_path = VENV_DIR / "bin" / "uv"

    # Install UV package manager if not already installed
    if not uv_path.exists():
        print("Installing UV package manager")
        run_command(
            [
                str(python_exe),
                "-m",
                "pip",
                "install",
                "uv",
            ],
        )

    # Install the backend as an editable package using UV
    print(f"Installing backend as editable package from {BACKEND_DIR}")
    run_command(
        [
            str(uv_path),
            "pip",
            "install",
            "-e",
            str(BACKEND_DIR),
        ],
    )

    # Install utils-specific dependencies if any
    utils_pyproject = CURRENT_DIR / "pyproject.toml"
    if utils_pyproject.exists():
        print("Installing utils dependencies")
        run_command(
            [
                str(uv_path),
                "pip",
                "install",
                "-e",
                str(CURRENT_DIR),
            ],
        )

    print("\nSetup complete!")
    print("\nTo activate the virtual environment:")
    if os.name == "nt":  # Windows
        print(f"    {VENV_DIR}\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print(f"    source {VENV_DIR}/bin/activate")

    print("\nTo run utils scripts with the virtual environment:")
    print(f"    {python_exe} -m utils.extract_sequence --help")


if __name__ == "__main__":
    main()
