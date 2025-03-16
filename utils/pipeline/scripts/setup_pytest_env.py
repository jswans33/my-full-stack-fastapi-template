#!/usr/bin/env python
"""
Script to set up a proper pytest environment for the pipeline project.

This script:
1. Creates a virtual environment if it doesn't exist
2. Installs the required dependencies
3. Installs the pipeline package in development mode
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return its output."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        print(result.stdout)
        return True
    except Exception as e:
        print(f"Error executing command: {e}")
        return False


def setup_env():
    """Set up the pytest environment."""
    # Get the directory of this script
    script_dir = Path(__file__).resolve().parent

    # Change to the script directory
    os.chdir(script_dir)

    # Check if virtual environment exists
    venv_dir = script_dir / ".venv"
    if not venv_dir.exists():
        print("Creating virtual environment...")
        if not run_command([sys.executable, "-m", "venv", str(venv_dir)]):
            return False

    # Determine the pip executable
    if sys.platform == "win32":
        pip_exe = venv_dir / "Scripts" / "pip"
    else:
        pip_exe = venv_dir / "bin" / "pip"

    # Upgrade pip
    print("Upgrading pip...")
    if not run_command([str(pip_exe), "install", "--upgrade", "pip"]):
        return False

    # Install pytest and related packages
    print("Installing pytest and related packages...")
    if not run_command([str(pip_exe), "install", "-r", "requirements-dev.txt"]):
        return False

    # Install the pipeline package in development mode
    print("Installing pipeline package in development mode...")
    if not run_command([str(pip_exe), "install", "-e", "."]):
        return False

    # Print success message
    print("\nPytest environment set up successfully!")
    print("\nTo activate the virtual environment:")
    if sys.platform == "win32":
        print(f"  {venv_dir}\\Scripts\\activate")
    else:
        print(f"  source {venv_dir}/bin/activate")

    print("\nTo run the tests:")
    print("  pytest")
    print("  pytest -v")
    print("  pytest --cov=.")

    return True


if __name__ == "__main__":
    if not setup_env():
        sys.exit(1)
