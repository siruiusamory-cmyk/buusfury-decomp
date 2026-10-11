"""Port Perfect Cell's art from The Legacy of Goku II into the Buu's Fury derivative (release 4B).

TWO ROMs, both read-only, and the canonical Buu's Fury image is never written: the output is a new file
under an ignored build path.

WHY THIS IS MOSTLY TRANSLATION AND NOT CONVERSION. The two titles share the engine and the container
codec, and their PIECE records are the same 12 bytes `{s8 x, s8 y, u8 w, u8 h, u32 attr, u32 container}`.
What differs is the layer above:

The Legacy of Goku II: structure at `def`, slot count at `def+0x04`, slot pointer array at `def+0x4C`,
and a slot points at a contiguous run of 12-byte piece records. Measured for Cell: 8 slots, which is
2 animations x 4 directions, with 2 records in slots 0-3 and 4 in slots 4-7.

Buu's Fury: slot count is the LOW BYTE of `def+0x00`, the slot array is at `def+0x54`, and a slot points
at an animation record of `u32 frame_count` then `frame_count` blocks of 16 bytes, one pointer per
direction, the frame for (frame, direction) being at `record + 4 + 16*frame + 4*dir`. A frame is
`u32 piece_count` then a 4-byte union box then `piece_count` 12-byte pieces.

So each LoG II record becomes one Buu's Fury frame holding exactly one piece, and the direction/frame
indexing lines up slot for slot. Cell is 64x64 in both titles, one piece per frame, so no piece has to be
composed or split.

WHAT THIS DELIBERATELY DOES NOT DO. It does not choose which encounter shows Cell: that is a story
decision, so the caller names the definition id to repoint. It does not touch palettes: Cell paints seven
indices that have no colour in this image's object palette, which is the palette route the coordinator is
choosing. And it stores each container UNPACKED (kind 0, which the engine reads straight from the header),
so it needs no packer and the appended region is larger than a packed build would be.
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
LOG2_DEFINITION_TABLE = 0x3B4E74
LOG2_SLOT_COUNT_OFFSET = 0x04
LOG2_SLOT_ARRAY_OFFSET = 0x4C

BF_DEFINITION_TABLE = 0x6B6BB4
BF_SLOT_COUNT_OFFSET = 0x00
BF_SLOT_ARRAY_OFFSET = 0x54
BF_SECONDARY_ARRAY_OFFSET = 0x50
#: The definition header's length. The character constructor reads fields inside it - the slot count as the
#: low byte of +0x00, the allocator BYTE SIZE at +0x02, the secondary array pointer at +0x50 - so a
#: replacement carries the header of the definition it replaces. A zero-filled header is CRASH-ROOT-CAUSE-001:
#: +0x02 = 0 is a value none of the 297 retail definitions carries.
BF_DEFINITION_HEADER = 0x54
NAME_TEXT_TABLE = 0x123CC
NAME_TEXT_SLOT = 1018
PIECE_BYTES = 12
FRAME_HEADER_BYTES = 8
ANIMATION_HEADER_BYTES = 4


class CellPortError(Exception):
    """A refusal: the input is not what this tool measured, so the port would be a guess."""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def pointer_at(image: bytes, offset: int) -> int | None:
    if offset + 4 > len(image):
        return None
    word = struct.unpack_from("<I", image, offset)[0]
    return word if ROM_BASE <= word < ROM_BASE + len(image) else None


def read_log2_cell(image: bytes) -> tuple[list[list[tuple[int, int, int, int, int, int]]], list[bytes]]:
    """Cell's animation slots from the LoG II image, with each piece's container payload resolved.

    Returns one list per LoG II slot, each holding `(x, y, w, h, attr, payload)` in frame order, plus the
    distinct payloads. A slot's run ends when the next 12-byte record does not carry a decodable container
    pointer, which is measured rather than assumed from a per-slot count.
    """
    definition = pointer_at(image, LOG2_DEFINITION_TABLE + 4 * LOG2_CELL_ID)
    if definition is None:
        raise CellPortError("the LoG II definition table has no pointer for id 30")
    base = definition - ROM_BASE
    slot_count = struct.unpack_from("<I", image, base + LOG2_SLOT_COUNT_OFFSET)[0]
    if not 1 <= slot_count <= 32:
        raise CellPortError(f"implausible slot count {slot_count} for id 30")

    # A slot's run length comes from the SPACING to the next slot, measured, not from walking while a
    # container pointer happens to resolve: that walk over-read into neighbouring records (it reported
    # 8/6/4/2 frames for the four directions of one animation). The four directions of an animation must
    # share a frame count in the target engine, so the three within-group spacings agree or this refuses.
    slot_pointers = []
    for slot in range(slot_count):
        pointer = pointer_at(image, base + LOG2_SLOT_ARRAY_OFFSET + 4 * slot)
        if pointer is None:
            raise CellPortError(f"slot {slot} of id 30 names no record")
        slot_pointers.append(pointer)
    if slot_count % 4 != 0:
        raise CellPortError(f"expected a multiple of four slots (animations x directions), got {slot_count}")

    slots: list[list[tuple[int, int, int, int, int, int]]] = []
    payloads: list[bytes] = []
    payload_index: dict[bytes, int] = {}
    for group in range(slot_count // 4):
        spacings = [slot_pointers[4 * group + direction + 1] - slot_pointers[4 * group + direction]
                    for direction in range(3)]
        if len(set(spacings)) != 1 or spacings[0] % PIECE_BYTES:
            raise CellPortError(
                f"animation {group} has inconsistent slot spacing {spacings}; its four directions must "
                f"share one frame count and their records must be contiguous")
        frames = spacings[0] // PIECE_BYTES
        if not 1 <= frames <= 32:
            raise CellPortError(f"animation {group} implies {frames} frames per direction")
        for direction in range(4):
            pointer = slot_pointers[4 * group + direction]
            cursor = pointer - ROM_BASE
            pieces = []
            for _ in range(frames):
                if cursor + PIECE_BYTES > len(image):
                    raise CellPortError(f"slot {4 * group + direction} runs past the image")
                x, y, width, height = struct.unpack_from("<bbBB", image, cursor)
                attr = struct.unpack_from("<I", image, cursor + 4)[0]
                container = pointer_at(image, cursor + 8)
                if container is None:
                    raise CellPortError(
                        f"slot {4 * group + direction} record {len(pieces)} names no container")
                try:
                    payload = bytes(webfoot_lz.unpack(image, container - ROM_BASE).data)
                except Exception as error:
                    raise CellPortError(
                        f"slot {4 * group + direction} record {len(pieces)} container at "
                        f"0x{container:08X} does not decode: {error}") from error
                if len(payload) != width * height:
                    raise CellPortError(
                        f"slot {4 * group + direction} record {len(pieces)} declares {width}x{height} "
                        f"but its container holds {len(payload)} bytes")
                if payload not in payload_index:
                    payload_index[payload] = len(payloads)
                    payloads.append(payload)
                pieces.append((x, y, width, height, attr, payload_index[payload]))
                cursor += PIECE_BYTES
            slots.append(pieces)
    return slots, payloads


def build_port(slots, payloads, image: bytes, header: bytes,
               slot_count: int | None = None) -> tuple[bytes, dict]:
    """Append payloads, frames, animations and the definition; fill `slot_count` slots if given.

    `slot_count` mirrors the definition being replaced: Spopovich announces 20 slots, so a two-animation
    replacement cycles its animations across all 20 and no selectable index is left empty.
    """
    out = bytearray(image)
    container_at: dict[int, int] = {}
    for index, payload in enumerate(payloads):
        container_at[index] = len(out)
        out += struct.pack("<II", 0, len(payload))       # kind 0: the engine reads the payload in place
        out += payload

    animations = len(slots) // 4
    total_slots = slot_count or animations
    animation_addresses = []
    slot_sources = []
    for slot in range(total_slots):
        animation = slot % animations
        slot_sources.append(animation)
        directions = [slots[4 * animation + direction] for direction in range(4)]
        frame_count = max(len(records) for records in directions)
        for records in directions:
            if len(records) != frame_count:
                raise CellPortError(
                    f"animation {animation} has directions with different frame counts "
                    f"({[len(r) for r in directions]}); the target engine shares one count across directions")
        # Each direction owns its frames; the animation record then lists four pointers per frame.
        direction_frames: list[list[int]] = []
        for records in directions:
            addresses = []
            for x, y, width, height, attr, payload_index in records:
                addresses.append(len(out))
                out += struct.pack("<I", 1)                       # one piece
                out += struct.pack("<bbBB", x, y, width, height)  # the union box
                out += struct.pack("<bbBB", x, y, width, height)  # the piece's own box
                out += struct.pack("<I", attr)
                out += struct.pack("<I", ROM_BASE + container_at[payload_index])
            direction_frames.append(addresses)
        record_address = len(out)
        out += struct.pack("<I", frame_count)
        for frame in range(frame_count):
            for direction in range(4):
                out += struct.pack("<I", ROM_BASE + direction_frames[direction][frame])
        animation_addresses.append(record_address)

    definition_address = len(out)
    # The header comes from the definition being replaced, so every constructor-read field keeps the value
    # this actor's own definition carries; only the slot count is ours to set.
    if len(header) != BF_DEFINITION_HEADER:
        raise CellPortError(f"the donor header is {len(header)} bytes, expected {BF_DEFINITION_HEADER}")
    out += header
    # ONLY the low byte of +0x00 is the slot count: packing a u32 here would clobber the allocator size
    # field at +0x02, which is exactly the crash-class defect this fix exists to remove.
    out[definition_address + BF_SLOT_COUNT_OFFSET] = total_slots & 0xFF
    for animation, record_address in enumerate(animation_addresses):
        out += struct.pack("<I", ROM_BASE + record_address)

    report = {
        "payloads": len(payloads),
        "animations": animations,
        "slots": total_slots,
        "slot_sources": ",".join(str(source) for source in slot_sources),
        "definition": ROM_BASE + definition_address,
        "animation_records": [ROM_BASE + address for address in animation_addresses],
        "appended_bytes": len(out) - len(image),
    }
    return bytes(out), report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log2", required=True)
    parser.add_argument("--image", required=True, help="the Buu's Fury derivative image to extend")
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--id", type=int, required=True, help="definition id to repoint at the port")
    parser.add_argument("--slots", type=int, default=0,
                        help="fill this many animation slots, cycling Cell's animations; the definition "
                             "being replaced announces 20, so an empty index cannot be selected")
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    log2_path = Path(args.log2)
    digest = sha256_of(log2_path)
    if digest != LOG2_SHA256:
        raise CellPortError(f"REFUSED: {log2_path} is {digest}, expected {LOG2_SHA256}")
    log2 = log2_path.read_bytes()

    image_path = Path(args.image)
    image_digest = sha256_of(image_path)
    if image_digest != args.expect_sha256.lower() and image_digest.upper() != args.expect_sha256.upper():
        raise CellPortError(f"REFUSED: {image_path} is {image_digest}, expected {args.expect_sha256}")
    image = image_path.read_bytes()

    if not 10 <= args.id <= 306:
        raise CellPortError("the definition id must be one the resolver reads from the table (10..306)")

    slots, payloads = read_log2_cell(log2)
    print(f"LoG II Cell: {len(slots)} slot(s), {sum(len(s) for s in slots)} record(s), "
          f"{len(payloads)} distinct container(s), payload bytes {sum(len(p) for p in payloads)}")

    base_pointer = pointer_at(image, BF_DEFINITION_TABLE + 4 * args.id)
    if base_pointer is None:
        raise CellPortError(
            f"REFUSED: id {args.id} has no definition in the base image to take a header from")
    base_header = image[base_pointer - ROM_BASE:base_pointer - ROM_BASE + BF_DEFINITION_HEADER]
    if len(base_header) != BF_DEFINITION_HEADER:
        raise CellPortError("REFUSED: the base definition's header runs past the image")
    # The allocator field is a u16 at +0x02 (retail carries 0x1000 for one 64x64 8bpp frame), so its LOW
    # byte is legitimately zero; the field as a whole must not be.
    base_allocator = struct.unpack_from("<H", base_header, 0x02)[0]
    if base_allocator == 0:
        raise CellPortError(
            "REFUSED: the base definition carries 0 for the allocator size field at +0x02, which no retail "
            "definition does, so this is not the definition the port should mimic")

    out, report = build_port(slots, payloads, image, base_header, args.slots)
    report["header_from"] = f"0x{base_pointer:08X}"
    report["header_allocator_bytes"] = base_allocator
    out = bytearray(out)          # the table word is repointed below
    table_word = BF_DEFINITION_TABLE + 4 * args.id
    struct.pack_into("<I", out, table_word, report["definition"])
    report["id"] = args.id
    report["table_word"] = f"0x{table_word + ROM_BASE:08X}"
    report["base_sha256"] = image_digest.lower()
    report["output_sha256"] = hashlib.sha256(out).hexdigest()
    report["output_bytes"] = len(out)

    # ROM_SAFETY: an output may never BE an input. The canonical ROM, the source title and the base image
    # are protected, and the write is staged so a failure cannot leave a half-written image behind.
    protected = {log2_path.resolve(), image_path.resolve()}
    out_path = Path(args.out).resolve()
    manifest_path = Path(args.manifest).resolve()
    for target, label in ((out_path, "--out"), (manifest_path, "--manifest")):
        if target in protected:
            raise CellPortError(f"REFUSED: {label} names an input this build reads: {target}")
        if any(part in ("roms", "extracted", "dump", "dumps", "stock", "exports")
               for part in target.parts):
            raise CellPortError(f"REFUSED: {label} is inside a protected input directory: {target}")
    for target, payload in ((out_path, out),
                            (manifest_path, ("\n".join(f"{key}: {value}"
                                                        for key, value in report.items())
                                             + "\n").encode("utf-8"))):
        staging = target.with_name(target.name + ".staging")
        staging.write_bytes(payload)
        staging.replace(target)
    for key, value in report.items():
        print(f"  {key}: {value}")
    print(f"# wrote {args.out} ({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CellPortError as error:
        print(f"FAIL: {error}")
        raise SystemExit(1)
