"""TOOLKIT-014: a static Buu record proven to own a script, and what that buys.

TOOLKIT-013 closed with two honest gaps: no attachment was proven for any Buu
script, and the branch contract rested on handler disassembly because no
supported corpus contained a branch. This module pins the evidence that closes
both, and pins just as hard the things that are still NOT proven, so a later
edit cannot quietly upgrade a candidate into a claim.

Evidence: docs/research/BUU_SCRIPT_OWNERSHIP.md
"""
from pathlib import Path
import hashlib
import struct
from collections import Counter
import pytest
from tools.webfoot.profile import RomProfileCatalog, ProfileConfigError
from tools.webfoot.scripts import load_scripts, script_families, script_references
from tools.webfoot.formats.script_vm import assemble, disassemble, Entry, ScriptError

SHA = '940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e'

#: The static owner table: 83 item records of 52 bytes.
OWNER_TABLE = 0x003BD2F8
OWNER_STRIDE = 52
OWNER_COUNT = 83
#: Field +0x30 of an owner record is its script pointer; 0 means "owns none".
SCRIPT_SLOT = 0x30
#: Halfwords +0x02..+0x08 are text indices, proven consumers (see the doc).
LABEL_SLOTS = (2, 4, 6, 8)

#: Measured extent of the item_use corpus.
POOL_START = 0x003BBBB0
POOL_SIZE = 703
ROOTS = 23
BLOCKS = 86
INSTRUCTIONS = 351

#: The interpreter call site this family was selected from, and its owner-forming
#: callers. Recorded as provenance for the ownership claim, never as identity.
CALL_SITE = 0x0801E182
OWNER_CALLERS = (0x0800D74E, 0x0800DDFA)

TEXT_POINTER_TABLE = 0x0806BCE8
TEXT_COUNT = 1534


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
def corpus(rom):
    return load_scripts(rom, RomProfileCatalog.load('config/roms.yaml'), 'item_use')


# --------------------------------------------------------------------------
# The census, and the call site that was selected out of it
# --------------------------------------------------------------------------

def test_the_interpreter_call_site_census_is_still_twenty_nine(rom):
    """The census this ticket selected from must not silently change size."""
    from tools.webfoot.analysis.thumb import scan_bl
    data = rom.read_bytes()
    sites = {b.site_address for b in scan_bl(data, 0, len(data))
             if b.target == 0x08004038}
    assert len(sites) == 29
    # The three static40 walker sites and the selected item_use site are in it.
    assert {0x080141FA, 0x0801420A, 0x08014232, CALL_SITE} <= sites


def test_the_selected_call_site_reads_the_owner_record_script_field(rom):
    """Proc 0x0801E164 gates on owner byte +0x00 bit 1, then interprets +0x30.

    This is the whole ownership claim in four instructions, so it is pinned
    against the executable rather than trusted from the evidence document.
    """
    data = rom.read_bytes()
    half = lambda addr: struct.unpack_from('<H', data, addr - 0x08000000)[0]
    assert half(0x0801E168) == 0x7801          # ldrb r1,[r0]
    assert half(0x0801E178) == 0x6B01          # ldr  r1,[r0,#0x30]
    # ...and the very next thing it does is call the interpreter.
    from tools.webfoot.analysis.thumb import decode_bl
    call = decode_bl(half(CALL_SITE), half(CALL_SITE + 2), CALL_SITE)
    assert call is not None and call.target == 0x08004038


