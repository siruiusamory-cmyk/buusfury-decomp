"""Build a runnable Cell image: triple art, a visible placement, and the runtime palette writer.

Steps, all deterministic and printed:
  1. take the triple emitter's image (the only one whose art is pixel-exact);
  2. redirect one visible placement in map 137 to Cell's id, so he is on screen in the owner's state;
  3. rewrite the animation record's piece bank bits from the logical 0/1/2 to the physical banks the writer
     will fill, so a free bank is used rather than bank 0, which the scene's other actors select;
  4. append the writer's address table and palettes, assemble the writer body, and patch the draw-loop
     block to jump to it;
  5. fill the named physical banks with the triple's palettes.

Read-only with respect to the canonical ROM: it reads a local image and writes a new local image.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.research import oam_bank_patch as patch  # noqa: E402
from tools.research import palette_writer as writer  # noqa: E402

ROM_BASE = 0x08000000
TABLE = 0x6B6BB4
HEADER = 0x54
CELL_ID = 252
MAP_TABLE = 0x8E2E0
MAP_STRIDE = 0x38
MAP = 137
VISIBLE_IDS = (158, 166, 222)
FAMILIES = {0x0800FD55: 0x10, 0x080111A9: 0x0C, 0x08017DA3: 0x10}


def word(image: bytes, offset: int) -> int:
    return struct.unpack_from("<I", image, offset)[0]


def redirect_placement(image: bytearray) -> list[tuple[int, int]]:
    """Point a visible map-137 placement at Cell's id, so the ported actor is on screen."""
    entry = MAP_TABLE + MAP_STRIDE * MAP
    count = word(image, entry + 0x04)
    array = word(image, entry + 0x14)
    base = array - ROM_BASE
    changed = []
    for slot in range(min(count, 256)):
        record = word(image, base + 4 * slot)
        if not (ROM_BASE <= record < ROM_BASE + len(image)):
            continue
        offset = record - ROM_BASE
        factory = word(image, offset)
        if factory not in FAMILIES:
            continue
        id_offset = offset + FAMILIES[factory]
        if word(image, id_offset) in VISIBLE_IDS:
            struct.pack_into("<I", image, id_offset, CELL_ID)
            changed.append((offset, id_offset))
    return changed


def rewrite_piece_banks(image: bytearray, mapping: dict[int, int]) -> list[tuple[int, int, int]]:
    """Move each piece's bank bits from the logical bank to the physical bank the writer fills."""
    definition = word(image, TABLE + 4 * CELL_ID) - ROM_BASE
    slot0 = word(image, definition + HEADER)
    if slot0 == 0:
        raise SystemExit("the Cell definition's slot 0 is null: nothing would be drawn")
    record = slot0 - ROM_BASE
    frames = word(image, record)
    rewritten = []
    for index in range(frames):
        pointer = word(image, record + 4 + 16 * index) - ROM_BASE
        count = word(image, pointer)
        for piece in range(count):
            entry = pointer + 8 + 12 * piece
            attr_offset = entry + 4
            attr = word(image, attr_offset)
            logical = (attr >> 25) & 7
            if logical not in mapping:
                raise SystemExit(f"frame {index} piece {piece}: logical bank {logical} has no physical bank")
            physical = mapping[logical]
            struct.pack_into("<I", image, attr_offset, (attr & ~(7 << 25)) | (physical << 25))
            rewritten.append((index, piece, physical))
    return rewritten


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", type=Path, default=REPO / "build" / "c1-triple.gba")
    parser.add_argument("--triple", type=Path, default=REPO / "build" / "joint_triple.json")
    parser.add_argument("--out", type=Path, default=REPO / "build" / "cell-runtime.gba")
    parser.add_argument("--banks", default="8,10,11",
                        help="physical bank for logical A,B,C; must be free in the scene")
    args = parser.parse_args()

    triple = json.loads(args.triple.read_text(encoding="utf-8"))
    physical = [int(text) for text in args.banks.split(",")]
    if len(physical) != 3 or len(triple["palettes"]) != 3:
        raise SystemExit("three physical banks and three palettes are required")
    mapping = {0: physical[0], 1: physical[1], 2: physical[2]}

    image = bytearray(args.image.read_bytes())
    print(f"source {args.image.name} {len(image)} bytes sha256 "
          f"{hashlib.sha256(bytes(image)).hexdigest()}")

    changed = redirect_placement(image)
    if not changed:
        raise SystemExit("no visible placement to redirect: the actor would not be on screen")
    print(f"placement redirected to id {CELL_ID} at "
          f"{[f'file 0x{offset:X}' for offset, _ in changed]}")

    rewritten = rewrite_piece_banks(image, mapping)
    counts = {bank: sum(1 for _, _, value in rewritten if value == bank) for bank in physical}
    print(f"piece bank bits rewritten: {len(rewritten)} piece(s) -> {counts}")

    while len(image) % 8:
        image.append(0)
    table_address = len(image) + ROM_BASE
    image.extend(writer.build_table(table_address))

    while len(image) % 4:
        image.append(0)
    body_address = len(image) + ROM_BASE
    body = writer.assemble(body_address, table_address)
    print(f"table at 0x{table_address:08X} ({writer.TABLE_BYTES + 16 * 32} bytes), "
          f"body at 0x{body_address:08X} ({len(body)} bytes)")

    # `patch` appends the body itself, so nothing here extends the image with it: the earlier revision did,
    # and patch then appended a second copy, which the assertion below caught by naming both addresses.
    stub_address, replaced = patch.patch(image, body=body)
    if stub_address + ROM_BASE != body_address:
        raise SystemExit(f"the stub landed at 0x{stub_address + ROM_BASE:08X}, expected the body's "
                         f"0x{body_address:08X}")
    print(f"draw-loop block 0x{patch.BLOCK_SITE:08X} replaced: {replaced.hex(' ')}")

    palettes = {}
    for index, bank in enumerate(physical):
        block = [0] * 16
        for slot, entry in enumerate(triple["palettes"][index], start=1):
            block[slot] = int(entry, 16)
        palettes[bank] = b"".join(struct.pack("<H", value) for value in block)
    writer.fill_palettes(image, table_address, palettes)
    for bank in physical:
        print(f"  physical bank {bank}: {palettes[bank].hex(' ')}")

    args.out.write_bytes(bytes(image))
    print(f"wrote {args.out} ({len(image)} bytes) sha256 {hashlib.sha256(bytes(image)).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
