"""Read-only ROM identification orchestration."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from .gba_header import GbaHeader, HEADER_SIZE
from .hashing import RomHashes, hash_stream
from .profile import ProfileMatch, RomProfileCatalog


class RomReadError(OSError):
    """Raised when a ROM path cannot be safely identified."""


class RomChangedError(RomReadError):
    """Raised when a file changes while it is being identified."""


@dataclass(frozen=True, slots=True)
class RomIdentification:
    path: Path
    size: int
    hashes: RomHashes
    header: GbaHeader
    profile_match: ProfileMatch


def identify_rom(path: str | Path, catalog: RomProfileCatalog) -> RomIdentification:
    source = Path(path)
    if not source.exists():
        raise RomReadError(f"ROM does not exist: {source}")
    if not source.is_file():
        raise RomReadError(f"ROM path is not a file: {source}")

    with source.open("rb") as stream:
        before = os.fstat(stream.fileno())
        hashes, header_bytes = hash_stream(stream, prefix_size=HEADER_SIZE)
        after = os.fstat(stream.fileno())

    path_after = source.stat()
    identity_before = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    )
    identity_after = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    )
    path_identity_after = (
        path_after.st_dev,
        path_after.st_ino,
        path_after.st_size,
        path_after.st_mtime_ns,
    )
    if identity_before != identity_after or identity_before != path_identity_after:
        raise RomChangedError(f"ROM changed while being identified: {source}")

    header = GbaHeader.from_bytes(header_bytes)
    match = catalog.match(size=before.st_size, hashes=hashes, header=header)
    return RomIdentification(
        path=source,
        size=before.st_size,
        hashes=hashes,
        header=header,
        profile_match=match,
    )
