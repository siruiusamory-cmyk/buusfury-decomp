"""TOOLKIT-013: the Buu's Fury bounded script/event corpus, proved against the ROM.

Buu runs the same VM *architecture* as Legacy of Goku II but a different
implementation. These tests pin the differences that a transferred LOGII decoder
would have got silently wrong, so a future edit cannot quietly re-introduce them.
"""
from pathlib import Path
import hashlib
import struct
from collections import Counter
from dataclasses import replace
import pytest
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.scripts import load_scripts, script_references
from tools.webfoot.formats.script_vm import assemble, ScriptError
from tools.webfoot.capability import CapabilityError

SHA = '940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e'

#: Measured extent of the static40 family (docs/research/BUU_SCRIPT_VM.md).
POOL_START = 0x00720340
POOL_SIZE = 548
TABLE = 0x00720564
ENTRY_RECORDS = 40
ENTRY_ROOTS = 120
INSTRUCTIONS = 328


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
    return load_scripts(rom, RomProfileCatalog.load('config/roms.yaml'))


def test_exhaustive_supported_corpus_identity(rom, corpus):
    """Every supported byte decodes and re-encodes byte-identically."""
    assert len(corpus.ir.entries) == ENTRY_ROOTS
    assert len(corpus.ir.blocks) == ENTRY_ROOTS
    assert corpus.instruction_count == INSTRUCTIONS
    assert corpus.source_offset == POOL_START
    assert corpus.ir.extent == POOL_SIZE
    # No uncovered bytes: the roots tile the pool, which is what proves the
    # operand widths rather than merely being consistent with them.
    assert not corpus.ir.opaque
    original = rom.read_bytes()[POOL_START:POOL_START + POOL_SIZE]
    assert assemble(corpus.ir) == original


def test_opcode_coverage_is_the_measured_census(corpus):
    assert Counter(i.opcode for b in corpus.ir.blocks
                   for i in b.instructions) == {0: 108, 1: 14, 2: 84, 4: 2, 17: 120}
    # Exactly one terminator per entry root, so no root runs off its stream.
    assert sum(1 for b in corpus.ir.blocks
               for i in b.instructions if i.opcode == 17) == ENTRY_ROOTS


def test_entry_enumeration_is_deterministic(rom, corpus):
    again = load_scripts(rom, RomProfileCatalog.load('config/roms.yaml'))
    assert corpus == again
    assert [e.identity for e in corpus.ir.entries] == [e.identity for e in again.ir.entries]


def test_entry_identity_is_stable_and_carries_no_rom_address(corpus):
    """Authoring identity must survive relocation, so it names slots not addresses."""
    for entry in corpus.ir.entries:
        profile, family, ordinal, slot = entry.identity.split(':')
        assert profile == 'buus_fury_usa_rev0_01c1707f'
        assert family == 'static40'
        assert 0 <= int(ordinal) < ENTRY_RECORDS
        assert slot in ('slot04', 'slot08', 'slot0c')
        assert f'{POOL_START:x}' not in entry.identity
    assert len({e.identity for e in corpus.ir.entries}) == ENTRY_ROOTS


def test_no_reference_is_fabricated(corpus):
    """The corpus proves no text/map/native reference, so none may be claimed."""
    assert script_references(corpus.ir) == ()


def test_executable_interpreter_and_root_contract(rom):
    """The addresses the profile depends on are what the executable actually holds."""
    d = rom.read_bytes()
    u = lambda pos: struct.unpack_from('<I', d, pos)[0]
    # Interpreter 0x08004038 loads its dispatch table from the literal at 0x0800415C.
    assert u(0x415C) == 0x080554C0
    # 31 slots: 0x11 is the null terminator and 0x1F is not a handler at all
    # (it is UTF-16 text), which is what bounds the opcode set.
    assert u(0x0554C0 + 0x11 * 4) == 0
    assert all(u(0x0554C0 + i * 4) & 1 for i in range(31) if i != 0x11)
    assert not (0x08000000 <= u(0x0554C0 + 0x1F * 4) < 0x08000000 + len(d))
    # The static walker's table literal and its `cmp r6,#0x28` loop bound.
    assert u(0x01441C) == 0x08720564
    assert d[0x014254:0x014256] == bytes.fromhex('282e')


def test_entry_table_shape_is_as_measured(rom):
    """120 distinct, non-null, strictly ascending roots ending exactly at the table."""
    d = rom.read_bytes()
    roots = [struct.unpack_from('<I', d, TABLE + 16 * i + 4 + 4 * j)[0]
             for i in range(ENTRY_RECORDS) for j in range(3)]
    assert len(roots) == ENTRY_ROOTS
    assert all(roots)
    assert len(set(roots)) == ENTRY_ROOTS
    assert roots == sorted(roots)
    assert min(roots) == 0x08000000 + POOL_START
    # The pool ends exactly where the entry table begins - a sharp boundary.
    assert 0x08000000 + POOL_START + POOL_SIZE == 0x08000000 + TABLE


