"""Read-only regression evidence for LOGX-TILE-001.

Only findings independently established in
``docs/research/LOGX_TILE_PROVENANCE.md`` are encoded here.  Physical facts -
container shape, access width, row stride, entry counts, bit usage, the
recurrence, and the tile-index coverage invariant - are asserted.  Platform
conventions and this ticket's unresolved questions are deliberately not.

The suite skips cleanly when the private canonical ROM is not configured, and it
never writes to it.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tools.research.logx_layer_probe import (
    CANONICAL_SHA256,
    resolve_selector_1_roots,
)
from tools.research.logx_tile_probe import (
    COLUMN_COUNT,
    DECODED_PAYLOAD_BYTES,
    DECODED_PAYLOAD_WORDS,
    DOMINANT_HANDLER,
    ROW_COUNT,
    ROW_STRIDE_BYTES,
    analyze_selectors,
    analyze_targets,
    build_report,
    classify_pointer,
    decode_container,
    enumerate_array_elements,
    read_container,
    resolve_layer_references,
)
from tools.research.thumb_disasm import (
    find_field_extractions,
    linear_thumb,
    linear_thumb_wide,
)

ROM_BASE = 0x08000000

# --- locally verified constants of the canonical image -----------------------

EXPECTED_MAP_ENTRIES = 452
EXPECTED_DISTINCT_ROOTS = 421
EXPECTED_DOMINANT_REFERENCES = 1516
EXPECTED_DOMINANT_UNIQUE_RECORDS = 1420
EXPECTED_ARRAY_ELEMENTS = 4274
EXPECTED_ARRAY_ELEMENTS_NULL = 156
EXPECTED_ARRAY_ELEMENTS_ALIGNED = 4118
EXPECTED_UNIQUE_TARGETS = 3745
EXPECTED_SHARED_TARGETS = 165
EXPECTED_MAX_TARGET_REFERENCES = 10
EXPECTED_TARGET_MIN = 0x08179A50
EXPECTED_TARGET_MAX = 0x082B8BAC
EXPECTED_NULL_WITHIN_PRODUCT = 117
EXPECTED_NULL_THEN_NON_NULL = 85

EXPECTED_UNION_ENTRIES = 3_834_880
EXPECTED_UNION_ZERO_ENTRIES = 2_727_181
EXPECTED_UNION_DISTINCT_RAW = 2879
EXPECTED_UNION_RAW_MAX = 0x0F7B
EXPECTED_UNION_LOW_FIELD_MAX = 895
EXPECTED_BIT10_SET = 46_034
EXPECTED_BIT11_SET = 15_668
EXPECTED_BIT10_AND_BIT11 = 5239

#: Bit set counts over the union of the 3745 unique payloads.
EXPECTED_BIT_OCCURRENCE = {
    "bit0": 581_251,
    "bit1": 507_444,
    "bit2": 518_253,
    "bit3": 513_338,
    "bit4": 513_485,
    "bit5": 472_053,
    "bit6": 451_130,
    "bit7": 377_289,
    "bit8": 177_836,
    "bit9": 81_271,
    "bit10": 46_034,
    "bit11": 15_668,
    "bit12": 0,
    "bit13": 0,
    "bit14": 0,
    "bit15": 0,
}

EXPECTED_NONZERO_TILE_REFERENCES = 1_241_888
EXPECTED_TILE_REFERENCES_STATIC = 1_218_581
EXPECTED_TILE_REFERENCES_ANIMATED = 23_307
EXPECTED_MAPS_USING_ANIMATION = 178

EXPECTED_STREAM_DECODED = 452
EXPECTED_BANK_TABLE = 0x08179764
EXPECTED_BANK_TABLE_ENTRIES = 187
EXPECTED_MAX_BANK_INDEX = 186

#: Representative containers and streams measured in the provenance document.
REPRESENTATIVE_CHUNKS = {
    # first dominant target in the image: a tile-index ramp
    0x08179A50: [
        "0x0001", "0x0002", "0x0003", "0x0004",
        "0x0005", "0x0006", "0x0007", "0x0008",
        "0x0009", "0x000a", "0x000b", "0x000c",
        "0x000c", "0x000c", "0x000c", "0x000c",
    ],
    # map 39, layer +0x18, cell 0
    0x082934C4: [
        "0x0000", "0x0000", "0x0000", "0x0000",
        "0x0000", "0x0000", "0x0000", "0x0000",
        "0x0027", "0x0028", "0x0029", "0x002a",
        "0x002b", "0x0000", "0x0000", "0x0000",
    ],
}

#: Map 39's animated-tile destinations, sorted; the map's highest referenced
#: tile index (895) is exactly the end of one record's range.
MAP39_ANIMATION_RANGES = ((882, 892, 11), (893, 895, 3))


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    path = Path(
        os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
    )
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA256
    return data


@pytest.fixture(scope="module")
def rows(canonical_bytes: bytes) -> list[dict]:
    return resolve_layer_references(canonical_bytes)


@pytest.fixture(scope="module")
def elements(canonical_bytes: bytes, rows: list[dict]) -> list[dict]:
    return enumerate_array_elements(canonical_bytes, rows, DOMINANT_HANDLER)


@pytest.fixture(scope="module")
def targets(canonical_bytes: bytes, rows: list[dict], elements: list[dict]) -> dict:
    return analyze_targets(canonical_bytes, rows, elements)


@pytest.fixture(scope="module")
def report(canonical_bytes: bytes) -> dict:
    return build_report(canonical_bytes)


# --- section A: the +0x18 array element targets -------------------------------


def test_dominant_layer_array_census_is_stable(report: dict) -> None:
    summary = report["target_summary"]
    assert summary["dominant_handler"] == f"{DOMINANT_HANDLER:#010x}"
    assert summary["dominant_record_references"] == EXPECTED_DOMINANT_REFERENCES
    assert summary["dominant_unique_records"] == EXPECTED_DOMINANT_UNIQUE_RECORDS
    assert summary["array_element_references"] == EXPECTED_ARRAY_ELEMENTS
    assert summary["array_element_references_null"] == EXPECTED_ARRAY_ELEMENTS_NULL
    assert summary["array_element_references_aligned_in_rom"] == EXPECTED_ARRAY_ELEMENTS_ALIGNED
    # The measured fact: no dominant array element is a malformed pointer.
    assert summary["array_element_references_unaligned_in_rom"] == 0
    assert summary["array_element_references_outside_rom"] == 0
    # 156 + 4118 = 4274: the two classes partition the enumerated cells.
    assert (
        summary["array_element_references_null"]
        + summary["array_element_references_aligned_in_rom"]
        == summary["array_element_references"]
    )


def test_shared_target_arithmetic_is_separable(report: dict) -> None:
    summary = report["target_summary"]
    assert summary["unique_targets"] == EXPECTED_UNIQUE_TARGETS
    assert summary["shared_targets"] == EXPECTED_SHARED_TARGETS
    assert summary["max_target_reference_count"] == EXPECTED_MAX_TARGET_REFERENCES
    assert summary["unique_targets"] <= summary["non_null_array_element_references"]
    assert summary["shared_targets"] <= summary["unique_targets"]
    assert summary["target_min"] == f"{EXPECTED_TARGET_MIN:#010x}"
    assert summary["target_max"] == f"{EXPECTED_TARGET_MAX:#010x}"
    assert summary["all_targets_4_byte_aligned"] is True


def test_every_unique_target_is_a_kind_one_container_declaring_0x800(
    report: dict,
) -> None:
    summary = report["target_summary"]
    assert summary["target_kind_census"] == {"1": EXPECTED_UNIQUE_TARGETS}
    assert summary["target_declared_size_census"] == {"0x800": EXPECTED_UNIQUE_TARGETS}
    assert summary["targets_decoded"] == EXPECTED_UNIQUE_TARGETS
    assert report["target_anomaly_counts"].get("decode_failed", 0) == 0
    assert report["target_anomaly_counts"].get("declared_size_not_0x800", 0) == 0


def test_internal_null_anomaly_matches_the_prior_ticket_measurement(report: dict) -> None:
    counts = report["target_anomaly_counts"]
    assert counts["null_within_product"] == EXPECTED_NULL_WITHIN_PRODUCT
    assert counts["null_then_non_null_within_product"] == EXPECTED_NULL_THEN_NON_NULL
    # The same anomaly counted once per unique record, not once per reference.
    assert (
        report["target_summary"]["unique_record_anomaly_counts"]["null_within_product"]
        == EXPECTED_NULL_WITHIN_PRODUCT
    )


def test_the_probe_does_not_walk_non_dominant_handlers_as_chunk_grids(
    report: dict, elements: list[dict]
) -> None:
    """A structurally different record is reported by shape, never dereferenced.

    ``0x0800897B`` has 29 of 41 records with a zero dimension product and its
    first window word is out of ROM on three records; ``0x08007A41`` is the
    zero-dimension absent-layer placeholder with an all-null window.  Walking the
    dominant ``x*y`` bound over those would read unrelated bytes, so the probe's
    enumeration is restricted to the dominant handler and the reference list
    contains exactly the dominant references.
    """
    census = report["non_dominant_shape_census"]
    assert set(census) == {
        f"{0x0800897B:#010x}",
        f"{0x08007A41:#010x}",
        f"{0x08007B63:#010x}",
        f"{0x080088BD:#010x}",
    }
    absent = census[f"{0x08007A41:#010x}"]
    assert absent["references"] == 249
    assert absent["dimension_product_values"] == {"0": 249}
    assert absent["first_window_word_classes"] == {"null": 1}

    class_897b = census[f"{0x0800897B:#010x}"]
    assert class_897b["references"] == 41
    assert class_897b["dimension_product_values"]["0"] == 29

    assert all(
        row["classification"] in {"null", "aligned_in_rom", "unaligned_in_rom", "outside_rom"}
        for row in elements
    )
    # Every enumerated element carries a dominant record.
    assert report["target_summary"]["array_element_references"] == EXPECTED_ARRAY_ELEMENTS


# --- section D/F: entry width, endianness and the union census ----------------


def test_payload_shape_constants_are_the_engine_constants() -> None:
    assert DECODED_PAYLOAD_BYTES == 0x800
    assert DECODED_PAYLOAD_WORDS == 1024
    assert ROW_STRIDE_BYTES == 64
    assert COLUMN_COUNT == 32
    assert ROW_COUNT == 32
    assert ROW_STRIDE_BYTES // 2 == COLUMN_COUNT
    assert COLUMN_COUNT * ROW_COUNT * 2 == DECODED_PAYLOAD_BYTES


def test_union_entry_census(report: dict) -> None:
    union = report["chunks"]["union"]
    assert union["entries"] == EXPECTED_UNION_ENTRIES
    assert union["entries"] == EXPECTED_UNIQUE_TARGETS * DECODED_PAYLOAD_WORDS
    assert union["payload_entry_count_census"] == {"1024": EXPECTED_UNIQUE_TARGETS}
    assert union["zero_entries"] == EXPECTED_UNION_ZERO_ENTRIES
    assert union["all_zero_payloads"] == []
    assert union["unique_payloads"] == EXPECTED_UNIQUE_TARGETS
    assert union["unique_payload_hashes"] == EXPECTED_UNIQUE_TARGETS
    assert union["payload_hashes_shared_by_multiple_targets"] == 0


def test_bit_occurrence_census_over_unique_payloads(report: dict) -> None:
    union = report["chunks"]["union"]
    assert union["bit_occurrence"] == EXPECTED_BIT_OCCURRENCE
    assert union["bit10_set"] == EXPECTED_BIT10_SET
    assert union["bit11_set"] == EXPECTED_BIT11_SET
    assert union["bit_occurrence"]["bit10"] == EXPECTED_BIT10_SET
    assert union["bit_occurrence"]["bit11"] == EXPECTED_BIT11_SET
    # bits 12-15: zero on every entry of every unique payload.
    for bit in (12, 13, 14, 15):
        assert union["bit_occurrence"][f"bit{bit}"] == 0
    assert union["high_nibble_nonzero_payloads"] == 0
    assert union["low_field_max"] == EXPECTED_UNION_LOW_FIELD_MAX


def test_representative_chunk_words(canonical_bytes: bytes) -> None:
    for address, expected in REPRESENTATIVE_CHUNKS.items():
        container = read_container(canonical_bytes, address)
        assert container["kind"] == 1
        assert container["declared_size"] == DECODED_PAYLOAD_BYTES
        decoded = decode_container(canonical_bytes, address)
        assert len(decoded) == DECODED_PAYLOAD_BYTES
        words = [
            f"{int.from_bytes(decoded[2 * i : 2 * i + 2], 'little'):#06x}"
            for i in range(16)
        ]
        assert words == expected, f"{address:#010x}"


# --- section C/G: dimensions and the 8x8 pixel unit ---------------------------


def test_all_payloads_decode_to_exactly_the_engine_destination_stride(
    report: dict,
) -> None:
    """`lsls r1,r5,#0xB` fixes 0x800 bytes per installed slot at 0x08007BFE."""
    for key, entry in report["chunks"]["chunks"].items():
        assert entry["decoded_size"] == DECODED_PAYLOAD_BYTES, key
        assert entry["entries"] == DECODED_PAYLOAD_WORDS, key


def test_the_row_and_column_masks_are_the_engine_masks(canonical_bytes: bytes) -> None:
    """0x0800806A..0x08008072: ``(row & 31) * 64`` and ``(col & 31) * 2``.

    ``lsls r4,r5,#0x1B`` / ``lsrs r4,r4,#0x15`` is a 5-bit field scaled by 64;
    ``lsls r1,r1,#0x1B`` / ``lsrs r1,r1,#0x1A`` is the same 5-bit field scaled
    by 2.  Those two constants are the 32x32 dimensions.
    """
    chunk_loop = canonical_bytes[0x08007BEC - ROM_BASE : 0x08007C08 - ROM_BASE]
    assert chunk_loop == bytes.fromhex("a068a90040188069002807d0611920310d70e90209194c3135f09cfe")

    row_mask = canonical_bytes[0x0800806A - ROM_BASE : 0x08008072 - ROM_BASE]
    assert row_mask == bytes.fromhex("ec06640dc906890e")

    column_mask = canonical_bytes[0x0800806E - ROM_BASE : 0x08008074 - ROM_BASE]
    assert column_mask == bytes.fromhex("c906890ee318")

    word_load = canonical_bytes[0x08008074 - ROM_BASE : 0x08008078 - ROM_BASE]
    assert word_load == bytes.fromhex("595a0029")  # ldrh r1,[r3,r1] ; cmp r1,#0


def test_the_occupancy_test_is_a_zero_test(canonical_bytes: bytes) -> None:
    """The only engine test on a 16-bit entry value anywhere is ``!= 0``.

    ``0x08008074``: ``ldrh r1,[r3,r1]`` / ``cmp r1,#0`` / ``bne`` / ``movs r0,#0``.
    """
    assert (
        canonical_bytes[0x08008074 - ROM_BASE : 0x0800807E - ROM_BASE].hex()
        == "595a002901d10020dee7"
    )


def test_the_pixel_to_tile_shift_is_three_on_both_axes(canonical_bytes: bytes) -> None:
    """``asrs r1,r1,#3`` / ``asrs r5,r5,#3`` at 0x0800805C / 0x0800805E: 8 px."""
    assert (
        canonical_bytes[0x0800805C - ROM_BASE : 0x08008062 - ROM_BASE].hex()
        == "c910ed100091"
    )
    # ... and the chunk index is a pixel coordinate shifted by 8 (256 px).
    assert (
        canonical_bytes[0x08008022 - ROM_BASE : 0x08008026 - ROM_BASE].hex()
        == "24121b12"
    )


