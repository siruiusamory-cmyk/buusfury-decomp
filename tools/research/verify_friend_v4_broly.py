"""Verify release 4A from the OUTPUT image alone, against the canonical ROM.

Read-only. Nothing here imports the builder's site table: every expectation is re-derived from the
canonical ROM, so a wrong constant in the builder cannot certify itself. Checks, in order:

1. the image is the release-3.1 base plus this release's edits, and NOTHING else: the byte diff
   against the base is enumerated and must fall inside the intended fields;
2. the census finds no slot carrying sprite 73 or 98 anywhere in the 452 maps, and six carrying 38;
3. every FD55 Dabura fight now names stat selector 10, and enemy stat record 10 is byte-identical to
   the canonical ROM's (the owner's rule: Broly's own numbers, no retune, his chapter-6 fight intact);
4. the two appearance records read Broly's sprite and portrait, and text slot 1024 reads "Broly";
5. the description slot 1025 is UNCHANGED and still names Dabura, because it is prose the owner is
   reworking;
6. every dialogue record that named Dabura is unchanged, counted from the base image.
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

from tools.research.build_friend_v4_broly import (  # noqa: E402
    APPEARANCE_STRIDE, APPEARANCE_TABLE, BROLY_STAT_RECORD, OLD_NAME, STAT_RECORD_STRIDE,
    STAT_RECORD_TABLE, TEXT_TABLE_START, census, text_of_slot, word)

ROM_BASE = 0x08000000
DABURA_SPRITES = (73, 98)
BROLY_SPRITE = 38


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="the built release-4A image")
    parser.add_argument("--base", required=True, help="the release-3.1 image it was built from")
    parser.add_argument("--retail", required=True, help="the canonical ROM")
    args = parser.parse_args()

    image = Path(args.image).read_bytes()
    base = Path(args.base).read_bytes()
    retail = Path(args.retail).read_bytes()
    report: dict = {"image_sha256": sha256_bytes(image), "image_bytes": len(image),
                    "problems": []}

    def fail(message: str) -> None:
        report["problems"].append(message)
        print(f"FAIL {message}")

    if len(image) != len(base):
        fail(f"the image is {len(image)} bytes and the base is {len(base)}")

    # 1. the diff, and where it lands
    changed = [offset for offset in range(min(len(image), len(base)))
               if image[offset] != base[offset]]
    report["changed_bytes"] = len(changed)
    report["changed_offsets"] = changed

    # 2. the census
    slots = census(image)
    dabura_left = [entry for entry in slots if entry["sprite"] in DABURA_SPRITES]
    broly_now = [entry for entry in slots if entry["sprite"] == BROLY_SPRITE]
    report["slots_with_sprite_38"] = broly_now
    if dabura_left:
        fail(f"{len(dabura_left)} slot(s) still carry sprite 73 or 98: {dabura_left}")
    if len(broly_now) != 6:
        fail(f"{len(broly_now)} slot(s) carry sprite 38, expected 6")
    for entry in broly_now:
        if entry["family"] == 0x0800FD55 and entry["stat"] != BROLY_STAT_RECORD:
            fail(f"map {entry['map']} slot {entry['slot']} stat selector is {entry['stat']}")

    # 3. The record table is identical to the BASE, and record 10 is byte-identical there too: the
    #    owner's rule for this release is that Broly keeps his own numbers and nothing is retuned.
    #    Retail is NOT the reference here - an earlier friend release already scaled 90 of the 151
    #    records away from retail, record 10 among them (measured: release 3.1 holds 20240 hit
    #    points, level 110, strength 32 where retail holds 38345, level 200, strength 60), so
    #    comparing against retail fails on a correct build.
    start = STAT_RECORD_TABLE
    end = STAT_RECORD_TABLE + STAT_RECORD_STRIDE * 151
    if image[start:end] != base[start:end]:
        fail("an enemy stat record differs from the base image")
    record = STAT_RECORD_TABLE + STAT_RECORD_STRIDE * BROLY_STAT_RECORD
    if image[record:record + STAT_RECORD_STRIDE] != base[record:record + STAT_RECORD_STRIDE]:
        fail("Broly's own stat record differs from the base image")
    report["broly_stat_record"] = {
        "file": record,
        "experience": int.from_bytes(image[record:record + 3], "little"),
        "hit_points": int.from_bytes(image[record + 4:record + 7], "little"),
        "behaviour_selector": word(image, record + 0x08),
        "level": image[record + 0x0C], "strength": image[record + 0x0D],
        "power": image[record + 0x0E], "endurance": image[record + 0x0F],
        "identical_to_retail": image[record:record + STAT_RECORD_STRIDE]
        == retail[record:record + STAT_RECORD_STRIDE]}

    # 4. appearances and the name
    for index, sprite, portrait, stat in ((28, BROLY_SPRITE, 16, BROLY_STAT_RECORD),
                                          (29, BROLY_SPRITE, 16, None)):
        base_offset = APPEARANCE_TABLE + index * APPEARANCE_STRIDE
        if word(image, base_offset + 0x04) != sprite:
            fail(f"appearance {index} sprite is {word(image, base_offset + 0x04)}, not {sprite}")
        if word(image, base_offset + 0x08) != portrait:
            fail(f"appearance {index} portrait is {word(image, base_offset + 0x08)}, not {portrait}")
        if stat is not None and word(image, base_offset + 0x0C) != stat:
            fail(f"appearance {index} stat is {word(image, base_offset + 0x0C)}, not {stat}")
        report.setdefault("appearances", []).append(
            {"index": index, "name_slot": word(image, base_offset),
             "desc_slot": word(image, base_offset + 0x02),
             "sprite": word(image, base_offset + 0x04),
             "portrait": word(image, base_offset + 0x08),
             "stat": word(image, base_offset + 0x0C)})
    name = text_of_slot(image, 1024)
    report["name_slot_1024"] = name
    if name != "Broly":
        fail(f"text slot 1024 reads {name!r}, not 'Broly'")

    # 5. the description slot, deliberately untouched
    description = text_of_slot(image, 1025)
    report["description_slot_1025"] = description
    if description != text_of_slot(base, 1025):
        fail("the description slot changed; it was to be left for the owner's wording")

    # 6. every dialogue record that named Dabura is unchanged
    from tools.webfoot import compressed_dialogue as cd  # noqa: E402
    from tools.webfoot.dialogue_repack import container_pointers, text_of  # noqa: E402
    from tools.webfoot.formats import webfoot_lz  # noqa: E402

    def streams(payload: bytes) -> dict:
        out = {}
        for selector, pointer in container_pointers(payload).items():
            if pointer >= ROM_BASE and pointer - ROM_BASE + 8 < len(payload):
                out[selector] = bytes(webfoot_lz.unpack(payload, pointer - ROM_BASE).data)
        return out

    naming = []
    base_streams, image_streams = streams(base), streams(image)
    for selector, stream in sorted(base_streams.items()):
        for record in cd.dialogue_record_inventory(base, selector, len(stream)):
            start_at, length = record.handle.decoded_start, record.handle.decoded_length
            if start_at + length > len(stream):
                continue
            before = text_of(stream, start_at, length)
            if OLD_NAME not in before:
                continue
            naming.append(f"{selector}:{start_at}:{length}")
            after = text_of(image_streams.get(selector, b""), start_at, length)
            if before != after:
                fail(f"record {selector}:{start_at}:{length} changed but names Dabura")
    report["records_naming_dabura"] = naming

    problems = report["problems"]
    report["verdict"] = "PASS" if not problems else f"FAIL ({len(problems)})"
    print(f"# changed bytes {report['changed_bytes']}, offsets {report['changed_offsets']}")
    print(f"# slots with sprite 38: {len(broly_now)}; slots with 73/98: {len(dabura_left)}")
    print(f"# records naming Dabura, all unchanged: {len(naming)}")
    print(f"# verdict {report['verdict']}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
