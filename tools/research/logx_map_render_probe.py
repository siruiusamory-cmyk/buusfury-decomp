"""Read-only selector-1 root census for LOGX-MAP-RENDER-001.

The probe resolves the selector-1 root for every MapEntry through the accepted
route and reports physical shape only:

    MapEntry[+0x2C] + 4 * (selector - 1)   with selector = 1

It deliberately does **not** name any root field semantically.  Each field is
reported as raw bytes with width, null, alignment, pointer-range and
distinctness statistics so a reader can judge physical structure separately
from any downstream meaning.

Pointer classification here means only: "4-byte aligned and inside the 8 MiB
ROM image".  It is not evidence of a target structure type.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROM_SIZE = 0x800000
ROM_BASE = 0x08000000
TABLE_OFFSET = 0x08E2E0
RECORD_SIZE = 0x38
RECORD_COUNT = 0x1C4
TABLE_END = TABLE_OFFSET + RECORD_SIZE * RECORD_COUNT

#: Root header census window, in bytes.  Wider than the LOGExtractor field set
#: so that field boundaries are observed rather than assumed.
ROOT_CENSUS_BYTES = 0x60

#: Root offsets reported per record in the full census, in field order.
REPORTED_OFFSETS = (
    (0x00, 2),
    (0x02, 2),
    (0x04, 4),
    (0x08, 2),
    (0x0A, 2),
    (0x0C, 4),
    (0x10, 4),
    (0x14, 4),
    (0x18, 4),
    (0x1C, 4),
    (0x20, 4),
    (0x24, 4),
    (0x28, 4),
    (0x2C, 4),
    (0x30, 4),
    (0x34, 4),
    (0x38, 4),
    (0x3C, 4),
    (0x40, 4),
    (0x44, 4),
    (0x48, 4),
    (0x4C, 4),
    (0x50, 4),
    (0x54, 4),
    (0x58, 4),
    (0x5C, 4),
)

#: Selector words inspected per MapEntry when bounding the source array.
SOURCE_ARRAY_WORD_LIMIT = 64


def _u16le(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "little")


def _u32le(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def in_rom_word(value: int, size: int) -> bool:
    """True when ``value`` is a 4-byte aligned address inside the ROM image."""
    return value % 4 == 0 and ROM_BASE <= value <= ROM_BASE + size - 4


def _read_field(data: bytes, file_offset: int, width: int) -> int:
    raw = data[file_offset : file_offset + width]
    return int.from_bytes(raw, "little")


def _source_array_run(data: bytes, source: int) -> list[int]:
    """Return the leading run of aligned in-ROM words at ``source``.

    The scan stops at the first null or non-pointer word.  It reports the run
    length observed, not an assumed array bound.
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


def _field_statistics(values: list[int], width: int, rom_size: int) -> dict[str, Any]:
    if not values:
        return {"count": 0}
    in_rom = [value for value in values if in_rom_word(value, rom_size)]
    return {
        "count": len(values),
        "null_count": sum(1 for value in values if value == 0),
        "non_null_count": sum(1 for value in values if value != 0),
        "distinct_values": len(set(values)),
        "aligned_in_rom_count": len(in_rom),
        "unaligned_in_rom_count": sum(
            1 for value in values if value and value not in in_rom
            and ROM_BASE <= value <= ROM_BASE + rom_size
        ),
        "out_of_rom_count": sum(
            1 for value in values if value and not (ROM_BASE <= value <= ROM_BASE + rom_size)
        ),
        "in_rom_not_aligned_count": sum(
            1
            for value in values
            if ROM_BASE <= value <= ROM_BASE + rom_size and value % 4 != 0
        ),
        "min_value": min(values),
        "max_value": max(values),
        "top_values": [
            {"value": value, "count": count}
            for value, count in Counter(values).most_common(6)
        ],
    }


