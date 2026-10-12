"""Decoder for Buu's Fury dialogue records and their in-stream control codes.

Read-only, and every function takes bytes so a test can drive them without a ROM.

The handle layout is NOT re-derived here: it comes from the project's proven decoder,
`tools.webfoot.handles.unpack_handle`, which the shipped releases already validate and which the
DIALOGUE-VARIABLE-LENGTH-001 ticket documents:

* bits 21-31, 11 bits: the decoded length in halfwords,
* bits 6-20, 15 bits: the decoded start in halfwords,
* bits 0-5, 6 bits: the container selector.

A RECORD is 8 bytes: `+0x00` u16 next-index (the page chain), `+0x02` u8 kind, `+0x03` u8 PORTRAIT OPERAND,
`+0x04` u32 packed handle. The portrait is a RECORD FIELD: there is no portrait code in the text.

The text is a span of a container. The container table's base literal sits at file `0x123CC`, and the copier
indexes it with the selector TIMES FOUR, so an entry lives at `base + 4*selector`.
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.webfoot.handles import unpack_handle  # noqa: E402

ROM_BASE = 0x08000000
RECORD_BYTES = 8
CONTAINER_TABLE_FILE = 0x123CC
KIND_TABLE = 0x080728AC
DIALOGUE_KIND = 5

#: Why the last `span_units` call returned None. A swallowed error once read exactly like an unreadable
#: record, so the reason is kept and printed.
span_error: str | None = None

#: Codes, by equality. The value is what the parser compares against; the entry says what it does.
CODES = {
    0x0000: ("terminator", 0, "written by the copier, never present in a container"),
    0x0008: ("ink", 1, "writes the argument to the strip ink byte (2 and 7 in dialogue)"),
    0x000A: ("line-break", 0, "the fitter returns: the line ends"),
    0x000B: ("page", 0, "sets the end flag; NOT an end of record, 252 records carry units after one"),
    0x0020: ("break-point", 0, "a wrap opportunity; skipped when leading"),
    0x0021: ("box-x", 0, "first-unit-only command, sets the box x to 0x28; also the glyph '!'"),
    0x0023: ("box-x", 0, "first-unit-only command, sets 0x78; also the glyph '#'"),
    0x002D: ("hyphen-join", 0, "skipped, and following spaces are eaten"),
    0x0040: ("box-x", 0, "first-unit-only command, sets 0x50; also the glyph '@'"),
    0x005E: ("pre-reveal", 0, "first-unit-only marker that starts the reveal early"),
}

#: Commands the constructor consumes only as the FIRST unit of a record.
LEADING_ONLY = frozenset({0x0021, 0x0023, 0x0040, 0x005E})

FIXED_ADVANCE_FROM = 0x00FF
NO_INK_FROM = 0x1D9D

#: How each control code renders in readable text, so a fixture can assert the readable part.
RENDER = {0x0020: " ", 0x000A: "\n", 0x000B: "\n"}

LAYOUTS = {
    0: {"record": 0x08071730, "lines_per_page": 4, "wrap_limit": 144, "text_x": 8, "first_y": 15,
        "art": 0x08071758, "portrait_operand": "anything except 7"},
    1: {"record": 0x08071744, "lines_per_page": 2, "wrap_limit": 128, "text_x": 16, "first_y": 30,
        "art": 0x08071A6C, "portrait_operand": "exactly 7"},
}


def word(image: bytes, offset: int) -> int:
    return struct.unpack_from("<I", image, offset)[0]


def is_pointer(value: int, image: bytes) -> bool:
    return ROM_BASE <= value < ROM_BASE + len(image)


def record(image: bytes, site: int) -> dict:
    """Read an 8-byte record word at a GBA address."""
    base = site - ROM_BASE
    return {
        "site": site,
        "next_index": struct.unpack_from("<H", image, base)[0],
        "kind": image[base + 2],
        "portrait_operand": image[base + 3],
        "handle": word(image, base + 4),
    }


def handle_parts(handle: int) -> dict:
    """The proven split, in halfwords and bytes. Delegates to `tools.webfoot.handles.unpack_handle`."""
    selector, start_bytes, length_bytes = unpack_handle(handle)
    return {
        "selector": selector,
        "start_bytes": start_bytes,
        "length_bytes": length_bytes,
        "start_units": start_bytes // 2,
        "length_units": length_bytes // 2,
    }


def container_address(image: bytes, selector: int) -> int | None:
    """The container a selector names. The pool word at `CONTAINER_TABLE_FILE` is the TABLE BASE.

    The copier indexes that base with the selector TIMES FOUR, so multiplying by four again here was a defect
    that sent most records to the wrong container.
    """
    base = word(image, CONTAINER_TABLE_FILE)
    if not is_pointer(base, image):
        return None
    pointer = word(image, base - ROM_BASE + 4 * selector)
    return pointer if is_pointer(pointer, image) else None


def span_units(image: bytes, site: int) -> list[int] | None:
    """The halfwords a record's handle selects, unpacked. None when the image cannot supply them."""
    global span_error
    span_error = None
    entry = record(image, site)
    parts = handle_parts(entry["handle"])
    if parts["length_units"] == 0:
        span_error = "the handle names a zero length, which is not a legal record"
        return None
    container = container_address(image, parts["selector"])
    if container is None:
        span_error = f"selector {parts['selector']} has no container pointer"
        return None
    try:
        from tools.webfoot.formats import webfoot_lz
        data = webfoot_lz.unpack(image, container - ROM_BASE).data
    except Exception as error:                                  # noqa: BLE001
        span_error = f"{type(error).__name__}: {error}"
        return None
    if parts["start_bytes"] + parts["length_bytes"] > len(data):
        span_error = (f"span {parts['start_bytes']}..{parts['start_bytes'] + parts['length_bytes']} runs past "
                      f"the {len(data)}-byte container")
        return None
    return list(struct.unpack_from(f"<{parts['length_units']}H", data, parts["start_bytes"]))


