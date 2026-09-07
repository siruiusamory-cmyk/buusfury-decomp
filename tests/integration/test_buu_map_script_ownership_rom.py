"""TOOLKIT-015: the map-scene script ownership question, answered honestly.

TOOLKIT-015 asked which stable Buu map-scene record owns script execution. Two
candidate families were traced statically and neither reaches a verified map,
placement or placement type. This module pins that negative result as hard as a
positive one, because the expensive failure mode here is a later edit quietly
promoting an adjacency into an ownership claim.

It also pins the one genuinely new measurement: the ``0x0800421F``
content-stream family round-trips exactly and is the first corpus in this
project to exercise backward branch opcode ``0x1C``. That corpus is measured but
deliberately NOT promoted to a project family, because it has no verified owner.

Evidence: docs/research/BUU_MAP_SCRIPT_OWNERSHIP.md
"""
from pathlib import Path
import hashlib
import struct
from collections import Counter
import pytest
from tools.webfoot.cli import load_catalog
from tools.webfoot.maps import load_maps
from tools.webfoot.scripts import load_scripts, script_families
from tools.webfoot.formats.script_vm import (
    Entry, assemble, disassemble, encode_instruction,
)
from tools.webfoot.scripts import OPCODE_SETS

SHA = '940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e'

#: The trampoline selected by the census, and the factory tag of its records.
TRAMPOLINE = 0x0800421E
FACTORY_TAG = 0x0800421F
INTERPRETER = 0x08004038

#: The MapEntry table and the heterogeneous content stream (TOOLKIT-007/012).
MAP_TABLE = 0x0808E2E0
MAP_COUNT = 452
MAP_STRIDE = 0x38
STREAM = (0x080728CC, 0x0808E1E0)

#: Measured extent of the 0x0800421F family. Not a supported project family.
RECORDS = 140
ROOTS = 44
BLOCKS = 69
INSTRUCTIONS = 358
UNIQUE_BYTES = 921

#: The verified placement corpus every ownership claim is measured against.
VERIFIED_PLACEMENTS = 1295

#: Constants that are byte-identical on every verified placement, which is what
#: disqualifies +0x18/+0x1C as a per-placement script selector.
PLACEMENT_VTABLE_FLAG = 0x00000001
PLACEMENT_VTABLE = 0x080716EC


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
    return struct.unpack_from('<I', data, addr - 0x08000000)[0]


