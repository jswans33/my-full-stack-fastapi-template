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

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # Simple format for user-friendly output
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Get the absolute paths
CURRENT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = CURRENT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
VENV_DIR = CURRENT_DIR / ".venv"


def run_command(cmd, cwd=None):
    """Run a command and log its output."""
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.stdout:
        logger.info(result.stdout)

    if result.stderr:
        logger.error(result.stderr)

    if result.returncode != 0:
        logger.error(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    return result


def main():
    """Set up the virtual environment."""
    # Check if --clean flag is provided
    clean = "--clean" in sys.argv

    # Remove existing virtual environment if --clean flag is provided
    if clean and VENV_DIR.exists():
        logger.info(f"Removing existing virtual environment at {VENV_DIR}")
        shutil.rmtree(VENV_DIR)

    # Create virtual environment if it doesn't exist
    if not VENV_DIR.exists():
        logger.info(f"Creating virtual environment in {VENV_DIR}")
        run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
    else:
        logger.info(f"Virtual environment already exists at {VENV_DIR}")

    # Determine the Python executable in the virtual environment
    if os.name == "nt":  # Windows
        python_exe = VENV_DIR / "Scripts" / "python.exe"
        uv_path = VENV_DIR / "Scripts" / "uv.exe"
    else:  # Unix/Linux/Mac
        python_exe = VENV_DIR / "bin" / "python"
        uv_path = VENV_DIR / "bin" / "uv"

    # Install UV package manager if not already installed
    if not uv_path.exists():
        logger.info("Installing UV package manager")
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
    logger.info(f"Installing backend as editable package from {BACKEND_DIR}")
    run_command(
        [
            str(uv_path),
            "pip",
            "install",
            "--python",
            str(python_exe),
            "-e",
            str(BACKEND_DIR),
        ],
    )

    # Install utils-specific dependencies if any
    utils_pyproject = CURRENT_DIR / "pyproject.toml"
    if utils_pyproject.exists():
        logger.info("Installing utils dependencies")
        run_command(
            [
                str(uv_path),
                "pip",
                "install",
                "--python",
                str(python_exe),
                "-e",
                str(CURRENT_DIR),
            ],
        )

    logger.info("\nSetup complete!")
    logger.info("\nTo activate the virtual environment:")
    if os.name == "nt":  # Windows
        logger.info(f"    Windows CMD: {VENV_DIR}\\Scripts\\activate")
        logger.info(f"    Windows Git Bash: source {VENV_DIR}/Scripts/activate")
    else:  # Unix/Linux/Mac
        logger.info(f"    source {VENV_DIR}/bin/activate")

    logger.info("\nTo run utils scripts with the virtual environment:")
    logger.info(f"    {python_exe} -m utils.extract_sequence --help")


if __name__ == "__main__":
    main()