def decode_units(units: list[int]) -> list[dict]:
    """Turn a span into events: control codes with their arguments, and glyph runs.

    A code is recognised by EQUALITY, and `0x08` consumes exactly one argument unit. A leading-only command is
    reported with its position, because the engine's rule is positional and a decoder cannot know intent.
    """
    events: list[dict] = []
    index = 0
    while index < len(units):
        value = units[index]
        if value == 0x0000:
            events.append({"position": index, "kind": "terminator", "value": 0, "argument": None,
                           "leading_only": False, "leading": index == 0, "note": "end of stream"})
            break
        entry = CODES.get(value)
        if entry is None:
            if value >= NO_INK_FROM:
                events.append({"position": index, "kind": "unreached-code", "value": value, "argument": None,
                               "leading_only": False, "leading": index == 0,
                               "note": "at or above 0x1D9D the rasteriser draws nothing"})
            else:
                events.append({"position": index, "kind": "glyph", "value": value, "argument": None,
                               "leading_only": False, "leading": index == 0, "note": ""})
            index += 1
            continue
        name, argument_units, note = entry
        argument = None
        if argument_units and index + argument_units < len(units):
            argument = units[index + 1]
        event = {"position": index, "kind": name, "value": value, "argument": argument,
                 "leading_only": value in LEADING_ONLY, "leading": index == 0, "note": note}
        if value >= FIXED_ADVANCE_FROM:
            event["note"] = "fixed advance class, indexes nothing"
        events.append(event)
        index += 1 + argument_units
    return events


def glyph_run(events: list[dict]) -> str:
    """The glyphs of a decode as a plain string, so a fixture can assert the readable part.

    TRANSITORY: pointed at an image this returns retail text, which must never be committed. A record is cited
    by its site and its length, never by its decoded characters.
    """
    return "".join(RENDER.get(event["value"], chr(event["value"]))
                   for event in events if event["kind"] in ("glyph", "break-point", "line-break", "page"))


def code_histogram(units: list[int]) -> dict:
    """Code occurrences in one span, for the corpus census."""
    counts: dict[int, int] = {}
    leading: set[int] = set()
    for event in decode_units(units):
        if event["kind"] in ("glyph", "unreached-code"):
            continue
        counts[event["value"]] = counts.get(event["value"], 0) + 1
        if event["leading"]:
            leading.add(event["value"])
    return {"codes": counts, "leading": leading}


def record_sites(image: bytes, low: int = 0x0877C5A4, high: int = 0x0879B704) -> list[int]:
    """Every dialogue record word whose site lies in the proven event-resource pool."""
    sites = []
    for site in range(low, high, 4):
        offset = site - ROM_BASE
        if offset + RECORD_BYTES > len(image):
            break
        if image[offset + 2] == DIALOGUE_KIND:
            sites.append(site)
    return sites


def corpus_census(image: bytes, low: int = 0x0877C5A4, high: int = 0x0879B704) -> dict:
    """Code counts over every readable record in the pool, plus span and record totals."""
    codes: dict[int, int] = {}
    leading: dict[int, int] = {}
    records = 0
    units_total = 0
    unreadable = 0
    for site in record_sites(image, low, high):
        units = span_units(image, site)
        if units is None:
            unreadable += 1
            continue
        records += 1
        units_total += len(units)
        histogram = code_histogram(units)
        for value, count in histogram["codes"].items():
            codes[value] = codes.get(value, 0) + count
        for value in histogram["leading"]:
            leading[value] = leading.get(value, 0) + 1
    return {"records": records, "unreadable_records": unreadable, "units": units_total,
            "codes": dict(sorted(codes.items())), "leading_only_counts": dict(sorted(leading.items()))}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Decode a dialogue record and its control codes, read-only")
    parser.add_argument("--image", required=True)
    parser.add_argument("--site", help="a record word's GBA address, for example 0x08780418")
    parser.add_argument("--corpus", action="store_true", help="count code occurrences over the pool")
    parser.add_argument("--events", action="store_true", help="print the event list for one record")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    image = Path(args.image).read_bytes()
    if args.corpus:
        print(json.dumps(corpus_census(image), indent=2))
        return 0
    if not args.site:
        parser.error("--site or --corpus is required")
    site = int(args.site, 0)
    entry = record(image, site)
    parts = handle_parts(entry["handle"])
    units = span_units(image, site)
    index = 1 if entry["portrait_operand"] == 7 else 0
    report = {"record": entry, "handle": parts, "layout_index": index, "layout": LAYOUTS[index],
              "units": len(units) if units else 0}
    if units:
        events = decode_units(units)
        report["event_count"] = len(events)
        report["codes"] = code_histogram(units)["codes"]
        if args.events:
            report["events"] = events
    print(json.dumps(report, indent=2) if args.json else "\n".join(
        [f"record at 0x{site:08X}: kind {entry['kind']} portrait operand {entry['portrait_operand']} "
         f"next {entry['next_index']} handle 0x{entry['handle']:08X}",
         f"handle: selector {parts['selector']} start {parts['start_units']} halfwords "
         f"({parts['start_bytes']} bytes) length {parts['length_units']} halfwords",
         f"layout index {index}: wrap limit {report['layout']['wrap_limit']} "
         f"art 0x{report['layout']['art']:08X}"] +
        ([f"units {len(units)}; codes {report['codes']}"] if units
         else [f"span unreadable: {span_error}"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