def test_both_owner_callers_form_table_plus_stride_times_index(rom):
    """`r0` reaching the call site is `table + 52*index` over one static base.

    That is what makes the owner static: the cursor is not read out of a heap
    object, it is read out of a ROM record selected by an index.
    """
    from tools.webfoot.analysis.thumb import decode_bl, ldr_literal_address
    data = rom.read_bytes()
    half = lambda addr: struct.unpack_from('<H', data, addr - 0x08000000)[0]
    word = lambda addr: struct.unpack_from('<I', data, addr - 0x08000000)[0]
    for site, stride_at, literal_at in ((0x0800D74E, 0x0800D742, 0x0800D744),
                                        (0x0800DDFA, 0x0800DDBE, 0x0800DDC2)):
        assert site in OWNER_CALLERS
        # `movs rX,#0x34` - the 52-byte stride, as an immediate in the code.
        assert half(stride_at) & 0xFF == OWNER_STRIDE
        # The literal it multiplies against is the owner table base.
        literal = ldr_literal_address(half(literal_at), literal_at)
        assert word(literal) == 0x08000000 + OWNER_TABLE
        # And the call really does reach the script-running proc.
        call = decode_bl(half(site), half(site + 2), site)
        assert call is not None and call.target == 0x0801E164


def test_the_owner_table_base_is_referenced_widely_enough_to_be_real(rom):
    """Twelve independent literals hold this base; it is not a lucky word."""
    from tools.webfoot.analysis.thumb import find_aligned_words
    data = rom.read_bytes()
    refs = find_aligned_words(data, 0x08000000 + OWNER_TABLE, 0, len(data))
    assert len(refs) == 12


def test_the_rejected_candidate_has_no_owner_at_all(rom):
    """Site 0x0800F67A looked like the best candidate and was rejected.

    Proc 0x0800F62C reads a descriptor-shaped record and sits right before the
    placement-type constructor, but nothing in the ROM references it, so there
    is no owner to attach to. Pinned so a later reader does not re-select it on
    shape and skip the reference check.
    """
    from tools.webfoot.analysis.thumb import scan_bl
    data = rom.read_bytes()
    assert not [b for b in scan_bl(data, 0, len(data)) if b.target == 0x0800F62C]
    for value in (0x0800F62C, 0x0800F62D):
        assert data.find(value.to_bytes(4, 'little')) == -1


# --------------------------------------------------------------------------
# The corpus: bounded, exhaustive, byte-identical
# --------------------------------------------------------------------------

def test_both_families_are_declared_and_stay_separate(rom):
    """The historical families stay separate when the owned placement family joins."""
    catalog = RomProfileCatalog.load('config/roms.yaml')
    assert script_families(rom, catalog) == ('static40', 'item_use', 'placement_descriptor_event')
    static40 = load_scripts(rom, catalog, 'static40')
    item_use = load_scripts(rom, catalog, 'item_use')
    assert static40.ir.opcode_set is item_use.ir.opcode_set
    # Disjoint bytes, so no script is owned twice.
    assert static40.source_offset + static40.ir.extent <= item_use.source_offset \
        or item_use.source_offset + item_use.ir.extent <= static40.source_offset


def test_static40_is_unchanged_by_this_ticket(rom):
    """TOOLKIT-013's measurements are a boundary, not a starting point."""
    corpus = load_scripts(rom, RomProfileCatalog.load('config/roms.yaml'), 'static40')
    assert len(corpus.ir.entries) == 120
    assert len(corpus.ir.blocks) == 120
    assert corpus.instruction_count == 328
    assert corpus.ir.extent == 548
    assert Counter(i.opcode for b in corpus.ir.blocks
                   for i in b.instructions) == {0: 108, 1: 14, 2: 84, 4: 2, 17: 120}
    # Still no attachment, because none was proven for it.
    assert corpus.attachments == ()


def test_exhaustive_corpus_identity(rom, corpus):
    """Every supported byte decodes and re-encodes byte-identically."""
    assert corpus.family == 'item_use'
    assert len(corpus.ir.entries) == ROOTS
    assert len(corpus.ir.blocks) == BLOCKS
    assert corpus.instruction_count == INSTRUCTIONS
    assert corpus.source_offset == POOL_START
    assert corpus.ir.extent == POOL_SIZE
    assert not corpus.ir.opaque
    original = rom.read_bytes()[POOL_START:POOL_START + POOL_SIZE]
    assert assemble(corpus.ir) == original


