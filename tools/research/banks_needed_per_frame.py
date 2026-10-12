"""How many written banks does each frame ACTUALLY need, once cell locality and bank capacity both count?

The earlier "two banks suffice" measurement was wrong: it checked that no bank's colour union exceeded 15 but not
that each 8x8 cell's colours share one bank. A cell is the smallest sub-piece, so locality is the binding
constraint, and this reports the smallest bank count that satisfies both, per frame.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"C:\Dev\log1-remake-cell-c1")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "build"))

from build_two_bank_split import two_bank_assignment  # noqa: E402
from split_frame_search import cells_of, cover_count  # noqa: E402
from tools.research.build_friend_v4b_cell import read_log2_cell  # noqa: E402

LOG2 = Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba")


def main() -> int:
    log2 = LOG2.read_bytes()
    slots, payloads = read_log2_cell(log2)
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        cells = cells_of(payload)
        line = f"frame {frame_index}: {len(set(payload) - {0})} colour(s) "
        for banks in (2, 3, 4):
            try:
                assignment = two_bank_assignment(cells, banks)
            except SystemExit as error:
                line += f"| {banks} banks FAIL ({str(error).split(';')[-1].strip()}) "
                continue
            cell_bank = {(cell.x, cell.y): (assignment[sorted(cell.colours)[0]] if cell.colours else 0)
                         for cell in cells}
            counts = [cover_count(cells, cell_bank, bank) for bank in range(banks)]
            sizes = [0] * banks
            for value in set(payload) - {0}:
                sizes[assignment[value]] += 1
            nonempty = [count for count, size in zip(counts, sizes) if size]
            line += f"| {banks} banks OK, {sum(nonempty)} piece(s) {nonempty}, colours {[s for s in sizes if s]} "
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
