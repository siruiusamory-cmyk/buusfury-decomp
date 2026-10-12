"""A rigorous certificate for joint-palette infeasibility, or else evidence that it is feasible.

Two 15-colour banks can hold all the colours of any two cells whose union is at most 15. If three cells exist such
that EVERY PAIR of them unions to more than 15, then no two of them can share a bank, so they need three banks and
the joint pair is impossible. That is a proof, not a search result, and it does not depend on any heuristic.

If no such triple exists, this reports that instead, so a heuristic failure is never presented as a proof.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.research import rom_paths  # noqa: E402
sys.path.insert(0, str(ROOT / "build"))

from split_frame_search import cells_of  # noqa: E402
from tools.research.build_friend_v4b_cell import read_log2_cell  # noqa: E402

LOG2 = rom_paths.legacy_of_goku_2()
CAPACITY = 15


def main() -> int:
    log2 = LOG2.read_bytes()
    slots, payloads = read_log2_cell(log2)
    cells = []
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        for cell in cells_of(payload):
            if cell.colours:
                cells.append((frame_index, cell.x, cell.y, frozenset(cell.colours)))
    print(f"{len(cells)} populated cell(s), largest {max(len(c[3]) for c in cells)} colour(s)")

    # Distinct colour sets only: duplicates add nothing to the certificate.
    unique = {}
    for frame_index, x, y, colours in cells:
        unique.setdefault(colours, (frame_index, x, y))
    sets = list(unique)
    print(f"{len(sets)} distinct colour set(s)")

    pairs_over = {}
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            union = len(sets[i] | sets[j])
            if union > CAPACITY:
                pairs_over[(i, j)] = union
    print(f"{len(pairs_over)} pair(s) whose union exceeds {CAPACITY}")

    # Look for a triple with all three pairs over capacity.
    neighbours = {}
    for (i, j) in pairs_over:
        neighbours.setdefault(i, set()).add(j)
        neighbours.setdefault(j, set()).add(i)
    for i, first in neighbours.items():
        for j in first:
            common = first & neighbours.get(j, set())
            if common:
                k = sorted(common)[0]
                print("\nCERTIFICATE FOUND: three cells, every pair over capacity, so they need three banks")
                for label, index in (("A", i), ("B", j), ("C", k)):
                    frame_index, x, y = unique[sets[index]]
                    print(f"  {label}: frame {frame_index} cell ({x},{y}), {len(sets[index])} colour(s) "
                          f"{sorted(sets[index])}")
                print(f"  unions: {len(sets[i] | sets[j])}, {len(sets[i] | sets[k])}, "
                      f"{len(sets[j] | sets[k])} (capacity {CAPACITY})")
                return 0

    print("\nNO CERTIFICATE: no triple has all three pairs over capacity, so this does not prove infeasibility")
    biggest = max(pairs_over.values()) if pairs_over else 0
    print(f"largest pair union seen: {biggest}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
