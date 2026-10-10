"""Write the owner-approved text batch into a friend image.

WHAT THIS IS. The seven approved biographies and the approved grammar repair to slot
1065, from the owner decision log (2026-10-10). The wording below is quoted from that
record; nothing here is invented, paraphrased or guessed.

HOW EACH SITE IS WRITTEN, AND WHY THE ASYMMETRY IS DELIBERATE.

* In place, when the approved text is no longer than the text it replaces: the new
  string and its terminator are written at the site's own offset and the tail bytes of
  the old span are left as they are. They are past the terminator, so no reader reaches
  them, and leaving them means the write is confined to offsets the site already owned.
* Relocated, when it is longer: the string is appended past the end of image, its single
  table pointer is repointed, and the guard is that a grown site must have exactly ONE
  word-aligned reference in the whole image - its own table entry. A string something
  else also points at would be moved out from under that reader, so it is refused.

Every site is checked before it is written: the table slot must point at the offset the
edit names, and the bytes there must be the text the edit replaces. A mismatch is a
refusal, never a correction.

Usage:
  python tools/research/apply_friend_v3_text_batch.py --image IN.gba \
      --expect-sha256 <hex> --out OUT.gba --manifest OUT.json
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

TABLE_START = 0x6BCE8
TABLE_SLOTS = 1534
ROM_BASE = 0x08000000
TERMINATOR = b"\x00\x00"


class TextBatchError(ValueError):
    """The batch refused rather than writing a byte it could not verify."""


class Edit:
    """One approved site: its slot, the text it holds now, and the approved text."""

    __slots__ = ("slot", "old", "new", "label")

    def __init__(self, slot: int, old: str, new: str, label: str) -> None:
        self.slot = slot
        self.old = old
        self.new = new
        self.label = label


#: The owner's approved wording, from the decision log. `old` is the text this image's
#: slot holds now, which is the guard that the write lands where the approval says.
APPROVED: tuple[Edit, ...] = (
    Edit(1189,
         "Yamcha is a Saiyan from the planet Vegeta that was stranded on Earth. He is an "
         "all-around good guy, who often saves the Earth.",
         "Yamcha was once a handsome bandit of the Diablo Desert, and is now one of "
         "Earth's greatest defenders.",
         "biography, Yamcha"),
    Edit(1195,
         "Tien was the prince of the Planet Vegeta before it was destroyed by Frieza. "
         "Although he was once a villian, he usually fights for the Z-Fighters now.",
         "Once a Crane School assassin and Yamcha's fierce rival, Tien now fights beside "
         "him. Husband of Tulma and father of Uub, he wields the Tri-Beam.",
         "biography, Tien"),
    Edit(1187,
         "Krillin is the son of Yamcha and Bulma. He is half human and half Saiyan. "
         "Krillin defeated Cell in the Cell Games.",
         "Krillin, son of Yamcha and Bulma, defeated Cell and now fights crime as the "
         "Great Soyman.",
         "biography, Krillin"),
    Edit(1191,
         "Videl is the son of  Yamcha and Bulma. Despite his young age, he's one of the "
         "most powerful fighters in the universe.",
         "Daughter of Yamcha and Bulma, Videl fights crime and attends Orange Star High "
         "School with her brother Krillin.",
         "biography, Videl"),
    Edit(1193,
         "Uub is the son of Tien and Tulma. Despite his young age he's one of the most "
         "powerful fighters in the universe.",
         "Uub is the adopted son of Tien and Tulma. Though young, he's one of the most "
         "powerful fighters in the universe.",
         "biography, Uub"),
    Edit(1059,
         "Once Dr. Gero's evil Android, she has now changed her ways and fights for the "
         "good guys. Is married to Goku.",
         "Chi-Chi, daughter of the Ox-King, is a fierce martial artist and the devoted, "
         "strong-willed wife of Goku.",
         "biography, Chi-Chi"),
    Edit(1069,
         "Gohan was once known as the dreaded Desert Bandit of Diablo Desert. He's now "
         "one of good guys.",
         "Gohan lost his left arm fighting the Androids, yet he never gave up and trained "
         "the next hero.",
         "biography, Future Gohan"),
    Edit(1065,
         "Tien was once a rival of Yamcha is now a loyal Z-Fighter. His most "
         "distinguishing feature is his mysterious third eye.",
         "Tien was once a rival of Yamcha, and is now a loyal Z-Fighter. His most "
         "distinguishing feature is his mysterious third eye.",
         "grammar repair"),
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def encoded(text: str) -> bytes:
    return text.encode("utf-16le")


def current_span(image: bytes, slot: int) -> tuple[int, int, str]:
    """``(file offset, span bytes including the terminator, text)`` for one slot."""
    if not 0 <= slot < TABLE_SLOTS:
        raise TextBatchError(f"slot {slot} is outside the pointer table")
    pointer_at = TABLE_START + slot * 4
    address = int.from_bytes(image[pointer_at:pointer_at + 4], "little")
    if address < ROM_BASE:
        raise TextBatchError(f"slot {slot} is not a ROM pointer")
    offset = address - ROM_BASE
    end = offset
    while image[end:end + 2] != TERMINATOR:
        end += 2
        if end >= len(image):
            raise TextBatchError(f"slot {slot}: no terminator before the end of image")
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


def apply(image: bytes, edits: tuple[Edit, ...]) -> tuple[bytes, list[dict]]:
    out = bytearray(image)
    report: list[dict] = []
    touched: set[int] = set()
    for edit in edits:
        offset, span, text = current_span(image, edit.slot)
        if text != edit.old:
            raise TextBatchError(
                f"{edit.label}: slot {edit.slot} holds {text!r}, not the text this edit "
                "replaces; refusing rather than correcting"
            )
        new = encoded(edit.new)
        if offset in touched:
            raise TextBatchError(f"{edit.label}: two edits name the same site")
        touched.add(offset)
        entry = {"slot": edit.slot, "label": edit.label, "old_offset": offset,
                 "old_span_bytes": span, "new_units": len(edit.new)}
        if len(new) + len(TERMINATOR) <= span:
            out[offset:offset + len(new)] = new
            out[offset + len(new):offset + len(new) + len(TERMINATOR)] = TERMINATOR
            entry.update(method="in place", new_offset=offset,
                         freed_bytes=span - len(new) - len(TERMINATOR))
        else:
            found = references(image, ROM_BASE + offset)
            if found != 1:
                raise TextBatchError(
                    f"{edit.label}: the grown site is named by {found} word-aligned "
                    "reference(s), not exactly its own table entry, so moving it would "
                    "orphan a reader"
                )
            start = len(out)
            while start % 4:
                out.append(0x00)
                start += 1
            out += new + TERMINATOR
            pointer_at = TABLE_START + edit.slot * 4
            out[pointer_at:pointer_at + 4] = (ROM_BASE + start).to_bytes(4, "little")
            entry.update(method="relocated", new_offset=start,
                         new_pointer=hex(ROM_BASE + start),
                         added_bytes=len(out) - len(image))
        report.append(entry)
    return bytes(out), report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest")
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise TextBatchError(f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")

    output, report = apply(image, APPROVED)
    target = Path(args.out)
    # THE INPUT IS NEVER THE OUTPUT, and the write is staged and read back before it is
    # published, so a run cannot overwrite the image it verified against.
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise TextBatchError(f"REFUSED: {error}") from error
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(output)
    if staged.read_bytes() != output:
        raise TextBatchError(f"REFUSED: the staged write at {staged} does not match the plan")
    staged.replace(target)
    manifest = {
        "input": str(source), "input_sha256": got, "input_bytes": len(image),
        "output": str(target), "output_sha256": sha256_bytes(output),
        "output_bytes": len(output), "growth_bytes": len(output) - len(image),
        "edits": report,
    }
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, indent=2) + "\n",
                                       encoding="utf-8")
    for entry in report:
        print(f"slot {entry['slot']:>4} {entry['label']:<18} {entry['method']:<10} "
              f"span {entry['old_span_bytes']:>4} -> {entry['new_units'] * 2:>4} units")
    print(f"# wrote {target} {len(output)} bytes sha256 {manifest['output_sha256']} "
          f"(growth {manifest['growth_bytes']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
