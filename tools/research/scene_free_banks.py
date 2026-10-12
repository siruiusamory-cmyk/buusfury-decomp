"""Which banks are free in the scenes that actually contain a Cell placement?

Game-wide no bank is free. Per scene the present actors are few, so their index usage is far smaller. This
computes, for every map that places sprite id 252, the set of other ids placed there, unions their per-definition
palette index usage from the static census, and reports which banks that union leaves untouched.

Per-definition index sets come from decoding every piece's container with the project codec, so this is the same
measurement as the game-wide census, restricted to the actors that can share a scene with Cell.
"""

from __future__ import annotations

import struct
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\Dev\log1-remake-cell-c1")
sys.path.insert(0, str(ROOT))
from tools.webfoot.formats import webfoot_lz  # noqa: E402

ROM_BASE = 0x08000000
DEFINITION_TABLE = 0x6B6BB4
HEADER = 0x54
PIECE_BYTES = 12
FRAME_HEADER = 8
ANIMATION_HEADER = 4
MAX_IDS = 1200
MAX_SLOTS = 256
MAX_FRAMES = 64
BANK = 16
CELL_ID = 252

MAP_TABLE = 0x8E2E0
MAP_STRIDE = 0x38
FAMILIES = {0x0800FD55: 0x10, 0x080111A9: 0x0C, 0x08017DA3: 0x10}

image = Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - Buu's Fury (U).gba").read_bytes()


def u32(offset: int) -> int | None:
    if offset < 0 or offset + 4 > len(image):
        return None
    return struct.unpack_from("<I", image, offset)[0]


def definition_indices() -> dict[int, set]:
    indices: dict[int, set] = defaultdict(set)
    for identifier in range(MAX_IDS):
        definition = u32(DEFINITION_TABLE + 4 * identifier)
        if definition is None or not (ROM_BASE <= definition < ROM_BASE + len(image)):
            continue
        base = definition - ROM_BASE
        slot_count = image[base]
        if not 1 <= slot_count <= MAX_SLOTS:
            continue
        seen: set[tuple[int, int, int]] = set()
        for slot in range(slot_count):
            record = u32(base + HEADER + 4 * slot)
            if record is None or not (ROM_BASE <= record < ROM_BASE + len(image)):
                continue
            record_offset = record - ROM_BASE
            frame_count = u32(record_offset)
            if frame_count is None or not 1 <= frame_count <= MAX_FRAMES:
                continue
            for direction in range(4):
                for frame in range(frame_count):
                    pointer = u32(record_offset + ANIMATION_HEADER + 16 * frame + 4 * direction)
                    if pointer is None or not (ROM_BASE <= pointer < ROM_BASE + len(image)):
                        continue
                    frame_offset = pointer - ROM_BASE
                    piece_count = u32(frame_offset)
                    if piece_count is None or piece_count > 64:
                        continue
                    for index in range(piece_count):
                        piece = frame_offset + FRAME_HEADER + PIECE_BYTES * index
                        width, height = image[piece + 2], image[piece + 3]
                        attr = u32(piece + 4)
                        container = u32(piece + 8)
                        if attr is None or container is None:
                            continue
                        if (attr >> 13) & 1 == 0:
                            continue
                        if not (ROM_BASE <= container < ROM_BASE + len(image)):
                            continue
                        key = (container, width, height)
                        if key in seen:
                            continue
                        seen.add(key)
                        try:
                            decoded = webfoot_lz.unpack(image, container - ROM_BASE,
                                                        maximum_output=1 << 20).data
                        except Exception:                                # noqa: BLE001
                            continue
                        for byte in decoded:
                            if byte:
                                indices[identifier].add(byte)
    return indices


def map_ids(map_id: int) -> list[int]:
    entry = MAP_TABLE + MAP_STRIDE * map_id
    count = u32(entry + 0x04)
    base = u32(entry + 0x14)
    if not count or base is None or not (ROM_BASE <= base < ROM_BASE + len(image)):
        return []
    out = []
    for slot in range(min(count, 256)):
        record = u32(base - ROM_BASE + 4 * slot)
        if record is None or not (ROM_BASE <= record < ROM_BASE + len(image)):
            continue
        offset = record - ROM_BASE
        factory = u32(offset)
        if factory not in FAMILIES:
            continue
        out.append(u32(offset + FAMILIES[factory]) or 0)
    return out


def main() -> int:
    per_definition = definition_indices()
    print(f"per-definition index sets computed for {len(per_definition)} definitions")

    scenes = [(map_id, map_ids(map_id)) for map_id in range(0x1000)]
    scenes = [(map_id, ids) for map_id, ids in scenes if CELL_ID in ids]
    print(f"maps placing sprite id {CELL_ID}: {[map_id for map_id, _ in scenes]}")

    for map_id, ids in scenes:
        present = sorted({identifier for identifier in ids if identifier != CELL_ID})
        used: set[int] = set()
        unknown = []
        for identifier in present:
            if identifier in per_definition:
                used |= per_definition[identifier]
            else:
                unknown.append(identifier)
        free = [bank for bank in range(16)
                if not any(bank * BANK <= value < bank * BANK + BANK for value in used)]
        print(f"\nmap {map_id}: {len(present)} other id(s), indices used by them {len(used)}, "
              f"free banks {free}")
        print(f"  ids present: {present[:24]}{' ...' if len(present) > 24 else ''}")
        if unknown:
            print(f"  ids with no measured art (no index data): {unknown[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
