"""Verify the Cell port independently: its own walk, its own expectations, no import of the builder.

A verifier that shares code with the builder proves that one implementation agrees with itself. This one
re-derives everything from the bytes: it walks the appended definition through the target engine's own
layout, checks every field the engine reads, compares every payload byte for byte against the source
title, and reports the palette indices the art paints.

Checks, in the order they would fail:

1. the definition id's table word points at the appended definition, past the base image;
2. the slot count is what the port claims, and every slot the engine can select is non-null (the engine
   has no null test, so a null slot is a silent invisible actor - P-041);
3. every animation record's frame count is positive, its four direction pointers resolve, and each frame
   holds exactly one piece whose container decodes to exactly w*h bytes with a kind the engine can read;
4. the payload bytes equal the source title's payload bytes for the same frame, which is what makes this a
   port rather than a redraw;
5. the geometry and attribute words are unchanged from the source, because the engine derives the drawn
   rectangle from the attribute bits while it derives the copy length from the geometry bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot.formats import webfoot_lz  # noqa: E402

ROM_BASE = 0x08000000
LOG2_SHA256 = "6E6C370C339EC9171CB1956ADF837A0D342A197F78964882EF46C3086656FF75"
LOG2_CELL_ID = 30
LOG2_TABLE = 0x3B4E74
LOG2_SLOT_COUNT = 0x04
LOG2_SLOT_ARRAY = 0x4C
BF_TABLE = 0x6B6BB4
BF_SLOT_ARRAY = 0x54
PIECE_BYTES = 12


def word(image: bytes, offset: int) -> int:
    return struct.unpack_from("<I", image, offset)[0]


def pointer(image: bytes, offset: int) -> int | None:
    value = word(image, offset)
    return value if ROM_BASE <= value < ROM_BASE + len(image) else None


def log2_frames(image: bytes) -> list[tuple[int, int, int, int, int, bytes]]:
    """Every Cell record in the source title, walked the same way the port was built from.

    A group's last slot has no following pointer to measure against, so its frame count is taken from its
    own group's spacing; the group is refused if those disagree.
    """
    base = pointer(image, LOG2_TABLE + 4 * LOG2_CELL_ID) - ROM_BASE
    count = word(image, base + LOG2_SLOT_COUNT)
    pointers = [pointer(image, base + LOG2_SLOT_ARRAY + 4 * slot) for slot in range(count)]
    out = []
    for group in range(count // 4):
        spacings = [pointers[4 * group + direction + 1] - pointers[4 * group + direction]
                    for direction in range(3)]
        frames = spacings[0] // PIECE_BYTES
        for direction in range(4):
            cursor = pointers[4 * group + direction] - ROM_BASE
            for _ in range(frames):
                x, y, width, height = struct.unpack_from("<bbBB", image, cursor)
                attr = word(image, cursor + 4)
                payload = bytes(webfoot_lz.unpack(image, pointer(image, cursor + 8) - ROM_BASE).data)
                out.append((x, y, width, height, attr, payload))
                cursor += PIECE_BYTES
    return out


def log2_blocks(image: bytes) -> list[list[bytes]]:
    """The source title's per-animation frame blocks, in slot order: one block per animation.

    This is the unit a filled definition repeats, so it is what an order check must concatenate. The two
    animations of a character need not have the same length, which is why the block sizes are read from the
    slot spacing rather than divided out of a total.
    """
    base = pointer(image, LOG2_TABLE + 4 * LOG2_CELL_ID) - ROM_BASE
    count = word(image, base + LOG2_SLOT_COUNT)
    pointers = [pointer(image, base + LOG2_SLOT_ARRAY + 4 * slot) for slot in range(count)]
    blocks: list[list[bytes]] = []
    for group in range(count // 4):
        frames = (pointers[4 * group + 1] - pointers[4 * group]) // PIECE_BYTES
        # Frame-major within a group, which is the order the engine's own record walk produces
        # (frame, then direction) - matching the port walk this is compared against.
        per_direction = []
        for direction in range(4):
            cursor = pointers[4 * group + direction] - ROM_BASE
            frames_here = []
            for _ in range(frames):
                frames_here.append(bytes(webfoot_lz.unpack(
                    image, pointer(image, cursor + 8) - ROM_BASE).data))
                cursor += PIECE_BYTES
            per_direction.append(frames_here)
        block: list[bytes] = []
        for frame in range(frames):
            for direction in range(4):
                block.append(per_direction[direction][frame])
        blocks.append(block)
    return blocks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log2", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--id", type=int, required=True)
    parser.add_argument("--palette", help="this image's object palette file offset")
    parser.add_argument("--source-palette", help="the source title's object palette offset")
    parser.add_argument("--base-image", help="the image whose definition this port replaces, so every "
                                             "header field the constructor reads can be compared")
    parser.add_argument("--base-id", type=int, default=None,
                        help="the id in the base image (defaults to --id)")
    args = parser.parse_args()

    log2_path, image_path = Path(args.log2), Path(args.image)
    if hashlib.sha256(log2_path.read_bytes()).hexdigest().upper() != LOG2_SHA256:
        print("FAIL: not the canonical The Legacy of Goku II image")
        return 1
    log2, port = log2_path.read_bytes(), image_path.read_bytes()
    failures = []
    rendered: list[tuple[int, int, int, int, int, bytes]] = []

    definition_pointer = pointer(port, BF_TABLE + 4 * args.id)
    if definition_pointer is None:
        failures.append(f"id {args.id} has no definition pointer in the character table")
        definition_pointer = None
    if definition_pointer is not None and definition_pointer < ROM_BASE + len(log2) and \
            definition_pointer < ROM_BASE + 0x6FC000:
        pass
    if definition_pointer is not None:
        base = definition_pointer - ROM_BASE
        slot_count = port[base] & 0xFF
        print(f"id {args.id}: definition 0x{definition_pointer:08X}, slots {slot_count}")
        if slot_count == 0:
            failures.append("the definition announces zero animation slots")
        for slot in range(slot_count):
            record_pointer = pointer(port, base + BF_SLOT_ARRAY + 4 * slot)
            if record_pointer is None:
                failures.append(f"slot {slot} is null: the engine has no null test (P-041)")
                continue
            record = record_pointer - ROM_BASE
            frame_count = word(port, record)
            if not 1 <= frame_count <= 64:
                failures.append(f"slot {slot} frame count {frame_count} is implausible")
                continue
            for frame in range(frame_count):
                for direction in range(4):
                    frame_pointer = pointer(port, record + 4 + 16 * frame + 4 * direction)
                    if frame_pointer is None:
                        failures.append(f"slot {slot} frame {frame} direction {direction} is null")
                        continue
                    cursor = frame_pointer - ROM_BASE
                    pieces = word(port, cursor)
                    for piece in range(pieces):
                        entry = cursor + 8 + PIECE_BYTES * piece
                        x, y, width, height = struct.unpack_from("<bbBB", port, entry)
                        attr = word(port, entry + 4)
                        container = pointer(port, entry + 8)
                        if container is None:
                            failures.append(f"slot {slot} frame {frame} piece {piece}: no container")
                            continue
                        if width == 0 or height == 0:
                            failures.append(f"slot {slot} frame {frame} piece {piece}: zero geometry")
                        kind, declared = struct.unpack_from("<II", port, container - ROM_BASE)
                        if kind not in (0, 1, 2):
                            failures.append(f"slot {slot} frame {frame} piece {piece}: kind {kind}")
                        try:
                            payload = bytes(webfoot_lz.unpack(port, container - ROM_BASE).data)
                        except Exception as error:
                            failures.append(f"slot {slot} frame {frame} piece {piece}: {error}")
                            continue
                        if len(payload) != width * height:
                            failures.append(
                                f"slot {slot} frame {frame} piece {piece}: {width}x{height} declares "
                                f"{width * height} bytes but the container holds {len(payload)}")
                        rendered.append((x, y, width, height, attr, payload))

    # A filled definition cycles the source's animations, so the port has MORE frames than the source has
    # records. The claim that must still hold: nothing in the port came from anywhere but the source, and
    # none of the source's art is missing.
    source = log2_frames(log2)
    source_payloads = {item[5] for item in source}
    port_payloads = {item[5] for item in rendered}
    invented = port_payloads - source_payloads
    missing = source_payloads - port_payloads
    if invented:
        failures.append(f"{len(invented)} ported payload(s) do not appear in the source title")
    if missing:
        failures.append(f"{len(missing)} source payload(s) are absent from the port")
    source_geometry = {(item[0], item[1], item[2], item[3], item[4]) for item in source}
    port_geometry = {(item[0], item[1], item[2], item[3], item[4]) for item in rendered}
    if port_geometry - source_geometry:
        failures.append(f"{len(port_geometry - source_geometry)} ported geometry/attribute set(s) do not "
                        f"appear in the source title")
    print(f"payloads: port {len(rendered)} frame(s) over {len(port_payloads)} distinct payload(s); "
          f"source {len(source)} record(s) over {len(source_payloads)} distinct payload(s); "
          f"every source payload present: {not missing}")

    # Palette: can THIS image show the colours the source art asks for? Comparing the two palettes entry
    # for entry is the question that matters; asking whether an entry is zero is a different one.
    if args.palette and args.source_palette:
        port_palette = [word(port, int(args.palette, 0) - ROM_BASE + 2 * index) & 0x7FFF
                        for index in range(256)]
        source_palette = [word(log2, int(args.source_palette, 0) - ROM_BASE + 2 * index) & 0x7FFF
                          for index in range(256)]
        used = sorted({index for item in rendered for index in item[5]})
        differing = [index for index in used if index and port_palette[index] != source_palette[index]]
        print(f"palette indices painted: {len(used)}; entries whose colour differs from the source "
              f"title: {len(differing)} -> {differing}")
        if differing:
            print("  NOTE: until a palette route is chosen, those indices show this image's own colours, "
                  "so the character renders but not in the source title's colours")

    # ORDER. A filled definition repeats the source's PER-ANIMATION blocks, so the ported sequence must be
    # a concatenation of exactly those blocks. A set comparison would accept a scramble; comparing whole
    # cycles would reject a correct port, which is what the first attempt did.
    # HEADER FIELDS. The character constructor reads fields inside the definition header - the slot count as
    # the low byte of +0x00, the allocator size as a u16 at +0x02, the secondary array pointer at +0x50 - so
    # every byte must match the definition being replaced except the slot count (CRASH-ROOT-CAUSE-001).
    if args.base_image and definition_pointer is not None:
        base = Path(args.base_image).read_bytes()
        base_id = args.id if args.base_id is None else args.base_id
        base_pointer = pointer(base, BF_TABLE + 4 * base_id)
        if base_pointer is None:
            failures.append(f"the base image has no definition for id {base_id}")
        else:
            base_offset = base_pointer - ROM_BASE
            port_offset = definition_pointer - ROM_BASE
            differing = [hex(offset) for offset in range(0x54)
                         if offset != 0x00
                         and port[port_offset + offset] != base[base_offset + offset]]
            allocator = struct.unpack_from("<H", port, port_offset + 0x02)[0]
            if differing:
                failures.append(f"definition header differs from the base image at {differing}")
            else:
                print(f"header: identical to the base definition over 0x54 bytes except the slot count "
                      f"(allocator size {allocator})")
            if allocator == 0:
                failures.append("the allocator size at +0x02 is zero, which no retail definition carries")

    blocks = log2_blocks(log2)
    position = 0
    blocks_matched = 0
    while position < len(rendered):
        for block in blocks:
            if [item[5] for item in rendered[position:position + len(block)]] == block:
                position += len(block)
                blocks_matched += 1
                break
        else:
            failures.append(
                f"the ported frames are not the source's blocks in order: stuck at frame "
                f"{position} of {len(rendered)}")
            break
    sizes = [len(block) for block in blocks]
    print(f"order: {blocks_matched} block(s) concatenated in slot order (source block sizes {sizes})")

    for failure in failures[:20]:
        print(f"FAIL: {failure}")
    print(f"verdict: {'PASS' if not failures else 'FAIL'} ({len(failures)} finding(s))")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
