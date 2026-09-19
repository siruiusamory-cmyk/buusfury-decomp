"""GRAPHICS-COVERAGE-001: deterministic enumerator for the portrait graphics
container population of Buu's Fury.

This is a *research probe*, not a shipping exporter. It reads the canonical image
read-only, refuses any other image by SHA-256, and emits addresses, counts and
sizes only - never a decoded payload.

The portrait population is enumerated SYSTEM-FIRST, from engine code, not from a
byte scan:

1. The appearance-definition consumer ``0x08011F20`` (LOGX-CHAR-001 s11) loads the
   portrait pointer array through a literal in its own constant pool at
   ``0x08012194``. This probe reads that pool word from the ROM to obtain the
   array base, so the base is *derived from the engine*, not hard-coded.
2. The array is walked from slot 8 (``FIRST_ARRAY_SLOT``) to the first slot that
   is not a ROM pointer. LOGX-CHAR-001 established that slots 0..7 are the
   reserved/zero prefix (the accessor returns 0 for indices 0 and 7 without
   reading the array) and the valid pointer run is slots 8..162; slot 163 holds
   ``0x0011E502``, which is not a ROM address, and bounds the array.
3. Each valid slot points at a Webfoot container. The probe decodes each one with
   the accepted project codec (``tools.webfoot.formats.webfoot_lz``) and reports
   the container kind, the declared size and the decoded size.

The population it reproduces (canonical image): **155** portrait containers, all
form 1, each declaring and decoding to exactly 4,096 bytes (INFERRED 64x64 at
8bpp; the container header has no dimension field). This probe enumerates and
self-checks portrait extents only; it does NOT compute disjointness. Whether the
155 are disjoint from every container the accepted sprite / tileset / map graphs
reach (the 11,715-container corpus) is a separate cross-check run by
``logx_gfxscan_probe ... --known``, not this module's output (GRAPHICS-COVERAGE-001).

Graphics identity is reported as CONFIRMED_SHAPE, not CONFIRMED_RENDER: the
consumer ``0x08025056`` passes each pointer to the container dispatcher
``0x0803D940`` (LOGX-CHAR-001 s11.2), every payload decodes to a whole 64x64 8bpp
tile block, and no ROM rendering/palette was captured here.

Completeness (PORTRAIT-COMPLETENESS-001)
----------------------------------------
Enumerating the run says how many containers it holds; it does not say whether
that run accounts for the portraits the engine asks for. ``portrait_reference_report``
answers that by joining the run to the field that selects it.

The field is ``+0x08`` of the **232-record appearance-definition table at
``0x0874D380``**, not of the 297-entry pointer run at ``0x086B6BDC``. That is read
off the engine, not assumed: the consumer ``0x08025056`` loads the literal
``0x0874D380`` from its pool at ``0x08025310`` (``0x08025086``), scales the
appearance index with ``lsls r0,r0,#4`` (``0x08025088``), forms the record base
with ``adds r7,r0,r1`` (``0x0802508A``), reads ``ldr r0,[r7,#8]`` (``0x080250CA``)
and only then calls ``0x08011F20`` (``0x080250D2``). ``portrait_field_evidence``
re-asserts each of those raw halfwords, so the binding cannot drift from the
image. The 297-entry run's records are a *different* structure and are reported
separately by ``definition_run_portrait_field_report`` as the corrected premise.

The join arithmetic is pure (:func:`join_portrait_references`) so every failure
branch - reserved slot, out-of-run slot - is exercised without a ROM.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections.abc import Sequence
from pathlib import Path

from tools.research import logx_char_probe
from tools.webfoot.formats import webfoot_lz

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
GBA_BASE = 0x08000000

#: LOGX-CHAR-001 s11: the constant-pool word inside the ``0x08011F20`` accessor
#: that holds the portrait-array base. Reading it from the ROM anchors the array
#: to the engine instead of hard-coding the array address.
PORTRAIT_ARRAY_POOL_WORD = 0x08012194

#: The accessor returns 0 for indices 0 and 7 without touching the array, and its
#: ``cmp r0, #8`` / ``bge`` only reaches the array for indices >= 8, so the first
#: array slot the array path can ever read is slot 8. This bound is the engine's,
#: not a magic number: it is the branch target in the disassembly quoted in
#: LOGX-CHAR-001 s11.1.
FIRST_ARRAY_SLOT = 8

#: Guard against a runaway walk on a corrupt image. The canonical array is 163
#: slots; anything far past that is a bug, not a longer table.
_MAX_SLOTS = 4096

# --- the population that carries the portrait field ---------------------------
#
# The record base, stride and count come from the accepted appearance-definition
# census (LOGX-CHAR-001), reused rather than re-declared: a second copy of a
# proven constant is a second thing that can drift.

#: GBA address of the appearance-definition table's first record.
APPEARANCE_TABLE_ADDRESS = logx_char_probe.CHAR_TABLE_ADDRESS

#: Records the engine's own loop bound accepts (``cmp r4,#0xe8``).
APPEARANCE_RECORD_COUNT = logx_char_probe.CHAR_RECORD_COUNT

#: Bytes per record; the engine's own ``lsls rn,#4`` index scale.
APPEARANCE_RECORD_SIZE = logx_char_probe.CHAR_RECORD_SIZE

#: The portrait field inside an appearance-definition record.
APPEARANCE_PORTRAIT_OFFSET = logx_char_probe.FIELD_08

# --- the second candidate population, reported to correct the premise ---------

#: GBA address of the 297-entry ``+0x04`` pointer run (LOGX-SPRITE-001). Its
#: records are *not* appearance definitions; ``+0x08`` of a record this run
#: points at is not a portrait slot, and this probe measures that rather than
#: asserting it.
DEFINITION_RUN_ADDRESS = logx_char_probe.FIELD_04_TABLE_LITERAL
DEFINITION_RUN_COUNT = logx_char_probe.FIELD_04_TABLE_ENTRY_COUNT

#: Engine instructions that bind the appearance-definition table to the portrait
#: accessor, as raw halfwords. Each is asserted by a test, so a re-transcription
#: cannot drift from the image. Reading them needs no disassembler.
PORTRAIT_FIELD_HALFWORDS: dict[str, tuple[int, int]] = {
    "consumer_table_literal_load": (0x08025086, 0x49A2),
    "consumer_index_scale": (0x08025088, 0x0100),
    "consumer_record_base_add": (0x0802508A, 0x1847),
    "consumer_portrait_field_load": (0x080250CA, 0x68B8),
    "accessor_slot_zero_test": (0x08011F20, 0x2800),
    "accessor_slot_seven_equal": (0x08011F24, 0x2807),
    "accessor_valid_floor_test": (0x08011F2C, 0x2808),
    "accessor_array_literal_load": (0x08011F52, 0x4990),
    "accessor_slot_scale": (0x08011F54, 0x0080),
    "accessor_array_load": (0x08011F56, 0x5808),
}

#: The consumer's literal pool word that holds the appearance-definition table.
CONSUMER_TABLE_POOL_WORD = 0x08025310

#: The accessor call site that consumes an appearance-definition record's field.
CONSUMER_PORTRAIT_CALL_SITE = 0x080250D2

#: The 24-byte-stride table the accessor's slots-1..6 party path resolves a
#: portrait slot through: ``0x08011F44`` loads it from pool ``0x08012190``, then
#: adds ``24 * party_index + slot`` and reads a byte at ``+0x0F``. That byte is a
#: portrait slot fed to the same array. The *instruction* is CONFIRMED; the
#: table's identity as a party/roster record table is **INFERRED**.
PARTY_RECORD_TABLE_ADDRESS = 0x086B82EC
PARTY_RECORD_STRIDE = 24
PARTY_SLOT_BYTE_BASE = 0x0F
PARTY_SLOT_RANGE = (1, 6)

#: The party table ends where the portrait container block begins. Taking *every*
#: whole record before that boundary is deliberately a superset of the records a
#: runtime index can select, which is what makes the escape check a bound.
PARTY_RECORD_TABLE_END = 0x086B880C

#: The inlined duplicate of the party path that loads the array base itself.
INLINE_PARTY_ARRAY_SITE = 0x0801213E


def load_rom(path: str | Path) -> bytes:
    data = Path(path).read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != CANONICAL_SHA256:
        raise SystemExit(
            f"refusing non-canonical image: expected {CANONICAL_SHA256}, got {actual}"
        )
    return data


def _u32(data: bytes, addr: int) -> int:
    off = addr - GBA_BASE
    return struct.unpack_from("<I", data, off)[0]


def _is_rom_ptr(data: bytes, value: int) -> bool:
    return GBA_BASE <= value < GBA_BASE + len(data)


def portrait_array_base(data: bytes) -> int:
    """The portrait-array base, read from the engine accessor's own pool word."""
    base = _u32(data, PORTRAIT_ARRAY_POOL_WORD)
    if not _is_rom_ptr(data, base):
        raise SystemExit(
            f"portrait-array pool word 0x{PORTRAIT_ARRAY_POOL_WORD:08X} = "
            f"0x{base:08X} is not a ROM pointer"
        )
    return base


