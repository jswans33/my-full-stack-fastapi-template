#!/usr/bin/env python
"""
Script to run tests with the pytest environment.

This script:
1. Activates the virtual environment if it exists
2. Runs pytest with the specified arguments
3. Generates a coverage report
"""

import os
import subprocess
import sys
from pathlib import Path


def find_venv_python():
    """Find the Python executable in the virtual environment."""
    script_dir = Path(__file__).resolve().parent
    venv_dir = script_dir / ".venv"

    if sys.platform == "win32":
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"

    if python_exe.exists():
        return str(python_exe)

    return sys.executable


def run_tests(args=None):
    """Run tests with coverage reporting."""
    if args is None:
        args = []

    # Get the directory of this script
    script_dir = Path(__file__).resolve().parent

    # Change to the script directory
    os.chdir(script_dir)

    # Find the Python executable in the virtual environment
    python_exe = find_venv_python()

    # Build the command
    cmd = [
        python_exe,
        "-m",
        "pytest",
        "--cov=.",
        "--cov-report=term",
        "--cov-report=html:coverage_html",
    ]
    cmd.extend(args)

    print(f"Running: {' '.join(cmd)}")

    try:
        # Run the command
        result = subprocess.run(cmd, capture_output=False)

        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed.")

        print("\nCoverage report generated in coverage_html/index.html")
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def check_venv():
    """Check if the virtual environment is set up."""
    script_dir = Path(__file__).resolve().parent
    venv_dir = script_dir / ".venv"

    if not venv_dir.exists():
        print("Virtual environment not found.")
        print("Please run setup_pytest_env.py to create it:")
        print("  python setup_pytest_env.py")
        return False

    return True


def main():
    """Main entry point."""
    if not check_venv():
        return 1

    # Pass any command line arguments to pytest
    args = sys.argv[1:]
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())
