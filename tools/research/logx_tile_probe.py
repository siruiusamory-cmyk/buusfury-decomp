"""Read-only Buu's Fury chunk/tile census for LOGX-TILE-001.

The probe answers, with deterministic output and no ROM writes:

* what every dominant-layer ``+0x18`` array element points at, and how many
  *references*, *unique targets* and *unique payloads* there are;
* what the payload decodes to, at the engine's own access width, and the full
  per-bit census of the decoded 16-bit words;
* what each selector-1 root's ``+0x48`` container decodes to, and what the
  engine's own prefix recurrence turns it into;
* what each selector-1 root's ``+0x4C`` table points at.

The root/layer traversal is the accepted ``LOGX-MAP-RENDER-001`` /
``LOGX-LAYER-001`` route and is imported rather than re-derived.  Nothing here
is named semantically: columns describe physical shape, container kind, decoded
width and raw bit positions.  The engine's semantic use of those bits is
established in ``docs/research/LOGX_TILE_PROVENANCE.md`` from instruction
evidence, not from this census.

The decoder is the project's single Webfoot container implementation
(``tools.webfoot.formats.webfoot_lz``); this module deliberately contains no
second compression implementation.
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
    ROOT_LAYER_SLOTS,
    TABLE_OFFSET,
    in_rom_any,
    in_rom_word,
    read_record,
    resolve_selector_1_roots,
)
from tools.webfoot.formats.webfoot_lz import ContainerError, unpack

#: The handler word that owns the chunk-pointer window this ticket reconstructs.
DOMINANT_HANDLER = 0x08008087

#: Bytes of one decoded dominant-form payload, as measured by the engine's own
#: fixed destination stride (``lsls r1,r5,#0xb`` at 0x08007BFE).
DECODED_PAYLOAD_BYTES = 0x800

#: Decoded words per payload at the engine's ``ldrh`` access width.
DECODED_PAYLOAD_WORDS = DECODED_PAYLOAD_BYTES // 2

#: Bytes per payload row: ``(row & 31) * 64`` at 0x0800806A.
ROW_STRIDE_BYTES = 64

#: Rows per payload: the engine masks the row index with ``& 31``.
ROW_COUNT = 32

#: Columns per payload at the engine's 2-byte element width.
COLUMN_COUNT = ROW_STRIDE_BYTES // 2

#: Bit ranges censused independently over the decoded words.
LOW_FIELD_MASK = 0x03FF
BIT_10_MASK = 0x0400
BIT_11_MASK = 0x0800

#: Container kinds the engine's decompressor entry point dispatches on.
CONTAINER_KINDS = (0, 1, 2)

#: Upper bound on the entries read from a ``root +0x4C`` bank table.  The table
#: in the canonical image is 187 entries and is followed by unrelated data, so
#: the walk stops at the first word that is not an aligned in-ROM address well
#: before this limit is reached.
BANK_TABLE_LIMIT = 4096


def _u16le(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "little")


def _u32le(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def classify_pointer(data: bytes, value: int) -> str:
    """Physical classification of one raw 32-bit array element."""
    if value == 0:
        return "null"
    if in_rom_word(value, len(data)):
        return "aligned_in_rom"
    if in_rom_any(value, len(data)):
        return "unaligned_in_rom"
    return "outside_rom"


def read_container(data: bytes, address: int) -> dict[str, Any]:
    """Header shape of the container at ``address`` without decoding it."""
    offset = address - ROM_BASE
    result: dict[str, Any] = {
        "address": address,
        "kind": None,
        "declared_size": None,
        "header_readable": False,
        "decode_error": None,
    }
    if offset < 0 or offset + 8 > len(data):
        result["decode_error"] = "header outside image"
        return result
    kind = _u32le(data, offset)
    result["kind"] = kind
    result["declared_size"] = _u32le(data, offset + 4)
    result["header_readable"] = True
    if kind not in CONTAINER_KINDS:
        result["decode_error"] = f"unsupported container kind {kind}"
    return result


def decode_container(data: bytes, address: int) -> bytes:
    """Decode one container through the project's Webfoot container decoder."""
    return unpack(data, address - ROM_BASE).data