def portrait_pointers(data: bytes) -> list[int]:
    """Every valid portrait container pointer, in slot order.

    Slots below ``FIRST_ARRAY_SLOT`` are documented zero and are skipped. The walk
    stops at the first slot at or above ``FIRST_ARRAY_SLOT`` that is not a ROM
    pointer, which is how the array bounds itself (slot 163 = 0x0011E502).
    """
    base = portrait_array_base(data)
    pointers: list[int] = []
    slot = FIRST_ARRAY_SLOT
    while slot < _MAX_SLOTS:
        value = _u32(data, base + 4 * slot)
        if not _is_rom_ptr(data, value):
            break
        pointers.append(value)
        slot += 1
    return pointers


def enumerate_portraits(data: bytes) -> dict:
    """Decode every portrait container and summarise the population."""
    base = portrait_array_base(data)
    pointers = portrait_pointers(data)

    kinds: dict[int, int] = {}
    declared_sizes: set[int] = set()
    decoded_sizes: set[int] = set()
    decode_failures = 0
    extents: list[tuple[int, int]] = []
    ascending = all(pointers[i] < pointers[i + 1] for i in range(len(pointers) - 1))

    for ptr in pointers:
        off = ptr - GBA_BASE
        kinds[_u32(data, ptr)] = kinds.get(_u32(data, ptr), 0) + 1
        declared_sizes.add(_u32(data, ptr + 4))
        try:
            container = webfoot_lz.unpack(data, off)
        except webfoot_lz.ContainerError:
            decode_failures += 1
            continue
        decoded_sizes.add(len(container.data))
        extents.append((off, container.packed_end))

    extents.sort()
    overlaps = sum(
        1 for i in range(1, len(extents)) if extents[i][0] < extents[i - 1][1]
    )

    return {
        "rom_sha256": CANONICAL_SHA256.upper(),
        "portrait_array_base": f"0x{base:08X}",
        "portrait_array_pool_word": f"0x{PORTRAIT_ARRAY_POOL_WORD:08X}",
        "portrait_count": len(pointers),
        "pointers_strictly_ascending": ascending,
        "first_pointer": f"0x{pointers[0]:08X}" if pointers else None,
        "last_pointer": f"0x{pointers[-1]:08X}" if pointers else None,
        "container_kinds": kinds,
        "declared_sizes": sorted(declared_sizes),
        "decoded_sizes": sorted(decoded_sizes),
        "decode_failures": decode_failures,
        "packed_extent_overlaps": overlaps,
        "packed_region": (
            f"0x{GBA_BASE + extents[0][0]:08X}..0x{GBA_BASE + extents[-1][1]:08X}"
            if extents
            else None
        ),
    }


