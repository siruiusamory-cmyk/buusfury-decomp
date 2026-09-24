"""Read-only character-definition census for LOGX-CHAR-001.

The probe answers, deterministically and without writing to the image:

* where the candidate character-definition table starts, how wide a record is
  and how many records the engine's own code accepts;
* what every record's five physical fields hold, with no semantic naming
  promoted beyond what engine instructions establish;
* which engine instruction reads each field, and what the engine does with the
  value afterwards;
* which pointer array the record's ``+0x04`` and ``+0x08`` actually reach.

Field names are deliberately neutral: ``text_index``, ``text_index_2``,
``field_04``, ``field_08``, ``field_0c``, and the two pointer arrays are named
after the *field that selects them* (``field_04``/``field_08``), not after what
their targets turn out to be.  LOGExtractor calls them the sprite-definition and
portrait tables; this ticket establishes only the field-to-table relationship,
so the external names appear in comments as claims under test and never as
identifiers or keys.  The semantic reading of each field is argued from
instruction evidence in ``docs/research/LOGX_CHAR_PROVENANCE.md``.

Evidence provenance labels follow ``docs/research-conventions.md``.  Addresses
are GBA addresses; a file offset is an address minus ``0x08000000``.

**Dependency boundary.** The census, record and target arithmetic are pure: they
need only the project's own pure codecs (``webfoot.formats.text_tables``,
``webfoot.formats.stat_tables``) and no third-party package.  Capstone is needed
*only* to read instruction text, so that import is deferred to first use:
``tools.research.thumb_disasm`` raises ``SystemExit`` when capstone is absent, and
CI's portable unit job installs only ``.[dev]``.  Deferring it is what lets
``tests/unit/test_logx_char_reference.py`` run in CI instead of skipping - an
environment without capstone can still import this module, use the whole census
API and run ``--rows``; only ``--engine``, ``format_instruction`` and
``instruction_at`` require capstone.

The probe performs no I/O beyond reading the caller's bytes and it never
mutates the canonical image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Sequence

from tools.webfoot.formats import stat_tables
from tools.webfoot.formats import text_tables

CANONICAL_SHA256 = "940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E"
ROM_SIZE = 8 * 1024 * 1024
ROM_BASE = 0x08000000

# --- the candidate character-definition table -------------------------------
#
# EXTERNAL CLAIM (mainant/LOGExtractor): a character table at 0x74D380 with 232
# sixteen-byte records.  LOGExtractor's addresses are file offsets: its "text
# pointer table 0x06BCE8" is this project's accepted TEXT_TABLE_START
# (0x0006BCE8), which fixes the address space rather than assuming it.

#: File offset of the first record.
CHAR_TABLE_FILE_OFFSET = 0x74D380

#: GBA address of the first record.
CHAR_TABLE_ADDRESS = CHAR_TABLE_FILE_OFFSET + ROM_BASE

#: Bytes per record, as the engine's own index arithmetic states it.
CHAR_RECORD_SIZE = 0x10

#: Records the engine accepts, as its own loop bound states it.
CHAR_RECORD_COUNT = 232

#: Physical field offsets inside a record.  Names are positions, not meanings.
FIELD_TEXT_INDEX = 0x00
FIELD_TEXT_INDEX_2 = 0x02
FIELD_04 = 0x04
FIELD_08 = 0x08
FIELD_0C = 0x0C

#: GBA address of the accepted UTF-16LE text pointer table (TOOLKIT-004).
#: The offset and count are this probe's OWN independent measurements, kept as
#: literals on purpose: a probe that read them from the codec it is checking
#: could not detect the codec drifting. The candidate table address and the
#: engine's own loop bound are what the probe tests, so they stay here.
TEXT_TABLE_FILE_OFFSET = 0x0006BCE8

#: Entries in that table; an index at or above this is out of range.
TEXT_TABLE_ENTRIES = 1534

#: GBA address of the accepted UTF-16LE text pointer table.
TEXT_TABLE_ADDRESS = TEXT_TABLE_FILE_OFFSET + ROM_BASE

# --- engine consumers --------------------------------------------------------

#: The engine accessor a record's ``+0x04`` is passed to.  For an id >= 10 it
#: returns ``u32 at FIELD_04_TABLE_LITERAL + 4*id - 0x28``.
FIELD_04_ACCESSOR = 0x08000158

#: A second entry to the same array, for a party record whose ``+0x0E`` is a u16
#: id.  Same literal, same displacement, same target arithmetic.
FIELD_04_ACCESSOR_PARTY = 0x0801713C

#: The literal that accessor loads.  The ``-0x28`` displacement is the compiler's
#: fold of ``-4 * 10``, so the *arithmetic* base is 0x086B6BB4.
FIELD_04_TABLE_LITERAL = 0x086B6BDC
FIELD_04_TABLE_DISPLACEMENT = -0x28
FIELD_04_TABLE_ARITHMETIC_BASE = FIELD_04_TABLE_LITERAL + FIELD_04_TABLE_DISPLACEMENT

#: Below this id the accessor does not read the array at all: ids 0..9 are
#: party-member slots handled by the accessor's own earlier branch.
FIELD_04_ID_FLOOR = 10

#: The contiguous run of valid, strictly ascending ROM pointers that starts at
#: the literal.  This is a *measured run extent*, not an engine bound:
#: independently established by TOOLKIT-010 (GRAPHICS_FORMAT.md).
FIELD_04_TABLE_ENTRY_RUN_START = FIELD_04_TABLE_LITERAL
FIELD_04_TABLE_ENTRY_COUNT = 297

#: The engine accessor a record's ``+0x08`` is passed to.  For a slot >= 8 it
#: returns ``u32 at FIELD_08_TABLE_ADDRESS + 4*slot``.
FIELD_08_ACCESSOR = 0x08011F20

#: GBA address of the second pointer array: the accessor's own literal.
FIELD_08_TABLE_ADDRESS = 0x086F393C

#: Slots before the first valid pointer.  The accessor returns 0 for slots 0 and
#: 7 without reading the array at all.
FIELD_08_FIRST_VALID_SLOT = 8

#: Last slot holding a valid ascending ROM pointer; the next word is not a ROM
#: address, which is where the array ends.  Again a *measured run extent*, not an
#: engine bound.
FIELD_08_VALID_SLOT_LAST = 162

#: The 0x1C-stride table a record's ``+0x0C`` indexes.  Same base as the
#: accepted enemy-stat table (TOOLKIT-009 / TOOLKIT-010).
STAT_TABLE_ADDRESS = stat_tables.ENEMY_TABLE_START + ROM_BASE
STAT_TABLE_RECORD_SIZE = stat_tables.ENEMY_RECORD_SIZE
STAT_TABLE_ACCEPTED_RECORDS = stat_tables.ENEMY_RECORD_COUNT

# --- structures immediately around the table (boundary evidence) -------------

#: A four-byte table referenced by ``0x0802734C``; it sits immediately before
#: the character table and is not a character record.
PRECEDING_BYTE_TABLE_ADDRESS = 0x0874D35C
PRECEDING_BYTE_TABLE_SIZE = 4

#: An eight-entry u32 pointer table referenced by ``0x08027494``, between the
#: byte table and the character table.
PRECEDING_POINTER_TABLE_ADDRESS = 0x0874D360
PRECEDING_POINTER_TABLE_ENTRIES = 8

#: The engine instructions this ticket quotes.  Each is asserted by a test from
#: the raw halfwords, so a re-transcription cannot drift from the record.
#: Reading them back needs capstone (see the dependency boundary above).
EVIDENCE_INSTRUCTIONS: dict[str, tuple[int, str]] = {
    "stride_loop_a": (0x080279A2, "lsls r0, r4, #4"),
    "stride_loop_b": (0x08027964, "lsls r0, r4, #4"),
    "stride_lookup_a": (0x08025088, "lsls r0, r0, #4"),
    "stride_lookup_b": (0x080251B8, "lsls r0, r0, #4"),
    "stride_lookup_c": (0x08025382, "lsls r0, r0, #4"),
    "stride_lookup_d": (0x08025E92, "lsls r1, r5, #4"),
    "stride_lookup_e": (0x080273AE, "lsls r0, r0, #4"),
    "stride_ui": (0x08024FA8, "lsls r5, r5, #4"),
    "count_loop_a": (0x080279CC, "cmp r4, #0xe8"),
    "count_loop_b": (0x08024F92, "cmp r0, #0xe8"),
    "text_index_read": (0x08024FAC, "ldrh r5, [r5]"),
    "text_index_read_b": (0x080251BC, "ldrh r0, [r0]"),
    "text_index_2_read_a": (0x080252E6, "ldrh r0, [r7, #2]"),
    "text_index_2_read_b": (0x0802539E, "ldrh r0, [r5, #2]"),
    "text_index_2_read_c": (0x08025EC2, "ldrh r0, [r0, #2]"),
    "text_index_scale_a": (0x080251C0, "lsls r0, r0, #2"),
    "text_index_scale_b": (0x080252EA, "lsls r0, r0, #2"),
    "text_index_scale_c": (0x080253A2, "lsls r0, r0, #2"),
    "text_index_scale_d": (0x08025EC6, "lsls r0, r0, #2"),
    "text_table_load_a": (0x080251C2, "ldr r1, [r1, r0]"),
    "text_table_load_b": (0x080253A4, "ldr r0, [r1, r0]"),
    "text_table_load_c": (0x08025EC8, "ldr r0, [r1, r0]"),
    "field_04_read_a": (0x080273B2, "ldr r0, [r0, #4]"),
    "field_04_read_b": (0x08027968, "ldr r0, [r6, #4]"),
    "field_04_accessor_call": (0x0802796A, "bl #0x8000158"),
    "field_08_read": (0x080250CA, "ldr r0, [r7, #8]"),
    "field_08_accessor_call": (0x080250D2, "bl #0x8011f20"),
    "field_0c_read_a": (0x08027974, "ldr r0, [r6, #0xc]"),
    "field_0c_read_b": (0x080279AA, "ldr r1, [r0, #0xc]"),
    "field_0c_sign_test": (0x080279AE, "blt #0x80279ca"),
    "stat_index_scale_a": (0x080279B0, "lsls r3, r1, #3"),
    "stat_index_scale_b": (0x080279B2, "subs r1, r3, r1"),
    "stat_index_scale_c": (0x080279B4, "lsls r1, r1, #2"),
    "field_04_literal_load": (0x0800015E, "ldr r1, [pc, #0x260]"),
    "field_04_displacement": (0x08000164, "subs r0, #0x40"),
    "field_04_field_offset": (0x08000166, "ldr r0, [r0, #0x18]"),
    "field_08_literal_load": (0x08011F52, "ldr r1, [pc, #0x240]"),
}

#: Every ``ldr Rt,[pc,#imm]`` site whose literal pool word is the character
#: table address.  A raw halfword scan; see :func:`thumb_ldr_literal_sites`.
CHAR_TABLE_LITERAL_SITES = (
    0x08024FA0,
    0x08025086,
    0x080251B6,
    0x08025380,
    0x08025E94,
    0x080273AC,
    0x08027962,
    0x080279A0,
)

#: Literal pool words belonging to the two structures immediately before the
#: table.  They are what makes the table's own start a boundary rather than a
#: guess.
NEIGHBOUR_LITERAL_VALUES = (0x0874D35C, 0x0874D360)

#: Range searched for any further literal that could reach the table through a
#: folded base: the 0x100 bytes below the table plus the table's own head.  A
#: folded base would sit immediately below the address, exactly as the ``+0x04``
#: accessor's does.  The whole image is scanned at every even offset; this range
#: is what the report enumerates.
NEIGHBOURHOOD = (CHAR_TABLE_ADDRESS - 0x100, CHAR_TABLE_ADDRESS + 0x80)


class CharProbeError(RuntimeError):
    """Raised when the image or the requested report cannot be produced."""


# --- byte helpers ------------------------------------------------------------


def _u16(data: bytes, address: int) -> int:
    return struct.unpack_from("<H", data, address - ROM_BASE)[0]


def _u32(data: bytes, address: int) -> int:
    return struct.unpack_from("<I", data, address - ROM_BASE)[0]


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def verify_canonical(data: bytes) -> None:
    """Fail closed unless ``data`` is the canonical Buu's Fury image."""
    if len(data) != ROM_SIZE:
        raise CharProbeError(f"image is {len(data)} bytes, expected {ROM_SIZE}")
    actual = sha256_of(data)
    if actual != CANONICAL_SHA256:
        raise CharProbeError(
            f"refusing non-canonical image: expected {CANONICAL_SHA256}, got {actual}"
        )


