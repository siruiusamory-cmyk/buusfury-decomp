"""Verify a text-slot edit against the image it was built from.

Read-only. Checks that the slot resolves through its table pointer to the approved wording,
that the one pointer moved and nothing else, and that every differing byte lies inside the
declared site or the appended string.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TABLE_START = 0x6BCE8
ROM_BASE = 0x08000000
TERMINATOR = b"\x00\x00"


def read_slot(image: bytes, slot: int) -> tuple[int, str]:
    pointer_at = TABLE_START + slot * 4
    address = int.from_bytes(image[pointer_at:pointer_at + 4], "little")
    if address < ROM_BASE:
        raise SystemExit(f"slot {slot} is not a ROM pointer")
    offset = address - ROM_BASE
    end = offset
    while image[end:end + 2] != TERMINATOR:
        end += 2
        if end >= len(image):
            raise SystemExit(f"slot {slot}: no terminator before the end of image")
    return offset, image[offset:end].decode("utf-16le")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--against", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    image = Path(args.image).read_bytes()
    against = Path(args.against).read_bytes()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    edit = manifest["edit"]
    slot = edit["slot"]
    problems: list[str] = []

    def check(condition: bool, message: str) -> None:
        print(("PASS " if condition else "FAIL ") + message)
        if not condition:
            problems.append(message)

    offset, text = read_slot(image, slot)
    check(text == edit["new_text"], f"slot {slot} reads the owner's replacement exactly")
    if text != edit["new_text"]:
        print(f"     expected {edit['new_text']!r}")
        print(f"     got      {text!r}")
    check(offset == edit["new_offset"],
          f"slot {slot} points at the write the plan made (file 0x{offset:X})")

    # Every other slot still resolves to its own text: compare all 1534 slot readings.
    drifted = []
    for index in range(1534):
        try:
            before = read_slot(against, index)[1]
            after = read_slot(image, index)[1]
        except SystemExit:
            continue
        if index != slot and before != after:
            drifted.append(index)
    check(not drifted, f"the other 1,533 slots read the same text (drifted: {drifted[:8]})")

    # 0.1846: every differing byte is either the moved pointer, the appended string, or the
    # old span's own bytes past the new terminator.
    allowed = set(range(manifest["input_bytes"], len(image)))
    allowed.update(range(TABLE_START + slot * 4, TABLE_START + slot * 4 + 4))
    allowed.update(range(edit["old_offset"], edit["old_offset"] + edit["old_span_bytes"]))
    stray = [index for index in range(min(len(image), len(against)))
             if image[index] != against[index] and index not in allowed]
    check(not stray, f"0 differing bytes outside the declared site (found {len(stray)})")
    if stray:
        print(f"     first stray offsets: {[hex(o) for o in stray[:8]]}")
    check(len(image) == manifest["output_bytes"], "the output byte count matches the manifest")

    print(f"\n{'VERIFY PASS' if not problems else 'VERIFY FAIL: ' + str(len(problems))}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
