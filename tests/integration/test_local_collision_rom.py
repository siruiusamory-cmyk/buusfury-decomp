"""ROM-gated collision-evidence regressions for TOOLKIT-012.

TOOLKIT-012 stopped at an evidence blocker: no bounded static collision family
reached verified movement-blocking semantics. These tests lock in the four
measurements that produced that conclusion, so a future ticket cannot quietly
promote a collision capability without first invalidating one of them.

The canonical image is opened read-only on every path; nothing here writes to
it. Every constant below was measured from that image in TOOLKIT-012, not
assumed and not inherited from a prior ticket's summary.

See docs/research/COLLISION_FORMAT.md.
"""

from __future__ import annotations

import struct
from pathlib import Path

import pytest


LOCAL_ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
BASE = 0x08000000

#: TOOLKIT-007, unchanged: the MapEntry table.
TABLE = 0x0008E2E0
STRIDE = 0x38
RECORD_COUNT = 452

#: The 20-byte rectangle-descriptor family, the strongest collision candidate.
RECT_FACTORY = 0x0800742D
RECT_STRIDE = 0x14
RECT_OCCURRENCES = 166
RECT_WELL_FORMED = 152
RECT_RUNS = 102

#: The per-map area-content descriptor stream reached from MapEntry +0x2C.
STREAM_FIELD = 0x2C
STREAM_LOW = 0x080728CC
STREAM_HIGH = 0x0808E1E0
STREAM_BYTES = 112916

#: The gcc __call_via_rN thunk block that AUTO_RE_STATE mis-read as a point
#: query. `bx rN` encodes as 0x4700 | (N << 3).
VENEER_BASE = 0x08046AA0


def require_rom():
    if not LOCAL_ROM.is_file():
        pytest.skip("user-supplied Buu's Fury ROM is not present")


@pytest.fixture(scope="module")
def rom() -> bytes:
    require_rom()
    return LOCAL_ROM.read_bytes()


def word(rom: bytes, addr: int) -> int:
    return struct.unpack_from("<I", rom, addr - BASE)[0]


def halfword(rom: bytes, addr: int) -> int:
    return struct.unpack_from("<H", rom, addr - BASE)[0]


def rect_records(rom: bytes) -> list[int]:
    """Every well-formed 20-byte rectangle descriptor, by address."""
    out = []
    for off in range(0, len(rom) - RECT_STRIDE, 4):
        if struct.unpack_from("<I", rom, off)[0] != RECT_FACTORY:
            continue
        subtype = struct.unpack_from("<I", rom, off + 4)[0]
        aux = struct.unpack_from("<I", rom, off + 0x10)[0]
        a0, a1 = struct.unpack_from("<hh", rom, off + 8)
        b0, b1 = struct.unpack_from("<hh", rom, off + 0xC)
        if not (0x08000000 <= subtype < 0x08800000 and subtype & 1):
            continue
        if not 0x08000000 <= aux < 0x08800000:
            continue
        if not (a0 <= b0 and a1 <= b1 and a0 >= 0 and a1 >= 0):
            continue
        out.append(BASE + off)
    return out


# --- the correction ------------------------------------------------------


def test_0x08046aa4_is_a_call_veneer_and_not_a_point_query(rom):
    """OLD CLAIM: AUTO_RE_STATE described a "point query" at 0x08046AA4.

    NEW EVIDENCE: the eight halfwords there are `bx r0`..`bx r7`, the gcc
    `__call_via_rN` indirect-call thunks. The address performs no query; it
    jumps to whatever the register holds.
    """
    for n in range(8):
        encoded = halfword(rom, VENEER_BASE + n * 2)
        assert encoded == 0x4700 | (n << 3), (
            f"0x{VENEER_BASE + n * 2:08X} is not `bx r{n}`; the veneer reading "
            "of this block has changed and COLLISION_FORMAT.md needs revisiting"
        )


# --- the four blocker findings -------------------------------------------


def test_the_rectangle_candidate_corpus_is_exactly_as_measured(rom):
    recs = rect_records(rom)
    occurrences = sum(
        1
        for off in range(0, len(rom) - 4, 4)
        if struct.unpack_from("<I", rom, off)[0] == RECT_FACTORY
    )
    assert occurrences == RECT_OCCURRENCES
    assert len(recs) == RECT_WELL_FORMED

    runs = 1
    for prev, cur in zip(recs, recs[1:]):
        if cur - prev != RECT_STRIDE:
            runs += 1
    assert runs == RECT_RUNS