# --- engine binding, read from raw halfwords (no disassembler) ----------------

def _u16(data: bytes, addr: int) -> int:
    return struct.unpack_from("<H", data, addr - GBA_BASE)[0]


def thumb_ldr_literal_pool(data: bytes, address: int) -> tuple[int, int]:
    """``(pool address, destination register)`` for a Thumb ``ldr Rt,[pc,#imm]``.

    Refuses any other encoding rather than returning a plausible number.
    """
    halfword = _u16(data, address)
    if (halfword & 0xF800) != 0x4800:
        raise ValueError(f"no Thumb ldr-literal at 0x{address:08X}: 0x{halfword:04X}")
    register = (halfword >> 8) & 7
    pool = ((address + 4) & ~3) + (halfword & 0xFF) * 4
    return pool, register


def thumb_bl_target(data: bytes, address: int) -> int:
    """The absolute target of the Thumb ``bl`` encoded at ``address``.

    The guard is the **ARMv4T** form the GBA's ARM7TDMI emits: ``11110 imm11``
    then ``11111 imm11``, i.e. ``(second & 0xF800) == 0xF800``. That is stricter
    than the Thumb-2 ``11 J1 1 J2 imm11`` shape, and deliberately so: bit 13 of
    the second halfword is J1 in Thumb-2 and a fixed 1 in ARMv4T, so accepting an
    unconstrained bit 13 would decode a non-``bl`` pair into a plausible-looking
    target instead of refusing it. On the ARMv4T form ``J1 == J2 == 1``, and the
    offset arithmetic below then reduces exactly to the 23-bit ARMv4T one. Only
    the *arithmetic* is shared: the guard accepts the ARMv4T shape alone, so this
    helper is ARMv4T-scoped and must not be reused unrevised on a Thumb-2 image.
    """
    first = _u16(data, address)
    second = _u16(data, address + 2)
    if (first & 0xF800) != 0xF000 or (second & 0xF800) != 0xF800:
        raise ValueError(f"no Thumb bl at 0x{address:08X}")
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    offset = (sign << 24) | (i1 << 23) | (i2 << 22) | ((first & 0x3FF) << 12)
    offset |= (second & 0x7FF) << 1
    if sign:
        offset -= 1 << 25
    return address + 4 + offset


