"""Emit Cell's port with sub-pieces per frame, appended palettes, and a raised allocation size.

KNOWN OPEN DEFECTS in this revision, found by its own self-check and not yet fixed:
  * the two palette slots are appended but left ZERO. They must hold one palette pair for the whole character,
    because the engine animates frames and a runtime writer cannot cheaply know which frame is showing. That
    means one JOINT colour-to-bank assignment across all eight frames (duplication allowed), not a pair per frame.
  * the frame box (four bytes) is zero. Whether the engine reads it is not established.

WHAT THIS WRITES, all of it appended above the image's end, none of it into the ROM palette table:
  one kind-0 container per sub-piece, one frame record per frame with the LOGICAL bank (0 = A, 1 = B) in the
  piece attr's bits 25..27, an animation record of eight frames, and a definition copying the header of the one
  it replaces with a slot count of one. The ROM palette table at 0x05652C is NOT touched.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(r"C:\Dev\log1-remake-cell-c1")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "build"))

from build_two_bank_split import build_frame, cell_bank_assignment, palette_for_bank  # noqa: E402
from split_frame_search import cells_of  # noqa: E402
from tools.research.build_friend_v4b_cell import read_log2_cell  # noqa: E402

ROM_BASE = 0x08000000
DEFINITION_TABLE = 0x6B6BB4
HEADER = 0x54
PIECE_BYTES = 12
FRAME_HEADER = 8
ANIMATION_HEADER = 4
CELL_ID = 252
LOG2 = Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba")
LOG2_SOURCE_PALETTE = 0x081DA6C8
BASE = Path(r"C:\Dev\log1-remake-fv4\build\fv4\v4a-broly.gba")
OUT = Path(r"C:\Dev\log1-remake-cell-c1\build\c1-split.gba")

SHAPE_SIZE = {  # (width, height) -> (shape, size)
    (8, 8): (0, 0), (16, 16): (0, 1), (32, 32): (0, 2), (64, 64): (0, 3),
    (16, 8): (1, 0), (32, 8): (1, 1), (32, 16): (1, 2), (64, 32): (1, 3),
    (8, 16): (2, 0), (8, 32): (2, 1), (16, 32): (2, 2), (32, 64): (2, 3),
}


def main() -> int:
    log2 = LOG2.read_bytes()
    image = bytearray(BASE.read_bytes())
    source_palette = log2[LOG2_SOURCE_PALETTE - 0x08000000:LOG2_SOURCE_PALETTE - 0x08000000 + 512]
    slots, payloads = read_log2_cell(log2)

    base_definition = struct.unpack_from("<I", image, DEFINITION_TABLE + 4 * CELL_ID)[0]
    base_offset = base_definition - ROM_BASE
    header = bytes(image[base_offset:base_offset + HEADER])

    pending: list[tuple[str, int]] = []          # (label, resolved address) for back-patching
    palettes_at: list[int] = []

    def align() -> None:
        while len(image) % 4:
            image.append(0)

    # The two palettes, in the order the logical banks use them.
    per_frame = []
    for frame in slots:
        piece = frame[0]
        payload = payloads[piece[5]]
        cells = cells_of(payload)
        cell_banks = cell_bank_assignment(cells, 2)
        per_bank = [set(), set()]
        for cell in cells:
            for value in cell.colours:
                per_bank[cell_banks[(cell.x, cell.y)]].add(value)
        palettes = [palette_for_bank(per_bank[0], source_palette),
                    palette_for_bank(per_bank[1], source_palette)]
        pieces = build_frame(payload, piece[2], cell_banks, palettes, 0)
        per_frame.append(pieces)

    align()
    for index in range(2):
        palettes_at.append(len(image))
        for _ in range(16):
            image.extend(struct.pack("<H", 0))
    print(f"palette slots appended at 0x{palettes_at[0] + ROM_BASE:08X} and "
          f"0x{palettes_at[1] + ROM_BASE:08X} (filled below per frame)")

    containers_at: list[list[int]] = []
    frames_at: list[int] = []
    for frame_index, pieces in enumerate(per_frame):
        frame_containers = []
        for x, y, width, height, logical_bank, packed in pieces:
            align()
            frame_containers.append(len(image))
            payload = bytes(packed)
            assert len(payload) == width * height // 2, (len(payload), width * height // 2)
            image.extend(struct.pack("<II", 0, width * height))
            image.extend(payload)
            padding = width * height - len(payload)
            if padding:
                image.extend(bytes(padding))
        containers_at.append(frame_containers)

        align()
        frames_at.append(len(image))
        image.extend(struct.pack("<I", len(pieces)))
        image.extend(bytes(4))
        for (x, y, width, height, logical_bank, _), container in zip(pieces, frame_containers):
            shape, size = SHAPE_SIZE[(width, height)]
            attr = (shape << 14) | (size << 12) | (logical_bank << 25)
            image.extend(struct.pack("<bbBBI", x, y, width, height, attr))
            image.extend(struct.pack("<I", ROM_BASE + container))

    align()
    animation_at = len(image)
    image.extend(struct.pack("<I", len(frames_at)))
    for pointer in frames_at:
        for _ in range(4):
            image.extend(struct.pack("<I", ROM_BASE + pointer))

    align()
    definition_at = len(image)
    image.extend(header)
    image.extend(bytes(4))                       # room for the one slot pointer at +0x54
    image[definition_at] = 1                     # the slot count is the LOW BYTE, and this copy has one slot
    struct.pack_into("<I", image, definition_at + HEADER, ROM_BASE + animation_at)
    struct.pack_into("<I", image, DEFINITION_TABLE + 4 * CELL_ID, ROM_BASE + definition_at)

    OUT.write_bytes(bytes(image))
    print(f"wrote {OUT} ({len(image)} bytes)")
    print(f"definition at 0x{definition_at + ROM_BASE:08X}, animation record at 0x{animation_at + ROM_BASE:08X}")
    print(f"frames: {[len(pieces) for pieces in per_frame]} piece(s)")

    # Walk the result back with the census structures.
    out = OUT.read_bytes()
    definition = struct.unpack_from("<I", out, DEFINITION_TABLE + 4 * CELL_ID)[0] - ROM_BASE
    print(f"\nself-check: definition low byte {out[definition]}, allocator size "
          f"{struct.unpack_from('<H', out, definition + 2)[0]}")
    record = struct.unpack_from("<I", out, definition + HEADER)[0] - ROM_BASE
    frame_count = struct.unpack_from("<I", out, record)[0]
    print(f"  slot 0 -> animation record with frame_count {frame_count}")
    for frame_index in range(frame_count):
        pointer = struct.unpack_from("<I", out, record + ANIMATION_HEADER + 16 * frame_index)[0] - ROM_BASE
        piece_count = struct.unpack_from("<I", out, pointer)[0]
        banks = set()
        tiles = 0
        for index in range(piece_count):
            entry = pointer + FRAME_HEADER + PIECE_BYTES * index
            width, height = out[entry + 2], out[entry + 3]
            attr = struct.unpack_from("<I", out, entry + 4)[0]
            banks.add((attr >> 25) & 7)
            tiles += width * height // 64
        print(f"  frame {frame_index}: piece_count {piece_count}, banks {sorted(banks)}, tiles {tiles}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
