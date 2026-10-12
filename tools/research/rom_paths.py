"""Where the retail images live, stated once, so no tool carries a machine's path.

WHY. Twenty-three probe scripts in this directory named a machine-specific absolute path for the same two
files, which the public-surface screen refuses by design: a tracked file must not depend on one machine's
layout. It also made the probes unusable from a worktree other than the one they were written in.

WHAT THE RULE IS NOW. The images live in the repository's own ``roms/`` directory. ``LOGX_ROM_DIR`` (or
``WEBFOOT_ROM_DIR``) overrides that directory for a checkout that keeps them elsewhere: a ticket worktree is
usually created without a ``roms/`` of its own, so either the directory is a junction into the checkout that
has the images or the variable names it. No filename is re-stated at a call site; the two images this
project reads are named here once.

These helpers resolve PATHS and nothing else. They do not check a digest, decide whether an image is
canonical, or refuse a file - a caller that needs identity compares the sha256 of what it read, which is the
rule every governed run already follows.
"""

from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

#: Environment variables that name the directory holding the retail images, first match wins.
ROM_DIR_ENVIRONMENT = ("LOGX_ROM_DIR", "WEBFOOT_ROM_DIR")

#: The destination title this project builds against.
BUU_FURY_NAME = "Dragon Ball Z - Buu's Fury (U).gba"
#: The source title the ported character art and palettes come from.
LEGACY_OF_GOKU_2_NAME = "Dragon Ball Z - The Legacy of Goku II (USA).gba"


def rom_dir() -> Path:
    """The directory holding the retail images: the environment's override, else ``<repo>/roms``."""
    for name in ROM_DIR_ENVIRONMENT:
        value = os.environ.get(name)
        if value:
            return Path(value)
    return REPO / "roms"


def buu_fury() -> Path:
    return rom_dir() / BUU_FURY_NAME


def legacy_of_goku_2() -> Path:
    return rom_dir() / LEGACY_OF_GOKU_2_NAME
