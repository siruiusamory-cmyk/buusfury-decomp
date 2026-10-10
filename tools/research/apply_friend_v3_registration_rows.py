"""Write the owner-authored registration-scene lines and a scanner biography, by append.

WHY THE WRITE APPENDS AND NEVER TRUNCATES. An earlier revision of this tool rebuilt selector
7's container in place, which deleted the container release 2 had appended at file 0x9ABE24
and the string release 2.1 had appended after it. Both are referenced by this image's own
tables, so that revision silently orphaned fifteen World Tournament records. This tool
therefore never removes a byte: it appends the new records and the new string at the end of
the image and repoints only the sites that must move.

THE THREE SITES, AND WHY EACH MOVES OR STAYS.

* `2:60922:140` and `2:60432:98`: both sit inside covering records (`2:57304:4046`,
  `2:57336:4046`, and for the first also `2:60720:2578`). Writing a shorter text into the
  record's own span would leave bytes the covering records read holding something else, so the
  text is COPIED into an appended container and the record's handle word is repointed. The
  covering records are untouched and keep reading exactly what they read before.
* text slot 1083 (the biography release 2.1 placed): the string is copied to the end of the
  image and the slot's single pointer is repointed, for the same reason - the payload it was
  written into belongs to selector 7, and adding records there would put them inside a decoder
  window that already has a declared size.

WHAT IS DELIBERATELY NOT DONE. The image's own size is not rounded up: this image ends at an
offset that is even but not 4-byte aligned, and the existing release-2 container sits at the
same kind of offset. The appended container is placed at the first 4-byte boundary after the
current end, so the up-to-three pad bytes before it lie in a decoder window nothing names, and
no byte of the image is moved.

THE APPROVED WORDING IS TRACKED, NOT PASSED IN. Every row comes from
`tools/research/friend_v3_text_approvals.py`, so a caller cannot write wording the owner did
not approve, and the manifest's copy of the text is provenance rather than authority.
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

from tools.research.friend_v3_text_approvals import (  # noqa: E402
    APPROVED_DIALOGUE_ROWS, APPROVED_TEXT_SLOTS)
from tools.webfoot import compressed_dialogue as cd             # noqa: E402
from tools.webfoot.dialogue_repack import container_pointers    # noqa: E402
from tools.webfoot.formats import webfoot_lz                    # noqa: E402
from tools.webfoot.handles import DialogueHandle                # noqa: E402
from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402

ROM_BASE = 0x08000000
TABLE_SLOT_NEW = 0x9A9D04
NEW_SELECTOR = 7
TEXT_TABLE_START = 0x6BCE8
TERMINATOR = b"\x00\x00"


class RegistrationRowError(ValueError):
    """The write refused rather than placing a byte it could not verify."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def container_stream(image: bytes, selector: int) -> bytes:
    pointer = container_pointers(image)[selector]
    return bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)


def dialogue_sites(image: bytes, selector: int, start: int, length: int) -> list[int]:
    stream = container_stream(image, selector)
    records = cd.dialogue_record_inventory(image, selector, len(stream))
    return [site for record in records
            if record.handle.decoded_start == start
            and record.handle.decoded_length == length
            for site in record.sites]


def read_text_slot(image: bytes, slot: int) -> tuple[int, str]:
    pointer_at = TEXT_TABLE_START + slot * 4
    address = int.from_bytes(image[pointer_at:pointer_at + 4], "little")
    if address < ROM_BASE:
        raise RegistrationRowError(f"text slot {slot} is not a ROM pointer")
    offset = address - ROM_BASE
    end = offset
    while image[end:end + 2] != TERMINATOR:
        end += 2
        if end >= len(image):
            raise RegistrationRowError(
                f"text slot {slot}: no terminator before the end of image")
    return offset, image[offset:end].decode("utf-16le")


