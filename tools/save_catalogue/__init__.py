"""The save catalogue: index every battery save and savestate on this machine.

The catalogue answers "which file is which" for an owner whose real save was
once found only after four wrong guesses. It is a library plus a CLI; the store
is SQLite under `LOG1_SAVE_CATALOGUE_HOME` (default `~/.dsh/work/saves`, outside
the repository) and no save byte ever enters it.

What it will claim, and what it will not:

* a file's kind comes from its first bytes, never from its extension, so a
  `.ss1` that is really a 240x160 RGB PNG screenshot is `screenshot-png` with
  `misnamed` set and is never offered as a state to load;
* a non-PNG `.ss*` is `unknown-state`: the mGBA savestate header is a
  HYPOTHESIS here (no real state exists in this corpus to verify field offsets
  against), so no ROM and no game is ever attributed from one;
* battery validity is computed only where a geometry is proven, per title: Buu's
  Fury and Legacy of Goku II today, each carrying its own evidence level in the
  `GEOMETRIES` table. Legacy of Goku's bytes are read untransformed because its
  byte-order transform is unknown, so its occupancy bit is unverified and its
  validity is UNKNOWN, never a pass.

The index, the logs and every report hold hashes, sizes, mtimes, offsets, field
names and notes only. Sources are opened read-only, and every write refuses a
target inside a scanned root or an indexed source.
"""

from __future__ import annotations

from . import geometry, sniff, store
from .walk import DEFAULT_PROTECTED_BACKUPS, default_roots, record_run, register, scan
from .store import Entry, Store, home

__all__ = [
    "DEFAULT_PROTECTED_BACKUPS",
    "Entry",
    "Store",
    "default_roots",
    "geometry",
    "home",
    "scan",
    "sniff",
    "store",
]
