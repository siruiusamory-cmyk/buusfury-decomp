"""Read-only Buu's Fury layer-record census for LOGX-LAYER-001.

The probe enumerates every non-null layer record reachable from the four
established selector-1 root slots (``root +0x14``, ``+0x18``, ``+0x1C``,
``+0x20``) for all 452 canonical ``MapEntry`` records, and separately scans the
whole image for every aligned occurrence of each observed ``+0x00`` word.

It reports physical shape only.  Field widths follow the engine's own accesses
where those are established (cited in ``docs/research/LOGX_LAYER_PROVENANCE.md``);
nothing is named semantically, and no field is combined into a wider type than
the instruction that reads it.

The root resolution reuses the accepted ``LOGX-MAP-RENDER-001`` route:

    MapEntry[+0x2C] -> leading run of aligned in-ROM words -> word[0]

which is selector ``1`` of ``MapEntry[+0x2C] + 4 * (selector - 1)``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROM_SIZE = 0x800000
ROM_BASE = 0x08000000
TABLE_OFFSET = 0x08E2E0
RECORD_SIZE = 0x38
RECORD_COUNT = 0x1C4
TABLE_END = TABLE_OFFSET + RECORD_SIZE * RECORD_COUNT

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

#: The four confirmed layer-pointer slots inside the selector-1 root, in slot
#: order.  The names are positional, not semantic: no BG identity is asserted.
ROOT_LAYER_SLOTS = (0x14, 0x18, 0x1C, 0x20)

#: Selector words inspected per MapEntry when bounding the source array.
SOURCE_ARRAY_WORD_LIMIT = 64

#: Layer-record census window, in bytes.  Wide enough for the 0x18-byte prefix,
#: the 0x24-byte +0x18 window and the 0x28-byte block that follows it.
CENSUS_BYTES = 0x60

#: Words inspected from ``record + 0x18`` when characterising the array window.
POINTER_WINDOW_OFFSET = 0x18
POINTER_WINDOW_WORDS = 16

#: Region scanned for the standalone ``+0x00`` word census.  Bounded so the scan
#: is cheap; the caller must state the bound when reporting a negative result.
SCAN_START = 0x08100000
SCAN_END = 0x08400000

#: Byte fields individually histogrammed across the unique-record corpus.
BYTE_FIELDS = (0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17)


def _u16le(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "little")


def _u32le(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def _s16le(data: bytes, offset: int) -> int:
    value = _u16le(data, offset)
    return value - 0x10000 if value & 0x8000 else value


def in_rom_word(value: int, size: int) -> bool:
    """True when ``value`` is a 4-byte aligned address inside the ROM image."""
    return value % 4 == 0 and ROM_BASE <= value <= ROM_BASE + size - 4


def in_rom_any(value: int, size: int) -> bool:
    """True when ``value`` is any address inside the ROM image (any alignment)."""
    return ROM_BASE <= value <= ROM_BASE + size - 1


def _source_array_run(data: bytes, source: int) -> list[int]:
    """Return the leading run of aligned in-ROM words at ``source``.

    Identical rule to the accepted ``logx_map_render_probe``: the scan stops at
    the first null or non-pointer word and reports the observed run, not an
    assumed array bound.
    """
    words: list[int] = []
    if not in_rom_word(source, len(data)):
        return words
    offset = source - ROM_BASE
    limit = min(offset + 4 * SOURCE_ARRAY_WORD_LIMIT, len(data) - 4)
    while offset <= limit:
        word = _u32le(data, offset)
        if word == 0 or not in_rom_word(word, len(data)):
            break
        words.append(word)
        offset += 4
    return words


def resolve_selector_1_roots(data: bytes) -> list[int]:
    """Return the 452 selector-1 root addresses (0 when the route fails)."""
    roots: list[int] = []
    for index in range(RECORD_COUNT):
        offset = TABLE_OFFSET + index * RECORD_SIZE
        source = _u32le(data, offset + 0x2C)
        run = _source_array_run(data, source)
        roots.append(run[0] if run else 0)
    return roots


def container_header(data: bytes, address: int) -> tuple[int, int] | None:
    """``(word0, word1)`` of a candidate container header at ``address``.

    Reads the two header words only.  This is a *shape* probe: it does not
    decompress, and a well-formed header is not by itself evidence that the
    target is a screenblock container.
    """
    if not in_rom_word(address, len(data)):
        return None
    offset = address - ROM_BASE
    if offset + 8 > len(data):
        return None
    return _u32le(data, offset), _u32le(data, offset + 4)


def read_record(data: bytes, address: int) -> dict[str, Any]:
    """Report one candidate layer record as physical fields.

    No field is merged and none is named.  ``pointer_window`` is the first
    ``POINTER_WINDOW_WORDS`` words from ``+0x18``; every word is classified as
    null, aligned in-ROM, or neither, and the leading run of aligned in-ROM
    words is reported separately from the non-null count so a gap is never
    mistaken for the end of an array.
    """
    base = address - ROM_BASE
    record: dict[str, Any] = {
        "address": address,
        "file_offset": base,
        "readable": base + CENSUS_BYTES <= len(data),
    }
    if not record["readable"]:
        return record

    handler = _u32le(data, base)
    preceding = _u32le(data, base - 4) if base >= 4 else None
    window: list[int] = []
    for index in range(POINTER_WINDOW_WORDS):
        slot = base + POINTER_WINDOW_OFFSET + index * 4
        if slot + 4 > len(data):
            break
        window.append(_u32le(data, slot))
    leading_run = 0
    for value in window:
        if value and in_rom_word(value, len(data)):
            leading_run += 1
        else:
            break

    first_header = None
    if window and window[0]:
        first_header = container_header(data, window[0])
    record.update(
        {
            "handler_raw": handler,
            "handler_target": handler & ~1,
            "handler_is_thumb_bit_set": bool(handler & 1),
            "handler_aligned": handler % 4 == 0,
            # The word immediately before the +0x00 field.  For the observed
            # self-patching redirect stubs this is the stub's own literal.
            "word_before_handler_raw": preceding,
            "preceding_word_equals_self_pointer": (
                preceding is not None and preceding == address - 0x04 + 0x02
            ),
            "bytes": data[base : base + CENSUS_BYTES].hex(),
            "plus_04_raw": _u32le(data, base + 0x04),
            "plus_08_raw": _u32le(data, base + 0x08),
            "plus_0c_u16": _u16le(data, base + 0x0C),
            "plus_0c_s16": _s16le(data, base + 0x0C),
            "plus_0e_u16": _u16le(data, base + 0x0E),
            "plus_0e_s16": _s16le(data, base + 0x0E),
            "plus_10_u16": _u16le(data, base + 0x10),
            "plus_10_s16": _s16le(data, base + 0x10),
            "plus_12_u16": _u16le(data, base + 0x12),
            "plus_12_s16": _s16le(data, base + 0x12),
            "plus_14_u16": _u16le(data, base + 0x14),
            "plus_16_u16": _u16le(data, base + 0x16),
            "plus_16_s16": _s16le(data, base + 0x16),
            "byte_14_raw": data[base + 0x14],
            "byte_15_raw": data[base + 0x15],
            "byte_16_raw": data[base + 0x16],
            "byte_17_raw": data[base + 0x17],
            "pointer_window": window,
            "pointer_window_non_null": sum(1 for value in window if value),
            "pointer_window_aligned_in_rom": sum(
                1 for value in window if value and in_rom_word(value, len(data))
            ),
            "pointer_window_leading_run": leading_run,
            "pointer_window_first_header": list(first_header) if first_header else None,
            "pointer_window_distinct": len({value for value in window if value}),
            "grid_product_raw": data[base + 0x14] * data[base + 0x15],
        }
    )
    product = int(record["grid_product_raw"])
    record["window_words_in_product"] = [
        window[index] for index in range(min(product, len(window)))
    ]
    record["window_all_product_words_aligned_in_rom"] = bool(product) and all(
        value and in_rom_word(value, len(data)) for value in record["window_words_in_product"]
    )
    return record


def scan_handler_words(
    data: bytes,
    handler: int,
    *,
    start: int = SCAN_START,
    end: int = SCAN_END,
    aligned_only: bool = True,
) -> list[int]:
    """Every occurrence of ``handler`` as a little-endian word in ``[start, end)``."""
    needle = handler.to_bytes(4, "little")
    step = 4 if aligned_only else 2
    hits: list[int] = []
    offset = start - ROM_BASE
    limit = min(end - ROM_BASE, len(data) - 4)
    while offset <= limit:
        if data[offset : offset + 4] == needle:
            hits.append(offset + ROM_BASE)
        offset += step
    return hits


def _histogram(values: list[int], limit: int = 12) -> list[dict[str, int]]:
    return [
        {"value": value, "count": count} for value, count in Counter(values).most_common(limit)
    ]


def analyze_roots(data: bytes) -> dict[str, Any]:
    """Return the deterministic root-referenced layer census."""
    if len(data) != ROM_SIZE:
        raise ValueError(f"expected 0x{ROM_SIZE:X}-byte canonical ROM, got {len(data):#x}")
    if TABLE_END > len(data):
        raise ValueError("candidate table is outside ROM")

    roots = resolve_selector_1_roots(data)
    references: list[dict[str, Any]] = []
    null_slots = 0
    for index, root in enumerate(roots):
        key = data[TABLE_OFFSET + index * RECORD_SIZE : TABLE_OFFSET + index * RECORD_SIZE + 2]
        for slot in ROOT_LAYER_SLOTS:
            if not in_rom_word(root, len(data)):
                state, layer = "root_invalid", 0
            else:
                layer = _u32le(data, root - ROM_BASE + slot)
                if layer == 0:
                    state = "null"
                elif not in_rom_word(layer, len(data)):
                    state = "not_aligned_in_rom" if in_rom_any(layer, len(data)) else "outside_rom"
                else:
                    state = "non_null"
            if state != "non_null":
                null_slots += 1
            references.append(
                {
                    "index": index,
                    "key_bytes_hex": key.hex(),
                    "root": root,
                    "slot": slot,
                    "layer": layer,
                    "slot_state": state,
                }
            )

    non_null = [r for r in references if r["slot_state"] == "non_null"]
    unique_records = sorted({int(r["layer"]) for r in non_null})
    records = {address: read_record(data, address) for address in unique_records}

    handlers = Counter(int(records[a]["handler_raw"]) for a in unique_records)
    reference_handlers = Counter(int(records[int(r["layer"])]["handler_raw"]) for r in non_null)

    scans: dict[str, Any] = {}
    for handler in sorted(handlers):
        hits = scan_handler_words(data, handler)
        scans[f"{handler:#010x}"] = {
            "scan_start": f"{SCAN_START:#010x}",
            "scan_end": f"{SCAN_END:#010x}",
            "aligned_hits": len(hits),
            "reference_count": sum(
                1 for r in non_null if int(records[int(r["layer"])]["handler_raw"]) == handler
            ),
            "hits_not_used_as_a_record": len(
                set(hits) - {int(r["layer"]) for r in non_null}
            ),
            "sample_hits": [f"{h:#010x}" for h in hits[:8]],
        }

    handler_summary: dict[str, Any] = {}
    for handler in sorted(handlers):
        members = [a for a in unique_records if int(records[a]["handler_raw"]) == handler]
        handler_summary[f"{handler:#010x}"] = {
            "unique_records": len(members),
            "references": sum(1 for r in non_null if int(r["layer"]) in set(members)),
            "preceding_word_matches_self_pointer": sum(
                1 for a in members if records[a]["preceding_word_equals_self_pointer"]
            ),
            "plus_14_u16_values": dict(
                sorted(Counter(int(records[a]["plus_14_u16"]) for a in members).items())
            ),
            "byte_14_values": dict(
                sorted(Counter(int(records[a]["byte_14_raw"]) for a in members).items())
            ),
            "byte_15_values": dict(
                sorted(Counter(int(records[a]["byte_15_raw"]) for a in members).items())
            ),
            "byte_16_values": dict(
                sorted(Counter(int(records[a]["byte_16_raw"]) for a in members).items())
            ),
            "byte_17_values": dict(
                sorted(Counter(int(records[a]["byte_17_raw"]) for a in members).items())
            ),
            "plus_0c_s16_top": _histogram([int(records[a]["plus_0c_s16"]) for a in members]),
            "plus_10_s16_top": _histogram([int(records[a]["plus_10_s16"]) for a in members]),
            "plus_0e_u16_top": _histogram([int(records[a]["plus_0e_u16"]) for a in members]),
            "plus_12_u16_top": _histogram([int(records[a]["plus_12_u16"]) for a in members]),
            "plus_16_s16_values": dict(
                sorted(Counter(int(records[a]["plus_16_s16"]) for a in members).items())
            ),
            "grid_product_values": dict(
                sorted(Counter(int(records[a]["grid_product_raw"]) for a in members).items())
            ),
            "window_all_product_words_aligned_in_rom": sum(
                1 for a in members if records[a]["window_all_product_words_aligned_in_rom"]
            ),
            "plus_04_distinct": len({int(records[a]["plus_04_raw"]) for a in members}),
            "plus_08_distinct": len({int(records[a]["plus_08_raw"]) for a in members}),
        }

    slot_usage: dict[str, Any] = {}
    for slot in ROOT_LAYER_SLOTS:
        slot_refs = [r for r in references if int(r["slot"]) == slot]
        slot_non_null = [r for r in slot_refs if r["slot_state"] == "non_null"]
        slot_usage[f"+0x{slot:02x}"] = {
            "references": len(slot_refs),
            "null": sum(1 for r in slot_refs if r["slot_state"] == "null"),
            "non_null": len(slot_non_null),
            "distinct_layers": len({int(r["layer"]) for r in slot_non_null}),
            "handler_census": {
                f"{handler:#010x}": count
                for handler, count in sorted(
                    Counter(
                        int(records[int(r["layer"])]["handler_raw"]) for r in slot_non_null
                    ).items()
                )
            },
        }

    byte_histograms: dict[str, Any] = {}
    for offset in BYTE_FIELDS:
        counter = Counter(data[address - ROM_BASE + offset] for address in unique_records)
        byte_histograms[f"+0x{offset:02x}"] = {
            "distinct": len(counter),
            "minimum": min(counter) if counter else None,
            "maximum": max(counter) if counter else None,
            "top_values": [
                {"value": value, "count": count} for value, count in counter.most_common(12)
            ],
        }

    shared = [
        {
            "layer": address,
            "layer_hex": f"{address:#010x}",
            "reference_count": count,
            "references": [
                {"index": int(r["index"]), "slot": f"+0x{int(r['slot']):02x}"}
                for r in non_null
                if int(r["layer"]) == address
            ],
        }
        for address, count in sorted(
            Counter(int(r["layer"]) for r in non_null).items(), key=lambda item: (-item[1], item[0])
        )
        if count > 1
    ]

    anomalies: dict[str, list[str]] = {
        "handler_thumb_bit_clear": [],
        "handler_aligned": [],
        "preceding_word_not_self_pointer": [],
        "pointer_window_all_null": [],
        "pointer_window_has_internal_null": [],
        "pointer_window_word_out_of_rom": [],
        "first_pointer_header_word1_not_0x800": [],
        "grid_product_zero": [],
        "plus_0e_nonzero": [],
        "plus_12_nonzero": [],
        "plus_16_nonzero": [],
        "byte_16_nonzero": [],
        "byte_17_nonzero": [],
    }
    for address in unique_records:
        record = records[address]
        name = f"{address:#010x}"
        if not record["handler_is_thumb_bit_set"]:
            anomalies["handler_thumb_bit_clear"].append(name)
        if record["handler_aligned"]:
            anomalies["handler_aligned"].append(name)
        if not record["preceding_word_equals_self_pointer"]:
            anomalies["preceding_word_not_self_pointer"].append(name)
        window = list(record["pointer_window"])
        product = int(record["grid_product_raw"])
        used = window[:product]
        if window and not any(window):
            anomalies["pointer_window_all_null"].append(name)
        if used and any(not value for value in used):
            anomalies["pointer_window_has_internal_null"].append(name)
        if any(value and not in_rom_word(value, len(data)) for value in used):
            anomalies["pointer_window_word_out_of_rom"].append(name)
        header = record["pointer_window_first_header"]
        if header is not None and product and header[1] != 0x800:
            anomalies["first_pointer_header_word1_not_0x800"].append(name)
        if product == 0:
            anomalies["grid_product_zero"].append(name)
        if int(record["plus_0e_u16"]):
            anomalies["plus_0e_nonzero"].append(name)
        if int(record["plus_12_u16"]):
            anomalies["plus_12_nonzero"].append(name)
        if int(record["plus_16_s16"]):
            anomalies["plus_16_nonzero"].append(name)
        if int(record["byte_16_raw"]):
            anomalies["byte_16_nonzero"].append(name)
        if int(record["byte_17_raw"]):
            anomalies["byte_17_nonzero"].append(name)

    return {
        "rom_size": ROM_SIZE,
        "table_offset": TABLE_OFFSET,
        "table_end": TABLE_END,
        "record_size": RECORD_SIZE,
        "record_count": RECORD_COUNT,
        "root_layer_slots": [f"+0x{slot:02x}" for slot in ROOT_LAYER_SLOTS],
        "census_bytes": CENSUS_BYTES,
        "pointer_window_offset": f"+0x{POINTER_WINDOW_OFFSET:02x}",
        "pointer_window_words": POINTER_WINDOW_WORDS,
        "summary": {
            "map_entries": RECORD_COUNT,
            "valid_roots": sum(1 for root in roots if in_rom_word(root, len(data))),
            "layer_references": len(references),
            "null_layer_slots": null_slots,
            "non_null_references": len(non_null),
            "unique_layer_records": len(unique_records),
            "shared_layer_records": len(shared),
            "distinct_handler_words": len(handlers),
            "handler_census_unique_records": {
                f"{handler:#010x}": count for handler, count in sorted(handlers.items())
            },
            "handler_census_references": {
                f"{handler:#010x}": count for handler, count in sorted(reference_handlers.items())
            },
            "layer_pointer_min": f"{min(unique_records):#010x}" if unique_records else None,
            "layer_pointer_max": f"{max(unique_records):#010x}" if unique_records else None,
            "unique_records_unreadable": sum(
                1 for address in unique_records if not records[address]["readable"]
            ),
            "unique_records_with_non_null_pointer_window": sum(
                1 for address in unique_records if records[address]["pointer_window_non_null"]
            ),
        },
        "standalone_scan": scans,
        "slot_usage": slot_usage,
        "byte_field_histograms": byte_histograms,
        "handler_summary": handler_summary,
        "shared_layer_records": shared,
        "anomalies": {key: value for key, value in anomalies.items() if value},
        "layer_records": {f"{address:#010x}": record for address, record in sorted(records.items())},
        "references": references,
    }


def load_rom(path: Path) -> bytes:
    data = path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != CANONICAL_SHA256:
        raise SystemExit(
            f"refusing non-canonical ROM: expected SHA-256 {CANONICAL_SHA256}, got {actual}"
        )
    return data


CSV_COLUMNS = (
    "map_index,key_hex,root,root_slot,layer,handler_raw,handler_target,"
    "preceding_word,+04,+08,+0c_u16,+0c_s16,+0e_u16,+10_u16,+10_s16,+12_u16,"
    "+14_u16,+16_u16,+16_s16,byte_14,byte_15,byte_16,byte_17,"
    "ptr_non_null,ptr_leading_run,ptr_distinct,ptr_product_all_rom,first_header_word1,slot_state"
)


def write_csv(report: dict[str, Any], path: Path) -> None:
    records = report["layer_records"]
    lines = [CSV_COLUMNS]
    for reference in report["references"]:
        layer = int(reference["layer"])
        record = records.get(f"{layer:#010x}") if layer else None
        record = record or {}
        header = record.get("pointer_window_first_header")
        lines.append(
            ",".join(
                str(value)
                for value in (
                    reference["index"],
                    reference["key_bytes_hex"],
                    f"{int(reference['root']):#010x}",
                    f"+0x{int(reference['slot']):02x}",
                    f"{layer:#010x}" if layer else "0",
                    f"{int(record['handler_raw']):#010x}" if record else "",
                    f"{int(record['handler_target']):#010x}" if record else "",
                    f"{int(record['word_before_handler_raw']):#010x}" if record else "",
                    f"{int(record['plus_04_raw']):#010x}" if record else "",
                    f"{int(record['plus_08_raw']):#010x}" if record else "",
                    record.get("plus_0c_u16", ""),
                    record.get("plus_0c_s16", ""),
                    record.get("plus_0e_u16", ""),
                    record.get("plus_10_u16", ""),
                    record.get("plus_10_s16", ""),
                    record.get("plus_12_u16", ""),
                    record.get("plus_14_u16", ""),
                    record.get("plus_16_u16", ""),
                    record.get("plus_16_s16", ""),
                    record.get("byte_14_raw", ""),
                    record.get("byte_15_raw", ""),
                    record.get("byte_16_raw", ""),
                    record.get("byte_17_raw", ""),
                    record.get("pointer_window_non_null", ""),
                    record.get("pointer_window_leading_run", ""),
                    record.get("pointer_window_distinct", ""),
                    record.get("window_all_product_words_aligned_in_rom", ""),
                    "" if header is None else header[1],
                    reference["slot_state"],
                )
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, help="canonical Buu's Fury ROM (opened read-only)")
    parser.add_argument("--references", action="store_true", help="include the 1808-row census")
    parser.add_argument("--layers", action="store_true", help="include the per-record dump")
    parser.add_argument("--csv", type=Path, default=None, help="write the reference census as CSV")
    args = parser.parse_args(argv)

    data = load_rom(args.rom)
    report = analyze_roots(data)
    report["sha256"] = hashlib.sha256(data).hexdigest()
    if args.csv is not None:
        write_csv(report, args.csv)
    if not args.references:
        report.pop("references")
    if not args.layers:
        report.pop("layer_records")
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