def plan(image: bytes) -> tuple[dict, list[dict]]:
    """The biography row, the two dialogue rows, and every site that must be rewritten."""
    bio_edit = APPROVED_TEXT_SLOTS[0]
    bio_offset, bio_text = read_text_slot(image, bio_edit.slot)
    if bio_text != bio_edit.new:
        raise RegistrationRowError(
            f"text slot {bio_edit.slot} holds {bio_text!r}, not the approved wording this "
            "tool is carrying forward; refusing")
    bio = {
        "kind": "text slot", "key": f"text:{bio_edit.slot}", "label": bio_edit.label,
        "text": bio_text, "bytes": len(bio_text.encode("utf-16le")),
        "units": len(bio_text), "sites": [TEXT_TABLE_START + bio_edit.slot * 4],
        "site_kind": "text pointer", "old_address": ROM_BASE + bio_offset,
        "approval": bio_edit.approval,
    }
    rows: list[dict] = []
    for row in APPROVED_DIALOGUE_ROWS:
        stream = container_stream(image, row.selector)
        current = stream[row.start:row.start + row.length].decode("utf-16le")
        if current != row.old:
            raise RegistrationRowError(
                f"{row.key}: the record holds {current!r}, not the text this approval "
                "replaces; refusing rather than correcting")
        prefix = current[:1] if current[:1] in "#!" else ""
        text = prefix + row.new
        sites = dialogue_sites(image, row.selector, row.start, row.length)
        if not sites:
            raise RegistrationRowError(f"{row.key}: no handle word carries this identity")
        encoded = text.encode("utf-16le")
        if len(encoded) > 4094:
            raise RegistrationRowError(
                f"{row.key}: {len(encoded)} bytes, above the 4,094-byte length field")
        rows.append({
            "kind": "dialogue record", "key": row.key, "label": row.label, "text": text,
            "bytes": len(encoded), "units": len(text), "sites": sites,
            "site_kind": "packed handle",
            "old_word": DialogueHandle(row.selector, row.start,
                                       row.length).encode(),
            "selector": row.selector, "old_start": row.start, "old_length": row.length,
            "current": current, "approval": row.approval,
        })
    return bio, rows


