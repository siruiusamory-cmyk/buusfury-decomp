"""Verify the emitted three-bank Cell port: structure, palettes, and a pixel-exact comparison.

Checks, all read-only, in the order they can fail:
  1. the ROM palette table at file 0x05652C is byte-identical to the base image's;
  2. the appended palette triples in the output equal the triple search's slot maps and colours;
  3. the definition's animation count equals the number of non-null slot pointers;
  4. every frame's pieces lie inside the valid OBJ rectangle table and their containers hold exactly
     width*height bytes of packed data;
  5. unpacking every piece through its logical bank's appended palette and comparing with the LoG II
     source frame gives zero mismatched and zero missed opaque pixels.

Invoke:
  python -m tools.research.verify_triple_port --base BASE.gba --out OUT.gba --triple build/joint_triple.json
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.research.cell_split import VALID_RECT, cells_of, pack_rect, unpack_rect  # noqa: E402

ROM_BASE = 0x08000000
DEFINITION_TABLE = 0x6B6BB4
HEADER = 0x54
PIECE_BYTES = 12
FRAME_HEADER = 8
ANIMATION_HEADER = 4
CELL_ID = 252
ROM_PALETTE_TABLE = 0x5652C
LOG2_SOURCE_PALETTE = 0x081DA6C8
BANK_COUNT = 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--triple", type=Path, default=REPO / "build" / "joint_triple.json")
    parser.add_argument("--log2", type=Path,
                        default=Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z "
                                     r"- The Legacy of Goku II (USA).gba"))
    args = parser.parse_args()

    from tools.research.build_friend_v4b_cell import read_log2_cell

    base = args.base.read_bytes()
    out = args.out.read_bytes()
    failure = 0

    same_table = base[ROM_PALETTE_TABLE:ROM_PALETTE_TABLE + 0x200] == \
        out[ROM_PALETTE_TABLE:ROM_PALETTE_TABLE + 0x200]
    print(f"1. ROM palette table 0x{ROM_PALETTE_TABLE:06X} unchanged: {same_table}")
    failure += 0 if same_table else 1

    triple = json.loads(args.triple.read_text(encoding="utf-8"))
    slot_maps = [{int(value): slot for value, slot in bank.items()} for bank in triple["slot_maps"]]
    banks = [frozenset(int(value, 16) for value in bank) for bank in triple["banks"]]
    print(f"2. triple: {len(banks)} bank(s), colours {[len(bank) for bank in banks]}")

    definition = struct.unpack_from("<I", out, DEFINITION_TABLE + 4 * CELL_ID)[0] - ROM_BASE
    announced = out[definition]
    slot_pointers = []
    for index in range(64):
        position = definition + HEADER + 4 * index
        if position + 4 > len(out):
            break
        pointer = struct.unpack_from("<I", out, position)[0]
        if pointer:
            slot_pointers.append(pointer)
    print(f"3. definition 0x{definition + ROM_BASE:08X}: animation count {announced}, "
          f"non-null slot pointers {len(slot_pointers)} "
          f"{'OK' if announced == len(slot_pointers) else 'MISMATCH'}")
    failure += 0 if announced == len(slot_pointers) else 1

    # The appended palettes' addresses come from the emitter's own manifest, not from a guess at the
    # layout: an earlier version of this verifier inferred them as `definition - N*32` and reported 45
    # false mismatches against a correct image.
    manifest_path = args.out.with_suffix(".json")
    if not manifest_path.exists():
        print(f"4. the emitter manifest {manifest_path} is missing: cannot locate the appended palettes")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    appended = []
    for address in manifest["palettes_at"]:
        offset = address - ROM_BASE
        appended.append([struct.unpack_from("<H", out, offset + 2 * slot)[0] for slot in range(16)])
    print(f"   appended palettes at "
          f"{[hex(address) for address in manifest['palettes_at']]} from the emitter manifest")
    for bank, mapping in enumerate(slot_maps):
        for colour, slot in mapping.items():
            expected = triple["palettes"][bank][slot - 1]
            got = f"0x{appended[bank][slot]:04X}"
            if got != expected:
                print(f"   bank {bank} slot {slot}: expected {expected}, found {got}")
                failure += 1
    print(f"   appended palettes "
          f"{'match the triple' if failure == 0 else 'MISMATCH'}")

    log2 = args.log2.read_bytes()
    slots, payloads = read_log2_cell(log2)
    if len(slot_pointers) != 1:
        print(f"4. expected exactly one animation slot for this port, found {len(slot_pointers)}")
        failure += 1
    record = struct.unpack_from("<I", out, definition + HEADER)[0] - ROM_BASE
    frame_count = struct.unpack_from("<I", out, record)[0]
    mismatch = 0
    missed = 0
    opaque = 0
    for frame_index in range(frame_count):
        pointer = struct.unpack_from("<I", out, record + ANIMATION_HEADER + 16 * frame_index)[0] - ROM_BASE
        piece_count = struct.unpack_from("<I", out, pointer)[0]
        source = payloads[slots[frame_index][0][5]]
        size = slots[frame_index][0][2]
        covered = set()
        for index in range(piece_count):
            entry = pointer + FRAME_HEADER + PIECE_BYTES * index
            x, y, width, height = struct.unpack_from("<bbBB", out, entry)
            attr = struct.unpack_from("<I", out, entry + 4)[0]
            bank = (attr >> 25) & 7
            container = struct.unpack_from("<I", out, entry + 8)[0] - ROM_BASE
            if (width, height) not in VALID_RECT:
                print(f"   frame {frame_index} piece {index}: invalid rectangle {(width, height)}")
                failure += 1
            body = out[container + 8:container + 8 + width * height // 2]
            if len(body) != width * height // 2:
                print(f"   frame {frame_index} piece {index}: short container")
                failure += 1
                continue
            inverse = {slot: value for value, slot in slot_maps[bank].items()}
            inverse[0] = 0
            decoded = unpack_rect(body, x, y, width, height, inverse)
            for tile_y in range(y, y + height, 8):
                for tile_x in range(x, x + width, 8):
                    for row in range(8):
                        for column in range(8):
                            px, py = tile_x + column, tile_y + row
                            covered.add((px, py))
                            value = source[py * size + px]
                            if not value:
                                continue
                            opaque += 1
                            if decoded.get((px, py)) != value:
                                mismatch += 1
        gaps = sum(1 for py in range(size) for px in range(size)
                   if source[py * size + px] and (px, py) not in covered)
        missed += gaps
        print(f"   frame {frame_index}: {piece_count} piece(s), mismatch {mismatch}, gaps {gaps}")
    print(f"4/5. opaque pixels {opaque}, mismatched {mismatch}, gaps {missed}")
    failure += mismatch + missed

    print("VERDICT:", "PASS" if failure == 0 else f"FAIL ({failure} finding(s))")
    return 0 if failure == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
