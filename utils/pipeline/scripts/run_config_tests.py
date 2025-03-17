"""Script to run all configuration system tests."""

import os
import subprocess
import sys


def run_tests():
    """Run all configuration system tests."""
    print("\n=== Running Configuration System Tests ===\n")

    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Add project root to Python path
    sys.path.insert(0, project_root)

    # Run unit tests
    print("Running unit tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/test_config_manager.py", "-v"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print("Unit tests failed!")
        return False

    # Run integration tests
    print("\nRunning integration tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/test_config_integration.py", "-v"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print("Integration tests failed!")
        return False

    print("\nAll tests passed!")
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
