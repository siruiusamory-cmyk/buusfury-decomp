"""BORROW: can Cell get his extra colours from banks the scene loader fills, with no write at all?

A written bank holds 15 opaque colours. If a colour Cell needs beyond those already exists EXACTLY (same RGB555
value) in the ROM OBJ palette table that the scene loader copies, then Cell's sub-piece can simply select THAT
bank and use THAT slot: no write, no loss, and nobody else's colour changes.

This measures, per frame: which of Cell's colours are not in the written bank, whether each of them exists in the
ROM table outside that bank, and which ROM banks could serve them.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(r"C:\Dev\log1-remake-cell-c1")
sys.path.insert(0, str(ROOT))
from tools.webfoot.formats import webfoot_lz  # noqa: E402

ROM_BASE = 0x08000000
DEFINITION_TABLE = 0x6B6BB4
HEADER = 0x54
PIECE_BYTES = 12
FRAME_HEADER = 8
ANIMATION_HEADER = 4
MAX_IDS = 1200
MAX_SLOTS = 256
MAX_FRAMES = 64
BANK = 16
CELL_ID = 252

LOG2 = Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba")
BF = Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - Buu's Fury (U).gba")
LOG2_SOURCE_PALETTE = 0x081DA6C8
BF_TABLE = 0x05652C
WRITTEN_BANK = 14

log2 = LOG2.read_bytes()
bf = BF.read_bytes()


def u32(image: bytes, offset: int) -> int | None:
    if offset < 0 or offset + 4 > len(image):
        return None
    return struct.unpack_from("<I", image, offset)[0]


def cell_frames() -> list[list[set]]:
    """Each frame's per-piece colour sets, via the project's proven LoG II reader."""
    from tools.research.build_friend_v4b_cell import read_log2_cell
    slots, payloads = read_log2_cell(log2)
    frames = []
    for frame in slots:
        pieces = []
        for piece in frame:
            pieces.append(set(payloads[piece[5]]) - {0})
        frames.append(pieces)
    return frames


def main() -> int:
    source_palette = log2[LOG2_SOURCE_PALETTE - ROM_BASE:LOG2_SOURCE_PALETTE - ROM_BASE + 512]
    table = bf[BF_TABLE:BF_TABLE + 512]

    value_to_slots: dict[int, list[int]] = {}
    for slot in range(256):
        value = struct.unpack_from("<H", table, 2 * slot)[0]
        value_to_slots.setdefault(value, []).append(slot)

    frames = cell_frames()
    all_colours: dict[int, int] = {}
    for pieces in frames:
        for colours in pieces:
            for index in colours:
                all_colours[index] = all_colours.get(index, 0) + 1
    print(f"Cell uses {len(all_colours)} distinct source indices across {len(frames)} frame(s)")

    print("\nfor each Cell colour: its RGB555 value and where that value already exists in the ROM table")
    borrowable = {}
    for index in sorted(all_colours):
        value = struct.unpack_from("<H", source_palette, 2 * index)[0]
        slots = value_to_slots.get(value, [])
        banks = sorted({slot // BANK for slot in slots})
        borrowable[index] = banks
        mark = "" if banks else "   <-- NOT IN THE TABLE AT ALL"
        print(f"  index {index:>3} value 0x{value:04X}: slots {slots[:8]} banks {banks}{mark}")

    # Bank 14 must hold every colour that exists NOWHERE in the ROM table, because those cannot be borrowed.
    # The remaining slots go to the most-used borrowable colours, which minimises borrowing overall.
    unborrowable = [index for index in all_colours if not borrowable[index]]
    borrowable_ranked = sorted((index for index in all_colours if borrowable[index]),
                               key=lambda index: -all_colours[index])
    written = set(unborrowable) | set(borrowable_ranked[:max(0, 15 - len(unborrowable))])
    print(f"\nunborrowable colours: {sorted(unborrowable)} ({len(unborrowable)} of 21)")
    print(f"written bank {WRITTEN_BANK} holds {len(written)} colour(s): {sorted(written)}")

    print("\nper frame: colours outside the written bank, and whether they can be borrowed")
    all_zero = True
    for frame_index, pieces in enumerate(frames):
        colours = set().union(*pieces) if pieces else set()
        outside = sorted(colours - written)
        missing = [index for index in outside if not borrowable[index]]
        banks = sorted({bank for index in outside for bank in borrowable[index]
                        if bank != WRITTEN_BANK})
        ok = not missing
        all_zero = all_zero and ok
        print(f"  frame {frame_index}: {len(colours)} colour(s), {len(outside)} outside the written bank "
              f"{outside}, borrowable {ok}, banks needed {banks}, unborrowable {missing}")

    print(f"\nZERO LOSS WITH ONE WRITTEN BANK: {'yes' if all_zero else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