def test_buu_branch_contract_differs_from_logii(rom):
    """Pin the divergences a transferred LOGII decoder would have corrupted.

    LOGII reads a one-byte displacement from the post-operand cursor. Buu reads
    a two-byte big-endian displacement from the pre-operand cursor, and 0x1C
    subtracts. Getting any of these wrong still "decodes", just wrongly.
    """
    from tools.webfoot.data.script_specs import OPCODE_SETS
    buu = OPCODE_SETS['stack_be16_buu_v1']
    logii = OPCODE_SETS['stack_be7_v1']
    for opcode in (0x12, 0x13, 0x1C):
        assert buu.lookup(opcode).encoding == 'be16'
        assert buu.lookup(opcode).branch_base == 'before_operand'
        assert logii.lookup(opcode).encoding == 'u8'
        assert logii.lookup(opcode).branch_base == 'after_operand'
    assert buu.lookup(0x1C).flow == 'count_back'
    assert buu.lookup(0x11).flow == 'stop'
    # Slot 0x1E is a real handler in Buu; in LOGII it is not a verified opcode.
    assert buu.lookup(0x1E).encoding == 'none'
    assert len(buu.instructions) == 31


def test_unknown_semantics_stay_unknown(corpus):
    """Structural support must not imply a gameplay meaning."""
    from tools.webfoot.data.script_specs import OPCODE_SETS
    from tools.webfoot.formats.script_vm import Evidence
    buu = OPCODE_SETS['stack_be16_buu_v1']
    # The single native operation this corpus uses is a shared handler; naming it
    # from one calling context is exactly the historical mistake.
    assert buu.lookup(2).semantics == Evidence.UNKNOWN
    assert buu.lookup(2).evidence == Evidence.CONFIRMED_ROM
    secondaries = {i.operands[0].value for b in corpus.ir.blocks
                   for i in b.instructions if i.opcode == 2}
    assert secondaries == {27}


def test_widened_extent_refused_at_config_load(rom):
    """The pool abuts the entry table exactly, so growing it by one byte is a
    provable overlap and is refused when the catalog is parsed - before any ROM
    read. Fixed-size support only: TOOLKIT-011 measured free capacity as zero."""
    from tools.webfoot.profile import ProfileConfigError
    text = Path('config/roms.yaml').read_text().replace(
        'pool_size: 548', 'pool_size: 549')
    assert 'pool_size: 549' in text
    with pytest.raises(ProfileConfigError, match='overlaps'):
        RomProfileCatalog.loads(text)


def test_altered_extent_refused_against_packaged_contract(rom):
    """A shrunk extent parses, so the packaged contract is what refuses it."""
    text = Path('config/roms.yaml').read_text().replace(
        'pool_size: 548', 'pool_size: 540')
    with pytest.raises(CapabilityError):
        load_scripts(rom, RomProfileCatalog.loads(text))


def test_opcode_profile_allowlist_enforced(rom, monkeypatch):
    from tools.webfoot.data.script_specs import OPCODE_SETS
    spec = OPCODE_SETS['stack_be16_buu_v1']
    monkeypatch.setitem(OPCODE_SETS, 'stack_be16_buu_v1', replace(spec, profiles=()))
    with pytest.raises(ScriptError, match='not verified for this profile'):
        load_scripts(rom, RomProfileCatalog.load('config/roms.yaml'))


def test_wrong_game_opcode_set_is_refused(rom):
    """LOGII's opcode set must not be usable against the Buu image.

    The packaged-contract check refuses the swapped encoding before the decoder
    is reached at all, so the wrong grammar never touches the bytes.
    """
    text = Path('config/roms.yaml').read_text().replace(
        'encoding: stack_be16_buu_v1', 'encoding: stack_be7_v1')
    with pytest.raises(CapabilityError):
        load_scripts(rom, RomProfileCatalog.loads(text))


def test_round_trip_alone_does_not_discriminate_the_grammars(rom):
    """Honest bound on what this corpus proves.

    This corpus uses only opcodes 00/01/02/04/11, whose widths are identical in
    both games, so LOGII's grammar decodes and round-trips it just as cleanly.
    The round-trip therefore does NOT by itself prove the Buu branch contract -
    the handler disassembly does (see the branch-contract test above), and the
    packaged-contract check is what keeps the right grammar bound to the right
    ROM. Recorded so nobody later mistakes a passing round-trip for proof that
    the encoding was validated end to end.
    """
    from tools.webfoot.data.script_specs import OPCODE_SETS
    from tools.webfoot.formats.script_vm import Entry, disassemble
    image = rom.read_bytes()
    data = image[POOL_START:POOL_START + POOL_SIZE]
    roots = [struct.unpack_from('<I', image, TABLE + 16 * i + 4 + 4 * j)[0]
             - (0x08000000 + POOL_START)
             for i in range(ENTRY_RECORDS) for j in range(3)]
    entries = tuple(Entry(f'root:{n:03d}', off) for n, off in enumerate(roots))
    both = [disassemble(data, entries, OPCODE_SETS[name])
            for name in ('stack_be16_buu_v1', 'stack_be7_v1')]
    for ir in both:
        assert not ir.opaque and len(ir.blocks) == ENTRY_ROOTS
        assert assemble(ir) == data
    # The corpus exercises none of the opcodes where the two grammars diverge.
    used = {i.opcode for b in both[0].blocks for i in b.instructions}
    assert used == {0, 1, 2, 4, 17}
    assert not used & {0x12, 0x13, 0x1C}
