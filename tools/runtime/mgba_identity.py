"""Fail-closed build identity for the mGBA executables the Python probes launch.

The runtime authority requires the emulator to be identified from the binary
itself and never from its path, because the shared install has been overwritten
in place by a different build before. The PowerShell launchers compare
VersionInfo.FileVersion; a Python driver has no equivalent without a platform
dependency, so these probes pin the stronger identity the repository already
records for the packaged build: the executable SHA-256 that
docs/runtime-capture.md stores beside its FileVersion. Each probe calls
require_mgba_build before it can reach a process launch.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class MgbaBuild:
    """One accepted emulator build, named and pinned by its executable digest."""

    label: str
    sha256: str


PACKAGED_0_10_5 = MgbaBuild(
    "packaged mGBA 0.10.5 (win64)",
    "5A3C98C2984DD04BD0D7C9378CDFAE937AE0D73A196C880BB2EECF3B254AF247",
)

DEFAULT_PACKAGED_MGBA = (
    Path(__file__).resolve().parents[2]
    / "build"
    / "tools"
    / "mgba-0.10.5"
    / "extracted"
    / "mGBA-0.10.5-win64"
    / "mGBA.exe"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def require_mgba_build(executable: Path, build: MgbaBuild) -> Path:
    """Return the resolved executable, or refuse before anything is launched."""
    resolved = Path(executable).resolve()
    if not resolved.is_file():
        raise RuntimeError(
            f"mGBA executable not found: {resolved} "
            f"(required {build.label}, sha256 {build.sha256})"
        )
    observed = _sha256(resolved)
    if observed != build.sha256:
        raise RuntimeError(
            f"mGBA identity mismatch: required {build.label} sha256 "
            f"{build.sha256}, found sha256 {observed} at {resolved}"
        )
    return resolved
