"""TOOLKIT-016: the second `0x0800FD55` variant, and who owns it.

TOOLKIT-015 closed BLOCKED because 64 script-bearing records were referenced
from a `0x0800FD55` record that the verified placement corpus excluded, and no
static owner could be found for them.

The reason no owner was found is that there is no second variant. The placement
record is variable-length -- `+0x18` is a child count and `+0x1C..` is a
`count`-long pointer array -- and it looked fixed-size only because 1,427 of
1,442 records carry `count == 1`, which freezes `+0x18`/`+0x1C` into apparent
constants at exactly 32 bytes. Read correctly, the ordinary `MapEntry[+0x14]`
array reaches all 1,295 verified placements *and* 57 script-bearing records
across 10 maps.

This module pins that chain, and pins just as hard the things that must not be
over-claimed: the unowned remainder stays excluded, the owned subset is a clean
partition, and the walk's boundaries are checked rather than assumed. The
expensive failure mode in this ticket's direction is the opposite of
TOOLKIT-015's: promoting an unowned record because a larger walk reached it.

Evidence: docs/research/BUU_FD55_SCRIPT_OWNER.md
"""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import struct

import pytest

from tools.webfoot.cli import load_catalog
from tools.webfoot.maps import load_maps
from tools.webfoot.formats.script_vm import Entry, assemble, disassemble, encode_instruction
from tools.webfoot.scripts import OPCODE_SETS

SHA = '940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e'
ROM_BASE = 0x08000000

#: The placement factory tag (TOOLKIT-008) and the MapEntry table (TOOLKIT-007).
FACTORY = 0x0800FD55
MAP_TABLE = 0x0808E2E0
MAP_COUNT = 452
MAP_STRIDE = 0x38

#: The three behavior handlers reached through a record's `+0x14` descriptor.
#: These are Thumb function pointers, not factory tags -- `0x0800421F` is the
#: interpreter trampoline TOOLKIT-015 disassembled.
HANDLER_NULL = 0x0800421D        # bx lr
HANDLER_SCRIPT = 0x0800421F      # ldr r1,[r0,#4] ; bl 0x08004038
HANDLER_OTHER = 0x0800424F       # ldr r0,[r0,#4] ; bl 0x08012588
INTERPRETER = 0x08004038

#: The shared null-handler descriptor every script-less record names.
NULL_DESCRIPTOR = 0x080555A0

#: Corrected corpus-wide walk measurements.
REACHED_RECORDS = 1442
REACHED_ARRAYS = 240
VERIFIED_PLACEMENTS = 1295

#: The owned script subset, which is what this ticket promotes.
OWNED_RECORDS = 57
OWNED_MAPS = 10
OWNED_ROOTS = 25
OWNED_BLOCKS = 42
OWNED_INSTRUCTIONS = 202
OWNED_BYTES = 514

#: Deliberately excluded remainder.
UNOWNED_REFERRING_RECORDS = 7
DESCRIPTORS_WITHOUT_REFERRER = 76
TOTAL_DESCRIPTORS = 140
UNOWNED_ROOTS = 19


@pytest.fixture
def rom():
    path = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
    if not path.exists():
        pytest.skip('canonical ROM not configured locally')
    before = path.read_bytes()
    assert hashlib.sha256(before).hexdigest() == SHA
    yield path
    # The canonical image is an input and must survive every test unchanged.
    assert path.read_bytes() == before


@pytest.fixture
def data(rom):
    return rom.read_bytes()


def _u32(data, addr):
    return struct.unpack_from('<I', data, addr - ROM_BASE)[0]


def _in_rom(data, addr):
    return ROM_BASE <= addr < ROM_BASE + len(data) - 3


def _factory_words(data):
    """Every four-aligned word equal to the placement factory tag."""
    return {ROM_BASE + o for o in range(0, len(data) - 3, 4)
            if struct.unpack_from('<I', data, o)[0] == FACTORY}


def _walk(data):
    """Bounded walk of every MapEntry's placement array.

    The array runs while each successive word points at a record led by the
    factory tag, and stops at the first word that does not. Nothing about a
    record's tail is required, because the tail is not fixed.
    """
    factories = _factory_words(data)
    arrays = {}
    for i in range(MAP_COUNT):
        ptr = _u32(data, MAP_TABLE + i * MAP_STRIDE + 0x14)
        if not _in_rom(data, ptr):
            continue
        records = []
        while _in_rom(data, ptr + 4 * len(records)):
            word = _u32(data, ptr + 4 * len(records))
            if word not in factories:
                break
            records.append(word)
        if records:
            arrays[i] = (ptr, tuple(records))
    return arrays


def _handler(data, record):
    """The behavior handler a record names through its `+0x14` descriptor."""
    descriptor = _u32(data, record + 0x14)
    if not _in_rom(data, descriptor):
        return None, descriptor
    return _u32(data, descriptor), descriptor