def resolve_layer_references(data: bytes) -> list[dict[str, Any]]:
    """Every root-referenced layer record, one row per (map, slot) reference.

    Reuses the accepted ``LOGX-MAP-RENDER-001`` selector-1 root resolution and
    the accepted ``LOGX-LAYER-001`` record reader; nothing about the route is
    re-derived here.
    """
    rows: list[dict[str, Any]] = []
    for index, root in enumerate(resolve_selector_1_roots(data)):
        for slot in ROOT_LAYER_SLOTS:
            layer = _u32le(data, (root - ROM_BASE) + slot)
            record = read_record(data, layer)
            rows.append(
                {
                    "map_index": index,
                    "slot": slot,
                    "root": root,
                    "layer": layer,
                    "handler_raw": int(record.get("handler_raw", 0)),
                    "grid_x": int(record.get("byte_14_raw", 0)),
                    "grid_y": int(record.get("byte_15_raw", 0)),
                    "pointer_window": list(record.get("pointer_window", [])),
                }
            )
    return rows


def enumerate_array_elements(
    data: bytes, rows: list[dict[str, Any]], handler: int
) -> list[dict[str, Any]]:
    """Every ``+0x18`` array element of every reference whose handler matches.

    Only records carrying the requested handler word are dereferenced at all: a
    structurally different record's dimension bytes are not a chunk-grid
    product and walking them would read unrelated bytes.  The bound is the
    accepted ``record[+0x14] * record[+0x15]`` product.
    """
    elements: list[dict[str, Any]] = []
    for row in rows:
        if int(row["handler_raw"]) != handler:
            continue
        x = int(row["grid_x"])
        y = int(row["grid_y"])
        product = x * y
        for cell in range(product):
            value = _u32le(data, (int(row["layer"]) - ROM_BASE) + 0x18 + 4 * cell)
            elements.append(
                {
                    "map_index": int(row["map_index"]),
                    "slot": f"+0x{int(row['slot']):02x}",
                    "layer": int(row["layer"]),
                    "grid_x": x,
                    "grid_y": y,
                    "cell_index": cell,
                    "cell_x": cell % x if x else None,
                    "cell_y": cell // x if x else None,
                    "raw_value": value,
                    "classification": classify_pointer(data, value),
                }
            )
    return elements


