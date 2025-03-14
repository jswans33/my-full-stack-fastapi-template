#!/usr/bin/env python
"""
Unified CLI for UML diagram generation.

This script provides a unified command-line interface for generating all types
of UML diagrams, including class, sequence, activity, and state diagrams.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import the UML modules
from utils.uml.core.filesystem import FileSystem
from utils.uml.core.service import UmlService
from utils.uml.factories import DefaultDiagramFactory

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Constants
OUTPUT_BASE_DIR = Path("docs/source/_generated_uml")


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate UML diagrams from source code.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Command to execute",
        required=True,
    )

    # Common arguments for all commands
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--source",
        "-s",
        required=True,
        help="Source directory or file to analyze",
    )
    common_parser.add_argument(
        "--output",
        "-o",
        help="Output directory for diagrams",
    )
    common_parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Recursively analyze directories",
    )
    common_parser.add_argument(
        "--exclude",
        "-e",
        action="append",
        default=[],
        help="Patterns to exclude (can be specified multiple times)",
    )
    common_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    # Class diagram command
    class_parser = subparsers.add_parser(
        "class",
        help="Generate class diagrams",
        parents=[common_parser],
    )
    class_parser.add_argument(
        "--include-private",
        "-p",
        action="store_true",
        help="Include private members in diagrams",
    )

    # Sequence diagram command
    sequence_parser = subparsers.add_parser(
        "sequence",
        help="Generate sequence diagrams",
        parents=[common_parser],
    )
    sequence_parser.add_argument(
        "--module",
        "-m",
        help="Module to analyze",
    )
    sequence_parser.add_argument(
        "--class",
        "-c",
        dest="class_name",
        help="Class to analyze",
    )
    sequence_parser.add_argument(
        "--method",
        help="Method to analyze",
    )
    sequence_parser.add_argument(
        "--function",
        "-f",
        help="Function to analyze",
    )

    # Activity diagram command
    activity_parser = subparsers.add_parser(
        "activity",
        help="Generate activity diagrams",
        parents=[common_parser],
    )

    # State diagram command
    state_parser = subparsers.add_parser(
        "state",
        help="Generate state diagrams",
        parents=[common_parser],
    )

    # All diagrams command
    all_parser = subparsers.add_parser(
        "all",
        help="Generate all types of diagrams",
        parents=[common_parser],
    )
    all_parser.add_argument(
        "--include-private",
        "-p",
        action="store_true",
        help="Include private members in class diagrams",
    )

    # App sequences command
    app_sequences_parser = subparsers.add_parser(
        "app-sequences",
        help="Generate sequence diagrams for key application entry points",
    )
    app_sequences_parser.add_argument(
        "--app-dir",
        default="backend/app",
        help="Application directory (default: backend/app)",
    )
    app_sequences_parser.add_argument(
        "--output",
        "-o",
        help="Output directory for diagrams",
    )
    app_sequences_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser


def get_output_dir(args: argparse.Namespace, diagram_type: str | None = None) -> Path:
    """Get the output directory for diagrams.

    Args:
        args: Command-line arguments
        diagram_type: Type of diagram (class, sequence, activity, state)

    Returns:
        Path to the output directory
    """
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = OUTPUT_BASE_DIR

    if diagram_type:
        output_dir = output_dir / diagram_type

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def create_service(settings: dict | None = None) -> UmlService:
    """Create and return a UML service with the given settings.

    Args:
        settings: Service settings

    Returns:
        UML service instance
    """
    file_system = FileSystem()
    factory = DefaultDiagramFactory(file_system, settings)
    return UmlService(factory, settings)


def generate_class_diagram(args: argparse.Namespace) -> int:
    """Generate class diagrams.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get output directory
    output_dir = get_output_dir(args, "class")

    # Create service
    settings = {
        "include_private": args.include_private,
        "recursive": args.recursive,
        "exclude_patterns": args.exclude,
    }
    service = create_service(settings)

    # Generate class diagrams
    try:
        source_path = Path(args.source)
        output_path = output_dir / f"{source_path.stem}.puml"

        service.generate_diagram(
            "class",
            source_path,
            output_path,
            **settings,
        )

        logger.info(f"Class diagram generated successfully in {output_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error generating class diagram: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def generate_sequence_diagram(args: argparse.Namespace) -> int:
    """Generate sequence diagrams.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get output directory
    output_dir = get_output_dir(args, "sequence")

    # Create service
    settings = {
        "recursive": args.recursive,
        "exclude_patterns": args.exclude,
    }

    # Add module, class, method, function if provided
    if args.module:
        settings["module"] = args.module
    if args.class_name:
        settings["class"] = args.class_name
    if args.method:
        settings["method"] = args.method
    if args.function:
        settings["function"] = args.function

    service = create_service(settings)

    # Generate sequence diagrams
    try:
        source_path = Path(args.source)
        output_path = output_dir / f"{source_path.stem}.puml"

        service.generate_diagram(
            "sequence",
            source_path,
            output_path,
            **settings,
        )

        logger.info(f"Sequence diagram generated successfully in {output_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error generating sequence diagram: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def generate_activity_diagram(args: argparse.Namespace) -> int:
    """Generate activity diagrams.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get output directory
    output_dir = get_output_dir(args, "activity")

    # Create service
    settings = {
        "recursive": args.recursive,
        "exclude_patterns": args.exclude,
    }
    service = create_service(settings)

    # Generate activity diagrams
    try:
        source_path = Path(args.source)
        output_path = output_dir / f"{source_path.stem}.puml"

        service.generate_diagram(
            "activity",
            source_path,
            output_path,
            **settings,
        )

        logger.info(f"Activity diagram generated successfully in {output_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error generating activity diagram: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def generate_state_diagram(args: argparse.Namespace) -> int:
    """Generate state diagrams.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get output directory
    output_dir = get_output_dir(args, "state")

    # Create service
    settings = {
        "recursive": args.recursive,
        "exclude_patterns": args.exclude,
    }
    service = create_service(settings)

    # Generate state diagrams
    try:
        source_path = Path(args.source)
        output_path = output_dir / f"{source_path.stem}.puml"

        service.generate_diagram(
            "state",
            source_path,
            output_path,
            **settings,
        )

        logger.info(f"State diagram generated successfully in {output_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error generating state diagram: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def generate_all_diagrams(args: argparse.Namespace) -> int:
    """Generate all types of diagrams.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get output directory
    output_dir = get_output_dir(args)

    # Create service
    settings = {
        "include_private": args.include_private,
        "recursive": args.recursive,
        "exclude_patterns": args.exclude,
    }
    service = create_service(settings)

    # Generate all diagrams
    try:
        source_path = Path(args.source)

        # Convert Path objects to strings to match the expected type
        source_paths = [str(source_path)]
        source_paths_dict = {
            "class": source_paths,
            "sequence": source_paths,
            "activity": source_paths,
            "state": source_paths,
        }

        results = service.generate_all_diagrams(source_paths_dict, output_dir)

        # Log results
        for diagram_type, diagrams in results.items():
            if diagrams:
                logger.info(
                    f"Generated {len(diagrams)} {diagram_type} diagrams in {output_dir / diagram_type}",
                )

        logger.info(f"All UML diagrams generated successfully in {output_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error generating diagrams: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def generate_app_sequences(args: argparse.Namespace) -> int:
    """Generate sequence diagrams for key application entry points.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    import subprocess

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get output directory
    output_dir = get_output_dir(args, "sequence")

    # Define important entry points for sequence diagrams
    # Format: (class_name, method_name, output_filename)
    ENTRY_POINTS = [
        # User Authentication Flows
        ("login", "login_access_token", "authentication_flow"),  # Login flow
        ("login", "test_token", "token_verification"),  # Token verification
        # User Management Flows
        ("users", "create_user", "admin_create_user"),  # Admin creates user
        ("users", "register_user", "user_signup"),  # User signup
        ("users", "update_user_me", "user_update_profile"),  # Update profile
        ("users", "update_password_me", "user_change_password"),  # Change password
        ("users", "delete_user_me", "user_delete_account"),  # Delete account
        # Password Recovery Flow
        (
            "login",
            "recover_password",
            "password_recovery_request",
        ),  # Request password reset
        ("login", "reset_password", "password_reset"),  # Reset password
        # Other API Endpoints
        # Add other important flows here
    ]

    print("Extracting sequence diagrams from backend/app...")
    print("=" * 50)

    success_count = 0
    for module_name, method_name, output_name in ENTRY_POINTS:
        output_file = output_dir / f"{output_name}.puml"

        # For routes modules, we need to specify the full path
        if module_name in ("login", "users", "items", "private", "utils"):
            # API route modules
            module_path = f"api.routes.{module_name}"
        else:
            # Other modules
            module_path = module_name

        print(f"Generating diagram for {module_path}.{method_name}...")

        # Construct the command
        cmd = [
            "python",
            "-m",
            "utils.uml.cli.uml_cli",
            "sequence",
            "--dir",
            args.app_dir,
            "--module",
            module_path,
            "--class",
            "router",  # For FastAPI routers, the class is "router"
            "--method",
            method_name,
            "--output",
            str(output_file),
            "--verbose" if args.verbose else "",
        ]

        # Remove empty arguments
        cmd = [arg for arg in cmd if arg]

        try:
            # Run the extraction command
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                print(f"✓ Successfully generated: {output_file}")
                success_count += 1
            else:
                print(f"× Failed to generate diagram. Error: {result.stderr}")

                # Try an alternative approach for router functions
                # Sometimes router functions are directly accessible by module.function_name
                alternative_cmd = [
                    "python",
                    "-m",
                    "utils.uml.cli.uml_cli",
                    "sequence",
                    "--dir",
                    args.app_dir,
                    "--module",
                    module_path,
                    "--function",
                    method_name,  # Try as a function instead of a class method
                    "--output",
                    str(output_file),
                    "--verbose" if args.verbose else "",
                ]

                # Remove empty arguments
                alternative_cmd = [arg for arg in alternative_cmd if arg]

                print("  Trying alternative approach...")
                alt_result = subprocess.run(
                    alternative_cmd,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if alt_result.returncode == 0:
                    print(
                        f"✓ Successfully generated using alternative approach: {output_file}",
                    )
                    success_count += 1
                else:
                    print(f"× Alternative approach also failed: {alt_result.stderr}")

        except Exception as e:
            print(f"× Error: {e!s}")

    print("=" * 50)
    print(
        f"Sequence diagram extraction completed: {success_count}/{len(ENTRY_POINTS)} successful",
    )
    print(f"Diagrams saved to: {output_dir}")

    return 0 if success_count > 0 else 1


def main() -> int:
    """Run the UML generator CLI.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = create_parser()
    args = parser.parse_args()

    # Execute the appropriate command
    if args.command == "class":
        return generate_class_diagram(args)
    if args.command == "sequence":
        return generate_sequence_diagram(args)
    if args.command == "activity":
        return generate_activity_diagram(args)
    if args.command == "state":
        return generate_state_diagram(args)
    if args.command == "all":
        return generate_all_diagrams(args)
    if args.command == "app-sequences":
        return generate_app_sequences(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