def _owned(data):
    """(map index, record, descriptor, root) for every owned script record."""
    out = []
    for index, (_, records) in sorted(_walk(data).items()):
        for record in records:
            handler, descriptor = _handler(data, record)
            if handler == HANDLER_SCRIPT:
                out.append((index, record, descriptor, _u32(data, descriptor + 4)))
    return out


def _decode(data, root):
    """Decode one root at its exact extent, so nothing decodes as opaque."""
    spec = OPCODE_SETS['stack_be16_buu_v1']
    off = root - ROM_BASE
    probe = disassemble(data[off:off + 512], (Entry('r', 0),), spec)
    end = max(i.source_offset + len(encode_instruction(i, spec))
              for b in probe.blocks for i in b.instructions)
    return disassemble(data[off:off + end], (Entry('r', 0),), spec), end


# --- the structural correction: the record is variable-length -----------------

def test_record_child_array_is_a_count_and_not_a_constant_tail(data):
    """`+0x18` is a count; the supported corpus just always carries count 1.

    This is the whole ticket in one measurement. TOOLKIT-008 read `+0x18`/`+0x1C`
    as constants because 1,427 of 1,442 records have exactly one child, making
    the record exactly 32 bytes. 15 records carry a different count.
    """
    sizes = Counter()
    for _, records in _walk(data).values():
        for record in records:
            sizes[0x1C + 4 * _u32(data, record + 0x18)] += 1
    assert sizes[32] == 1427
    assert sizes[36] == 7
    assert sizes[40] == 6
    assert sizes[44] == 2
    assert sum(sizes.values()) == REACHED_RECORDS
    # More than one size is what refutes the fixed-32 reading.
    assert len(sizes) == 4


def test_every_child_pointer_lands_inside_the_image(data):
    """A count is only a count if the array it declares is readable."""
    for _, records in _walk(data).values():
        for record in records:
            count = _u32(data, record + 0x18)
            for i in range(count):
                assert _in_rom(data, _u32(data, record + 0x1C + 4 * i))


def test_record_bodies_never_run_into_the_next_record(data):
    """The variable-length extent is self-consistent across the whole corpus.

    If `+0x18` were not a count, bounding records at `0x1C + 4n` would make some
    record swallow its neighbour. None does, which is what makes the extent
    checkable rather than assumed.
    """
    records = sorted({r for _, rs in _walk(data).values() for r in rs})
    for record, following in zip(records, records[1:]):
        assert record + 0x1C + 4 * _u32(data, record + 0x18) <= following


# --- the walk is bounded, not merely larger ----------------------------------

def test_walk_reaches_every_verified_placement_and_loses_none(data):
    """The corrected walk is a strict superset of the verified corpus.

    TOOLKIT-015 rejected a 1,442-record walk for disagreeing with the verified
    1,295. The disagreement is real and the walk is the correct side of it: it
    reaches all 1,295 and adds 147 records the tail requirement truncated.
    """
    maps = load_maps("roms/Dragon Ball Z - Buu's Fury (U).gba", load_catalog(None))
    verified = {ROM_BASE + e.file_offset for e in maps.legacy_placements()}
    assert len(verified) == VERIFIED_PLACEMENTS

    reached = {r for _, rs in _walk(data).values() for r in rs}
    assert len(reached) == REACHED_RECORDS
    assert verified <= reached
    assert not verified - reached


def test_both_placement_counts_stay_meaningful(data):
    """1,295 and 1,442 name different things and both remain correct.

    1,442 is the full census under the variable-length contract. 1,295 is the
    legacy supported fixed-codec subset -- the records the 32-byte codec can
    read. This test exists so neither figure is quietly rewritten into the
    other: the legacy subset is exactly the reached records carrying one child
    and the shared null descriptor, which is why the old codec saw a constant.
    """
    maps = load_maps("roms/Dragon Ball Z - Buu's Fury (U).gba", load_catalog(None))
    verified = {ROM_BASE + e.file_offset for e in maps.legacy_placements()}
    reached = {r for _, rs in _walk(data).values() for r in rs}

    assert len(verified) == VERIFIED_PLACEMENTS
    assert len(reached) == REACHED_RECORDS
    assert len(reached - verified) == REACHED_RECORDS - VERIFIED_PLACEMENTS

    for record in verified:
        assert _u32(data, record + 0x18) == 1
        assert _u32(data, record + 0x14) == NULL_DESCRIPTOR


def test_owned_records_remain_outside_the_legacy_fixed_tail_shape(data):
    """The historical fixed-tail restriction excluded every owned script record.

    TOOLKIT-017 supports these through the variable-length path. This assertion
    preserves the historical distinction rather than claiming a current limit.
    """
    from tools.webfoot.formats.map_placements import RECORD_TAIL

    for _, record, _, _ in _owned(data):
        tail = tuple(_u32(data, record + 0x14 + 4 * i) for i in range(3))
        assert tail != RECORD_TAIL


