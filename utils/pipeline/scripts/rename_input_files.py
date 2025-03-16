"""
Script to rename input files with a QUOTE_ prefix.
"""

import shutil
from pathlib import Path


def rename_files_with_prefix(directory, prefix="QUOTE_"):
    """
    Rename all files in the directory with the given prefix.

    Args:
        directory: Directory containing files to rename
        prefix: Prefix to add to filenames
    """
    directory_path = Path(directory)

    if not directory_path.exists() or not directory_path.is_dir():
        print(f"Directory {directory} does not exist or is not a directory")
        return

    # Create a backup directory
    backup_dir = directory_path / "original_files_backup"
    backup_dir.mkdir(exist_ok=True)

    # Get all files in the directory
    files = [f for f in directory_path.iterdir() if f.is_file()]

    renamed_count = 0
    for file_path in files:
        # Skip files that already have the prefix
        if file_path.name.startswith(prefix):
            continue

        # Create backup
        backup_path = backup_dir / file_path.name
        shutil.copy2(file_path, backup_path)

        # Create new filename with prefix
        new_name = f"{prefix}{file_path.name}"
        new_path = file_path.parent / new_name

        # Rename file
        try:
            file_path.rename(new_path)
            renamed_count += 1
            print(f"Renamed: {file_path.name} -> {new_name}")
        except Exception as e:
            print(f"Error renaming {file_path.name}: {str(e)}")

    print(f"\nRenamed {renamed_count} files")
    print(f"Original files backed up to {backup_dir}")


if __name__ == "__main__":
    input_dir = Path(__file__).parent / "data" / "input"
    rename_files_with_prefix(input_dir, "QUOTE_")