def _literal_pool_of(data: bytes, site: int) -> dict:
    """The PC-relative literal pool a load site addresses, derived not assumed.

    Reporting the *derived* pool address means the evidence does not depend on
    this module repeating an address the instruction already encodes.
    """
    pool, register = thumb_ldr_literal_pool(data, site)
    value = _u32(data, pool)
    return {
        "load_site": f"0x{site:08X}",
        "derived_pool_address": f"0x{pool:08X}",
        "destination_register": f"r{register}",
        "value": f"0x{value:08X}",
    }


def portrait_field_evidence(data: bytes) -> dict:
    """The engine binding that makes the portrait field the appearance table's.

    Returns the observed halfwords, the derived literal pools and the accessor
    call target, so a caller can assert the binding instead of trusting prose.
    """
    table_load_site = PORTRAIT_FIELD_HALFWORDS["consumer_table_literal_load"][0]
    array_load_site = PORTRAIT_FIELD_HALFWORDS["accessor_array_literal_load"][0]
    table_pool = _literal_pool_of(data, table_load_site)
    array_pool = _literal_pool_of(data, array_load_site)
    return {
        "table_address": f"0x{APPEARANCE_TABLE_ADDRESS:08X}",
        "portrait_offset": f"0x{APPEARANCE_PORTRAIT_OFFSET:02X}",
        "record_size": APPEARANCE_RECORD_SIZE,
        "record_count": APPEARANCE_RECORD_COUNT,
        "halfwords": {
            name: {
                "address": f"0x{address:08X}",
                "expected": f"0x{expected:04X}",
                "observed": f"0x{_u16(data, address):04X}",
                "matches": _u16(data, address) == expected,
            }
            for name, (address, expected) in PORTRAIT_FIELD_HALFWORDS.items()
        },
        "consumer_table_pool_word": {
            **table_pool,
            "expected_pool_address": f"0x{CONSUMER_TABLE_POOL_WORD:08X}",
            "is_appearance_table": table_pool["value"]
            == f"0x{APPEARANCE_TABLE_ADDRESS:08X}",
        },
        "consumer_portrait_call_target": (
            f"0x{thumb_bl_target(data, CONSUMER_PORTRAIT_CALL_SITE):08X}"
        ),
        "portrait_array_pool_word": {
            **array_pool,
            "expected_pool_address": f"0x{PORTRAIT_ARRAY_POOL_WORD:08X}",
            "is_portrait_array_base": array_pool["value"]
            == f"0x{portrait_array_base(data):08X}",
        },
    }


# --- the completeness join ---------------------------------------------------