def load_rom(path: Path) -> bytes:
    data = Path(path).read_bytes()
    verify_canonical(data)
    return data


def in_rom(data: bytes, address: int) -> bool:
    """True when ``address`` is a word-aligned GBA address inside the image."""
    if address % 4:
        return False
    offset = address - ROM_BASE
    return 0 <= offset and offset + 4 <= len(data)


# --- the records -------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CharacterRecord:
    """One sixteen-byte record, read at its physical width, uninterpreted."""

    index: int
    file_offset: int
    address: int
    text_index: int
    text_index_2: int
    field_04: int
    field_08: int
    field_0c: int

    @property
    def field_0c_signed(self) -> int:
        """``+0x0C`` read as the engine reads it: ``ldr``, then a signed test."""
        return self.field_0c - 0x100000000 if self.field_0c & 0x80000000 else self.field_0c

    @property
    def raw(self) -> bytes:
        return struct.pack(
            "<HHIII",
            self.text_index,
            self.text_index_2,
            self.field_04,
            self.field_08,
            self.field_0c,
        )


def read_record(data: bytes, index: int) -> CharacterRecord:
    address = CHAR_TABLE_ADDRESS + index * CHAR_RECORD_SIZE
    text_index, text_index_2, field_04, field_08, field_0c = struct.unpack_from(
        "<HHIII", data, address - ROM_BASE
    )
    return CharacterRecord(
        index=index,
        file_offset=address - ROM_BASE,
        address=address,
        text_index=text_index,
        text_index_2=text_index_2,
        field_04=field_04,
        field_08=field_08,
        field_0c=field_0c,
    )


