#!/usr/bin/env python
"""
Script to run the UML generator from the virtual environment.
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Run the UML generator from the virtual environment."""
    # Get the utils directory
    utils_dir = Path(__file__).parent.absolute()
    venv_dir = utils_dir / ".venv"

    # Check if the virtual environment exists
    if not venv_dir.exists():
        print(f"Virtual environment not found at {venv_dir}")
        print(
            "Please run utils/install_dev.py first to set up the virtual environment.",
        )
        return 1

    # Determine the python executable path based on the platform
    if sys.platform == "win32":
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"

    # Check if the python executable exists
    if not python_exe.exists():
        print(f"Python executable not found at {python_exe}")
        print(
            "Please run utils/install_dev.py first to set up the virtual environment.",
        )
        return 1

    # Get the command line arguments
    args = sys.argv[1:]

    # If no arguments are provided, show help
    if not args:
        print("Usage: python utils/run_uml.py [COMMAND] [ARGS]")
        print("\nAvailable commands:")
        print(
            "  uml/cli/run_uml_generator.py                  - Generate all UML diagrams",
        )
        print(
            "  uml/cli/extract_class.py --source PATH        - Generate class diagrams",
        )
        print(
            "  uml/cli/extract_sequence.py --source PATH     - Generate sequence diagrams",
        )
        print(
            "  uml/cli/extract_activity.py --source PATH     - Generate activity diagrams",
        )
        print(
            "  uml/cli/extract_state.py --source PATH        - Generate state diagrams",
        )
        print(
            "  uml/run.py --type TYPE --source PATH  - Generate diagrams with more options",
        )
        print("\nExamples:")
        print("  python utils/run_uml.py uml/cli/run_uml_generator.py")
        print("  python utils/run_uml.py uml/cli/extract_class.py --source backend/app")
        print("  python utils/run_uml.py uml/run.py --type all --source backend/app")
        return 0

    # Construct the command to run
    script_path = utils_dir / args[0]
    if not script_path.exists():
        print(f"Script not found: {script_path}")
        return 1

    # Run the command
    try:
        # Add the project root to the Python path to ensure imports work correctly
        project_root = utils_dir.parent.absolute()
        env = os.environ.copy()

        # Set PYTHONPATH to include the project root
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{project_root}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = str(project_root)

        cmd = [str(python_exe), str(script_path)] + args[1:]
        print(f"Running: {' '.join(cmd)}")
        print(f"With PYTHONPATH: {env.get('PYTHONPATH')}")
        subprocess.run(cmd, check=True, env=env)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
