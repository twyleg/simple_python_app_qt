from simple_python_app import __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

html_theme = "sphinx_rtd_theme"

master_doc = "index"
project = "simple_python_app"
copyright = "2023, twyleg"
author = "Torsten Wylegala"
version = release = __version__
