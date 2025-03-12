"""
PlantUML API Server

This module provides a FastAPI server for serving PlantUML diagrams and diagram metadata.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .settings import settings

app = FastAPI(title="PlantUML API")

# Allow CORS for React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/diagrams")
def get_diagrams():
    """Get all available diagrams grouped by folder."""
    diagram_structure = {}
    output_dir = settings.output_dir

    for path in output_dir.glob("**/*"):
        if path.is_file() and path.suffix in (".svg", ".png"):
            # Get folder relative to output directory
            rel_dir = path.parent.relative_to(output_dir)
            folder = str(rel_dir) if rel_dir.name != "." else "root"

            # Get base name without extension
            base_name = path.stem

            # Add to diagram structure
            if folder not in diagram_structure:
                diagram_structure[folder] = set()
            diagram_structure[folder].add(base_name)

    # Convert sets to sorted lists for JSON serialization
    return {k: sorted(v) for k, v in diagram_structure.items()}


# Serve diagrams statically
app.mount(
    "/diagrams",
    StaticFiles(directory=str(settings.output_dir)),
    name="diagrams",
)


def run_server(host: str = "127.0.0.1", port: int = 8088):
    """Run the API server."""
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