def test_the_character_writer_copies_64_bytes_per_tile(canonical_bytes: bytes) -> None:
    """0x08009C66..0x08009C74: ``movs r2,#0x40`` and ``(value & 0xFF) << 6``."""
    assert (
        canonical_bytes[0x08009C66 - ROM_BASE : 0x08009C74 - ROM_BASE].hex()
        == "085a009940220006800c4118301c"
    )


# --- section 9: the BG configuration the engine writes ------------------------


def test_the_engine_bg_control_word_is_8bpp_with_screen_bases_28_to_31(
    canonical_bytes: bytes,
) -> None:
    table = canonical_bytes[0x080716D8 - ROM_BASE : 0x080716D8 - ROM_BASE + 8]
    assert table == bytes.fromhex("801c801d801e801f")
    values = [
        int.from_bytes(table[2 * i : 2 * i + 2], "little") for i in range(4)
    ]
    assert values == [0x1C80, 0x1D80, 0x1E80, 0x1F80]
    for index, value in enumerate(values):
        assert value & 0x3 == 0  # priority 0
        assert (value >> 2) & 0x3 == 0  # character base 0 -> 0x06000000
        assert value & 0x80  # 8bpp
        assert (value >> 8) & 0x1F == 28 + index  # screen base 28..31
        assert (value >> 14) & 0x3 == 0  # 256x256


