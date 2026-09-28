"""Buu's Fury decompilation baseline harness.

The package deliberately has NO third-party dependencies: it runs on a stock
CPython with only the standard library, so the baseline can be reproduced on a
bare machine.

Modules
-------
identity   canonical ROM identity and fail-closed verification
regions    the region map: loading, tiling validation, markdown rendering
toolchain  toolchain discovery and the doctor report
assets     rebuild the grit / JCALG1 asset regions and compare them to the ROM
build      assemble a ROM from the region map, with explicit provenance
cli        command-line entry point (`python -m buusfury ...`)
"""

__all__ = ["identity", "regions", "toolchain", "assets", "build", "cli"]

__version__ = "0.1.0"
