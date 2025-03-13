#!/usr/bin/env python
"""Extract sequence diagrams from key entry points in the application.

This script analyzes the backend/app and extracts sequence diagrams for
important entry points in the API, creating visual documentation of the
application's key workflows.
"""

import os
import subprocess
from pathlib import Path

# Ensure output directory exists
OUTPUT_DIR = Path("docs/source/_generated_uml/sequence")
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
    output_file = OUTPUT_DIR / f"{output_name}.puml"

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
        "utils.extract_sequence",
        "--dir",
        "backend/app",
        "--module",
        module_path,
        "--class",
        "router",  # For FastAPI routers, the class is "router"
        "--method",
        method_name,
        "--output",
        str(output_file),
        "--verbose",
    ]

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
                "utils.extract_sequence",
                "--dir",
                "backend/app",
                "--module",
                module_path,
                "--function",
                method_name,  # Try as a function instead of a class method
                "--output",
                str(output_file),
                "--verbose",
            ]

            print("  Trying alternative approach...")
            alt_result = subprocess.run(
                alternative_cmd, capture_output=True, text=True, check=False
            )

            if alt_result.returncode == 0:
                print(
                    f"✓ Successfully generated using alternative approach: {output_file}"
                )
                success_count += 1
            else:
                print(f"× Alternative approach also failed: {alt_result.stderr}")

    except Exception as e:
        print(f"× Error: {e!s}")

print("=" * 50)
print(
    f"Sequence diagram extraction completed: {success_count}/{len(ENTRY_POINTS)} successful"
)
print(f"Diagrams saved to: {OUTPUT_DIR}")

# Remind the user to run the main UML generator to include these in the docs
print("\nTo include these diagrams in the documentation, run:")
print("python -m utils.run_uml_generator")

if success_count == 0:
    print(
        "\nNote: If extraction failed, you may need to modify the extract_sequence.py script"
    )
    print("to better handle the specific structure of your FastAPI application.")
