"""Write one owner-approved text-table slot into a friend image.

WHY THIS IS A SEPARATE TOOL FROM THE TEXT BATCH. The batch writes a fixed set of approved
sites and refuses everything else; this writes ONE named slot and refuses if the bytes there
are not the text the approval replaces. Keeping it separate means a later quick fix cannot
widen the batch that produced the release it is based on.

HOW THE SITE IS WRITTEN. In place, when the approved text is no longer than the text it
replaces: the string and its terminator are written at the site's own offset and the tail of
the old span is left alone, because it lies past the terminator and no reader reaches it.
Relocated, when it is longer: the string is appended past the end of image, its single table
pointer is repointed, and the guard is that a grown site must have exactly ONE word-aligned
reference in the image - its own table entry. A string something else also names would be
moved out from under that reader, so it is refused.

Usage:
  python tools/research/apply_friend_v3_text_slot.py --image IN.gba \
      --expect-sha256 <hex> --slot N --old "..." --new "..." \
      --out OUT.gba --manifest OUT.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402
from tools.research.friend_v3_text_approvals import APPROVED_TEXT_SLOTS  # noqa: E402

TABLE_START = 0x6BCE8
TABLE_SLOTS = 1534
ROM_BASE = 0x08000000
TERMINATOR = b"\x00\x00"


class TextSlotError(ValueError):
    """The write refused rather than placing a byte it could not verify."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def current_span(image: bytes, slot: int) -> tuple[int, int, str]:
    """``(file offset, span bytes including the terminator, text)`` for one slot."""
    if not 0 <= slot < TABLE_SLOTS:
        raise TextSlotError(f"slot {slot} is outside the pointer table")
    pointer_at = TABLE_START + slot * 4
    address = int.from_bytes(image[pointer_at:pointer_at + 4], "little")
    if address < ROM_BASE:
        raise TextSlotError(f"slot {slot} is not a ROM pointer")
    offset = address - ROM_BASE
    end = offset
    while image[end:end + 2] != TERMINATOR:
        end += 2
        if end >= len(image):
            raise TextSlotError(f"slot {slot}: no terminator before the end of image")
    return offset, end + 2 - offset, image[offset:end].decode("utf-16le")


def references(image: bytes, address: int) -> int:
    """Every word-aligned occurrence of an address in the image."""
    needle = address.to_bytes(4, "little")
    count = 0
    position = image.find(needle)
    while position != -1:
        if position % 4 == 0:
            count += 1
        position = image.find(needle, position + 1)
    return count


def apply(image: bytes, slot: int, old: str, new: str) -> tuple[bytes, dict]:
    out = bytearray(image)
    offset, span, text = current_span(image, slot)
    if text != old:
        raise TextSlotError(
            f"slot {slot} holds {text!r}, not the text this edit replaces; refusing rather "
            "than correcting")
    encoded = new.encode("utf-16le")
    entry = {"slot": slot, "old_offset": offset, "old_span_bytes": span,
             "old_units": len(old), "old_text": old, "new_text": new,
             "new_units": len(new), "new_bytes": len(encoded),
             "new_span_bytes": len(encoded) + len(TERMINATOR)}
    if len(encoded) + len(TERMINATOR) <= span:
        out[offset:offset + len(encoded)] = encoded
        out[offset + len(encoded):offset + len(encoded) + len(TERMINATOR)] = TERMINATOR
        entry.update(method="in place", new_offset=offset,
                     freed_bytes=span - len(encoded) - len(TERMINATOR))
        return bytes(out), entry

    found = references(image, ROM_BASE + offset)
    if found != 1:
        raise TextSlotError(
            f"slot {slot}: the grown site is named by {found} word-aligned reference(s), not "
            "exactly its own table entry, so moving it would orphan a reader")
    start = len(out)
    while start % 4:
        out.append(0x00)
        start += 1
    out += encoded + TERMINATOR
    pointer_at = TABLE_START + slot * 4
    old_pointer = bytes(image[pointer_at:pointer_at + 4])
    out[pointer_at:pointer_at + 4] = (ROM_BASE + start).to_bytes(4, "little")
    entry.update(method="relocated", new_offset=start,
                 new_pointer=f"0x{ROM_BASE + start:08X}",
                 old_pointer=old_pointer.hex(),
                 added_bytes=len(out) - len(image))
    return bytes(out), entry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--slot", type=int, required=True)
    parser.add_argument("--old", required=True)
    parser.add_argument("--new", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise TextSlotError(f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")

    approved = next((edit for edit in APPROVED_TEXT_SLOTS if edit.slot == args.slot), None)
    if approved is None:
        raise TextSlotError(
            f"slot {args.slot} has no approved wording in "
            "tools/research/friend_v3_text_approvals.py, so this tool will not write it")
    if args.old != approved.old or args.new != approved.new:
        raise TextSlotError(
            f"slot {args.slot}: the requested text is not the approved wording for this slot "
            f"({approved.label}, {approved.approval}); refusing")

    output, entry = apply(image, args.slot, args.old, args.new)
    entry["approval"] = approved.approval
    entry["label"] = approved.label
    report = {"input": str(source), "input_sha256": got, "input_bytes": len(image),
              "edit": entry, "output_bytes": len(output)}
    target = Path(args.out)
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise TextSlotError(f"REFUSED: {error}") from error
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(output)
    if staged.read_bytes() != output:
        raise TextSlotError("REFUSED: the staged write does not match the plan")
    staged.replace(target)
    report["output"] = str(target)
    report["output_sha256"] = sha256_bytes(output)
    Path(args.manifest).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"# slot {entry['slot']}: {entry['method']} at file 0x{entry['new_offset']:X}, "
          f"{entry['old_span_bytes']} -> {len(args.new) * 2 + 2} bytes")
    print(f"# wrote {target} {len(output)} bytes sha256 {report['output_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
