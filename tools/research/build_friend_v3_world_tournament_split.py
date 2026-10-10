"""Build the World Tournament text release on the split-container route.

WHY THIS WRITES RATHER THAN RE-LAYS OUT. Every one of the eighteen World Tournament records
sits inside a 3,872-byte covering record that spans 6232..10104 of container 3, so shrinking
any of them in place would move bytes the covering record reads. The covering record does not
move: the bytes it reads are left exactly as they are. The records the scene actually reads
are the eighteen, and each one is COPIED into a new container on selector 7 with the wording
the owner approved, its handle words rewritten to name the new home. That is the whole edit:
no container byte of the original moves, no game code changes, and the table word at file
0x9A9D04 is the only table slot touched.

WHY THE TABLE IS NOT MOVED. The engine reads the table's base from one literal word at file
0x123CC, and the release already reserves selector slots past the seven live ones: slot 7 at
file 0x9A9D04 belongs to the same 64-slot block, in 228 bytes of retail data that this image
copies but nothing names. Writing slot 7 there was measured on the emulator in this ticket's
route proof (the engine resolved selector 7 from that slot and rendered the container). This
builder therefore writes exactly that slot and rewrites the handle words, and it does not
move the table, so the edit's shape is the shape that was run.

REFUSALS. The builder checks the input digest, checks that every named record exists at the
named identity, refuses any handle word that does not carry the record's own handle, refuses
a row whose approved wording cannot be encoded, and reads the staged file back before
publishing. Nothing is written on a disagreement.
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

from tools.webfoot import compressed_dialogue as cd             # noqa: E402
from tools.webfoot.dialogue_repack import (container_pointers,  # noqa: E402
                                           text_of)
from tools.webfoot.formats import webfoot_lz                    # noqa: E402
from tools.webfoot.handles import DialogueHandle                # noqa: E402
from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402

ROM_BASE = 0x08000000
#: The one word that names the container table base.
TABLE_LITERAL = 0x123CC
#: Selector 7's slot, inside the table's own 64-slot block and past the seven live pointers.
TABLE_SLOT_NEW = 0x9A9D04
NEW_SELECTOR = 7
SPACE = 0x0020

#: The owner's script, verbatim. `prefix` is the record's own leading control unit, kept as
#: the record carries it; `None` marks a row the owner left unchanged except where noted.
OWNER_ROWS: tuple[tuple[str, str | None], ...] = (
    ("3:7406:136",
     "Hey sis, if you win the tournament, what do you think you'll get with the prize Zeni?"),
    ("3:7542:42", "Uh, tons of okonomiyaki, I guess!"),
    ("3:7584:80", "Sheesh, Videl! How are you not fat?"),
    ("3:7664:60", "EXCUSE ME?! What are you going to get then?"),
    ("3:7724:72", "Candy. Lots and lots of candy."),
    ("3:7796:204", "And you call me fat. Hey, isn't that kind of meta?"),
    ("3:8000:214",
     "Hey, half pint! We don't take too kindly to your folk around here."),
    ("3:8214:118", "Huh? Do you mean brown people?"),
    ("3:8332:218",
     "What?! No! My mom may be racist, but I'm not! Geez, I meant adopted kids!"),
    ("3:8550:414", None),
    ("3:8964:148", None),
    ("3:9112:62", "You really made me look bad earlier."),
    ("3:9174:114", "Bruh. You were still totally a dick."),
    ("3:9288:282",
     "That's my baby Idasa down there! Oooooo! Idasa! I wish they would match Idasa up "
     "with a whiter kid! This is a disgrace!"),
    ("3:9570:92", None),
    ("3:9662:116", "Get him, Uub! You make that boy sorry his mom is racist!"),
    ("3:9778:114", "Noooo! My baby! That was unfair! That thing cheated!"),
)
#: Row 18 replaces one passage inside the announcer's record and preserves the rest exactly.
WT18_RECORD = "3:9892:486"
WT18_OLD = "Championship between eight-year-old Uub    and seven-year-old Videl!"
WT18_NEW = ("Championship between adopted siblings, ten-year-old Uub and "
            "sixteen-year-old Videl!")


class WorldTournamentBuildError(ValueError):
    """The build refused rather than writing a byte it could not verify."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def record_index(image: bytes):
    """``key -> (decoded stream, container file offset, handle sites)`` for selector 3."""
    pointers = container_pointers(image)
    offset = pointers[3] - ROM_BASE
    stream = bytes(webfoot_lz.unpack(image, offset).data)
    out: dict[str, tuple[bytes, int, list[int]]] = {}
    for record in cd.dialogue_record_inventory(image, 3, len(stream)):
        key = f"3:{record.handle.decoded_start}:{record.handle.decoded_length}"
        out[key] = (stream, offset, list(record.sites))
    return out


