"""GATE: which of the 256 OBJ palette indices does ANY retail actor's opaque pixels use?

A bank is 16 consecutive palette indices. An 8bpp sprite indexes the whole palette, so a bank is free for Cell
only if no other actor's opaque pixel uses any index inside it. This decodes the tile data every piece references,
across all definitions, frames and directions, and histograms the indices.

Container header is `(kind, length)` then the payload. Only kind 0 is read in place; any other kind is counted and
NOT guessed at. Index 0 is transparent in both depths and is excluded from the histogram.

The output is counts only: no ROM bytes are printed or written.
"""

from __future__ import annotations

import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.webfoot.formats import webfoot_lz  # noqa: E402
from tools.research import rom_paths  # noqa: E402

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

image = rom_paths.buu_fury().read_bytes()


def u32(offset: int) -> int | None:
    if offset < 0 or offset + 4 > len(image):
        return None
    return struct.unpack_from("<I", image, offset)[0]


def main() -> int:
    indices = Counter()
    bank_ids: dict[int, set] = defaultdict(set)
    kinds = Counter()
    seen_containers: set[tuple[int, int, int]] = set()
    pieces_8bpp = pieces_4bpp = 0
    pieces_unread = 0
    frames_total = 0
    failures: list = []
    mismatches: list = []

    for identifier in range(MAX_IDS):
        definition = u32(DEFINITION_TABLE + 4 * identifier)
        if definition is None or not (ROM_BASE <= definition < ROM_BASE + len(image)):
            continue
        base = definition - ROM_BASE
        slot_count = image[base]
        if not 1 <= slot_count <= MAX_SLOTS:
            continue
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
                    frames_total += 1
                    for index in range(piece_count):
                        piece = frame_offset + FRAME_HEADER + PIECE_BYTES * index
                        width = image[piece + 2]
                        height = image[piece + 3]
                        attr = u32(piece + 4)
                        container = u32(piece + 8)
                        if attr is None or container is None:
                            continue
                        if (attr >> 13) & 1:
                            pieces_8bpp += 1
                        else:
                            pieces_4bpp += 1
                        if not (ROM_BASE <= container < ROM_BASE + len(image)):
                            pieces_unread += 1
                            continue
                        key = (container, width, height)
                        if key in seen_containers:
                            continue
                        seen_containers.add(key)
                        head = container - ROM_BASE
                        kind, length = struct.unpack_from("<II", image, head)
                        kinds[kind] += 1
                        if (attr >> 13) & 1 == 0:
                            continue
                        # Retail containers are kind 1 (packed), so the payload is decoded with the
                        # project's proven codec rather than read in place. Its absence from the census
                        # was the reason the first run reported every bank free.
                        try:
                            decoded = webfoot_lz.unpack(image, head, maximum_output=1 << 20).data
                        except Exception as error:                      # noqa: BLE001
                            failures.append((container, str(error)[:60]))
                            continue
                        if len(decoded) != width * height:
                            mismatches.append((container, len(decoded), width * height))
                            continue
                        for byte in decoded:
                            if byte:
                                indices[byte] += 1
                                bank_ids[byte // BANK].add(identifier)

    total = sum(indices.values())
    print(f"decode failures {len(failures)} {failures[:3]}; size mismatches {len(mismatches)} "
          f"{mismatches[:3]}")
    print(f"pieces: {pieces_8bpp} 8bpp, {pieces_4bpp} 4bpp, {pieces_unread} unreadable; "
          f"frames {frames_total}; distinct containers {sum(kinds.values())}")
    print(f"container kinds seen: {dict(kinds)}")
    print(f"opaque pixels counted over unique 8bpp containers: {total}")
    print(f"distinct palette indices used: {len(indices)}")

    print("\nper-bank occupancy (index counts, and how many definitions touch it):")
    free = []
    for bank in range(16):
        low, high = bank * BANK, bank * BANK + BANK - 1
        used_index_count = sum(1 for value in indices if low <= value <= high)
        pixels = sum(count for value, count in indices.items() if low <= value <= high)
        ids = sorted(bank_ids[bank])
        if used_index_count == 0:
            free.append(bank)
        print(f"  bank {bank:>2} (indices {low:>3}-{high:>3}): {used_index_count:>2} index(es) used, "
              f"{pixels:>9} pixel(s), {len(ids):>3} definition(s){'' if not ids else ' e.g. ' + str(ids[:6])}")

    print(f"\nFULLY FREE banks: {free}")
    if len(free) < 2:
        print("\nFEWER THAN TWO FULLY FREE BANKS. Closest candidates, by fewest indices used:")
        ranked = sorted(range(16), key=lambda bank: sum(
            1 for value in indices if bank * BANK <= value < bank * BANK + BANK))
        for bank in ranked[:6]:
            low = bank * BANK
            values = sorted(value for value in indices if low <= value < low + BANK)
            pixels = sum(indices[value] for value in values)
            print(f"  bank {bank}: {len(values)} index(es) {values}, {pixels} pixel(s), "
                  f"definitions {sorted(bank_ids[bank])[:10]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
