"""Buu's Fury Text Editor: a desktop front end for `tools.webfoot.textedit`.

The engine owns every ROM semantic. This package owns the window, the project
file, and the state of a row.

    python -m tools.buufury_text <rom> [--canonical <rom>]
"""

from __future__ import annotations

from .identity import PRODUCT_NAME, PRODUCT_VERSION
from .project import Project, ProjectFileError, load, save
from .session import RECORD, SLOT, Hit, Line, Meter, Session, State, open_image

__all__ = [
    "PRODUCT_NAME",
    "PRODUCT_VERSION",
    "Hit",
    "Line",
    "Meter",
    "Project",
    "ProjectFileError",
    "RECORD",
    "SLOT",
    "Session",
    "State",
    "load",
    "open_image",
    "save",
]