def join_portrait_references(
    slots: Sequence[int],
    *,
    first_run_slot: int = FIRST_ARRAY_SLOT,
    last_run_slot: int = logx_char_probe.FIELD_08_VALID_SLOT_LAST,
) -> dict:
    """Join portrait field values to the run's valid slots. Pure arithmetic.

    ``slots`` is the portrait field of every appearance-definition record, in
    record order.

    Three cases are counted apart rather than merged, because merging them would
    hide the only failure modes this join exists to catch:

    * ``0`` is **no portrait**: the accessor returns zero without reading the
      array, so the record carries no reference.
    * A value in ``1..first_run_slot-1`` is **reserved**: the accessor returns 0
      for slots 0 and 7, and for 1..6 takes its party path, so such a value never
      indexes a run entry. It is non-zero and therefore counted in
      ``with_reference``, but it is neither inside nor outside the run.
    * A value above ``last_run_slot`` indexes **past the measured run**.

    ``with_reference`` is therefore "non-zero field". For a well-formed
    population it equals ``references_inside_run + references_outside_run`` +
    ``reserved_references``; the separate buckets say so when it does not. A
    negative value is impossible for a field the engine reads with ``ldr`` as an
    unsigned word, so it is **rejected** rather than bucketed: a negative input
    means the caller built the population wrongly, and silently reporting a
    self-contradictory join would hide that.
    """
    if first_run_slot <= 0:
        raise ValueError("first_run_slot must be positive")
    if last_run_slot < first_run_slot:
        raise ValueError("last_run_slot must not precede first_run_slot")
    negative = sorted({value for value in slots if value < 0})
    if negative:
        raise ValueError(f"portrait field values must not be negative: {negative[:8]}")

    run_slots = set(range(first_run_slot, last_run_slot + 1))
    zero = [value for value in slots if value == 0]
    reserved = sorted({value for value in slots if 0 < value < first_run_slot})
    outside = sorted({value for value in slots if value > last_run_slot})
    in_run = {value for value in slots if first_run_slot <= value <= last_run_slot}
    non_zero = {value for value in slots if value != 0}

    with_reference = len(slots) - len(zero)
    unused = sorted(run_slots - in_run)
    return {
        "records": len(slots),
        "with_reference": with_reference,
        "without_reference": len(zero),
        "references": with_reference,
        "unique_references": len(non_zero),
        # Reported separately: the in-run range says what the run must cover, the
        # whole non-zero range says how far the field strays from it.
        "min_in_run_reference": min(in_run) if in_run else None,
        "max_in_run_reference": max(in_run) if in_run else None,
        "min_non_zero_reference": min(non_zero) if non_zero else None,
        "max_non_zero_reference": max(non_zero) if non_zero else None,
        "references_inside_run": sum(
            1 for value in slots if first_run_slot <= value <= last_run_slot
        ),
        "references_outside_run": sum(1 for value in slots if value > last_run_slot),
        "reserved_references": sum(
            1 for value in slots if 0 < value < first_run_slot
        ),
        "reserved_values": reserved,
        "outside_values": outside,
        "run_first_slot": first_run_slot,
        "run_last_slot": last_run_slot,
        "run_entries": len(run_slots),
        "run_entries_referenced": len(in_run),
        "run_entries_unused": len(unused),
        "unused_slots": unused,
        "references_outside_run_is_empty": not outside,
    }


def appearance_portrait_slots(data: bytes) -> list[int]:
    """The portrait field of every appearance-definition record, in order."""
    return [record.field_08 for record in logx_char_probe.iter_records(data)]


def definition_run_portrait_field_report(data: bytes) -> dict:
    """Whether the 297-entry ``+0x04`` run's records carry a portrait slot.

    Reported so the corrected premise is measured, not asserted: if those
    records carried slot indices the field would be the run's, not the
    appearance table's.
    """
    pointers = [
        _u32(data, DEFINITION_RUN_ADDRESS + 4 * index)
        for index in range(DEFINITION_RUN_COUNT)
    ]
    values = [_u32(data, pointer + APPEARANCE_PORTRAIT_OFFSET) for pointer in pointers]
    in_slot_range = [
        value
        for value in values
        if value == 0 or FIRST_ARRAY_SLOT <= value <= logx_char_probe.FIELD_08_VALID_SLOT_LAST
    ]
    return {
        "run_address": f"0x{DEFINITION_RUN_ADDRESS:08X}",
        "run_entries": len(pointers),
        "field_offset": f"0x{APPEARANCE_PORTRAIT_OFFSET:02X}",
        "distinct_values": len(set(values)),
        "zero_values": sum(1 for value in values if value == 0),
        "values_in_portrait_slot_range": len(in_slot_range),
        "non_zero_values_in_portrait_slot_range": sum(
            1 for value in in_slot_range if value != 0
        ),
        # True only if *every* record's field is either "no portrait" or a slot
        # index the accessor could resolve. False means these records do not
        # carry a portrait field at this offset.
        "carries_portrait_slot_indices": len(in_slot_range) == len(values),
    }