def test_walk_claims_no_record_twice_and_no_slot_twice(data):
    """Boundedness, stated as the two ways an over-collecting walk shows up."""
    arrays = _walk(data)
    assert len(arrays) == REACHED_ARRAYS

    claims = Counter(r for _, rs in arrays.values() for r in rs)
    assert not [r for r, n in claims.items() if n > 1]

    slots = Counter()
    for ptr, records in arrays.values():
        for i in range(len(records)):
            slots[ptr + 4 * i] += 1
    assert not [s for s, n in slots.items() if n > 1]
    assert sum(slots.values()) == REACHED_RECORDS


# --- the behavior descriptor -------------------------------------------------

def test_exactly_three_handlers_are_named_by_map_reached_records(data):
    """A record names a handler; only one of the three is the interpreter."""
    handlers = Counter()
    maps_per_handler = defaultdict(set)
    for index, (_, records) in _walk(data).items():
        for record in records:
            handler, _ = _handler(data, record)
            handlers[handler] += 1
            maps_per_handler[handler].add(index)

    assert set(handlers) == {HANDLER_NULL, HANDLER_SCRIPT, HANDLER_OTHER}
    assert handlers[HANDLER_NULL] == 1361
    assert handlers[HANDLER_SCRIPT] == OWNED_RECORDS
    assert handlers[HANDLER_OTHER] == 24
    assert len(maps_per_handler[HANDLER_SCRIPT]) == OWNED_MAPS


def test_the_supported_corpus_constant_is_the_null_handler_descriptor(data):
    """`0x080555A0` is not a magic tail word, it is a shared descriptor.

    It holds `0x0800421D` (`bx lr`), which is why 1,361 records have no script.
    Its inbound reference count matching the walk exactly is independent
    corroboration that the walk's extent is right.
    """
    assert _u32(data, NULL_DESCRIPTOR) == HANDLER_NULL
    inbound = sum(1 for o in range(0, len(data) - 3, 4)
                  if struct.unpack_from('<I', data, o)[0] == NULL_DESCRIPTOR)
    assert inbound == REACHED_RECORDS


def test_script_handler_is_the_interpreter_trampoline(data):
    """The handler is a Thumb pointer whose body calls the VM.

    Checked from the bytes rather than from TOOLKIT-015's prose: the trampoline
    loads the descriptor's `+0x04` and branches to the interpreter.
    """
    off = (HANDLER_SCRIPT & ~1) - ROM_BASE
    assert data[off:off + 2] == b'\x00\xb5'          # push {lr}
    assert data[off + 2:off + 4] == b'\x41\x68'      # ldr r1,[r0,#4]

    # bl 0x08004038 at 0x0800422E, decoded from the two halfwords.
    site = 0x0800422E - ROM_BASE
    hi, lo = struct.unpack_from('<HH', data, site)
    offset = ((hi & 0x7FF) << 12) | ((lo & 0x7FF) << 1)
    if offset & (1 << 22):
        offset -= 1 << 23
    assert 0x0800422E + 4 + offset == INTERPRETER


def test_null_and_script_handlers_are_distinct_routines(data):
    """The null handler really is a return, so its records really have no script."""
    assert data[(HANDLER_NULL & ~1) - ROM_BASE:(HANDLER_NULL & ~1) - ROM_BASE + 2] == b'\x70\x47'
    assert HANDLER_NULL != HANDLER_SCRIPT


# --- ownership ---------------------------------------------------------------

def test_owned_subset_is_fifty_seven_records_across_ten_maps(data):
    owned = _owned(data)
    assert len(owned) == OWNED_RECORDS
    assert len({index for index, _, _, _ in owned}) == OWNED_MAPS
    assert {index for index, _, _, _ in owned} == {
        19, 21, 22, 240, 309, 325, 428, 430, 432, 437}


def test_owned_records_are_not_verified_placements(data):
    """The owned records are new corpus, not a relabelling of supported records.

    They are precisely the records the tail requirement excluded, so promoting
    them cannot silently restate an existing capability.
    """
    maps = load_maps("roms/Dragon Ball Z - Buu's Fury (U).gba", load_catalog(None))
    verified = {ROM_BASE + e.file_offset for e in maps.legacy_placements()}
    assert not {record for _, record, _, _ in _owned(data)} & verified