def analyze(data: bytes) -> dict[str, Any]:
    """Return a deterministic census of all selector-1 roots."""
    if len(data) != ROM_SIZE:
        raise ValueError(f"expected 0x{ROM_SIZE:X}-byte canonical ROM, got {len(data):#x}")
    if TABLE_END > len(data):
        raise ValueError("candidate table is outside ROM")

    records: list[dict[str, Any]] = []
    source_runs: dict[int, int] = {}
    for index in range(RECORD_COUNT):
        offset = TABLE_OFFSET + index * RECORD_SIZE
        key_bytes = data[offset : offset + 2]
        source = _u32le(data, offset + 0x2C)
        source_valid = in_rom_word(source, len(data))
        run = _source_array_run(data, source) if source_valid else []
        source_runs[index] = len(run)
        selected = run[0] if run else None
        root = selected if selected is not None else 0
        root_valid = selected is not None and in_rom_word(root, len(data))

        fields: dict[str, Any] = {}
        if root_valid:
            root_file = root - ROM_BASE
            if root_file + ROOT_CENSUS_BYTES <= len(data):
                for field_offset, width in REPORTED_OFFSETS:
                    fields[f"+0x{field_offset:02x}"] = _read_field(
                        data, root_file + field_offset, width
                    )

        records.append(
            {
                "index": index,
                "record_offset": offset,
                "key_bytes_le": int.from_bytes(key_bytes, "little"),
                "key_bytes_be": int.from_bytes(key_bytes, "big"),
                "key_bytes_hex": key_bytes.hex(),
                "source_raw": source,
                "source_valid": source_valid,
                "source_array_run_length": len(run),
                "selector_1_root": root,
                "selector_1_root_hex": f"{root:#010x}" if root else "0x00000000",
                "root_valid": root_valid,
                "fields": fields,
            }
        )

    valid_roots = [int(r["selector_1_root"]) for r in records if r["root_valid"]]
    null_roots = RECORD_COUNT - len(valid_roots)

    field_census: dict[str, Any] = {}
    for field_offset, width in REPORTED_OFFSETS:
        key = f"+0x{field_offset:02x}"
        values = [
            int(r["fields"][key])
            for r in records
            if r["root_valid"] and key in r["fields"]
        ]
        field_census[key] = {"width": width, **_field_statistics(values, width, len(data))}

    root_counter = Counter(valid_roots)
    shared_roots = [
        {
            "root": root,
            "root_hex": f"{root:#010x}",
            "count": count,
            "map_indices": [i for i, r in enumerate(records) if r["selector_1_root"] == root],
        }
        for root, count in sorted(root_counter.items(), key=lambda item: (-item[1], item[0]))
        if count > 1
    ]

    run_histogram = Counter(source_runs.values())
    shared_sources = [
        {
            "source_hex": f"{source:#010x}",
            "count": count,
            "map_indices": [
                i
                for i in range(RECORD_COUNT)
                if _u32le(data, TABLE_OFFSET + i * RECORD_SIZE + 0x2C) == source
            ],
        }
        for source, count in sorted(
            Counter(
                _u32le(data, TABLE_OFFSET + i * RECORD_SIZE + 0x2C)
                for i in range(RECORD_COUNT)
            ).items()
        )
        if count > 1
    ]

    return {
        "rom_size": ROM_SIZE,
        "table_offset": TABLE_OFFSET,
        "table_end": TABLE_END,
        "record_size": RECORD_SIZE,
        "record_count": RECORD_COUNT,
        "root_census_bytes": ROOT_CENSUS_BYTES,
        "selector_formula": "MapEntry[+0x2C] + 4 * (selector - 1)",
        "selector_used": 1,
        "summary": {
            "records": RECORD_COUNT,
            "valid_sources": sum(1 for r in records if r["source_valid"]),
            "valid_selector_1_roots": len(valid_roots),
            "null_or_invalid_roots": null_roots,
            "distinct_roots": len(root_counter),
            "shared_root_groups": len(shared_roots),
            "distinct_sources": len(
                {
                    int(r["source_raw"])
                    for r in records
                }
            ),
            "source_array_run_histogram": {
                str(length): count for length, count in sorted(run_histogram.items())
            },
            "root_min": f"{min(valid_roots):#010x}" if valid_roots else None,
            "root_max": f"{max(valid_roots):#010x}" if valid_roots else None,
        },
        "field_census": field_census,
        "shared_roots": shared_roots,
        "shared_sources": shared_sources,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, help="canonical Buu's Fury ROM (opened read-only)")
    parser.add_argument(
        "--records",
        action="store_true",
        help="include the full per-record census for all 452 MapEntries",
    )
    args = parser.parse_args()

    data = args.rom.read_bytes()
    report = analyze(data)
    report["sha256"] = hashlib.sha256(data).hexdigest()
    if not args.records:
        report.pop("records")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