def plan(image: bytes) -> tuple[list[dict], list[str]]:
    """Every row, with the wording it must read and the sites to rewrite."""
    index = record_index(image)
    rows: list[dict] = []
    notes: list[str] = []
    for key, approved in OWNER_ROWS + ((WT18_RECORD, None),):
        found = index.get(key)
        if found is None:
            raise WorldTournamentBuildError(f"{key}: no record carries this identity")
        stream, offset, sites = found
        _sel, start, length = (int(part) for part in key.split(":"))
        current = text_of(stream, start, length)
        if approved is None and key == WT18_RECORD:
            if WT18_OLD not in current:
                raise WorldTournamentBuildError(
                    f"{key}: the passage to replace is absent")
            approved = current.replace(WT18_OLD, WT18_NEW)
        if approved is None:
            notes.append(f"{key}: unchanged by owner decision")
            continue
        prefix = current[:1] if current[:1] in "#!" else ""
        text = prefix + approved
        encoded = text.encode("utf-16le")
        if len(encoded) > 4094:
            raise WorldTournamentBuildError(
                f"{key}: {len(encoded)} bytes, above the 4,094-byte length field")
        rows.append({"record": key, "current": current, "text": text,
                     "bytes": len(encoded), "units": len(text),
                     "was_units": length // 2, "sites": sites,
                     "source_selector": 3,
                     "source_container_offset": offset, "source_start": start,
                     "source_length": length})
    for key, _approved in OWNER_ROWS:
        if key not in index:
            notes.append(f"{key}: absent from this image")
    return rows, notes


def apply(image: bytes, rows: list[dict]) -> tuple[bytes, dict]:
    out = bytearray(image)
    # The new container is appended 4-byte aligned. Its payload is the rows' texts laid out
    # back to back; the container's declared size is the payload length, and each row's
    # offset in it becomes that row's new decoded start.
    offset = len(out)
    while offset % 4:
        out.append(0x00)
        offset += 1
    payload = bytearray()
    placed: list[dict] = []
    for row in rows:
        new_start = len(payload)
        payload += row["text"].encode("utf-16le")
        placed.append({**row, "new_start": new_start, "new_length": row["bytes"]})
    if len(payload) % 2:
        payload += bytes([0x00, 0x00])
    container_offset = offset
    out += (0).to_bytes(4, "little")
    out += len(payload).to_bytes(4, "little")
    out += bytes(payload)

    # The table's own 64-slot block already reserves this slot: slot 7 sits at file 0x9A9D04,
    # past the seven live pointers, in copied retail data this image never reads. Writing it
    # is the whole table edit - no table move, no literal repoint.
    before_slot = bytes(image[TABLE_SLOT_NEW:TABLE_SLOT_NEW + 4])
    out[TABLE_SLOT_NEW:TABLE_SLOT_NEW + 4] = \
        (ROM_BASE + container_offset).to_bytes(4, "little")

    handle_changes: list[dict] = []
    for row in placed:
        word = DialogueHandle(NEW_SELECTOR, row["new_start"],
                              row["new_length"]).encode()
        for site in row["sites"]:
            before_word = bytes(image[site:site + 4])
            handle = DialogueHandle(row["source_selector"], row["source_start"],
                                    row["source_length"]).encode()
            if int.from_bytes(before_word, "little") != handle:
                raise WorldTournamentBuildError(
                    f"{row['record']}: handle site 0x{site:06X} carries "
                    f"0x{int.from_bytes(before_word, 'little'):08X}, not this record's "
                    f"0x{handle:08X}")
            out[site:site + 4] = word.to_bytes(4, "little")
            handle_changes.append({"record": row["record"], "site": site,
                                   "old": before_word.hex(),
                                   "new": word.to_bytes(4, "little").hex()})
    report = {
        "container_file_offset": container_offset,
        "container_pointer": f"0x{ROM_BASE + container_offset:08X}",
        "container_declared_size": len(payload),
        "table_slot_file_offset": TABLE_SLOT_NEW,
        "table_slot_before": before_slot.hex(),
        "table_slot_after": (ROM_BASE + container_offset).to_bytes(4, "little").hex(),
        "table_slot_selector": NEW_SELECTOR,
        "table_file_offset": int.from_bytes(image[TABLE_LITERAL:TABLE_LITERAL + 4],
                                            "little") - ROM_BASE,
        "rows": placed,
        "handle_changes": handle_changes,
    }
    return bytes(out), report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise WorldTournamentBuildError(
            f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")

    rows, notes = plan(image)
    for row in rows:
        print(f"  {row['record']:<14} {row['was_units']:>3} -> {row['units']:>3} units "
              f"({len(row['sites'])} site(s))  {row['text'][:56]!r}")
    for note in notes:
        print(f"  {note}")
    output, report = apply(image, rows)
    report["input"] = str(source)
    report["input_sha256"] = got
    report["input_bytes"] = len(image)
    report["output_bytes"] = len(output)
    report["rows_placed"] = len(rows)
    report["handle_words_rewritten"] = len(report["handle_changes"])

    target = Path(args.out)
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise WorldTournamentBuildError(f"REFUSED: {error}") from error
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(output)
    if staged.read_bytes() != output:
        raise WorldTournamentBuildError("REFUSED: the staged write does not match the plan")
    staged.replace(target)
    digest = sha256_bytes(output)
    report["output"] = str(target)
    report["output_sha256"] = digest
    Path(args.manifest).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"# wrote {target} {len(output)} bytes sha256 {digest}")
    print(f"# container at file 0x{report['container_file_offset']:X} "
          f"({report['container_declared_size']} bytes), "
          f"{report['handle_words_rewritten']} handle word(s) rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
