"""Apply the FRIEND-V3-COMPLETE-TEXT-PASS-001 menu-pool edits.

WHY A SECOND SPAN WRITER. The content pass shipped and merged its own seven-site table
in `apply_friend_v3_text_edits.py`; this ticket adds sites to the same pool. The span
rule, the guards and the staging are imported from that tool rather than copied, because
the rule that matters here is the one that cost the previous ticket a defect: a site's
span is its OWN text plus its own terminator, never the distance to the next table-named
string, and the replacement covers only the front of that span.

TWO MECHANISMS, because two different things have to happen and each keeps one job:

  * SECTION_2 writes in place. Every replacement is at most as long as the text it
    replaces, so nothing moves and no pointer changes.
  * SECTION_3 relocates. Its replacement is LONGER than the site's span, which an
    in-place prefix write cannot express. Each relocated site is appended to the end of
    the image and its single table pointer is repointed, which is the mechanism the
    earlier rename pass used for 84 slots. The guard is what makes it safe: the tool
    counts every word-aligned occurrence of the site's old pointer in the whole image
    and refuses unless there is exactly ONE, its own table entry. A string referenced
    from code as well as from the table would be found twice and refused.

THE PROVENANCE RULE, WHICH IS WHY THESE SITES AND NOT OTHERS. The rename pass left two
different characters spelled `Bulma` in this pool. Where the canonical ROM holds `Bulma`
in a slot, the word is original Bulma and the content pass renamed that character to
Tulma, so the slot follows. Where the canonical ROM holds `Chi-Chi`, the rename pass put
the DISPLAYED name `Bulma` there, and that word keeps it: slots 535, 1082, 1083, 1123,
1187 and 1191 are deliberately absent. Slot 1033 is the content pass's authored
twin-sister biography and is preserved as approved.

The other sites are names the audit found shown as their own retail spelling:
`Gogeta`/`Vegito` (four of the nine carry it in dialogue already) and one CASCADE, slot
1347, where the content pass applied the map twice - retail `Gohan` had already become
`Krillin`, and the merged image shows `Goku`. That slot is corrected back to the
single-step name.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from tools.research.apply_friend_v3_text_edits import (FriendTextEditError, SpanEdit,
                                                       apply_edits, sha256)
from tools.webfoot.formats.text_tables import GBA_ROM_BASE, TextCodecError
from tools.webfoot.write import WriteError, ensure_not_source_alias

#: CONFIRMED. The friend's text pointer table.
TABLE_START = 0x0006BCE8
NUL = b"\x00\x00"

#: In-place sites. Each replacement is the same byte length as the text it replaces or
#: shorter, measured against the built image rather than against the plan's prose.
SECTION_2: tuple[SpanEdit, ...] = (
    SpanEdit(527, 0x05D52E, "Bulma's Airship", "Tulma's Airship"),
    SpanEdit(528, 0x05D54E, "Bulma's House", "Tulma's House"),
    SpanEdit(618, 0x05E0A6, 'Fly to West City and talk to Bulma',
             'Fly to West City and talk to Tulma'),
    SpanEdit(624, 0x9485CA, "Tell Bulma and Tien That Yamcha's Coming Back",
             "Tell Tulma and Tien That Yamcha's Coming Back"),
    SpanEdit(627, 0x05E382, 'Meet Bulma to go to the World Tournament',
             'Meet Tulma to go to the World Tournament'),
    SpanEdit(634, 0x05E560, 'Get the Dragon Radar from Bulma',
             'Get the Dragon Radar from Tulma'),
    SpanEdit(1075, 0x064920,
             "Dr. Brief is the president of the Capsule Corporation, and Bulma's father.",
             "Dr. Brief is the president of the Capsule Corporation, and Tulma's father."),
    SpanEdit(1077, 0x0649CC, "Mrs. Brief is Dr. Brief's wife, and Bulma's mother.",
             "Mrs. Brief is Dr. Brief's wife, and Tulma's mother."),
    SpanEdit(1193, 0x9499B8,
             "Uub is the son of Tien and Bulma. Despite his young age he's one of the "
             "most powerful fighters in the universe.",
             "Uub is the son of Tien and Tulma. Despite his young age he's one of the "
             "most powerful fighters in the universe."),
    SpanEdit(136, 0x058552, "SS Gogeta", "SS Yamien"),
    SpanEdit(165, 0x058754, "Gogeta", "Yamien"),
    SpanEdit(181, 0x058836, "GOGETA", "YAMIEN"),
    SpanEdit(1304, 0x068F7E, "Gogeta", "Yamien"),
    SpanEdit(1305, 0x949CE0,
             "Gogeta is the fusion of Yamcha and Tien using the Metamorese Art of Fusion.",
             "Yamien is the fusion of Yamcha and Tien using the Metamorese Art of Fusion."),
)


@dataclass(frozen=True, slots=True)
class RelocatedEdit:
    """One site whose replacement needs more bytes than its span holds."""

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


#: Relocated sites. Every one of these grows by at least one character, so the in-place
#: writer refuses it by design and the append-and-repoint path carries it.
SECTION_3: tuple[RelocatedEdit, ...] = (
    RelocatedEdit(134, 0x058530, "Vegito", "Tiencha"),
    RelocatedEdit(135, 0x05853E, "SS Vegito", "SS Tiencha"),
    RelocatedEdit(164, 0x058746, "Vegito", "Tiencha"),
    RelocatedEdit(180, 0x058828, "VEGITO", "TIENCHA"),
    RelocatedEdit(1306, 0x069024, "Vegito", "Tiencha"),
    RelocatedEdit(1307, 0x949D78,
                  "Vegito is the fusion of Yamcha and Tien using the magic Potara "
                  "earrings.",
                  "Tiencha is the fusion of Yamcha and Tien using the magic Potara "
                  "earrings."),
    RelocatedEdit(1347, 0x949E9E,
                  "Press the B Button to turn into the Great Soyman.  Press the B Button "
                  "again to turn back into Goku.",
                  "Press the B Button to turn into the Great Soyman.  Press the B Button "
                  "again to turn back into Krillin."),
)


def references(image: bytes, address: int) -> int:
    """Every word-aligned occurrence of `address` in the image."""
    needle = address.to_bytes(4, "little")
    count = 0
    position = image.find(needle)
    while position != -1:
        if position % 4 == 0:
            count += 1
        position = image.find(needle, position + 1)
    return count


def apply_relocations(image: bytes, edits: tuple[RelocatedEdit, ...]) -> dict:
    """Append each grown string and repoint its one table pointer at the new copy."""
    out = bytearray(image)
    report: list[dict] = []
    touched: set[int] = set()
    for edit in edits:
        if not 0 <= edit.slot < 1534:
            raise FriendTextEditError(f"{edit.site}: slot is outside the pointer table")
        pointer_at = TABLE_START + edit.slot * 4
        address = int.from_bytes(out[pointer_at:pointer_at + 4], "little")
        if address != GBA_ROM_BASE + edit.offset:
            raise FriendTextEditError(
                f"{edit.site}: the table's slot {edit.slot} points at "
                f"{address:#010x}, not at this edit's offset"
            )
        span = len(edit.encoded_current())
        actual = bytes(out[edit.offset:edit.offset + span])
        if actual != edit.encoded_current():
            raise FriendTextEditError(
                f"{edit.site}: this site does not hold the text this edit replaces: it "
                f"holds {actual.decode('utf-16le', 'replace')!r}"
            )
        if len(edit.encoded_replacement()) <= span:
            raise FriendTextEditError(
                f"{edit.site}: the replacement fits the site's own span, so it belongs "
                f"to the in-place table and not to the relocation path"
            )
        found = references(out, address)
        if found != 1:
            raise FriendTextEditError(
                f"{edit.site}: {found} word-aligned references to {address:#010x} exist, "
                f"and this tool only repoints a site referenced exactly once"
            )
        while len(out) % 4:
            out.append(0)
        new_offset = len(out)
        out += edit.encoded_replacement()
        out[pointer_at:pointer_at + 4] = (
            GBA_ROM_BASE + new_offset).to_bytes(4, "little")
        touched.update(range(pointer_at, pointer_at + 4))
        report.append({
            "slot": edit.slot,
            "old_offset": f"0x{edit.offset:06X}",
            "new_offset": f"0x{new_offset:06X}",
            "old_address": f"0x{address:08X}",
            "new_address": f"0x{GBA_ROM_BASE + new_offset:08X}",
            "current": edit.current,
            "replacement": edit.replacement,
            "appended_bytes": len(edit.encoded_replacement()),
        })

    stray = [index for index in range(len(image))
             if image[index] != out[index] and index not in touched]
    if stray:
        raise FriendTextEditError(
            f"{len(stray)} byte(s) outside the repointed pointers changed, first at "
            f"0x{stray[0]:06X}; refusing to publish"
        )
    return {"image": bytes(out), "edits": report,
            "changed": sorted(touched), "appended": len(out) - len(image)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True)
    parser.add_argument("--base-sha256", required=True,
                        help="the exact digest the base must have")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
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

    try:
        in_place = apply_edits(base.read_bytes(), SECTION_2)
        relocated = apply_relocations(in_place["image"], SECTION_3)
    except (FriendTextEditError, TextCodecError) as exc:
        raise SystemExit(str(exc)) from exc

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent,
                                     prefix=destination.name + ".",
                                     suffix=".partial", delete=False) as handle:
        staged = Path(handle.name)
        try:
            handle.write(relocated["image"])
        except BaseException:
            handle.close()
            staged.unlink(missing_ok=True)
            raise
    staged.replace(destination)

    if sha256(base) != args.base_sha256.lower():
        raise SystemExit("the base image changed during the build")

    report = {
        "base_sha256": measured,
        "output": str(destination),
        "output_sha256": sha256(destination),
        "size": len(relocated["image"]),
        "in_place_edits": in_place["edits"],
        "relocated_edits": relocated["edits"],
        "appended_bytes": relocated["appended"],
        "changed_byte_count": len(in_place["changed"]) + len(relocated["changed"]),
        "changed_offsets": in_place["changed"] + relocated["changed"],
    }
    print(f"derivative     : {destination}")
    print(f"derivative sha : {report['output_sha256']}")
    print(f"size           : {report['size']} bytes")
    print(f"in place       : {len(report['in_place_edits'])} site(s), "
          f"{len(in_place['changed'])} byte(s)")
    print(f"relocated      : {len(report['relocated_edits'])} site(s), "
          f"{report['appended_bytes']} byte(s) appended")
    for edit in report["relocated_edits"]:
        print(f"  slot {edit['slot']:<5} {edit['old_offset']} -> {edit['new_offset']}")
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"report         : {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
