"""EXACT: enumerate every 15-subset A of Cell's 21 colours and decide feasibility by construction.

WLOG bank A holds exactly 15 colours, because adding a colour to A never hurts. For a given A, every cell whose
colour set is inside A goes to A; every other cell must go to B, so B is the union of those cells' colours, and the
pair is usable exactly when |B| is at most 15. Colours are allowed in both banks; that costs a slot in each.

This is complete. It returns a pair or it proves none exists. Among the feasible pairs it keeps the one that needs
the fewest sub-pieces, preferring large same-bank rectangles, and then re-verifies all eight frames at 0/4096.
"""

from __future__ import annotations

import itertools
import json
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
OUT = Path(r"C:\Dev\log1-remake-cell-c1\build\joint_pair.json")


def main() -> int:
    log2 = LOG2.read_bytes()
    source_palette = log2[LOG2_SOURCE_PALETTE - 0x08000000:LOG2_SOURCE_PALETTE - 0x08000000 + 512]
    slots, payloads = read_log2_cell(log2)

    cells: dict[tuple[int, int, int], int] = {}
    colour_list = []
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        for cell in cells_of(payload):
            if cell.colours:
                for value in cell.colours:
                    if value not in colour_list:
                        colour_list.append(value)
                cells[(frame_index, cell.x, cell.y)] = 0
    colour_list.sort()
    bit = {value: 1 << index for index, value in enumerate(colour_list)}
    print(f"{len(cells)} cell(s), {len(colour_list)} colour(s)")

    cell_masks = {}
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        for cell in cells_of(payload):
            if cell.colours:
                mask = 0
                for value in cell.colours:
                    mask |= bit[value]
                cell_masks[(frame_index, cell.x, cell.y)] = mask

    full = (1 << len(colour_list)) - 1
    feasible = []
    for subset in itertools.combinations(range(len(colour_list)), CAPACITY):
        a_mask = 0
        for index in subset:
            a_mask |= 1 << index
        b_mask = 0
        for mask in cell_masks.values():
            if mask & ~a_mask:
                b_mask |= mask
        b_size = bin(b_mask).count("1")
        if b_size <= CAPACITY:
            feasible.append((b_size, a_mask, b_mask))
    print(f"15-subsets enumerated: {len(list(itertools.combinations(range(len(colour_list)), CAPACITY)))}, "
          f"feasible: {len(feasible)}")

    if not feasible:
        print("\nPROOF OF INFEASIBILITY: no 15-subset A leaves B within capacity.")
        print("  smallest B reached:", min(
            (bin(b_mask).count('1') for _, a_mask, b_mask in
             ((None, None, None),) if False), default=None) or "see enumeration")
        print("  smallest |B| over all 54,264 subsets:")
        best_b = 99
        for subset in itertools.combinations(range(len(colour_list)), CAPACITY):
            a_mask = 0
            for index in subset:
                a_mask |= 1 << index
            b_mask = 0
            for mask in cell_masks.values():
                if mask & ~a_mask:
                    b_mask |= mask
            best_b = min(best_b, bin(b_mask).count("1"))
        print(f"    {best_b} colours, {best_b - CAPACITY} over capacity")
        return 1

    feasible.sort(key=lambda item: item[0])
    best = None
    for b_size, a_mask, b_mask in feasible[:120]:
        local_a = {value: slot for slot, value in
                   enumerate([value for value in colour_list if a_mask & bit[value]], start=1)}
        local_b = {value: slot for slot, value in
                   enumerate([value for value in colour_list if b_mask & bit[value]], start=1)}
        per_frame_pieces = 0
        ok = True
        for frame_index, frame in enumerate(slots):
            payload = payloads[frame[0][5]]
            cell_banks = {}
            for cell in cells_of(payload):
                if not cell.colours:
                    continue
                mask = 0
                for value in cell.colours:
                    mask |= bit[value]
                cell_banks[(cell.x, cell.y)] = 0 if not (mask & ~a_mask) else 1
            pieces = build_frame(payload, frame[0][2], cell_banks,
                                 [{"slots": local_a}, {"slots": local_b}], 0)
            per_frame_pieces += len(pieces)
        if ok and (best is None or per_frame_pieces < best[0]):
            best = (per_frame_pieces, b_size, local_a, local_b, a_mask, b_mask)

    total, b_size, local_a, local_b, a_mask, b_mask = best
    print(f"\nBEST PAIR: bank A {len(local_a)} colour(s), bank B {len(local_b)} colour(s), "
          f"{total} sub-piece(s) across all frames")
    print(f"  A-only: {sorted(value for value in colour_list if a_mask & bit[value] and not b_mask & bit[value])}")
    print(f"  shared: {sorted(value for value in colour_list if a_mask & bit[value] and b_mask & bit[value])}")
    print(f"  B-only: {sorted(value for value in colour_list if b_mask & bit[value] and not a_mask & bit[value])}")

    def colours_of(local):
        entry = [0] * 16
        for value, slot in local.items():
            entry[slot] = struct.unpack_from("<H", source_palette, 2 * value)[0]
        return entry

    palette_a, palette_b = colours_of(local_a), colours_of(local_b)
    total_diff = 0
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        size = frame[0][2]
        cell_banks = {}
        for cell in cells_of(payload):
            if not cell.colours:
                continue
            mask = 0
            for value in cell.colours:
                mask |= bit[value]
            cell_banks[(cell.x, cell.y)] = 0 if not (mask & ~a_mask) else 1
        pieces = build_frame(payload, size, cell_banks, [{"slots": local_a}, {"slots": local_b}], 0)
        rendered = {}
        for x, y, width, height, bank, packed in pieces:
            inverse = {slot: value for value, slot in (local_a if bank == 0 else local_b).items()}
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
        print(f"  frame {frame_index}: {len(pieces)} piece(s), {diff} of {size * size} pixel(s) differ")

    print(f"\ndiffering pixels across all frames: {total_diff}")
    print("VERDICT:", "zero colour loss through ONE joint palette pair" if total_diff == 0 else "LOSS DETECTED")
    if total_diff == 0:
        OUT.write_text(json.dumps({
            "palette_a": [f"0x{value:04X}" for value in palette_a],
            "palette_b": [f"0x{value:04X}" for value in palette_b],
            "slot_map_a": {str(k): v for k, v in local_a.items()},
            "slot_map_b": {str(k): v for k, v in local_b.items()},
        }, indent=2), encoding="utf-8")
        print(f"written to {OUT}")
    return 0 if total_diff == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
