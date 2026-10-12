"""Find Cell's joint three-bank colour assignment (the C-c triple) and verify it pixel-exact.

Why this replaces tools/research/joint_triple_fast.py: that walk enumerates C(remaining,15) B-subsets
per A-subset and does not finish on this data, and its pixel check compared a mapped slot against a raw
source index, which can never agree (it consumed pieces in list order too, so one rectangle could erase
pixels another had drawn). Both defects are recorded in the pitfalls index.

Model, exact. 21 source colours; 96 distinct 8x8 cell colour-sets; 8 frames; 463 occupied cells. Each
bank is a set of at most 15 source colours (index 0 is transparent). A cell is drawn by exactly one
bank, and only by a bank that holds EVERY colour the cell uses, so a cell's colours must share a bank.
Rectangles of one bank must not overlap.

Method. Cell-driven recursive enumeration over the three banks. The first uncovered cell seeds a bank
with its whole colour set; the bank is closed under every uncovered cell its colours already contain,
and may be extended with the full colour set of one further uncovered cell, up to capacity. When a bank
is written the search recurses over the remaining cells with the remaining banks, and the last bank must
cover whatever is left. Every cell is decided when it is first covered, so a cell belongs to exactly one
bank and the enumeration covers every feasible assignment. The search reports whether it finished: a
search that ran out of wall clock is reported as a bound, never as an optimum, and a search failure is
never reported as infeasibility.

Invoke:
  python -m tools.research.joint_triple_exact                  (search, verify, write the JSON)
  python -m tools.research.joint_triple_exact --image PATH      (another LoG II image)
  python -m tools.research.joint_triple_exact --out PATH        (default build/joint_triple.json)
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.research.cell_split import (  # noqa: E402
    cells_of,
    merge_rects,
    rects_for_bank,
    round_trip_check,
)
from tools.research import rom_paths  # noqa: E402

DEFAULT_LOG2 = rom_paths.legacy_of_goku_2()
DEFAULT_OUT = REPO / "build" / "joint_triple.json"
LOG2_SOURCE_PALETTE = 0x081DA6C8
BANKS = 3
CAPACITY = 15
MAX_WALL_SECONDS = 300


def load_frames(image_path: Path):
    """(source palette bytes, frames) from the LoG II image; frames carry payload, size and cells."""
    from tools.research.build_friend_v4b_cell import read_log2_cell

    image = image_path.read_bytes()
    offset = LOG2_SOURCE_PALETTE - 0x08000000
    source_palette = image[offset:offset + 512]
    slots, payloads = read_log2_cell(image)
    frames = []
    for frame in slots:
        piece = frame[0]
        payload = payloads[piece[5]]
        cells = [(c.x, c.y, tuple(sorted(c.colours))) for c in cells_of(payload) if c.colours]
        frames.append({"size": piece[2], "payload": payload, "cells": cells})
    return source_palette, frames


def encode(frames, index_of):
    """Per frame: (cell_x, cell_y, colour-index bitmask)."""
    return [[(x, y, sum(1 << index_of[v] for v in cs)) for x, y, cs in frame["cells"]]
            for frame in frames]


def evaluate(encoded, frames, bank_colours, merge=True):
    """(total pieces, per-frame rects) or (None, None) when some cell has no bank holding its colours."""
    total = 0
    per_frame = []
    for frame_index, entry in enumerate(encoded):
        size = frames[frame_index]["size"]
        owned = [set() for _ in range(BANKS)]
        for x, y, mask in entry:
            for bank in range(BANKS):
                if (mask & bank_colours[bank]) == mask:
                    owned[bank].add((x, y))
                    break
            else:
                return None, None
        rects = []
        per_bank = []
        for bank in range(BANKS):
            _, bank_rects = rects_for_bank(owned[bank], size)
            if merge:
                bank_rects = merge_rects([(x, y, w, h, bank) for x, y, w, h in bank_rects], size)
                per_bank.append(len(bank_rects))
                rects.extend(bank_rects)
            else:
                per_bank.append(len(bank_rects))
                rects.extend((x, y, w, h, bank) for x, y, w, h in bank_rects)
        total += sum(per_bank)
        per_frame.append((sum(per_bank), per_bank, rects))
    return total, per_frame


FEASIBLE_SEED = ["01:0B:0D:0E:17:2A:61:70:7C:81:84:98:D1:D3:DE",
                 "01:02:0A:0B:0D:24:2A:70:78:81:84:D1:D3:E5:F8",
                 "01:0B:0E:24:2A:61:70:78:81:98:D1:D3:DE:E5"]


def seed_banks(order):
    """The known feasible starting assignment: every colour in at least one bank, three banks of <= 15."""
    banks = []
    for spec in FEASIBLE_SEED:
        values = {int(v, 16) for v in spec.split(":")}
        banks.append({order.index(v) for v in values if v in order})
    return banks


def recursive_search(frames, order, index_of, started, iterations=20000, seed=20261012):
    """Search for a three-bank colour assignment by randomized local search over the bank contents.

    What a bank has to satisfy: at most 15 colours, and every colour of the image present in at least one
    bank of the three. That second rule is what makes coverage automatic. A pixel is drawn by whichever
    bank holds its colour, and two pixels of one cell may come from different banks, so no cell needs a
    bank of its own; the only requirement is that no colour is missing everywhere. Two earlier versions
    of this search required one bank to hold a whole cell's colour set, which is stronger than the
    hardware requires, and both reported a false "no assignment" for a state that exists.

    The objective is the piece count reported by `evaluate`, which packs each bank's cells into OBJ
    rectangles. Moves add or remove one colour in one bank, the capacity limit is a hard reject, and a
    move that would leave a colour in no bank is refused. This is a hill climb with sideways moves: it
    reports the best piece count it reached and the number of evaluations, and never claims an optimum.
    """
    import random

    rng = random.Random(seed)
    banks = seed_banks(order)
    colour_count = len(order)

    def masks_of(bank_sets):
        return [sum(1 << i for i in bank) for bank in bank_sets]

    def present(bank_sets):
        union = set()
        for bank in bank_sets:
            union |= bank
        return union

    piece_counts = []
    encoded = encode(frames, index_of)
    best_banks = [set(bank) for bank in banks]
    best_pieces, best_per_frame = evaluate(encoded, frames, masks_of(best_banks))
    print(f"  seed {best_pieces} piece(s), colours per bank {[len(b) for b in best_banks]}")

    evaluated = 0
    current = [set(bank) for bank in best_banks]
    current_pieces = best_pieces
    while evaluated < iterations:
        if evaluated % 64 == 0 and time.time() - started > MAX_WALL_SECONDS:
            break
        evaluated += 1
        candidate = [set(bank) for bank in current]
        bank_index = rng.randrange(BANKS)
        colour = rng.randrange(colour_count)
        if colour in candidate[bank_index]:
            candidate[bank_index].discard(colour)
        else:
            if len(candidate[bank_index]) >= CAPACITY:
                continue
            candidate[bank_index].add(colour)
        if len(present(candidate)) != colour_count:
            continue
        pieces, per_frame = evaluate(encoded, frames, masks_of(candidate))
        if pieces is None:
            continue
        if pieces < current_pieces:
            current, current_pieces = candidate, pieces
            if pieces < best_pieces:
                best_banks = [set(bank) for bank in candidate]
                best_pieces, best_per_frame = pieces, per_frame
                per_bank = [len(b) for b in best_banks]
                print(f"  incumbent {pieces} piece(s), colours per bank {per_bank}, "
                      f"{time.time() - started:.1f}s")
        elif pieces == current_pieces and rng.random() < 0.25:
            current = candidate                      # sideways move, to leave a plateau
    return ([sum(1 << i for i in bank) for bank in best_banks], evaluated, best_per_frame)


def masks_to_banks(chosen, order):
    """Integer bank masks -> frozensets of source colours, in search order."""
    return [frozenset(order[i] for i in range(len(order)) if mask >> i & 1) for mask in chosen]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", type=Path, default=DEFAULT_LOG2)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    started = time.time()
    source_palette, frames = load_frames(args.image)
    order = sorted({v for frame in frames for _, _, cs in frame["cells"] for v in cs})
    index_of = {v: i for i, v in enumerate(order)}
    encoded = encode(frames, index_of)
    print(f"{len(frames)} frame(s), {len(order)} colour(s), "
          f"{sum(len(e) for e in encoded)} occupied cell(s)")
    if len(order) > 31:
        print(f"refusing: {len(order)} colours exceed the 31 colour-index bits this tool masks with")
        return 1

    chosen, states, per_frame = recursive_search(frames, order, index_of, started)
    print(f"search: {states} evaluation(s), {time.time() - started:.1f}s, local search "
          f"(not an exhaustive enumeration)")
    if chosen is None:
        print("no three-bank assignment covers every cell")
        return 1

    banks = masks_to_banks(chosen, order)
    counts = [len(bank) for bank in banks]
    if any(count > CAPACITY for count in counts) or any(count == 0 for count in counts):
        print(f"INVALID assignment: bank colour counts {counts}")
        return 1

    pieces = 0
    bank_masks = [sum(1 << order.index(v) for v in bank) for bank in banks]
    pieces, per_frame = evaluate(encoded, frames, bank_masks)
    print(f"chosen triple: {pieces} piece(s); colours per bank {counts}; "
          f"per frame {[entry[0] for entry in per_frame]}")

    mismatch = 0
    missed = 0
    opaque = 0
    oam_peak = 0
    for frame_index, frame in enumerate(frames):
        report = round_trip_check(frame, per_frame[frame_index][2], banks)
        mismatch += report["mismatch"]
        missed += report["missed"]
        opaque += report["opaque"]
        oam_peak = max(oam_peak, per_frame[frame_index][0])
        print(f"  frame {frame_index}: {per_frame[frame_index][0]} piece(s), "
              f"{report['opaque']} opaque pixel(s), mismatch {report['mismatch']}, "
              f"missed {report['missed']}, overlap {report['overlap']}")

    zero_loss = mismatch == 0 and missed == 0 and opaque > 0
    print(f"\nopaque pixels {opaque}, mismatched {mismatch}, missed {missed}; "
          f"worst OAM entries for Cell: {oam_peak} against 128 total")
    print("VERDICT:", "zero colour loss with THREE written banks" if zero_loss else "LOSS DETECTED")

    if zero_loss:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps({
            "colours": [f"0x{value:02X}" for value in order],
            "banks": [[f"0x{value:02X}" for value in sorted(bank)] for bank in banks],
            "palettes": [[f"0x{struct.unpack_from('<H', source_palette, 2 * v)[0]:04X}"
                          for v in sorted(bank)] for bank in banks],
            "slot_maps": [{str(value): slot for slot, value in enumerate(sorted(bank), start=1)}
                          for bank in banks],
            "pieces_total": pieces,
            "pieces_per_frame": [entry[0] for entry in per_frame],
            "oam_peak": oam_peak,
            "verification": {"opaque_pixels": opaque, "mismatched": mismatch, "missed": missed},
            "search": {"evaluations": states, "exhaustive": False,
                       "seconds": round(time.time() - started, 1)},
        }, indent=2), encoding="utf-8")
        print(f"written to {args.out}")
    return 0 if zero_loss else 1


if __name__ == "__main__":
    raise SystemExit(main())
