#!/usr/bin/env python
"""Script to run the UML generator from the virtual environment."""

import logging
import os
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # Simple format to match previous print output
)
logger = logging.getLogger(__name__)


class EnvironmentError(Exception):
    """Exception raised when the virtual environment is not properly set up."""

    pass


def check_environment(utils_dir: Path) -> Path:
    """Validate the virtual environment and return the Python executable path.

    Args:
        utils_dir: Path to the utils directory

    Returns:
        Python executable path if found.

    Raises:
        EnvironmentError: If the virtual environment is not properly set up.
    """
    venv_dir = utils_dir / ".venv"
    if not venv_dir.exists():
        error_message = f"Virtual environment not found at {venv_dir}"
        raise EnvironmentError(error_message)

    # Determine the python executable path based on the platform
    python_exe = venv_dir / ("Scripts" if sys.platform == "win32" else "bin") / "python"
    if not python_exe.exists():
        error_message = f"Python executable not found at {python_exe}"
        raise EnvironmentError(error_message)

    return python_exe


def show_help_text() -> None:
    """Display usage information and available commands."""
    logger.info("Usage: python utils/run_uml.py [COMMAND] [ARGS]")
    logger.info("\nAvailable commands:")
    logger.info(
        "  uml/cli/run_uml_generator.py                  - Generate all UML diagrams",
    )
    logger.info(
        "  uml/cli/extract_class.py --source PATH        - Generate class diagrams",
    )
    logger.info(
        "  uml/cli/extract_sequence.py --source PATH     - Generate sequence diagrams",
    )
    logger.info(
        "  uml/cli/extract_activity.py --source PATH     - Generate activity diagrams",
    )
    logger.info(
        "  uml/cli/extract_state.py --source PATH        - Generate state diagrams",
    )
    logger.info(
        "  uml/run.py --type TYPE --source PATH  - Generate diagrams with more options",
    )
    logger.info("\nExamples:")
    logger.info("  python utils/run_uml.py uml/cli/run_uml_generator.py")
    logger.info(
        "  python utils/run_uml.py uml/cli/extract_class.py --source backend/app",
    )
    logger.info("  python utils/run_uml.py uml/run.py --type all --source backend/app")


def setup_python_env(project_root: Path) -> dict[str, str]:
    """Set up the Python environment with the correct PYTHONPATH.

    Args:
        project_root: Path to the project root directory

    Returns:
        Dictionary containing the environment variables
    """
    env = os.environ.copy()
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{project_root}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = str(project_root)
    return env


def run_uml_command(
    python_exe: Path,
    script_path: Path,
    args: list[str],
    env: dict[str, str],
) -> int:
    """Execute the UML generation command.

    Args:
        python_exe: Path to the Python executable
        script_path: Path to the UML script to run
        args: Command line arguments
        env: Environment variables dictionary

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        cmd = [str(python_exe), str(script_path)] + args[1:]
        logger.info(f"Running: {' '.join(cmd)}")
        logger.info(f"With PYTHONPATH: {env.get('PYTHONPATH')}")
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError:
        logger.exception("Error running UML command")
        return 1
    else:
        return 0


def main() -> int:
    """Run the UML generator from the virtual environment.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    utils_dir = Path(__file__).parent.absolute()

    try:
        # Validate environment
        python_exe = check_environment(utils_dir)

        # Get the command line arguments
        args = sys.argv[1:]
        if not args:
            show_help_text()
            return 0

        # Validate script path
        script_path = utils_dir / args[0]
        if not script_path.exists():
            logger.error("Script not found: %s", script_path)
            return 1

        # Set up environment and run command
        env = setup_python_env(utils_dir.parent.absolute())
        return run_uml_command(python_exe, script_path, args, env)

    except EnvironmentError:
        logger.exception("Environment setup error")
        logger.info(
            "Please run utils/install_dev.py first to set up the virtual environment.",
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
