"""Streaming file hashes used for exact ROM identity."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import BinaryIO
from pathlib import Path
import zlib


DEFAULT_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True, slots=True)
class RomHashes:
    crc32: str
    md5: str
    sha1: str
    sha256: str


def hash_stream(
    stream: BinaryIO,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    prefix_size: int = 0,
) -> tuple[RomHashes, bytes]:
    """Hash one binary stream and optionally capture its leading bytes."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if prefix_size < 0:
        raise ValueError("prefix_size must not be negative")

    crc32 = 0
    md5 = hashlib.md5(usedforsecurity=False)
    sha1 = hashlib.sha1(usedforsecurity=False)
    sha256 = hashlib.sha256()
    prefix = bytearray()

    while chunk := stream.read(chunk_size):
        if len(prefix) < prefix_size:
            prefix.extend(chunk[: prefix_size - len(prefix)])
        crc32 = zlib.crc32(chunk, crc32)
        md5.update(chunk)
        sha1.update(chunk)
        sha256.update(chunk)

    return (
        RomHashes(
            crc32=f"{crc32 & 0xFFFFFFFF:08x}",
            md5=md5.hexdigest(),
            sha1=sha1.hexdigest(),
            sha256=sha256.hexdigest(),
        ),
        bytes(prefix),
    )


def hash_file(path: str | Path, *, chunk_size: int = DEFAULT_CHUNK_SIZE) -> RomHashes:
    """Hash *path* through a read-only streaming handle."""
    source = Path(path)
    with source.open("rb") as stream:
        hashes, _ = hash_stream(stream, chunk_size=chunk_size)
    return hashes
