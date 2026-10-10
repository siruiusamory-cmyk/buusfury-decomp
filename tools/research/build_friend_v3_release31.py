"""Release 3.1: rename retail Videl's actor to Lazuli.

WHAT IS RENAMED, AND HOW THE TARGET IS FIXED. The owner's rule is that an occurrence of "Videl" is
retail Videl - and so becomes "Lazuli" - only where the canonical ROM says "Videl" at the same
place. Where the canonical ROM says "Goten", the word belongs to the earlier pass's Goten-turned-
Videl actor and is left exactly as it is. Where there is no retail counterpart to compare against,
nothing is written. Without that test the rename would merge two different characters that display
the same name in this image: measured, retail's appearance records 65 to 70 (Goten's art) display
"Videl" and records 214 and 215 (retail Videl) also display "Videl".

WHY NOTHING IS WRITTEN IN PLACE. "Lazuli" is one unit longer than "Videl", so no record can absorb
it: a record's span is fixed by its handle and by the text-table slot's allocation. Two routes are
used instead, both proven in this ticket:

* dialogue records are COPIED into a container on selector 7 - the one release 2 already appended
  and proved at runtime - whose payload is that container's own payload carried forward as a
  prefix, so every handle release 2 and 2.1 wrote still lands inside the declared size. No byte of
  any of the seven retail containers moves.
* text-table slots 138, 172 and 1066 are appended past the end of the image and their single table
  word is repointed, guarded by counting every word-aligned reference to the old pointer.

REFUSALS. The input digest, the retail-side test for every record, the handle word at every site,
the one-reference guard on each relocated slot, and a readback of the staged file. Nothing is
written on a disagreement.
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
    APPROVED_CHARACTER_RENAMES, APPROVED_RELEASES)
from tools.webfoot import compressed_dialogue as cd  # noqa: E402
from tools.webfoot.dialogue_repack import container_pointers, text_of  # noqa: E402
from tools.webfoot.formats import webfoot_lz  # noqa: E402
from tools.webfoot.handles import DialogueHandle  # noqa: E402
from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402

RENAME = next(r for r in APPROVED_CHARACTER_RENAMES if r.old == "Videl")
RELEASE = next(r for r in APPROVED_RELEASES if r.name == "release-3.1")

ROM_BASE = 0x08000000
TABLE_LITERAL = 0x123CC
TEXT_TABLE_START = 0x6BCE8
CONTAINERS = 8
NEW_SELECTOR = 7                      # the slot release 2 appended its container to, proven at runtime
TABLE_SLOT_NEW = 0x9A9D04             # slot 7, the only appended selector this image uses
OLD_NAME = "Videl"
NEW_NAME = "Lazuli"
RELOCATED_SLOTS = (138, 172, 1066)


class RenameError(ValueError):
    """The rename refused rather than writing a byte it could not verify."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def slot_text(image: bytes, slot: int) -> tuple[str, int]:
    at = TEXT_TABLE_START + slot * 4
    pointer = int.from_bytes(image[at:at + 4], "little")
    if pointer < ROM_BASE or pointer - ROM_BASE >= len(image):
        return "", 0
    offset = pointer - ROM_BASE
    raw = image[offset:offset + 600]
    end = 0
    while end + 1 < len(raw) and raw[end:end + 2] != b"\x00\x00":
        end += 2
    return raw[:end].decode("utf-16le", "replace"), offset


