"""With a joint pair proven impossible, what is the smallest loss?

No 15-subset of the 21 colours leaves B within 15: the best leaves 17, two over. So a single joint pair must drop
at least two colours from bank B. This picks the pair of colours whose loss costs the fewest pixels, over all
frames, and reports the count. It also reports the per-frame alternative, which was already proven lossless.
"""

from __future__ import annotations

import itertools
import sys
from collections import Counter
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

    colour_list = []
    frames = []
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        frames.append(payload)
        for value in sorted(set(payload) - {0}):
            if value not in colour_list:
                colour_list.append(value)
    colour_list.sort()
    bit = {value: 1 << index for index, value in enumerate(colour_list)}

    cells_by_frame = []
    for payload in frames:
        entry = []
        for cell in cells_of(payload):
            if cell.colours:
                mask = 0
                for value in cell.colours:
                    mask |= bit[value]
                entry.append(((cell.x, cell.y), mask))
        cells_by_frame.append(entry)

    best = None
    for subset in itertools.combinations(range(len(colour_list)), CAPACITY):
        a_mask = 0
        for index in subset:
            a_mask |= 1 << index
        b_mask = 0
        b_colours = set()
        for entry in cells_by_frame:
            for _, mask in entry:
                if mask & ~a_mask:
                    b_mask |= mask
                    for value in colour_list:
                        if mask & bit[value]:
                            b_colours.add(value)
        size = bin(b_mask).count("1")
        if best is None or size < best[0]:
            best = (size, a_mask, b_colours)
    size, a_mask, b_colours = best
    print(f"smallest bank B over all 54,264 subsets: {size} colour(s)")

    # Which B colours are cheapest to drop, counted in pixels over all frames?
    pixel_counts = Counter()
    for payload in frames:
        for value in set(payload) - {0}:
            pixel_counts[value] += payload.count(value)
    b_only = sorted(b_colours, key=lambda value: pixel_counts[value])
    excess = size - CAPACITY
    drop = b_only[:excess]
    print(f"excess colour(s) to drop: {excess}")
    for value in drop:
        print(f"  drop colour {value}: {pixel_counts[value]} pixel(s) across all frames")
    # Only pixels in cells that actually use a dropped colour are lost.
    lost = 0
    for payload in frames:
        dropped = {value for value in drop}
        for cell in cells_of(payload):
            if cell.colours & dropped:
                for row in range(8):
                    for column in range(8):
                        index = payload[(cell.y + row) * 64 + cell.x + column]
                        if index in dropped:
                            lost += 1
    total_pixels = sum(len(payload) for payload in frames)
    print(f"\nSMALLEST LOSS OPTION: {lost} pixel(s) of {total_pixels} across the eight frames "
          f"({100.0 * lost / total_pixels:.3f}%)")
    print("per-frame pairs need no loss at all: they were verified 0/4096 on every frame, but they require the")
    print("runtime writer to reload the pair each time the animation frame changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
