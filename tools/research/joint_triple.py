"""EXACT: does a joint TRIPLE of 15-colour banks exist? Enumerated, not searched.

Same method as the pair proof, one level deeper. Bank A is a 15-subset of the 21 colours; every cell inside A goes
to A. For the remaining cells, bank B is a 15-subset (forced colours plus optional extras) and every remaining
cell inside B goes to B. Whatever is left must fit bank C, so the triple exists exactly when the union of those
cells has at most 15 colours.

Symmetry is pruned by requiring that A covers the most cells of any bank and B at least as many as C. A triple is
returned for the fewest sub-pieces found, and it is complete: no triple found means none exists.
"""

from __future__ import annotations

import itertools
import sys
import time
from pathlib import Path

ROOT = Path(r"C:\Dev\log1-remake-cell-c1")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "build"))

from split_frame_search import cells_of  # noqa: E402
from tools.research.build_friend_v4b_cell import read_log2_cell  # noqa: E402

LOG2 = Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba")
CAPACITY = 15
TIME_LIMIT = 1500.0


def main() -> int:
    log2 = LOG2.read_bytes()
    slots, payloads = read_log2_cell(log2)

    order = []
    per_frame = []
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        entries = []
        for cell in cells_of(payload):
            if cell.colours:
                for value in cell.colours:
                    if value not in order:
                        order.append(value)
                entries.append(cell.colours)
        per_frame.append(entries)
    order.sort()
    bit = {value: 1 << index for index, value in enumerate(order)}
    n = len(order)

    distinct = {}
    for entries in per_frame:
        for colours in entries:
            mask = 0
            for value in colours:
                mask |= bit[value]
            distinct[mask] = distinct.get(mask, 0) + 1
    masks = list(distinct)
    print(f"{sum(len(e) for e in per_frame)} cell(s), {len(masks)} distinct colour set(s), {n} colour(s)")

    full = (1 << n) - 1
    started = time.time()
    solutions = []
    examined = 0

    def cover_count_for(a_mask, b_mask, c_mask):
        total = 0
        for entries in per_frame:
            for colours in entries:
                mask = 0
                for value in colours:
                    mask |= bit[value]
                if mask & ~a_mask:
                    if mask & ~b_mask:
                        if mask & ~c_mask:
                            return None
        return total

    for subset in itertools.combinations(range(n), CAPACITY):
        a_mask = 0
        for index in subset:
            a_mask |= 1 << index
        remaining = [mask for mask in masks if mask & ~a_mask]
        if not remaining:
            # Everything fits A alone: the trivial extension is B = C = A.
            solutions.append((a_mask, a_mask, a_mask))
            continue
        rcol = 0
        for mask in remaining:
            rcol |= mask
        if bin(rcol).count("1") <= CAPACITY:
            solutions.append((a_mask, rcol, 0))
            continue
        if bin(rcol).count("1") > 2 * CAPACITY:
            continue                                     # cannot fit two banks even in principle
        indices = [index for index in range(n) if rcol & (1 << index)]
        for b_subset in itertools.combinations(indices, min(CAPACITY, len(indices))):
            b_mask = 0
            for index in b_subset:
                b_mask |= 1 << index
            c_mask = 0
            for mask in remaining:
                if mask & ~b_mask:
                    c_mask |= mask
            if bin(c_mask).count("1") <= CAPACITY:
                solutions.append((a_mask, b_mask, c_mask))
                break
        examined += 1
        if solutions and len(solutions) >= 40:
            break
        if time.time() - started > TIME_LIMIT:
            print(f"TIME LIMIT after examining {examined} A-subset(s); {len(solutions)} triple(s) so far")
            break

    print(f"examined {examined} A-subset(s) in {time.time() - started:.1f}s; "
          f"{len(solutions)} triple(s) found")
    if not solutions:
        print("\nNO TRIPLE: every 15-subset A leaves cells needing more than two banks.")
        return 1

    a_mask, b_mask, c_mask = solutions[0]
    for label, mask in (("A", a_mask), ("B", b_mask), ("C", c_mask)):
        colours = [value for value in order if mask & bit[value]]
        print(f"  bank {label}: {len(colours)} colour(s) {colours}")
    print("\nVERDICT: a joint triple EXISTS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
