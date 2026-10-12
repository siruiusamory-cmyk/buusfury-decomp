"""ONE joint colour-to-bank assignment for all eight frames, then verify every frame through it.

The engine animates frames and a runtime writer cannot cheaply know which one is showing, so the character needs a
SINGLE pair of 15-colour palettes, not a pair per frame. Cells are assigned to logical banks across all frames at
once, each bank's union of source colours must fit 15, and duplication is allowed: a colour used by cells in both
banks is simply written into both.

Then the structural proof is repeated per frame THROUGH THE JOINT PALETTES: reassembling the sub-pieces must
reproduce the source frame at every one of the 4096 pixels, by exact RGB555.
"""

from __future__ import annotations

import random
import struct
import sys
from pathlib import Path

ROOT = Path(r"C:\Dev\log1-remake-cell-c1")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "build"))

from build_two_bank_split import build_frame, pack_rect, rects_for_bank  # noqa: E402
from split_frame_search import cells_of  # noqa: E402
from tools.research.build_friend_v4b_cell import read_log2_cell  # noqa: E402

LOG2 = Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba")
LOG2_SOURCE_PALETTE = 0x081DA6C8
RESTARTS = 400
STEPS = 4000
CAPACITY = 15
OUT = Path(r"C:\Dev\log1-remake-cell-c1\build\joint_palettes.json")


def search(all_cells) -> dict[tuple[int, int, int], int]:
    """Assign every (frame, x, y) cell to bank 0 or 1 so both banks' colour unions fit `CAPACITY`."""

    def unions(assignment):
        result = [set(), set()]
        for key, colours in all_cells.items():
            result[assignment[key]] |= colours
        return result

    def cost(assignment):
        return sum(max(0, len(group) - CAPACITY) for group in unions(assignment))

    keys = list(all_cells)
    random.seed(11)
    best_cost, best = None, None
    for _ in range(RESTARTS):
        assignment = {key: random.randrange(2) for key in keys}
        current = cost(assignment)
        for _ in range(STEPS):
            if current == 0:
                break
            improved = False
            order = keys[:]
            random.shuffle(order)
            for key in order:
                here = assignment[key]
                target = 1 - here
                assignment[key] = target
                candidate = cost(assignment)
                if candidate < current:
                    current = candidate
                    improved = True
                    break
                assignment[key] = here
            if not improved:
                break
        if current == 0:
            return assignment
        if best_cost is None or current < best_cost:
            best_cost, best = current, dict(assignment)
    raise SystemExit(f"NO JOINT ASSIGNMENT: best overflow {best_cost} colour(s) over capacity "
                     f"with {len(all_cells)} cell(s)")


def main() -> int:
    log2 = LOG2.read_bytes()
    source_palette = log2[LOG2_SOURCE_PALETTE - 0x08000000:LOG2_SOURCE_PALETTE - 0x08000000 + 512]
    slots, payloads = read_log2_cell(log2)

    all_cells: dict[tuple[int, int, int], frozenset] = {}
    per_frame_payload = []
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        per_frame_payload.append(payload)
        for cell in cells_of(payload):
            if cell.colours:
                all_cells[(frame_index, cell.x, cell.y)] = cell.colours
    print(f"{len(all_cells)} populated cell(s) over {len(slots)} frame(s)")

    assignment = search(all_cells)
    groups = [set(), set()]
    for key, colours in all_cells.items():
        groups[assignment[key]] |= colours
    print(f"joint palettes: {len(groups[0])} and {len(groups[1])} colour(s) of {CAPACITY} usable")
    if max(len(group) for group in groups) > CAPACITY:
        print("STOP: joint palettes do not fit")
        return 1

    # Local slots per bank: slot 1 upward, transparent 0.
    local = []
    colours = []
    for group in groups:
        mapping = {value: slot for slot, value in enumerate(sorted(group), start=1)}
        local.append(mapping)
        entry = [0] * 16
        for value, slot in mapping.items():
            entry[slot] = struct.unpack_from("<H", source_palette, 2 * value)[0]
        colours.append(entry)

    total_diff = 0
    total_pieces = 0
    for frame_index, payload in enumerate(per_frame_payload):
        size = slots[frame_index][0][2]
        cells = cells_of(payload)
        cell_banks = {(cell.x, cell.y): assignment[(frame_index, cell.x, cell.y)]
                      for cell in cells if cell.colours}
        palettes = [{"slots": local[0], "colours": colours[0]},
                    {"slots": local[1], "colours": colours[1]}]
        pieces = build_frame(payload, size, cell_banks, palettes, 0)
        total_pieces += len(pieces)

        rendered: dict[tuple[int, int], int] = {}
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

    print(f"\n{total_pieces} piece(s) total; differing pixels across all frames: {total_diff}")
    print("VERDICT:", "zero colour loss through the JOINT palettes" if total_diff == 0 else "LOSS DETECTED")
    if total_diff == 0:
        import json
        OUT.write_text(json.dumps({
            "palette_a": [f"0x{value:04X}" for value in colours[0]],
            "palette_b": [f"0x{value:04X}" for value in colours[1]],
            "slot_map_a": {str(key): value for key, value in local[0].items()},
            "slot_map_b": {str(key): value for key, value in local[1].items()},
        }, indent=2), encoding="utf-8")
        print(f"joint palettes and slot maps written to {OUT}")
    return 0 if total_diff == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
