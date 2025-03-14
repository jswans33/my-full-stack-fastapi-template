#!/usr/bin/env python
"""
Script to set up the utils virtual environment and install the utils package in development mode.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Set up the utils virtual environment and install the utils package in development mode."""
    # Get the utils directory
    utils_dir = Path(__file__).parent.absolute()
    venv_dir = utils_dir / ".venv"

    # Print information
    print(f"Setting up utils virtual environment in {venv_dir}...")

    # Check if uv is installed
    try:
        subprocess.run(
            ["uv", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("uv not found. Please install uv first:")
        print("  pip install uv")
        return 1

    # Create virtual environment if it doesn't exist
    if not venv_dir.exists():
        print("Creating virtual environment...")
        try:
            subprocess.run(
                ["uv", "venv", str(venv_dir)],
                check=True,
            )
            print(f"Virtual environment created at {venv_dir}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            return 1

    # Determine the activate script path based on the platform
    if sys.platform == "win32":
        activate_script = venv_dir / "Scripts" / "activate.bat"
        activate_cmd = f"call {activate_script}"
    else:
        activate_script = venv_dir / "bin" / "activate"
        activate_cmd = f"source {activate_script}"

    # Install the package in development mode
    print("Installing utils package in development mode...")
    try:
        # On Windows, we need to use a batch file to activate the venv and run the command
        if sys.platform == "win32":
            temp_bat = utils_dir / "temp_install.bat"
            with open(temp_bat, "w") as f:
                f.write("@echo off\n")
                f.write(f"call {activate_script}\n")
                f.write(f"uv pip install -e {utils_dir}\n")

            subprocess.run([str(temp_bat)], check=True, shell=True)
            temp_bat.unlink()  # Remove the temporary batch file
        else:
            # On Unix-like systems, we can use a single shell command
            subprocess.run(
                f"{activate_cmd} && uv pip install -e {utils_dir}",
                check=True,
                shell=True,
            )

        print("Installation successful!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing package: {e}")
        return 1

    # Install additional dependencies
    print("Installing additional dependencies...")
    try:
        if sys.platform == "win32":
            temp_bat = utils_dir / "temp_deps.bat"
            with open(temp_bat, "w") as f:
                f.write("@echo off\n")
                f.write(f"call {activate_script}\n")
                f.write("uv pip install pyyaml\n")

            subprocess.run([str(temp_bat)], check=True, shell=True)
            temp_bat.unlink()  # Remove the temporary batch file
        else:
            subprocess.run(
                f"{activate_cmd} && uv pip install pyyaml",
                check=True,
                shell=True,
            )

        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return 1

    # Print activation instructions
    print("\nTo activate the virtual environment:")
    if sys.platform == "win32":
        print(f"  {activate_cmd}")
    else:
        print(f"  {activate_cmd}")

    print(
        "\nAfter activating the virtual environment, you can run the UML generator scripts:"
    )
    print("  python utils/run_uml_generator.py")
    print("  python utils/extract_class.py --source backend/app")
    print("  python utils/extract_sequence.py --source backend/app")
    print("  python utils/extract_activity.py --source backend/app")
    print("  python utils/extract_state.py --source backend/app")
    print("  python utils/uml/run.py --type all --source backend/app")

    return 0


if __name__ == "__main__":
    sys.exit(main())
