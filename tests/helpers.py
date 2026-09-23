from __future__ import annotations

import hashlib
import zlib

import yaml

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


# --- a sprite-declaring synthetic ROM (graphics-export safety tests) ---------
#
# `graphics export` is the one ROM-loading command whose destination is a
# caller-chosen artefact path, so its source-alias refusal needs a ROM the
# catalog can verify *and* that declares the actor-sprite capability. Only the
# read-only corpus load itself has to be stubbed, because `capability.require`
# re-checks every declared extent against the *packaged* catalogue and synthetic
# bytes can never satisfy that - the same shape the code-quality audit's own
# CQA-01 probe used.

#: File offsets the synthetic sprite declaration points at. All are inside the
#: image, 4-byte (table) / 2-byte (palette) aligned, and leave the palette's 256
#: halfwords and the one-entry character table in range.
SPRITE_TABLE_OFFSET = 0x1000
SPRITE_STRUCTURE_OFFSET = 0x0400
SPRITE_PALETTE_OFFSET = 0x0200
SPRITE_ROM_SIZE = 0x2000

#: The profile id the synthetic sprite ROM is catalogued under.
SPRITE_PROFILE_ID = "synthetic_actor_sprites"


def actor_sprite_tables() -> dict[str, object]:
    """The `tables.actor_sprites` mapping a synthetic sprite ROM declares."""
    return {
        "actor_sprites": {
            "character_table_address": 0x08000000 + SPRITE_TABLE_OFFSET,
            "character_count": 1,
            "animation_pointer_offset": 0,
            "object_palette_address": 0x08000000 + SPRITE_PALETTE_OFFSET,
            "evidence": "synthetic fixture for graphics-export safety tests",
        }
    }


def make_synthetic_sprite_rom() -> bytes:
    """A catalogued synthetic ROM whose profile declares one actor-sprite slot.

    The single character-table entry is a well-formed ROM pointer, so the real
    `ActorSprites` walk constructs and simply finds no graphics (the structure's
    animation list is zeroed). That is enough for the export path: the source
    alias refusal must run before any asset lookup.
    """
    data = bytearray(
        make_synthetic_rom(game_code="BG3E", size=SPRITE_ROM_SIZE)
    )
    data[SPRITE_TABLE_OFFSET : SPRITE_TABLE_OFFSET + 4] = (
        0x08000000 + SPRITE_STRUCTURE_OFFSET
    ).to_bytes(4, "little")
    return bytes(data)


def write_catalog(path, profiles, tables: dict[str, object] | None = None) -> None:
    """Write a `--profiles` catalogue YAML from `RomProfile` objects.

    Mirrors `tests.unit.test_cli.write_catalog`, plus an optional extra `tables`
    block so a synthetic profile can declare a capability the packaged catalogue
    does not carry for it.
    """
    mappings = []
    for profile in profiles:
        mapping = {
            "id": profile.id,
            "game": profile.game,
            "region": profile.region,
            "revision": profile.revision,
            "game_code": profile.game_code,
            "size": profile.size,
            "crc32": profile.crc32,
            "md5": profile.md5,
            "sha1": profile.sha1,
            "sha256": profile.sha256,
            "sources": list(profile.sources),
            "notes": profile.notes,
        }
        if tables is not None:
            mapping["tables"] = tables
        mappings.append(mapping)
    path.write_text(
        yaml.safe_dump({"schema_version": 1, "profiles": mappings}), encoding="utf-8"
    )
