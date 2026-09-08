"""TOOLKIT-019: event-resource record structure, measured against the ROM.

TOOLKIT-018 proved that map-scene event operands select entries of table
0x0879B704 and stopped there, with the records' internals UNKNOWN. This ticket
opens the records themselves.

The naming here is the engine's own. Consumer 0x0800327E reaches 0x08004098,
which asserts "Expected dialog to start with a code block" against source file
T:\\Source\\ByteCodeInterpreter\\ByteCodeInterpreter.cpp line 60. That is a
developer-left string in the shipped image, so "dialog" and "code block" are
Webfoot's own terms for these structures, not an interpretation of gameplay.
What a dialog *does* on screen is still UNKNOWN and nothing here claims
otherwise.

Evidence: docs/research/BUU_EVENT_RESOURCE.md
"""
from pathlib import Path

import pytest

from tools.webfoot.data.placement_contracts import CONTRACTS
from tools.webfoot.data.script_specs import OPCODE_SETS
from tools.webfoot.formats import placement_links as links
from tools.webfoot.formats.script_vm import ScriptError, assemble
from tools.webfoot.maps import load_maps
from tools.webfoot.placement_events import PlacementEvents
from tools.webfoot.profile import RomProfileCatalog

ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
PROFILE = 'buus_fury_usa_rev0_01c1707f'

TABLE = 0x0879B704
POOL_START = 0x0877C5A4
COUNT = 522
#: Independently corroborated: Data Crystal records this as the start of a
#: separate compressed-text region. The canonical measurement stays primary.
TABLE_END = 0x0879BF2C
POOL_BYTES = 127328

#: The four records reachable from the supported map-scene event corpus.
REACHABLE = (393, 506, 508, 509)

#: Interpreter 0x08004038 indexes this table; index 31 onward is the assertion
#: string, which is what bounds it at 31 entries.
DIALOG_DISPATCH_TABLE = 0x080554C0
ASSERTION_STRING = 0x0805553C
SOURCE_PATH_STRING = 0x08004160

#: Consumer 0x080030F8 (slot 182) selects the record, then constructs and
#: queues an object. Consumer 0x0800327E (slot 216) selects from the same table
#: and runs the record instead.
CONSTRUCT_CONSUMER_TABLE_LOAD = 0x08003118
CONSTRUCT_CONSUMER_CALL = 0x08003120
OBJECT_CONSTRUCTOR = 0x08012588
EXECUTE_CONSUMER_TABLE_LOAD = 0x080032B0
EXECUTE_CONSUMER_CALL = 0x080032BA
DIALOG_ENTRY = 0x08004098
#: ldrb r1,[r0,#2] inside 0x08004098 - the promoted dialog type field.
DIALOG_TYPE_READ = 0x080040BA


def _bl_target(image, address):
    """Absolute target of the 32-bit Thumb BL at `address`."""
    offset = address - 0x08000000
    high = int.from_bytes(image[offset:offset + 2], 'little')
    low = int.from_bytes(image[offset + 2:offset + 4], 'little')
    displacement = ((high & 0x7FF) << 12) | ((low & 0x7FF) << 1)
    if displacement & (1 << 22):
        displacement -= 1 << 23
    return address + 4 + displacement

pytestmark = pytest.mark.skipif(not ROM.exists(), reason='canonical ROM not present')


@pytest.fixture(scope='module')
def events():
    return PlacementEvents(load_maps(ROM, RomProfileCatalog.load('config/roms.yaml')))


@pytest.fixture(scope='module')
def records(events):
    return events.resource_records()


@pytest.fixture(scope='module')
def spec():
    return OPCODE_SETS[CONTRACTS[PROFILE]['encoding']]


def test_the_pointer_table_is_pinned_where_two_methods_agree():
    contract = CONTRACTS[PROFILE]['event_resource']
    assert contract['table'] == TABLE
    assert contract['count'] == COUNT
    assert contract['pool_start'] == POOL_START
    assert TABLE + 4 * COUNT == TABLE_END


