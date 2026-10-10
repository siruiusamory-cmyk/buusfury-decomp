"""Plan the friend-image dialogue containers so every record start fits its ceiling.

WHY A PLAN, AND NOT A WRITE. A record's home is a 6-bit container selector plus a 15-bit
start in halfwords, so a container may not hold a record whose start passes 65,534 decoded
bytes. Today's containers sit just under their own decoder ceiling and hold records only up
to that start, so nothing is displaced yet. Two changes need room that does not exist in
the record's own span: a line that grows its record, and a pad a shared reader will not let
the rebuild drop. This module measures the cheapest way to give those records a home:

  * a record whose padding is read by NO other record is repaired IN PLACE, by writing its
    target text into its own span and filling the tail with space units. No byte moves, no
    selector changes, no handle word changes.
  * a record whose padding sits inside bytes another record also reads cannot be trimmed
    where it is. It is COPIED into a new container with its target text, and its handle
    words are rewritten to name the new home. The bytes it left behind stay exactly as they
    were, so every other record's view of them is unchanged.

THE NEW CONTAINER USES A SLOT THE IMAGE ALREADY RESERVES. The table the engine reads is at
file `0x9A9CE8` (named by the one word at file `0x123CC`), seven slots live and the rest
228 bytes of copied retail data that no word in either image names, ending exactly at
`0x9A9DE8`. Slots 7 and above are therefore free, and writing one is a data edit: no table
move, no literal repoint, and the table cannot grow at the retail offset because slot 7
there is the first word of a live structure.

The plan refuses rather than guesses: a record whose target text does not fit the length
field, or whose moved set does not fit the selector range, is reported and no write is
planned. Nothing here writes an image; `plan()` returns the arithmetic and the tool prints
it.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot import compressed_dialogue as cd
from tools.webfoot.dialogue_repack import (container_pointers, live_table,
                                           target_text, text_of)
from tools.webfoot.formats import webfoot_lz
from tools.webfoot.handles import (HANDLE_LENGTH_MAX_BYTES,
                                   HANDLE_START_MAX_BYTES)

ROM_BASE = 0x08000000
#: The selectors the engine resolves to a live dialogue container today.
DIALOGUE_SELECTORS = (0, 1, 2, 3, 4, 5)
#: The first slot the derivative's table reserves and no live container uses.
FIRST_FREE_SELECTOR = 7
#: The table's own extent: 64 slots, ending where the "Tiencha" text begins.
TABLE_SLOTS = 64


class SplitPlanError(ValueError):
    """The plan refused rather than proposing a layout it cannot stand behind."""


def retail_streams(retail: bytes | None) -> dict[int, bytes]:
    """Each retail container's decoded bytes, by selector, for the pad reference."""
    if retail is None:
        return {}
    streams: dict[int, bytes] = {}
    for selector, pointer in container_pointers(retail).items():
        container = webfoot_lz.unpack(retail, pointer - ROM_BASE)
        if container.declared_size:
            streams[selector] = bytes(container.data)
    return streams


def reference_text(reference: bytes | None, record) -> str | None:
    """The retail text at the same decoded span, or None when there is no reference."""
    if reference is None:
        return None
    end = record.handle.decoded_end
    if end > len(reference):
        return None
    return reference[record.handle.decoded_start:end].decode("utf-16le")