def non_dominant_shape_census(data: bytes, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Physical shape of the non-dominant handlers, without dereferencing them."""
    census: dict[str, Any] = {}
    for handler in sorted({int(row["handler_raw"]) for row in rows}):
        if handler == DOMINANT_HANDLER:
            continue
        members = [row for row in rows if int(row["handler_raw"]) == handler]
        products = Counter(int(row["grid_x"]) * int(row["grid_y"]) for row in members)
        first_words = Counter(
            int(row["pointer_window"][0]) for row in members if row["pointer_window"]
        )
        first_word_classes = Counter(
            classify_pointer(data, value) for value in first_words
        )
        census[f"{handler:#010x}"] = {
            "references": len(members),
            "unique_records": len({int(row["layer"]) for row in members}),
            "grid_x_values": {str(k): v for k, v in sorted(Counter(int(row["grid_x"]) for row in members).items())},
            "grid_y_values": {str(k): v for k, v in sorted(Counter(int(row["grid_y"]) for row in members).items())},
            "dimension_product_values": {str(k): v for k, v in sorted(products.items())},
            "first_window_word_distinct_values": len(first_words),
            "first_window_word_classes": dict(sorted(first_word_classes.items())),
        }
    return census


def analyze_targets(
    data: bytes, rows: list[dict[str, Any]], elements: list[dict[str, Any]]
) -> dict[str, Any]:
    """Full ``+0x18`` element census plus per-unique-target resolution."""
    reference_values = [int(row["raw_value"]) for row in elements]
    non_null = [value for value in reference_values if value]
    unique_targets = sorted(set(non_null))
    reference_counts = Counter(non_null)
    by_class = Counter(str(row["classification"]) for row in elements)

    target_rows: dict[str, Any] = {}
    for address in unique_targets:
        container = read_container(data, address)
        entry: dict[str, Any] = {
            "address": address,
            "reference_count": reference_counts[address],
            "classification": classify_pointer(data, address),
            "kind": container["kind"],
            "declared_size": container["declared_size"],
            "decoded": False,
            "decode_error": container["decode_error"],
        }
        if container["kind"] in CONTAINER_KINDS and container["header_readable"]:
            try:
                decoded = decode_container(data, address)
            except ContainerError as exc:
                entry["decode_error"] = str(exc)
            else:
                words = [_u16le(decoded, 2 * i) for i in range(len(decoded) // 2)]
                entry["decoded"] = True
                entry["decoded_size"] = len(decoded)
                entry["decoded_word_count"] = len(words)
                entry["declared_matches_decoded"] = len(decoded) == container["declared_size"]
                entry["payload_sha256"] = hashlib.sha256(decoded).hexdigest()
                entry["first_words"] = [f"{word:#06x}" for word in words[:16]]
                entry["word_census"] = census_words(words)
        target_rows[f"{address:#010x}"] = entry

    declared_sizes = Counter(
        int(entry["declared_size"])
        for entry in target_rows.values()
        if entry["declared_size"] is not None
    )
    kinds = Counter(
        int(entry["kind"]) for entry in target_rows.values() if entry["kind"] is not None
    )

    # Per-reference grid shape, computed from the referenced record itself.
    cells: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for row in elements:
        cells.setdefault((int(row["map_index"]), int(row["layer"])), []).append(row)

    anomalies: dict[str, list[str]] = {
        "unaligned_in_rom": [],
        "outside_rom": [],
        "null_within_product": [],
        "null_then_non_null_within_product": [],
        "declared_size_not_0x800": [],
        "decode_failed": [],
        "empty_array_with_nonzero_product": [],
    }
    for row in elements:
        name = f"map{row['map_index']}{row['slot']}#{row['cell_index']}"
        if row["classification"] == "unaligned_in_rom":
            anomalies["unaligned_in_rom"].append(name)
        elif row["classification"] == "outside_rom":
            anomalies["outside_rom"].append(name)
    for key, group in sorted(cells.items()):
        ordered = sorted(group, key=lambda item: int(item["cell_index"]))
        if any(item["classification"] == "null" for item in ordered):
            anomalies["null_within_product"].append(f"map{key[0]}layer{key[1]:#010x}")
        seen_null = False
        for item in ordered:
            if item["classification"] == "null":
                seen_null = True
            elif seen_null:
                anomalies["null_then_non_null_within_product"].append(
                    f"map{key[0]}layer{key[1]:#010x}#{item['cell_index']}"
                )
                break
    for key, entry in sorted(target_rows.items()):
        if entry["declared_size"] is not None and int(entry["declared_size"]) != DECODED_PAYLOAD_BYTES:
            anomalies["declared_size_not_0x800"].append(key)
        if entry["kind"] in CONTAINER_KINDS and not entry["decoded"]:
            anomalies["decode_failed"].append(key)
    for row in rows:
        if int(row["handler_raw"]) == DOMINANT_HANDLER and int(row["grid_x"]) * int(row["grid_y"]) == 0:
            anomalies["empty_array_with_nonzero_product"].append(
                f"map{row['map_index']}+0x{int(row['slot']):02x}"
            )

    unique_dominant_records = {
        int(row["layer"]) for row in rows if int(row["handler_raw"]) == DOMINANT_HANDLER
    }
    dominant_references = [
        row for row in rows if int(row["handler_raw"]) == DOMINANT_HANDLER
    ]

    # The same two anomalies counted once per unique record rather than once per
    # reference, so a shared record is not counted several times.
    unique_record_anomalies = {
        "null_within_product": 0,
        "null_then_non_null_within_product": 0,
    }
    for layer in sorted(unique_dominant_records):
        record = read_record(data, layer)
        x = int(record["byte_14_raw"])
        y = int(record["byte_15_raw"])
        values = [
            _u32le(data, (layer - ROM_BASE) + 0x18 + 4 * cell) for cell in range(x * y)
        ]
        if any(value == 0 for value in values):
            unique_record_anomalies["null_within_product"] += 1
        seen_null = False
        for value in values:
            if value == 0:
                seen_null = True
            elif seen_null:
                unique_record_anomalies["null_then_non_null_within_product"] += 1
                break

    return {
        "summary": {
            "dominant_handler": f"{DOMINANT_HANDLER:#010x}",
            "dominant_record_references": len(dominant_references),
            "dominant_unique_records": len(unique_dominant_records),
            "unique_record_anomaly_counts": unique_record_anomalies,
            "array_element_references": len(elements),
            "array_element_references_null": by_class.get("null", 0),
            "array_element_references_aligned_in_rom": by_class.get("aligned_in_rom", 0),
            "array_element_references_unaligned_in_rom": by_class.get("unaligned_in_rom", 0),
            "array_element_references_outside_rom": by_class.get("outside_rom", 0),
            "non_null_array_element_references": len(non_null),
            "unique_targets": len(unique_targets),
            "shared_targets": sum(1 for value in reference_counts.values() if value > 1),
            "max_target_reference_count": max(reference_counts.values(), default=0),
            "target_min": f"{min(unique_targets):#010x}" if unique_targets else None,
            "target_max": f"{max(unique_targets):#010x}" if unique_targets else None,
            "all_targets_4_byte_aligned": all(value % 4 == 0 for value in unique_targets),
            "target_kind_census": {str(kind): count for kind, count in sorted(kinds.items())},
            "target_declared_size_census": {
                f"{size:#x}": count for size, count in sorted(declared_sizes.items())
            },
            "targets_decoded": sum(1 for entry in target_rows.values() if entry["decoded"]),
            "expected_words_per_target": DECODED_PAYLOAD_WORDS,
            "row_stride_bytes": ROW_STRIDE_BYTES,
            "row_count": ROW_COUNT,
            "column_count": COLUMN_COUNT,
        },
        "anomaly_counts": {key: len(value) for key, value in sorted(anomalies.items())},
        "anomalies": {key: value for key, value in anomalies.items() if value},
        "non_dominant_shape_census": non_dominant_shape_census(data, rows),
        "targets": target_rows,
        "references": [
            {
                "map_index": int(row["map_index"]),
                "slot": row["slot"],
                "layer": f"{int(row['layer']):#010x}",
                "grid_x": int(row["grid_x"]),
                "grid_y": int(row["grid_y"]),
                "cell_index": int(row["cell_index"]),
                "cell_x": row["cell_x"],
                "cell_y": row["cell_y"],
                "raw_value": f"{int(row['raw_value']):#010x}",
                "classification": row["classification"],
            }
            for row in elements
        ],
    }


def census_words(words: list[int]) -> dict[str, Any]:
    """Deterministic per-bit census over a flat list of decoded 16-bit words."""
    counter = Counter(words)
    low = [word & LOW_FIELD_MASK for word in words]
    bit_counts = {
        f"bit{bit}": sum(1 for word in words if word & (1 << bit)) for bit in range(16)
    }
    return {
        "entries": len(words),
        "distinct_raw_values": len(counter),
        "raw_min": min(words) if words else None,
        "raw_max": max(words) if words else None,
        "zero_entries": sum(1 for word in words if word == 0),
        "all_zero": bool(words) and all(word == 0 for word in words),
        "low_field_max": max(low) if low else None,
        "low_field_distinct": len(set(low)),
        "low_field_zero_entries": sum(1 for value in low if value == 0),
        "bit_occurrence": bit_counts,
        "bit10_set": sum(1 for word in words if word & BIT_10_MASK),
        "bit11_set": sum(1 for word in words if word & BIT_11_MASK),
        "bit10_and_bit11_set": sum(
            1 for word in words if (word & BIT_10_MASK) and (word & BIT_11_MASK)
        ),
        "high_nibble_census": {
            f"{value:#x}": count
            for value, count in sorted(Counter(word >> 12 for word in words).items())
        },
        "high_nibble_nonzero_entries": sum(1 for word in words if word >> 12),
        "top_raw_values": [
            {"value": value, "count": count} for value, count in counter.most_common(16)
        ],
    }


def analyze_chunks(targets: dict[str, Any]) -> dict[str, Any]:
    """Aggregate the per-target word censuses into a union census.

    Each payload is decoded exactly once, inside :func:`analyze_targets`, so
    this pass is pure aggregation over unique targets.  That is what keeps the
    headline counts free of shared-reference multiplication: every payload
    contributes its 1024 words once, no matter how many layer cells point at it.
    """
    per_chunk: dict[str, Any] = {}
    totals: Counter = Counter()
    low_field_max = 0
    bit10_total = 0
    bit11_total = 0
    zero_payloads: list[str] = []
    for key, entry in sorted(targets["targets"].items()):
        census = entry.get("word_census")
        if census is None:
            continue
        row = dict(census)
        row.update(
            {
                "address": int(entry["address"]),
                "reference_count": int(entry["reference_count"]),
                "decoded_size": int(entry["decoded_size"]),
                "payload_sha256": entry["payload_sha256"],
                "first_words": entry["first_words"],
            }
        )
        per_chunk[key] = row
        totals.update(census["bit_occurrence"])
        totals["entries"] += int(census["entries"])
        totals["zero_entries"] += int(census["zero_entries"])
        if census["low_field_max"] is not None:
            low_field_max = max(low_field_max, int(census["low_field_max"]))
        bit10_total += int(census["bit10_set"])
        bit11_total += int(census["bit11_set"])
        if census["all_zero"]:
            zero_payloads.append(key)

    payload_hashes = Counter(str(entry["payload_sha256"]) for entry in per_chunk.values())
    duplicated = {digest: count for digest, count in payload_hashes.items() if count > 1}
    union: dict[str, Any] = {
        "entries": totals["entries"],
        "zero_entries": totals["zero_entries"],
        "bit_occurrence": {f"bit{bit}": totals[f"bit{bit}"] for bit in range(16)},
        "bit10_set": bit10_total,
        "bit11_set": bit11_total,
        "low_field_max": low_field_max,
        "unique_payloads": len(per_chunk),
        "unique_payload_hashes": len(payload_hashes),
        "payload_hashes_shared_by_multiple_targets": len(duplicated),
        "targets_whose_payload_hash_is_shared": sum(duplicated.values()),
        "all_zero_payloads": sorted(zero_payloads),
        "payload_entry_count_census": {
            str(count): occurrences
            for count, occurrences in sorted(
                Counter(int(entry["entries"]) for entry in per_chunk.values()).items()
            )
        },
        "high_nibble_nonzero_payloads": sum(
            1 for entry in per_chunk.values() if int(entry["high_nibble_nonzero_entries"])
        ),
    }
    return {"union": union, "chunks": per_chunk}


def analyze_selectors(data: bytes, roots: list[int]) -> dict[str, Any]:
    """``root +0x48`` container decode plus the engine's prefix recurrence."""
    rows: list[dict[str, Any]] = []
    for index, root in enumerate(roots):
        entry: dict[str, Any] = {"map_index": index, "root": f"{root:#010x}"}
        pointer = _u32le(data, root - ROM_BASE + 0x48)
        entry["stream_pointer"] = f"{pointer:#010x}"
        entry["stream_classification"] = classify_pointer(data, pointer)
        bank_table = _u32le(data, root - ROM_BASE + 0x4C)
        entry["bank_table_pointer"] = f"{bank_table:#010x}"
        entry["bank_table_classification"] = classify_pointer(data, bank_table)
        if entry["stream_classification"] == "aligned_in_rom":
            container = read_container(data, pointer)
            entry["stream_kind"] = container["kind"]
            entry["stream_declared_size"] = container["declared_size"]
            try:
                decoded = decode_container(data, pointer)
            except ContainerError as exc:
                entry["stream_decoded"] = False
                entry["stream_decode_error"] = str(exc)
            else:
                raw = [_u16le(decoded, 2 * i) for i in range(len(decoded) // 2)]
                absolute = list(raw)
                for i in range(1, len(absolute)):
                    absolute[i] = (absolute[i] + absolute[i - 1] + 1) & 0xFFFF
                entry["stream_decoded"] = True
                entry["stream_decoded_size"] = len(decoded)
                entry["stream_word_count"] = len(raw)
                entry["raw_first_words"] = [f"{word:#06x}" for word in raw[:12]]
                entry["absolute_first_words"] = [f"{word:#06x}" for word in absolute[:12]]
                entry["absolute_min"] = min(absolute) if absolute else None
                entry["absolute_max"] = max(absolute) if absolute else None
                entry["distinct_banks"] = len({word >> 8 for word in absolute})
                entry["distinct_low_bytes"] = len({word & 0xFF for word in absolute})
                entry["bank_run_count"] = (
                    sum(
                        1
                        for i in range(1, len(absolute))
                        if (absolute[i] >> 8) != (absolute[i - 1] >> 8)
                    )
                    + (1 if absolute else 0)
                )
        rows.append(entry)

    decoded_rows = [row for row in rows if row.get("stream_decoded")]
    bank_pointer_counts = Counter(
        str(row["bank_table_pointer"])
        for row in rows
        if row["bank_table_classification"] == "aligned_in_rom"
    )
    bank_tables: dict[str, Any] = {}
    for key in sorted(bank_pointer_counts):
        address = int(key, 16)
        banks = []
        for index in range(BANK_TABLE_LIMIT):
            value = _u32le(data, address - ROM_BASE + 4 * index)
            if value == 0 or not in_rom_word(value, len(data)):
                break
            container = read_container(data, value)
            banks.append(
                {
                    "index": index,
                    "address": f"{value:#010x}",
                    "kind": container["kind"],
                    "declared_size": container["declared_size"],
                }
            )
        bank_tables[key] = {"address": address, "bank_count": len(banks), "banks": banks}

    return {
        "summary": {
            "maps": len(rows),
            "distinct_roots": len({row["root"] for row in rows}),
            "stream_pointer_outside_rom": sum(
                1 for row in rows if row["stream_classification"] == "outside_rom"
            ),
            "stream_pointer_unaligned_in_rom": sum(
                1 for row in rows if row["stream_classification"] == "unaligned_in_rom"
            ),
            "stream_decoded": len(decoded_rows),
            "stream_decode_failed": sum(
                1 for row in rows if row.get("stream_decoded") is False
            ),
            "stream_kind_census": {
                str(kind): count
                for kind, count in sorted(
                    Counter(
                        int(row["stream_kind"]) for row in decoded_rows if "stream_kind" in row
                    ).items()
                )
            },
            "stream_declared_size_min": min(
                (int(row["stream_declared_size"]) for row in decoded_rows), default=None
            ),
            "stream_declared_size_max": max(
                (int(row["stream_declared_size"]) for row in decoded_rows), default=None
            ),
            "all_stream_declared_sizes_even": all(
                int(row["stream_declared_size"]) % 2 == 0 for row in decoded_rows
            ),
            "word_count_min": min(
                (int(row["stream_word_count"]) for row in decoded_rows), default=None
            ),
            "word_count_max": max(
                (int(row["stream_word_count"]) for row in decoded_rows), default=None
            ),
            "distinct_bank_table_pointers": len(bank_pointer_counts),
            "bank_table_pointer_census": dict(sorted(bank_pointer_counts.items())),
            "recurrence": (
                "absolute[0] = raw[0]; "
                "absolute[i] = (raw[i] + absolute[i - 1] + 1) & 0xFFFF"
            ),
        },
        "bank_tables": bank_tables,
        "maps": rows,
    }


def analyze_tile_index(
    data: bytes, rows: list[dict[str, Any]], targets: dict[str, Any]
) -> dict[str, Any]:
    """Check every nonzero tile-index reference against the map's own tile loaders.

    A map's character region is populated by exactly two engine paths: the
    ``root +0x48`` selector stream, which writes one 64-byte tile per selector
    at ordinal ``i``, and the animated-tile records at ``root + 0x0C`` /
    ``root + 0x10``, each of which writes ``tile_count`` tiles starting at its
    own ``destination_tile``.  This function expands the bits 0-9 field of every
    nonzero entry of every dominant payload a map references and reports which
    of those two sources can supply it.  It is the measurement behind the
    "bits 0-9 are the tile ordinal" conclusion; it is a census, not a decoder.
    """
    roots = resolve_selector_1_roots(data)
    static_counts: dict[int, int] = {}
    animation_ranges: dict[int, list[tuple[int, int, int]]] = {}
    for index, root in enumerate(roots):
        stream = _u32le(data, root - ROM_BASE + 0x48)
        try:
            static_counts[index] = len(decode_container(data, stream)) // 2
        except ContainerError:
            static_counts[index] = 0
        count = _u32le(data, root - ROM_BASE + 0x0C)
        array = _u32le(data, root - ROM_BASE + 0x10)
        ranges: list[tuple[int, int, int]] = []
        if count and in_rom_word(array, len(data)):
            for record in range(count):
                pointer = _u32le(data, (array - ROM_BASE) + 4 * record)
                if not in_rom_word(pointer, len(data)):
                    continue
                tiles = data[pointer - ROM_BASE + 1]
                destination = _u16le(data, (pointer - ROM_BASE) + 2)
                if tiles:
                    ranges.append((destination, destination + tiles - 1, tiles))
        animation_ranges[index] = ranges

    animation_record_counts = Counter(len(ranges) for ranges in animation_ranges.values())

    nonzero = 0
    in_static = 0
    in_animation = 0
    uncovered: list[str] = []
    max_index = 0
    maps_with_animation_coverage = set()
    maps_with_references = set()
    for row in rows:
        if int(row["handler_raw"]) != DOMINANT_HANDLER:
            continue
        index = int(row["map_index"])
        maps_with_references.add(index)
        static = static_counts.get(index, 0)
        ranges = animation_ranges.get(index, [])
        x = int(row["grid_x"])
        y = int(row["grid_y"])
        for cell in range(x * y):
            value = _u32le(data, (int(row["layer"]) - ROM_BASE) + 0x18 + 4 * cell)
            if value == 0:
                continue
            entry = targets["targets"].get(f"{value:#010x}")
            if entry is None or not entry["decoded"]:
                continue
            payload = decode_container(data, value)
            for offset in range(0, len(payload), 2):
                word = payload[offset] | (payload[offset + 1] << 8)
                if word == 0:
                    continue
                tile = word & LOW_FIELD_MASK
                nonzero += 1
                if tile > max_index:
                    max_index = tile
                if tile < static:
                    in_static += 1
                    continue
                if any(low <= tile <= high for low, high, _ in ranges):
                    in_animation += 1
                    maps_with_animation_coverage.add(index)
                    continue
                if len(uncovered) < 64:
                    uncovered.append(
                        f"map{index}+0x{int(row['slot']):02x}#{cell}: tile {tile} "
                        f"(static {static}, animation {ranges})"
                    )

    return {
        "summary": {
            "maps_examined": len(roots),
            "maps_with_dominant_layer_references": len(maps_with_references),
            "nonzero_tile_index_references": nonzero,
            "references_supplied_by_the_static_selector_stream": in_static,
            "references_supplied_by_an_animation_destination_range": in_animation,
            "maps_using_an_animation_destination_range": len(maps_with_animation_coverage),
            "uncovered_references": len(uncovered),
            "uncovered_examples": uncovered,
            "global_max_tile_index": max_index,
            "static_selector_count_min": min(static_counts.values(), default=None),
            "static_selector_count_max": max(static_counts.values(), default=None),
            "animation_record_count_census": {
                str(count): occurrences
                for count, occurrences in sorted(animation_record_counts.items())
            },
            "max_animation_destination_end": max(
                (high for ranges in animation_ranges.values() for _, high, _ in ranges),
                default=None,
            ),
        }
    }


def build_report(data: bytes) -> dict[str, Any]:
    roots = resolve_selector_1_roots(data)
    rows = resolve_layer_references(data)
    elements = enumerate_array_elements(data, rows, DOMINANT_HANDLER)
    targets = analyze_targets(data, rows, elements)
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "rom_size": len(data),
        "table_offset": f"{TABLE_OFFSET:#x}",
        "record_size": f"{RECORD_SIZE:#x}",
        "record_count": RECORD_COUNT,
        "root_layer_slots": [f"+0x{slot:02x}" for slot in ROOT_LAYER_SLOTS],
        "dominant_handler": f"{DOMINANT_HANDLER:#010x}",
        "decoded_payload_bytes": DECODED_PAYLOAD_BYTES,
        "decoded_payload_words": DECODED_PAYLOAD_WORDS,
        "row_stride_bytes": ROW_STRIDE_BYTES,
        "row_count": ROW_COUNT,
        "column_count": COLUMN_COUNT,
        "target_summary": targets["summary"],
        "target_anomaly_counts": targets["anomaly_counts"],
        "target_anomalies": targets["anomalies"],
        "non_dominant_shape_census": targets["non_dominant_shape_census"],
        "chunks": analyze_chunks(targets),
        "selectors": analyze_selectors(data, roots),
        "tile_index": analyze_tile_index(data, rows, targets),
        "targets": targets["targets"],
        "references": targets["references"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, help="canonical Buu's Fury ROM (opened read-only)")
    parser.add_argument("--targets", action="store_true", help="include per-unique-target rows")
    parser.add_argument("--references", action="store_true", help="include per-array-element rows")
    parser.add_argument("--chunks", action="store_true", help="include per-payload word census")
    parser.add_argument("--selectors", action="store_true", help="include per-map selector rows")
    parser.add_argument(
        "--tile-index",
        action="store_true",
        help="include the bits 0-9 coverage analysis against the engine's tile loaders",
    )
    args = parser.parse_args(argv)

    data = load_rom(args.rom)
    report = build_report(data)
    if not args.targets:
        report.pop("targets")
    if not args.references:
        report.pop("references")
    if not args.chunks:
        report["chunks"].pop("chunks", None)
    if not args.selectors:
        report["selectors"].pop("maps", None)
    if not args.tile_index:
        report.pop("tile_index")
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