def test_opcode_coverage_is_the_measured_census(corpus):
    assert Counter(i.opcode for b in corpus.ir.blocks for i in b.instructions) == {
        0x00: 79, 0x01: 19, 0x02: 101, 0x03: 44, 0x07: 42,
        0x11: 23, 0x12: 21, 0x13: 21, 0x1D: 1}
    # Exactly one terminator per root, so no root runs off its stream.
    assert sum(1 for b in corpus.ir.blocks
               for i in b.instructions if i.opcode == 0x11) == ROOTS


def test_owner_table_shape_is_as_measured(rom):
    """83 records; 23 own a script; those 23 are distinct and ascending."""
    data = rom.read_bytes()
    pointers = [struct.unpack_from(
        '<I', data, OWNER_TABLE + i * OWNER_STRIDE + SCRIPT_SLOT)[0]
        for i in range(OWNER_COUNT)]
    live = [p for p in pointers if p]
    assert len(live) == ROOTS
    assert len(set(live)) == ROOTS
    assert live == sorted(live)
    assert min(live) == 0x08000000 + POOL_START
    assert max(live) < 0x08000000 + POOL_START + POOL_SIZE
    # A null slot is a record that owns no script, not a malformed record.
    assert pointers.count(0) == OWNER_COUNT - ROOTS


def test_the_pool_bound_is_measured_not_assumed(rom):
    """703 is the only extent that tiles: shorter overruns, longer leaves slack."""
    data = rom.read_bytes()
    offsets = sorted({struct.unpack_from(
        '<I', data, OWNER_TABLE + i * OWNER_STRIDE + SCRIPT_SLOT)[0]
        - (0x08000000 + POOL_START) for i in range(OWNER_COUNT)
        if struct.unpack_from('<I', data, OWNER_TABLE + i * OWNER_STRIDE + SCRIPT_SLOT)[0]})
    entries = tuple(Entry(f'root:{n:02d}', off) for n, off in enumerate(offsets))
    from tools.webfoot.data.script_specs import OPCODE_SETS
    spec = OPCODE_SETS['stack_be16_buu_v1']
    with pytest.raises(ScriptError):
        disassemble(data[POOL_START:POOL_START + POOL_SIZE - 1], entries, spec)
    over = disassemble(data[POOL_START:POOL_START + POOL_SIZE + 1], entries, spec)
    assert over.opaque  # a trailing byte no root reaches
    exact = disassemble(data[POOL_START:POOL_START + POOL_SIZE], entries, spec)
    assert not exact.opaque


def test_enumeration_is_deterministic(rom, corpus):
    again = load_scripts(rom, RomProfileCatalog.load('config/roms.yaml'), 'item_use')
    assert corpus == again
    assert [e.identity for e in corpus.ir.entries] == \
           [e.identity for e in again.ir.entries]
    assert corpus.attachments == again.attachments


def test_identities_are_authoring_names_not_addresses(corpus):
    """Owner and event identities must survive relocation, so no address leaks."""
    for entry in corpus.ir.entries:
        profile, family, ordinal, slot = entry.identity.split(':')
        assert profile == 'buus_fury_usa_rev0_01c1707f'
        assert family == 'item_use'
        assert 0 <= int(ordinal) < OWNER_COUNT
        assert slot == 'slot30'
    for attachment in corpus.attachments:
        kind, ordinal = attachment.owner.split(':')
        assert kind == 'item'
        assert 0 <= int(ordinal) < OWNER_COUNT
        assert '0x' not in attachment.owner
        assert f'{POOL_START:x}' not in attachment.owner
        assert f'{OWNER_TABLE:x}' not in attachment.owner


# --------------------------------------------------------------------------
# The attachment graph
# --------------------------------------------------------------------------