def _records(data):
    """Every four-aligned word equal to the family's factory tag."""
    words = struct.unpack_from('<%dI' % (len(data) // 4), data, 0)
    return tuple(0x08000000 + i * 4
                 for i, w in enumerate(words) if w == FACTORY_TAG)


def _roots(data):
    return tuple(sorted({_u32(data, r + 4) for r in _records(data)}))


def _decode(data, root):
    """Decode one root at its exact extent, so nothing decodes as opaque."""
    spec = OPCODE_SETS['stack_be16_buu_v1']
    off = root - 0x08000000
    probe = disassemble(data[off:off + 512], (Entry('r', 0),), spec)
    end = max(i.source_offset + len(encode_instruction(i, spec))
              for b in probe.blocks for i in b.instructions)
    return disassemble(data[off:off + end], (Entry('r', 0),), spec), end


# --- the census result that selected the candidate ---------------------------

def test_the_trampoline_is_the_only_unresolved_site_reachable_from_map_content(data):
    """Selection was measured, not preferred.

    Every unresolved interpreter call site from the TOOLKIT-014 census was
    tested for inbound Thumb pointers from the map content stream. Exactly one
    proc answered, which is why it was the candidate.
    """
    words = struct.unpack_from('<%dI' % (len(data) // 4), data, 0)
    others = (0x08004098, 0x0800423A, 0x08004784, 0x08007368, 0x080089A0,
              0x080089D8, 0x08008A36, 0x08008B30, 0x08009030, 0x080091B8,
              0x08011F5A, 0x080121A8, 0x080121D8, 0x080122B4, 0x08013C02,
              0x0802574C, 0x08033308, 0x08033360, 0x08033390)
    counts = Counter()
    for i, w in enumerate(words):
        if w & 1 and (w & ~1) in (TRAMPOLINE,) + others:
            addr = 0x08000000 + i * 4
            if STREAM[0] <= addr < STREAM[1]:
                counts[w & ~1] += 1
    assert counts[TRAMPOLINE] == RECORDS
    for proc in others:
        assert counts[proc] == 0, f'{proc:#x} gained map-content references'


def test_the_trampoline_interprets_its_records_script_pointer(data):
    """0x0800421E is a pure trampoline: ldr r1,[r0,#4] then call the VM."""
    off = TRAMPOLINE - 0x08000000
    assert data[off:off + 2] == b'\x00\xb5'          # push {lr}
    assert data[off + 2:off + 4] == b'\x41\x68'      # ldr r1,[r0,#4]
    # The BL pair at +0x10 targets the one verified interpreter.
    hi, lo = struct.unpack_from('<HH', data, off + 0x10)
    offset = (((hi & 0x7FF) << 12) | ((lo & 0x7FF) << 1))
    if offset & (1 << 22):
        offset -= 1 << 23
    assert TRAMPOLINE + 0x10 + 4 + offset == INTERPRETER


# --- candidate 1: placement +0x18/+0x1C is a shared vtable, not a script ------

def test_placement_vtable_fields_are_constant_and_cannot_select_a_script(rom, data):
    """A field identical on all 1,295 placements selects nothing per-placement."""
    maps = load_maps(rom, load_catalog(None))
    placements = list(maps.placements())
    assert len(placements) == VERIFIED_PLACEMENTS
    for entry in placements:
        base = 0x08000000 + entry.file_offset
        assert _u32(data, base + 0x18) == PLACEMENT_VTABLE_FLAG
        assert _u32(data, base + 0x1C) == PLACEMENT_VTABLE


def test_the_placement_tail_target_is_a_dispatch_block(data):
    """0x080716EC is a mixed vtable: Thumb code pointers plus an IWRAM slot.

    Only the entries actually dispatched are claimed as code. Slot 1 holds
    0x030019A4, an IWRAM address, so this is a vtable-plus-state block rather
    than a pure function-pointer table.
    """
    assert _u32(data, PLACEMENT_VTABLE + 0x00) == 0x0800A26F
    assert _u32(data, PLACEMENT_VTABLE + 0x04) == 0x030019A4
    for i in (2, 3, 4):
        word = _u32(data, PLACEMENT_VTABLE + 4 * i)
        assert word & 1, 'dispatched slot is not a Thumb pointer'
        assert 0x08000000 <= word < 0x08800000


# --- candidate 2: the corpus is real, its ownership is not --------------------

def test_the_family_is_bounded_and_shared(data):
    records = _records(data)
    roots = _roots(data)
    assert len(records) == RECORDS
    assert len(roots) == ROOTS, 'root sharing changed'
    # The script always sits BEHIND its record, but at no fixed distance: the
    # deltas run from -9 to -50,036. Claiming a fixed -12 would generalise the
    # first four consecutive records over a corpus that does not support it.
    deltas = [_u32(data, r + 4) - r for r in records]
    assert all(d < 0 for d in deltas)
    assert Counter(deltas).most_common(1)[0] == (-12, 14)
    assert min(deltas) == -50036
    assert all(STREAM[0] <= r < STREAM[1] for r in records)
    assert all(STREAM[0] <= root < STREAM[1] for root in roots)


def test_every_root_decodes_and_re_encodes_exactly(data):
    """Exact round-trip over the whole family, with no uncovered byte."""
    covered = set()
    blocks = instructions = 0
    for root in _roots(data):
        ir, end = _decode(data, root)
        assert not ir.opaque, f'{root:#x} left uncovered bytes'
        off = root - 0x08000000
        assert assemble(ir) == data[off:off + end]
        blocks += len(ir.blocks)
        instructions += sum(len(b.instructions) for b in ir.blocks)
        covered.update(range(off, off + end))
    assert blocks == BLOCKS
    assert instructions == INSTRUCTIONS
    # Summed extents equal unique bytes, so no two roots overlap.
    assert len(covered) == UNIQUE_BYTES


def test_the_family_exercises_the_backward_branch_opcode(data):
    """0x1C occurs in canonical bytes here for the first time in the project."""
    opcodes = Counter()
    for root in _roots(data):
        ir, _ = _decode(data, root)
        for block in ir.blocks:
            for ins in block.instructions:
                opcodes[ins.opcode] += 1
    assert opcodes[0x1C] == 3
    assert opcodes[0x13] == 9
    assert opcodes[0x12] == 1


def test_every_backward_branch_satisfies_the_handler_derived_contract(data):
    """The checks that promote the 0x1C ENCODING to canonical-ROM corroborated.

    The rule under test lives in script_vm.py:147-159 with the Buu spec at
    script_specs.py:49-50 (be16 / count_back) and :77 (before_operand). The
    target is recomputed here independently of the decoder, so a decoder change
    that silently altered the contract would fail this test rather than agree
    with itself.

    This promotes the opcode's encoding only. The owning family stays
    unsupported, unattached and semantically UNKNOWN.
    """
    spec = OPCODE_SETS['stack_be16_buu_v1']
    op = spec.lookup(0x1C)
    assert (op.encoding, op.flow, op.branch_base) == (
        'be16', 'count_back', 'before_operand')

    seen = []
    for root in _roots(data):
        ir, end = _decode(data, root)
        heads = {b.instructions[0].source_offset for b in ir.blocks}
        off = root - 0x08000000
        for block in ir.blocks:
            for ins in block.instructions:
                if ins.opcode != 0x1C:
                    continue
                raw = data[off + ins.source_offset:
                           off + ins.source_offset + ins.encoded_length]
                displacement = ins.operands[0].value
                # two-byte big-endian displacement
                assert len(ins.operands[0].encoding) == 2
                assert displacement == (raw[1] << 8) | raw[2]
                # before_operand base, and subtraction, recomputed independently
                assert ins.target == (ins.source_offset + 1) - displacement
                # backward, in extent, and onto a real basic-block head
                assert ins.target < ins.source_offset
                assert 0 <= ins.target < end
                assert ins.target in heads
                seen.append((root, ins.source_offset, displacement, ins.target))

    assert seen == [
        (0x080853E8, 104, 82, 23),
        (0x080853E8, 186, 56, 131),
        (0x080853E8, 231, 24, 208),
    ]


def test_the_family_control_flow_is_coherent(data):
    """No edge leaves the corpus, and the only backward edges are the three 0x1C."""
    edges = unknown = backward = 0
    for root in _roots(data):
        ir, _ = _decode(data, root)
        identities = {b.identity for b in ir.blocks}
        for block in ir.blocks:
            for edge in block.edges:
                edges += 1
                if edge.target not in identities:
                    unknown += 1
            for ins in block.instructions:
                if ins.target is not None and ins.target < ins.source_offset:
                    backward += 1
    assert edges == 37
    assert unknown == 0
    assert backward == 3


def test_no_map_entry_reaches_the_family_at_any_indirection_level(data):
    """The ownership answer: no static path from the map table exists."""
    records = set(_records(data))
    direct = via_array = 0
    for index in range(MAP_COUNT):
        base = MAP_TABLE + index * MAP_STRIDE
        for field in range(0x0C, MAP_STRIDE, 4):
            ptr = _u32(data, base + field)
            if ptr in records:
                direct += 1
            if 0x08000000 <= ptr < 0x08800000:
                for k in range(64):
                    word = _u32(data, ptr + 4 * k)
                    if word in records:
                        via_array += 1
                        break
                    if not 0x08000000 <= word < 0x08800000:
                        break
    assert direct == 0, 'a MapEntry field now points straight at a script record'
    assert via_array == 0, 'a MapEntry array now reaches a script record'


def test_no_verified_placement_owns_or_precedes_a_record(rom, data):
    """The refuted hypothesis, pinned so it cannot be re-adopted silently.

    A hand-written walker once suggested 57 map-reachable placements sat 8 bytes
    after a record. That walker over-collected 1,442 placements; the verified
    parser reaches 1,295 and the true count is zero.
    """
    maps = load_maps(rom, load_catalog(None))
    verified = {0x08000000 + e.file_offset for e in maps.placements()}
    records = set(_records(data))
    assert len(verified) == VERIFIED_PLACEMENTS
    assert not any(addr - 8 in records for addr in verified)
    assert not (verified & records)


def test_the_only_structural_referrers_are_outside_the_verified_corpus(rom, data):
    """64 structural referrers, all at +0x14 of an unverified 0x0800FD55 variant.

    A 65th inbound word exists at 0x081267A0, outside the content stream and not
    preceded by any factory tag. It is counted and excluded rather than ignored:
    one matching word in unrelated data is a coincidence, not a reference.
    """
    records = set(_records(data))
    words = struct.unpack_from('<%dI' % (len(data) // 4), data, 0)
    maps = load_maps(rom, load_catalog(None))
    verified = {0x08000000 + e.file_offset for e in maps.placements()}
    bases, incidental = set(), []
    for i, w in enumerate(words):
        if w in records:
            addr = 0x08000000 + i * 4
            if _u32(data, addr - 20) == 0x0800FD55:
                bases.add(addr - 20)
            else:
                incidental.append(addr)
    assert len(bases) == 64
    assert incidental == [0x081267A0]
    assert not STREAM[0] <= incidental[0] < STREAM[1]
    # None of the 64 bases is a placement the project supports, and in every
    # verified placement +0x14 is a constant, not a pointer to a script record.
    assert not (bases & verified)
    for entry in maps.placements():
        assert _u32(data, 0x08000000 + entry.file_offset + 0x14) == 0x080555A0


# --- guards: nothing here is promoted ----------------------------------------

def test_the_family_is_not_declared_as_a_supported_script_family(rom):
    """Measured is not promoted. Without an owner it stays out of the profile."""
    families = script_families(rom, load_catalog(None))
    assert set(families) == {'static40', 'item_use'}


def test_existing_families_are_unregressed(rom):
    catalog = load_catalog(None)
    static40 = load_scripts(rom, catalog, 'static40')
    assert len(static40.ir.blocks) == 120
    assert sum(len(b.instructions) for b in static40.ir.blocks) == 328

    item_use = load_scripts(rom, catalog, 'item_use')
    assert len(item_use.ir.blocks) == 86
    assert sum(len(b.instructions) for b in item_use.ir.blocks) == 351
    assert len(item_use.attachments) == 23
