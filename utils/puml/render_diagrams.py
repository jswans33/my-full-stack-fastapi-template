"""
PlantUML Diagram Renderer

This module renders PlantUML diagrams to PNG or SVG images using the plantuml Python package.
It can be used as an alternative to the HTML viewer if you prefer local rendering.

Requirements:
- Python 3.6+
- plantuml package (pip install plantuml)
- Internet connection (for the PlantUML server)
"""

import re
from pathlib import Path

import plantuml  # type: ignore

from .core import ensure_dir_exists, get_output_path, setup_logger
from .exceptions import RenderError
from .settings import settings

# Set up logger
logger = setup_logger("render_diagrams")


def render_diagram(
    puml_file: str | Path,
    output_dir: str | Path | None = None,
    format: str = settings.default_format,
) -> bool:
    """
    Render a PlantUML diagram to an image.

    Args:
        puml_file: Path to the PlantUML file
        output_dir: Directory to save the rendered image (default: settings.output_dir)
        format: Output format (png or svg, default: settings.default_format)

    Returns:
        True if successful, False otherwise

    Raises:
        RenderError: If there is an error rendering the diagram
    """
    try:
        # Convert paths to Path objects
        puml_path = Path(puml_file)
        out_dir = Path(output_dir) if output_dir else settings.output_dir

        # Create output directory if it doesn't exist
        ensure_dir_exists(out_dir)

        # Get the output file path
        output_file = get_output_path(puml_path, format)

        # Check if the output file already exists and is newer than the input file
        if output_file.exists():
            puml_mtime = puml_path.stat().st_mtime
            output_mtime = output_file.stat().st_mtime
            if output_mtime > puml_mtime:
                logger.info(f"Skipping {puml_path} (already rendered and up to date)")
                return True

        # Create a PlantUML server instance with the appropriate URL for the format
        server_url = (
            settings.plantuml_server_svg
            if format.lower() == "svg"
            else settings.plantuml_server_png
        )
        plantuml_server = plantuml.PlantUML(url=server_url)

        # Generate the diagram
        logger.info(f"Rendering {puml_path} to {format.upper()}...")
        plantuml_server.processes_file(str(puml_path), outfile=str(output_file))
        logger.info(f"Saved to {output_file}")
        return True

    except Exception as e:
        raise RenderError(f"Error rendering {puml_file}: {e}") from e


def update_viewer_index(output_dir: str | Path | None = None) -> None:
    """
    Update the index.html file with the new diagrams.

    Args:
        output_dir: Directory containing rendered images (default: settings.output_dir)

    Raises:
        RenderError: If there is an error updating the index file
    """
    try:
        out_dir = Path(output_dir) if output_dir else settings.output_dir
        index_path = out_dir / "index.html"

        if not index_path.exists():
            logger.warning(f"Index file not found at {index_path}")
            return

        # Read the index.html file
        content = index_path.read_text(encoding="utf-8")

        # Find the scanDiagramsInFolder function
        pattern = r"function scanDiagramsInFolder\(folder\) \{(.*?)return \[\];\s*\}"
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            logger.warning("Could not find scanDiagramsInFolder function in index.html")
            return

        # Get all diagram folders
        folders: dict[str, list[str]] = {}
        for path in out_dir.glob("**/*.svg"):
            if path.parent == out_dir:
                continue

            folder_name = path.parent.name
            if folder_name not in folders:
                folders[folder_name] = []

            folders[folder_name].append(path.stem)

        # Build the new function content
        new_function = [
            "function scanDiagramsInFolder(folder) {",
            "        // In a browser environment with local files, we can't use fetch to check if files exist",
            "        // So we'll just return the diagrams we know exist based on the folder",
            "",
        ]

        # Add each folder's diagrams
        first_folder = True
        for folder, diagrams in folders.items():
            if diagrams:
                if first_folder:
                    new_function.append(f"        if (folder === '{folder}') {{")
                    first_folder = False
                else:
                    new_function.append(f"        else if (folder === '{folder}') {{")

                # Format the diagrams list as a JavaScript array
                diagrams_str = str(diagrams).replace("'", '"')
                new_function.append(f"          return {diagrams_str};")
                new_function.append("        }")

        # Add the default case
        if first_folder:
            new_function.append("        return [];")
        else:
            new_function.extend(
                [
                    " else {",
                    "          return [];",
                    "        }",
                ],
            )

        new_function.extend(
            [
                "",
                "        return [];",
                "      }",
            ],
        )

        # Replace the function in the content
        new_content = re.sub(
            pattern,
            "\n".join(new_function),
            content,
            flags=re.DOTALL,
        )

        # Write the updated content back to the file
        index_path.write_text(new_content, encoding="utf-8")
        logger.info(
            f"Updated index.html with {sum(len(diagrams) for diagrams in folders.values())} diagrams",
        )

    except Exception as e:
        raise RenderError(f"Error updating index file: {e}") from e


def render_all_diagrams(
    directory: str | Path | None = None,
    output_dir: str | Path | None = None,
    format: str = settings.default_format,
) -> tuple[int, int]:
    """
    Render all PlantUML diagrams in the specified directory.

    Args:
        directory: Directory containing PlantUML files (default: settings.source_dir)
        output_dir: Directory to save rendered images (default: settings.output_dir)
        format: Output format (png or svg, default: settings.default_format)

    Returns:
        Tuple of (success_count, total_count)

    Raises:
        RenderError: If there is an error rendering the diagrams
    """
    try:
        # Convert paths to Path objects
        src_dir = Path(directory) if directory else settings.source_dir
        out_dir = Path(output_dir) if output_dir else settings.output_dir

        # Find all .puml files in the directory and its subdirectories
        puml_files = list(src_dir.glob("**/*.puml"))

        if not puml_files:
            logger.warning(f"No .puml files found in {src_dir}")
            return (0, 0)

        # Create output directory
        ensure_dir_exists(out_dir)

        # Render each diagram
        success_count = 0
        for puml_path in puml_files:
            if render_diagram(puml_path, out_dir, format):
                success_count += 1

        # Print summary
        logger.info(
            f"Rendered {success_count} of {len(puml_files)} diagrams to {out_dir}",
        )

        # Update the index.html file
        update_viewer_index(out_dir)

        return (success_count, len(puml_files))

    except Exception as e:
        raise RenderError(f"Error rendering diagrams: {e}") from e


def launch_viewer() -> bool:
    """
    Launch the PlantUML viewer in the default web browser.

    Returns:
        True if successful, False otherwise

    Raises:
        RenderError: If there is an error launching the viewer
    """
    try:
        import webbrowser

        # Get the path to the HTML viewer
        viewer_path = settings.output_dir / "index.html"

        # Check if the viewer exists
        if not viewer_path.exists():
            raise RenderError(f"React HTML viewer not found: {viewer_path}")

        # Check if the output directory exists
        if not settings.output_dir.exists():
            raise RenderError(
                f"Output directory not found: {settings.output_dir}\n"
                "Please render the diagrams first using the 'render' command.",
            )

        # Open the viewer in the default web browser
        logger.info(f"Opening React HTML viewer: {viewer_path}")
        webbrowser.open(f"file://{viewer_path.resolve()}")

        return True

    except Exception as e:
        raise RenderError(f"Error launching viewer: {e}") from e
