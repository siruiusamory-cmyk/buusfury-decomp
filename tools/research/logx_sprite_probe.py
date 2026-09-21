"""Read-only sprite-definition / animation-table census for LOGX-SPRITE-001.

The probe answers, deterministically and without writing to the image:

* what each of the 297 entries in the accepted ``+0x04`` pointer run points to,
  and how the run relates to the accessor's compiler-folded arithmetic base;
* the physical layout of a sprite-definition object, including the inline
  32-bit pointer array the project's accepted run sits immediately after;
* the byte the engine uses as that array's index bound, with the five
  instructions that read it and compare it against an array index;
* the animation records the array's entries point to, and the frame records
  those in turn point to, stopping at the animation boundary that
  LOGX-FRAME-001 inherits.

Names are positional, not semantic.  ``definition``, ``animation`` and ``frame``
name three levels of the *physical* structure the engine walks; the accepted ROM
bible (``docs/research/GRAPHICS_FORMAT.md``) already calls the second and third
levels an animation record and a frame record, and this probe keeps those names
so the two documents cannot drift.  Field names inside each level stay neutral
(``field_04_raw``, ``array``, ``byte_04``) until an engine instruction justifies
a meaning.  The two names this ticket does promote - the byte at
``definition + 0x00`` as the inline array's element count, and
``definition + 0x54`` as that inline array - are promoted only because five
engine sites read the byte and then compare it against the index of an element
they are about to load; those five sites are listed in
:data:`COUNT_GUARD_SITES` and re-read by the ROM-gated suite.

Evidence provenance labels follow ``docs/research-conventions.md``.  Addresses
are GBA addresses; a file offset is an address minus ``0x08000000``.

**Dependency boundary.**  The census, definition, animation and frame arithmetic
are pure: they need only the standard library.  Capstone is needed *only* to read
instruction text, so that import is deferred to first use: ``tools.research.
thumb_disasm`` raises ``SystemExit`` when capstone is absent, and CI's portable
unit job installs only ``.[dev]``.  An environment without capstone can still
import this module, run the whole census API and use the ``--rows`` / ``--run``
reports; only ``--engine``, :func:`instruction_at` and
:func:`format_instruction` require it.

The probe performs no I/O beyond reading the caller's bytes, and it never mutates
the canonical image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Sequence

from tools.research import logx_char_probe

CANONICAL_SHA256 = "940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E"
ROM_SIZE = 8 * 1024 * 1024
ROM_BASE = 0x08000000

#: GBA address of the reference window into the sprite-definition (``+0x04``)
#: pointer run.  This is the word the accessor ``0x08000158`` loads as its
#: literal, and it is entry ``id == 10``: the accessor's real first index.
#:
#: EXTERNAL CLAIM (mainant/LOGExtractor): the sprite-definition pointer table
#: begins at file offset ``0x6B6BB4``.  The project's accepted run begins here,
#: 40 bytes higher; that disagreement is resolved by measurement, not inherited.
#: The definition at ``0x086B6B60`` is 0x7C bytes long and its own inline array
#: occupies ``0x086B6BB4..0x086B6BD8``, which is exactly what the folded base
#: points at.  See :func:`folded_base_explanation`.
DEFINITION_ARRAY_ADDRESS = 0x086B6BDC

#: File offset of :data:`DEFINITION_ARRAY_ADDRESS`.
DEFINITION_ARRAY_FILE_OFFSET = DEFINITION_ARRAY_ADDRESS - ROM_BASE

#: Entries in the accepted run: ids ``10..306`` inclusive.
DEFINITION_ARRAY_ENTRY_COUNT = 297

#: The smallest caller-visible id the accessor resolves through the array.
DEFINITION_ID_FLOOR = 10

#: The largest caller-visible id the canonical image uses (appearance ``+0x04``).
DEFINITION_ID_LAST_USED = 306

#: The accessor's compiler-folded arithmetic base: ``literal - 4 * 10``.
#: It is **not** the first entry of the run; it is the first word of the last
#: definition object's inline array.  Kept as its own constant so the two
#: readings can never be silently merged.
FOLDED_ARITHMETIC_BASE = DEFINITION_ARRAY_ADDRESS - 4 * DEFINITION_ID_FLOOR

#: The engine accessor: for ``id >= 10`` it returns
#: ``u32 at DEFINITION_ARRAY_ADDRESS + 4*id - 0x28``.
DEFINITION_ACCESSOR = 0x08000158

#: A second entry to the same array.  It has **no** party-slot branch: it reads
#: the id from a 16-bit field of its argument and applies the identical
#: arithmetic, which is how ids below the floor can still reach the array.
DEFINITION_ACCESSOR_RECORD = 0x0801713C

#: The character-object constructor that consumes a definition.
CHARACTER_CTOR = 0x0800EB60

#: The re-skin / morph entry: swaps the definition a live object uses.
CHARACTER_MORPH = 0x0800EDF8

#: Physical field offsets inside a sprite-definition object.  Names are
#: positions except where an engine consumer supports a meaning.
FIELD_COUNT = 0x00  # u16; the low byte bounds the inline array at +0x54
FIELD_SIZE = 0x02  # u16; passed to the allocator 0x0803D5B8 as a byte size
FIELD_04 = 0x04
FIELD_08 = 0x08
FIELD_0C = 0x0C
FIXED_BLOCK_START = 0x10
FIXED_BLOCK_END = 0x50
FIELD_50 = 0x50
FIELD_ARRAY = 0x54

#: The four 16-byte records that occupy ``+0x10 .. +0x4F``.
FIXED_BLOCK_RECORDS = 4
FIXED_BLOCK_RECORD_SIZE = 0x10

#: Every definition observed in the canonical image has an element count in
#: ``1..23``.  This is a *measured data range*, not an engine bound: no
#: instruction in the image compares the count against 23.
COUNT_MIN = 1
COUNT_MAX = 23

#: The definition object ends at ``+0x54 + 4 * count``; 232 of the 297 canonical
#: objects are packed with exactly that stride, and the remaining 65 are followed
#: by a 256-byte block that the object's own ``+0x04`` points at.
OBJECT_HEADER_SIZE = FIELD_ARRAY

#: The 256-byte block that separates 65 of the 297 structures.  It is a
#: near-identity byte permutation (index -> replacement index) with a handful of
#: substitutions, which is the shape of a palette-index remap; ``+0x04`` holds
#: its address and nothing else in the object does.  The *pointer relationship*
#: is CONFIRMED (65 of 65); the palette reading is INFERRED.
REMAP_BLOCK_SIZE = 0x100

#: Physical layout of an *animation record*: the structure an element of the
#: definition's inline array points at.  ``frame_count`` and the four
#: direction slots are the accepted ROM-bible names; the engine reaches slot
#: ``direction`` of frame ``frame`` as ``animation[16*frame + 4*direction + 4]``.
ANIM_FRAME_COUNT = 0x00  # u32
ANIM_DIRECTIONS = 4  # pointers per frame
ANIM_POINTERS = 0x04

#: Physical layout of a *frame record*: ``u32 piece_count``, the frame's own
#: bounding box (the four bytes below), then that many **12-byte** piece records
#: beginning at ``+0x08``.  LOGX-FRAME-001 established the accepted layout; this
#: module was corrected to it by EVIDENCE-RISK-DEBT-001, having previously read a
#: 4-byte header and a 16-byte stride.  Only the record's extent and the four
#: bounding-box bytes are recorded here; everything below the count is
#: LOGX-FRAME-001's.
FRAME_PIECE_COUNT = 0x00  # u32
FRAME_FIRST_PIECE = 0x08
PIECE_RECORD_SIZE = 0x0C
FRAME_FIELD_04 = 0x04  # s8, the minimum piece x, read with ldrsb
FRAME_FIELD_05 = 0x05  # s8, the minimum piece y, read with ldrsb
FRAME_FIELD_06 = 0x06  # u8, the width of the pieces' union, read with ldrb
FRAME_FIELD_07 = 0x07  # u8, the height of the pieces' union, read with ldrb

#: The translation table that maps a *state* number to an animation index.  It
#: is read by ``0x0800ECF0`` and ``0x0800ED3E`` as ``ldrb rX,[base+0x88+r1]``
#: where ``base`` is the literal ``0x080725E8``.
STATE_TABLE_LITERAL = 0x080725E8
STATE_TABLE_OFFSET = 0x88
STATE_TABLE_ADDRESS = STATE_TABLE_LITERAL + STATE_TABLE_OFFSET

#: The largest index the state table maps; entries above it are zero.
STATE_TABLE_SIZE = 25

#: The four sites that read the state -> animation-index table.  Two reach it
#: from :data:`STATE_TABLE_LITERAL` with ``adds #0x88``; one reaches it from the
#: only ``ldr Rt,[pc,#imm]`` in the whole image whose pool word is the table
#: address; and one reaches it from the *other* literal in the same structure
#: (``0x080725F0``) with ``adds #0x80``.  The last is a predicate, not an
#: assignment: it compares the animation the state maps to against the one the
#: object currently has.
STATE_TABLE_LOOKUP_SITES = (0x0800ECF6, 0x0800ED48, 0x0802CB96, 0x0800EEB6)
STATE_TABLE_LITERAL_SITES = (0x0800ECF4, 0x0800ED46)
STATE_TABLE_ADDRESS_LITERAL_SITE = 0x0802CB94

#: The ``cmp`` that null-tests the element each guarded array load produced.  The
#: engine checks both that the animation index exists (the count compare) and
#: that the element is non-null; the branch that acts on the test is the
#: instruction after each of these.
COUNT_GUARD_NULL_TESTS = (0x0801304E, 0x08013090, 0x080131E2, 0x08027374, 0x0802A296)

#: The direct animation selector: ``(obj, index)`` assigns
#: ``*(u32*)(definition + 0x54 + 4*index)`` to ``obj+0x50`` and has no range
#: check.  It has 162 ``BL`` call sites, 161 of them with a compile-time
#: constant in ``0..21``; whether a definition actually has that index is a data
#: property, which is why the count's five guarded reads exist.
ANIMATION_SELECTOR = 0x0800ECDA

#: Instruction sites that read ``definition + 0x00`` as a byte and compare it
#: against the index of the inline-array element they then load.  The five sites
#: cover indices 1, 6, 7 and 8, and they are what promotes the byte from a
#: physical field to an array bound.  Each is asserted by a test.
COUNT_GUARD_SITES: tuple[tuple[int, int, int, int], ...] = (
    # (definition pointer load, count load, compare, array element load)
    (0x08013044, 0x08013046, 0x08013048, 0x0801304C),  # index 7, +0x70
    (0x08013086, 0x08013088, 0x0801308A, 0x0801308E),  # index 8, +0x74
    (0x080131D8, 0x080131DA, 0x080131DC, 0x080131E0),  # index 7, +0x70
    (0x0802736A, 0x0802736C, 0x0802736E, 0x08027372),  # index 1, +0x58
    (0x0802A28A, 0x0802A28E, 0x0802A290, 0x0802A294),  # index 6, +0x6C
)

#: The engine instructions this ticket quotes, as ``name -> (address, text)``.
#: Reading them back needs capstone (see the dependency boundary).
EVIDENCE_INSTRUCTIONS: dict[str, tuple[int, str]] = {
    # --- the two accessors -------------------------------------------------
    "accessor_floor": (0x0800015A, "cmp r0, #0xa"),
    "accessor_floor_branch": (0x0800015C, "blt #0x800016a"),
    "accessor_literal": (0x0800015E, "ldr r1, [pc, #0x260]"),
    "accessor_scale": (0x08000160, "lsls r0, r0, #2"),
    "accessor_base": (0x08000162, "adds r0, r0, r1"),
    "accessor_fold": (0x08000164, "subs r0, #0x40"),
    "accessor_load": (0x08000166, "ldr r0, [r0, #0x18]"),
    "record_accessor_id": (0x0801713C, "ldrh r0, [r0, #0xe]"),
    "record_accessor_literal": (0x0801713E, "ldr r1, [pc, #0x1c]"),
    "record_accessor_scale": (0x08017140, "lsls r0, r0, #2"),
    "record_accessor_base": (0x08017142, "adds r0, r0, r1"),
    "record_accessor_fold": (0x08017144, "subs r0, #0x40"),
    "record_accessor_load": (0x08017146, "ldr r0, [r0, #0x18]"),
    # --- the definition's fields, as the constructor reads them ------------
    "definition_size_load": (0x0800EB7C, "ldrh r5, [r6, #2]"),
    "definition_50_load": (0x0800EBB6, "ldr r0, [r6, #0x50]"),
    "definition_array_load": (0x0800EBD0, "ldr r0, [r6, #0x54]"),
    "definition_array_store": (0x0800EBD2, "str r0, [r4, #0x50]"),
    "definition_04_load": (0x0800EBF6, "ldr r1, [r0, #4]"),
    "definition_size_alloc": (0x0800EC00, "ldrh r0, [r0, #2]"),
    "definition_0b_load": (0x0800EC0A, "ldrb r1, [r0, #0xb]"),
    "definition_0a_load": (0x0800EC0C, "ldrb r0, [r0, #0xa]"),
    # --- the count-guarded inline-array reads ------------------------------
    "guard_7_pointer": (0x08013044, "ldr r0, [r4, #0x58]"),
    "guard_7_count": (0x08013046, "ldrb r1, [r0]"),
    "guard_7_compare": (0x08013048, "cmp r1, #7"),
    "guard_7_branch": (0x0801304A, "bls #0x8013078"),
    "guard_7_array": (0x0801304C, "ldr r0, [r0, #0x70]"),
    "guard_8_pointer": (0x08013086, "ldr r0, [r4, #0x58]"),
    "guard_8_count": (0x08013088, "ldrb r1, [r0]"),
    "guard_8_compare": (0x0801308A, "cmp r1, #8"),
    "guard_8_branch": (0x0801308C, "bls #0x80130a4"),
    "guard_8_array": (0x0801308E, "ldr r0, [r0, #0x74]"),
    "guard_7b_pointer": (0x080131D8, "ldr r0, [r4, #0x58]"),
    "guard_7b_count": (0x080131DA, "ldrb r1, [r0]"),
    "guard_7b_compare": (0x080131DC, "cmp r1, #7"),
    "guard_7b_branch": (0x080131DE, "bls #0x8013210"),
    "guard_7b_array": (0x080131E0, "ldr r0, [r0, #0x70]"),
    "guard_1_pointer": (0x0802736A, "ldr r1, [r0, #0x58]"),
    "guard_1_count": (0x0802736C, "ldrb r2, [r1]"),
    "guard_1_compare": (0x0802736E, "cmp r2, #1"),
    "guard_1_branch": (0x08027370, "bls #0x8027368"),
    "guard_1_array": (0x08027372, "ldr r1, [r1, #0x58]"),
    "guard_6_pointer": (0x0802A28A, "ldr r0, [r1, #0x58]"),
    "guard_6_count": (0x0802A28E, "ldrb r1, [r0]"),
    "guard_6_compare": (0x0802A290, "cmp r1, #6"),
    "guard_6_branch": (0x0802A292, "bls #0x802a29a"),
    "guard_6_array": (0x0802A294, "ldr r2, [r0, #0x6c]"),
    # --- animation selection ----------------------------------------------
    "select_direct_pointer": (0x0800ECDA, "ldr r2, [r0, #0x58]"),
    "select_direct_scale": (0x0800ECDC, "lsls r1, r1, #2"),
    "select_direct_base": (0x0800ECDE, "adds r3, r2, r1"),
    "select_direct_load": (0x0800ECE0, "ldr r3, [r3, #0x54]"),
    "select_direct_store": (0x0800ECE2, "str r3, [r0, #0x50]"),
    "select_state_literal": (0x0800ECF0, "ldr r2, [pc, #0xec]"),
    "select_state_offset": (0x0800ECF4, "adds r2, #0x88"),
    "select_state_lookup": (0x0800ECF6, "ldrb r3, [r2, r1]"),
    "select_state_definition": (0x0800ECF8, "ldr r2, [r0, #0x58]"),
    "select_state_array": (0x0800ECFE, "ldr r4, [r4, #0x54]"),
    "select_state_entry": (0x0800ED3E, "push {r3, r4, r5, lr}"),
    "select_state2_offset": (0x0800ED46, "adds r0, #0x88"),
    "select_state2_lookup": (0x0800ED48, "ldrb r1, [r0, r1]"),
    "select_state2_definition": (0x0800ED4A, "ldr r0, [r4, #0x58]"),
    "select_state2_array": (0x0800ED50, "ldr r2, [r2, #0x54]"),
    "select_state2_row": (0x0800ED7C, "strb r5, [r4, #0x11]"),
    # --- part selection ----------------------------------------------------
    "part_row": (0x0800EF38, "ldrb r2, [r0, #0x11]"),
    "part_base": (0x0800EF3A, "ldr r1, [r0, #0x50]"),
    "part_row_scale": (0x0800EF3C, "lsls r2, r2, #4"),
    "part_row_add": (0x0800EF3E, "adds r1, r1, r2"),
    "part_column": (0x0800EF40, "ldrb r2, [r0, #0x10]"),
    "part_column_scale": (0x0800EF42, "lsls r2, r2, #2"),
    "part_column_add": (0x0800EF44, "adds r1, r1, r2"),
    "part_load": (0x0800EF46, "ldr r1, [r1, #4]"),
    "part_store": (0x0800EF48, "str r1, [r0, #0x54]"),
    # --- part record fields, as the constructor reads them ------------------
    "part_ctor_store": (0x080273E4, "str r1, [r4, #0x54]"),
    "part_ctor_origin_x": (0x080273F0, "ldrsb r7, [r1, r3]"),
    "part_ctor_origin_y": (0x080273F4, "ldrsb r1, [r1, r3]"),
    "part_ctor_width": (0x0802740C, "ldrb r2, [r3, #6]"),
    "part_ctor_height": (0x08027410, "ldrb r3, [r3, #7]"),
    # --- the definition's +0x08 byte, used as a screen offset ---------------
    "definition_08_pointer": (0x0800EF6C, "ldr r4, [r1, #0x58]"),
    "definition_08_byte": (0x0800EF74, "ldrb r4, [r4, #8]"),
}

#: Every ``ldr Rt,[pc,#imm]`` site whose literal word is the definition array
#: address.  A raw halfword scan over every even offset of the whole image.
DEFINITION_ARRAY_LITERAL_SITES = (0x0800015E, 0x0801713E)


class SpriteProbeError(RuntimeError):
    """Raised when the image or the requested report cannot be produced."""


# --- byte helpers ------------------------------------------------------------


def _u8(data: bytes, address: int) -> int:
    return data[address - ROM_BASE]


def _u16(data: bytes, address: int) -> int:
    return struct.unpack_from("<H", data, address - ROM_BASE)[0]


def _u32(data: bytes, address: int) -> int:
    return struct.unpack_from("<I", data, address - ROM_BASE)[0]


def _s8(value: int) -> int:
    return value - 0x100 if value & 0x80 else value


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def verify_canonical(data: bytes) -> None:
    """Fail closed unless ``data`` is the canonical Buu's Fury image."""
    if len(data) != ROM_SIZE:
        raise SpriteProbeError(f"image is {len(data)} bytes, expected {ROM_SIZE}")
    actual = sha256_of(data)
    if actual != CANONICAL_SHA256:
        raise SpriteProbeError(
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


# --- the pointer run ---------------------------------------------------------


def definition_entry_address(index: int) -> int:
    """GBA address of run entry ``index`` (0-based over the 297 accepted entries)."""
    if not 0 <= index < DEFINITION_ARRAY_ENTRY_COUNT:
        raise SpriteProbeError(
            f"run index {index} is outside 0..{DEFINITION_ARRAY_ENTRY_COUNT - 1}"
        )
    return DEFINITION_ARRAY_ADDRESS + 4 * index


def run_index_for_id(identifier: int) -> int:
    """The run index the accessor resolves ``identifier`` to.

    Mirrors ``0x08000158`` exactly: ``address = folded_base + 4*id``.  Only ids
    at or above the accessor's floor read the array at all; below it the
    accessor takes its party-slot branch and never touches these bytes.
    """
    if identifier < DEFINITION_ID_FLOOR:
        raise SpriteProbeError(
            f"id {identifier} is below the accessor's floor {DEFINITION_ID_FLOOR}; "
            "the accessor takes its party-slot branch instead"
        )
    return identifier - DEFINITION_ID_FLOOR


def definition_pointer(data: bytes, identifier: int) -> int:
    """The word the accessor returns for ``identifier``.

    It does **not** claim the word is a structure of any particular kind; the
    definition's own layout is established by :func:`read_definition` and the
    instructions the engine uses to walk it.
    """
    return _u32(data, FOLDED_ARITHMETIC_BASE + 4 * identifier)


def read_run(data: bytes) -> list[int]:
    """All 297 entries of the accepted run, as raw words."""
    return [
        _u32(data, definition_entry_address(index))
        for index in range(DEFINITION_ARRAY_ENTRY_COUNT)
    ]


def run_report(data: bytes) -> dict[str, Any]:
    """Shape of the accepted pointer run and of the folded base below it."""
    entries = read_run(data)
    pre_run = [_u32(data, FOLDED_ARITHMETIC_BASE + 4 * index) for index in range(DEFINITION_ID_FLOOR)]
    return {
        "array_address": f"{DEFINITION_ARRAY_ADDRESS:#010x}",
        "array_file_offset": f"{DEFINITION_ARRAY_FILE_OFFSET:#08x}",
        "folded_arithmetic_base": f"{FOLDED_ARITHMETIC_BASE:#010x}",
        "entry_count": DEFINITION_ARRAY_ENTRY_COUNT,
        "first_id": DEFINITION_ID_FLOOR,
        "last_id": DEFINITION_ID_FLOOR + DEFINITION_ARRAY_ENTRY_COUNT - 1,
        "all_entries_in_rom": all(in_rom(data, value) for value in entries),
        "strictly_ascending": all(
            entries[i] < entries[i + 1] for i in range(len(entries) - 1)
        ),
        "unique_targets": len(set(entries)),
        "first_entry": f"{entries[0]:#010x}",
        "last_entry": f"{entries[-1]:#010x}",
        "word_before_run_hex": f"{_u32(data, DEFINITION_ARRAY_ADDRESS - 4):08x}",
        "word_after_run_hex": f"{_u32(data, DEFINITION_ARRAY_ADDRESS + 4 * len(entries)):08x}",
        "word_after_run_in_rom": in_rom(
            data, _u32(data, DEFINITION_ARRAY_ADDRESS + 4 * len(entries))
        ),
        "words_below_run": [f"{value:#010x}" for value in pre_run],
        "words_below_run_in_rom": sum(1 for value in pre_run if in_rom(data, value)),
        "words_below_run_null": sum(1 for value in pre_run if value == 0),
    }


def folded_base_explanation(data: bytes) -> dict[str, Any]:
    """Show that the folded base is the *last definition's inline array*.

    If the run's 297 entries are preceded by exactly one definition object whose
    own count is ``k``, then that object starts at ``base - 0x54 - 4*k`` and its
    inline array occupies ``base - 4*k .. base - 1``.  The report finds the
    object by walking backwards over the words below the run and checking the
    definition header signature, which keeps the claim arithmetic rather than
    interpretive.
    """
    base = DEFINITION_ARRAY_ADDRESS
    candidates = []
    for count in range(COUNT_MIN, COUNT_MAX + 1):
        start = base - OBJECT_HEADER_SIZE - 4 * count
        if start < ROM_BASE:
            continue
        header = _u32(data, start)
        if header_like(data, start) and (header & 0xFF) == count:
            candidates.append(
                {
                    "count": count,
                    "object_address": f"{start:#010x}",
                    "object_end": f"{start + OBJECT_HEADER_SIZE + 4 * count:#010x}",
                    "inline_array": f"{start + FIELD_ARRAY:#010x}",
                    "header_hex": f"{header:08x}",
                }
            )
    return {
        "accepted_run": f"{base:#010x}",
        "folded_arithmetic_base": f"{FOLDED_ARITHMETIC_BASE:#010x}",
        "objects_ending_at_run": candidates,
    }


# --- definitions -------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Definition:
    """One sprite-definition object, read at the engine's own width.

    ``count`` and ``size`` are the two halfwords the engine reads at ``+0x00``
    and ``+0x02``.  ``array`` holds ``count`` raw words read from ``+0x54``.
    """

    identifier: int
    address: int
    file_offset: int
    field_00: int
    field_02: int
    field_04: int
    field_08: int
    field_0C: int
    field_50: int
    array: tuple[int, ...]
    fixed_block: tuple[int, ...]

    @property
    def count(self) -> int:
        return self.field_00 & 0xFF

    @property
    def count_high(self) -> int:
        return (self.field_00 >> 8) & 0xFF

    @property
    def size(self) -> int:
        return self.field_02

    @property
    def end_address(self) -> int:
        return self.address + OBJECT_HEADER_SIZE + 4 * self.count

    @property
    def raw(self) -> bytes:
        """The object's bytes up to its end, at the engine's own extent model."""
        return (
            struct.pack(
                "<HHIII", self.field_00, self.field_02, self.field_04,
                self.field_08, self.field_0C,
            )
            + struct.pack(f"<{len(self.fixed_block)}I", *self.fixed_block)
            + struct.pack("<I", self.field_50)
            + struct.pack(f"<{len(self.array)}I", *self.array)
        )


def header_like(data: bytes, address: int) -> bool:
    """Whether ``address`` carries the canonical definition-header signature.

    Three invariants hold on all 297 accepted objects: the high byte of the
    first halfword is zero, the ``+0x02`` halfword is one of the eight observed
    allocation sizes, and the ``+0x08`` word is one of the observed constants.
    This is a *data* helper, used by :func:`folded_base_explanation`; it is not
    presented as an engine test.
    """
    if address < ROM_BASE or address + OBJECT_HEADER_SIZE > ROM_BASE + len(data):
        return False
    word = _u32(data, address)
    if not COUNT_MIN <= (word & 0xFF) <= COUNT_MAX:
        return False
    if (word >> 8) & 0xFF:
        return False
    if _u16(data, address + FIELD_SIZE) not in (
        0x0040, 0x0100, 0x0200, 0x0400, 0x0800, 0x1000, 0x1800, 0x2400,
    ):
        return False
    return True


def read_definition(data: bytes, identifier: int) -> Definition:
    """Read the object the accessor returns for ``identifier``."""
    address = definition_pointer(data, identifier)
    count = _u16(data, address + FIELD_COUNT)
    if not COUNT_MIN <= (count & 0xFF) <= COUNT_MAX or count >> 8:
        raise SpriteProbeError(
            f"definition at {address:#010x} has a non-canonical first halfword "
            f"{count:#06x}"
        )
    fixed = tuple(
        _u32(data, address + FIXED_BLOCK_START + 4 * i)
        for i in range((FIXED_BLOCK_END - FIXED_BLOCK_START) // 4)
    )
    array = tuple(
        _u32(data, address + FIELD_ARRAY + 4 * i) for i in range(count & 0xFF)
    )
    return Definition(
        identifier=identifier,
        address=address,
        file_offset=address - ROM_BASE,
        field_00=count,
        field_02=_u16(data, address + FIELD_SIZE),
        field_04=_u32(data, address + FIELD_04),
        field_08=_u32(data, address + FIELD_08),
        field_0C=_u32(data, address + FIELD_0C),
        field_50=_u32(data, address + FIELD_50),
        array=array,
        fixed_block=fixed,
    )


def iter_definitions(data: bytes) -> list[Definition]:
    """All 297 accepted definitions, in run order."""
    return [
        read_definition(data, DEFINITION_ID_FLOOR + index)
        for index in range(DEFINITION_ARRAY_ENTRY_COUNT)
    ]


# --- animations and parts ----------------------------------------------------


@dataclass(frozen=True, slots=True)
class Animation:
    """One animation record: ``frame_count`` and ``4 * frame_count`` pointers.

    The four pointers of one frame are the animation's *direction slots* in the
    accepted ROM bible.  The engine reaches slot ``direction`` of frame
    ``frame`` at ``address + 4 + 16 * frame + 4 * direction``; the two words
    after the pointer array are read by :func:`read_animation_tail` and are not
    interpreted here.
    """

    address: int
    frame_count: int
    pointers: tuple[int, ...]

    @property
    def end_address(self) -> int:
        return self.address + ANIM_POINTERS + 4 * len(self.pointers)

    def pointer_for(self, frame: int, direction: int) -> int:
        if not 0 <= frame < self.frame_count:
            raise SpriteProbeError(f"frame {frame} out of range")
        if not 0 <= direction < ANIM_DIRECTIONS:
            raise SpriteProbeError(f"direction slot {direction} out of range")
        return self.pointers[frame * ANIM_DIRECTIONS + direction]


def read_animation_tail(data: bytes, address: int) -> tuple[int, int, int]:
    """``(frame_count, trailer_0, trailer_1)`` for the animation at ``address``.

    ``trailer_0`` is the word after the last frame pointer and ``trailer_1`` the
    one after that.  They are recorded as raw words; this ticket makes no claim
    about them.
    """
    animation = read_animation(data, address)
    end = animation.end_address
    return animation.frame_count, _u32(data, end), _u32(data, end + 4)


def read_animation(data: bytes, address: int) -> Animation:
    """Read the animation record at ``address``."""
    if not in_rom(data, address):
        raise SpriteProbeError(f"animation address {address:#010x} is not in ROM")
    frames = _u32(data, address + ANIM_FRAME_COUNT)
    if frames == 0 or frames > 64:
        raise SpriteProbeError(
            f"animation at {address:#010x} has an implausible frame count {frames}"
        )
    pointers = tuple(
        _u32(data, address + ANIM_POINTERS + 4 * i)
        for i in range(frames * ANIM_DIRECTIONS)
    )
    return Animation(address=address, frame_count=frames, pointers=pointers)


@dataclass(frozen=True, slots=True)
class FrameRecord:
    """One frame record: a piece count, a bounding box and the pieces.

    ``piece_count`` is the leading word; the record's extent is therefore
    ``8 + 12 * piece_count``.  The four bytes at ``+0x04..+0x07`` - the ones the
    character constructor reads with ``ldrsb``/``ldrb`` - are the frame's own
    bounding box over its pieces: signed minimum x and y, then unsigned width and
    height.  Everything below the count belongs to LOGX-FRAME-001; this module
    records the extent and those four bytes.
    """

    address: int
    piece_count: int
    byte_04: int
    byte_05: int
    byte_06: int
    byte_07: int

    @property
    def end_address(self) -> int:
        return self.address + FRAME_FIRST_PIECE + PIECE_RECORD_SIZE * self.piece_count

    @property
    def signed_04(self) -> int:
        return _s8(self.byte_04)

    @property
    def signed_05(self) -> int:
        return _s8(self.byte_05)


def read_frame_record(data: bytes, address: int) -> FrameRecord:
    """Read the frame record at ``address``."""
    if not in_rom(data, address):
        raise SpriteProbeError(f"frame address {address:#010x} is not in ROM")
    return FrameRecord(
        address=address,
        piece_count=_u32(data, address + FRAME_PIECE_COUNT),
        byte_04=_u8(data, address + FRAME_FIELD_04),
        byte_05=_u8(data, address + FRAME_FIELD_05),
        byte_06=_u8(data, address + FRAME_FIELD_06),
        byte_07=_u8(data, address + FRAME_FIELD_07),
    )


def state_to_index_table(data: bytes) -> tuple[int, ...]:
    """The state -> animation-index byte table the engine reads at ``+0x88``."""
    return tuple(_u8(data, STATE_TABLE_ADDRESS + i) for i in range(STATE_TABLE_SIZE))


# --- census arithmetic (pure) ------------------------------------------------


#: The eight `definition + 0x02` halfwords the canonical image uses.  They are
#: *observed data values*, not an engine table: the engine only hands the
#: halfword to an allocator.  The census flags any other value rather than
#: pretending the set is a type enumeration.
KNOWN_ALLOCATION_SIZES = (0x0040, 0x0100, 0x0200, 0x0400, 0x0800, 0x1000, 0x1800, 0x2400)


@dataclass(frozen=True, slots=True)
class DefinitionLimits:
    """Bounds a census row is checked against, each with a stated source.

    ``count_min``/``count_max`` and ``known_allocations`` are the measured ranges
    of the canonical objects' fields, a *data* range and not an engine bound.
    ``index_max`` comes from the engine: the state table has 25 entries.
    """

    count_min: int = COUNT_MIN
    count_max: int = COUNT_MAX
    known_allocations: tuple[int, ...] = KNOWN_ALLOCATION_SIZES
    index_max: int = STATE_TABLE_SIZE - 1


def census_definitions(
    rows: Sequence[Sequence[int]], limits: DefinitionLimits | None = None
) -> dict[str, Any]:
    """Census over ``(field_00, field_02, field_04, field_08, field_0C, field_50)``.

    Pure: it takes plain integers so synthetic rows can exercise every anomaly
    branch without a ROM.  ``array`` is supplied separately as a sequence of
    tuples so the count/array relationship can be checked.
    """
    limits = limits or DefinitionLimits()
    counters = {
        "definitions": 0,
        "count_below_min": 0,
        "count_above_max": 0,
        "count_high_byte_nonzero": 0,
        "size_zero": 0,
        "size_not_a_known_allocation": 0,
        "field_04_zero": 0,
        "field_04_not_a_rom_pointer": 0,
        "field_0c_nonzero": 0,
        "field_50_zero": 0,
        "field_50_nonzero": 0,
    }
    allocations = set(limits.known_allocations)
    anomalies: list[dict[str, Any]] = []
    counts: dict[int, int] = {}
    for index, row in enumerate(rows):
        field_00, field_02, field_04, field_08, field_0C, field_50 = row
        counters["definitions"] += 1
        count = field_00 & 0xFF
        flags: list[str] = []
        if count < limits.count_min:
            flags.append("count_below_min")
            counters["count_below_min"] += 1
        if count > limits.count_max:
            flags.append("count_above_max")
            counters["count_above_max"] += 1
        if field_00 >> 8:
            flags.append("count_high_byte_nonzero")
            counters["count_high_byte_nonzero"] += 1
        counts[count] = counts.get(count, 0) + 1
        if field_02 == 0:
            flags.append("size_zero")
            counters["size_zero"] += 1
        elif field_02 not in allocations:
            flags.append("size_not_a_known_allocation")
            counters["size_not_a_known_allocation"] += 1
        if field_04 == 0:
            counters["field_04_zero"] += 1
        if field_0C:
            counters["field_0c_nonzero"] += 1
        if field_50:
            counters["field_50_nonzero"] += 1
        else:
            counters["field_50_zero"] += 1
        if flags:
            anomalies.append({"index": index, "flags": sorted(flags)})
    return {
        "counters": counters,
        "anomalies": anomalies,
        "count_distribution": dict(sorted(counts.items())),
        "distinct": {
            "field_00": len({row[0] for row in rows}),
            "field_02": len({row[1] for row in rows}),
            "field_04": len({row[2] for row in rows}),
            "field_08": len({row[3] for row in rows}),
            "field_0C": len({row[4] for row in rows}),
            "field_50": len({row[5] for row in rows}),
        },
    }


def census_array_slots(
    arrays: Sequence[Sequence[int]],
) -> dict[str, Any]:
    """Census of the inline pointer arrays: occupancy by position.

    Pure.  ``arrays`` is one sequence of raw words per definition, already
    truncated to that definition's count.
    """
    by_index: dict[int, dict[str, int]] = {}
    total = 0
    non_null = 0
    for array in arrays:
        total += len(array)
        for index, value in enumerate(array):
            bucket = by_index.setdefault(index, {"present": 0, "non_null": 0})
            bucket["present"] += 1
            if value:
                bucket["non_null"] += 1
                non_null += 1
    return {
        "total_slots": total,
        "non_null_slots": non_null,
        "null_slots": total - non_null,
        "by_index": {index: by_index[index] for index in sorted(by_index)},
        "index_zero_always_non_null": by_index.get(0, {}).get("present", 0)
        == by_index.get(0, {}).get("non_null", -1),
    }


def census_animation_pointers(
    pointers: Sequence[int], in_rom: Callable[[int], bool]
) -> dict[str, Any]:
    """Census of animation references: totals, uniqueness, sharing, nulls.

    Reference counts and unique-target counts are kept apart: 1,721 non-null
    slots over 1,017 unique animation records are two different populations, and
    a reader must be able to tell which is which.
    """
    seen: dict[int, int] = {}
    for value in pointers:
        if value:
            seen[value] = seen.get(value, 0) + 1
    return {
        "slots": len(pointers),
        "null_slots": sum(1 for value in pointers if not value),
        "non_null_slots": sum(1 for value in pointers if value),
        "unique_targets": len(seen),
        "malformed_slots": sum(1 for value in pointers if value and not in_rom(value)),
        "reuse_histogram": dict(
            sorted(
                {
                    count: sum(1 for value in seen.values() if value == count)
                    for count in set(seen.values())
                }.items()
            )
        ),
        "max_reuse": max(seen.values()) if seen else 0,
    }


# --- assembled reports -------------------------------------------------------


def definition_census(data: bytes) -> dict[str, Any]:
    definitions = iter_definitions(data)
    rows = [
        (d.field_00, d.field_02, d.field_04, d.field_08, d.field_0C, d.field_50)
        for d in definitions
    ]
    summary = census_definitions(rows)
    summary["array_slots"] = census_array_slots([d.array for d in definitions])
    summary["animation_references"] = census_animation_pointers(
        [value for d in definitions for value in d.array],
        lambda value: in_rom(data, value) and value % 4 == 0,
    )
    summary["remap_pointer_invariant"] = remap_pointer_invariant(data)
    summary["extent_models"] = extent_model_comparison(data)
    return summary


def remap_pointer_invariant(data: bytes) -> dict[str, Any]:
    """The 65 structures whose ``+0x04`` holds ``structure - 0x100``.

    The invariant is measured, not assumed: the report counts how many
    structures satisfy it and reports every structure that does not.  Whether
    the 256 bytes are a palette-index remap is INFERRED from their shape (an
    identity permutation with a few substitutions) and is not asserted here.
    """
    definitions = iter_definitions(data)
    holding = [
        d.identifier for d in definitions if d.field_04 == d.address - REMAP_BLOCK_SIZE
    ]
    nonzero = [d.identifier for d in definitions if d.field_04]
    deviations = []
    for definition in definitions:
        if not definition.field_04:
            continue
        block = data[
            definition.field_04 - ROM_BASE:
            definition.field_04 - ROM_BASE + REMAP_BLOCK_SIZE
        ]
        if len(block) != REMAP_BLOCK_SIZE:
            continue
        deviations.append(
            {
                "id": definition.identifier,
                "deviations": sum(1 for i, value in enumerate(block) if value != i),
            }
        )
    return {
        "structures_with_nonzero_field_04": len(nonzero),
        "structures_where_field_04_is_structure_minus_0x100": len(holding),
        "all_nonzero_field_04_hold_the_invariant": len(holding) == len(nonzero),
        "minimum_block_deviations": min(d["deviations"] for d in deviations)
        if deviations
        else 0,
        "maximum_block_deviations": max(d["deviations"] for d in deviations)
        if deviations
        else 0,
    }


def extent_model_comparison(data: bytes) -> dict[str, Any]:
    """Compare the counted extent with the accepted next-structure-walk extent.

    ``tools/webfoot/graphics.py`` resolves a structure's animation pointers by
    walking from ``+0x54`` to the *next* structure, on the stated ground that no
    field in the header has been shown to bound the list.  The count does bound
    it, so this report measures how far the two models differ on the canonical
    image: how many structures they agree on, how many slots each scans, and
    whether the accepted model's extra slots resolve to ROM pointers at all.
    """
    definitions = iter_definitions(data)
    addresses = [d.address for d in definitions]
    agree = 0
    pairs = 0
    pair_agree = 0
    counted_slots = 0
    walked_slots = 0
    extra_nonzero = 0
    extra_rom_pointers = 0
    for index, definition in enumerate(definitions):
        next_start = (
            addresses[index + 1]
            if index + 1 < len(addresses)
            else DEFINITION_ARRAY_ADDRESS
        )
        end = definition.address + OBJECT_HEADER_SIZE + 4 * definition.count
        if next_start == end:
            agree += 1
            if index + 1 < len(addresses):
                pair_agree += 1
        if index + 1 < len(addresses):
            pairs += 1
        counted_slots += definition.count
        walked = max(0, (next_start - (definition.address + FIELD_ARRAY)) // 4)
        walked_slots += walked
        for extra in range(definition.count, walked):
            value = _u32(data, definition.address + FIELD_ARRAY + 4 * extra)
            if value:
                extra_nonzero += 1
                if in_rom(data, value):
                    extra_rom_pointers += 1
    return {
        "structures": len(definitions),
        "consecutive_pairs": pairs,
        "consecutive_pairs_where_the_next_definition_starts_at_the_counted_end": pair_agree,
        "structures_where_the_counted_end_is_the_next_boundary": agree,
        "counted_slots": counted_slots,
        "walked_slots": walked_slots,
        "extra_slots_the_walk_scans": walked_slots - counted_slots,
        "extra_slots_nonzero": extra_nonzero,
        "extra_slots_that_are_rom_pointers": extra_rom_pointers,
    }


def animation_census(data: bytes) -> dict[str, Any]:
    definitions = iter_definitions(data)
    addresses: dict[int, list[tuple[int, int]]] = {}
    for definition in definitions:
        for index, value in enumerate(definition.array):
            if value:
                addresses.setdefault(value, []).append((definition.identifier, index))
    frames: dict[int, int] = {}
    frame_counts: dict[int, int] = {}
    trailer_0: dict[int, int] = {}
    trailer_1: dict[int, int] = {}
    for address in addresses:
        animation = read_animation(data, address)
        frame_counts[animation.frame_count] = (
            frame_counts.get(animation.frame_count, 0) + 1
        )
        for pointer in animation.pointers:
            frames[pointer] = frames.get(pointer, 0) + 1
        _, first, second = read_animation_tail(data, address)
        trailer_0[first] = trailer_0.get(first, 0) + 1
        trailer_1[second] = trailer_1.get(second, 0) + 1
    return {
        "unique_animations": len(addresses),
        "frame_count_distribution": dict(sorted(frame_counts.items())),
        # Slots over the *unique* animation records, not over every reference:
        # the 1,721 non-null references reach only 1,017 records.
        "frame_slots_over_unique_animations": sum(frames.values()),
        "unique_frames": len(frames),
        "frame_max_reuse": max(frames.values()) if frames else 0,
        "trailer_0_histogram": dict(sorted(trailer_0.items())),
        "trailer_1_histogram": dict(sorted(trailer_1.items())),
        "animations_with_multiple_referrers": sum(
            1 for sites in addresses.values() if len(sites) > 1
        ),
        "max_animation_reuse": max(len(sites) for sites in addresses.values()),
    }


def frame_record_census(data: bytes) -> dict[str, Any]:
    """Extent and leading bytes of every distinct frame record."""
    definitions = iter_definitions(data)
    addresses: set[int] = set()
    for definition in definitions:
        for value in definition.array:
            if value:
                animation = read_animation(data, value)
                addresses.update(pointer for pointer in animation.pointers if pointer)
    piece_counts: dict[int, int] = {}
    in_image = 0
    for address in addresses:
        record = read_frame_record(data, address)
        piece_counts[record.piece_count] = piece_counts.get(record.piece_count, 0) + 1
        if record.end_address <= ROM_BASE + len(data):
            in_image += 1
    return {
        "unique_frames": len(addresses),
        "piece_count_distribution": dict(sorted(piece_counts.items())),
        "frames_fully_inside_the_image": in_image,
    }


def appearance_join(data: bytes) -> dict[str, Any]:
    """Join the accepted appearance table to the run, reusing LOGX-CHAR-001.

    The appearance table's ``+0x04`` is the id the accessor resolves; LOGX-CHAR-001
    established that relationship and this report does not re-open it.  It only
    measures how the 232 appearances land on the 297 run entries.
    """
    records = logx_char_probe.iter_records(data)
    by_id: dict[int, list[int]] = {}
    for record in records:
        by_id.setdefault(record.field_04, []).append(record.index)
    run_index = {definition_pointer(data, i): run_index_for_id(i) for i in by_id}
    ids = sorted(by_id)
    resolved = {i: definition_pointer(data, i) for i in ids}
    return {
        "appearance_records": len(records),
        "ids_used": len(ids),
        "id_min": ids[0],
        "id_max": ids[-1],
        "unique_targets": len(set(resolved.values())),
        "run_indices_referenced": len(run_index),
        "run_index_min": min(run_index.values()),
        "run_index_max": max(run_index.values()),
        "unreferenced_run_indices": DEFINITION_ARRAY_ENTRY_COUNT - len(run_index),
        "every_id_in_run": all(
            DEFINITION_ID_FLOOR
            <= i
            < DEFINITION_ID_FLOOR + DEFINITION_ARRAY_ENTRY_COUNT
            for i in ids
        ),
        "shared_by_multiple_appearances": {
            str(i): by_id[i] for i in ids if len(by_id[i]) > 1
        },
    }


def count_guard_report(data: bytes) -> list[dict[str, Any]]:
    """The five engine sites that bound an array read with the definition's count.

    Each entry also names the null test that follows the array load, because the
    engine checks the element as well as the index.  ``array_offset`` is
    ``FIELD_ARRAY + 4 * index`` and is what the site's load instruction uses.
    """
    report = []
    for (pointer_site, count_site, compare_site, array_site), null_site in zip(
        COUNT_GUARD_SITES, COUNT_GUARD_NULL_TESTS
    ):
        # The compare immediate is the low byte of the ``cmp rX, #imm8``
        # halfword; the branch that follows skips the array load when the
        # count is at or below it.
        index = data[compare_site - ROM_BASE]
        report.append(
            {
                "pointer_site": f"{pointer_site:#010x}",
                "count_site": f"{count_site:#010x}",
                "compare_site": f"{compare_site:#010x}",
                "array_site": f"{array_site:#010x}",
                "null_test_site": f"{null_site:#010x}",
                "index": index,
                "array_offset": f"{FIELD_ARRAY + 4 * index:#04x}",
            }
        )
    return report


def selector_argument_census(data: bytes, *, lookback: int = 20) -> dict[str, Any]:
    """Census of the arguments the image passes to :data:`ANIMATION_SELECTOR`.

    Requires capstone (see the module docstring).  The *site count* is
    authoritative and is taken from :func:`tools.research.thumb_disasm.scan_thumb_calls`,
    which decodes every halfword-aligned site in the image and accepts only a real
    four-byte ``bl``/``blx``.  It replaced the raw halfword predicate that used to
    stand here, whose result this census once published as fact: that predicate
    invented 1,552 sites across the image, recognised one J1/J2 combination of each
    encoding, and resolved every non-word-aligned ``BLX`` two bytes high, so
    ``const_*``/``runtime_index_sites`` here were derived from an incomplete and
    partly fabricated caller set.  The counts in this report change with that fix;
    they are measurements, not constants, and the ROM-gated suite pins them.

    The census remains a **static site** count: it cannot tell code from data, so a
    valid encoding standing in a data table is still a site.  The argument
    classification is explicitly a *heuristic*: the argument is the nearest write to
    ``r1`` within ``lookback`` instructions, so it is bounded by a window rather
    than by a data-flow proof.  ``lookback`` and ``unresolved_sites`` are reported
    so the heuristic's reach is visible rather than implied.
    """
    from tools.research.thumb_disasm import iter_thumb_wide, scan_thumb_calls

    wanted = ANIMATION_SELECTOR & ~1
    calls = [site for site in scan_thumb_calls(data) if site.cleared_target == wanted]
    sites = sorted(site.address for site in calls)
    kinds: dict[str, int] = {}
    for site in calls:
        kinds[site.kind] = kinds.get(site.kind, 0) + 1
    items = [
        item
        for item in iter_thumb_wide(data, ROM_BASE, ROM_BASE + 0x60000)
        if not isinstance(item, int)
    ]
    position = {item.address: i for i, item in enumerate(items)}
    constants: dict[int, int] = {}
    runtime = 0
    unresolved = 0
    for site in sites:
        start = position.get(site)
        if start is None:
            unresolved += 1
            continue
        classified = False
        for j in range(start - 1, max(-1, start - lookback), -1):
            item = items[j]
            text = f"{item.mnemonic} {item.operands}"
            match = re.match(r"^movs?\s+r1,\s*#(0x[0-9a-f]+|\d+)$", text)
            if match:
                value = int(match.group(1), 16) if match.group(1).startswith("0x") else int(match.group(1))
                constants[value] = constants.get(value, 0) + 1
                classified = True
                break
            if re.match(r"^(ldr|ldrb|ldrh|adds?|mov)\s+r1,", text):
                runtime += 1
                classified = True
                break
        if not classified:
            unresolved += 1
    return {
        "selector": f"{ANIMATION_SELECTOR:#010x}",
        "call_sites": len(sites),
        "call_kinds": dict(sorted(kinds.items())),
        "census_method": "decoded halfword-aligned sites, BL and BLX",
        "argument_classification": "heuristic: nearest r1 write within lookback",
        "lookback_instructions": lookback,
        "constant_index_histogram": dict(sorted(constants.items())),
        "constant_index_count": sum(constants.values()),
        "max_constant_index": max(constants) if constants else None,
        "runtime_index_sites": runtime,
        "unresolved_sites": unresolved,
    }


def state_table_report(data: bytes) -> dict[str, Any]:
    table = state_to_index_table(data)
    return {
        "address": f"{STATE_TABLE_ADDRESS:#010x}",
        "size": len(table),
        "entries": list(table),
        # ``max_value`` is the largest value the table holds; ``largest_state``
        # is the largest index the engine addresses.  They are different numbers
        # and must not be conflated.
        "max_value": max(table),
        "largest_state": STATE_TABLE_SIZE - 1,
        "identity_prefix": all(table[i] == i for i in range(16)),
        # The bytes immediately after the 25-entry table are *not* part of it.
        # They are reported so the "above 24 is zero" reading can be falsified
        # rather than assumed.
        "bytes_after_table_hex": data[
            STATE_TABLE_ADDRESS - ROM_BASE + STATE_TABLE_SIZE:
            STATE_TABLE_ADDRESS - ROM_BASE + STATE_TABLE_SIZE + 0x18
        ].hex(),
        "lookup_sites": [f"{site:#010x}" for site in STATE_TABLE_LOOKUP_SITES],
        "literal_sites": {
            f"{site:#010x}": f"{STATE_TABLE_LITERAL:#010x}"
            for site in STATE_TABLE_LITERAL_SITES
        },
        "address_literal_site": f"{STATE_TABLE_ADDRESS_LITERAL_SITE:#010x}",
        "address_literal_sites": state_table_address_literal_sites(data),
    }


def state_table_address_literal_sites(data: bytes) -> list[dict[str, Any]]:
    """Every ``ldr Rt,[pc,#imm]`` whose literal-word value is the state table.

    A raw halfword scan over every even offset of the whole image, so an
    undecodable neighbour cannot hide a site.
    """
    found = []
    address = ROM_BASE
    limit = ROM_BASE + len(data)
    while address + 4 <= limit:
        halfword = _u16(data, address)
        if (halfword & 0xF800) == 0x4800:
            register = (halfword >> 8) & 7
            pool = ((address + 4) & ~3) + (halfword & 0xFF) * 4
            if ROM_BASE <= pool and pool + 4 <= limit:
                if _u32(data, pool) == STATE_TABLE_ADDRESS:
                    found.append(
                        {
                            "site": f"{address:#010x}",
                            "register": f"r{register}",
                            "pool": f"{pool:#010x}",
                        }
                    )
        address += 2
    return found


############################################
# engine instruction evidence
############################################


@lru_cache(maxsize=1)
def _decode_thumb_at() -> Callable[[bytes, int], Any]:
    """The Thumb decoder, imported on first use rather than at module import.

    ``tools.research.thumb_disasm`` raises ``SystemExit`` when capstone is
    missing, and capstone is research tooling rather than a declared dependency
    of the shipping SDK that CI's portable job installs.  Importing it lazily
    keeps the census, definition, animation and part API usable - and
    CI-coverable - without it.
    """
    from tools.research.thumb_disasm import decode_thumb_at

    return decode_thumb_at


def instruction_at(data: bytes, address: int) -> tuple[str, str, bytes]:
    """``(mnemonic, operands, raw bytes)`` for the Thumb instruction at a site."""
    item = _decode_thumb_at()(data, address)
    if item is None:
        raise SpriteProbeError(f"no Thumb instruction decodes at {address:#010x}")
    offset = address - ROM_BASE
    return item.mnemonic, item.operands, data[offset: offset + item.size]


def format_instruction(data: bytes, address: int) -> str:
    mnemonic, operands, _ = instruction_at(data, address)
    return f"{address:08x}  {mnemonic:<9} {operands}".rstrip()


def thumb_ldr_literal_sites(data: bytes) -> dict[int, list[tuple[int, int, int]]]:
    """Every ``ldr Rt,[pc,#imm]`` whose literal-word value is keyed in the result.

    Returns ``{literal value: [(site, Rt, pool address), ...]}``.  A raw halfword
    scan over every even offset, so an undecodable neighbouring halfword cannot
    hide a site.  The returned mapping is cached and must not be mutated.
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


def engine_report(data: bytes) -> dict[str, Any]:
    """Instruction evidence for the accessor, the count, and the selection path."""
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
    sites = [
        {"site": f"{site:#010x}", "register": f"r{register}", "pool": f"{pool:#010x}"}
        for site, register, pool in sorted(literal_sites.get(DEFINITION_ARRAY_ADDRESS, []))
    ]
    return {
        "definition_array_address": f"{DEFINITION_ARRAY_ADDRESS:#010x}",
        "definition_array_literal_sites": sites,
        "instructions": instructions,
        "count_guards": count_guard_report(data),
        "state_table": state_table_report(data),
        "selector_arguments": selector_argument_census(data),
        "accessors": {
            "definition": f"{DEFINITION_ACCESSOR:#010x}",
            "definition_record": f"{DEFINITION_ACCESSOR_RECORD:#010x}",
            "character_ctor": f"{CHARACTER_CTOR:#010x}",
            "character_morph": f"{CHARACTER_MORPH:#010x}",
            "animation_selector": f"{ANIMATION_SELECTOR:#010x}",
            "folded_arithmetic_base": f"{FOLDED_ARITHMETIC_BASE:#010x}",
        },
    }


def build_report(data: bytes, *, include_rows: bool = False) -> dict[str, Any]:
    report = {
        "canonical_sha256": CANONICAL_SHA256,
        "run": run_report(data),
        "folded_base": folded_base_explanation(data),
        "definitions": definition_census(data),
        "animations": animation_census(data),
        "frames": frame_record_census(data),
        "appearances": appearance_join(data),
        "engine": engine_report(data),
    }
    if include_rows:
        report["rows"] = [
            {
                "id": definition.identifier,
                "address": f"{definition.address:#010x}",
                "file_offset": f"{definition.file_offset:#08x}",
                "count": definition.count,
                "size": definition.size,
                "field_04": f"{definition.field_04:#010x}",
                "field_08": f"{definition.field_08:#010x}",
                "field_0c": f"{definition.field_0C:#010x}",
                "field_50": f"{definition.field_50:#010x}",
                "array": [f"{value:#010x}" for value in definition.array],
                "raw": definition.raw.hex(),
            }
            for definition in iter_definitions(data)
        ]
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, help="canonical Buu's Fury ROM (read-only)")
    parser.add_argument("--rows", action="store_true", help="include every definition")
    parser.add_argument("--engine", action="store_true", help="engine evidence only")
    parser.add_argument("--run", action="store_true", help="pointer-run report only")
    args = parser.parse_args(argv)

    data = load_rom(args.rom)
    if args.engine:
        json.dump(engine_report(data), sys.stdout, indent=2, sort_keys=True)
    elif args.run:
        json.dump(
            {"run": run_report(data), "folded_base": folded_base_explanation(data)},
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
    else:
        json.dump(build_report(data, include_rows=args.rows), sys.stdout,
                  indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