def iter_records(data: bytes) -> list[CharacterRecord]:
    return [read_record(data, index) for index in range(CHAR_RECORD_COUNT)]


# --- resolving each field's target -------------------------------------------


def resolve_text(data: bytes, index: int) -> str:
    """The string a u16 text index selects, through the accepted text codec."""
    if not 0 <= index < TEXT_TABLE_ENTRIES:
        raise CharProbeError(f"text index {index} is outside 0..{TEXT_TABLE_ENTRIES - 1}")
    offset = text_tables.read_pointer(data, index, TEXT_TABLE_FILE_OFFSET)
    text, _ = text_tables.decode_string(data, offset)
    return text


def text_target(data: bytes, index: int) -> int:
    """The GBA address a text index selects, through the accepted text table."""
    if not 0 <= index < TEXT_TABLE_ENTRIES:
        raise CharProbeError(f"text index {index} is outside 0..{TEXT_TABLE_ENTRIES - 1}")
    return text_tables.read_pointer(data, index, TEXT_TABLE_FILE_OFFSET) + ROM_BASE


def field_04_target(data: bytes, identifier: int) -> int:
    """The word the ``+0x04`` accessor returns for ``identifier``.

    Mirrors ``0x08000158`` exactly: ``u32 at FIELD_04_TABLE_LITERAL + 4*id -
    0x28`` for an id at or above the party-slot floor.  It does **not** claim
    that the word is a structure of any particular kind; that reading belongs to
    LOGX-SPRITE-001.
    """
    if identifier < FIELD_04_ID_FLOOR:
        raise CharProbeError(
            f"id {identifier} is below the accessor's table floor "
            f"{FIELD_04_ID_FLOOR}; the accessor takes its party-slot branch instead"
        )
    return _u32(data, FIELD_04_TABLE_ARITHMETIC_BASE + identifier * 4)