def test_attachment_graph_covers_exactly_the_scripted_owners(corpus):
    assert len(corpus.attachments) == ROOTS
    assert len({a.owner for a in corpus.attachments}) == ROOTS
    assert len({a.event for a in corpus.attachments}) == ROOTS
    assert {a.owner_kind for a in corpus.attachments} == {'item'}
    # Every attachment names an event that really exists in this corpus.
    identities = {e.identity for e in corpus.ir.entries}
    assert {a.event for a in corpus.attachments} <= identities
    # Ownership is one-to-one here; no script is shared between owners.
    for attachment in corpus.attachments:
        assert corpus.owners_of(attachment.event) == (attachment.owner,)
        assert corpus.events_of(attachment.owner) == (attachment.event,)


def test_no_attachment_is_claimed_beyond_the_measured_corpus(corpus):
    """60 of the 83 owners have no script, and must not acquire a phantom one."""
    owners = {a.owner for a in corpus.attachments}
    assert 'item:0022' not in owners      # a null +0x30 record
    assert corpus.events_of('item:0022') == ()
    assert corpus.events_of('item:9999') == ()
    assert corpus.owners_of('no such event') == ()
    # No map, placement or placement-type owner is invented for this family.
    assert not any(a.owner_kind in ('map', 'placement', 'placement_type')
                   for a in corpus.attachments)


# --------------------------------------------------------------------------
# Branch opcodes: the contract gains canonical evidence
# --------------------------------------------------------------------------

def test_this_corpus_actually_exercises_branch_opcodes(corpus):
    """The thing static40 could not do: real branches over canonical bytes."""
    branches = [i for b in corpus.ir.blocks for i in b.instructions
                if i.opcode in (0x12, 0x13, 0x1C)]
    assert len(branches) == 42
    assert Counter(i.opcode for i in branches) == {0x12: 21, 0x13: 21}
    # 0x1C stays unexercised, so it stays handler-derived only. Recorded, not
    # glossed: an untested opcode must not inherit a tested one's confidence.
    assert not any(i.opcode == 0x1C for i in branches)


def test_reconstructed_control_flow_is_sound(corpus):
    """Every edge lands on a block this same decode produced."""
    labels = {b.identity for b in corpus.ir.blocks}
    edges = [e for b in corpus.ir.blocks for e in b.edges]
    assert len(corpus.ir.blocks) == BLOCKS
    assert edges and all(e.target in labels for e in edges)
    starts = {i.source_offset for b in corpus.ir.blocks for i in b.instructions}
    for block in corpus.ir.blocks:
        for ins in block.instructions:
            if ins.opcode in (0x12, 0x13, 0x1C):
                # Buu measures from the cursor BEFORE the operand bytes.
                assert ins.source_offset + 1 + ins.operands[0].value in starts


