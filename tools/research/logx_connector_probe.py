"""Read-only Buu's Fury root ``+0x40``/``+0x44`` transition-record census.

This probe answers, with deterministic output and no ROM writes:

* what ``root +0x40`` and ``root +0x44`` physically hold for all 452 canonical
  selector-1 roots, and whether the two are coupled;
* how many *array references*, *unique record addresses* and *shared record
  addresses* exist, keeping those three numbers separate;
* what the pointed records physically contain, at the engine's own access
  widths, with every field left unnamed wherever the engine does not name it;
* how two candidate destination bytes compare against the accepted two-byte
  ``MapEntry`` lookup key, and which reading resolves.

The root traversal is the accepted ``LOGX-MAP-RENDER-001`` /
``LOGX-LAYER-001`` route and is imported rather than re-derived.  Column names
are physical: ``count_raw``, ``list_raw``, ``bound_a``..``bound_d``,
``key_hi_off_0x11`` and so on.  Any semantic statement about those fields is
made in ``docs/research/LOGX_CONNECTOR_PROVENANCE.md`` from cited engine
instructions, never from this census alone.

Nothing here writes to the ROM image or to any file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from tools.research.logx_layer_probe import (
    CANONICAL_SHA256,
    RECORD_COUNT,
    RECORD_SIZE,
    ROM_BASE,
    ROM_SIZE,
    TABLE_OFFSET,
    in_rom_word,
    resolve_selector_1_roots,
)

#: ``root +0x40`` - the u32 the engine reads as a count.
COUNT_OFFSET = 0x40

#: ``root +0x44`` - the aligned pointer into the array of 4-byte entries.
LIST_OFFSET = 0x44

#: Element width of the array ``root +0x44`` points at.  Taken from the
#: engine's own ``4 * index`` arithmetic, not from target spacing.
ELEMENT_WIDTH = 4

#: The four ``u16`` values the engine's own record consumers read from
#: ``record + 0x08``.
BOUND_BASE = 0x08

#: Two candidate bytes the engine's warp path reads separately and passes to
#: the ``MapEntry`` two-byte-key scan: high byte first, then low byte.
KEY_HIGH_OFFSET = 0x11
KEY_LOW_OFFSET = 0x12

#: A byte the engine reads immediately after the destination pair.
KEY_TAIL_OFFSET = 0x13

#: A byte the engine reads before the destination pair.
PRE_KEY_OFFSET = 0x10

#: The two ``u16`` values at ``record + 0x14`` read by the portal object.
TRAILING_BASE = 0x14

#: Bytes of the record prefix that are identical on every canonical record,
#: plus the bytes of the record that the engine's consumers actually touch.
RECORD_SCAN_BYTES = 0x20


def _u16le(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "little")


def _u16be(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "big")


def _u32le(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def classify_pointer(data: bytes, value: int) -> str:
    """Physical classification of one raw 32-bit array element."""
    if value == 0:
        return "null"
    if in_rom_word(value, len(data)):
        return "aligned_in_rom"
    if ROM_BASE <= value <= ROM_BASE + len(data) - 1:
        return "unaligned_in_rom"
    return "outside_rom"


def map_entry_keys(data: bytes) -> list[bytes]:
    """The accepted two-byte ``MapEntry +0x00`` lookup key of every record."""
    return [
        data[TABLE_OFFSET + i * RECORD_SIZE : TABLE_OFFSET + i * RECORD_SIZE + 2]
        for i in range(RECORD_COUNT)
    ]


def resolve_roots(data: bytes) -> list[dict[str, Any]]:
    """``root +0x40`` / ``root +0x44`` for every selector-1 root."""
    rows: list[dict[str, Any]] = []
    for index, root in enumerate(resolve_selector_1_roots(data)):
        base = root - ROM_BASE
        count = _u32le(data, base + COUNT_OFFSET)
        pointer = _u32le(data, base + LIST_OFFSET)
        rows.append(
            {
                "map_index": index,
                "map_key_bytes_hex": data[
                    TABLE_OFFSET + index * RECORD_SIZE :
                    TABLE_OFFSET + index * RECORD_SIZE + 2
                ].hex(),
                "root": root,
                "root_hex": f"{root:#010x}",
                "count_raw": count,
                "list_raw": pointer,
                "list_hex": f"{pointer:#010x}",
                "list_classification": classify_pointer(data, pointer),
                "list_minus_root": root - pointer if pointer else None,
                "list_is_count_times_four_before_root": (
                    pointer == root - ELEMENT_WIDTH * count if count else pointer == 0
                ),
            }
        )
    return rows


def read_record(data: bytes, address: int) -> dict[str, Any]:
    """Physical fields of one pointed record, at the engine's access widths."""
    base = address - ROM_BASE
    record: dict[str, Any] = {
        "address": address,
        "address_hex": f"{address:#010x}",
        "readable": 0 <= base and base + RECORD_SCAN_BYTES <= len(data),
    }
    if not record["readable"]:
        return record
    record.update(
        {
            "raw_prefix_words": [
                f"{_u32le(data, base + 4 * i):#010x}" for i in range(2)
            ],
            "raw_bytes_0x00_0x1b": data[base : base + 0x1C].hex(),
            # The four u16 values the engine reads from record + 0x08.
            "bound_a_raw": _u16le(data, base + BOUND_BASE + 0),
            "bound_b_raw": _u16le(data, base + BOUND_BASE + 2),
            "bound_c_raw": _u16le(data, base + BOUND_BASE + 4),
            "bound_d_raw": _u16le(data, base + BOUND_BASE + 6),
            "bound_a_signed": _s16(_u16le(data, base + BOUND_BASE + 0)),
            "bound_b_signed": _s16(_u16le(data, base + BOUND_BASE + 2)),
            "bound_c_signed": _s16(_u16le(data, base + BOUND_BASE + 4)),
            "bound_d_signed": _s16(_u16le(data, base + BOUND_BASE + 6)),
            # Candidate destination readings, all unnamed.
            "byte_at_0x10": data[base + PRE_KEY_OFFSET],
            "key_hi_off_0x11": data[base + KEY_HIGH_OFFSET],
            "key_lo_off_0x12": data[base + KEY_LOW_OFFSET],
            "key_pair_big_endian": data[
                base + KEY_HIGH_OFFSET : base + KEY_LOW_OFFSET + 1
            ].hex(),
            "key_pair_little_endian": data[
                base + KEY_LOW_OFFSET : base + KEY_HIGH_OFFSET - 1 : -1
            ].hex(),
            "byte_at_0x13": data[base + KEY_TAIL_OFFSET],
            # The two u16 values the portal object reads from record + 0x14.
            "trailing_u16_at_0x14": _u16le(data, base + TRAILING_BASE),
            "trailing_u16_at_0x16": _u16le(data, base + TRAILING_BASE + 2),
        }
    )
    record["bounds_a_le_c"] = record["bound_a_raw"] <= record["bound_c_raw"]
    record["bounds_b_le_d"] = record["bound_b_raw"] <= record["bound_d_raw"]
    record["width_raw"] = record["bound_c_raw"] - record["bound_a_raw"]
    record["height_raw"] = record["bound_d_raw"] - record["bound_b_raw"]
    record["zero_area"] = bool(
        record["width_raw"] == 0 or record["height_raw"] == 0
    )
    return record


