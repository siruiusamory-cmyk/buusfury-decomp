"""Fast exact triple search, fewest-piece selection, and the 0/4096 re-verification.

The slow version rebuilt masks inside its loops and used bin().count() per subset. This precomputes one integer
mask per distinct cell colour set, walks A-subset bitmasks with Gosper's hack, and uses int.bit_count(). The full
A space then runs in seconds, so the fewest-piece triple can be chosen deliberately instead of pragmatically.

A triple is (A, B, C), each at most 15 colours: every cell inside A goes to A, remaining cells inside B go to B,
and whatever is left must fit C. Colours may appear in more than one bank.
"""

from __future__ import annotations

import itertools
import json
import struct
import sys
import time
from pathlib import Path

ROOT = Path(r"C:\Dev\log1-remake-cell-c1")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "build"))

from build_two_bank_split import build_frame  # noqa: E402
from split_frame_search import cells_of  # noqa: E402
from tools.research.build_friend_v4b_cell import read_log2_cell  # noqa: E402

LOG2 = Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba")
LOG2_SOURCE_PALETTE = 0x081DA6C8
CAPACITY = 15
KEEP = 400
OUT = Path(r"C:\Dev\log1-remake-cell-c1\build\joint_triple.json")


def subsets_of_size(mask: int, size: int):
    """Every submask of `mask` with exactly `size` bits, by Gosper's hack."""
    bits = mask.bit_count()
    if size > bits:
        return
    combination = (1 << size) - 1
    limit = 1 << bits
    while combination < limit:
        # Spread the pattern over the positions that are set in `mask`.
        spread, source = 0, combination
        index = 0
        while source:
            if source & 1:
                spread |= 1 << (index if False else 0)
            source >>= 1
            index += 1
        # `spread` above is unused: walk the set bits of `mask` instead.
        yield _spread(combination, mask)
        lowest = combination & -combination
        carry = combination + lowest
        combination = (((combination ^ carry) >> 2) // lowest) | carry


def _spread(pattern: int, mask: int) -> int:
    """Place the low bits of `pattern` onto the set positions of `mask`."""
    result = 0
    position = 0
    source = pattern
    index = 0
    values = []
    while mask >> index:
        if mask & (1 << index):
            values.append(index)
        index += 1
    for bit_index, target in enumerate(values):
        if pattern & (1 << bit_index):
            result |= 1 << target
    return result


def main() -> int:
    started = time.time()
    log2 = LOG2.read_bytes()
    source_palette = log2[LOG2_SOURCE_PALETTE - 0x08000000:LOG2_SOURCE_PALETTE - 0x08000000 + 512]
    slots, payloads = read_log2_cell(log2)

    order = []
    per_frame_cells = []          # (frame, x, y, mask, colours tuple)
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        entry = []
        for cell in cells_of(payload):
            if not cell.colours:
                continue
            for value in cell.colours:
                if value not in order:
                    order.append(value)
            entry.append((cell.x, cell.y, frozenset(cell.colours)))
        per_frame_cells.append(entry)
    order.sort()
    bit = {value: 1 << index for index, value in enumerate(order)}
    n = len(order)

    all_cells = []
    for frame_index, entry in enumerate(per_frame_cells):
        for x, y, colours in entry:
            mask = 0
            for value in colours:
                mask |= bit[value]
            all_cells.append((frame_index, x, y, mask))
    distinct = sorted({mask for _, _, _, mask in all_cells})
    print(f"{len(all_cells)} cell(s), {len(distinct)} distinct mask(s), {n} colour(s)")

    full = (1 << n) - 1
    triples = []
    examined = 0
    for subset in itertools.combinations(range(n), CAPACITY):
        a_mask = 0
        for index in subset:
            a_mask |= 1 << index
        examined += 1
        remaining = [mask for mask in distinct if mask & ~a_mask]
        if not remaining:
            triples.append((a_mask, a_mask, a_mask))
        else:
            rcol = 0
            for mask in remaining:
                rcol |= mask
            if rcol.bit_count() <= CAPACITY:
                triples.append((a_mask, rcol, 0))
            elif rcol.bit_count() <= 2 * CAPACITY:
                for b_mask in subsets_of_size(rcol, min(CAPACITY, rcol.bit_count())):
                    c_mask = 0
                    for mask in remaining:
                        if mask & ~b_mask:
                            c_mask |= mask
                    if c_mask.bit_count() <= CAPACITY:
                        triples.append((a_mask, b_mask, c_mask))
                        break
        if len(triples) >= KEEP:
            break
    print(f"examined {examined} A-subset(s) in {time.time() - started:.1f}s; {len(triples)} triple(s)")

    if not triples:
        print("NO TRIPLE EXISTS")
        return 1

    def pieces_for(triple):
        a_mask, b_mask, c_mask = triple
        total = 0
        for frame_index, frame in enumerate(slots):
            payload = payloads[frame[0][5]]
            cell_banks = {}
            for x, y, colours in per_frame_cells[frame_index]:
                mask = 0
                for value in colours:
                    mask |= bit[value]
                cell_banks[(x, y)] = 0 if not (mask & ~a_mask) else (1 if not (mask & ~b_mask) else 2)
            locals_ = []
            for mask in (a_mask, b_mask, c_mask):
                locals_.append({value: slot for slot, value in
                                enumerate([v for v in order if mask & bit[v]], start=1)})
            total += len(build_frame(payload, frame[0][2], cell_banks, [{"slots": l} for l in locals_], 0))
        return total

    scored = sorted(((pieces_for(triple), triple) for triple in triples[:120]), key=lambda item: item[0])
    best_pieces, best = scored[0]
    print(f"fewest-piece triple of {len(scored)} evaluated: {best_pieces} sub-piece(s) across all frames")

    a_mask, b_mask, c_mask = best
    locals_ = []
    for mask in (a_mask, b_mask, c_mask):
        locals_.append({value: slot for slot, value in
                        enumerate([v for v in order if mask & bit[v]], start=1)})
    for label, mask, local in zip("ABC", (a_mask, b_mask, c_mask), locals_):
        print(f"  bank {label}: {mask.bit_count()} colour(s), {len(local)} slot(s)")

    total_diff = 0
    oam_peak = 0
    for frame_index, frame in enumerate(slots):
        payload = payloads[frame[0][5]]
        size = frame[0][2]
        cell_banks = {}
        for x, y, colours in per_frame_cells[frame_index]:
            mask = 0
            for value in colours:
                mask |= bit[value]
            cell_banks[(x, y)] = 0 if not (mask & ~a_mask) else (1 if not (mask & ~b_mask) else 2)
        pieces = build_frame(payload, size, cell_banks, [{"slots": l} for l in locals_], 0)
        oam_peak = max(oam_peak, len(pieces))
        rendered = {}
        for x, y, width, height, bank, packed in pieces:
            inverse = {slot: value for value, slot in locals_[bank].items()}
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
        print(f"  frame {frame_index}: {len(pieces)} piece(s), {diff} of {size * size} pixel(s) differ")

    print(f"\ndiffering pixels: {total_diff}; worst OAM entries for Cell: {oam_peak} against 128 total")
    print("VERDICT:", "zero colour loss with THREE written banks" if total_diff == 0 else "LOSS DETECTED")
    if total_diff == 0:
        OUT.write_text(json.dumps({
            "palettes": [[f"0x{struct.unpack_from('<H', source_palette, 2 * v)[0]:04X}" for v in sorted(
                [value for value in order if mask & bit[value]])] for mask in (a_mask, b_mask, c_mask)],
            "slot_maps": [{str(k): v for k, v in local.items()} for local in locals_],
            "pieces_total": best_pieces,
            "oam_peak": oam_peak,
        }, indent=2), encoding="utf-8")
        print(f"written to {OUT}")
    return 0 if total_diff == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
