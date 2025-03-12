"""
PlantUML Diagram Renderer

This module renders PlantUML diagrams to PNG or SVG images using the plantuml Python package.
It can be used as an alternative to the HTML viewer if you prefer local rendering.

Requirements:
- Python 3.6+
- plantuml package (pip install plantuml)
- Internet connection (for the PlantUML server)
"""

import socket
import threading
import time
from pathlib import Path

import plantuml  # type: ignore

from .api import run_server
from .core import ensure_dir_exists, get_output_path, setup_logger
from .exceptions import RenderError
from .settings import settings

# Set up logger
logger = setup_logger("render_diagrams")


def is_port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return False
        except OSError:
            return True


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
        viewer_template = Path(__file__).parent / "viewer" / "index.html"

        # Check if the viewer exists
        if not viewer_template.exists():
            raise RenderError(f"Viewer template not found: {viewer_template}")

        # Check if the output directory exists and render diagrams if needed
        if not settings.output_dir.exists():
            logger.info("Output directory not found, rendering diagrams...")
            render_all_diagrams()
            render_all_diagrams(format="png")  # Also render PNG versions
        else:
            # Check if any diagrams need to be rendered
            puml_files = list(settings.source_dir.glob("**/*.puml"))
            needs_render = False
            for puml_path in puml_files:
                svg_path = get_output_path(puml_path, "svg")
                png_path = get_output_path(puml_path, "png")
                if not svg_path.exists() or not png_path.exists():
                    needs_render = True
                    break

            if needs_render:
                logger.info("Some diagrams need to be rendered...")
                render_all_diagrams()
                render_all_diagrams(format="png")

        # Check if the API server is already running
        port = 8088
        if is_port_in_use(port):
            logger.info(f"API server already running on port {port}")
        else:
            # Start the API server in a background thread
            server_thread = threading.Thread(
                target=run_server,
                kwargs={"host": "127.0.0.1", "port": port},
                daemon=True,
            )
            server_thread.start()
            logger.info(f"Starting API server on http://localhost:{port}")

            # Give the server a moment to start
            time.sleep(1)

        # Open the viewer in the default web browser
        logger.info("Opening viewer...")
        webbrowser.open(f"file://{viewer_template.resolve()}")

        # Keep the main thread alive while the server is running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down server...")

        return True

    except Exception as e:
        raise RenderError(f"Error launching viewer: {e}") from e