def _s16(value: int) -> int:
    return value - 0x10000 if value & 0x8000 else value


def build_report(data: bytes) -> dict[str, Any]:
    roots = resolve_roots(data)
    keys = map_entry_keys(data)
    key_index = {key: i for i, key in enumerate(keys)}

    references: list[dict[str, Any]] = []
    for root_row in roots:
        pointer = int(root_row["list_raw"])
        count = int(root_row["count_raw"])
        for element in range(count):
            if root_row["list_classification"] != "aligned_in_rom":
                value = 0
                state = "unreadable_list"
            else:
                value = _u32le(data, (pointer - ROM_BASE) + ELEMENT_WIDTH * element)
                state = classify_pointer(data, value)
            key_bytes = None
            if state == "aligned_in_rom":
                base = value - ROM_BASE
                key_bytes = data[base + KEY_HIGH_OFFSET : base + KEY_LOW_OFFSET + 1]
            references.append(
                {
                    "map_index": int(root_row["map_index"]),
                    "root_hex": root_row["root_hex"],
                    "element_index": element,
                    "element_address": pointer + ELEMENT_WIDTH * element
                    if root_row["list_classification"] == "aligned_in_rom"
                    else 0,
                    "record_raw": value,
                    "record_hex": f"{value:#010x}",
                    "classification": state,
                    "key_pair_big_endian_hex": (
                        key_bytes.hex() if key_bytes is not None else None
                    ),
                }
            )

    non_null = [row for row in references if row["classification"] == "aligned_in_rom"]
    unique_records = sorted({int(row["record_raw"]) for row in non_null})
    reference_counts = Counter(int(row["record_raw"]) for row in non_null)
    shared = sorted(
        (address for address, count in reference_counts.items() if count > 1)
    )
    records = {address: read_record(data, address) for address in unique_records}

    # Destination key resolution against the accepted MapEntry lookup key.
    resolved = 0
    unresolved: list[str] = []
    destinations: Counter = Counter()
    for address in unique_records:
        record = records[address]
        pair = bytes.fromhex(record["key_pair_big_endian"])
        if not record.get("readable"):
            continue
        index = key_index.get(pair)
        if index is None:
            unresolved.append(f"{address:#010x}")
        else:
            resolved += 1
            destinations[index] += 1
            record["destination_map_index"] = index
            record["destination_key_bytes_hex"] = pair.hex()

    # Ordered bounds census.
    ordered = sum(
        1
        for address in unique_records
        if records[address].get("readable")
        and records[address]["bounds_a_le_c"]
        and records[address]["bounds_b_le_d"]
    )

    anomalies: dict[str, list[str]] = {
        "count_nonzero_with_null_list": [],
        "count_zero_with_nonnull_list": [],
        "list_not_four_times_count_before_root": [],
        "list_outside_rom": [],
        "record_null": [],
        "record_outside_rom": [],
        "record_unaligned_in_rom": [],
        "bounds_not_ordered": [],
        "zero_area_region": [],
        "destination_key_unresolved": [],
        "duplicate_element_in_one_root": [],
    }
    for root_row in roots:
        count = int(root_row["count_raw"])
        pointer = int(root_row["list_raw"])
        name = f"map{root_row['map_index']}"
        if count and not pointer:
            anomalies["count_nonzero_with_null_list"].append(name)
        if pointer and not count:
            anomalies["count_zero_with_nonnull_list"].append(name)
        if pointer and not root_row["list_is_count_times_four_before_root"]:
            anomalies["list_not_four_times_count_before_root"].append(name)
        if pointer and root_row["list_classification"] != "aligned_in_rom":
            anomalies["list_outside_rom"].append(name)
    per_root: dict[int, list[int]] = {}
    for row in references:
        name = f"map{row['map_index']}#{row['element_index']}"
        if row["classification"] == "null":
            anomalies["record_null"].append(name)
        elif row["classification"] == "outside_rom":
            anomalies["record_outside_rom"].append(name)
        elif row["classification"] == "unaligned_in_rom":
            anomalies["record_unaligned_in_rom"].append(name)
        if row["classification"] == "aligned_in_rom":
            per_root.setdefault(int(row["map_index"]), []).append(
                int(row["record_raw"])
            )
    for index, values in sorted(per_root.items()):
        if len(values) != len(set(values)):
            anomalies["duplicate_element_in_one_root"].append(f"map{index}")
    for address in unique_records:
        record = records[address]
        if not record.get("readable"):
            continue
        name = record["address_hex"]
        if not (record["bounds_a_le_c"] and record["bounds_b_le_d"]):
            anomalies["bounds_not_ordered"].append(name)
        if record["zero_area"]:
            anomalies["zero_area_region"].append(name)
        if "destination_map_index" not in record:
            anomalies["destination_key_unresolved"].append(name)
    anomalies["destination_key_unresolved"] = unresolved
    anomalies = {key: value for key, value in anomalies.items() if value}

    bound_values = [
        records[address][field]
        for address in unique_records
        if records[address].get("readable")
        for field in ("bound_a_raw", "bound_b_raw", "bound_c_raw", "bound_d_raw")
    ]

    # Reciprocal-link census over resolved destinations.
    links = {
        (int(row["map_index"]), int(records[int(row["record_raw"])].get("destination_map_index", -1)))
        for row in non_null
        if "destination_map_index" in records.get(int(row["record_raw"]), {})
    }
    reciprocal = sum(1 for src, dst in links if (dst, src) in links and src != dst)
    self_links = sorted(src for src, dst in links if src == dst)

    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "rom_size": len(data),
        "root_count": len(roots),
        "count_offset": f"+0x{COUNT_OFFSET:02x}",
        "list_offset": f"+0x{LIST_OFFSET:02x}",
        "element_width_bytes": ELEMENT_WIDTH,
        "bound_base_offset": f"+0x{BOUND_BASE:02x}",
        "key_high_offset": f"+0x{KEY_HIGH_OFFSET:02x}",
        "key_low_offset": f"+0x{KEY_LOW_OFFSET:02x}",
        "root_summary": {
            "roots": len(roots),
            "count_zero": sum(1 for row in roots if int(row["count_raw"]) == 0),
            "count_nonzero": sum(1 for row in roots if int(row["count_raw"]) > 0),
            "count_sum": sum(int(row["count_raw"]) for row in roots),
            "count_max": max((int(row["count_raw"]) for row in roots), default=0),
            "count_distribution": {
                str(value): count
                for value, count in sorted(
                    Counter(int(row["count_raw"]) for row in roots).items()
                )
            },
            "list_null": sum(1 for row in roots if int(row["list_raw"]) == 0),
            "list_nonnull": sum(1 for row in roots if int(row["list_raw"]) != 0),
            "list_unique_targets": len(
                {int(row["list_raw"]) for row in roots if int(row["list_raw"])}
            ),
            "list_shared_targets": sum(
                1
                for count in Counter(
                    int(row["list_raw"]) for row in roots if int(row["list_raw"])
                ).values()
                if count > 1
            ),
            "list_classification": dict(
                sorted(
                    Counter(str(row["list_classification"]) for row in roots).items()
                )
            ),
            "count_zero_iff_list_null": all(
                (int(row["count_raw"]) == 0) == (int(row["list_raw"]) == 0)
                for row in roots
            ),
            "list_always_four_times_count_before_root": all(
                row["list_is_count_times_four_before_root"] for row in roots
            ),
            "list_minus_root_distribution": {
                str(value): count
                for value, count in sorted(
                    Counter(
                        int(row["list_minus_root"])
                        for row in roots
                        if row["list_minus_root"] is not None
                    ).items()
                )
            },
        },
        "array_summary": {
            "references": len(references),
            "references_null": sum(
                1 for row in references if row["classification"] == "null"
            ),
            "references_nonnull": len(non_null),
            "references_aligned_in_rom": sum(
                1 for row in references if row["classification"] == "aligned_in_rom"
            ),
            "references_unaligned_in_rom": sum(
                1 for row in references if row["classification"] == "unaligned_in_rom"
            ),
            "references_outside_rom": sum(
                1 for row in references if row["classification"] == "outside_rom"
            ),
            "unique_records": len(unique_records),
            "shared_records": len(shared),
            "max_reference_count": max(reference_counts.values(), default=0),
            "record_pointer_min": f"{min(unique_records):#010x}"
            if unique_records
            else None,
            "record_pointer_max": f"{max(unique_records):#010x}"
            if unique_records
            else None,
            "all_records_4_byte_aligned": all(
                address % 4 == 0 for address in unique_records
            ),
        },
        "record_summary": {
            "records": len(unique_records),
            "readable": sum(
                1 for address in unique_records if records[address].get("readable")
            ),
            "destination_resolved": resolved,
            "destination_unresolved": len(unresolved),
            "bounds_ordered": ordered,
            "bounds_not_ordered": len(unique_records) - ordered,
            "zero_area_regions": sum(
                1
                for address in unique_records
                if records[address].get("zero_area")
            ),
            "bound_value_min": min(bound_values) if bound_values else None,
            "bound_value_max": max(bound_values) if bound_values else None,
            "bound_value_distinct": len(set(bound_values)),
            "bound_value_mod8_census": {
                str(value): count
                for value, count in sorted(
                    Counter(value % 8 for value in bound_values).items()
                )
            },
            "byte_at_0x10_census": {
                str(value): count
                for value, count in sorted(
                    Counter(
                        records[address]["byte_at_0x10"]
                        for address in unique_records
                        if records[address].get("readable")
                    ).items()
                )
            },
            "byte_at_0x13_census": {
                str(value): count
                for value, count in sorted(
                    Counter(
                        records[address]["byte_at_0x13"]
                        for address in unique_records
                        if records[address].get("readable")
                    ).items()
                )
            },
            "prefix_word_0_census": {
                value: count
                for value, count in sorted(
                    Counter(
                        records[address]["raw_prefix_words"][0]
                        for address in unique_records
                        if records[address].get("readable")
                    ).items()
                )
            },
            "prefix_word_4_census": {
                value: count
                for value, count in sorted(
                    Counter(
                        records[address]["raw_prefix_words"][1]
                        for address in unique_records
                        if records[address].get("readable")
                    ).items()
                )
            },
        },
        "transition_graph": {
            "links": len(links),
            "reciprocal": reciprocal,
            "one_way": len(links) - reciprocal,
            "self_links": len(self_links),
            "self_link_sources": self_links,
            "distinct_destinations": len(destinations),
            "maps_with_at_least_one_link": len({src for src, _ in links}),
        },
        "anomalies": anomalies,
        "anomaly_counts": {key: len(value) for key, value in anomalies.items()},
        "roots": roots,
        "references": references,
        "records": {f"{address:#010x}": record for address, record in sorted(records.items())},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, help="canonical Buu's Fury ROM (read-only)")
    parser.add_argument("--roots", action="store_true", help="include the 452 root rows")
    parser.add_argument("--references", action="store_true", help="include every array element")
    parser.add_argument("--records", action="store_true", help="include every unique record")
    args = parser.parse_args(argv)

    data = load_rom(args.rom)
    report = build_report(data)
    if not args.roots:
        report.pop("roots")
    if not args.references:
        report.pop("references")
    if not args.records:
        report.pop("records")
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


def load_rom(path: Path) -> bytes:
    data = path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != CANONICAL_SHA256:
        raise SystemExit(
            f"refusing non-canonical ROM: expected SHA-256 {CANONICAL_SHA256}, got {actual}"
        )
    if len(data) != ROM_SIZE:
        raise SystemExit(f"refusing image of {len(data)} bytes, expected {ROM_SIZE:#x}")
    return data


if __name__ == "__main__":
    raise SystemExit(main())