def streams(image: bytes) -> dict[int, bytes]:
    """Each container's decoded payload, by selector. The canonical ROM has seven selectors and
    this image has eight, so a selector the image does not carry is simply absent."""
    out = {}
    pointers = container_pointers(image)
    for selector in range(CONTAINERS):
        pointer = pointers.get(selector, 0) if isinstance(pointers, dict) else pointers[selector]
        if pointer < ROM_BASE:
            continue
        out[selector] = bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--retail", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise RenameError(f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")
    retail = Path(args.retail).read_bytes()

    out = bytearray(image)
    document: dict = {"input": str(source), "input_sha256": got, "input_bytes": len(image),
                      "old_name": OLD_NAME, "new_name": NEW_NAME, "rows": [], "slots": [],
                      "left": [], "listed": [], "output_bytes": None}

    # --- dialogue records, by the retail-side test ---------------------------------------
    friend_streams = streams(image)
    retail_streams = streams(retail)
    rows = []
    for selector, stream in sorted(friend_streams.items()):
        for record in cd.dialogue_record_inventory(image, selector, len(stream)):
            start, length = record.handle.decoded_start, record.handle.decoded_length
            if start + length > len(stream):
                continue
            current = text_of(stream, start, length)
            if OLD_NAME not in current:
                continue
            other = retail_streams.get(selector, b"")
            counterpart = (other[start:start + length].decode("utf-16le", "replace")
                           if start + length <= len(other) else None)
            if counterpart is None or OLD_NAME not in counterpart:
                document["left"].append({"handle": f"{selector}:{start}:{length}",
                                         "friend": current[:70],
                                         "retail": (counterpart or "")[:70]})
                continue
            text = current.replace(OLD_NAME, NEW_NAME)
            encoded = text.encode("utf-16le")
            if len(encoded) > 4094:
                raise RenameError(f"{selector}:{start}:{length}: {len(encoded)} bytes, above the "
                                  "4,094-byte length field")
            rows.append({"record": f"{selector}:{start}:{length}", "current": current, "text": text,
                         "bytes": len(encoded), "units": len(text), "was_units": length // 2,
                         "sites": list(record.sites), "source_selector": selector,
                         "source_container_offset": 0, "source_start": start,
                         "source_length": length})

    if not rows:
        raise RenameError("REFUSED: no record passed the retail-side test")

    # --- carry slot 7's payload forward, then append the renamed records ------------------
    #
    # WHY THIS CONTAINER AND NOT A SPARE SLOT. The words after the seven live selectors are not
    # free space: measured, retail's slot 7 holds an IWRAM pointer and slots 8 to 15 hold more of
    # them, so the block past the live entries belongs to something else. Selector 7 is the one
    # slot this image already uses for an appended container, proven at runtime in release 2, and
    # release 2.1 proved the carry-forward: the new container's payload begins with the OLD
    # container's payload, so every handle release 2 wrote still lands inside the declared size.
    slot_word = int.from_bytes(image[TABLE_SLOT_NEW:TABLE_SLOT_NEW + 4], "little")
    if slot_word < ROM_BASE:
        raise RenameError(f"REFUSED: table slot {NEW_SELECTOR} does not name a container")
    previous = slot_word - ROM_BASE
    if previous + 8 > len(image):
        raise RenameError("REFUSED: the container slot 7 names lies outside the image")
    declared = int.from_bytes(image[previous + 4:previous + 8], "little")
    if declared <= 0 or previous + 8 + declared > len(image):
        raise RenameError("REFUSED: the container slot 7 names does not hold its declared size")
    prefix_payload = bytes(image[previous + 8:previous + 8 + declared])

    offset = len(out)
    while offset % 4:
        out.append(0x00)
        offset += 1
    payload = bytearray(prefix_payload)
    placed = []
    for row in rows:
        new_start = len(payload)
        payload += row["text"].encode("utf-16le")
        placed.append({**row, "new_start": new_start, "new_length": row["bytes"]})
    if len(payload) % 2:
        payload += bytes([0x00, 0x00])
    if len(payload) > 65534:
        raise RenameError(f"REFUSED: the carried payload would be {len(payload)} bytes, above the "
                          "container ceiling")
    out += (0).to_bytes(4, "little") + len(payload).to_bytes(4, "little") + bytes(payload)

    slot_before = bytes(image[TABLE_SLOT_NEW:TABLE_SLOT_NEW + 4])
    out[TABLE_SLOT_NEW:TABLE_SLOT_NEW + 4] = (ROM_BASE + offset).to_bytes(4, "little")

    handle_changes = []
    for row in placed:
        word = DialogueHandle(NEW_SELECTOR, row["new_start"], row["new_length"]).encode()
        for site in row["sites"]:
            before_word = bytes(image[site:site + 4])
            handle = DialogueHandle(row["source_selector"], row["source_start"],
                                    row["source_length"]).encode()
            if int.from_bytes(before_word, "little") != handle:
                raise RenameError(f"{row['record']}: site 0x{site:06X} carries "
                                  f"0x{int.from_bytes(before_word, 'little'):08X}, not this "
                                  f"record's 0x{handle:08X}")
            out[site:site + 4] = word.to_bytes(4, "little")
            handle_changes.append({"record": row["record"], "site": site,
                                   "old": before_word.hex(), "new": word.to_bytes(4, "little").hex()})

    # --- the three name slots, relocated -------------------------------------------------
    for slot in RELOCATED_SLOTS:
        text, old_offset = slot_text(image, slot)
        if text != OLD_NAME:
            raise RenameError(f"REFUSED: slot {slot} reads {text!r}, not {OLD_NAME!r}")
        at = len(out)
        while at % 4:
            out.append(0x00)
            at += 1
        encoded = (NEW_NAME + "\x00").encode("utf-16le")
        out += encoded
        word_at = TEXT_TABLE_START + slot * 4
        before_word = bytes(image[word_at:word_at + 4])
        needle = before_word
        references = sum(1 for index in range(0, len(image) - 4, 4)
                         if image[index:index + 4] == needle)
        if references != 1:
            raise RenameError(f"REFUSED: slot {slot}'s pointer 0x{int.from_bytes(before_word, 'little'):08X} "
                              f"has {references} word-aligned references, so it cannot be repointed")
        out[word_at:word_at + 4] = (ROM_BASE + at).to_bytes(4, "little")
        document["slots"].append({"slot": slot, "was": text, "now": NEW_NAME,
                                  "old_file_offset": old_offset, "new_file_offset": at,
                                  "replaced_word_at": word_at,
                                  "before": before_word.hex(),
                                  "after": (ROM_BASE + at).to_bytes(4, "little").hex()})

    document["rows"] = placed
    document["handle_changes"] = handle_changes
    document["container_file_offset"] = offset
    document["container_pointer"] = f"0x{ROM_BASE + offset:08X}"
    document["container_declared_size"] = len(payload)
    document["table_slot_file_offset"] = TABLE_SLOT_NEW
    document["table_slot_before"] = slot_before.hex()
    document["table_slot_after"] = (ROM_BASE + offset).to_bytes(4, "little").hex()

    target = Path(args.out)
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise RenameError(f"REFUSED: {error}") from error
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(out)
    if staged.read_bytes() != bytes(out):
        raise RenameError("REFUSED: the staged write does not match the plan")
    staged.replace(target)
    written = target.read_bytes()

    # Readback: every renamed record reads the new name, every record the test left still reads the
    # old one, every record that ALREADY lived in the carried container still reads exactly what it
    # read before, and each relocated slot reads the new name through its own table word. The
    # written containers are unpacked ONCE: unpacking them inside the loop made this quadratic.
    renamed = {row["record"] for row in placed}
    carried = {f"{s}:{start}:{length}"
               for s, stream in friend_streams.items() if s == NEW_SELECTOR
               for start, length in [(record.handle.decoded_start, record.handle.decoded_length)
                                     for record in cd.dialogue_record_inventory(image, s,
                                                                               len(stream))]
               if start + length <= len(stream)}
    written_streams = streams(written)
    problems = 0
    for selector, stream in sorted(friend_streams.items()):
        new_stream = written_streams.get(selector, b"")
        for record in cd.dialogue_record_inventory(image, selector, len(stream)):
            start, length = record.handle.decoded_start, record.handle.decoded_length
            key = f"{selector}:{start}:{length}"
            before = text_of(stream, start, length)
            if key in renamed:
                continue
            if key in carried:
                # These handles were rewritten to selector 7 by an earlier release. Their text now
                # lives in the carried prefix, so it is compared there.
                after = text_of(written_streams[NEW_SELECTOR], start, length)
            else:
                after = (text_of(new_stream, start, length)
                         if start + length <= len(new_stream) else "")
            if before != after:
                problems += 1
                print(f"FAIL {key}: a record the test left alone changed\n"
                      f"     before {before[:60]!r}\n     after  {after[:60]!r}")
    for row in placed:
        new_stream = written_streams[NEW_SELECTOR]
        after = text_of(new_stream, row["new_start"], row["new_length"])
        if NEW_NAME not in after or OLD_NAME in after:
            problems += 1
            print(f"FAIL {row['record']}: does not read the new name")
    for entry in document["slots"]:
        text, _offset = slot_text(written, entry["slot"])
        if text != NEW_NAME:
            problems += 1
            print(f"FAIL slot {entry['slot']}: reads {text!r}")
    if problems:
        raise RenameError(f"REFUSED: {problems} readback problem(s)")

    document["output"] = str(target)
    document["output_sha256"] = sha256_bytes(written)
    document["output_bytes"] = len(written)
    Path(args.manifest).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"# renamed {len(placed)} record(s) into container {NEW_SELECTOR} at "
          f"0x{ROM_BASE + offset:08X} ({len(payload)} bytes), "
          f"{len(handle_changes)} handle word(s) rewritten")
    print(f"# relocated {len(document['slots'])} name slot(s): "
          f"{[entry['slot'] for entry in document['slots']]}")
    print(f"# left for the owner: {len(document['left'])} record(s) with no retail Videl to compare")
    if document["output_sha256"] != RELEASE.output_sha256:
        raise RenameError(
            f"REFUSED: the chain produced {document['output_sha256']} and release 3.1 is "
            f"{RELEASE.output_sha256}. A byte moved somewhere.")
    print(f"# wrote {target} {len(written)} bytes sha256 {document['output_sha256']} matches the "
          "frozen release identity")
    return 0


def pointers_name(image: bytes, pointer: int) -> bool:
    """Whether any word-aligned word in the image already equals this container pointer."""
    if pointer < ROM_BASE:
        return False
    needle = pointer.to_bytes(4, "little")
    return any(image[index:index + 4] == needle for index in range(0, len(image) - 4, 4))


if __name__ == "__main__":
    sys.exit(main())