def test_only_the_buu_reading_makes_the_branches_mean_anything(rom):
    """The measurement TOOLKIT-013 could not make.

    Both grammars decode these bytes and both re-encode them byte-identically,
    so round-trip alone still does not discriminate. What discriminates is what
    the branches DO: under LOGII's one-byte reading all 42 branches have
    displacement zero and jump to their own fallthrough, which is not what
    authored code looks like. Under Buu's two-byte big-endian reading all 42
    are real jumps. That is canonical-corpus evidence for the branch contract,
    on top of the handler disassembly.
    """
    from tools.webfoot.data.script_specs import OPCODE_SETS
    data = rom.read_bytes()
    blob = data[POOL_START:POOL_START + POOL_SIZE]
    offsets = sorted({struct.unpack_from(
        '<I', data, OWNER_TABLE + i * OWNER_STRIDE + SCRIPT_SLOT)[0]
        - (0x08000000 + POOL_START) for i in range(OWNER_COUNT)
        if struct.unpack_from('<I', data, OWNER_TABLE + i * OWNER_STRIDE + SCRIPT_SLOT)[0]})
    entries = tuple(Entry(f'root:{n:02d}', off) for n, off in enumerate(offsets))

    verdicts = {}
    for name, pre in (('stack_be16_buu_v1', 1), ('stack_be7_v1', 2)):
        ir = disassemble(blob, entries, OPCODE_SETS[name])
        # Both are lossless; that is precisely why round-trip cannot decide.
        assert not ir.opaque and assemble(ir) == blob
        ordered = sorted({i.source_offset: i for b in ir.blocks
                          for i in b.instructions}.items())
        following = {off: ordered[k + 1][0] for k, (off, _) in enumerate(ordered[:-1])}
        no_ops = sum(1 for _, i in ordered if i.opcode in (0x12, 0x13, 0x1C)
                     and i.source_offset + pre + i.operands[0].value
                     == following.get(i.source_offset))
        total = sum(1 for _, i in ordered if i.opcode in (0x12, 0x13, 0x1C))
        verdicts[name] = (len(ir.blocks), total, no_ops)

    assert verdicts['stack_be16_buu_v1'] == (BLOCKS, 42, 0)
    assert verdicts['stack_be7_v1'] == (65, 42, 42)


# --------------------------------------------------------------------------
# Text references: promoted here, still CANDIDATE there
# --------------------------------------------------------------------------

def test_owner_text_ids_are_consumed_through_the_verified_table(rom):
    """A dereference, not a numeric match.

    0x0801F818 loads the TOOLKIT-004 text pointer table and 0x0801F85E..62
    reads owner record +0x02, shifts left by two and indexes it. That consumer
    path is what promotes these from CANDIDATE to a real text reference.
    """
    from tools.webfoot.analysis.thumb import ldr_literal_address
    data = rom.read_bytes()
    half = lambda addr: struct.unpack_from('<H', data, addr - 0x08000000)[0]
    word = lambda addr: struct.unpack_from('<I', data, addr - 0x08000000)[0]
    literal = ldr_literal_address(half(0x0801F818), 0x0801F818)
    assert word(literal) == TEXT_POINTER_TABLE
    assert half(0x0801F85E) == 0x8852        # ldrh r2,[r2,#2]
    assert half(0x0801F860) == 0x0092        # lsls r2,r2,#2
    assert half(0x0801F862) == 0x5889        # ldr  r1,[r1,r2]


def test_every_owner_carries_four_resolvable_text_ids(rom, corpus):
    """All 83 owners, not only the 23 scripted ones, name real strings."""
    data = rom.read_bytes()
    for ordinal in range(OWNER_COUNT):
        record = OWNER_TABLE + ordinal * OWNER_STRIDE
        for slot in LABEL_SLOTS:
            index = struct.unpack_from('<H', data, record + slot)[0]
            assert 0 <= index < TEXT_COUNT
            pointer = struct.unpack_from(
                '<I', data, TEXT_POINTER_TABLE - 0x08000000 + index * 4)[0]
            assert 0x08000000 <= pointer < 0x08000000 + len(data)
    # And the attachments carry those ids rather than re-deriving them later.
    first = next(a for a in corpus.attachments if a.owner == 'item:0000')
    assert first.label_text_ids == (0x028E, 0x028F, 0x0290, 0x0291)
    assert all(len(a.label_text_ids) == len(LABEL_SLOTS) for a in corpus.attachments)


def test_owner_identity_is_established_by_its_own_text(rom):
    """The record is an item because its strings say so, not because upstream did."""
    data = rom.read_bytes()

    def string_at(index):
        pointer = struct.unpack_from(
            '<I', data, TEXT_POINTER_TABLE - 0x08000000 + index * 4)[0]
        offset = pointer - 0x08000000
        out = bytearray()
        while True:
            unit = struct.unpack_from('<H', data, offset)[0]
            if unit == 0:
                break
            out += struct.pack('<H', unit)
            offset += 2
        return out.decode('utf-16le')

    assert string_at(0x028E) == 'Miso Soup'
    assert string_at(0x0290) == 'Miso Soups'
    assert string_at(0x0291).startswith('A tasty, yet nutritious soup.')
    assert string_at(0x0292) == 'Rice Ball'