def test_the_vram_destination_matches_the_engine_screen_base(canonical_bytes: bytes) -> None:
    """0x08007DAE..0x08007DB4: ``0x0600E000 + object[+4] * 0x800``."""
    assert (
        canonical_bytes[0x08007DAE - ROM_BASE : 0x08007DB6 - ROM_BASE].hex()
        == "2879341cc0024718"
    )
    assert (
        int.from_bytes(canonical_bytes[0x08007E80 - ROM_BASE : 0x08007E84 - ROM_BASE], "little")
        == 0x0600E000
    )


def test_the_engine_writes_the_bg_control_registers(canonical_bytes: bytes) -> None:
    """0x080093E6..0x080093EA: ``r1 = 0x04000000`` then ``strh r2,[r1,#8]``."""
    assert (
        canonical_bytes[0x080093E6 - ROM_BASE : 0x080093EC - ROM_BASE].hex()
        == "012189060a81"
    )
    # ... and the table index is 8 * root[+0x3C] off 0x080716D8.
    assert (
        canonical_bytes[0x080093D6 - ROM_BASE : 0x080093DE - ROM_BASE].hex()
        == "e06b9c49c0001431"
    )
    assert (
        int.from_bytes(canonical_bytes[0x0800964C - ROM_BASE : 0x08009650 - ROM_BASE], "little")
        == 0x080716C4
    )


