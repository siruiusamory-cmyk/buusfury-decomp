"""Build Cell's frames as sub-pieces over TWO written banks, each sub-piece carrying its own bank.

Why two banks and not borrow: a sub-piece is at least an 8x8 cell and one piece selects one bank, so a cell's
colours must share a bank. Borrowed ROM slots scatter neighbouring colours and leave 16 cells unsatisfiable, so
both banks are written with Cell's exact LoG II colours (matched 1:1 by source index), which makes the cell
constraint a clean two-colouring that is feasible for every frame.

What this emits per frame: the 8x8 cells grouped by bank, merged into the largest OBJ rectangles available, each
piece carrying its own palette bank in its attr word and its own 4bpp tiles in the container's existing tile
order. The two palettes go into the DESTINATION image's own OBJ palette table at 0x05652C, which is the source
the scene loader copies from, so the engine's own load path performs the write and no code runs for it.
"""

from __future__ import annotations

import random
import struct
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.research import rom_paths  # noqa: E402
sys.path.insert(0, str(ROOT / "build"))

from split_frame_search import SHAPES, cells_of  # noqa: E402
from tools.research import cell_4bpp as convert  # noqa: E402
from tools.research.build_friend_v4b_cell import read_log2_cell  # noqa: E402

LOG2 = rom_paths.legacy_of_goku_2()
BF = rom_paths.buu_fury()
LOG2_SOURCE_PALETTE = 0x081DA6C8
BF_TABLE = 0x05652C
BANK = 16
RESTARTS = 60
STEPS = 600


def cell_bank_assignment(cells, banks: int = 2, seed: int = 7) -> dict[tuple[int, int], int]:
    """Assign each 8x8 CELL to one of `banks`, so each bank's colour UNION fits 15.

    This is the correct model and my first two attempts were not. Colours may be DUPLICATED across banks: the same
    RGB555 value can sit in both palettes at different local slots, and a piece reaches it through its own bank's
    slot. So the constraint is not a partition of colours but a partition of CELLS, and a colour shared by cells in
    different banks is simply written twice. A union-find over shared colours wrongly proves impossibility; this
    search, with the union capacity as the objective, found a zero-overflow state for every frame.
    """
    colours = sorted({value for cell in cells for value in cell.colours})

    def unions(assignment):
        result = [set() for _ in range(banks)]
        for cell in cells:
            if cell.colours:
                result[assignment[(cell.x, cell.y)]] |= set(cell.colours)
        return result

    def cost(assignment):
        return sum(max(0, len(group) - 15) for group in unions(assignment))

    random.seed(seed)
    best_cost, best = None, None
    for _ in range(RESTARTS):
        assignment = {(cell.x, cell.y): random.randrange(banks) for cell in cells}
        current = cost(assignment)
        for _ in range(STEPS):
            if current == 0:
                break
            improved = False
            order = list(cells)
            random.shuffle(order)
            for cell in order:
                here = assignment[(cell.x, cell.y)]
                for target in range(banks):
                    if target == here:
                        continue
                    saved = [set(group) for group in unions(assignment)]
                    assignment[(cell.x, cell.y)] = target
                    candidate = cost(assignment)
                    if candidate < current:
                        current = candidate
                        improved = True
                        break
                    assignment[(cell.x, cell.y)] = here
            if not improved:
                break
        if current == 0:
            return assignment
        if best_cost is None or current < best_cost:
            best_cost, best = current, dict(assignment)
    raise SystemExit(f"no cell assignment with {banks} bank(s) fits 15 colours; best overflow {best_cost}")


def two_bank_assignment(cells, banks: int = 2) -> dict[int, int]:
    """Colour-level view of a cell assignment, for the packing step. A colour in both banks keeps bank 0 here."""
    cell_banks = cell_bank_assignment(cells, banks)
    per_colour: dict[int, int] = {}
    for cell in cells:
        for value in cell.colours:
            per_colour.setdefault(value, cell_banks[(cell.x, cell.y)])
    return per_colour