def field_08_target(data: bytes, slot: int) -> int:
    """The word the ``+0x08`` accessor returns for ``slot``.

    Mirrors ``0x08011F20``: 0 for slots 0 and 7, and for a slot at or above the
    first valid slot ``u32 at FIELD_08_TABLE_ADDRESS + 4*slot``.  Slots 1..6 take
    a party-record path in the engine and are refused here rather than guessed.
    """
    if slot in (0, 7):
        return 0
    if 1 <= slot <= 6:
        raise CharProbeError(f"slot {slot} takes the accessor's party path, not the array")
    if slot < FIELD_08_FIRST_VALID_SLOT:
        raise CharProbeError(f"slot {slot} is out of range")
    return _u32(data, FIELD_08_TABLE_ADDRESS + slot * 4)


def stat_record_address(data: bytes, index: int) -> int:
    """The record ``+0x0C`` selects, at the engine's own stride arithmetic."""
    if index < 0:
        raise CharProbeError(f"stat index {index} is negative")
    return STAT_TABLE_ADDRESS + index * STAT_TABLE_RECORD_SIZE


# --- engine instruction evidence ---------------------------------------------


@lru_cache(maxsize=1)
def _decode_thumb_at() -> Callable[[bytes, int], Any]:
    """The Thumb decoder, imported on first use rather than at module import.

    ``tools.research.thumb_disasm`` raises ``SystemExit`` when capstone is
    missing, and capstone is research tooling rather than a declared dependency
    of the shipping SDK that CI's portable job installs.  Importing it lazily
    keeps the census, record and target API usable - and CI-coverable - without
    it; only the instruction helpers below require it, and they are exercised
    only by the ROM-gated suite and ``--engine``.
    """
    from tools.research.thumb_disasm import decode_thumb_at

    return decode_thumb_at


