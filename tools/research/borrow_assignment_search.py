"""Search for a bank assignment where every 8x8 cell's colours share ONE bank.

Borrow by value alone scatters neighbouring colours (58 cells spanned up to four banks). The freedom that fixes it
is that a colour often exists in several ROM banks, and any colour may instead live in the written bank 14 if it
has a slot there. So this is a constrained colouring: colours that share a cell must share a bank, bank 14 holds
at most 15 colours, and every other bank may only host colours whose exact RGB555 value it already contains.

Local search with restarts; the objective is the number of cells whose colours span more than one bank, and a
feasible state has zero.
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

LOG2 = rom_paths.legacy_of_goku_2()
BF = rom_paths.buu_fury()
LOG2_SOURCE_PALETTE = 0x081DA6C8
BF_TABLE = 0x05652C
WRITTEN_BANK = 14
BANK = 16
WRITTEN_CAPACITY = 15
RESTARTS = 200
STEPS = 2000

log2 = LOG2.read_bytes()
bf = BF.read_bytes()


def load():
    from tools.research.build_friend_v4b_cell import read_log2_cell
    slots, payloads = read_log2_cell(log2)
    source_palette = log2[LOG2_SOURCE_PALETTE - 0x08000000:LOG2_SOURCE_PALETTE - 0x08000000 + 512]
    table = bf[BF_TABLE:BF_TABLE + 512]

    value_to_banks: dict[int, set] = defaultdict(set)
    for slot in range(256):
        value_to_banks[struct.unpack_from("<H", table, 2 * slot)[0]].add(slot // BANK)

    cells = []
    colours = set()
    for frame in slots:
        payload = payloads[frame[0][5]]
        size = frame[0][2]
        for cell_y in range(0, size, 8):
            for cell_x in range(0, size, 8):
                present = set()
                for row in range(8):
                    for column in range(8):
                        value = payload[(cell_y + row) * size + cell_x + column]
                        if value:
                            present.add(value)
                if present:
                    cells.append(frozenset(present))
                    colours |= present
    options = {}
    for index in colours:
        value = struct.unpack_from("<H", source_palette, 2 * index)[0]
        banks = {bank for bank in value_to_banks.get(value, set()) if bank != WRITTEN_BANK}
        banks.add(WRITTEN_BANK)
        options[index] = sorted(banks)
    return cells, sorted(colours), options


def violations(cells, assignment):
    bad = 0
    for cell in cells:
        if len({assignment[index] for index in cell}) > 1:
            bad += 1
    return bad


def main() -> int:
    cells, colours, options = load()
    print(f"{len(cells)} populated 8x8 cells, {len(colours)} colours")
    written_only = [index for index in colours if options[index] == [WRITTEN_BANK]]
    print(f"colours that can ONLY live in the written bank: {len(written_only)} {written_only}")
    if len(written_only) > WRITTEN_CAPACITY:
        print("INFEASIBLE: more must-write colours than the bank holds")
        return 1

    random.seed(20261012)
    best = None
    for _ in range(RESTARTS):
        assignment = {index: random.choice(options[index]) for index in colours}
        current = violations(cells, assignment)
        for _ in range(STEPS):
            if current == 0:
                break
            moved = False
            order = list(colours)
            random.shuffle(order)
            for index in order:
                for bank in options[index]:
                    if bank == assignment[index]:
                        continue
                    previous = assignment[index]
                    assignment[index] = bank
                    candidate = violations(cells, assignment)
                    written = sum(1 for value in assignment.values() if value == WRITTEN_BANK)
                    if candidate <= current and written <= WRITTEN_CAPACITY:
                        if candidate < current:
                            current = candidate
                            moved = True
                        break
                    assignment[index] = previous
                if moved:
                    break
            if not moved:
                break
        if current == 0:
            written = sorted(index for index, bank in assignment.items() if bank == WRITTEN_BANK)
            used = sorted({bank for bank in assignment.values()})
            best = (assignment, used, written)
            break
        if best is None or current < best[0]:
            best = (current, assignment)

    if best and isinstance(best[0], int):
        print(f"no feasible assignment found; best state still has {best[0]} bad cell(s)")
        return 1
    assignment, used, written = best
    print(f"FEASIBLE: every cell fits one bank")
    print(f"banks used: {used}")
    print(f"written bank {WRITTEN_BANK} holds {len(written)} colour(s): {written}")
    per_bank = defaultdict(int)
    for index, bank in assignment.items():
        per_bank[bank] += 1
    print(f"colours per bank: {dict(sorted(per_bank.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
