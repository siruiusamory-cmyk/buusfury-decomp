"""WARPRAND-APP-001 - the standalone *Buu's Fury Warp Randomizer* application.

A small, user-facing Windows utility that wraps the already-proven
``reciprocal-door-pairs/3`` warp randomizer. It ships an offline artefact: it adds
no DragonByte Z capability, opens no Workbench surface and changes no capability
count.

The layers, outermost last::

    tools.webfoot.warp_randomizer          the algorithm (unchanged, reused)
    tools.webfoot.warprand.service         the application boundary (no Qt)
    tools.webfoot.warprand.gui             one window over that boundary
    Buu-Fury-Warp-Randomizer.exe           the packaged release

Run it from a checkout with ``python -m tools.webfoot.warprand``; the frozen
build uses :mod:`tools.webfoot.warprand._pyinstaller_entry`.
"""

from __future__ import annotations

from .service import (
    DEFAULT_SEED,
    MANIFEST_SUFFIX,
    POLICY_ID,
    PROGRESS_STEPS,
    PROGRESSION_DISCLAIMER,
    SUPPORTED_POLICIES,
    TOOL_NAME,
    TOOL_VERSION,
    ManifestWriteError,
    OutputAlreadyExistsError,
    OutputPathRefusedError,
    ProgressCallback,
    RandomizationOutcome,
    RomVerification,
    SeedRefusedError,
    SourceChangedError,
    UnsupportedRomError,
    WarpRandomizerAppError,
    WarpRandomizerService,
    default_manifest_path,
    default_output_path,
    default_service,
    random_seed,
    randomize_warps,
    sanitize_seed_for_filename,
    shorten_hash,
    verify_rom,
)

__all__ = [
    "DEFAULT_SEED",
    "MANIFEST_SUFFIX",
    "POLICY_ID",
    "PROGRESS_STEPS",
    "PROGRESSION_DISCLAIMER",
    "SUPPORTED_POLICIES",
    "TOOL_NAME",
    "TOOL_VERSION",
    "ManifestWriteError",
    "OutputAlreadyExistsError",
    "OutputPathRefusedError",
    "ProgressCallback",
    "RandomizationOutcome",
    "RomVerification",
    "SeedRefusedError",
    "SourceChangedError",
    "UnsupportedRomError",
    "WarpRandomizerAppError",
    "WarpRandomizerService",
    "default_manifest_path",
    "default_output_path",
    "default_service",
    "random_seed",
    "randomize_warps",
    "sanitize_seed_for_filename",
    "shorten_hash",
    "verify_rom",
]
