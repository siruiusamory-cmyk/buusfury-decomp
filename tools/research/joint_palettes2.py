"""Joint palettes, searched in the model that matches the hardware.

A colour may be in bank A, in bank B, or in BOTH (duplication). A cell is drawable if all its colours are in the
bank it is assigned to. So the real variables are the 21 colours, each with three states, and the constraints are
that each union holds at most 15 colours and every cell is contained in some bank.

The cell-level search was the wrong parameterisation: it cannot duplicate a colour on the side that needs it
without also moving cells. This reports the best state it can reach and, if it cannot reach zero, the cells that
pin the infeasibility.
"""

from __future__ import annotations

import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\Dev\log1-remake-cell-c1")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "build"))

from split_frame_search import cells_of  # noqa: E402
from tools.research.build_friend_v4b_cell import read_log2_cell  # noqa: E402

LOG2 = Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba")
CAPACITY = 15
ONLY_A, ONLY_B, BOTH = 0, 1, 2
RESTARTS = 200
STEPS = 4000


def main() -> int:
    log2 = LOG2.read_bytes()
    slots, payloads = read_log2_cell(log2)
    cells = []
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        for cell in cells_of(payload):
            if cell.colours:
                cells.append(frozenset(cell.colours))
    colours = sorted({value for cell in cells for value in cell})
    print(f"{len(cells)} cell(s), {len(colours)} colour(s)")

    def evaluate(state):
        union_a = {value for value in colours if state[value] in (ONLY_A, BOTH)}
        union_b = {value for value in colours if state[value] in (ONLY_B, BOTH)}
        overflow = max(0, len(union_a) - CAPACITY) + max(0, len(union_b) - CAPACITY)
        uncovered = 0
        worst = None
        for cell in cells:
            in_a = cell <= union_a
            in_b = cell <= union_b
            if not (in_a or in_b):
                uncovered += 1
                if worst is None or len(cell) > len(worst):
                    worst = cell
        return overflow * 1000 + uncovered, overflow, uncovered, worst

    random.seed(13)
    best = None
    for _ in range(RESTARTS):
        state = {value: random.choice((ONLY_A, ONLY_B, BOTH)) for value in colours}
        current = evaluate(state)[0]
        for _ in range(STEPS):
            if current == 0:
                break
            improved = False
            order = colours[:]
            random.shuffle(order)
            for value in order:
                for target in (ONLY_A, ONLY_B, BOTH):
                    if target == state[value]:
                        continue
                    previous = state[value]
                    state[value] = target
                    candidate = evaluate(state)[0]
                    if candidate < current:
                        current = candidate
                        improved = True
                        break
                    state[value] = previous
                if improved:
                    break
            if not improved:
                break
        score, overflow, uncovered, worst = evaluate(state)
        if score == 0:
            union_a = sorted(value for value in colours if state[value] in (ONLY_A, BOTH))
            union_b = sorted(value for value in colours if state[value] in (ONLY_B, BOTH))
            print(f"FEASIBLE: bank A holds {len(union_a)} colour(s), bank B {len(union_b)}")
            print(f"  A-only: {[v for v in colours if state[v] == ONLY_A]}")
            print(f"  B-only: {[v for v in colours if state[v] == ONLY_B]}")
            print(f"  both:   {[v for v in colours if state[v] == BOTH]}")
            return 0
        if best is None or score < best[0]:
            best = (score, overflow, uncovered, worst, dict(state))

    score, overflow, uncovered, worst, state = best
    print(f"\nNO FEASIBLE JOINT PAIR. best state: overflow {overflow}, uncovered cells {uncovered}")
    print(f"  the largest uncoverable cell has {len(worst)} colour(s): {sorted(worst)}")
    for value in sorted(worst):
        print(f"    colour {value}: state {['only A', 'only B', 'both'][state[value]]}")
    print("  a cell needing more colours than one bank holds cannot be drawn even with duplication:")
    print(f"  the largest cell anywhere has {max(len(cell) for cell in cells)} colour(s)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