# --- section 10: the selector stream -----------------------------------------


def test_every_selector_stream_decodes(canonical_bytes: bytes) -> None:
    summary = build_selector_summary(canonical_bytes)
    assert summary["maps"] == EXPECTED_MAP_ENTRIES
    assert summary["distinct_roots"] == EXPECTED_DISTINCT_ROOTS
    assert summary["stream_decoded"] == EXPECTED_STREAM_DECODED
    assert summary["stream_decode_failed"] == 0
    assert summary["stream_pointer_outside_rom"] == 0
    assert summary["stream_pointer_unaligned_in_rom"] == 0
    assert summary["all_stream_declared_sizes_even"] is True
    assert summary["stream_kind_census"] == {"0": 2, "1": 450}
    assert summary["word_count_min"] == 2
    assert summary["word_count_max"] == 892


def build_selector_summary(canonical_bytes: bytes) -> dict:
    roots = resolve_selector_1_roots(canonical_bytes)
    return analyze_selectors(canonical_bytes, roots)["summary"]


def test_the_selector_recurrence_is_the_engine_recurrence(canonical_bytes: bytes) -> None:
    """0x08009C08..0x08009C12: ``absolute[i] = raw[i] + absolute[i-1] + 1``."""
    assert (
        canonical_bytes[0x08009C08 - ROM_BASE : 0x08009C12 - ROM_BASE].hex()
        == "db8b625a0130d2180132"
    )
    roots = resolve_selector_1_roots(canonical_bytes)
    report = analyze_selectors(canonical_bytes, roots)
    row = report["maps"][39]
    assert row["stream_pointer"] == f"{0x08294660:#010x}"
    assert row["stream_kind"] == 1
    assert row["stream_declared_size"] == 0x206
    assert row["stream_word_count"] == 259
    assert row["raw_first_words"][:4] == ["0x0000", "0x01bc", "0x0000", "0x0000"]
    assert row["absolute_first_words"][:6] == [
        "0x0000",
        "0x01bd",
        "0x01be",
        "0x01bf",
        "0x01c0",
        "0x01c1",
    ]
    # The recurrence is applied exactly once per element, in place.
    raw = row["raw_first_words"]
    absolute = row["absolute_first_words"]
    assert absolute[0] == raw[0]
    for i in range(1, 4):
        assert (
            int(absolute[i], 16)
            == (int(raw[i], 16) + int(absolute[i - 1], 16) + 1) & 0xFFFF
        )


