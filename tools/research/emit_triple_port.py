"""Emit Cell's port: sub-piece frames over THREE written banks, with one joint palette triple.

WHAT IT WRITES, all of it appended above the image's end, none of it into the ROM palette table:
  one kind-0 container per sub-piece, one frame record per frame with the LOGICAL bank (0=A, 1=B, 2=C) in
  the piece attr's bits 25..27, an animation record of eight frames, one appended 16-halfword palette per
  bank, and a definition that copies the header of the one it replaces.

The definition header is calibrated against retail definitions, not guessed: the low byte of `def+0x00`
is the ANIMATION COUNT (sprite 73 has 23 with 23 slot pointers, sprite 38 has 22 with 22, Cell's retail
id 252 has 20), byte `+0x01` is zero in all three, byte `+0x03` is 0x10, and the inline animation pointer
array starts at `def+0x54` (measured, and the selector at `0x0800ECDA` reads `[def + 0x54 + 4*index]`
with no bound check). The port carries ONE animation, so the count is the LENGTH OF THE SLOT ARRAY --
one -- and the field is set from `len(slot_pointers)` rather than masked out of the copied header.

The ROM palette table at file 0x05652C is NOT touched: the three palettes travel as appended data and the
runtime writer copies them into whichever banks are free at that moment.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.research.cell_split import (  # noqa: E402
    build_frame,
    cells_of,
    palette_for_bank,
)
from tools.research import rom_paths  # noqa: E402

ROM_BASE = 0x08000000
DEFINITION_TABLE = 0x6B6BB4
HEADER = 0x54
PIECE_BYTES = 12
FRAME_HEADER = 8
ANIMATION_HEADER = 4
CELL_ID = 252
LOG2_SOURCE_PALETTE = 0x081DA6C8
DEFAULT_LOG2 = rom_paths.legacy_of_goku_2()
BANK_COUNT = 3

SHAPE_SIZE = {  # (width, height) -> (shape, size)
    (8, 8): (0, 0), (16, 16): (0, 1), (32, 32): (0, 2), (64, 64): (0, 3),
    (16, 8): (1, 0), (32, 8): (1, 1), (32, 16): (1, 2), (64, 32): (1, 3),
    (8, 16): (2, 0), (8, 32): (2, 1), (16, 32): (2, 2), (32, 64): (2, 3),
}


def read_bank_colours(path: Path, order) -> list:
    """The three banks' colour sets from the triple search's JSON, as sets of source indices."""
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    banks = [{int(value, 16) for value in bank} for bank in data["banks"]]
    missing = [value for bank in banks for value in bank if value not in order]
    if missing:
        raise SystemExit(f"bank colours not present in the frames: {missing}")
    return banks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", type=Path,
                        default=REPO / "build" / "fv4" / "v4a-broly.gba")
    parser.add_argument("--log2", type=Path, default=DEFAULT_LOG2)
    parser.add_argument("--triple", type=Path,
                        default=REPO / "build" / "joint_triple.json")
    parser.add_argument("--out", type=Path, default=REPO / "build" / "c1-triple.gba")
    args = parser.parse_args()

    from tools.research.build_friend_v4b_cell import read_log2_cell

    log2 = args.log2.read_bytes()
    image = bytearray(args.image.read_bytes())
    source_palette = log2[LOG2_SOURCE_PALETTE - 0x08000000:LOG2_SOURCE_PALETTE - 0x08000000 + 512]
    slots, payloads = read_log2_cell(log2)
    order = sorted({v for frame in slots for c in cells_of(payloads[frame[0][5]]) for v in c.colours})
    bank_colours = read_bank_colours(args.triple, order)
    if len(bank_colours) != BANK_COUNT:
        raise SystemExit(f"the triple names {len(bank_colours)} bank(s), expected {BANK_COUNT}")

    base_definition = struct.unpack_from("<I", image, DEFINITION_TABLE + 4 * CELL_ID)[0]
    base_offset = base_definition - ROM_BASE
    header = bytes(image[base_offset:base_offset + HEADER])

    def align() -> None:
        while len(image) % 4:
            image.append(0)

    # One palette per bank, built once for the WHOLE character: frames animate, so a per-frame palette
    # could not be selected by a writer that does not know which frame is showing.
    palettes = [palette_for_bank(bank, source_palette) for bank in bank_colours]

    per_frame = []
    for frame in slots:
        piece = frame[0]
        payload = payloads[piece[5]]
        cell_banks = {}
        for cell in cells_of(payload):
            for bank, colours in enumerate(bank_colours):
                if cell.colours <= colours:
                    cell_banks[(cell.x, cell.y)] = bank
                    break
            else:
                raise SystemExit(f"frame piece {piece[5]}: cell ({cell.x},{cell.y}) fits no bank")
        per_frame.append(build_frame(payload, piece[2], cell_banks, palettes))

    align()
    palettes_at = []
    for bank in range(BANK_COUNT):
        palettes_at.append(len(image))
        for colour in palettes[bank]["colours"]:
            image.extend(struct.pack("<H", colour))
    print("appended palettes at " + ", ".join(f"0x{offset + ROM_BASE:08X}" for offset in palettes_at))

    frames_at = []
    for pieces in per_frame:
        containers = []
        for x, y, width, height, logical_bank, packed in pieces:
            align()
            containers.append(len(image))
            assert len(packed) == width * height // 2, (len(packed), width * height // 2)
            image.extend(struct.pack("<II", 0, width * height))
            image.extend(packed)
        align()
        frames_at.append(len(image))
        image.extend(struct.pack("<I", len(pieces)))
        image.extend(bytes(4))
        for (x, y, width, height, logical_bank, _), container in zip(pieces, containers):
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

    slot_pointers = [ROM_BASE + animation_at]
    align()
    definition_at = len(image)
    image.extend(header)
    for pointer in slot_pointers:
        image.extend(struct.pack("<I", pointer))
    # Set the fields from the data structure this definition actually has, never by masking the copy.
    image[definition_at] = len(slot_pointers)      # animation count == slot array length
    image[definition_at + 1] = 0                   # zero in every retail definition measured
    struct.pack_into("<I", image, DEFINITION_TABLE + 4 * CELL_ID, ROM_BASE + definition_at)

    args.out.write_bytes(bytes(image))
    manifest = {
        "image": str(args.out),
        "size": len(image),
        "palettes_at": [offset + ROM_BASE for offset in palettes_at],
        "definition": definition_at + ROM_BASE,
        "animation_record": animation_at + ROM_BASE,
        "slot_pointers": [pointer for pointer in slot_pointers],
        "pieces_per_frame": [len(pieces) for pieces in per_frame],
        "banks": [[f"0x{value:02X}" for value in sorted(bank)] for bank in bank_colours],
        "slot_maps": [{str(value): slot for value, slot in palette["slots"].items()}
                      for palette in palettes],
    }
    args.out.with_suffix(".json").write_text(
        __import__("json").dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {args.out} ({len(image)} bytes) and {args.out.with_suffix('.json')}")
    print(f"definition at 0x{definition_at + ROM_BASE:08X} with {len(slot_pointers)} slot(s), "
          f"animation record at 0x{animation_at + ROM_BASE:08X}")
    print(f"pieces per frame: {[len(pieces) for pieces in per_frame]}")

    # Self-check: walk the emitted definition back out of the written image.
    out = args.out.read_bytes()
    definition = struct.unpack_from("<I", out, DEFINITION_TABLE + 4 * CELL_ID)[0] - ROM_BASE
    announced = out[definition]
    actual_slots = 0
    for index in range(64):
        position = definition + HEADER + 4 * index
        if position + 4 > len(out):
            break
        if struct.unpack_from("<I", out, position)[0]:
            actual_slots += 1
    print(f"self-check: animation count {announced}, slot pointers present {actual_slots}")
    assert announced == len(slot_pointers) == actual_slots, (announced, actual_slots)
    record = struct.unpack_from("<I", out, definition + HEADER)[0] - ROM_BASE
    frame_count = struct.unpack_from("<I", out, record)[0]
    print(f"  slot 0 -> animation record with {frame_count} frame(s)")
    for frame_index in range(frame_count):
        pointer = struct.unpack_from("<I", out, record + ANIMATION_HEADER + 16 * frame_index)[0] - ROM_BASE
        piece_count = struct.unpack_from("<I", out, pointer)[0]
        banks = set()
        for index in range(piece_count):
            entry = pointer + FRAME_HEADER + PIECE_BYTES * index
            attr = struct.unpack_from("<I", out, entry + 4)[0]
            banks.add((attr >> 25) & 7)
        print(f"  frame {frame_index}: piece_count {piece_count}, logical banks {sorted(banks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