def other_portrait_slot_sources(data: bytes) -> dict:
    """Portrait-slot sources other than the appearance-definition ``+0x08``.

    The accessor is reached from three callers: one reads the appearance table's
    ``+0x08`` directly, one reads the same field through an object cache, and one
    resolves a slot through the accessor's own slots-1..6 party path - a byte of
    the 24-byte-stride table at ``0x086B82EC``. Reporting the party-table values
    here, and every literal load of the portrait-array base, is what makes the
    "no source escapes the run" statement reproducible from the tracked tree
    instead of from a scratch script.

    Scope, stated rather than implied: ``array_base_literal_sites`` comes from a
    raw halfword scan of every even offset for the ``ldr Rt,[pc,#imm]`` encoding.
    That scan is resynchronising by construction, so it does not carry the
    linear-sweep false negative; its gap is that ``add Rd,pc,#imm``, ARM-state
    and register-computed bases are invisible to it. It is evidence of two
    *literal* sites, not proof that no other code reaches the array.
    """
    records = max(0, (PARTY_RECORD_TABLE_END - PARTY_RECORD_TABLE_ADDRESS))
    records //= PARTY_RECORD_STRIDE
    low, high = PARTY_SLOT_RANGE
    party_values = {
        data[PARTY_RECORD_TABLE_ADDRESS + PARTY_RECORD_STRIDE * index
             + PARTY_SLOT_BYTE_BASE + slot - GBA_BASE]
        for index in range(records)
        for slot in range(low, high + 1)
    }
    party_in_run = {value for value in party_values
                    if FIRST_ARRAY_SLOT <= value <= logx_char_probe.FIELD_08_VALID_SLOT_LAST}

    base = portrait_array_base(data)
    literal_sites = logx_char_probe.thumb_ldr_literal_sites(data)
    array_sites = [
        {"site": f"0x{site:08X}", "register": f"r{register}", "pool": f"0x{pool:08X}"}
        for site, register, pool in sorted(literal_sites.get(base, []))
    ]
    table_sites = len(literal_sites.get(APPEARANCE_TABLE_ADDRESS, []))

    appearance_in_run = {
        value
        for value in appearance_portrait_slots(data)
        if FIRST_ARRAY_SLOT <= value <= logx_char_probe.FIELD_08_VALID_SLOT_LAST
    }
    union = appearance_in_run | party_in_run
    run_slots = set(
        range(FIRST_ARRAY_SLOT, logx_char_probe.FIELD_08_VALID_SLOT_LAST + 1)
    )
    return {
        "party_record_table_address": f"0x{PARTY_RECORD_TABLE_ADDRESS:08X}",
        "party_record_stride": PARTY_RECORD_STRIDE,
        "party_records_scanned": records,
        "party_slot_range": [low, high],
        "party_slot_values": sorted(party_values),
        "party_distinct_values": len(party_values),
        "party_min_slot": min(party_values) if party_values else None,
        "party_max_slot": max(party_values) if party_values else None,
        "party_values_outside_run": sorted(
            value for value in party_values if value > logx_char_probe.FIELD_08_VALID_SLOT_LAST
        ),
        "array_base_literal_sites": array_sites,
        "array_base_literal_site_count": len(array_sites),
        "appearance_table_literal_site_count": table_sites,
        "inline_party_array_site": f"0x{INLINE_PARTY_ARRAY_SITE:08X}",
        "union_run_entries_covered": len(union),
        "run_entries_covered_by_no_source": len(run_slots - union),
        "scan_encoding_covered": "ldr Rt,[pc,#imm] at every even offset",
        "scan_gap": "add Rd,pc,#imm, ARM state and register-computed bases",
    }


def portrait_reference_report(data: bytes) -> dict:
    """The completeness join: the appearance table's portrait field vs the run."""
    join = join_portrait_references(appearance_portrait_slots(data))
    return {
        "rom_sha256": CANONICAL_SHA256.upper(),
        "appearance_table_address": f"0x{APPEARANCE_TABLE_ADDRESS:08X}",
        "appearance_record_size": APPEARANCE_RECORD_SIZE,
        "appearance_record_count": APPEARANCE_RECORD_COUNT,
        "appearance_portrait_offset": f"0x{APPEARANCE_PORTRAIT_OFFSET:02X}",
        "portrait_array_base": f"0x{portrait_array_base(data):08X}",
        "run_entry_count": len(portrait_pointers(data)),
        "join": join,
        "second_population": definition_run_portrait_field_report(data),
        "other_portrait_slot_sources": other_portrait_slot_sources(data),
        "engine_binding": portrait_field_evidence(data),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", help="canonical Buu's Fury ROM (read-only)")
    parser.add_argument("--json", help="write the report to this path")
    parser.add_argument(
        "--references",
        action="store_true",
        help="emit the appearance-definition completeness join only",
    )
    args = parser.parse_args(argv)

    data = load_rom(args.rom)
    report = (
        portrait_reference_report(data)
        if args.references
        else enumerate_portraits(data) | {"references": portrait_reference_report(data)}
    )
    text = json.dumps(report, indent=2)
    print(text)
    if args.json:
        Path(args.json).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