def test_no_rectangle_run_start_is_owned_by_the_mapentry_table(rom):
    """Blocker finding 1: the candidate family has no static map ownership.

    Ticket section 4 requires verified map ownership. Zero of the run starts is
    referenced from the MapEntry table, so the family is reachable only by
    walking the +0x2C stream.
    """
    recs = rect_records(rom)
    starts = {recs[0]}
    for prev, cur in zip(recs, recs[1:]):
        if cur - prev != RECT_STRIDE:
            starts.add(cur)
    assert len(starts) == RECT_RUNS

    table_lo = BASE + TABLE
    table_hi = table_lo + STRIDE * RECORD_COUNT
    owned = [
        BASE + off
        for off in range(TABLE, TABLE + STRIDE * RECORD_COUNT, 4)
        if struct.unpack_from("<I", rom, off)[0] in starts
    ]
    assert owned == [], (
        "a MapEntry field now points at a rectangle run start; the ownership "
        "blocker in COLLISION_FORMAT.md no longer holds"
    )
    assert table_lo < table_hi  # the window actually scanned


def test_rectangle_subtypes_resolve_to_iwram_vtables(rom):
    """Blocker finding 2: record class identity is built in RAM, not stored.

    Each +0x04 subtype word is a `ldr r0,[pc,#N] ; bx lr` getter. Every one that
    decodes returns an IWRAM address, so there is no static ROM class table for
    this toolkit to own or validate.
    """
    recs = rect_records(rom)
    subtypes = {word(rom, a + 4) for a in recs}
    assert subtypes, "no subtypes found"

    resolved = 0
    for thunk in subtypes:
        addr = thunk & ~1
        first = halfword(rom, addr)
        if first >> 11 != 0b01001:  # not LDR (literal)
            continue
        pool = (((addr + 4) & ~3)) + (first & 0xFF) * 4
        value = word(rom, pool)
        resolved += 1
        assert 0x03000000 <= value < 0x04000000, (
            f"subtype thunk 0x{thunk:08X} now returns 0x{value:08X}, which is "
            "not IWRAM; the runtime-identity blocker needs revisiting"
        )
    assert resolved >= 8, "expected at least 8 decodable subtype thunks"


def test_no_mapentry_pointer_reaches_a_low_entropy_block(rom):
    """Blocker finding 4: there is no dense walkability grid behind any map.

    A tile or bitmask walkability grid would appear as a low-entropy byte block
    hanging off a MapEntry pointer. None does, in any pointer field.
    """
    fields = (0x10, 0x14, 0x18, 0x1C, 0x20, 0x30)
    live = 0
    low_entropy = []
    for index in range(RECORD_COUNT):
        for field in fields:
            value = struct.unpack_from(
                "<I", rom, TABLE + index * STRIDE + field
            )[0]
            if not (0x08000000 <= value < 0x08800000 and value % 4 == 0):
                continue
            off = value - BASE
            if off + 512 > len(rom):
                continue
            live += 1
            block = rom[off : off + 512]
            distinct = len(set(block))
            modal = max(block.count(b) for b in set(block)) / 512
            if distinct <= 16 and modal >= 0.25:
                low_entropy.append((index, field, value))
    assert live > 0
    assert low_entropy == [], (
        "a MapEntry pointer now reaches a low-entropy block; a walkability "
        "grid may exist after all and COLLISION_FORMAT.md needs revisiting"
    )


def test_the_area_content_stream_is_one_shared_heterogeneous_region(rom):
    """The structural finding: Buu keeps no separate per-map collision table.

    MapEntry +0x2C is the only pointer live on every map, its targets are all
    distinct, and they address one contiguous stream that ends where the
    MapEntry table begins.
    """
    targets = [
        struct.unpack_from("<I", rom, TABLE + i * STRIDE + STREAM_FIELD)[0]
        for i in range(RECORD_COUNT)
    ]
    assert all(0x08000000 <= t < 0x08800000 for t in targets)
    assert len(set(targets)) == RECORD_COUNT, "a +0x2C target is now shared"
    assert min(targets) == STREAM_LOW
    assert max(targets) == STREAM_HIGH
    assert STREAM_HIGH - STREAM_LOW == STREAM_BYTES
    assert STREAM_HIGH < BASE + TABLE


# --- domain separation guards (ticket sections 21 and 22) ----------------


def test_collision_is_not_promoted_by_any_shipped_capability():
    """Sections 21/22: no API may treat a transition or combat rectangle as a
    movement blocker. TOOLKIT-012 shipped no collision capability at all, so
    the guard is that none appeared.
    """
    from tools.webfoot import capability

    names = [n.lower() for n in dir(capability)]
    assert not any("collision" in n for n in names), (
        "a collision capability appeared in webfoot.capability; TOOLKIT-012 "
        "closed BLOCKED and shipped none"
    )


def test_the_confirmed_rectangle_is_documented_as_a_transition():
    """Section 21: the one CONFIRMED rectangle (MapEntry 39 -> 0x080755C0) was
    runtime-proven in ROM-012 to initiate a map transition. The evidence
    document must keep saying so, because that is what refuses the family.
    """
    doc = Path("docs/research/COLLISION_FORMAT.md")
    assert doc.is_file(), "TOOLKIT-012 evidence document is missing"
    text = doc.read_text(encoding="utf-8")
    assert "0x0300195C" in text
    assert "transition" in text.lower()
