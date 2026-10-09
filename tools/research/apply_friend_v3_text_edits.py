"""Apply the FRIEND-V3-CONTENT-PASS-001 section 3.1 edits into the friend text pool.

WHY A SPAN WRITER. The friend's text table is 1,534 pointers at file `0x6BCE8`
(`tools/webfoot/formats/text_tables.py`). Every section 3.1 replacement is the same
byte length as the site it replaces, or shorter, so the edit is a prefix
substitution: the replacement and its terminator are written over the head of the
site, and every byte after them is left exactly as it was. Nothing is padded and
nothing is relocated, so no offset in the pool moves and no table-named string
starting outside the site can be affected. That last clause is bounded on purpose:
a pointer into the same bytes held in code rather than in the table is not visible
here, which is why the shipped edit table was measured against the real image
rather than trusted.

WHAT A SITE'S SPAN IS, AND WHAT IT IS NOT. A span measured as "the distance to the
next string" is wrong for this pool, and was measured wrong while building this
tool. Slot 1032 at `0x063642` holds `Bulma` (10 bytes, terminator at `0x06364C`),
and the very next bytes are not padding but a second copy of the long Brief
biography - 488 bytes of real text the 1,534-pointer table does not enumerate,
because the slot-1033 pointer was relocated into the appended block and the retail
copy was orphaned in place, beginning at `0x06364E`. Spanning to the next
*enumerated* string swallowed the orphan's whole 490 bytes - 488 bytes of text plus
its terminator - and zeroed them. The pool is not
exhaustively tiled by table targets alone, so a writer addressed by offset has no
way to know whether an unenumerated string is unreachable, and it is not entitled
to treat one as slack.

A site's span is therefore its OWN extent: the text the image holds there plus its
terminator, exactly as the image already holds it. The write is bounded by that
number and by nothing else, and it touches bytes only from the site's first byte
through the replacement and its new terminator.

A span is not proof that nothing else reads those bytes: another pointer-table slot
may aim inside it, and a pointer held in code outside the table cannot be seen at
all. Both cases are refused rather than guessed when the table can show them, and
the report names only the slots whose own spans were written.

WHY IT IS DIGEST-GATED AND SPAN-EXACT. A pool edit addressed by offset is only
meaningful if the bytes at that offset are the text the edit replaces. Every entry
therefore refuses unless the site holds exactly its expected text and terminator
("this site does not hold the text this edit replaces"), and refuses a replacement
that does not fit its span ("<site>: replacement needs N bytes, the span is M").
The whole image is then verified byte-for-byte outside the written regions before
anything is published, because a write correct at every site and wrong somewhere
else is the one failure a per-site check cannot see.

Section 7 of the plan is deliberately a separate table with an empty default. It is
authored wording awaiting the owner's approval, so it is not applied here, and a
caller who has that approval states the table rather than editing this file.

Nothing here writes to a base image: the derivative is staged and published by
rename, and the base's digest is checked before and after.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from tools.webfoot.formats.text_tables import (GBA_ROM_BASE, TERMINATOR,
                                               TextCodecError, decode_string)
from tools.webfoot.write import WriteError, ensure_not_source_alias

#: CONFIRMED. The friend's text pointer table and its entry count for this image.
TABLE_START = 0x0006BCE8
TABLE_COUNT = 1534
NUL = TERMINATOR.to_bytes(2, "little")


class FriendTextEditError(ValueError):
    """A site refused the edit, so no derivative was written."""


@dataclass(frozen=True, slots=True)
class SpanEdit:
    """One site: which slot, where it sits, what it holds now, what it becomes."""

    slot: int
    offset: int
    current: str
    replacement: str

    @property
    def site(self) -> str:
        return f"slot {self.slot} (file 0x{self.offset:06X})"

    def encoded_current(self) -> bytes:
        return self.current.encode("utf-16le") + NUL

    def encoded_replacement(self) -> bytes:
        return self.replacement.encode("utf-16le") + NUL


#: Plan section 3.1, measured against `roms/v3-safe.gba`. Only these seven sites
#: are applied; the plan's section 7 wording is not. Each `current` is the text the
#: image actually holds at that offset, taken from the image rather than from the
#: plan's prose: slot 1033's row quotes a summary of the biography, while v3-safe
#: holds the renamed copy naming Yamcha and Tien.
SECTION_3_1: tuple[SpanEdit, ...] = (
    SpanEdit(1032, 0x063642, "Bulma", "Tulma"),
    SpanEdit(
        1033,
        0x94879C,
        "Bulma Brief is the daughter of the founder and president of the Capsule "
        "Corporation, Dr. Brief. Bulma has many invention patents in her name, most "
        "notably the Dragon Radar. Bulma is often involved in Yamcha's adventures, and "
        "is married to Tien.",
        "Tulma Brief is the daughter of the founder and president of the Capsule "
        "Corporation, Dr. Brief. Tulma is the identical twin sister of Bulma. Like her "
        "sister, Tulma has many invention patents in her name, most notably the Dragon "
        "Radar.",
    ),
    SpanEdit(122, 0x058454, "Great Saiyaman", "Great Soyman"),
    SpanEdit(1453, 0x06B5C4, "Great Saiyaman", "Great Soyman"),
    SpanEdit(603, 0x05DE3E, "Great Saiyaman Saga", "Great Soyman Saga"),
    SpanEdit(1346, 0x06A3E0, "Saiyaman", "Soyman"),
    SpanEdit(
        1347,
        0x949E9E,
        "Press the B Button to turn into the Great Saiyaman.  Press the B Button "
        "again to turn back into Krillin.",
        "Press the B Button to turn into the Great Soyman.  Press the B Button again "
        "to turn back into Goku.",
    ),
)

#: Plan section 7, authored wording awaiting the owner's approval. Empty on purpose:
#: a run that has that approval passes its own table rather than enabling these.
SECTION_7: tuple[SpanEdit, ...] = ()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pointer_offsets(image: bytes) -> list[int]:
    """Every file offset the 1,534-pointer table enumerates, in table order."""
    offsets: list[int] = []
    for index in range(TABLE_COUNT):
        slot = TABLE_START + index * 4
        address = int.from_bytes(image[slot:slot + 4], "little")
        if not GBA_ROM_BASE <= address < GBA_ROM_BASE + len(image):
            raise FriendTextEditError(
                f"pointer table entry {index} holds {address:#010x}, which is not a "
                f"GBA ROM address into this image"
            )
        offsets.append(address - GBA_ROM_BASE)
    return offsets


def apply_edits(image: bytes, edits: tuple[SpanEdit, ...]) -> dict:
    """Rewrite each site's own span in place; touch nothing else.

    The span of an edit is the byte length of the text the image holds there, plus
    its terminator. Anything the replacement does not occupy keeps its base bytes:
    the remainder of the old text and its old terminator stay where they are, which
    is what makes this a prefix write rather than a pad-to-span overwrite.
    """
    sites = pointer_offsets(image)
    out = bytearray(image)
    report_edits: list[dict] = []
    written: list[range] = []
    named = set(sites)
    claimed: list[tuple[int, int]] = []

    for edit in edits:
        if not 0 <= edit.slot < TABLE_COUNT:
            raise FriendTextEditError(
                f"{edit.site}: slot {edit.slot} is outside the table's 0..{TABLE_COUNT - 1}"
            )
        if edit.offset not in named:
            raise FriendTextEditError(
                f"{edit.site}: no entry of the text pointer table starts here, so this "
                f"is not a site of the friend text pool"
            )
        if sites[edit.slot] != edit.offset:
            raise FriendTextEditError(
                f"{edit.site}: the pointer table's slot {edit.slot} starts at "
                f"0x{sites[edit.slot]:06X}, not at this edit's offset"
            )
        # Two edits over one site would let the second silently overwrite the first
        # and both would be reported as applied.
        span = len(edit.encoded_current())
        if any(edit.offset < done_end and done_start < edit.offset + span
               for done_start, done_end in claimed):
            raise FriendTextEditError(
                f"{edit.site}: this site's span overlaps another edit already claimed"
            )
        claimed.append((edit.offset, edit.offset + span))
        # A pointer that aims INSIDE this span would have its own string changed by
        # this write, and the report would not name it. So would a SECOND slot aliasing
        # this very offset, which is why the count is compared and not only the
        # offsets: an alias has no offset of its own to compare against.
        intruders = sorted(other for other in named
                           if edit.offset < other < edit.offset + span)
        aliases = sum(1 for value in sites if value == edit.offset)
        if intruders or aliases > 1:
            where = f"0x{intruders[0]:06X}" if intruders else f"0x{edit.offset:06X}"
            reason = (f"a string starts inside it at {where}" if intruders
                      else f"{aliases} table slots alias it at {where}")
            raise FriendTextEditError(
                f"{edit.site}: {reason}, and this edit names only its own slot, so "
                f"rewriting it would change a site the report does not name"
            )
        expected = edit.encoded_current()
        actual = bytes(image[edit.offset:edit.offset + span])
        if actual != expected:
            raise FriendTextEditError(
                f"{edit.site}: this site does not hold the text this edit replaces: it "
                f"holds {actual.decode('utf-16le', 'replace')!r} where "
                f"{edit.current!r} was expected"
            )
        replacement = edit.encoded_replacement()
        if len(replacement) > span:
            raise FriendTextEditError(
                f"{edit.site}: replacement needs {len(replacement)} bytes, the span is "
                f"{span}"
            )
        out[edit.offset:edit.offset + span] = replacement + image[
            edit.offset + len(replacement):edit.offset + span]
        touched = [index for index in range(edit.offset, edit.offset + span)
                   if image[index] != out[index]]
        written.append(range(edit.offset, edit.offset + span))
        report_edits.append({
            "slot": edit.slot,
            "offset": edit.offset,
            "offset_hex": f"0x{edit.offset:06X}",
            "span_bytes": span,
            "current": edit.current,
            "replacement": edit.replacement,
            "replacement_bytes": len(replacement),
            "changed_bytes": len(touched),
            "changed_offsets": touched,
        })

    permitted: set[int] = set()
    for span in written:
        permitted.update(span)
    stray = [index for index in range(len(image))
             if image[index] != out[index] and index not in permitted]
    if stray:
        raise FriendTextEditError(
            f"{len(stray)} byte(s) outside the named spans changed, first at "
            f"0x{stray[0]:06X}; refusing to publish"
        )
    changed = sorted(index for index in permitted if image[index] != out[index])
    return {"image": bytes(out), "edits": report_edits, "changed": changed}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True)
    parser.add_argument("--base-sha256", required=True,
                        help="the exact digest the base must have")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--sections", default="3.1",
                        help="which planned section to apply: 3.1 (default). "
                             "Section 7 has no approved table and cannot be selected")
    args = parser.parse_args()

    base, destination = Path(args.base), Path(args.out)
    try:
        ensure_not_source_alias(base, destination)
        if args.report:
            ensure_not_source_alias(base, Path(args.report))
            ensure_not_source_alias(destination, Path(args.report))
    except WriteError as exc:
        raise SystemExit(str(exc)) from exc

    measured = sha256(base)
    if measured != args.base_sha256.lower():
        raise SystemExit(
            f"the base is not the declared image: {measured} != {args.base_sha256.lower()}"
        )

    if args.sections.strip() != "3.1":
        raise SystemExit(
            f"section {args.sections!r} has no approved edit table: only 3.1 is applied, "
            f"and section 7 is authored wording still awaiting owner approval"
        )

    image = base.read_bytes()
    try:
        result = apply_edits(image, SECTION_3_1)
    except (FriendTextEditError, TextCodecError) as exc:
        raise SystemExit(str(exc)) from exc

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent,
                                     prefix=destination.name + ".",
                                     suffix=".partial", delete=False) as handle:
        staged = Path(handle.name)
        try:
            handle.write(result["image"])
        except BaseException:
            handle.close()
            staged.unlink(missing_ok=True)
            raise
    staged.replace(destination)

    after = sha256(base)
    if after != args.base_sha256.lower():
        raise SystemExit("the base image changed during the build")

    report = {
        "base_sha256": measured,
        "output": str(destination),
        "output_sha256": sha256(destination),
        "size": len(result["image"]),
        "edits": result["edits"],
        "changed_byte_count": len(result["changed"]),
        "changed_offsets": result["changed"],
    }
    print(f"derivative     : {destination}")
    print(f"derivative sha : {report['output_sha256']}")
    print(f"size           : {report['size']} bytes")
    print(f"edits applied  : {len(report['edits'])}")
    for edit in report["edits"]:
        print(f"  slot {edit['slot']:<5} {edit['offset_hex']}  span {edit['span_bytes']:>4} B"
              f"  replacement {edit['replacement_bytes']:>4} B"
              f"  {edit['changed_bytes']:>3} byte(s) changed")
    print(f"total bytes changed: {report['changed_byte_count']}")
    print("changed offsets    : " + ", ".join(f"0x{o:06X}" for o in result["changed"]))
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"report         : {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
