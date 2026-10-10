"""Build the FRIEND-V3 playtest-boost image from a verified friend foundation.

One image in, one image out. `main` refuses unless the input digest equals the
caller's expected digest, so the builder can never patch an image it was not
verified against. It then refuses unless every changed byte is contained in the
span its own patch table declared: a write that escapes that table is caught,
while a wrong offset or width inside it is not, because the table is also what
drives the writes.

Read-only with respect to its input. The canonical ROM is never an input here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Character base-stat table, Buu's Fury. Layout verified in
# tools/webfoot/formats/stat_tables.py:decode_base_stat_record.
BASE_STAT_TABLE = 0x006FDA4C
BASE_STAT_RECORD_SIZE = 0x12
BASE_STAT_COUNT = 9

# Records 0..4 in BASE_STAT_NAMES order. Which record is which character is an
# INFERENCE: tools/webfoot/formats/stat_tables.py:80 calls the names inferred and
# :77 calls all nine records playable. Records 5..8 (Gotenks, Vegito, Gogeta,
# Hercule) are therefore left at retail values, the conservative side of that
# uncertainty. See section 2 of docs/research/FRIEND_V3_PLAYTEST_BOOST.md.
PARTY_RECORDS = (0, 1, 2, 3, 4)
ROSTER_NAMES = ("Goku", "Gohan", "Goten", "Trunks", "Vegeta")

# Field name -> (offset in the record, width in bytes). Widths and offsets match
# tools/webfoot/formats/stat_tables.py:decode_base_stat_record.
#
# hp and ep are deliberately absent. Both are u16 and the engine reads them as
# signed: writing 0xFFFF made a live character read HP -1 and EP -5 and disabled
# energy attacks, observed on the status screen of a cold boot of the previous
# candidate. The owner's ruling on that observation: the hp and ep fields do not
# need changing. strength, power, endurance and speed are u8, where 0xFF is fine,
# and level is u8 with its own ceiling below.
FIELD_OFFSETS = {
    "level": (0x00, 1),
    "strength": (0x06, 1),
    "power": (0x07, 1),
    "endurance": (0x08, 1),
    "speed": (0x09, 1),
}

# Every value is the widest its own mode uses. Level stops at 200 rather than the
# u8 bound of 255 because 200 is the game's own XP ceiling: `cmp r6,#0xc8` before
# the threshold lookup at 0x08013A00 (tools/webfoot/stats.py:71-75,
# docs/research/P010_ENEMY_DEATH_AND_REWARDS.md:393).
LEVEL_CEILING = 200
MAXIMUM = {
    "level": LEVEL_CEILING,
    "strength": 0xFF,
    "power": 0xFF,
    "endurance": 0xFF,
    "speed": 0xFF,
}

# The starting Bandana.
#
# The equipment inventory is the count-and-entry array: a u32 count at save-block
# base +0xE4 and one 4-byte word per entry from +0xE8, the low 28 bits the gear id
# and the top nibble the wearer's index plus one. The add routine at 0x08004448
# takes the base in r0 and the gear id in r1, refuses only at 250 entries, and
# never refuses a duplicate.
#
# The hook replaces `adds r0,r4,#0` at the tail of the save-block init, after the
# whole function has run, NOT the count clear in the middle of it: the first attempt
# hooked the clear and the game hung inside the trampoline with the counter at 1.
# At this site r4 still holds the base, the next instruction is untouched, and
# control rejoins the function's own epilogue.
BANDANA_ID = 126
GBA_BASE = 0x08000000
INIT_COUNT_CLEAR = 0x08004892          # adds r0,r4,#0, the last work before the epilogue
INIT_ADDRESS = 0x08004448              # add(base, id)
TRAMPOLINE = 0x083C22FC                # inside a 4,348-byte zero run at 0x083C22FC
TRAMPOLINE_FILE = TRAMPOLINE - GBA_BASE
TRAMPOLINE_RETURN = 0x08004894         # the branch that rejoins the function's epilogue
TRAMPOLINE_LENGTH = [0]                # filled by bandana_patch with what it wrote


class BoostError(ValueError):
    """A refusal. Nothing is written when this is raised."""


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def encode_bl(here: int, target: int) -> bytes:
    """Thumb BL. `here` is the instruction's own address."""
    delta = target - (here + 4)
    if delta % 2:
        raise BoostError(f"odd branch from {here:#x} to {target:#x}")
    imm = delta >> 1
    if not -(1 << 22) <= imm < (1 << 22):
        raise BoostError(f"branch {here:#x} -> {target:#x} is out of Thumb BL range")
    imm &= 0x3FFFFF
    return (0xF000 | ((imm >> 11) & 0x7FF)).to_bytes(2, "little") + \
           (0xF800 | (imm & 0x7FF)).to_bytes(2, "little")