def apply(image: bytes, bio: dict, rows: list[dict]) -> tuple[bytes, dict]:
    out = bytearray(image)
    while len(out) % 4:
        out.append(0x00)

    # The container release 2 appended is left exactly where it is; only the slot word that
    # names it is repointed. Its PAYLOAD is carried into the new container as a prefix, because
    # the fifteen World Tournament handles released in release 2 still resolve selector 7 at
    # their own start offsets: a container that declared only the new records would put those
    # offsets past its declared size, and a decoder that honours the declared size would stop
    # reading before the World Tournament text.
    previous_slot = bytes(image[TABLE_SLOT_NEW:TABLE_SLOT_NEW + 4])
    previous_pointer = int.from_bytes(previous_slot, "little")
    previous_container = previous_pointer - ROM_BASE if previous_pointer >= ROM_BASE else None
    prefix_payload = b""
    if previous_container is None or previous_container + 8 > len(image):
        raise RegistrationRowError("slot 7 does not name a container this tool can carry")
    declared = int.from_bytes(image[previous_container + 4:previous_container + 8], "little")
    if declared <= 0 or previous_container + 8 + declared > len(image):
        raise RegistrationRowError(
            "the container slot 7 names does not hold its declared size; refusing")
    prefix_payload = bytes(image[previous_container + 8:previous_container + 8 + declared])

    # The dialogue records go into a new container appended at the end of the image. Its
    # payload is the previous container's own payload first, so the offsets release 2 gave the
    # World Tournament handles still land inside the declared size, then the two new records'
    # texts back to back. The header's declared size is the whole payload.
    container_offset = len(out)
    payload = bytearray(prefix_payload)
    placed: list[dict] = []
    for row in rows:
        new_start = len(payload)
        payload += row["text"].encode("utf-16le")
        placed.append({**row, "new_start": new_start, "new_length": row["bytes"]})
    out += (0).to_bytes(4, "little")
    out += len(payload).to_bytes(4, "little")
    out += bytes(payload)
    out[TABLE_SLOT_NEW:TABLE_SLOT_NEW + 4] = \
        (ROM_BASE + container_offset).to_bytes(4, "little")

    # The biography string is copied to the end of the image and the slot's pointer repointed;
    # its single reference is the slot word itself.
    string_offset = len(out)
    out += bio["text"].encode("utf-16le") + TERMINATOR
    bio_pointer_at = bio["sites"][0]
    out[bio_pointer_at:bio_pointer_at + 4] = (ROM_BASE + string_offset).to_bytes(4, "little")

    changes: list[dict] = []
    for row in placed:
        word = DialogueHandle(NEW_SELECTOR, row["new_start"],
                              row["new_length"]).encode().to_bytes(4, "little")
        for site in row["sites"]:
            before = bytes(image[site:site + 4])
            if int.from_bytes(before, "little") != row["old_word"]:
                raise RegistrationRowError(
                    f"{row['key']}: site 0x{site:06X} carries "
                    f"0x{int.from_bytes(before, 'little'):08X}, not this record's "
                    f"0x{row['old_word']:08X}; refusing")
            out[site:site + 4] = word
            changes.append({"key": row["key"], "site": site, "kind": row["site_kind"],
                            "old": before.hex(), "new": word.hex()})
    old_string_pointer = bytes(image[bio_pointer_at:bio_pointer_at + 4])
    changes.append({"key": bio["key"], "site": bio_pointer_at, "kind": bio["site_kind"],
                    "old": old_string_pointer.hex(),
                    "new": (ROM_BASE + string_offset).to_bytes(4, "little").hex()})
    report = {
        "container_file_offset": container_offset,
        "container_pointer": f"0x{ROM_BASE + container_offset:08X}",
        "container_declared_size": len(payload),
        "container_payload_bytes": len(payload),
        "table_slot_file_offset": TABLE_SLOT_NEW,
        "table_slot_selector": NEW_SELECTOR,
        "table_slot_before": previous_slot.hex(),
        "table_slot_after": (ROM_BASE + container_offset).to_bytes(4, "little").hex(),
        "previous_container_file_offset": previous_container,
        "carried_prefix_bytes": len(prefix_payload),
        "string_file_offset": string_offset,
        "string_pointer": f"0x{ROM_BASE + string_offset:08X}",
        "old_string_file_offset": bio["old_address"] - ROM_BASE,
        "rows": [{k: v for k, v in row.items() if k != "old_word"} for row in placed],
        "site_changes": changes,
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
        raise RegistrationRowError(
            f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")

    bio, rows = plan(image)
    for row in rows:
        print(f"  {row['key']:<14} {row['units']:>3} units ({len(row['sites'])} site(s))  "
              f"{row['text'][:58]!r}")
    print(f"  {bio['key']:<14} {bio['units']:>3} units (1 site)  {bio['text'][:58]!r}")
    output, report = apply(image, bio, rows)
    report.update({"input": str(source), "input_sha256": got, "input_bytes": len(image),
                   "output_bytes": len(output), "rows_placed": len(rows) + 1,
                   "sites_rewritten": len(report["site_changes"])})
    target = Path(args.out)
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise RegistrationRowError(f"REFUSED: {error}") from error
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(output)
    if staged.read_bytes() != output:
        raise RegistrationRowError("REFUSED: the staged write does not match the plan")
    staged.replace(target)
    report["output"] = str(target)
    report["output_sha256"] = sha256_bytes(output)
    # Read the finished image back and prove, in the tool that wrote it, that the appended
    # container is what slot 7 names, that every repointed handle resolves into it, and that
    # the biography slot reads the wording. The earlier revision of this tool deleted the
    # container release 2 had appended, and a writer that checks only its own intent cannot
    # notice that.
    written = Path(args.out).read_bytes()
    wt_pointer = int.from_bytes(written[TABLE_SLOT_NEW:TABLE_SLOT_NEW + 4], "little")
    if wt_pointer - ROM_BASE != report["container_file_offset"]:
        raise RegistrationRowError("readback: slot 7 does not name the appended container")
    for row in report["rows"]:
        for site in row["sites"]:
            got = DialogueHandle.decode(int.from_bytes(written[site:site + 4], "little"))
            if (got.selector, got.decoded_start, got.decoded_length) != \
                    (NEW_SELECTOR, row["new_start"], row["new_length"]):
                raise RegistrationRowError(
                    f"readback: {row['key']} site 0x{site:06X} does not resolve into the "
                    "appended container")
    bio_slot_at = bio["sites"][0]
    bio_slot = int.from_bytes(written[bio_slot_at:bio_slot_at + 4], "little")
    offset = bio_slot - ROM_BASE
    end = offset
    while written[end:end + 2] != TERMINATOR:
        end += 2
    if written[offset:end].decode("utf-16le") != bio["text"]:
        raise RegistrationRowError("readback: the biography slot does not read its wording")
    report["readback"] = {
        "appended_container": f"0x{wt_pointer:08X}",
        "biography_pointer": f"0x{bio_slot:08X}",
        "previous_container_pointer_kept": report["table_slot_before"],
    }
    # The carried prefix must still read as the World Tournament texts: the first row release 2
    # placed begins at offset 0 with the Uub line.
    carried = bytes(written[report["container_file_offset"] + 8:
                            report["container_file_offset"] + 8 + 100]).decode("utf-16le")
    if "Hey sis" not in carried:
        raise RegistrationRowError(
            f"readback: the carried prefix does not hold the release-2 wording ({carried!r})")
    report["readback"]["carried_prefix_head"] = carried[:40]
    Path(args.manifest).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"# wrote {target} {len(output)} bytes sha256 {report['output_sha256']}")
    print(f"# container at file 0x{report['container_file_offset']:X} "
          f"({report['container_declared_size']} bytes); string at "
          f"0x{report['string_file_offset']:X}; {report['sites_rewritten']} site(s) rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
