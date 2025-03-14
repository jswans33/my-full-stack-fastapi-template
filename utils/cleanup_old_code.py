#!/usr/bin/env python
"""
Script to clean up old UML generator code by moving it to the z_archive directory.

This script:
1. Creates a backup of the old code in the z_archive directory
2. Removes the old directories after backup
3. Updates any references to the old code in documentation
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
UTILS_DIR = PROJECT_ROOT / "utils"
ARCHIVE_DIR = PROJECT_ROOT / "z_archive"

# Directories to archive
OLD_DIRS = [
    UTILS_DIR / "uml_generator",
    UTILS_DIR / "sequence_extractor",
]

# Create timestamp for archive folder
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
ARCHIVE_UML_DIR = ARCHIVE_DIR / f"uml_old_{TIMESTAMP}"


def create_archive_directory():
    """Create the archive directory if it doesn't exist."""
    print(f"Creating archive directory: {ARCHIVE_UML_DIR}")
    os.makedirs(ARCHIVE_UML_DIR, exist_ok=True)


def backup_old_code():
    """Backup old code to the archive directory."""
    for old_dir in OLD_DIRS:
        if old_dir.exists():
            # Get the directory name
            dir_name = old_dir.name

            # Create the destination directory
            dest_dir = ARCHIVE_UML_DIR / dir_name

            print(f"Backing up {old_dir} to {dest_dir}")

            # Copy the directory to the archive
            shutil.copytree(old_dir, dest_dir)

            print(f"Backup of {dir_name} completed")
        else:
            print(f"Directory {old_dir} does not exist, skipping")


def remove_old_directories():
    """Remove old directories after backup."""
    for old_dir in OLD_DIRS:
        if old_dir.exists():
            print(f"Removing directory: {old_dir}")

            # Ask for confirmation before removing
            confirm = input(f"Are you sure you want to remove {old_dir}? (y/n): ")
            if confirm.lower() == "y":
                shutil.rmtree(old_dir)
                print(f"Removed {old_dir}")
            else:
                print(f"Skipping removal of {old_dir}")
        else:
            print(f"Directory {old_dir} does not exist, skipping")


def main():
    """Run the cleanup process."""
    print("Starting cleanup of old UML generator code")

    # Create archive directory
    create_archive_directory()

    # Backup old code
    backup_old_code()

    # Ask if user wants to remove old directories
    remove = input("Do you want to remove the old directories? (y/n): ")
    if remove.lower() == "y":
        remove_old_directories()
    else:
        print("Skipping removal of old directories")

    print("\nCleanup completed!")
    print(f"Old code has been backed up to: {ARCHIVE_UML_DIR}")
    print("\nNext steps:")
    print("1. Update any documentation or scripts that reference the old code")
    print("2. Enhance the activity and state diagram implementations")
    print("3. Create comprehensive test cases")
    print("4. Update documentation to reflect the new architecture")


if __name__ == "__main__":
    main()
