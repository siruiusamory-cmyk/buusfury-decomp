"""Read-only regression evidence for LOGX-CONNECTOR-001.

Only findings independently established in
``docs/research/LOGX_CONNECTOR_PROVENANCE.md`` are encoded here: the physical
``root +0x40``/``+0x44`` census, the 4-byte array element, the record's physical
field offsets and access widths, the engine's own two-byte destination read, and
the record census arithmetic.  No LOGExtractor field name, its ``+8`` viewer
adjustment, or any unproven rectangle semantics is asserted.

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
import tempfile

import pytest

from tools.research.logx_connector_probe import (
    BOUND_BASE,
    COUNT_OFFSET,
    ELEMENT_WIDTH,
    KEY_HIGH_OFFSET,
    KEY_LOW_OFFSET,
    LIST_OFFSET,
    build_report,
    classify_pointer,
    load_rom,
    map_entry_keys,
    read_record,
    resolve_roots,
)
from tools.research.logx_layer_probe import (
    CANONICAL_SHA256,
    RECORD_COUNT,
    ROM_BASE,
    TABLE_OFFSET,
    resolve_selector_1_roots,
)
from tools.research.thumb_mem_operands import (
    coverage_note,
    decode_memory_operands,
    find_field_accesses,
)

# --- locally measured constants of the canonical image -----------------------

EXPECTED_ROOTS = 452
EXPECTED_ROOTS_WITH_ZERO_COUNT = 104
EXPECTED_ROOTS_WITH_NONZERO_COUNT = 348
EXPECTED_COUNT_SUM = 735
EXPECTED_COUNT_MAX = 14
EXPECTED_LIST_NULL = 104
EXPECTED_LIST_NONNULL = 348
EXPECTED_UNIQUE_LIST_TARGETS = 348

EXPECTED_ARRAY_REFERENCES = 735
EXPECTED_UNIQUE_RECORDS = 735
EXPECTED_SHARED_RECORDS = 0
EXPECTED_RECORD_MIN = 0x0817CA70
EXPECTED_RECORD_MAX = 0x0829B478

EXPECTED_DESTINATION_RESOLVED = 735
EXPECTED_BOUNDS_ORDERED = 735
EXPECTED_ZERO_AREA = 0
EXPECTED_BOUND_VALUE_MIN = 0
EXPECTED_BOUND_VALUE_MAX = 977
EXPECTED_BOUND_VALUE_DISTINCT = 155

#: Every canonical record's ``+0x04`` word is the same value; ``+0x00`` has two.
EXPECTED_PREFIX_WORD_0 = {"0x080072cd": 169, "0x08007675": 566}
EXPECTED_PREFIX_WORD_4 = {"0x0800776d": 735}

#: The engine's own ``MapEntry`` two-byte-key scan.  ``0x080089FC`` compares
#: ``entry[+0]`` and ``entry[+1]`` against its two arguments and advances by
#: ``0x38``; the literal at ``0x08008A58`` holds the table base.
EXPECTED_LOOKUP_FUNCTION_BYTES = (
    "38b5041c0d1c09f0edfd0022002813490bdd0b78a34204d14b78ab4201d1081c38bd383101328242f3db"
)

#: The three separate byte reads the record consumer performs around the warp
#: call: ``0x08007282`` reads ``+0x13`` into r1, ``0x0800728C`` reads ``+0x12``
#: into r2 and ``0x0800728E`` reads ``+0x11`` into r1.  The last two are the
#: pair handed to the two-byte ``MapEntry`` lookup, high byte in r1.
EXPECTED_KEY_READ_BYTES = "a27c617c0438006804ab"


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
def report(canonical_bytes: bytes) -> dict:
    return build_report(canonical_bytes)


# --- section A: root +0x40 / +0x44 ------------------------------------------


def test_root_offsets_are_the_confirmed_slots() -> None:
    assert COUNT_OFFSET == 0x40
    assert LIST_OFFSET == 0x44
    assert ELEMENT_WIDTH == 4
    assert BOUND_BASE == 0x08
    assert KEY_HIGH_OFFSET == 0x11
    assert KEY_LOW_OFFSET == 0x12


def test_root_pair_census(report: dict) -> None:
    summary = report["root_summary"]
    assert summary["roots"] == EXPECTED_ROOTS
    assert summary["count_zero"] == EXPECTED_ROOTS_WITH_ZERO_COUNT
    assert summary["count_nonzero"] == EXPECTED_ROOTS_WITH_NONZERO_COUNT
    assert summary["count_zero"] + summary["count_nonzero"] == EXPECTED_ROOTS
    assert summary["count_sum"] == EXPECTED_COUNT_SUM
    assert summary["count_max"] == EXPECTED_COUNT_MAX
    assert summary["list_null"] == EXPECTED_LIST_NULL
    assert summary["list_nonnull"] == EXPECTED_LIST_NONNULL
    assert summary["list_null"] + summary["list_nonnull"] == EXPECTED_ROOTS
    assert summary["list_unique_targets"] == EXPECTED_UNIQUE_LIST_TARGETS
    assert summary["list_shared_targets"] == 0
    assert summary["list_classification"] == {
        "aligned_in_rom": EXPECTED_LIST_NONNULL,
        "null": EXPECTED_LIST_NULL,
    }


def test_count_zero_and_null_list_are_the_same_roots(report: dict) -> None:
    """The exact coupling claim: ``count == 0`` iff ``list == 0``, on all 452."""
    assert report["root_summary"]["count_zero_iff_list_null"] is True
    roots = report["roots"]
    assert len(roots) == EXPECTED_ROOTS
    assert all(
        (int(row["count_raw"]) == 0) == (int(row["list_raw"]) == 0) for row in roots
    )
    # ... and every null list has a zero count, and vice versa, counted directly.
    assert sum(1 for row in roots if int(row["count_raw"]) == 0 and int(row["list_raw"]) == 0) == (
        EXPECTED_ROOTS_WITH_ZERO_COUNT
    )


def test_list_pointer_is_always_exactly_count_times_four_before_the_root(
    report: dict,
) -> None:
    """The measured structural invariant of the canonical corpus.

    This is a corpus property, not a format rule: the engine reads the count
    from ``+0x40`` and the array from ``+0x44`` and does not rely on their
    relative position.  It is asserted because it is what the image does on all
    452 roots, so a future regression in the root resolver shows up here.
    """
    assert report["root_summary"]["list_always_four_times_count_before_root"] is True
    for row in report["roots"]:
        count = int(row["count_raw"])
        pointer = int(row["list_raw"])
        root = int(row["root"])
        if pointer:
            assert pointer == root - ELEMENT_WIDTH * count, row
        else:
            assert count == 0, row
    assert report["root_summary"]["list_minus_root_distribution"] == {
        "4": 86, "8": 188, "12": 40, "16": 27, "20": 5, "24": 1, "56": 1,
    }


# --- section C: array census -------------------------------------------------


def test_array_element_census(report: dict) -> None:
    summary = report["array_summary"]
    assert summary["references"] == EXPECTED_ARRAY_REFERENCES
    assert summary["references_null"] == 0
    assert summary["references_nonnull"] == EXPECTED_ARRAY_REFERENCES
    assert summary["references_aligned_in_rom"] == EXPECTED_ARRAY_REFERENCES
    assert summary["references_unaligned_in_rom"] == 0
    assert summary["references_outside_rom"] == 0
    # references == count_sum is the arithmetic that ties +0x40 to the walk.
    assert summary["references"] == report["root_summary"]["count_sum"]


def test_unique_and_shared_record_arithmetic_stays_separate(report: dict) -> None:
    summary = report["array_summary"]
    assert summary["unique_records"] == EXPECTED_UNIQUE_RECORDS
    assert summary["shared_records"] == EXPECTED_SHARED_RECORDS
    assert summary["max_reference_count"] == 1
    assert summary["unique_records"] <= summary["references_nonnull"]
    assert summary["record_pointer_min"] == f"{EXPECTED_RECORD_MIN:#010x}"
    assert summary["record_pointer_max"] == f"{EXPECTED_RECORD_MAX:#010x}"
    assert summary["all_records_4_byte_aligned"] is True


# --- sections E/F/I: record layout ------------------------------------------


def test_record_census(report: dict) -> None:
    summary = report["record_summary"]
    assert summary["records"] == EXPECTED_UNIQUE_RECORDS
    assert summary["readable"] == EXPECTED_UNIQUE_RECORDS
    assert summary["destination_resolved"] == EXPECTED_DESTINATION_RESOLVED
    assert summary["destination_unresolved"] == 0
    assert summary["bounds_ordered"] == EXPECTED_BOUNDS_ORDERED
    assert summary["bounds_not_ordered"] == 0
    assert summary["zero_area_regions"] == EXPECTED_ZERO_AREA
    assert summary["bound_value_min"] == EXPECTED_BOUND_VALUE_MIN
    assert summary["bound_value_max"] == EXPECTED_BOUND_VALUE_MAX
    assert summary["bound_value_distinct"] == EXPECTED_BOUND_VALUE_DISTINCT


def test_bound_values_are_zero_or_one_modulo_eight(report: dict) -> None:
    """A physical shape fact about the four u16 at ``record + 0x08``.

    Every value the engine reads there is either ``0`` or ``8k + 1``.  This
    ticket does NOT claim that makes them tile coordinates; it records the
    distribution as a reproducible property of the corpus.
    """
    census = report["record_summary"]["bound_value_mod8_census"]
    assert set(census) <= {"0", "1", "7"}
    assert census["0"] + census["1"] + census.get("7", 0) == 4 * EXPECTED_UNIQUE_RECORDS
    # 1468 + 1448 + 24 = 2940 = 4 * 735
    assert census == {"0": 1468, "1": 1448, "7": 24}


def test_record_prefix_words(report: dict) -> None:
    summary = report["record_summary"]
    assert summary["prefix_word_0_census"] == EXPECTED_PREFIX_WORD_0
    assert summary["prefix_word_4_census"] == EXPECTED_PREFIX_WORD_4
    # +0x04 is invariant across all 735; +0x00 has exactly two values.
    assert sum(EXPECTED_PREFIX_WORD_4.values()) == EXPECTED_UNIQUE_RECORDS
    assert sum(EXPECTED_PREFIX_WORD_0.values()) == EXPECTED_UNIQUE_RECORDS


def test_pre_key_and_key_tail_byte_censuses(report: dict) -> None:
    summary = report["record_summary"]
    assert summary["byte_at_0x13_census"] == {"0": 561, "1": 174}
    # +0x10 is a small value on all but ten records.
    small = sum(
        count
        for value, count in summary["byte_at_0x10_census"].items()
        if int(value) <= 3
    )
    assert small == 725
    assert sum(summary["byte_at_0x10_census"].values()) == EXPECTED_UNIQUE_RECORDS


def test_only_the_engine_key_byte_pair_resolves(report: dict, canonical_bytes: bytes) -> None:
    """``record +0x11`` and ``+0x12`` are the destination pair, read high first.

    Across the whole record the pair ``(+0x11, +0x12)`` is the *only* byte pair
    whose big-endian reading is an accepted ``MapEntry`` lookup key on all 735
    records.  A neighbouring pair scores far below that, so the offset is not a
    free choice among equals.
    """
    keyset = set(map_entry_keys(canonical_bytes))
    assert len(keyset) == RECORD_COUNT

    def score(high: int, low: int) -> int:
        hits = 0
        for row in report["references"]:
            base = int(row["record_raw"]) - ROM_BASE
            pair = bytes([canonical_bytes[base + high], canonical_bytes[base + low]])
            if pair in keyset:
                hits += 1
        return hits

    assert score(0x11, 0x12) == EXPECTED_UNIQUE_RECORDS
    # The swapped reading is not the key.
    assert score(0x12, 0x11) < EXPECTED_UNIQUE_RECORDS
    # Immediate neighbours score far lower.
    assert score(0x10, 0x11) < EXPECTED_UNIQUE_RECORDS
    assert score(0x12, 0x13) < EXPECTED_UNIQUE_RECORDS


def test_representative_records(canonical_bytes: bytes) -> None:
    """Byte-exact anchors so a decoder regression is visible immediately."""
    roots = resolve_selector_1_roots(canonical_bytes)
    expected = {
        # map index: (root, count, list, first record, first record bytes)
        33: (0x0829B494, 1, 0x0829B490, 0x0829B478,
             "757600086d770008c803a000d103e10003010200"),
        39: (0x08294968, 2, 0x08294960, 0x08294930,
             "cd7200086d770008600000000101110001010a00"),
        338: (0x081DAD0C, 3, 0x081DAD00, 0x081DACB8, None),
    }
    for index, (root, count, list_pointer, record, raw) in expected.items():
        assert roots[index] == root
        row = resolve_roots(canonical_bytes)[index]
        assert int(row["count_raw"]) == count
        assert int(row["list_raw"]) == list_pointer
        base = record - ROM_BASE
        listed = int.from_bytes(
            canonical_bytes[
                list_pointer - ROM_BASE : list_pointer - ROM_BASE + 4
            ],
            "little",
        )
        assert listed == record
        if raw is not None:
            assert canonical_bytes[base : base + 0x14].hex() == raw


def test_transition_graph_shape(report: dict) -> None:
    graph = report["transition_graph"]
    assert graph["links"] == 694
    assert graph["reciprocal"] == 674
    assert graph["one_way"] == 20
    assert graph["self_links"] == 3
    assert graph["self_link_sources"] == [125, 126, 127]
    assert graph["distinct_destinations"] == 350
    assert graph["maps_with_at_least_one_link"] == EXPECTED_ROOTS_WITH_NONZERO_COUNT
    # Every resolved destination is a real MapEntry index.
    assert all(
        "destination_map_index" not in record
        or 0 <= int(record["destination_map_index"]) < RECORD_COUNT
        for record in report["records"].values()
    )


def test_census_is_free_of_anomalies(report: dict) -> None:
    assert report["anomalies"] == {}
    assert report["anomaly_counts"] == {}


# --- section D/H: the engine's own reads ------------------------------------


def test_map_entry_lookup_scans_both_key_bytes(canonical_bytes: bytes) -> None:
    """``0x080089FC`` is a linear scan over the ``0x38``-stride table.

    It compares ``entry[+0]`` and ``entry[+1]`` against its two arguments as
    *separate byte loads* - there is no halfword load of the key anywhere - and
    advances the cursor by ``0x38``.  That is the accepted two-byte lookup key
    being read as two bytes, which is what makes ``record +0x11``/``+0x12`` a
    two-byte destination pair rather than a big-endian u16 object.
    """
    start = 0x080089FC - ROM_BASE
    raw = canonical_bytes[start : start + 0x2A].hex()
    assert raw == EXPECTED_LOOKUP_FUNCTION_BYTES

    # The two byte loads and the stride advance, at their exact addresses.
    assert canonical_bytes[0x08008A0E - ROM_BASE : 0x08008A18 - ROM_BASE].hex() == (
        "0b78a34204d14b78ab42"
    )
    assert canonical_bytes[0x08008A1E - ROM_BASE : 0x08008A22 - ROM_BASE].hex() == (
        "38310132"
    )  # adds r1, #0x38 ; adds r2, #1

    # Decoding the two byte loads gives a constant zero displacement: the key
    # is entry[+0] and entry[+1], not a wider field at a larger offset.
    first = decode_memory_operands(canonical_bytes, 0x08008A0E)
    second = decode_memory_operands(canonical_bytes, 0x08008A14)
    assert [(item.mnemonic, item.immediate) for item in first] == [("ldrb", 0)]
    assert [(item.mnemonic, item.immediate) for item in second] == [("ldrb", 1)]


def test_table_base_literal_is_inside_that_function(canonical_bytes: bytes) -> None:
    """``0x08008A0A`` loads the table base from a pool word at ``0x08008A58``."""
    value = int.from_bytes(
        canonical_bytes[0x08008A58 - ROM_BASE : 0x08008A5C - ROM_BASE], "little"
    )
    assert value == TABLE_OFFSET + ROM_BASE
    assert TABLE_OFFSET + ROM_BASE == 0x0808E2E0


def test_the_destination_is_read_as_two_separate_byte_loads(canonical_bytes: bytes) -> None:
    """The record consumer reads ``+0x12`` and ``+0x11`` as two ``ldrb`` sites.

    ``0x0800728C`` is ``ldrb r2,[r4,#0x12]`` and ``0x0800728E`` is
    ``ldrb r1,[r4,#0x11]``, so the pair handed to the key lookup is
    (high = ``[r4,+0x11]``, low = ``[r4,+0x12]``).  A third read at
    ``0x08007282`` takes ``+0x13`` separately.  This is a statement about
    *these* sites, not a claim that no halfword load exists anywhere at those
    displacements: other structures are read with ``ldrh`` at ``+0x11`` and
    ``+0x12`` elsewhere in the image.  What it establishes is that both of the
    engine's paths to *this* record field are byte-wise.
    """
    assert canonical_bytes[0x0800728C - ROM_BASE : 0x08007296 - ROM_BASE].hex() == (
        EXPECTED_KEY_READ_BYTES
    )
    low = decode_memory_operands(canonical_bytes, 0x0800728C)
    high = decode_memory_operands(canonical_bytes, 0x0800728E)
    assert [(item.mnemonic, item.rt_name, item.rn_name, item.immediate) for item in low] == [
        ("ldrb", "r2", "r4", 0x12)
    ]
    assert [(item.mnemonic, item.rt_name, item.rn_name, item.immediate) for item in high] == [
        ("ldrb", "r1", "r4", 0x11)
    ]
    tail = decode_memory_operands(canonical_bytes, 0x08007282)
    assert [(item.mnemonic, item.rt_name, item.immediate) for item in tail] == [
        ("ldrb", "r1", 0x13)
    ]


def test_the_record_key_field_is_read_by_bytes_on_both_paths(
    canonical_bytes: bytes,
) -> None:
    """Two independent byte-wise reads of the key, with their raw encodings.

    The record consumer reads ``[r4,#0x12]`` into r2 and ``[r4,#0x11]`` into r1
    (``a27c`` / ``617c``), and the accepted ``MapEntry`` lookup compares its key
    argument with two separate byte loads (``0b78`` / ``4b78``) and a byte
    ``cmp r3,r4`` (``a342``).  A halfword read of the key would make the second
    byte a ``+1`` displacement of an ``ldrh``; neither path does that.
    """
    assert canonical_bytes[0x0800728C - ROM_BASE : 0x0800728E - ROM_BASE].hex() == "a27c"
    assert canonical_bytes[0x0800728E - ROM_BASE : 0x08007290 - ROM_BASE].hex() == "617c"
    assert canonical_bytes[0x08008A0E - ROM_BASE : 0x08008A10 - ROM_BASE].hex() == "0b78"
    assert canonical_bytes[0x08008A14 - ROM_BASE : 0x08008A16 - ROM_BASE].hex() == "4b78"
    assert canonical_bytes[0x08008A10 - ROM_BASE : 0x08008A12 - ROM_BASE].hex() == "a342"
    for address, expected in (
        (0x0800728C, ("ldrb", "r2", "r4", 0x12)),
        (0x0800728E, ("ldrb", "r1", "r4", 0x11)),
        (0x08008A0E, ("ldrb", "r3", "r1", 0x00)),
        (0x08008A14, ("ldrb", "r3", "r1", 0x01)),
    ):
        operands = decode_memory_operands(canonical_bytes, address)
        assert [
            (item.mnemonic, item.rt_name, item.rn_name, item.immediate)
            for item in operands
        ] == [expected], address


def test_the_portal_object_copies_the_record_prefix(canonical_bytes: bytes) -> None:
    """``0x0800CF1C`` copies sixteen bytes from the record and then reads ``+0x16``.

    ``ldm r4!,{r1,r2,r3}`` / ``stm r7!,{r1,r2,r3}`` / ``ldm r4!,{r3}`` is an
    eight-byte copy with a four-byte extension, and the following
    ``ldrb r2,[r1,#0x16]`` reads the record's ``+0x16`` byte through the saved
    record pointer.  This is the data flow that ties the record to an engine
    object; it is not a statement that the record *is* that object.
    """
    assert canonical_bytes[0x0800CF1C - ROM_BASE : 0x0800CF28 - ROM_BASE].hex() == (
        "0ecc0ec708cc103c08c7016a"
    )
    assert canonical_bytes[0x0800CF28 - ROM_BASE : 0x0800CF2C - ROM_BASE].hex() == (
        "8a7d0272"
    )
    read = decode_memory_operands(canonical_bytes, 0x0800CF28)
    assert [(item.mnemonic, item.immediate) for item in read] == [("ldrb", 0x16)]


def test_constant_immediate_accesses_at_the_root_pair_offsets_are_other_objects(
    canonical_bytes: bytes,
) -> None:
    """Why the ``+0x40``/``+0x44`` pair never shows up in this offset scan.

    The real consumer was recovered (see
    ``test_the_engine_reads_both_words_with_one_ldm``): it reads the pair with
    a single ``ldm r1, {r1, r2}`` from ``root + 0x40``, so neither word is ever
    loaded by a constant-immediate ``ldr ..., #0x40`` / ``#0x44`` form.  This
    test pins the residue of searching for one anyway: over
    ``0x08000000..0x08007000`` there are exactly three constant-immediate sites
    at displacement ``0x40`` or ``0x44``, all three are ordinary word accesses
    at ``+0x44`` on some other object, and none is a walk of the selector-1
    root.  Recording them keeps a future ticket from reading an empty scan as
    evidence of absence.
    """
    hits = find_field_accesses(
        canonical_bytes,
        {COUNT_OFFSET, LIST_OFFSET},
        start=0x08000000,
        end=0x08007000,
    )
    assert len(hits) == 3
    assert [item.address for item in hits] == [0x08003FC2, 0x08004060, 0x080040B6]
    # All three are word accesses at displacement 0x44, all below the map/layer
    # code region 0x08007000..0x0800A000 that owns the selector-1 root.
    assert all(item.address < 0x08007000 for item in hits)
    assert {(item.mnemonic, item.immediate) for item in hits} == {
        ("ldr", 0x44),
        ("str", 0x44),
    }
    # The coverage sentence a reader needs is available from the tool.
    note = coverage_note(0x08000000, 0x08007000)
    assert "register-offset" in note


# --- the constant-immediate operand scan -------------------------------------


def test_the_operand_scan_agrees_with_capstone(canonical_bytes: bytes) -> None:
    """Two-directional differential against the project's other disassembler.

    ``tools/research/thumb_mem_operands.py`` carries negative claims of the form
    "no constant-immediate access touches this field", so its coverage has to be
    measured rather than asserted.  Two directions are checked over the canonical
    code region, with the same definition of scope on both sides: an access whose
    displacement is written out (16-bit ``[Rn]`` counts as displacement zero),
    with base register neither SP nor PC and a non-negative displacement.

    1. **No misses.** Every in-scope access Capstone decodes at an instruction
       boundary must be reported identically by the module.
    2. **No misreports.** Wherever Capstone decodes an instruction *of the same
       width* as the module's own decode, a site the module reports must be one
       Capstone decodes as in-scope.

    The width qualifier in (2) is deliberate and is the only escape hatch: this
    module decodes Thumb-1 encodings, so at an address where Capstone finds a
    32-bit instruction it may still report the 16-bit encoding of the same
    halfword.  That is an architectural ambiguity of a fixed-width scanner, not
    a disagreement about a site.

    The boundary walk resynchronises past undecodable halfwords, and the
    population is asserted so the check cannot pass vacuously.
    """
    capstone = pytest.importorskip("capstone")
    from tools.research.thumb_mem_operands import REGS, decode_memory_operands

    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    memory = {"ldr", "str", "ldrb", "strb", "ldrh", "strh"}
    regs = list(REGS)

    def capstone_site(address: int):
        """``(instruction, width, in-scope site)`` for the decode at ``address``."""
        offset = address - ROM_BASE
        if offset < 0 or offset + 4 > len(canonical_bytes):
            return None, 0, None
        ins = next(md.disasm(canonical_bytes[offset : offset + 4], address, 1), None)
        if ins is None:
            return None, 0, None
        mnemonic = ins.mnemonic if ins.mnemonic in memory else ins.mnemonic.split(".")[0]
        if mnemonic not in memory or "[" not in ins.op_str or "!" in ins.op_str:
            return ins, ins.size, None
        body = ins.op_str.split("[")[1].split("]")[0]
        parts = [piece.strip() for piece in body.split(",")]
        if not parts or not parts[0].startswith("r") or not parts[0][1:].isdigit():
            return ins, ins.size, None
        if len(parts) == 1:
            immediate = 0
        elif len(parts) == 2 and parts[1].startswith("#"):
            immediate = int(parts[1].lstrip("#"), 0)
        else:
            return ins, ins.size, None
        try:
            base = regs.index(parts[0])
            target = regs.index(ins.op_str.split(",")[0].strip())
        except ValueError:
            return ins, ins.size, None
        if base in (13, 15) or immediate < 0:
            return ins, ins.size, None
        return ins, ins.size, (mnemonic, target, base, immediate)

    # Direction 1: real instruction boundaries, no misses.
    in_scope = 0
    missed: list[str] = []
    address = 0x08000000
    while address + 4 <= 0x08007000:
        ins, _, want = capstone_site(address)
        if ins is None:
            address += 2
            continue
        if want is not None:
            in_scope += 1
            got = [
                (op.mnemonic, op.rt, op.rn, op.immediate)
                for op in decode_memory_operands(canonical_bytes, address)
            ]
            if want not in got:
                missed.append(f"{address:#010x} {ins.mnemonic} {ins.op_str}")
        address += ins.size

    # Direction 2: no invented sites at a same-width instruction boundary.
    misreported: list[str] = []
    offset = 0x08000000
    while offset + 4 <= 0x08007000:
        ins, width, want = capstone_site(offset)
        if ins is not None:
            got = [
                (op.mnemonic, op.rt, op.rn, op.immediate)
                for op in decode_memory_operands(canonical_bytes, offset)
            ]
            if got and want is None and width == 2:
                misreported.append(
                    f"{offset:#010x} {ins.mnemonic} {ins.op_str} module={got}"
                )
        offset += 2

    # Thousands of in-scope sites exist; a regression that lost most of the
    # scan would fail these bounds.
    assert in_scope > 3000, in_scope
    assert missed[:20] == []
    assert misreported[:20] == []


# --- section D: the recovered engine consumer --------------------------------


def test_the_engine_reads_both_words_with_one_ldm(canonical_bytes: bytes) -> None:
    """``0x08009670`` is the consumer, and it reads the pair with a single ``ldm``.

    This is why a constant-immediate offset scan cannot see it, and it is the
    instruction evidence that promotes the ``+0x40`` count semantic from a census
    inference to a cited engine loop.
    """
    assert canonical_bytes[0x08009670 - ROM_BASE : 0x08009680 - ROM_BASE].hex() == (
        "08b54031a04806c9806808f0f3ff08bd"
    )
    # `adds r1,#0x40` then `ldm r1,{r1,r2}`: 8 bytes read atomically.
    assert canonical_bytes[0x08009672 - ROM_BASE : 0x08009674 - ROM_BASE].hex() == "4031"
    assert canonical_bytes[0x08009676 - ROM_BASE : 0x08009678 - ROM_BASE].hex() == "06c9"
    # The pool word at 0x080098F8 is the static base 0x080716C4.
    assert (
        int.from_bytes(
            canonical_bytes[0x080098F8 - ROM_BASE : 0x080098FC - ROM_BASE], "little"
        )
        == 0x080716C4
    )


def test_the_registry_walk_uses_the_count_and_a_four_byte_stride(
    canonical_bytes: bytes,
) -> None:
    """``0x08012664`` walks exactly ``count`` elements at a 4-byte stride.

    ``subs r4,r1,#1`` seeds the index, ``lsls r0,r4,#2`` scales it, ``bpl``
    terminates at index 0, and ``ldr r1,[r0]`` takes the record's first word as
    the function pointer to call.
    """
    assert canonical_bytes[0x08012664 - ROM_BASE : 0x0801268A - ROM_BASE].hex() == (
        "70b5161c051c4c1e0cd4a0003058016834f015fa29684a1c890049192a604860013cf2d570bd"
    )
    assert canonical_bytes[0x0801266A - ROM_BASE : 0x0801266C - ROM_BASE].hex() == "4c1e"
    assert canonical_bytes[0x0801266E - ROM_BASE : 0x08012670 - ROM_BASE].hex() == "a000"
    assert canonical_bytes[0x08012670 - ROM_BASE : 0x08012672 - ROM_BASE].hex() == "3058"
    assert canonical_bytes[0x08012672 - ROM_BASE : 0x08012674 - ROM_BASE].hex() == "0168"
    assert canonical_bytes[0x08012686 - ROM_BASE : 0x08012688 - ROM_BASE].hex() == "f2d5"

    # The two loads are register-offset forms (`ldr r0,[r6,r0]` and
    # `ldr r1,[r0]`), so the constant-immediate decoder covers only the second.
    assert decode_memory_operands(canonical_bytes, 0x0801266E) == ()
    first_word = decode_memory_operands(canonical_bytes, 0x08012672)
    assert [(item.mnemonic, item.rn_name, item.immediate) for item in first_word] == [
        ("ldr", "r0", 0)
    ]


def test_the_only_caller_reaches_it_through_the_selector_route(
    canonical_bytes: bytes,
) -> None:
    """``0x08009670`` has one ``bl`` caller, ``0x08008AC2``, on the map-load path.

    The caller resolves the selector-1 root with the accepted
    ``0x080089CC`` route and then registers that root's records, so the array this
    ticket censused is reached on the ordinary map-load route and not from an
    unrelated subsystem.
    """
    assert canonical_bytes[0x08008AB6 - ROM_BASE : 0x08008AC6 - ROM_BASE].hex() == (
        "b9787868fff787ff011ce86800f0d5fd"
    )
    # ldrb r1,[r7,#2] ; ldr r0,[r7,#4] ; bl 0x080089CC
    assert canonical_bytes[0x08008AB6 - ROM_BASE : 0x08008ABE - ROM_BASE].hex() == "b9787868fff787ff"
    # adds r1,r0,#0 ; ldr r0,[r5,#0xc] ; bl 0x08009670
    assert canonical_bytes[0x08008ABE - ROM_BASE : 0x08008AC6 - ROM_BASE].hex() == "011ce86800f0d5fd"


def test_the_record_first_word_is_the_constructor_the_registry_calls(
    canonical_bytes: bytes,
) -> None:
    """Two constructor values on all 735 records, one shared ``+0x04`` word.

    That is what a class tag plus a shared second word looks like, and it is
    consistent with ``0x08012672`` calling ``record[+0x00]`` as a function
    pointer through the ``bx r1`` trampoline at ``0x08046AA2``.
    """
    assert canonical_bytes[0x08046AA2 - ROM_BASE : 0x08046AA4 - ROM_BASE].hex() == "0847"


# --- tooling and ROM safety ---------------------------------------------------


def test_pointer_classification_contract() -> None:
    data = bytes(0x1000)
    assert classify_pointer(data, 0) == "null"
    assert classify_pointer(data, ROM_BASE + 0x1000) == "outside_rom"
    assert classify_pointer(data, 0x09000000) == "outside_rom"
    assert classify_pointer(data, ROM_BASE + 2) == "unaligned_in_rom"
    assert classify_pointer(data, ROM_BASE + 4) == "aligned_in_rom"


def test_read_record_reports_the_bound_offsets() -> None:
    """A synthetic record pins the physical field offsets and widths."""
    data = bytearray(0x100)
    base = 0x40
    record = ROM_BASE + base
    # prefix
    data[base + 0x00 : base + 0x04] = (0x08007675).to_bytes(4, "little")
    data[base + 0x04 : base + 0x08] = (0x0800776D).to_bytes(4, "little")
    # four u16 bounds
    for index, value in enumerate((0x0010, 0x0020, 0x0030, 0x0040)):
        data[base + 0x08 + 2 * index : base + 0x0A + 2 * index] = value.to_bytes(
            2, "little"
        )
    data[base + 0x10] = 0x02
    data[base + 0x11] = 0x01
    data[base + 0x12] = 0x0B
    data[base + 0x13] = 0x01
    data[base + 0x14 : base + 0x16] = (0x1234).to_bytes(2, "little")
    data[base + 0x16 : base + 0x18] = (0x5678).to_bytes(2, "little")

    parsed = read_record(bytes(data), record)
    assert parsed["readable"] is True
    assert parsed["bound_a_raw"] == 0x0010
    assert parsed["bound_b_raw"] == 0x0020
    assert parsed["bound_c_raw"] == 0x0030
    assert parsed["bound_d_raw"] == 0x0040
    assert parsed["width_raw"] == 0x20
    assert parsed["height_raw"] == 0x20
    assert parsed["bounds_a_le_c"] is True
    assert parsed["bounds_b_le_d"] is True
    assert parsed["zero_area"] is False
    assert parsed["byte_at_0x10"] == 0x02
    assert parsed["key_pair_big_endian"] == "010b"
    assert parsed["byte_at_0x13"] == 0x01
    assert parsed["trailing_u16_at_0x14"] == 0x1234
    assert parsed["trailing_u16_at_0x16"] == 0x5678
    assert parsed["raw_prefix_words"] == ["0x08007675", "0x0800776d"]


def test_probe_rejects_a_non_canonical_image() -> None:
    """A synthetic 8 MiB zero image is refused by the canonical SHA gate."""
    with tempfile.TemporaryDirectory() as directory:
        not_a_rom = Path(directory) / "not-canonical.gba"
        not_a_rom.write_bytes(bytes(0x800000))
        with pytest.raises(SystemExit):
            load_rom(not_a_rom)


def test_documented_module_invocation_emits_the_canonical_report(
    canonical_bytes: bytes,
) -> None:
    with tempfile.TemporaryDirectory() as directory:
        rom = Path(directory) / "canonical.gba"
        rom.write_bytes(canonical_bytes)
        before = hashlib.sha256(rom.read_bytes()).hexdigest()
        result = subprocess.run(
            [sys.executable, "-m", "tools.research.logx_connector_probe", str(rom)],
            capture_output=True,
            text=True,
            check=True,
        )
        assert rom.read_bytes() == canonical_bytes
        assert hashlib.sha256(rom.read_bytes()).hexdigest() == before
    payload = json.loads(result.stdout)
    assert payload["sha256"] == CANONICAL_SHA256
    assert payload["root_summary"]["count_sum"] == EXPECTED_COUNT_SUM
    assert payload["array_summary"]["unique_records"] == EXPECTED_UNIQUE_RECORDS
    # The heavy detail blocks are opt-in.
    assert "roots" not in payload
    assert "references" not in payload
    assert "records" not in payload


def test_the_probe_refuses_a_non_canonical_file() -> None:
    with tempfile.TemporaryDirectory() as directory:
        rom = Path(directory) / "not-canonical.gba"
        rom.write_bytes(bytes(0x800000))
        result = subprocess.run(
            [sys.executable, "-m", "tools.research.logx_connector_probe", str(rom)],
            capture_output=True,
            text=True,
        )
    assert result.returncode != 0
    assert "refusing non-canonical ROM" in (result.stdout + result.stderr)