def test_the_bank_table_is_the_descriptor_field_value(canonical_bytes: bytes) -> None:
    """All 452 roots hold ``0x08179764`` at ``+0x4C``; the table has 187 entries."""
    summary = build_selector_summary(canonical_bytes)
    assert summary["distinct_bank_table_pointers"] == 1
    assert summary["bank_table_pointer_census"] == {f"{EXPECTED_BANK_TABLE:#010x}": 452}

    offset = EXPECTED_BANK_TABLE - ROM_BASE
    entries = 0
    while True:
        value = int.from_bytes(
            canonical_bytes[offset + 4 * entries : offset + 4 * entries + 4], "little"
        )
        if not (ROM_BASE <= value <= ROM_BASE + len(canonical_bytes) - 4) or value % 4:
            break
        entries += 1
    assert entries == EXPECTED_BANK_TABLE_ENTRIES
    following = int.from_bytes(
        canonical_bytes[offset + 4 * entries : offset + 4 * entries + 4], "little"
    )
    assert following == 0x1  # not an aligned in-ROM pointer

    sizes = {}
    kinds = set()
    for index in range(entries):
        bank = int.from_bytes(
            canonical_bytes[offset + 4 * index : offset + 4 * index + 4], "little"
        )
        header = read_container(canonical_bytes, bank)
        kinds.add(header["kind"])
        sizes[header["declared_size"]] = sizes.get(header["declared_size"], 0) + 1
    assert kinds == {1}
    assert sizes == {0x4000: 186, 0x3C40: 1}