def test_records_tile_the_pool_exhaustively_without_gap_or_overlap(records):
    assert len(records) == COUNT
    assert records[0].start == POOL_START - 0x08000000
    assert records[-1].end == TABLE - 0x08000000
    for earlier, later in zip(records, records[1:]):
        assert earlier.end == later.start, 'a gap or overlap would break identity'
    assert sum(r.size for r in records) == POOL_BYTES


def test_the_table_is_strictly_ascending(records):
    assert all(a.start < b.start for a, b in zip(records, records[1:]))


def test_record_size_distribution_is_deterministic(records):
    sizes = [r.size for r in records]
    assert min(sizes) == 16
    assert max(sizes) == 3168
    assert len(set(sizes)) == 166
    assert all(size % 4 == 0 for size in sizes), 'records stay word aligned'


def test_every_record_but_the_first_opens_with_a_pool_pointer(records):
    """The consumer dereferences +0x00 before reading anything else.

    Record 0 is the single exception and is reported as it measures rather than
    forced into the rule; a census that hid it would be the wrong kind of tidy.
    """
    pool, table = POOL_START - 0x08000000, TABLE - 0x08000000
    inside = [r for r in records if pool <= r.dialog_offset < table]
    assert len(inside) == 521
    assert records[0] not in inside


def test_the_dialog_type_byte_partitions_the_corpus(records):
    """Type is read at dialog+0x02 and branched on at 0x080040BA..0x080040C2."""
    counts = {}
    for record in records:
        counts[record.dialog_type] = counts.get(record.dialog_type, 0) + 1
    assert counts == {0: 236, 3: 2, 4: 141, 5: 139, 6: 2, 7: 2}
    assert links.DIALOG_TYPE_CODE_BLOCK == 0
    assert links.DIALOG_TYPE_PACKED == 4


def test_only_a_type_zero_dialog_is_claimed_supported(records):
    """Type 4 is real but expands through a routine relocated into IWRAM.

    Its algorithm is not resolvable from ROM bytes, so it is declared
    unsupported instead of being decoded on a guess.
    """
    assert all(r.supported == (r.dialog_type == 0) for r in records)
    assert sum(1 for r in records if r.supported) == 236


def test_the_four_reachable_records_have_exact_identities(events, records):
    reached = sorted({r.index for r in events.operand_references()
                      if r.kind == 'event_resource'})
    assert reached == list(REACHABLE)
    expected = {
        393: (7938672, 7938720, 48),
        506: (7972544, 7972600, 56),
        508: (7973388, 7974212, 824),
        509: (7974212, 7974300, 88),
    }
    for index, (start, end, size) in expected.items():
        record = records[index]
        assert (record.start, record.end, record.size) == (start, end, size)
        assert record.slot_offset == (TABLE - 0x08000000) + 4 * index


def test_the_four_reachable_records_are_all_code_block_dialogs(records):
    assert all(records[i].dialog_type == 0 for i in REACHABLE)
    assert all(records[i].supported for i in REACHABLE)


def test_each_reachable_dialog_decodes_and_re_encodes_exactly(events, records, spec):
    """Exact re-encode is the guarantee; the extent is walked, never searched."""
    image = events.maps.base_bytes
    expected = {393: (12, 6), 506: (38, 17), 508: (56, 20), 509: (54, 20)}
    for index, (size, instructions) in expected.items():
        start, raw, ir = links.dialog_code_block(image, records[index], spec)
        assert start == records[index].dialog_offset + links.DIALOG_CODE_OFFSET
        assert len(raw) == size
        assert assemble(ir) == raw
        assert sum(len(b.instructions) for b in ir.blocks) == instructions