def instruction_at(data: bytes, address: int) -> tuple[str, str, bytes]:
    """``(mnemonic, operands, raw bytes)`` for the Thumb instruction at a site.

    Requires capstone; see the module docstring's dependency boundary.
    """
    item = _decode_thumb_at()(data, address)
    if item is None:
        raise CharProbeError(f"no Thumb instruction decodes at {address:#010x}")
    offset = address - ROM_BASE
    return item.mnemonic, item.operands, data[offset : offset + item.size]


def format_instruction(data: bytes, address: int) -> str:
    mnemonic, operands, _ = instruction_at(data, address)
    return f"{address:08x}  {mnemonic:<8} {operands}".rstrip()


def thumb_ldr_literal_sites(data: bytes) -> dict[int, list[tuple[int, int, int]]]:
    """Every ``ldr Rt,[pc,#imm]`` whose literal-word value is ``address``.

    Returns ``{literal value: [(site, Rt, pool address), ...]}``.  This is a raw
    halfword scan over every even offset, so an undecodable neighbouring halfword
    cannot hide a site and no control-flow knowledge is needed.  It is how this
    ticket states a *negative* claim about the table address.

    The returned mapping is shared with the caller and must not be mutated; the
    whole-image scan is cached because several reports need it.
    """
    return _thumb_ldr_literal_sites(data)


@lru_cache(maxsize=4)
def _thumb_ldr_literal_sites(data: bytes) -> dict[int, list[tuple[int, int, int]]]:
    found: dict[int, list[tuple[int, int, int]]] = {}
    address = ROM_BASE
    limit = ROM_BASE + len(data)
    while address + 4 <= limit:
        halfword = _u16(data, address)
        if (halfword & 0xF800) == 0x4800:
            register = (halfword >> 8) & 7
            pool = ((address + 4) & ~3) + (halfword & 0xFF) * 4
            if ROM_BASE <= pool and pool + 4 <= limit:
                found.setdefault(_u32(data, pool), []).append((address, register, pool))
        address += 2
    return found


def literal_values_in_range(data: bytes, low: int, high: int) -> dict[int, list[int]]:
    """Literal-pool values in ``[low, high]``, with their load sites.

    A folded base (as the ``+0x04`` accessor uses) hides the table address behind
    a displacement, so a scan for the exact word alone would not be exhaustive.
    This reports the neighbourhood so the caller can adjudicate each value.
    """
    sites = thumb_ldr_literal_sites(data)
    return {
        value: sorted(site for site, _, _ in sites[value])
        for value in sorted(sites)
        if low <= value <= high
    }


def engine_report(data: bytes) -> dict[str, Any]:
    """The instruction evidence for the table's start, stride, count and fields."""
    instructions = {
        name: {
            "address": f"{address:#010x}",
            "encoding": instruction_at(data, address)[2].hex(),
            "text": format_instruction(data, address),
            "expected": text,
        }
        for name, (address, text) in EVIDENCE_INSTRUCTIONS.items()
    }
    literal_sites = thumb_ldr_literal_sites(data)
    char_sites = [
        {"site": f"{site:#010x}", "register": f"r{register}", "pool": f"{pool:#010x}"}
        for site, register, pool in sorted(literal_sites.get(CHAR_TABLE_ADDRESS, []))
    ]
    neighbours = literal_values_in_range(data, *NEIGHBOURHOOD)
    return {
        "char_table_address": f"{CHAR_TABLE_ADDRESS:#010x}",
        "char_table_literal_sites": char_sites,
        "neighbourhood_literals": {
            f"{value:#010x}": [f"{site:#010x}" for site in sites]
            for value, sites in neighbours.items()
        },
        "instructions": instructions,
        "accessors": {
            "field_04": f"{FIELD_04_ACCESSOR:#010x}",
            "field_04_party": f"{FIELD_04_ACCESSOR_PARTY:#010x}",
            "field_08": f"{FIELD_08_ACCESSOR:#010x}",
            "field_04_literal": f"{FIELD_04_TABLE_LITERAL:#010x}",
            "field_04_arithmetic_base": f"{FIELD_04_TABLE_ARITHMETIC_BASE:#010x}",
            "field_08_table": f"{FIELD_08_TABLE_ADDRESS:#010x}",
            "stat_table": f"{STAT_TABLE_ADDRESS:#010x}",
        },
    }


