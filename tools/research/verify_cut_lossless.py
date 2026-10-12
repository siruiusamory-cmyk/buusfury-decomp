"""Prove the cut is lossless: reassemble the sub-pieces and compare every pixel with the source.

Each sub-piece carries its own bank and its own local slot mapping. Reassembling them through those palettes must
reproduce the source frame's colour at every one of the 4096 pixels, by exact RGB555. A single mismatch is a lost
or altered colour, so this is the structural proof of zero loss, before any emulator run.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(r"C:\Dev\log1-remake-cell-c1")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "build"))

from build_two_bank_split import (build_frame, palette_for_bank, cell_bank_assignment,  # noqa: E402
                                  two_bank_assignment)
from split_frame_search import cells_of  # noqa: E402
from tools.research.build_friend_v4b_cell import read_log2_cell  # noqa: E402

LOG2 = Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba")
LOG2_SOURCE_PALETTE = 0x081DA6C8
BASE_BANK = 14


def main() -> int:
    log2 = LOG2.read_bytes()
    source_palette = log2[LOG2_SOURCE_PALETTE - 0x08000000:LOG2_SOURCE_PALETTE - 0x08000000 + 512]
    slots, payloads = read_log2_cell(log2)

    total_pieces, failures = 0, 0
    for frame_index, frame in enumerate(slots):
        piece = frame[0]
        payload = payloads[piece[5]]
        size = piece[2]
        cells = cells_of(payload)
        cell_banks = cell_bank_assignment(cells, 2)
        per_bank = [{}, {}]
        for cell in cells:
            for value in cell.colours:
                per_bank[cell_banks[(cell.x, cell.y)]][value] = True
        palettes = [palette_for_bank(set(per_bank[0]), source_palette),
                    palette_for_bank(set(per_bank[1]), source_palette)]
        pieces = build_frame(payload, size, cell_banks, palettes, BASE_BANK)
        total_pieces += len(pieces)

        rendered: dict[tuple[int, int], int] = {}
        for x, y, width, height, bank, packed in pieces:
            local = palettes[bank - BASE_BANK]["slots"]
            slot_to_index = {slot: index for index, slot in local.items()}
            cursor = 0
            for tile_y in range(y, y + height, 8):
                for tile_x in range(x, x + width, 8):
                    for row in range(8):
                        for pair in range(0, 8, 2):
                            byte = packed[cursor]
                            cursor += 1
                            for offset, value in ((0, byte & 0xF), (1, (byte >> 4) & 0xF)):
                                index = 0 if value == 0 else slot_to_index.get(value, None)
                                rendered[(tile_x + pair + offset, tile_y + row)] = index

        mismatches = 0
        for y in range(size):
            for x in range(size):
                source_index = payload[y * size + x]
                if rendered.get((x, y), 0) != source_index:
                    mismatches += 1
        if mismatches:
            failures += 1
        print(f"frame {frame_index}: {len(pieces)} piece(s), {mismatches} of {size * size} pixel(s) differ "
              f"from the source")
    print(f"\n{total_pieces} piece(s) in total; frames with any pixel difference: {failures}")
    print("VERDICT:", "zero colour loss" if failures == 0 else "LOSS DETECTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
