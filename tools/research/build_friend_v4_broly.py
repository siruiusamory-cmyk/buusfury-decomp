"""Release 4A: the chapter-4 Dabura encounter, and every other Dabura draw site, become Broly.

Base: the shipped release-3.1 image (sha256 f5c9648b...). Read-only on everything else.

THE ROUTE, AND WHY IT IS THIS SMALL. A placed or scripted actor gets its art from ONE door: the
engine's resolver 0x08000158 maps a sprite id through the character table to a sprite definition, and
all three map-object families and the event-script operands reach it that way. So changing the sprite
id a draw site carries changes what that site draws, and the scripts follow with no edit of their own.
The census (tools/research/census_draw_sites.py, re-derived in this tool) finds exactly five sites
carrying Dabura's ids: sprite 73 at map 207 slot 4 (the Babidi's-ship fight), map 32 slot 42, map 206
slot 3 and map 207 slot 3, and sprite 98 at map 451 slot 0 (the Heaven form). The owner asked for
Broly everywhere, so all five take sprite 38.

THE FIGHT'S NUMBERS ARE BROLY'S OWN, UNCHANGED. Both FD55 fights carry stat selector 18 (Dabura's).
Broly's chapter-6 fight is map 390 slot 0, whose stat selector is 10 - measured, not assumed - so
both fights are pointed at selector 10 and record 10 is left BYTE-IDENTICAL. It is not retuned, and
the owner was told plainly that this is likely brutal at chapter 4.

THE NAME. Text slot 1024 holds "Dabura" and is the name both appearance records display, so "Broly"
is written in place over it. The replacement is shorter than the original, so the pointer does not
move and the rule of the text table applies: write the new wording plus its terminator and leave the
old tail past it. Slot 1025 is Dabura's DESCRIPTION and still names him: it is prose, not a draw
site, and the owner is reworking the wording, so it is reported and NOT touched.

WHAT IS NOT TOUCHED: the enemy stat records, the behaviour tables, the placement descriptors and
their handlers, the appearance description slots, and every dialogue record that names Dabura.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.research.friend_v3_text_approvals import APPROVED_RELEASES  # noqa: E402
from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402

#: The frozen identity this tool must reproduce, and refuse otherwise.
RELEASE = next(record for record in APPROVED_RELEASES if record.name == "release-4a")

ROM_BASE = 0x08000000
TEXT_TABLE_START = 0x6BCE8
STAT_RECORD_TABLE = 0x711274
STAT_RECORD_STRIDE = 0x1C
APPEARANCE_TABLE = 0x74D380
APPEARANCE_STRIDE = 0x10

OLD_NAME = "Dabura"
NEW_NAME = "Broly"
NAME_SLOT = 1024
BROLY_STAT_RECORD = 10          # map 390 slot 0 carries stat selector 10: Broly's chapter-6 fight

#: (label, file offset, expected word, new word). The expected word is what the canonical ROM holds,
#: so a base image that disagrees refuses instead of writing over something else.
SITES = (
    ("map207 slot4 sprite (ship fight, sprite 73 -> 38)", 0x7F09C, 73, 38),
    ("map207 slot4 stat selector (Dabura 18 -> Broly 10)", 0x7F094, 18, BROLY_STAT_RECORD),
    ("map32 slot42 sprite (other Dabura fight, 73 -> 38)", 0x74AE0, 73, 38),
    ("map32 slot42 stat selector (18 -> Broly 10)", 0x74AD8, 18, BROLY_STAT_RECORD),
    ("map206 slot3 sprite (ship scene, 73 -> 38)", 0x7F004, 73, 38),
    ("map207 slot3 sprite (ship scene, 73 -> 38)", 0x7F078, 73, 38),
    ("map451 slot0 sprite (Heaven form, 98 -> 38)", 0x8E204, 98, 38),
)

#: appearance record 28 is the Dabura the fights display (sprite 73, portrait 24, stat 18);
#: record 29 is the Heaven form (sprite 98, portrait 32, stat -1). Broly's portrait slot is 16 and
#: his own appearance records are 16 and 17, both sprite 38 and portrait 16.
APPEARANCES = (
    ("appearance 28 sprite 73 -> 38", APPEARANCE_TABLE + 28 * APPEARANCE_STRIDE + 0x04, 73, 38),
    ("appearance 28 portrait 24 -> 16", APPEARANCE_TABLE + 28 * APPEARANCE_STRIDE + 0x08, 24, 16),
    ("appearance 28 stat 18 -> Broly 10", APPEARANCE_TABLE + 28 * APPEARANCE_STRIDE + 0x0C, 18,
     BROLY_STAT_RECORD),
    ("appearance 29 sprite 98 -> 38", APPEARANCE_TABLE + 29 * APPEARANCE_STRIDE + 0x04, 98, 38),
    ("appearance 29 portrait 32 -> 16", APPEARANCE_TABLE + 29 * APPEARANCE_STRIDE + 0x08, 32, 16),
)


class BrolyError(Exception):
    """A refusal: the image is not what this build says it is, or a field moved."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def word(image: bytes, offset: int) -> int:
    return struct.unpack_from("<I", image, offset)[0]