# --- census arithmetic -------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CensusLimits:
    """The bounds a row is checked against.

    Every bound has a stated source, and the two kinds of source are kept apart:
    ``text_entries`` is a codec constant and ``stat_accepted_records`` is the
    record count TOOLKIT-009 validated, while ``field_04_entry_count`` and
    ``field_08_last_valid_slot`` are *measured pointer-run extents* for which no
    engine bound was found.  None of them is inferred from the data being
    censused.
    """

    text_entries: int = TEXT_TABLE_ENTRIES
    field_04_id_floor: int = FIELD_04_ID_FLOOR
    field_04_entry_count: int = FIELD_04_TABLE_ENTRY_COUNT
    field_08_first_valid_slot: int = FIELD_08_FIRST_VALID_SLOT
    field_08_last_valid_slot: int = FIELD_08_VALID_SLOT_LAST
    stat_accepted_records: int = STAT_TABLE_ACCEPTED_RECORDS


def census_rows(
    rows: Sequence[Sequence[int]], limits: CensusLimits | None = None
) -> dict[str, Any]:
    """Census arithmetic over ``(text, text2, field_04, field_08, field_0c_signed)``.

    Pure: it takes plain integers so synthetic rows can exercise every anomaly
    branch without a ROM.  ``field_0c_signed`` is the signed reading, because
    the engine tests that field with ``blt``.
    """
    limits = limits or CensusLimits()
    field_04_limit = limits.field_04_id_floor + limits.field_04_entry_count

    seen: dict[tuple[int, ...], list[int]] = {}
    anomalies: list[dict[str, Any]] = []
    counters = {
        "records": 0,
        "text_index_out_of_range": 0,
        "text_index_2_not_text_index_plus_one": 0,
        "field_04_id_below_accessor_floor": 0,
        "field_04_id_out_of_table": 0,
        "field_08_slot_reserved": 0,
        "field_08_slot_out_of_table": 0,
        "field_0c_negative": 0,
        "field_0c_beyond_accepted_stat_extent": 0,
        "field_0c_zero": 0,
        "zero_field_04": 0,
        "zero_field_08": 0,
    }
    for index, row in enumerate(rows):
        text, text2, field_04, field_08, field_0c = row
        counters["records"] += 1
        flags: list[str] = []
        if not 0 <= text < limits.text_entries:
            flags.append("text_index_out_of_range")
            counters["text_index_out_of_range"] += 1
        if text2 != text + 1:
            flags.append("text_index_2_not_text_index_plus_one")
            counters["text_index_2_not_text_index_plus_one"] += 1
        if field_04 == 0:
            counters["zero_field_04"] += 1
        elif field_04 < limits.field_04_id_floor:
            flags.append("field_04_id_below_accessor_floor")
            counters["field_04_id_below_accessor_floor"] += 1
        elif field_04 >= field_04_limit:
            flags.append("field_04_id_out_of_table")
            counters["field_04_id_out_of_table"] += 1
        if field_08 == 0:
            counters["zero_field_08"] += 1
        elif 1 <= field_08 < limits.field_08_first_valid_slot:
            flags.append("field_08_slot_reserved")
            counters["field_08_slot_reserved"] += 1
        elif field_08 > limits.field_08_last_valid_slot:
            flags.append("field_08_slot_out_of_table")
            counters["field_08_slot_out_of_table"] += 1
        if field_0c < 0:
            counters["field_0c_negative"] += 1
        else:
            if field_0c == 0:
                counters["field_0c_zero"] += 1
            if field_0c >= limits.stat_accepted_records:
                flags.append("field_0c_beyond_accepted_stat_extent")
                counters["field_0c_beyond_accepted_stat_extent"] += 1
        if flags:
            anomalies.append({"index": index, "flags": sorted(flags)})
        seen.setdefault(tuple(int(value) for value in row), []).append(index)

    duplicates = [
        {"row": list(key), "indices": indices}
        for key, indices in sorted(seen.items())
        if len(indices) > 1
    ]
    return {
        "counters": counters,
        "anomalies": anomalies,
        "duplicate_complete_records": duplicates,
        "distinct": {
            "text_index": len({row[0] for row in rows}),
            "text_index_2": len({row[1] for row in rows}),
            "field_04": len({row[2] for row in rows}),
            "field_08": len({row[3] for row in rows}),
            "field_0c": len({row[4] for row in rows}),
        },
        "zero_counts": {
            "text_index": sum(1 for row in rows if row[0] == 0),
            "field_04": counters["zero_field_04"],
            "field_08": counters["zero_field_08"],
            "field_0c": counters["field_0c_zero"],
        },
    }


def _target_counts(data: bytes, references: dict[int, list[int]], resolve: Any) -> dict[str, int]:
    return {
        "references": sum(len(v) for v in references.values()),
        "unique_values": len(references),
        "unique_targets": len({resolve(data, key) for key in references}),
    }


