from __future__ import annotations

import hashlib
import zlib

from tools.webfoot.gba_header import GbaHeader, calculate_header_checksum
from tools.webfoot.hashing import RomHashes
from tools.webfoot.profile import RomProfile


def make_synthetic_rom(
    *,
    title: str = "SYNTHETIC",
    game_code: str = "TEST",
    maker_code: str = "01",
    revision: int = 0,
    size: int = 0x100,
) -> bytes:
    if size < 0xC0:
        raise ValueError("synthetic ROM size must be at least 0xC0")
    data = bytearray(size)
    data[0xA0:0xAC] = title.encode("ascii").ljust(12, b"\x00")[:12]
    data[0xAC:0xB0] = game_code.encode("ascii")
    data[0xB0:0xB2] = maker_code.encode("ascii")
    data[0xB2] = 0x96
    data[0xBC] = revision
    data[0xBD] = calculate_header_checksum(bytes(data))
    return bytes(data)


def hashes_for(data: bytes) -> RomHashes:
    return RomHashes(
        crc32=f"{zlib.crc32(data) & 0xFFFFFFFF:08x}",
        md5=hashlib.md5(data, usedforsecurity=False).hexdigest(),
        sha1=hashlib.sha1(data, usedforsecurity=False).hexdigest(),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def profile_for(data: bytes, **overrides: object) -> RomProfile:
    header = GbaHeader.from_bytes(data)
    hashes = hashes_for(data)
    mapping: dict[str, object] = {
        "id": "synthetic_exact",
        "game": "synthetic",
        "region": "test",
        "revision": header.software_version,
        "game_code": header.game_code,
        "size": len(data),
        "crc32": hashes.crc32,
        "md5": hashes.md5,
        "sha1": hashes.sha1,
        "sha256": hashes.sha256,
        "sources": ["synthetic test data"],
        "notes": "not ROM-derived",
    }
    mapping.update(overrides)
    return RomProfile.from_mapping(mapping)