def test_a_dialog_may_branch_over_its_own_terminate(events, records, spec):
    """Record 393 is why the extent follows reachability, not first terminate.

    Its branch_if_zero at +4 targets +9, which sits past a terminate at +7. A
    first-terminate rule would cut the block at 8 bytes and lose real code.
    """
    _, raw, _ = links.dialog_code_block(events.maps.base_bytes, records[393], spec)
    assert len(raw) == 12
    assert raw[7] == 0x11 and raw[11] == 0x11, 'two terminates, one unreachable'


def test_unsupported_records_are_refused_rather_than_guessed(events, records, spec):
    packed = [r for r in records if r.dialog_type == links.DIALOG_TYPE_PACKED]
    assert packed, 'the packed form must remain represented'
    assert links.dialog_code_block(events.maps.base_bytes, packed[0], spec) is None


def test_every_supported_dialog_in_the_corpus_re_encodes_exactly(events, records, spec):
    """All 236 type-0 dialogs, not just the four reachable ones."""
    image = events.maps.base_bytes
    decoded = code_bytes = 0
    for record in records:
        if not record.supported:
            continue
        _, raw, ir = links.dialog_code_block(image, record, spec)
        assert assemble(ir) == raw
        decoded += 1
        code_bytes += len(raw)
    assert (decoded, code_bytes) == (236, 10263)


def test_a_malformed_table_pointer_is_rejected(events):
    image = bytearray(events.maps.base_bytes)
    table = TABLE - 0x08000000
    image[table:table + 4] = (0x08000000).to_bytes(4, 'little')
    with pytest.raises(ValueError, match='outside declared pool'):
        links.event_resource_records(bytes(image), CONTRACTS[PROFILE]['event_resource'])


def test_a_non_ascending_table_is_rejected(events):
    image = bytearray(events.maps.base_bytes)
    table = TABLE - 0x08000000
    image[table + 4:table + 8] = POOL_START.to_bytes(4, 'little')
    with pytest.raises(ValueError, match='ascending'):
        links.event_resource_records(bytes(image), CONTRACTS[PROFILE]['event_resource'])


def test_resource_show_is_deterministic_and_uses_stable_identities(events):
    first = [events.resource_show(i) for i in REACHABLE]
    second = [events.resource_show(i) for i in REACHABLE]
    assert first == second
    assert [v['identity'] for v in first] == [f'event_resource:{i:04d}'
                                              for i in REACHABLE]


def test_an_out_of_range_resource_index_is_refused(events):
    with pytest.raises(ScriptError):
        events.resource_show(COUNT)


def test_toolkit_018_reference_counts_do_not_regress(events):
    refs = [r for r in events.operand_references() if r.kind == 'event_resource']
    assert len(refs) == 15
    assert len({r.event for r in refs}) == 15
    assert len({r.index for r in refs}) == 4
    flags = [r for r in events.operand_references() if r.kind == 'save_flag']
    assert sorted({r.index for r in flags}) == [266, 267]
    assert {r.access for r in flags} == {'set'}


def test_no_reachable_dialog_reaches_the_text_table(events, records, spec):
    """TOOLKIT-018's refutation is not reopened by this ticket.

    A dialog is a script for the VM the toolkit already models, so it could
    only reach text through a proven text consumer. None of the reachable
    dialogs even contains the text table base, and this pins that.
    """
    image = events.maps.base_bytes
    needle = (0x0806BCE8).to_bytes(4, 'little')
    for index in REACHABLE:
        _, raw, _ = links.dialog_code_block(image, records[index], spec)
        assert needle not in raw


