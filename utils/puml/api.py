import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Allow CORS for React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Convert relative path to absolute path
diagrams_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../docs/diagrams/output"),
)


@app.get("/api/diagrams")
def get_diagrams():
    diagram_structure = {}
    for root, _, files in os.walk(diagrams_dir):
        rel_dir = os.path.relpath(root, diagrams_dir)
        # Group files by base name (without extension)
        diagram_files = {}
        for f in files:
            if f.endswith((".svg", ".png")):
                base_name = os.path.splitext(f)[0]
                diagram_files[base_name] = True

        if diagram_files:
            if rel_dir == ".":
                rel_dir = "root"
            diagram_structure[rel_dir] = list(diagram_files.keys())
    return diagram_structure


# Serve diagrams statically
# Convert relative path to absolute path
diagrams_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../docs/diagrams/output"),
)

app.mount(
    "/diagrams",
    StaticFiles(directory=diagrams_dir),
    name="diagrams",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8088)
