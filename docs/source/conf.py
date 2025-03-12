"""Sphinx configuration."""

import os
import sys

sys.path.insert(0, os.path.abspath("../../backend"))

project = "FastAPI Full Stack Template"
copyright = "2025, FastAPI Team"
author = "FastAPI Team"
version = "1.0"
release = "1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "myst_parser",
    "sphinxcontrib.mermaid",
    "sphinxcontrib.plantuml",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# PlantUML configuration
plantuml = r"java -jar C:\ProgramData\chocolatey\lib\plantuml\tools\plantuml.jar"
plantuml_output_format = "svg"
plantuml_latex_output_format = "pdf"

# Configure PlantUML search paths
import os

plantuml_search_path = [os.path.abspath(os.path.join(os.path.dirname(__file__)))]
