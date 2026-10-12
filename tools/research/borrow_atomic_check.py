"""Can every 8x8 cell of every frame live in ONE bank under the borrow assignment?

Borrow gives each colour a bank: the written bank if it is unborrowable or in the chosen written set, otherwise
the ROM-filled bank whose slot holds that colour exactly. A sub-piece is at least an 8x8 cell, and one piece
selects one bank, so a cell whose colours span two banks cannot be drawn at all. This checks that before anything
is built.
"""

from __future__ import annotations

import struct
import sys
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

log2 = LOG2.read_bytes()
bf = BF.read_bytes()


def assign() -> dict[int, tuple[int, int]]:
    """source index -> (bank, slot), using the written bank for unborrowables and the ROM table otherwise."""
    from tools.research.build_friend_v4b_cell import read_log2_cell
    slots, payloads = read_log2_cell(log2)
    source_palette = log2[LOG2_SOURCE_PALETTE - 0x08000000:LOG2_SOURCE_PALETTE - 0x08000000 + 512]
    table = bf[BF_TABLE:BF_TABLE + 512]

    value_to_slots: dict[int, list[int]] = {}
    for slot in range(256):
        value_to_slots.setdefault(struct.unpack_from("<H", table, 2 * slot)[0], []).append(slot)

    usage: dict[int, int] = {}
    for frame in slots:
        for piece in frame:
            for index in set(payloads[piece[5]]) - {0}:
                usage[index] = usage.get(index, 0) + 1

    unborrowable = [index for index in usage
                    if not [slot for slot in value_to_slots.get(
                        struct.unpack_from("<H", source_palette, 2 * index)[0], [])
                            if slot // BANK != WRITTEN_BANK]]
    borrowable_ranked = sorted((index for index in usage if index not in unborrowable),
                               key=lambda index: -usage[index])
    written = set(unborrowable) | set(borrowable_ranked[:max(0, 15 - len(unborrowable))])
    print(f"written bank {WRITTEN_BANK}: {len(written)} colour(s) = {sorted(written)}")

    mapping: dict[int, tuple[int, int]] = {}
    slot_in_written = 1
    for index in sorted(written):
        mapping[index] = (WRITTEN_BANK, slot_in_written)
        slot_in_written += 1
    for index in usage:
        if index in written:
            continue
        value = struct.unpack_from("<H", source_palette, 2 * index)[0]
        candidates = [slot for slot in value_to_slots.get(value, []) if slot // BANK != WRITTEN_BANK]
        if not candidates:
            raise SystemExit(f"index {index} has no borrow slot")
        slot = candidates[0]
        mapping[index] = (slot // BANK, slot % BANK)
    return mapping, slots, payloads


def main() -> int:
    mapping, slots, payloads = assign()
    print(f"borrow banks used: {sorted({bank for bank, _ in mapping.values()})}")

    failures = 0
    for frame_index, frame in enumerate(slots):
        piece = frame[0]
        payload = payloads[piece[5]]
        size = piece[2]
        worst = 0
        for cell_y in range(0, size, 8):
            for cell_x in range(0, size, 8):
                banks = set()
                for row in range(8):
                    for column in range(8):
                        index = payload[(cell_y + row) * size + cell_x + column]
                        if index:
                            banks.add(mapping[index][0])
                worst = max(worst, len(banks))
                if len(banks) > 1:
                    failures += 1
                    if failures <= 4:
                        print(f"  frame {frame_index} cell ({cell_x},{cell_y}): banks {sorted(banks)}")
        print(f"frame {frame_index}: worst cell spans {worst} bank(s)")
    print(f"\nATOMIC: {failures} cell(s) span more than one bank")
    print("VERDICT:", "every cell fits one bank" if failures == 0 else "NOT feasible at 8x8 granularity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
