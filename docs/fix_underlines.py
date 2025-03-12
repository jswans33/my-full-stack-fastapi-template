"""Fix RST title underlines to match title length exactly."""

import re
from pathlib import Path


def count_visible_chars(text):
    """Count visible characters in text, handling Unicode correctly."""
    return len(text.strip())


def fix_underlines(content):
    """Fix underlines in RST content."""
    lines = content.split("\n")
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()  # Remove trailing whitespace
        # If we have at least one more line
        if i + 1 < len(lines):
            next_line = lines[i + 1].rstrip()  # Remove trailing whitespace
            # Check if next line is an underline
            if re.match(r"^[=\-~^]+$", next_line):
                # Get the character used for underlining
                char = next_line[0]
                # Create new underline exactly matching title length
                title_length = count_visible_chars(line)
                new_underline = char * title_length
                # Add current line and new underline
                fixed_lines.append(line)
                fixed_lines.append(new_underline)
                i += 2
                continue
        fixed_lines.append(line)
        i += 1
    return "\n".join(fixed_lines) + "\n"  # Ensure final newline


def process_file(file_path):
    """Process a single RST file."""
    print(f"Processing {file_path}")
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    fixed_content = fix_underlines(content)

    if fixed_content != content:
        with open(file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(fixed_content)
        print(f"Fixed underlines in {file_path}")


def main():
    """Process all RST files in the source directory."""
    source_dir = Path("source")
    for rst_file in source_dir.rglob("*.rst"):
        process_file(rst_file)


if __name__ == "__main__":
    main()