def census(data: bytes) -> dict[str, Any]:
    """Full census of the canonical table plus the referenced-target arithmetic."""
    records = iter_records(data)
    rows = [
        (record.text_index, record.text_index_2, record.field_04, record.field_08,
         record.field_0c_signed)
        for record in records
    ]
    summary = census_rows(rows)

    text_references: dict[int, list[int]] = {}
    text_2_references: dict[int, list[int]] = {}
    field_04_references: dict[int, list[int]] = {}
    field_08_references: dict[int, list[int]] = {}
    stat_references: dict[int, list[int]] = {}
    for record in records:
        text_references.setdefault(record.text_index, []).append(record.index)
        text_2_references.setdefault(record.text_index_2, []).append(record.index)
        if record.field_04 >= FIELD_04_ID_FLOOR:
            field_04_references.setdefault(record.field_04, []).append(record.index)
        if record.field_08:
            field_08_references.setdefault(record.field_08, []).append(record.index)
        if record.field_0c_signed >= 0:
            stat_references.setdefault(record.field_0c_signed, []).append(record.index)

    summary["references"] = {
        "text_index": _target_counts(data, text_references, text_target),
        "text_index_2": _target_counts(data, text_2_references, text_target),
        "field_04": _target_counts(data, field_04_references, field_04_target),
        "field_08": _target_counts(data, field_08_references, field_08_target),
        "field_0c": _target_counts(data, stat_references,
                                  lambda buf, key: stat_record_address(buf, key)),
    }
    # Distinct *strings* are fewer than distinct indices: several slots can hold
    # identical text.  Counted separately so the two are never conflated.
    summary["distinct_text_strings"] = {
        "text_index": len({resolve_text(data, key) for key in text_references}),
        "text_index_2": len({resolve_text(data, key) for key in text_2_references}),
    }
    summary["table"] = {
        "file_offset": f"{CHAR_TABLE_FILE_OFFSET:#08x}",
        "address": f"{CHAR_TABLE_ADDRESS:#010x}",
        "record_size": CHAR_RECORD_SIZE,
        "record_count": CHAR_RECORD_COUNT,
    }
    summary["rows"] = [
        {
            "index": record.index,
            "file_offset": f"{record.file_offset:#08x}",
            "address": f"{record.address:#010x}",
            "text_index": record.text_index,
            "text_index_2": record.text_index_2,
            "field_04": record.field_04,
            "field_08": record.field_08,
            "field_0c": record.field_0c,
            "field_0c_signed": record.field_0c_signed,
            "raw": record.raw.hex(),
        }
        for record in records
    ]
    return summary


# --- the two pointer arrays and the table boundary ---------------------------


def field_04_table_report(data: bytes) -> dict[str, Any]:
    """The ``+0x04`` pointer array's entry run, read as raw words."""
    values = [
        _u32(data, FIELD_04_TABLE_ENTRY_RUN_START + index * 4)
        for index in range(FIELD_04_TABLE_ENTRY_COUNT + 2)
    ]
    entries = values[:FIELD_04_TABLE_ENTRY_COUNT]
    slots_before = [
        _u32(data, FIELD_04_TABLE_ARITHMETIC_BASE + index * 4)
        for index in range(FIELD_04_ID_FLOOR)
    ]
    return {
        "literal": f"{FIELD_04_TABLE_LITERAL:#010x}",
        "arithmetic_base": f"{FIELD_04_TABLE_ARITHMETIC_BASE:#010x}",
        "entry_run_start": f"{FIELD_04_TABLE_ENTRY_RUN_START:#010x}",
        "entry_count": FIELD_04_TABLE_ENTRY_COUNT,
        "all_entries_in_rom": all(in_rom(data, value) for value in entries),
        "strictly_ascending": all(
            entries[i] < entries[i + 1] for i in range(len(entries) - 1)
        ),
        "word_before_run_hex": f"{_u32(data, FIELD_04_TABLE_LITERAL - 4):08x}",
        "word_after_run_hex": f"{values[FIELD_04_TABLE_ENTRY_COUNT]:08x}",
        "word_after_run_in_rom": in_rom(data, values[FIELD_04_TABLE_ENTRY_COUNT]),
        "first_entry": f"{entries[0]:#010x}",
        "last_entry": f"{entries[-1]:#010x}",
        "slots_before_run": [f"{value:#010x}" for value in slots_before],
        "slots_before_run_valid": sum(
            1 for value in slots_before if in_rom(data, value)
        ),
        "slots_before_run_null": sum(1 for value in slots_before if value == 0),
    }