def test_sharing_is_real_and_must_not_be_flattened(data):
    """Maps 21 and 22 each point 15 records at one root.

    A `map -> event` model would report 30 events where the ROM stores 2, which
    is why attachment is exposed at the descriptor level.
    """
    per_map = defaultdict(list)
    for index, _, _, root in _owned(data):
        per_map[index].append(root)
    assert len(per_map[21]) == 15 and len(set(per_map[21])) == 1
    assert len(per_map[22]) == 15 and len(set(per_map[22])) == 1
    assert len(per_map[19]) == 10 and len(set(per_map[19])) == 10


# --- the promoted script corpus ----------------------------------------------

def test_owned_roots_round_trip_byte_identically(data):
    """Promotion requires exactness, measured per root against the image."""
    roots = sorted({root for _, _, _, root in _owned(data)})
    assert len(roots) == OWNED_ROOTS

    blocks = instructions = 0
    covered = set()
    summed = 0
    for root in roots:
        ir, end = _decode(data, root)
        off = root - ROM_BASE
        assert assemble(ir) == data[off:off + end]
        blocks += len(ir.blocks)
        instructions += sum(len(b.instructions) for b in ir.blocks)
        covered.update(range(off, off + end))
        summed += end

    assert blocks == OWNED_BLOCKS
    assert instructions == OWNED_INSTRUCTIONS
    assert len(covered) == OWNED_BYTES
    # Summed extents equalling unique bytes is what proves no root overlaps.
    assert summed == OWNED_BYTES


def test_owned_subset_carries_all_three_backward_branches(data):
    """The `0x1C` evidence now sits inside an owned corpus.

    TOOLKIT-015 promoted the opcode's encoding contract while its corpus had no
    owner. The contract is unchanged; what is new is that the bytes exercising
    it are owned, so the family carrying them can be supported.
    """
    opcodes = Counter()
    for root in sorted({root for _, _, _, root in _owned(data)}):
        ir, _ = _decode(data, root)
        for block in ir.blocks:
            for instruction in block.instructions:
                opcodes[instruction.opcode] += 1
    assert opcodes[0x1C] == 3
    assert opcodes[0x11] == OWNED_ROOTS      # one terminator per root
    assert len(opcodes) == 14


# --- the remainder stays out -------------------------------------------------

def test_referring_records_that_no_map_reaches_are_excluded(data):
    """7 of the 64 referring records have no owner and must not be promoted."""
    factories = _factory_words(data)
    referring = {record for record in factories
                 if _handler(data, record)[0] == HANDLER_SCRIPT}
    assert len(referring) == 64

    owned = {record for _, record, _, _ in _owned(data)}
    assert len(referring - owned) == UNOWNED_REFERRING_RECORDS
    assert sorted(referring - owned) == [
        0x0807CDF4, 0x0807FA1C, 0x08081A04, 0x08083DA4,
        0x0808DF58, 0x0808E018, 0x0808E0CC]


def test_descriptors_without_a_placement_referrer_are_excluded(data):
    """76 of the 140 descriptors are named by no record at all."""
    descriptors = {ROM_BASE + o for o in range(0, len(data) - 3, 4)
                   if struct.unpack_from('<I', data, o)[0] == HANDLER_SCRIPT
                   and _in_rom(data, _u32(data, ROM_BASE + o + 4))}
    assert len(descriptors) == TOTAL_DESCRIPTORS

    referenced = {_u32(data, record + 0x14) for record in _factory_words(data)
                  if _handler(data, record)[0] == HANDLER_SCRIPT}
    assert len(descriptors - referenced) == DESCRIPTORS_WITHOUT_REFERRER


def test_owned_and_unowned_roots_do_not_share_bytes(data):
    """The partition is clean, so promoting the owned subset promotes nothing else.

    If an owned root were also reachable from an unowned descriptor, supporting
    it would quietly extend support to unowned content. None is.
    """
    descriptors = {ROM_BASE + o for o in range(0, len(data) - 3, 4)
                   if struct.unpack_from('<I', data, o)[0] == HANDLER_SCRIPT
                   and _in_rom(data, _u32(data, ROM_BASE + o + 4))}
    owned_descriptors = {d for _, _, d, _ in _owned(data)}

    owned_roots = {_u32(data, d + 4) for d in owned_descriptors}
    other_roots = {_u32(data, d + 4) for d in descriptors - owned_descriptors}
    assert len(owned_roots) == OWNED_ROOTS
    assert len(other_roots) == UNOWNED_ROOTS
    assert not owned_roots & other_roots


def test_no_map_or_placement_attachment_is_claimed_for_the_remainder(data):
    """The unowned roots must not become reachable through any owned map.

    This is the guard against the failure mode opposite to TOOLKIT-015's: a
    later edit widening the walk until everything is "owned".
    """
    owned_records = {record for _, record, _, _ in _owned(data)}
    reached = {r for _, rs in _walk(data).values() for r in rs}
    unowned = {record for record in _factory_words(data)
               if _handler(data, record)[0] == HANDLER_SCRIPT} - owned_records
    assert not unowned & reached