def plan(image: bytes, retail: bytes | None = None,
         grown: dict[str, str] | None = None) -> dict:
    """The container arithmetic: what is repaired in place, what moves, and where.

    ``grown`` maps a record key (``selector:start:length``) to the wording it must read
    afterwards. A grown row whose wording is longer than its own span cannot be written
    where it is and joins the move set; a grown row that fits stays where it is. Rows
    already long enough are reported and not planned, which is the same refusal
    ``dialogue_repack.plan_group`` makes rather than truncating an owner's line.
    """
    table = live_table(image)
    if table + TABLE_SLOTS * 4 > len(image):
        raise SplitPlanError(f"the table at file 0x{table:X} does not fit this image")
    pointers = container_pointers(image)
    references = retail_streams(retail)
    out = {"table_file_offset": table, "selectors": [], "in_place": [], "move": [],
           "grown": [], "grown_blocked": [], "move_bytes": 0, "move_records": 0,
           "move_handle_sites": 0}
    inside = collections.Counter()
    outside = collections.Counter()

    for selector in DIALOGUE_SELECTORS:
        if selector not in pointers:
            continue
        container = webfoot_lz.unpack(image, pointers[selector] - ROM_BASE)
        stream = bytes(container.data)
        records = cd.dialogue_record_inventory(image, selector, len(stream))
        spans = [(r.handle.decoded_start, r.handle.decoded_end) for r in records]
        row = {"selector": selector, "decoded_size": len(stream),
               "records": len(records),
               "sites": sum(len(r.sites) for r in records),
               "in_place": 0, "shared_tail": 0, "trimmed_units": 0,
               "over_ceiling": sum(1 for r in records
                                   if r.handle.decoded_start > HANDLE_START_MAX_BYTES)}
        for record in records:
            start, end = record.handle.decoded_start, record.handle.decoded_end
            text = text_of(stream, start, end - start)
            body = target_text(text, reference_text(references.get(selector), record))
            body = body.rstrip(" ")
            if len(body) == len(text):
                continue
            row["trimmed_units"] += len(text) - len(body)
            new_length = len(body) * 2
            if new_length > HANDLE_LENGTH_MAX_BYTES:
                raise SplitPlanError(
                    f"selector {selector} record {start}: target text is {new_length} "
                    f"bytes, above the {HANDLE_LENGTH_MAX_BYTES}-byte length field")
            # A trim is invisible only when nothing else reads the units it drops.
            shared = any(other_start < end and start < other_end
                         and not (other_start == start and other_end == end)
                         and min(other_end, end) > max(other_start, start + new_length)
                         for other_start, other_end in spans)
            entry = {"record": f"{selector}:{start}:{end - start}",
                     "selector": selector, "decoded_start": start,
                     "decoded_length": end - start, "target_units": len(body),
                     "target_bytes": new_length, "sites": list(record.sites)}
            if shared:
                row["shared_tail"] += 1
                out["move"].append(entry)
                out["move_bytes"] += new_length
                out["move_records"] += 1
                out["move_handle_sites"] += len(record.sites)
            else:
                row["in_place"] += 1
                out["in_place"].append(entry)
        out["selectors"].append(row)

    # Which other selectors already carry record-shaped words, and whether those words sit
    # inside a dialogue payload (never parsed) or elsewhere in the image (a real risk if a
    # container is put on that selector).
    decoded_by_selector = {row["selector"]: row["decoded_size"]
                           for row in out["selectors"]}
    payloads = [(pointers[s] - ROM_BASE,
                 pointers[s] - ROM_BASE + 8 + decoded_by_selector[s])
                for s in DIALOGUE_SELECTORS if s in pointers]
    pattern = bytes([cd.TEXT_RECORD_ZERO_VALUE, cd.TEXT_RECORD_KIND])
    position = image.find(pattern)
    while position != -1:
        record = position - cd.TEXT_RECORD_ZERO_OFFSET
        if record >= 0 and record % 4 == 0 and record + cd.TEXT_RECORD_SIZE <= len(image):
            word = int.from_bytes(
                image[record + cd.TEXT_RECORD_HANDLE_OFFSET:
                      record + cd.TEXT_RECORD_HANDLE_OFFSET + 4], "little")
            selector = word & 0x3F
            if selector > 6:
                if any(lo <= record < hi for lo, hi in payloads):
                    inside[selector] += 1
                else:
                    outside[selector] += 1
        position = image.find(pattern, position + 1)
    out["record_words_above_6"] = {"inside_payloads": dict(inside),
                                   "elsewhere": dict(outside)}
    for key, wording in (grown or {}).items():
        selector, start, length = (int(part) for part in key.split(":"))
        stream = bytes(webfoot_lz.unpack(image, pointers[selector] - ROM_BASE).data)
        current = text_of(stream, start, length)
        entry = {"record": key, "current_units": length // 2,
                 "approved_units": len(wording), "current": current, "approved": wording}
        if len(wording) * 2 <= length:
            entry["route"] = "in place, with the handle length reduced"
            out["grown"].append(entry)
            continue
        records = cd.dialogue_record_inventory(image, selector, len(stream))
        sites = [site for record in records
                 if record.handle.decoded_start == start
                 and record.handle.decoded_length == length
                 for site in record.sites]
        if not sites:
            raise SplitPlanError(f"{key}: no record carries this identity, so it cannot move")
        entry["route"] = "moved to a new container"
        entry["sites"] = sites
        out["grown"].append(entry)
        out["move"].append({"record": key, "selector": selector,
                            "decoded_start": start, "decoded_length": length,
                            "target_units": len(wording), "target_bytes": len(wording) * 2,
                            "sites": sites})
        out["move_bytes"] += len(wording) * 2
        out["move_records"] += 1
        out["move_handle_sites"] += len(sites)

    slots_needed = 1 if out["move_bytes"] else 0
    out["new_containers_needed"] = slots_needed
    out["first_free_selector"] = FIRST_FREE_SELECTOR
    out["move_fits_one_container"] = out["move_bytes"] <= 65536
    if out["move_bytes"] and not out["move_fits_one_container"]:
        raise SplitPlanError(
            f"{out['move_bytes']} bytes of moved text do not fit one 65,536-byte "
            "container; the plan needs a second selector and a stated shard rule")
    if out["move_bytes"]:
        largest = max(entry["target_bytes"] for entry in out["move"])
        if largest > HANDLE_LENGTH_MAX_BYTES:
            raise SplitPlanError(
                f"the largest moved text is {largest} bytes, above the "
                f"{HANDLE_LENGTH_MAX_BYTES}-byte length field")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--retail")
    parser.add_argument("--json")
    parser.add_argument("--grown-json",
                        help="a JSON object of record key -> the wording it must read; "
                             "each row is planned by measurement, never on trust")
    args = parser.parse_args()

    image = Path(args.image).read_bytes()
    retail = Path(args.retail).read_bytes() if args.retail else None
    grown = json.loads(Path(args.grown_json).read_text(encoding="utf-8")) \
        if args.grown_json else None
    report = plan(image, retail, grown)
    print(json.dumps(report, indent=2))
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