def field_08_table_report(data: bytes) -> dict[str, Any]:
    """The ``+0x08`` pointer array's slot run, read as raw words."""
    slots = [
        _u32(data, FIELD_08_TABLE_ADDRESS + index * 4)
        for index in range(FIELD_08_VALID_SLOT_LAST + 2)
    ]
    valid = slots[FIELD_08_FIRST_VALID_SLOT : FIELD_08_VALID_SLOT_LAST + 1]
    return {
        "address": f"{FIELD_08_TABLE_ADDRESS:#010x}",
        "slot_count": FIELD_08_VALID_SLOT_LAST + 1,
        "slots_before_first_valid_are_zero": all(
            slots[index] == 0 for index in range(FIELD_08_FIRST_VALID_SLOT)
        ),
        "valid_slots_all_in_rom": all(in_rom(data, value) for value in valid),
        "valid_slots_strictly_ascending": all(
            valid[i] < valid[i + 1] for i in range(len(valid) - 1)
        ),
        "first_valid_slot": f"{valid[0]:#010x}",
        "last_valid_slot": f"{valid[-1]:#010x}",
        "valid_slot_count": len(valid),
        "word_after_last_slot_hex": f"{slots[FIELD_08_VALID_SLOT_LAST + 1]:08x}",
        "word_after_last_slot_in_rom": in_rom(data, slots[FIELD_08_VALID_SLOT_LAST + 1]),
    }


def boundary_report(data: bytes) -> dict[str, Any]:
    """What sits immediately before and after the candidate table."""
    end = CHAR_TABLE_ADDRESS + CHAR_RECORD_COUNT * CHAR_RECORD_SIZE
    pre_byte = data[
        PRECEDING_BYTE_TABLE_ADDRESS - ROM_BASE :
        PRECEDING_BYTE_TABLE_ADDRESS - ROM_BASE + PRECEDING_BYTE_TABLE_SIZE
    ]
    pre_pointers = [
        _u32(data, PRECEDING_POINTER_TABLE_ADDRESS + index * 4)
        for index in range(PRECEDING_POINTER_TABLE_ENTRIES)
    ]
    after = _u32(data, end)
    after_text, after_text_2, after_04, after_08, after_0c = struct.unpack_from(
        "<HHIII", data, end - ROM_BASE
    )
    invariants = {
        "text_index_in_range": after_text < TEXT_TABLE_ENTRIES,
        "text_index_2_is_text_index_plus_one": after_text_2 == after_text + 1,
        "field_04_is_a_table_id": FIELD_04_ID_FLOOR
        <= after_04
        < FIELD_04_ID_FLOOR + FIELD_04_TABLE_ENTRY_COUNT,
        "field_08_is_a_slot_or_zero": after_08 == 0
        or FIELD_08_FIRST_VALID_SLOT <= after_08 <= FIELD_08_VALID_SLOT_LAST,
    }
    return {
        "preceding_byte_table": {
            "address": f"{PRECEDING_BYTE_TABLE_ADDRESS:#010x}",
            "bytes_hex": pre_byte.hex(),
        },
        "preceding_pointer_table": {
            "address": f"{PRECEDING_POINTER_TABLE_ADDRESS:#010x}",
            "entries": PRECEDING_POINTER_TABLE_ENTRIES,
            "all_in_rom": all(in_rom(data, value) for value in pre_pointers),
        },
        "first_word_after_table": {
            "address": f"{end:#010x}",
            "hex": f"{after:08x}",
        },
        "first_candidate_beyond_count": {
            "index": CHAR_RECORD_COUNT,
            "text_index": after_text,
            "text_index_2": after_text_2,
            "field_04": after_04,
            "field_08": after_08,
            "field_0c": after_0c,
            **invariants,
            "invariants_failed": sorted(
                name for name, held in invariants.items() if not held
            ),
        },
    }


# --- report assembly ---------------------------------------------------------


def build_report(data: bytes, *, include_rows: bool = False) -> dict[str, Any]:
    report = {
        "canonical_sha256": CANONICAL_SHA256,
        "census": census(data),
        "field_04_table": field_04_table_report(data),
        "field_08_table": field_08_table_report(data),
        "boundary": boundary_report(data),
        "engine": engine_report(data),
    }
    if not include_rows:
        report["census"].pop("rows", None)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, help="canonical Buu's Fury ROM (read-only)")
    parser.add_argument("--rows", action="store_true", help="include every record")
    parser.add_argument("--engine", action="store_true", help="engine evidence only")
    args = parser.parse_args(argv)

    data = load_rom(args.rom)
    if args.engine:
        json.dump(engine_report(data), sys.stdout, indent=2, sort_keys=True)
    else:
        json.dump(build_report(data, include_rows=args.rows), sys.stdout,
                  indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