def text_of_slot(image: bytes, slot: int) -> str:
    pointer = word(image, TEXT_TABLE_START + 4 * slot)
    if pointer < ROM_BASE:
        raise BrolyError(f"text slot {slot} holds 0x{pointer:08X}, not a ROM pointer")
    offset = pointer - ROM_BASE
    end = offset
    while end + 1 < len(image) and image[end:end + 2] != b"\x00\x00":
        end += 2
    return image[offset:end].decode("utf-16le")


def census(image: bytes) -> list[dict]:
    """Every map object slot whose sprite id is one of Dabura's, re-derived from the image."""
    map_table, stride, count = 0x8E2E0, 0x38, 452
    families = {0x0800FD55: 0x10, 0x080111A9: 0x0C, 0x08017DA3: 0x10}
    hits = []
    for map_index in range(count):
        entry = map_table + stride * map_index
        runs = image[entry + 0x04]
        array = word(image, entry + 0x14)
        if array < ROM_BASE or array - ROM_BASE + 4 > len(image):
            continue
        array -= ROM_BASE
        for slot in range(runs):
            pointer = word(image, array + 4 * slot)
            if pointer < ROM_BASE or pointer - ROM_BASE + 0x1C > len(image):
                continue
            base = pointer - ROM_BASE
            family = word(image, base)
            if family not in families:
                continue
            sprite = word(image, base + families[family])
            if sprite in (73, 98, 38):
                hits.append({"map": map_index, "slot": slot, "family": family, "file": base,
                             "sprite": sprite,
                             "stat": word(image, base + 0x08) if family == 0x0800FD55 else None})
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="release-3.1 image")
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise BrolyError(f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")

    document: dict = {"input": str(source), "input_sha256": got, "input_bytes": len(image),
                      "old_name": OLD_NAME, "new_name": NEW_NAME, "sites": [], "appearances": [],
                      "name_slot": NAME_SLOT}

    # The census must find exactly the five Dabura sites this tool knows about. A sixth would mean the
    # inventory is incomplete and the "Broly everywhere" claim is false.
    before = census(image)
    dabura_sites = [entry for entry in before if entry["sprite"] in (73, 98)]
    if len(dabura_sites) != 5:
        raise BrolyError(
            f"REFUSED: the census finds {len(dabura_sites)} slots carrying sprite 73 or 98, not the "
            "five this build accounts for")
    document["census_before"] = dabura_sites

    out = bytearray(image)
    for label, offset, expected, new in SITES + APPEARANCES:
        current = word(image, offset)
        if current != expected:
            raise BrolyError(
                f"REFUSED: {label}: file 0x{offset:X} holds 0x{current:X}, expected 0x{expected:X}")
        out[offset:offset + 4] = new.to_bytes(4, "little")
        (document["sites"] if (label, offset, expected, new) in SITES
         else document["appearances"]).append({"label": label, "file": offset, "was": expected,
                                               "now": new})

    # The name. "Broly" is shorter than "Dabura", so the wording and its terminator go in place and
    # the old tail stays past it (the text table's own rule); the pointer does not move.
    current_name = text_of_slot(image, NAME_SLOT)
    if current_name != OLD_NAME:
        raise BrolyError(f"REFUSED: text slot {NAME_SLOT} holds {current_name!r}, not {OLD_NAME!r}")
    if len(NEW_NAME) > len(OLD_NAME):
        raise BrolyError("REFUSED: the new wording does not fit the slot in place")
    name_pointer = word(image, TEXT_TABLE_START + 4 * NAME_SLOT) - ROM_BASE
    encoded = NEW_NAME.encode("utf-16le") + b"\x00\x00"
    out[name_pointer:name_pointer + len(encoded)] = encoded
    document["name_slot_edit"] = {"file": name_pointer, "was": current_name, "now": NEW_NAME,
                                  "bytes": len(encoded),
                                  "tail_left": len(OLD_NAME) * 2 + 2 - len(encoded)}

    # Readback, on the in-memory image, before anything is written.
    problems = 0
    for label, offset, expected, new in SITES + APPEARANCES:
        if word(out, offset) != new:
            problems += 1
            print(f"FAIL {label}: reads 0x{word(out, offset):X}")
    if text_of_slot(out, NAME_SLOT) != NEW_NAME:
        problems += 1
        print(f"FAIL text slot {NAME_SLOT}: reads {text_of_slot(out, NAME_SLOT)!r}")
    after = census(out)
    still_dabura = [entry for entry in after if entry["sprite"] in (73, 98)]
    if still_dabura:
        problems += 1
        print(f"FAIL {len(still_dabura)} slot(s) still carry sprite 73 or 98: {still_dabura}")
    broly_now = [entry for entry in after if entry["sprite"] == 38]
    if len(broly_now) != 6:
        problems += 1
        print(f"FAIL after the swap {len(broly_now)} slot(s) carry sprite 38, expected 6")
    for entry in after:
        if entry["family"] == 0x0800FD55 and entry["stat"] != BROLY_STAT_RECORD:
            problems += 1
            print(f"FAIL map {entry['map']} slot {entry['slot']} stat selector is {entry['stat']}")
    # Broly's own record must be untouched, byte for byte, along with every other enemy record.
    start = STAT_RECORD_TABLE
    end = STAT_RECORD_TABLE + STAT_RECORD_STRIDE * 151
    if bytes(out[start:end]) != image[start:end]:
        problems += 1
        print("FAIL an enemy stat record changed")
    if problems:
        raise BrolyError(f"REFUSED: {problems} readback problem(s)")

    written = bytes(out)
    changed = [offset for offset in range(len(image))
               if written[offset] != image[offset]]
    document["changed_bytes"] = len(changed)
    document["changed_ranges"] = _ranges(changed)
    document["census_after"] = after
    document["output_sha256"] = sha256_bytes(written)
    document["output_bytes"] = len(written)

    target = Path(args.out)
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise BrolyError(f"REFUSED: {error}") from error
    # The output must equal the frozen release identity, and the check runs BEFORE anything is
    # written, so a build that disagrees leaves no image on disk to be played or shipped.
    if document["output_sha256"] != RELEASE.output_sha256:
        raise BrolyError(
            f"REFUSED: the chain produced {document['output_sha256']} and release 4A is "
            f"{RELEASE.output_sha256}. A byte moved somewhere.")
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(written)
    if staged.read_bytes() != written:
        raise BrolyError("REFUSED: the staged write does not match the verified bytes")
    staged.replace(target)
    Path(args.manifest).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"# {len(SITES)} draw site(s) and {len(APPEARANCES)} appearance field(s) rewritten")
    print(f"# text slot {NAME_SLOT}: {OLD_NAME!r} -> {NEW_NAME!r} in place")
    print(f"# slots carrying sprite 38 after the swap: {len(broly_now)} "
          f"(was 1: map 390 slot 0)")
    print(f"# changed bytes: {len(changed)} in {len(document['changed_ranges'])} range(s)")
    print(f"# wrote {target} {len(written)} bytes sha256 {document['output_sha256']}")
    return 0


def _ranges(offsets: list[int]) -> list[list[int]]:
    if not offsets:
        return []
    ranges = []
    start = previous = offsets[0]
    for offset in offsets[1:]:
        if offset != previous + 1:
            ranges.append([start, previous])
            start = offset
        previous = offset
    ranges.append([start, previous])
    return ranges


if __name__ == "__main__":
    sys.exit(main())
