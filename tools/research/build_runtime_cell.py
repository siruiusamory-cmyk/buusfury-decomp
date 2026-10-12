"""Build a runnable Cell image: triple art, a visible placement, and the ONE-SHOT runtime palette write.

Steps, all deterministic and printed:
  1. take the triple emitter's image (the only one whose art is pixel-exact);
  2. redirect one visible placement in map 137 to Cell's id, so he is on screen;
  3. move each piece's logical bank (0/1/2) to palette index 1/2/3, because index 0 means "every retail
     piece" to the draw-loop body and is left alone;
  4. append the three 32-byte palette blocks, one per logical bank;
  5. assemble the one-shot picker/writer just above them and hook the scene palette loader's OBJ copy, so
     the palettes are written once, after the scene's own 512-byte load;
  6. assemble the draw-loop body, which resolves a piece's index through the markers the one-shot left, and
     patch the draw-loop block plus the loop's attr1 clear.

NO BANK IS CHOSEN HERE. The picker chooses the three banks at runtime from the palette indices the visible
OAM entries paint; this builder only writes down where the palettes are and what the marker looks like.

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
from tools.research import palette_oneshot as oneshot  # noqa: E402
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
BANKS = 3


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


def raise_piece_indices(image: bytearray) -> list[tuple[int, int, int]]:
    """Move each piece's logical bank 0/1/2 to the palette index 1/2/3 the body resolves at runtime."""
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
            if logical >= BANKS:
                raise SystemExit(f"frame {index} piece {piece}: logical bank {logical} is not one of "
                                 f"the {BANKS} ported banks")
            struct.pack_into("<I", image, attr_offset, (attr & ~(7 << 25)) | ((logical + 1) << 25))
            rewritten.append((index, piece, logical + 1))
    return rewritten


def palette_block(entries: list[str]) -> bytes:
    """One 32-byte bank: slot 0 stays transparent, the colours fill slots 1 upward."""
    block = [0] * writer.BANK_COUNT
    for slot, entry in enumerate(entries, start=1):
        block[slot] = int(entry, 16)
    return b"".join(struct.pack("<H", value) for value in block)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", type=Path, default=REPO / "build" / "c1-triple.gba")
    parser.add_argument("--triple", type=Path, default=REPO / "build" / "joint_triple.json")
    parser.add_argument("--out", type=Path, default=REPO / "build" / "cell-oneshot.gba")
    parser.add_argument("--minimum-used", type=int, default=oneshot.DEFAULT_MINIMUM_USED,
                        help="marked banks below which the OAM is treated as not composed (nothing written)")
    args = parser.parse_args()

    triple = json.loads(args.triple.read_text(encoding="utf-8"))
    if len(triple["palettes"]) != BANKS:
        raise SystemExit(f"the triple names {len(triple['palettes'])} palette(s), expected {BANKS}")

    image = bytearray(args.image.read_bytes())
    print(f"source {args.image.name} {len(image)} bytes sha256 "
          f"{hashlib.sha256(bytes(image)).hexdigest()}")

    changed = redirect_placement(image)
    if not changed:
        raise SystemExit("no visible placement to redirect: the actor would not be on screen")
    print(f"placement redirected to id {CELL_ID} at "
          f"{[f'file 0x{offset:X}' for offset, _ in changed]}")

    rewritten = raise_piece_indices(image)
    counts = {index: sum(1 for _, _, value in rewritten if value == index) for index in range(1, BANKS + 1)}
    print(f"piece indices raised to 1..{BANKS}: {len(rewritten)} piece(s) -> {counts}")

    while len(image) % 4:
        image.append(0)
    palettes_address = len(image) + ROM_BASE
    for index in range(BANKS):
        image.extend(palette_block(triple["palettes"][index]))
    print(f"palettes at 0x{palettes_address:08X} ({BANKS} x {writer.BANK_BYTES} bytes)")

    while len(image) % 4:
        image.append(0)
    oneshot_address = len(image) + ROM_BASE
    code = oneshot.assemble(oneshot_address, palettes_address, args.minimum_used)
    image.extend(code)
    print(f"one-shot at 0x{oneshot_address:08X} ({len(code)} bytes), "
          f"minimum marked banks {args.minimum_used}")

    replaced = oneshot.hook(image, oneshot_address)
    print(f"scene palette loader 0x{oneshot.HOOK_SITE:08X} OBJ copy replaced: {replaced.hex(' ')} "
          f"-> bl 0x{oneshot_address:08X}")

    while len(image) % 4:
        image.append(0)
    body_address = len(image) + ROM_BASE
    body = writer.assemble(body_address)
    print(f"draw-loop body at 0x{body_address:08X} ({len(body)} bytes), marker 0x{writer.MARKER_BASE:04X}")

    # `patch` appends the body itself, so nothing here extends the image with it.
    stub_address, replaced = patch.patch(image, body=body)
    if stub_address + ROM_BASE != body_address:
        raise SystemExit(f"the stub landed at 0x{stub_address + ROM_BASE:08X}, expected the body's "
                         f"0x{body_address:08X}")
    print(f"draw-loop block 0x{patch.BLOCK_SITE:08X} replaced: {replaced.hex(' ')}")
    patch.patch_index_carrier(image)
    print(f"attr1 clear 0x{patch.INDEX_CLEAR_SITE:08X} narrowed: "
          f"{patch.EXPECTED_INDEX_CLEAR.hex(' ')} -> {patch.INDEX_CLEAR_PATCH.hex(' ')}")

    args.out.write_bytes(bytes(image))
    print(f"wrote {args.out} ({len(image)} bytes) sha256 {hashlib.sha256(bytes(image)).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
