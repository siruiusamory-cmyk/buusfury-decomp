"""Census the UTF-16 source-unit namespace the spoken-dialogue decoder sees.

Ticket DIALOGUE-EXPANSION-TOKEN-DESIGN-001, section 1. Read-only: nothing here
writes to the ROM, and the canonical digest is checked before the image is read.

What is counted, and why it is counted this way
-----------------------------------------------

The corpus is the SEVEN pointer-reachable compressed-dialogue containers named by
the table at file 0x007B5B64. That is the same table the atlas producer uses
(`tools/webfoot/atlas_producers/scan.py`, COMPRESSED_TEXT_TABLE and
COMPRESSED_TEXT_COUNT = 7, cited there to
docs/research/BUU_MAP_EVENT_REFERENCES.md:247) and the same one the authoring
target uses (`tools/webfoot/compressed_dialogue.py`, table_offset 0x7B5B64).

Three unit sets are counted, because they answer three different questions:

* REACHABLE UNITS (primary). The union of every span a record handle can name,
  de-duplicated by decoded offset. A stored unit exists once; several record
  words pointing into the same span do not make it two units. This is the set a
  token would live in.
* RECORD-SPAN OCCURRENCES (secondary). Every unit of every record span, so the
  duplication between handles is visible and not hidden by the union.
* WHOLE-CONTAINER. Every halfword of every decoded container, including bytes no
  handle currently names.

The record inventory comes from `dialogue_record_inventory`, the shipped
structural query: a 4-byte-aligned word whose +0x01 is zero and whose +0x02 is
kind 0x05, carrying a handle at +0x04 that decodes to a legal span. The engine's
own dispatch loop at 0x08012552 branches on byte +0x02 and only kind 0x05 reaches
the compressed-dialogue consumer at 0x08012230, which loads [record+0x04] as the
handle (TEXT-HANDLE-001, TEXT-HANDLE-002, both runtime-proven).

Payload question. `ends_a_span` and `starts_a_span` are adjacency counts, not
semantics. The engine-side answer to "does this value carry a payload" comes from
the branch table in `tools/research/dialogue_control_codes.py`, whose entries cite
the instruction that tests the value.

Glyph question. Each value carries the font record it resolves to, read from the
two-level table the rasteriser reads: `font_base = u32[0x0806EE6C]` (measured at
runtime; decoded by `tools/research/dialogue_font_probe.py`), `index =
u16[font_base + c*2]`, `width = u16[font_base + index*2]`. An index of zero is the
engine's own "no glyph" answer.

Usage
-----

    python -m tools.research.dialogue_unit_census --rom <canonical.gba> \
        --json build/dialogue-expansion-001/unit-census.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.research.dialogue_control_codes import classify  # noqa: E402
from tools.research.dialogue_font_probe import glyph, read_u16, read_u32  # noqa: E402
from tools.webfoot.binary import GBA_ROM_BASE  # noqa: E402
from tools.webfoot.compressed_dialogue import dialogue_record_inventory  # noqa: E402
from tools.webfoot.formats.webfoot_lz import unpack  # noqa: E402

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

#: The pointer table that defines the compressed-text region: seven consecutive
#: words, each a ROM address of one container.
CONTAINER_TABLE_FILE_OFFSET = 0x007B5B64
CONTAINER_TABLE_PROBE = 8

#: The font holder whose u32 is the base of the code -> record-index table.
FONT_HOLDER_ROM_ADDRESS = 0x0806EE6C

#: The dialogue font descriptor (docs/research/DIALOGUE_RENDER_PATH.md records it
#: as the source of the glyph blob); dumped so the map's extent is measured rather
#: than assumed.
FONT_DESCRIPTOR_ROM_ADDRESS = 0x08071720


def containers(image: bytes) -> list[dict]:
    found = []
    for selector in range(CONTAINER_TABLE_PROBE):
        slot = CONTAINER_TABLE_FILE_OFFSET + selector * 4
        word = int.from_bytes(image[slot:slot + 4], "little")
        if word < GBA_ROM_BASE or word - GBA_ROM_BASE >= len(image):
            continue
        container = unpack(image, word - GBA_ROM_BASE)
        if not container.declared_size:
            continue
        found.append({"selector": selector, "rom_address": word,
                      "file_offset": word - GBA_ROM_BASE, "container": container})
    return found


def record_spans(image: bytes, selector: int, decoded: bytes):
    """Spans the engine can be pointed at, as (start, length) in bytes."""
    spans = set()
    for record in dialogue_record_inventory(image, selector, len(decoded)):
        handle = record.handle
        spans.add((handle.decoded_start, handle.decoded_length))
    return sorted(spans)


def units_at(data: bytes, start: int, length: int):
    """The halfwords of one span, clipped to the decoded stream."""
    end = min(start + length, len(data))
    return [(offset, data[offset] | (data[offset + 1] << 8))
            for offset in range(start, end - 1, 2)]


def second_store_census(image: bytes) -> dict | None:
    """The other UTF-16 string store, for the collision proof.

    The seven spoken containers are not the only text in the image: the
    menu/quest/item pool is declared by the shipped profile (text_strings in
    tools/webfoot/data/roms.yaml: pool_address 0x0805792C, pool_size 82,874,
    utf16le_nul_terminated, 1,534 pointers) and rendered by a different path
    (measurer 0x0803FFE8, emitter 0x0802BFBC). A token window that another store
    already uses would be a collision the dialogue census cannot see, so the same
    question is asked of this pool.
    """
    from tools.webfoot.profile import RomProfileCatalog

    catalog = RomProfileCatalog.load(ROOT / "tools" / "webfoot" / "data" / "roms.yaml")
    profile = next((item for item in catalog.profiles
                    if (item.sha256 or "").lower() == CANONICAL_SHA256), None)
    if profile is None or profile.text_strings is None:
        return None
    table = profile.text_strings
    start = table.pool_address.to_file_offset(len(image))
    pool = image[start:start + table.pool_size]
    counts = Counter(pool[offset] | (pool[offset + 1] << 8)
                     for offset in range(0, len(pool) - 1, 2))
    above = {value: count for value, count in counts.items() if value >= 0x100}
    return {
        "profile_id": profile.id,
        "pool_address": f"0x{table.pool_address.raw:08X}",
        "pool_size": table.pool_size,
        "declared_strings": table.count,
        "units": sum(counts.values()),
        "distinct_values": len(counts),
        "highest_value": f"0x{max(counts):04X}",
        "values_at_or_above_0x0100": {f"0x{value:04X}": count
                                      for value, count in sorted(above.items())},
    }


def census(rom: Path) -> dict:
    digest = hashlib.sha256(rom.read_bytes()).hexdigest()
    if digest != CANONICAL_SHA256:
        raise SystemExit(f"not the canonical image: {digest}")
    image = rom.read_bytes()
    font_base = read_u32(image, FONT_HOLDER_ROM_ADDRESS)

    reachable: Counter = Counter()
    occurrences: Counter = Counter()
    whole: Counter = Counter()
    starts: Counter = Counter()
    ends: Counter = Counter()
    successor: dict[int, Counter] = {}
    per_selector = []

    for entry in containers(image):
        selector = entry["selector"]
        data = entry["container"].data
        spans = record_spans(image, selector, data)
        covered: set[int] = set()
        followed_by_nul = 0
        interior_nul = 0
        for start, length in spans:
            span_units = units_at(data, start, length)
            occurrences.update(value for _offset, value in span_units)
            if span_units:
                starts[span_units[0][1]] += 1
                ends[span_units[-1][1]] += 1
            current = [(offset, value) for offset, value in span_units
                       if offset not in covered]
            for index, (offset, value) in enumerate(span_units[:-1]):
                successor.setdefault(value, Counter())[span_units[index + 1][1]] += 1
            for offset, value in current:
                covered.add(offset)
                reachable[value] += 1
            after = start + length
            if after + 1 < len(data) and data[after] == 0 and data[after + 1] == 0:
                followed_by_nul += 1
            if any(value == 0 for offset, value in span_units if offset != after - 2):
                interior_nul += 1
        whole_units = units_at(data, 0, len(data))
        whole.update(value for _offset, value in whole_units)
        span_units_total = sum(len(units_at(data, start, length))
                               for start, length in spans)
        per_selector.append({
            "selector": selector,
            "rom_address": f"0x{entry['rom_address']:08X}",
            "file_offset": f"0x{entry['file_offset']:06X}",
            "decoded_units": len(whole_units),
            "record_span_count": len(spans),
            "record_span_units_total": span_units_total,
            "record_span_units_covered": len(covered),
            "record_span_overlap_units": span_units_total - len(covered),
            "nul_halfwords_in_container": sum(
                1 for _offset, value in whole_units if value == 0),
            "record_spans_followed_by_nul": followed_by_nul,
            "record_spans_with_interior_nul": interior_nul,
        })

    values = []
    for value in sorted(whole):
        record_glyph = glyph(image, font_base, value) if value < 0x100 else None
        values.append({
            "value": f"0x{value:04X}",
            "class": classify(value),
            "reachable_units": reachable.get(value, 0),
            "record_span_occurrences": occurrences.get(value, 0),
            "whole_container_units": whole.get(value, 0),
            "starts_a_record_span": starts.get(value, 0),
            "ends_a_record_span": ends.get(value, 0),
            "successors": {f"0x{other:04X}": count
                           for other, count in
                           sorted(successor.get(value, Counter()).items())},
            "code_index": read_u16(image, font_base + value * 2) if value < 0x100
            else None,
            "glyph_width": record_glyph[0] if record_glyph else None,
        })

    return {
        "ticket": "DIALOGUE-EXPANSION-TOKEN-DESIGN-001",
        "rom": str(rom),
        "sha256": digest,
        "container_table_file_offset": f"0x{CONTAINER_TABLE_FILE_OFFSET:06X}",
        "font_holder": f"0x{FONT_HOLDER_ROM_ADDRESS:08X}",
        "font_base": f"0x{font_base:08X}",
        "containers": per_selector,
        "reachable_units": sum(reachable.values()),
        "reachable_distinct_values": len(reachable),
        "record_span_occurrence_units": sum(occurrences.values()),
        "whole_container_units": sum(whole.values()),
        "whole_container_distinct_values": len(whole),
        "second_text_store": second_store_census(image),
        "values": values,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path,
                        default=ROOT / "roms" / "Dragon Ball Z - Buu's Fury (U).gba")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--font-map", action="store_true",
                        help="dump the code -> font record index map and stop")
    parser.add_argument("--font-map-from", type=lambda text: int(text, 0), default=0xF0)
    parser.add_argument("--font-map-to", type=lambda text: int(text, 0), default=0x120)
    args = parser.parse_args()

    report = census(args.rom)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=1, sort_keys=True),
                             encoding="utf-8")
        print(f"wrote {args.json}")

    if args.font_map:
        image = args.rom.read_bytes()
        font_base = read_u32(image, FONT_HOLDER_ROM_ADDRESS)
        print(f"font descriptor 0x{FONT_DESCRIPTOR_ROM_ADDRESS:08X}:")
        for index in range(8):
            address = FONT_DESCRIPTOR_ROM_ADDRESS + index * 4
            print(f"  +0x{index * 4:02X} 0x{read_u32(image, address):08X}")
        print(f"code map at 0x{font_base:08X}: value -> record index, then width")
        for value in range(args.font_map_from, args.font_map_to):
            index = read_u16(image, font_base + value * 2)
            record = glyph(image, font_base, value)
            print(f"  {value:#06x} index {index:5d} width "
                  f"{record[0] if record else None}")
        return 0

    print(f"rom             : {report['rom']}")
    print(f"sha256          : {report['sha256']}")
    print(f"font base       : {report['font_base']}")
    print(f"reachable units : {report['reachable_units']} "
          f"({report['reachable_distinct_values']} distinct values)")
    print(f"whole container : {report['whole_container_units']} "
          f"({report['whole_container_distinct_values']} distinct values)")
    for entry in report["containers"]:
        print(f"  selector {entry['selector']}: {entry['record_span_count']:4d} records, "
              f"reachable {entry['record_span_units_covered']:6d}/"
              f"{entry['decoded_units']} units, overlap "
              f"{entry['record_span_overlap_units']:6d}, "
              f"NUL {entry['nul_halfwords_in_container']}, "
              f"spans followed by NUL {entry['record_spans_followed_by_nul']}")
    print()
    print("every non-ASCII-printable value, and every value with no glyph record:")
    for row in report["values"]:
        value = int(row["value"], 16)
        printable = 0x20 <= value < 0x7F
        if printable and row["glyph_width"] is not None:
            continue
        print(f"  {row['value']} class={row['class']:<16} reachable "
              f"{row['reachable_units']:6d} occurrences "
              f"{row['record_span_occurrences']:6d} whole "
              f"{row['whole_container_units']:5d} index {row['code_index']} "
              f"width {row['glyph_width']}")
    print()
    ranked = sorted(report["values"], key=lambda row: -row["reachable_units"])
    print(f"top {args.top} values by reachable count:")
    for row in ranked[:args.top]:
        value = int(row["value"], 16)
        print(f"  {row['value']} {chr(value)!r:5} reachable {row['reachable_units']:6d} "
              f"width {row['glyph_width']}")

    image = args.rom.read_bytes()
    font_base = read_u32(image, FONT_HOLDER_ROM_ADDRESS)
    used = {int(row["value"], 16) for row in report["values"]
            if row["reachable_units"]}
    no_glyph = [c for c in range(0x100) if read_u16(image, font_base + c * 2) == 0]
    glyph_unused = [c for c in range(0x100)
                    if read_u16(image, font_base + c * 2) != 0 and c not in used]
    print()
    print(f"values 0x00..0xFF with NO glyph record ({len(no_glyph)}): "
          + " ".join(f"{c:#04x}" for c in no_glyph))
    print(f"values 0x00..0xFF with a glyph record and NO occurrence in the "
          f"reachable corpus ({len(glyph_unused)}): "
          + " ".join(f"{c:#04x}" for c in glyph_unused))
    print("raw code map 0x0000..0x0020: "
          + " ".join(f"{read_u16(image, font_base + c * 2)}" for c in range(0x21)))
    print("first byte past the code map (0x0100) reads: "
          + " ".join(f"{read_u16(image, font_base + c * 2)}" for c in range(0x100, 0x108)))
    highest = max(int(row["value"], 16) for row in report["values"]
                  if row["reachable_units"])
    print("highest unit value in the reachable corpus: "
          f"{highest:#06x}")
    unreached = [row for row in report["values"]
                 if row["whole_container_units"] and not row["reachable_units"]]
    print("values present in a container but in NO record span: "
          + (", ".join(f"{row['value']} ({row['whole_container_units']})"
                       for row in unreached) if unreached else "none"))
    store = report["second_text_store"]
    if store:
        print(f"second text store ({store['profile_id']}): pool "
              f"{store['pool_address']} size {store['pool_size']}, "
              f"{store['declared_strings']} declared strings, "
              f"{store['units']} units, {store['distinct_values']} distinct, "
              f"highest {store['highest_value']}, values >= 0x0100: "
              f"{store['values_at_or_above_0x0100']}")
    print("successors of every classified control value (occurrence count):")
    for row in report["values"]:
        if row["class"].startswith("unclassified"):
            continue
        print(f"  {row['value']} {row['class']}: {row['successors']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
