"""Exact answer: how many written banks does each frame need, given cell locality?

The constraint is not a search problem. Each colour lives in exactly ONE bank, and each 8x8 cell's colours must all
be in that cell's bank. So if two cells share any colour, every colour of both must share one bank: the cells
form connected components under "shares a colour", and each component's colour set must fit one 15-colour bank.

That makes the answer exact: the components are fixed, and the bank count is the number needed to pack the
component colour sets into banks of 15.
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


def components(cells) -> list[set]:
    """Union cells that share a colour, so each component's colours must share one bank."""
    parent: dict[int, int] = {}

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for cell in cells:
        for value in cell.colours:
            parent.setdefault(value, value)
    for cell in cells:
        values = sorted(cell.colours)
        for other in values[1:]:
            union(values[0], other)

    groups: dict[int, set] = {}
    for value in parent:
        groups.setdefault(find(value), set()).add(value)
    return sorted(groups.values(), key=len, reverse=True)


def pack(groups: list[set]) -> int:
    """First-fit-decreasing: the number of 15-colour banks needed for these component sets."""
    bins: list[set] = []
    for group in sorted(groups, key=len, reverse=True):
        if len(group) > CAPACITY:
            return -1
        for existing in bins:
            if len(existing | group) <= CAPACITY:
                existing |= group
                break
        else:
            bins.append(set(group))
    return len(bins)


def main() -> int:
    log2 = LOG2.read_bytes()
    slots, payloads = read_log2_cell(log2)
    worst = 0
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        cells = [cell for cell in cells_of(payload) if cell.colours]
        groups = components(cells)
        banks = pack(groups)
        worst = max(worst, banks)
        too_big = [len(group) for group in groups if len(group) > CAPACITY]
        print(f"frame {frame_index}: {len(set(payload) - {0})} colour(s), {len(cells)} populated cell(s), "
              f"{len(groups)} forced group(s) of sizes {[len(g) for g in groups]}, banks needed {banks}"
              f"{'' if not too_big else '  A GROUP EXCEEDS CAPACITY ' + str(too_big)}")
    print(f"\nworst frame needs {worst} written bank(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