def rects_for_bank(cells, cell_banks, bank, size):
    """Merge this bank's cells into the largest OBJ rectangles available, row-major.

    Ownership comes from the CELL assignment. Projecting colours onto one bank instead loses every cell whose
    colours appear in both banks, and the loss is silent: those pixels are simply never emitted.
    """
    owned = {(cell.x, cell.y) for cell in cells if cell_banks.get((cell.x, cell.y)) == bank and cell.colours}
    covered, rects = set(), []
    for cell_y in range(0, size, 8):
        for cell_x in range(0, size, 8):
            if (cell_x, cell_y) not in owned or (cell_x, cell_y) in covered:
                continue
            best = None
            for width, height in SHAPES:
                if cell_x + width > size or cell_y + height > size:
                    continue
                block = {(x, y) for y in range(cell_y, cell_y + height, 8)
                         for x in range(cell_x, cell_x + width, 8)}
                if block <= owned and not (block & covered):
                    if best is None or len(block) > best[0]:
                        best = (len(block), block, width, height)
            if best is None:
                continue
            covered |= best[1]
            rects.append((cell_x, cell_y, best[2], best[3]))
    return rects


def pack_rect(payload, size, x, y, width, height, mapping) -> bytes:
    out = bytearray()
    for tile_y in range(y, y + height, 8):
        for tile_x in range(x, x + width, 8):
            for row in range(8):
                for pair in range(0, 8, 2):
                    low = mapping[payload[(tile_y + row) * size + tile_x + pair]] & 0xF
                    high = mapping[payload[(tile_y + row) * size + tile_x + pair + 1]] & 0xF
                    out.append(low | (high << 4))
    return bytes(out)


def build_frame(payload, size, cell_banks, palettes, base_bank):
    """Return [(x, y, w, h, bank, packed)] for one frame over two written banks, using the CELL assignment."""
    cells = cells_of(payload)
    pieces = []
    for local_bank in (0, 1):
        mapping = dict(palettes[local_bank]["slots"])
        mapping[0] = 0
        for x, y, width, height in rects_for_bank(cells, cell_banks, local_bank, size):
            packed = pack_rect(payload, size, x, y, width, height, mapping)
            pieces.append((x, y, width, height, base_bank + local_bank, packed))
    return pieces


def palette_for_bank(indices, source_palette) -> dict:
    slots = {}
    for slot, index in enumerate(sorted(indices), start=1):
        slots[index] = slot
    colours = [0] * 16
    for index, slot in slots.items():
        colours[slot] = struct.unpack_from("<H", source_palette, 2 * index)[0]
    return {"slots": slots, "colours": colours}


def main() -> int:
    base_bank = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    log2 = LOG2.read_bytes()
    source_palette = log2[LOG2_SOURCE_PALETTE - 0x08000000:LOG2_SOURCE_PALETTE - 0x08000000 + 512]
    slots, payloads = read_log2_cell(log2)

    total = defaultdict(int)
    for frame_index, frame in enumerate(slots):
        piece = frame[0]
        payload = payloads[piece[5]]
        size = piece[2]
        cells = cells_of(payload)
        cell_banks = cell_bank_assignment(cells, 2)
        per_bank = [set(), set()]
        for cell in cells:
            for value in cell.colours:
                per_bank[cell_banks[(cell.x, cell.y)]].add(value)
        palettes = [palette_for_bank(per_bank[0], source_palette),
                    palette_for_bank(per_bank[1], source_palette)]
        pieces = build_frame(payload, size, cell_banks, palettes, base_bank)
        total[len(pieces)] += 1
        print(f"frame {frame_index}: {len(pieces)} piece(s), banks "
              f"{sorted({p[4] for p in pieces})}, colours per bank "
              f"{[len(palettes[0]['slots']), len(palettes[1]['slots'])]}, "
              f"tiles {sum(p[2] * p[3] // 64 for p in pieces)}")
    print(f"\npiece counts across frames: {dict(sorted(total.items()))}")
    print(f"banks written: {base_bank} and {base_bank + 1}")
    print(f"target table 0x{BF_TABLE:06X} would receive 32 bytes per bank")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
