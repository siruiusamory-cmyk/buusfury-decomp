"""Verify the combined registration-rows release against the release-2.1 image.

Read-only. Checks, in order:

  1. the two new dialogue rows resolve through the table the literal names, indexed by their
     handle's selector, and read the owner's approved wording with their own control prefix;
  2. the biography slot reads its approved wording from its new home;
  3. the fifteen World Tournament rows from release 2 still resolve, with their own start
     offsets, inside the container that now carries the new records (the declared size covers
     them, which is the check that caught the first version of this tool);
  4. every differing byte is a declared site or an appended byte, and no byte of the base was
     moved.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.research.friend_v3_text_approvals import (  # noqa: E402
    APPROVED_DIALOGUE_ROWS, APPROVED_REPLACEMENTS)
from tools.webfoot import compressed_dialogue as cd            # noqa: E402
from tools.webfoot.dialogue_repack import container_pointers    # noqa: E402
from tools.webfoot.formats import webfoot_lz                    # noqa: E402
from tools.webfoot.handles import unpack_handle                 # noqa: E402

ROM_BASE = 0x08000000
TABLE_LITERAL = 0x123CC
TEXT_TABLE_START = 0x6BCE8
TERMINATOR = b"\x00\x00"

#: The fifteen World Tournament rows release 2 placed, with the wording they must still read.
WT_ROWS = (
    ("3:7406:136", "#Hey sis, if you win the tournament, what do you think you'll get with "
                   "the prize Zeni?"),
    ("3:7542:42", "#Uh, tons of okonomiyaki, I guess!"),
    ("3:7584:80", "#Sheesh, Videl! How are you not fat?"),
    ("3:7664:60", "#EXCUSE ME?! What are you going to get then?"),
    ("3:7724:72", "#Candy. Lots and lots of candy."),
    ("3:7796:204", "#And you call me fat. Hey, isn't that kind of meta?"),
    ("3:8000:214", "#Hey, half pint! We don't take too kindly to your folk around here."),
    ("3:8214:118", "#Huh? Do you mean brown people?"),
    ("3:8332:218", "#What?! No! My mom may be racist, but I'm not! Geez, I meant adopted "
                   "kids!"),
    ("3:9112:62", "You really made me look bad earlier."),
    ("3:9174:114", "#Bruh. You were still totally a dick."),
    ("3:9288:282", "#That's my baby Idasa down there! Oooooo! Idasa! I wish they would match "
                   "Idasa up with a whiter kid! This is a disgrace!"),
    ("3:9662:116", "#Get him, Uub! You make that boy sorry his mom is racist!"),
    ("3:9778:114", "Noooo! My baby! That was unfair! That thing cheated!"),
    ("3:9892:486", "Unbelievable! Uub    wins and this means he's going to the final! This "
                   "is truly amazing ladies and gentlemen! It's the moment you've all been "
                   "waiting for! The Junior Division Championship between adopted siblings, "
                   "ten-year-old Uub and sixteen-year-old Videl!"),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--against", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    image = Path(args.image).read_bytes()
    against = Path(args.against).read_bytes()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    problems: list[str] = []

    def check(condition: bool, message: str) -> None:
        print(("PASS " if condition else "FAIL ") + message)
        if not condition:
            problems.append(message)

    table = int.from_bytes(image[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE

    def resolved_in(source: bytes, selector: int) -> tuple[int, bytes]:
        literal = int.from_bytes(source[TABLE_LITERAL:TABLE_LITERAL + 4],
                                 "little") - ROM_BASE
        pointer = int.from_bytes(source[literal + selector * 4:literal + selector * 4 + 4],
                                 "little")
        if not ROM_BASE <= pointer < ROM_BASE + len(source):
            raise SystemExit(f"selector {selector} does not resolve inside the image")
        container = webfoot_lz.unpack(source, pointer - ROM_BASE)
        return pointer - ROM_BASE, bytes(container.data)

    def resolved(selector: int) -> tuple[int, bytes]:
        return resolved_in(image, selector)

    # 1: the two new dialogue rows. The handle site is recomputed from the BASELINE image's
    # own inventory, not read out of the manifest the builder wrote: after the write those
    # records' handles name selector 7, so the finished image's inventory no longer lists them
    # under their original coordinates, while the baseline's does.
    container_two_baseline = resolved_in(against, 2)[1]
    for row in APPROVED_DIALOGUE_ROWS:
        sites = sorted(
            site for record in cd.dialogue_record_inventory(against, row.selector,
                                                            len(container_two_baseline))
            if record.handle.decoded_start == row.start
            and record.handle.decoded_length == row.length
            for site in record.sites)
        check(bool(sites),
              f"{row.key} has a handle site the baseline's own inventory reports")
        if not sites:
            continue
        handle = int.from_bytes(image[sites[0]:sites[0] + 4], "little")
        selector, start, length = unpack_handle(handle)
        _container, payload = resolved(selector)
        got = payload[start:start + length].decode("utf-16le")
        prefix = got[:1] if got[:1] in "#!" else ""
        check(got == prefix + row.new, f"{row.key} reads the owner's wording exactly")
        if got != prefix + row.new:
            print(f"     expected {prefix + row.new!r}")
            print(f"     got      {got!r}")

    # 2: the biography slot.
    slot = 1083
    slot_at = TEXT_TABLE_START + slot * 4
    pointer = int.from_bytes(image[slot_at:slot_at + 4], "little")
    offset = pointer - ROM_BASE
    end = offset
    while image[end:end + 2] != TERMINATOR:
        end += 2
    check(image[offset:end].decode("utf-16le") == APPROVED_REPLACEMENTS[slot],
          f"text slot {slot} reads its approved wording from its new home")

    # 3: the fifteen World Tournament rows still resolve inside their container's declared
    # size, AT THE SITES THAT CARRY THEM. Their handles were rewritten by release 2 to selector
    # 7 with the container-7 start offsets, so this reads each handle from the image at a site
    # the baseline itself reports, then checks the text at the start that handle names. A
    # substring test over the payload would pass even if the records had been reordered, which
    # is the failure this step exists to catch.
    container_offset, payload = resolved(7)
    declared = int.from_bytes(image[container_offset + 4:container_offset + 8], "little")
    check(len(payload) == declared,
          f"the selector-7 container declares {declared} bytes and decodes to {len(payload)}")
    baseline_sites = sorted(
        site for record in cd.dialogue_record_inventory(against, 7, declared)
        for site in record.sites)
    check(bool(baseline_sites),
          f"the baseline reports {len(baseline_sites)} handle site(s) in container 7")
    for key, expected in WT_ROWS:
        _selector, _start, _length = (int(part) for part in key.split(":"))
        hit = None
        for site in baseline_sites:
            selector, start, length = unpack_handle(
                int.from_bytes(image[site:site + 4], "little"))
            if (selector == 7 and length and start + length <= len(payload)
                    and payload[start:start + length].decode("utf-16le") == expected):
                hit = (site, start, length)
                break
        check(hit is not None,
              f"{key} still reads its release-2 wording at a handle site in container 7")
        if hit is not None:
            print(f"     {key} -> site 0x{hit[0]:06X}, start {hit[1]}, length {hit[2]}")

    # 4: the differing bytes are the declared sites plus the append, and the base is intact.
    allowed = set(range(len(against), len(image)))
    for change in manifest["site_changes"]:
        allowed.update(range(change["site"], change["site"] + 4))
    allowed.update(range(manifest["table_slot_file_offset"],
                         manifest["table_slot_file_offset"] + 4))
    stray = [index for index in range(min(len(image), len(against)))
             if image[index] != against[index] and index not in allowed]
    check(not stray, f"0 differing bytes outside the declared sites (found {len(stray)})")
    if stray:
        print(f"     first stray offsets: {[hex(o) for o in stray[:8]]}")
    moved = [index for index in range(min(len(image), len(against)))
             if image[index] != against[index]]
    check(len(moved) == len(manifest["site_changes"]) * 4,
          f"{len(moved)} differing byte(s) in the base equal "
          f"{len(manifest['site_changes'])} site(s) x 4")
    check(len(image) == manifest["output_bytes"], "the output byte count matches the manifest")

    print(f"\n{'VERIFY PASS' if not problems else 'VERIFY FAIL: ' + str(len(problems))}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
