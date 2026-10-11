"""Measure route A's blast radius: who else is in Cell's maps, and which palette indices they paint.

Route A appends a bank with Cell's colours and repoints the loader for the scenes he appears in. The loader
that exists is per map SCENE, not per map id, so before choosing it the honest measurement is who else is
placed in those maps and how much of the palette their art uses - because any index they share with Cell
changes under their feet.

Inputs: the built image (Cell already in it) and the base image, whose definition table gives every
placement's art. Read-only.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot.formats import webfoot_lz  # noqa: E402

ROM_BASE = 0x08000000
MAP_TABLE = 0x8E2E0
MAP_STRIDE = 0x38
DEFINITION_TABLE = 0x6B6BB4
CELL_MAPS = (32, 137, 138)
CELL_INDICES = (0x00, 0x01, 0x02, 0x0A, 0x0B, 0x0D, 0x0E, 0x17, 0x24, 0x2A, 0x61, 0x70, 0x78, 0x7C,
                0x81, 0x84, 0x98, 0xD1, 0xD3, 0xDE, 0xE5, 0xF8)


def word(image: bytes, offset: int) -> int:
    return struct.unpack_from("<I", image, offset)[0]


def pointer(image: bytes, offset: int) -> int | None:
    value = word(image, offset)
    return value if ROM_BASE <= value < ROM_BASE + len(image) else None


def placed_ids(image: bytes, map_id: int) -> list[int]:
    entry = MAP_TABLE + MAP_STRIDE * map_id
    count = word(image, entry + 0x04)
    array = pointer(image, entry + 0x14)
    ids = []
    if array is None or not 0 < count <= 256:
        return ids
    base = array - ROM_BASE
    for slot in range(count):
        record = pointer(image, base + 4 * slot)
        if record is None:
            continue
        offset = record - ROM_BASE
        factory = word(image, offset) if word(image, offset) >= ROM_BASE else None
        if factory not in (0x0800FD55, 0x080111A9, 0x08017DA3):
            continue
        sprite_at = offset + (0x0C if factory == 0x080111A9 else 0x10)
        if sprite_at + 4 <= len(image):
            ids.append(word(image, sprite_at))
    return ids


def sprite_indices(image: bytes, sprite_id: int) -> set[int]:
    """Every palette index the art of one sprite id paints, via its frames' containers."""
    definition = pointer(image, DEFINITION_TABLE + 4 * sprite_id)
    if definition is None:
        return set()
    base = definition - ROM_BASE
    indices: set[int] = set()
    for slot in range(image[base] & 0xFF):
        record = pointer(image, base + 0x54 + 4 * slot)
        if record is None:
            continue
        record_offset = record - ROM_BASE
        frames = word(image, record_offset)
        if not 1 <= frames <= 64:
            continue
        for frame in range(frames):
            for direction in range(4):
                frame_pointer = pointer(image, record_offset + 4 + 16 * frame + 4 * direction)
                if frame_pointer is None:
                    continue
                cursor = frame_pointer - ROM_BASE
                for piece in range(word(image, cursor)):
                    entry = cursor + 8 + 12 * piece
                    container = pointer(image, entry + 8)
                    if container is None:
                        continue
                    try:
                        indices.update(webfoot_lz.unpack(image, container - ROM_BASE).data)
                    except Exception:
                        continue
    return indices


def main() -> int:
    image = Path(sys.argv[1]).read_bytes()
    cell = set(CELL_INDICES)
    others: dict[int, set[int]] = {}
    for map_id in CELL_MAPS:
        ids = placed_ids(image, map_id)
        print(f"map {map_id}: {len(ids)} placement(s), sprite ids {sorted(set(ids))}")
        for sprite_id in sorted(set(ids)):
            if sprite_id in others:
                continue
            others[sprite_id] = sprite_indices(image, sprite_id)

    print()
    overlapping = {}
    for sprite_id, indices in sorted(others.items()):
        shared = indices & cell
        if shared:
            overlapping[sprite_id] = sorted(shared)
    if not overlapping:
        print("no other placement in those maps paints any index Cell uses")
    for sprite_id, shared in sorted(overlapping.items()):
        print(f"sprite {sprite_id:>4}: shares {len(shared)} of Cell's indices -> {shared}")
    union = set().union(*others.values()) if others else set()
    print(f"\nindices any other placement in those maps paints: {len(union)}")
    print(f"of Cell's {len(cell)} indices, shared with another placement: "
          f"{len(set().union(*overlapping.values()) if overlapping else set())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