def test_static40_text_candidates_are_not_promoted_by_adjacency(rom):
    """Item ids start at 0x028E, right after static40's candidates end at 0x028D.

    Adjacency to a proven range is suggestive and nothing more. static40's
    halfwords are read by different code with no path to the text table, so
    they stay CANDIDATE. This test exists to make that refusal deliberate.
    """
    data = rom.read_bytes()
    static40_ids = {struct.unpack_from('<H', data, 0x00720564 + 16 * i + 2)[0]
                    for i in range(40)}
    item_ids = {struct.unpack_from('<H', data, OWNER_TABLE + i * OWNER_STRIDE + 2)[0]
                for i in range(OWNER_COUNT)}
    assert max(static40_ids) == 0x028D
    assert min(item_ids) == 0x028E
    assert not (static40_ids & item_ids)
    # The static40 corpus still declares no reference of any kind.
    static40 = load_scripts(rom, RomProfileCatalog.load('config/roms.yaml'), 'static40')
    assert script_references(static40.ir) == ()


# --------------------------------------------------------------------------
# Semantics stay unknown; the surface stays read-only
# --------------------------------------------------------------------------

def test_native_targets_are_structural_only(rom, corpus):
    """Eight native handlers resolve; none acquires a gameplay name."""
    from tools.webfoot.data.script_specs import OPCODE_SETS
    from tools.webfoot.formats.script_vm import Evidence
    data = rom.read_bytes()
    spec = OPCODE_SETS['stack_be16_buu_v1']
    targets = set()
    for block in corpus.ir.blocks:
        for ins in block.instructions:
            if ins.opcode in (0x02, 0x03):
                secondary = ins.operands[0].value
                targets.add(struct.unpack_from(
                    '<I', data, 0x08055098 - 0x08000000 + secondary * 4)[0])
    assert len(targets) == 8
    # An item description saying "restores hit points" is not proof that any
    # particular native call is the one that does it.
    for opcode in (0x02, 0x03):
        assert spec.lookup(opcode).semantics == Evidence.UNKNOWN
        assert spec.lookup(opcode).evidence == Evidence.CONFIRMED_ROM
    # static40's lone native target does not occur here and stays UNKNOWN.
    assert 0x080007B7 not in targets


def test_no_reference_is_fabricated_from_the_script_bodies(corpus):
    """Text is proven on the OWNER record, not inside the bytecode.

    No operand in these scripts was shown to resolve through the text table, so
    the script bodies still declare no references. Keeping these separate is the
    point: proving one did not license inventing the other.
    """
    assert script_references(corpus.ir) == ()


def test_unknown_family_is_refused(rom):
    with pytest.raises(ScriptError, match='unknown script family'):
        load_scripts(rom, RomProfileCatalog.load('config/roms.yaml'), 'no_such_family')


def test_overlapping_families_are_refused_at_config_load(rom):
    """Two families may not claim the same bytes; that would double-own a script."""
    text = Path('config/roms.yaml').read_text(encoding='utf-8-sig').replace(
        'pool_address: 0x083bbbb0', 'pool_address: 0x08720340')
    with pytest.raises(ProfileConfigError, match='overlap'):
        RomProfileCatalog.loads(text)


def test_no_authoring_command_exists_for_the_new_family(rom):
    """Free capacity is still zero, so growth is absent by construction."""
    from tools.webfoot.cli import build_parser
    parser = build_parser()
    event = parser._subparsers._group_actions[0].choices['event']
    commands = set(event._subparsers._group_actions[0].choices)
    assert not commands & {'write', 'edit', 'author', 'insert', 'relocate', 'grow'}