def bandana_patch(base: bytes) -> bytes:
    """The trampoline and the hook, byte for byte, with every byte derived here.

    The hook replaces the init's last work instruction, so the function has already
    zeroed the count and rebuilt the per-character blocks. r4 still holds the
    save-block base, the instruction after the hook is untouched, and lr still points
    into the init, so `bx lr` returns to the instruction after the hook and control
    rejoins the function's own epilogue. Only r0-r3 and lr are clobbered, and r0-r3
    are saved.
    """
    t = TRAMPOLINE
    code = bytearray()
    code += (0xB50F).to_bytes(2, "little")            # push {r0-r3,lr}
    code += (0x1C20).to_bytes(2, "little")            # mov r0, r4      ; the save-block base
    code += (0x4903).to_bytes(2, "little")            # ldr r1,[pc,#12] ; literal at +14
    code += encode_bl(t + 6, INIT_ADDRESS)            # bl 0x08004448
    code += (0xBC0F).to_bytes(2, "little")            # pop {r0-r3}
    code += (0x4770).to_bytes(2, "little")            # bx lr           ; back into the init
    code += BANDANA_ID.to_bytes(4, "little")          # the literal ldr r1 reads
    TRAMPOLINE_LENGTH[0] = len(code)

    patch = bytearray(base)
    patch[INIT_COUNT_CLEAR - GBA_BASE:INIT_COUNT_CLEAR - GBA_BASE + 4] = encode_bl(INIT_COUNT_CLEAR, TRAMPOLINE)
    patch[TRAMPOLINE_FILE:TRAMPOLINE_FILE + len(code)] = code
    return bytes(patch)


def plan(base: bytes) -> tuple[bytes, list[dict]]:
    """Return the boosted image bytes and the manifest of changes."""
    need = BASE_STAT_TABLE + BASE_STAT_COUNT * BASE_STAT_RECORD_SIZE
    if len(base) < need:
        raise BoostError("image is smaller than the character base-stat table")

    out = bytearray(base)
    changes: list[dict] = []
    for name, index in zip(ROSTER_NAMES, PARTY_RECORDS):
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        fields = []
        for field, (rel, width) in FIELD_OFFSETS.items():
            offset = record + rel
            was = int.from_bytes(base[offset:offset + width], "little")
            now = MAXIMUM[field]
            if now != was:
                out[offset:offset + width] = now.to_bytes(width, "little")
            fields.append({"field": field, "offset": offset, "was": was, "now": now})
        changes.append({"record": index, "name": name, "fields": fields})

    # The Bandana hook is NOT applied: every variant that called the add routine from the
    # save-block init hung in game, while a structure-only hook of the same shape booted
    # normally. See docs/research/FRIEND_V3_PLAYTEST_BOOST_INVENTORY.md, section 6.
    boosted = bytes(out)
    _assert_only_declared_bytes_changed(base, boosted, changes)
    return boosted, changes


def _assert_only_declared_bytes_changed(base: bytes, boosted: bytes, changes: list[dict]) -> None:
    """Refuse a byte neither the field table nor the hook declared.

    This catches a write outside the two declared regions. It cannot catch a wrong
    offset or width inside them, because both regions are also what drives the writes.
    """
    declared: set[int] = set()
    for entry in changes:
        for field in entry["fields"]:
            if field["was"] != field["now"]:
                _, width = FIELD_OFFSETS[field["field"]]
                declared.update(range(field["offset"], field["offset"] + width))
    undeclared = {i for i, (a, b) in enumerate(zip(base, boosted)) if a != b} - declared
    if undeclared:
        raise BoostError(f"{len(undeclared)} byte(s) changed outside the declared spans")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args(argv)

    base = args.image.read_bytes()
    got = sha256_bytes(base)
    if got != args.expect_sha256.lower():
        raise BoostError(f"input digest {got} is not the expected {args.expect_sha256.lower()}")
    if args.out.exists() and args.out.samefile(args.image):
        raise BoostError("output is the input; a boost is never written over its own base")

    boosted, changes = plan(base)
    args.out.write_bytes(boosted)
    report = {
        "input": {"path": str(args.image), "sha256": got, "bytes": len(base)},
        "output": {"path": str(args.out), "sha256": sha256_bytes(boosted), "bytes": len(boosted)},
        "changed_bytes": sum(1 for a, b in zip(base, boosted) if a != b),
        "records": changes,
    }
    if args.manifest:
        args.manifest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['output']['sha256']}  {len(boosted)}  {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
