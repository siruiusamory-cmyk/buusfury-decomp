"""Buu's Fury Text Editor: a desktop front end for `tools.webfoot.textedit`.

The engine owns every ROM semantic. This package owns the window, the project
file, and the state of a row.

    python -m tools.buufury_text <rom> [--canonical <rom>]
"""

from __future__ import annotations

from .identity import PACKAGE, PRODUCT_NAME, PRODUCT_VERSION, VERSION_TUPLE
from .project import Project, ProjectFileError, load, save
from .session import (
    APPEARANCE,
    BY_PLACE,
    BY_SPEAKER,
    LINES,
    RECORDS,
    RECORD,
    SLOT,
    STORAGE,
    UNGROUPED,
    Hit,
    Line,
    Meter,
    Session,
    State,
    open_image,
)

__all__ = [
    "APPEARANCE",
    "BY_PLACE",
    "BY_SPEAKER",
    "Hit",
    "LINES",
    "Line",
    "Meter",
    "PACKAGE",
    "PRODUCT_NAME",
    "PRODUCT_VERSION",
    "Project",
    "ProjectFileError",
    "RECORDS",
    "RECORD",
    "SLOT",
    "STORAGE",
    "Session",
    "State",
    "UNGROUPED",
    "VERSION_TUPLE",
    "load",
    "open_image",
    "save",
]
