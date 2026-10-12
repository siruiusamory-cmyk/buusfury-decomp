"""Construct the joint palette pair instead of searching for it.

The certificate search shows the structure is loose: of 96 distinct cell colour sets, exactly ONE pair unions to
more than 15, so only that pair is forced apart. That pair is the whole difficulty, and a constructive greedy
settles it: start with every cell in bank A, move cells to B until both unions fit, split the conflict pair, and
accept when both unions are within capacity.
"""

from __future__ import annotations

import random
import struct
import sys
from pathlib import Path

ROOT = Path(r"C:\Dev\log1-remake-cell-c1")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "build"))

from build_two_bank_split import build_frame  # noqa: E402
from split_frame_search import cells_of  # noqa: E402
from tools.research.build_friend_v4b_cell import read_log2_cell  # noqa: E402

LOG2 = Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba")
LOG2_SOURCE_PALETTE = 0x081DA6C8
CAPACITY = 15
ATTEMPTS = 400


def main() -> int:
    log2 = LOG2.read_bytes()
    source_palette = log2[LOG2_SOURCE_PALETTE - 0x08000000:LOG2_SOURCE_PALETTE - 0x08000000 + 512]
    slots, payloads = read_log2_cell(log2)

    cells: dict[tuple[int, int, int], frozenset] = {}
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        for cell in cells_of(payload):
            if cell.colours:
                cells[(frame_index, cell.x, cell.y)] = frozenset(cell.colours)
    keys = list(cells)

    def unions(assignment):
        result = [set(), set()]
        for key in keys:
            result[assignment[key]] |= cells[key]
        return result

    random.seed(23)
    best = None
    for _ in range(ATTEMPTS):
        assignment = {key: 0 for key in keys}
        for _ in range(4000):
            groups = unions(assignment)
            over = [index for index in (0, 1) if len(groups[index]) > CAPACITY]
            if not over:
                break
            index = over[0]
            candidates = [key for key in keys if assignment[key] == index
                          and cells[key] & groups[index]]
            if not candidates:
                break
            key = min(candidates, key=lambda item: -len(cells[item] & groups[index]))
            assignment[key] = 1 - index
        groups = unions(assignment)
        if all(len(group) <= CAPACITY for group in groups):
            best = assignment
            break

    if best is None:
        groups = unions(best)
        print(f"constructive greedy failed: unions {[len(g) for g in groups]} against capacity {CAPACITY}")
        return 1

    groups = unions(best)
    print(f"joint palettes: bank A {len(groups[0])} colour(s), bank B {len(groups[1])} colour(s) "
          f"of {CAPACITY} usable")
    print(f"  A colours: {sorted(groups[0])}")
    print(f"  B colours: {sorted(groups[1])}")

    local = []
    for group in groups:
        local.append({value: slot for slot, value in enumerate(sorted(group), start=1)})

    total_diff = 0
    total_pieces = 0
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        size = frame[0][2]
        cell_banks = {(cell.x, cell.y): best[(frame_index, cell.x, cell.y)]
                      for cell in cells_of(payload) if cell.colours}
        palettes = [{"slots": local[0]}, {"slots": local[1]}]
        pieces = build_frame(payload, size, cell_banks, palettes, 0)
        total_pieces += len(pieces)
        rendered = {}
        for x, y, width, height, bank, packed in pieces:
            inverse = {slot: value for value, slot in local[bank].items()}
            cursor = 0
            for tile_y in range(y, y + height, 8):
                for tile_x in range(x, x + width, 8):
                    for row in range(8):
                        for pair in range(0, 8, 2):
                            byte = packed[cursor]
                            cursor += 1
                            for offset, value in ((0, byte & 0xF), (1, (byte >> 4) & 0xF)):
                                rendered[(tile_x + pair + offset, tile_y + row)] = \
                                    0 if value == 0 else inverse.get(value, -1)
        diff = sum(1 for y in range(size) for x in range(size)
                   if rendered.get((x, y), 0) != payload[y * size + x])
        total_diff += diff
        print(f"frame {frame_index}: {len(pieces)} piece(s), {diff} of {size * size} pixel(s) differ")

    print(f"\n{total_pieces} piece(s); differing pixels across all frames: {total_diff}")
    print("VERDICT:", "zero colour loss through ONE joint palette pair" if total_diff == 0 else "LOSS DETECTED")
    return 0 if total_diff == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