def test_the_dialog_interpreter_uses_the_vm_the_toolkit_already_models(events):
    """The central claim of this ticket: there is no second Buu VM.

    Interpreter 0x08004038 fetches one opcode byte and calls through dispatch
    table 0x080554C0. Every entry of that table is compared against the
    *actual* declared specification imported from script_specs, not against a
    copy pasted in here, so the two cannot drift apart silently.
    """
    from tools.webfoot.data.script_specs import _BUU_HANDLERS

    image = events.maps.base_bytes
    table = DIALOG_DISPATCH_TABLE - 0x08000000
    decoded = tuple(int.from_bytes(image[table + 4 * i:table + 4 * i + 4], 'little')
                    for i in range(len(_BUU_HANDLERS)))
    assert len(_BUU_HANDLERS) == 31, 'the declared Buu VM has 31 opcodes'
    assert decoded == _BUU_HANDLERS, 'ROM dispatch table is the declared VM'
    # Slot 17 is the null terminator, which is why it carries no handler.
    assert decoded[17] == 0
    assert all(raw & 1 for i, raw in enumerate(decoded) if i != 17), 'Thumb'


def test_the_dispatch_table_ends_where_the_assertion_string_begins(events):
    """The 31-entry bound is measured, not assumed.

    Index 31 onward is UTF-16 text, and it is the very assertion that names
    this subsystem. That is what bounds the table.
    """
    image = events.maps.base_bytes
    after = DIALOG_DISPATCH_TABLE - 0x08000000 + 4 * 31
    assert after == ASSERTION_STRING - 0x08000000
    text = image[after:after + 2 * 60].decode('utf-16-le').split('\x00')[0]
    assert text == '"Expected dialog to start with a code block"'


def test_the_engine_names_its_own_source_file(events):
    """Provenance for the word "dialog": it is Webfoot's, not an interpretation."""
    image = events.maps.base_bytes
    start = SOURCE_PATH_STRING - 0x08000000
    raw = image[start:start + 64]
    assert raw[:raw.index(b'\x00')].decode('ascii') == (
        r'T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp')


def test_the_two_consumers_differ_in_operation_not_in_record_format(events):
    """Same resource class, different operation - the TOOLKIT-019 discriminator.

    Both handlers load the same table base and index it identically. They then
    diverge into different callees: one constructs and queues an object, the
    other runs the record. Pinning the shared load plus the divergent call is
    what stops a later reader concluding these are two record formats, two
    resource classes or two VMs.
    """
    image = events.maps.base_bytes
    table = CONTRACTS[PROFILE]['event_resource']['table']

    def literal(address):
        """Value of the PC-relative word an ldr at `address` loads."""
        offset = address - 0x08000000
        displacement = image[offset] * 4
        pool = (((address + 4) & ~3) + displacement) - 0x08000000
        return int.from_bytes(image[pool:pool + 4], 'little')

    # Both consumers select from the SAME table, at the analogous instruction.
    assert literal(CONSTRUCT_CONSUMER_TABLE_LOAD) == table
    assert literal(EXECUTE_CONSUMER_TABLE_LOAD) == table
    # ...and both index it the same way: lsls r0,r0,#2 then ldr rX,[r1,r0].
    def opcode_at(address):
        offset = address - 0x08000000
        return image[offset:offset + 2]

    assert opcode_at(CONSTRUCT_CONSUMER_TABLE_LOAD + 2) == b'\x80\x00'
    assert opcode_at(EXECUTE_CONSUMER_TABLE_LOAD + 2) == b'\x80\x00'
    # The operation differs: the callees are different routines.
    assert _bl_target(image, CONSTRUCT_CONSUMER_CALL) == OBJECT_CONSTRUCTOR
    assert _bl_target(image, EXECUTE_CONSUMER_CALL) == DIALOG_ENTRY
    assert OBJECT_CONSTRUCTOR != DIALOG_ENTRY


def test_the_execute_consumer_branches_on_the_dialog_type_byte(events):
    """0x08004098 reads dialog+0x02 and dispatches on it.

    This is the one record field TOOLKIT-019 promotes, so the instruction that
    reads it is pinned rather than only described.
    """
    image = events.maps.base_bytes
    offset = DIALOG_TYPE_READ - 0x08000000
    # ldrb r1,[r0,#2] - the type byte, two bytes into the dereferenced dialog.
    assert image[offset:offset + 2] == b'\x81\x78'
    assert links.DIALOG_TYPE_CODE_BLOCK == 0
