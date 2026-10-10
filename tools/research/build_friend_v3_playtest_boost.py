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
# The equipment inventory is the count-and-entry array: a u32 count at save-block base +0xE4
# and one 4-byte word per entry from +0xE8, the low 28 bits the gear id and the top nibble the
# wearer's index plus one. The add routine at 0x08004448 takes the base in r0 and the id in r1,
# refuses only at 250 entries, and never refuses a duplicate.
BANDANA_ID = 126
GBA_BASE = 0x08000000
HOOK = 0x08004892                      # `adds r0,r4,#0`, which the four-byte BL displaces
HOOK_FILE = HOOK - GBA_BASE
INIT_COUNT_CLEAR = HOOK                # kept for the tests that name the hook site
INIT_ADDRESS = 0x08004448              # add(base, id)
TRAMPOLINE = 0x083C22FC                # inside a 4,348-byte zero run
TRAMPOLINE_FILE = TRAMPOLINE - GBA_BASE
# The second displaced halfword is the first half of `b #0x800484e` at 0x08004894, so the
# original flow continued at that branch's destination, not at the byte after the hook.
TRAMPOLINE_RETURN = 0x0800484E
TRAMPOLINE_LENGTH = [0]


class BoostError(ValueError):
    """A refusal. Nothing is written when this is raised."""


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def encode_bl(here: int, target: int) -> bytes:
    """Thumb BL from the instruction at `here`. `here` is its OWN address."""
    delta = target - (here + 4)
    if delta % 2:
        raise BoostError(f"odd branch from {here:#x} to {target:#x}")
    imm = delta >> 1
    if not -(1 << 22) <= imm < (1 << 22):
        raise BoostError(f"branch {here:#x} -> {target:#x} is out of range")
    imm &= 0x3FFFFF
    return (0xF000 | ((imm >> 11) & 0x7FF)).to_bytes(2, "little") + \
           (0xF800 | (imm & 0x7FF)).to_bytes(2, "little")


def bl_halfwords(here: int, target: int) -> tuple[int, int]:
    blob = encode_bl(here, target)
    return int.from_bytes(blob[0:2], "little"), int.from_bytes(blob[2:4], "little")


def _ldr_literal(rt: int, here: int, literal: int) -> int:
    """The halfword for `ldr rt,[pc,#imm*4]` that reads exactly `literal`.

    Thumb computes the base as ((here + 4) & ~3) and only low registers can be loaded
    pc-relatively, so a literal is reachable only at four-byte steps from that base. This
    refuses rather than emitting a load of the wrong word.
    """
    if rt > 7:
        raise BoostError(f"pc-relative load cannot target r{rt}")
    base = (here + 4) & ~3
    delta = literal - base
    if delta < 0 or delta % 4 or delta // 4 > 0xFF:
        raise BoostError(f"literal {literal:#x} unreachable from {here:#x}")
    return 0x4800 | (rt << 8) | (delta // 4)


def _build_trampoline() -> bytes:
    """Assemble the trampoline so the frame delivers the epilogue address to pc.

    THREE rules govern this, each learned from a measured failure:

    1. A pop reads its list from the LOWEST address upward, lowest register at lowest address.
       Two single-register pushes therefore build the reverse of one merged push. Here the
       pushes are deliberately ordered so the LAST word pushed is the one pc reads:
           +4 push {r4}   S-4 = caller r4     -> popped into r4
           +6 push {r5}   S-8 = 0x0800484E    -> popped into pc
    2. r0 is LIVE at the continuation. The displaced `adds r0,r4,#0` exists to leave the base in
       r0 for this function's caller, so it is replayed AFTER the nested call.
    3. The continuation is 0x0800484E, the destination of the `b` the hook displaces. It is not
       the byte after the hook: 0x08004896 is `push {r3, lr}`, the head of another routine, so
       returning through lr loops inside that routine instead of reaching the epilogue.

    Layout:

        +0   ldr  r1, [pc,..]   the gear id                     reads +20
        +2   ldr  r5, [pc,..]   the epilogue address           reads +24
        +4   push {r4}          S-4: the FIRST register the pop reads
        +6   push {r5}          S-8: the SECOND register the pop reads
        +8   adds r0, r4, #0    r0 = the base, for the call
        +10  bl   0x08004448
        +14  adds r0, r4, #0    replays the displaced instruction after the call
        +16  pop  {r4, pc}      pc <- 0x0800484E, r4 <- caller r4, SP exact
        +20  .word 126
        +24  .word 0x0800484E
    """
    base = TRAMPOLINE
    id_slot = 20
    ret_slot = 24

    high, low = bl_halfwords(base + 10, INIT_ADDRESS)
    instructions = [
        (0, _ldr_literal(1, base + 0, base + id_slot)),
        (2, _ldr_literal(5, base + 2, base + ret_slot)),
        (4, 0xB420),      # push {r5}  S-4 = the epilogue  -> popped into r4? see the note
        (6, 0xB410),      # push {r4}  S-8 = caller r4
        (8, 0x1C20),      # adds r0, r4, #0
        (10, high), (12, low),
        (14, 0x1C20),     # adds r0, r4, #0 again, after the call
        (16, 0xBD10),     # pop {r4, pc}
    ]
    code = bytearray()
    for offset, half in instructions:
        if len(code) != offset:
            raise BoostError(f"trampoline layout drifted: {len(code)} != {offset}")
        code += half.to_bytes(2, "little")
    if len(code) > id_slot:
        raise BoostError(f"trampoline code overruns its literals: {len(code)} > {id_slot}")
    blob = bytearray(code)
    blob += b"\x00" * (id_slot - len(blob))
    blob[id_slot:id_slot + 4] = BANDANA_ID.to_bytes(4, "little")
    blob += b"\x00" * (ret_slot - len(blob))
    blob[ret_slot:ret_slot + 4] = TRAMPOLINE_RETURN.to_bytes(4, "little")
    TRAMPOLINE_LENGTH[0] = len(blob)
    return bytes(blob)


def bandana_patch(base: bytes) -> bytes:
    """UNUSED RESEARCH: the Bandana startup injection was CANCELLED BY OWNER 2026-10-09.

    Nothing calls this. The hook it applies was measured to make the main menu selection arrow
    visibly wrong, so it must never reach a playtest image. The delivered ROM is produced by
    `plan` without it.

    The hook is four bytes of BL on two-byte instructions, so it displaces TWO halfwords:
    `adds r0,r4,#0` at 0x08004892 and the first half of `b #0x800484e` at 0x08004894. Both
    are accounted for: the adds is replayed at +8, and the continuation is that branch's own
    destination, the epilogue at 0x0800484e.
    """
    patch = bytearray(base)
    patch[HOOK_FILE:HOOK_FILE + 4] = encode_bl(HOOK, TRAMPOLINE)
    code = _build_trampoline()
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

    # The Bandana startup injection was CANCELLED BY OWNER on 2026-10-09. `bandana_patch`
    # below is retained as documented research and has no caller: this build produces the
    # stat-only playtest image, and the hook cannot be enabled by accident from here.
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