def test_the_largest_bank_index_used_matches_the_table_size(canonical_bytes: bytes) -> None:
    roots = resolve_selector_1_roots(canonical_bytes)
    max_bank = 0
    for root in roots:
        pointer = int.from_bytes(
            canonical_bytes[root - ROM_BASE + 0x48 : root - ROM_BASE + 0x4C], "little"
        )
        decoded = decode_container(canonical_bytes, pointer)
        words = [
            int.from_bytes(decoded[2 * i : 2 * i + 2], "little")
            for i in range(len(decoded) // 2)
        ]
        for i in range(1, len(words)):
            words[i] = (words[i] + words[i - 1] + 1) & 0xFFFF
        if words:
            max_bank = max(max_bank, max(word >> 8 for word in words))
    assert max_bank == EXPECTED_MAX_BANK_INDEX
    assert max_bank + 1 == EXPECTED_BANK_TABLE_ENTRIES


# --- section 8.3: bits 0-9 against both engine tile loaders -------------------


def test_every_tile_index_is_supplied_by_one_of_the_two_engine_loaders(
    report: dict,
) -> None:
    """The tile-index coverage invariant.

    Expanding every nonzero entry of every dominant payload a map references and
    comparing bits 0-9 against (a) the map's static selector ordinals and (b) its
    animated-tile destination ranges leaves no exception.
    """
    summary = report["tile_index"]["summary"]
    assert summary["nonzero_tile_index_references"] == EXPECTED_NONZERO_TILE_REFERENCES
    assert summary["uncovered_references"] == 0
    assert summary["uncovered_examples"] == []
    assert (
        summary["references_supplied_by_the_static_selector_stream"]
        + summary["references_supplied_by_an_animation_destination_range"]
        == summary["nonzero_tile_index_references"]
    )
    assert (
        summary["references_supplied_by_the_static_selector_stream"]
        == EXPECTED_TILE_REFERENCES_STATIC
    )
    assert (
        summary["references_supplied_by_an_animation_destination_range"]
        == EXPECTED_TILE_REFERENCES_ANIMATED
    )
    assert summary["maps_using_an_animation_destination_range"] == EXPECTED_MAPS_USING_ANIMATION
    assert summary["global_max_tile_index"] == EXPECTED_UNION_LOW_FIELD_MAX
    assert summary["max_animation_destination_end"] == EXPECTED_UNION_LOW_FIELD_MAX


def test_map39_animation_records_explain_its_high_tile_indices(
    canonical_bytes: bytes,
) -> None:
    """Map 39 has 259 static selectors but entries up to tile 895.

    The two animated-tile records at ``root+0x0C``/``root+0x10`` cover 882..892
    and 893..895, which is exactly the highest index the payloads use.
    """
    roots = resolve_selector_1_roots(canonical_bytes)
    root = roots[39]
    count = int.from_bytes(
        canonical_bytes[root - ROM_BASE + 0x0C : root - ROM_BASE + 0x10], "little"
    )
    array = int.from_bytes(
        canonical_bytes[root - ROM_BASE + 0x10 : root - ROM_BASE + 0x14], "little"
    )
    assert count == 2
    ranges = []
    for index in range(count):
        pointer = int.from_bytes(
            canonical_bytes[array - ROM_BASE + 4 * index : array - ROM_BASE + 4 * index + 4],
            "little",
        )
        tiles = canonical_bytes[pointer - ROM_BASE + 1]
        destination = int.from_bytes(
            canonical_bytes[pointer - ROM_BASE + 2 : pointer - ROM_BASE + 4], "little"
        )
        ranges.append((destination, destination + tiles - 1, tiles))
    assert tuple(sorted(ranges)) == MAP39_ANIMATION_RANGES
    assert max(high for _, high, _ in ranges) == EXPECTED_UNION_LOW_FIELD_MAX


# --- section 8.2/8.4: engine-side bit scans ----------------------------------


def test_no_engine_site_reads_the_control_bits_of_an_entry(canonical_bytes: bytes) -> None:
    """A raw halfword scan, so an undecodable neighbour cannot hide a site.

    The scan reports every ``lsls rd,rs,#a ; lsrs rd,rd,#b`` pair as
    ``(right_shift, width)``, covering both the plain mask idiom
    (``right_shift == 0``) and true field extraction.  A strict ``b > a`` test
    would never produce ``right_shift == 0`` and would make the mask half of
    this assertion vacuously true, which is why the pairing is verified
    separately in the portable synthetic suite.
    """
    extractions = find_field_extractions(canonical_bytes)
    assert len(extractions) == 1532

    by_key: dict[tuple[int, int], list[int]] = {}
    for item in extractions:
        by_key.setdefault((item.right_shift, item.width), []).append(item.address)

    # No site anywhere in the image isolates bit 10.
    assert by_key.get((10, 1), []) == []
    # No site masks a field of width 11, 13 or 14 (masks 0x7FF, 0x1FFF, 0x3FFF).
    assert by_key.get((0, 11), []) == []
    assert by_key.get((0, 13), []) == []
    assert by_key.get((0, 14), []) == []

    # The four `(11, 1)` sites all sit in the 0x0806E000..0x0806F000 table block,
    # which no BL/BLX encoding in the image reaches, and none is in map code.
    bit11 = by_key.get((11, 1), [])
    assert bit11 == [0x0806E682, 0x0806ECD8, 0x0806ECF4, 0x0806ED10]
    assert all(0x0806E000 <= address < 0x0806F000 for address in bit11)

    # No site isolates bits 12-15 inside the executable region.
    assert by_key.get((12, 4), []) == [
        0x0816A0E2,
        0x08780714,
        0x08781C16,
        0x08788D9E,
    ]

    # Nothing in the map/layer code region touches a field starting at bit 9..12.
    map_region = [
        item for item in extractions if 0x08007000 <= item.address < 0x0800A000
    ]
    assert len(map_region) == 29
    assert [item.right_shift for item in map_region if item.right_shift >= 9] == []
    assert max(item.width for item in map_region) <= 16
    # The widest mask used in the map/layer region is one byte.
    assert max(
        item.width for item in map_region if item.right_shift == 0
    ) == 16

    # The low-ten-bit mask does exist in the image, but only outside that region.
    low_ten = by_key.get((0, 10), [])
    assert len(low_ten) == 51
    assert not any(0x08007000 <= address < 0x0800A000 for address in low_ten)
    # Sampled sites are OAM attribute packing: `ldrh r0,[r0,#0xc]` masked to ten
    # bits and merged into an OAM attribute word at `[r3,#4]` / `[r4,#4]`.
    assert (
        canonical_bytes[0x0800ACEE - ROM_BASE : 0x0800ACFC - ROM_BASE].hex()
        == "80895968890a8005800d89020843"
    )


def test_no_mask_constant_for_the_high_nibble_or_the_low_field(canonical_bytes: bytes) -> None:
    """Exhaustive 4-byte-aligned search for the field masks over the whole image.

    The unaligned byte sequence ``00 f0 00 00`` does occur, but never as a
    literal-pool word, which is the only way the engine could load it as a mask.
    """
    length = len(canonical_bytes)
    for value in (0x0000F000, 0x00000FFF):
        needle = value.to_bytes(4, "little")
        offset = 0
        while True:
            found = canonical_bytes.find(needle, offset)
            if found < 0:
                break
            assert found % 4 != 0, f"{value:#010x} appears as an aligned word at {found:#x}"
            offset = found + 1
    words = {
        int.from_bytes(canonical_bytes[i : i + 4], "little")
        for i in range(0, length - 4, 4)
    }
    assert 0x0000F000 not in words
    assert 0x00000FFF not in words
    assert 0x000003FF in words  # the low-field mask does exist; it is unused for entries


def test_the_wide_sweep_decodes_the_two_halfword_instructions(
    canonical_bytes: bytes,
) -> None:
    """The legacy two-byte sweep cannot decode ``bl``; the wide window can."""
    wide = linear_thumb_wide(canonical_bytes, 0x08007B78, 0x08007D20)
    narrow = linear_thumb(canonical_bytes, 0x08007B78, 0x08007D20)
    assert wide.undecodable_halfwords == []
    assert len(wide.instructions) == 210
    assert narrow.undecodable_halfwords == [0x08007B86, 0x08007B88, 0x08007C04, 0x08007C06]
    assert len(narrow.instructions) == 208


# --- tooling and ROM safety ---------------------------------------------------


def test_pointer_classification_contract() -> None:
    data = bytes(0x1000)
    assert classify_pointer(data, 0) == "null"
    assert classify_pointer(data, ROM_BASE + 0x1000) == "outside_rom"
    assert classify_pointer(data, 0x09000000) == "outside_rom"
    assert classify_pointer(data, ROM_BASE + 2) == "unaligned_in_rom"
    assert classify_pointer(data, ROM_BASE + 4) == "aligned_in_rom"


def test_analysis_rejects_a_non_canonical_image(tmp_path: Path) -> None:
    import tools.research.logx_tile_probe as probe

    not_a_rom = tmp_path / "not-canonical.gba"
    not_a_rom.write_bytes(bytes(0x800000))
    with pytest.raises(SystemExit):
        probe.load_rom(not_a_rom)


def test_documented_module_invocation_emits_the_canonical_report(
    canonical_bytes: bytes, tmp_path: Path
) -> None:
    rom = tmp_path / "canonical.gba"
    rom.write_bytes(canonical_bytes)
    before = hashlib.sha256(rom.read_bytes()).hexdigest()
    result = subprocess.run(
        [sys.executable, "-m", "tools.research.logx_tile_probe", str(rom)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert rom.read_bytes() == canonical_bytes
    assert hashlib.sha256(rom.read_bytes()).hexdigest() == before
    payload = json.loads(result.stdout)
    assert payload["sha256"] == CANONICAL_SHA256
    assert payload["target_summary"]["unique_targets"] == EXPECTED_UNIQUE_TARGETS
    # The heavy detail blocks are opt-in.
    assert "targets" not in payload
    assert "references" not in payload
    assert "chunks" not in payload["chunks"]
    assert "maps" not in payload["selectors"]
    assert "tile_index" not in payload


def test_the_probe_refuses_a_non_canonical_file(tmp_path: Path) -> None:
    rom = tmp_path / "not-canonical.gba"
    rom.write_bytes(bytes(0x800000))
    result = subprocess.run(
        [sys.executable, "-m", "tools.research.logx_tile_probe", str(rom)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "refusing non-canonical ROM" in (result.stdout + result.stderr)
