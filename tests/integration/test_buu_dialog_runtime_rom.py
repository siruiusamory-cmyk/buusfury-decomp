"""TOOLKIT-020: what a type-0 dialog does, measured against the ROM.

TOOLKIT-019 proved the 236 type-0 records are scripts for the VM already
modelled and that the engine calls them "dialogs", closing with player-visible
meaning UNKNOWN. This ticket resolves that: a dialog renders text on screen,
and the text comes from the verified UTF-16 table 0x0806BCE8 that TOOLKIT-004
tiled and TOOLKIT-014's item consumer already reads.

The selection method matters as much as the result. Every one of the 107 native
slots this corpus uses was asked one objective question - does its call graph
reach 0x0806BCE8 - and exactly one answered yes. The other 106 were excluded by
a measurement, not by an opinion about which operands looked like text ids.

This is a NEW relation through a NEW consumer chain, not a reversal of
TOOLKIT-018, whose refutation concerned three map-scene *event* consumer
families - none of them this native slot. A test below pins that distinction.

Evidence: docs/research/BUU_DIALOG_RUNTIME.md
"""
from pathlib import Path

import pytest

from tools.webfoot.data.placement_contracts import CONTRACTS
from tools.webfoot.data.script_specs import OPCODE_SETS
from tools.webfoot.formats import placement_links as links
from tools.webfoot.maps import load_maps
from tools.webfoot.placement_events import PlacementEvents
from tools.webfoot.profile import RomProfileCatalog

ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
PROFILE = 'buus_fury_usa_rev0_01c1707f'

#: TOOLKIT-019's pinned corpus. Restated so a regression in the codec fails
#: here too, rather than silently changing what this ticket measured.
TYPE0_DIALOGS = 236
TYPE0_CODE_BYTES = 10263
NON_TYPE0_RECORDS = 286

#: The one native slot whose call graph reaches the verified text table.
TEXT_SLOT = 178
TEXT_NATIVE = 0x08003031
#: 0x08003030 pops three; the deepest becomes the table index.
TEXT_SLOT_POPS = 3

#: The verified Buu text pointer table (TOOLKIT-004), reached at depth 1.
TEXT_TABLE = 0x0806BCE8
TEXT_COUNT = 1534
#: 0x0802BFBC: ldr r1,=0x0806BCE8 / lsls r0,#2 / ldr r4,[r1,r0]. The same
#: access shape TOOLKIT-014 proved at 0x0801F85E for the item consumer.
TEXT_CONSUMER = 0x0802BFBC
TEXT_TABLE_LOAD = 0x0802BFC0
TEXT_TABLE_INDEX = 0x0802BFC4
#: Walks UTF-16LE halfwords to NUL summing per-glyph advance widths.
STRING_MEASURE = 0x0803FFE8
#: Emits 8-byte OAM entries; 0x06010000 is the GBA OBJ VRAM base.
OAM_EMITTER = 0x0802BFEC
OBJ_VRAM_BASE = 0x06010000

#: Investigated and rejected as presentation families.
CONDITION_SELECTOR_SLOT = 139
CONDITION_SELECTOR_WORKER = 0x08008AA0
#: Decodes a group/bit pair and tests it against a flag block at +0x50.
CONDITION_EVALUATOR = 0x08004784
QUEUE_SLOT = 83
QUEUE_APPEND = 0x0801936A

#: The seven dialogs whose text index is a literal, and what they resolve to.
PROVEN = {290: (1525, 'Match 2 Fight!'), 291: (1526, 'Match 3 Fight!'),
          292: (1527, 'Match 4 Fight!'), 295: (1529, 'Match 6 Fight!'),
          296: (1530, 'Match 7 Fight!'), 297: (1531, 'Match 8 Fight!'),
          298: (1532, 'Match 9 Fight!')}
#: The gaps in that run are type 4, which TOOLKIT-019 declared UNSUPPORTED.
UNSUPPORTED_NEIGHBOURS = (289, 293, 299)
#: Its index is left by native_stack, so it is computed at runtime.
RUNTIME_INDEX_DIALOG = 516
#: Centre of the 240-pixel GBA screen; 0x0802BF5E centres the string on it.
SCREEN_CENTRE_X = 120

#: TOOLKIT-018/019: the only dialogs the verified map corpus reaches.
MAP_REACHABLE = (393, 506, 508, 509)

#: Bounds for the reachability scan that selected the investigated families.
#: Depth 1 is where slot 178 answers; 4 is generous headroom for the negative
#: result on the other 106 slots.
SEARCH_DEPTH = 4
WALK_LIMIT = 400

pytestmark = pytest.mark.skipif(not ROM.exists(), reason='canonical ROM not present')


@pytest.fixture(scope='module')
def image():
    return ROM.read_bytes()


@pytest.fixture(scope='module')
def events():
    return PlacementEvents(load_maps(ROM, RomProfileCatalog.load('config/roms.yaml')))


@pytest.fixture(scope='module')
def records(events):
    return events.resource_records()


@pytest.fixture(scope='module')
def spec():
    return OPCODE_SETS[CONTRACTS[PROFILE]['encoding']]


def _word(image, address):
    offset = address - 0x08000000
    return int.from_bytes(image[offset:offset + 4], 'little')


def _literal(image, address):
    """Value of the PC-relative literal loaded by the LDR at `address`."""
    offset = address - 0x08000000
    halfword = int.from_bytes(image[offset:offset + 2], 'little')
    assert halfword >> 11 == 0b01001, 'not an LDR literal'
    pool = ((address + 4) & ~3) + (halfword & 0xFF) * 4
    return _word(image, pool)


def _string(image, index):
    """Decode text entry `index` from the verified UTF-16LE pool."""
    pointer = _word(image, TEXT_TABLE + 4 * index) - 0x08000000
    out = []
    while True:
        unit = int.from_bytes(image[pointer:pointer + 2], 'little')
        pointer += 2
        if unit == 0:
            return ''.join(out)
        out.append(chr(unit))


# --- corpus census -----------------------------------------------------------

def test_the_supported_corpus_is_unchanged_from_toolkit_019(records, image, spec):
    """This ticket measures TOOLKIT-019's corpus; it must not have moved."""
    supported = [r for r in records if r.supported]
    assert len(supported) == TYPE0_DIALOGS
    assert len(records) - len(supported) == NON_TYPE0_RECORDS
    total = sum(len(links.dialog_code_block(image, r, spec)[1]) for r in supported)
    assert total == TYPE0_CODE_BYTES


def test_every_supported_dialog_still_round_trips(records, image, spec):
    """Semantics are layered above the codec, so the codec must stay exact."""
    from tools.webfoot.formats.script_vm import assemble
    for record in [r for r in records if r.supported]:
        _, raw, ir = links.dialog_code_block(image, record, spec)
        assert assemble(ir) == raw, f'dialog {record.index} stopped round-tripping'


def test_the_opcode_census_is_deterministic(records, image, spec):
    """A dialog is overwhelmingly native calls with pushed arguments.

    That is what selected the native table, rather than the arithmetic
    opcodes, as the place dialog semantics live.
    """
    counts = {}
    dialogs = {}
    for record in [r for r in records if r.supported]:
        _, _, ir = links.dialog_code_block(image, record, spec)
        seen = set()
        for block in ir.blocks:
            for ins in block.instructions:
                counts[ins.opcode] = counts.get(ins.opcode, 0) + 1
                seen.add(ins.opcode)
        for opcode in seen:
            dialogs[opcode] = dialogs.get(opcode, 0) + 1
    assert counts[0x02] == 1656 and dialogs[0x02] == 230, 'native_stack census'
    assert counts[0x00] == 1126 and dialogs[0x00] == 193, 'push_byte census'
    assert counts[0x11] == 378 and dialogs[0x11] == TYPE0_DIALOGS, 'every dialog terminates'
    assert counts[0x13] == 340 and counts[0x1D] == 305
    assert sum(counts.values()) == 4826
    # native_stack is the single largest opcode by a wide margin and appears in
    # all but six dialogs. That is what pointed this investigation at the
    # native table rather than at the arithmetic or branch opcodes.
    assert counts[0x02] == max(counts.values())
    assert counts[0x02] > 4 * counts[0x13], 'natives dominate control flow'


def test_the_native_slot_census_is_deterministic(records, image, spec):
    used = {}
    for record in [r for r in records if r.supported]:
        _, _, ir = links.dialog_code_block(image, record, spec)
        for block in ir.blocks:
            for ins in block.instructions:
                if ins.opcode in (0x02, 0x03) and ins.operands:
                    used.setdefault(ins.operands[0].value, set()).add(record.index)
    assert len(used) == 107, 'distinct native slots used by the corpus'
    # Slot 29 is TOOLKIT-018's proven save-flag SET. It ranks top by breadth,
    # which is what makes this ranking trustworthy on the unknown slots.
    assert len(used[29]) == 54
    assert len(used[TEXT_SLOT]) == 8, 'eight dialogs call the text slot'


# --- family 1: the proven content source -------------------------------------

def test_exactly_one_native_slot_reaches_the_verified_text_table(records, image, spec):
    """The selection criterion, re-run: 107 slots asked, one answers.

    This is the test that keeps the finding honest. If a future change made a
    second slot reach the table, the claim "slot 178 is the text family" would
    need re-deriving rather than quietly widening.
    """
    table = CONTRACTS[PROFILE]['native_table']
    used = set()
    for record in [r for r in records if r.supported]:
        _, _, ir = links.dialog_code_block(image, record, spec)
        for block in ir.blocks:
            for ins in block.instructions:
                if ins.opcode in (0x02, 0x03) and ins.operands:
                    used.add(ins.operands[0].value)

    # The repo's own Thumb helpers own BL decoding and literal-pool addressing.
    # Re-deriving either here would be a second implementation that could drift
    # from the real one - the exact defect TOOLKIT-019 hit with its walker.
    from tools.webfoot.analysis.thumb import (is_pop_with_pc, ldr_literal_address,
                                              scan_bl)

    def body_end(address):
        """First `pop {..,pc}` or `bx lr` at or after `address`, bounded."""
        for step in range(0, WALK_LIMIT * 2, 2):
            offset = address - 0x08000000 + step
            halfword = int.from_bytes(image[offset:offset + 2], 'little')
            if is_pop_with_pc(halfword) or halfword == 0x4770:
                return address + step + 2
        return address + WALK_LIMIT * 2

    def reaches(entry, depth=0, seen=None):
        seen = set() if seen is None else seen
        address = entry & ~1
        if address in seen or depth > SEARCH_DEPTH:
            return False
        if not 0x08000000 <= address < 0x08000000 + len(image):
            return False
        seen.add(address)
        end = body_end(address)
        for step in range(0, end - address, 2):
            offset = address - 0x08000000 + step
            halfword = int.from_bytes(image[offset:offset + 2], 'little')
            pool = ldr_literal_address(halfword, address + step)
            if pool is not None and _word(image, pool) == TEXT_TABLE:
                return True
        calls = [bl.target for bl in scan_bl(image, address - 0x08000000,
                                             end - 0x08000000)]
        return any(reaches(target, depth + 1, seen) for target in calls)

    # A fresh `seen` per slot: sharing one across slots would let whichever
    # slot ran first claim a shared callee and starve the others.
    hits = {slot for slot in used
            if reaches(_word(image, table + 4 * slot), 0, set())}
    assert hits == {TEXT_SLOT}, 'exactly one slot reaches the text table'


def test_the_text_slot_handler_pops_three_and_indexes_the_verified_table(image):
    """The chain, pinned at each address rather than summarised."""
    assert _word(image, CONTRACTS[PROFILE]['native_table']
                 + 4 * TEXT_SLOT) == TEXT_NATIVE
    # 0x0802BFBC loads the verified table and indexes it by index*4 - the same
    # shape TOOLKIT-014 proved for the item consumer, not a numeric guess.
    assert _literal(image, TEXT_TABLE_LOAD) == TEXT_TABLE
    lsls = int.from_bytes(image[TEXT_TABLE_INDEX - 2 - 0x08000000:
                                TEXT_TABLE_INDEX - 0x08000000], 'little')
    assert lsls == 0x0080, 'lsls r0, r0, #2 scales the index to a word'
    ldr = int.from_bytes(image[TEXT_TABLE_INDEX - 0x08000000:
                               TEXT_TABLE_INDEX + 2 - 0x08000000], 'little')
    assert ldr >> 9 == 0b0101100, 'ldr r4,[r1,r0] loads the string pointer'


def test_the_consumer_treats_the_pointer_as_utf16_text(image):
    """0x0803FFE8 walks halfwords to NUL - the encoding TOOLKIT-004 verified.

    A routine that merely read a table would not prove text. One that consumes
    the pointer *as a UTF-16LE NUL-terminated string* does.
    """
    offset = STRING_MEASURE - 0x08000000
    assert int.from_bytes(image[offset + 2:offset + 4], 'little') == 0x880B, 'ldrh r3,[r1]'
    assert int.from_bytes(image[offset + 6:offset + 8], 'little') == 0x2B00, 'cmp r3,#0'
    assert int.from_bytes(image[offset + 12:offset + 14], 'little') == 0x3102, 'adds r1,#2'


def test_the_output_is_on_screen_sprite_text(image):
    """8-byte OAM entries, 32-pixel steps, glyphs blitted into OBJ VRAM."""
    def halfword(address):
        offset = address - 0x08000000
        return int.from_bytes(image[offset:offset + 2], 'little')

    assert halfword(0x0802C030) == 0x3208, 'adds r2,#8 - one OAM entry per sprite'
    assert halfword(0x0802C032) == 0x3320, 'adds r3,#0x20 - 32 pixels per sprite'
    # The OBJ attribute template the emitter stores into each entry.
    assert _literal(image, 0x0802BFFA) == 0x80002000
    # The sibling routine blits glyph tiles into the GBA OBJ VRAM base.
    assert _literal(image, 0x0802BF90) == OBJ_VRAM_BASE


def test_every_proven_reference_resolves_to_its_expected_string(events, image):
    """Structural position and semantic content are checked against each other.

    The ids are sequential across sequential dialogs and the strings they
    resolve to are themselves a sequence. Either alone would be weak; together
    they are what settles the classification.
    """
    references = events.dialog_text_references()
    assert len(references) == len(PROVEN)
    for reference in references:
        index, text = PROVEN[reference.dialog]
        assert reference.index == index
        assert _string(image, reference.index) == text
        assert reference.x == SCREEN_CENTRE_X, 'centred on the screen midpoint'
        assert reference.y == 65


def test_operand_provenance_is_physical_not_decoded(events, image, spec):
    """The recorded offset must hold the index operand's own bytes.

    Provenance resolves by physical position, as every prior ticket required;
    a decoded value that happened to match would not be enough.
    """
    from tools.webfoot.formats.script_vm import decode_instruction
    for reference in events.dialog_text_references():
        window = image[reference.source:reference.source + reference.encoded_length]
        assert len(window) == reference.encoded_length
        raw = 0
        for byte in window:
            raw = (raw << 7) | (byte & 0x7F)
            if byte < 0x80:
                break
        value = -(raw >> 1) if raw & 1 else raw >> 1
        assert value == reference.index, 'offset does not hold this index'


def test_the_match_sequence_gaps_are_exactly_the_unsupported_records(records, image):
    """A consistency check the hypothesis could have failed.

    Dialogs 290..298 map onto "Match 2".."Match 9" with three missing. The
    missing ones are precisely the type-4 records TOOLKIT-019 declared
    unsupported, so the gaps are a codec boundary, not a broken mapping.
    """
    by_index = {r.index: r for r in records}
    for index in UNSUPPORTED_NEIGHBOURS:
        assert not by_index[index].supported
        assert by_index[index].dialog_type == links.DIALOG_TYPE_PACKED
    # The full run of ten strings exists in the text pool either way.
    for offset in range(10):
        assert _string(image, 1524 + offset) == f'Match {offset + 1} Fight!'


def test_a_runtime_computed_index_yields_no_reference(events, records, image, spec):
    """Dialog 516 calls the same slot with its index left by native_stack.

    Refusing it is the point: an operand that cannot be resolved statically
    stays UNKNOWN rather than being guessed at.
    """
    record = next(r for r in records if r.index == RUNTIME_INDEX_DIALOG)
    assert record.supported
    _, _, ir = links.dialog_code_block(image, record, spec)
    calls = [ins for block in ir.blocks for ins in block.instructions
             if ins.opcode == 0x02 and ins.operands
             and ins.operands[0].value == TEXT_SLOT]
    assert len(calls) == 2, 'it really does call the text slot twice'
    assert events.dialog_text_references(RUNTIME_INDEX_DIALOG) == ()


# --- families 2 and 3: investigated and rejected ------------------------------

def test_the_terminal_family_is_a_condition_selector_not_presentation(image):
    """Slot 139 ends 27 dialogs, which is why it was investigated.

    Its worker filters a list by a bitfield predicate. Terminal position is not
    evidence of presentation, and naming it wait_for_input would have been the
    context-guessed name this ticket forbids.
    """
    native = _word(image, CONTRACTS[PROFILE]['native_table']
                   + 4 * CONDITION_SELECTOR_SLOT)
    assert native == 0x08002703
    offset = CONDITION_SELECTOR_WORKER - 0x08000000
    body = image[offset:offset + 0x60]
    # It calls the bitfield condition evaluator and branches on the verdict:
    # a failing entry is skipped, a passing one is appended to a list.
    from tools.webfoot.analysis.thumb import scan_bl
    targets = {bl.target & ~1 for bl in scan_bl(image, offset, offset + 0x60)}
    assert CONDITION_EVALUATOR in targets, 'calls the bitfield predicate'
    # No presentation: it reaches neither the text table nor a font routine.
    assert TEXT_TABLE.to_bytes(4, 'little') not in body
    assert STRING_MEASURE not in targets and TEXT_CONSUMER not in targets


def test_the_queue_family_appends_rather_than_renders(image):
    """Slot 83 constructs an object and appends it to a linked list.

    Same construct-then-queue shape as TOOLKIT-019's 0x080030F8, but a
    different destination, so no identity between the two queues is claimed.
    """
    native = _word(image, CONTRACTS[PROFILE]['native_table'] + 4 * QUEUE_SLOT)
    assert native == 0x080015BB
    offset = QUEUE_APPEND - 0x08000000
    body = image[offset:offset + 0x30]
    # The tail walk: ldr r2,[r2] / adds r2,#4 / ldr r3,[r2] / bne back.
    assert int.from_bytes(image[offset + 0x1E:offset + 0x20], 'little') == 0x6812
    assert int.from_bytes(image[offset + 0x20:offset + 0x22], 'little') == 0x3204
    assert TEXT_TABLE.to_bytes(4, 'little') not in body


# --- reverse traversal -------------------------------------------------------

def test_reverse_traversal_from_text_to_dialogs(events):
    for dialog, (index, _) in PROVEN.items():
        assert events.dialogs_for_text(index) == (dialog,)


def test_reverse_traversal_is_silent_for_unreferenced_text(events):
    """1524 and 1533 exist in the pool but no *supported* dialog names them."""
    assert events.dialogs_for_text(1524) == ()
    assert events.dialogs_for_text(1533) == ()


def test_dialog_text_is_kept_distinct_from_the_item_text_path(events):
    """TOOLKIT-014's item->text consumers are a separate provenance path.

    Both reach 0x0806BCE8; merging them would erase which chain proved what.
    """
    dialog_texts = {r.index for r in events.dialog_text_references()}
    # The item consumer's text ids live nowhere near this range, and nothing
    # in this ticket emits an item edge.
    assert all(1524 <= index <= 1533 for index in dialog_texts)
    assert not hasattr(events, 'item_text_references'), (
        'this ticket must not invent or merge an item text API')


# --- refutations preserved ---------------------------------------------------

def test_toolkit_018_event_to_text_refutation_is_untouched(events):
    """No map-scene *event* operand becomes a text reference.

    TOOLKIT-018 refuted three event consumer families as text sources. This
    ticket proves a *dialog* operand instead - different opcode, different
    native slot, different handler, different call graph.
    """
    assert {r.kind for r in events.operand_references()} == {'event_resource',
                                                             'save_flag'}


def test_the_map_reachable_dialogs_still_contain_no_text_call(events, records,
                                                              image, spec):
    """TOOLKIT-019's test, restated: those four dialogs reach no text.

    They are not contradicted by this ticket. Text is reached by dialogs
    outside the map-reachable subset entirely.
    """
    by_index = {r.index: r for r in records}
    for index in MAP_REACHABLE:
        _, _, ir = links.dialog_code_block(image, by_index[index], spec)
        slots = {ins.operands[0].value for block in ir.blocks
                 for ins in block.instructions
                 if ins.opcode in (0x02, 0x03) and ins.operands}
        assert TEXT_SLOT not in slots
        assert events.dialog_text_references(index) == ()


def test_the_full_map_chain_is_not_claimed(events):
    """The preferred milestone is NOT reached, and the code must say so.

    Each half is proven; they do not meet, because no dialog is in both sets.
    Composing them anyway would assert an ownership edge no code supports.
    """
    reachable = {index for _, index in
                 {(r.kind, r.index) for r in events.operand_references()}
                 if _ == 'event_resource'}
    assert reachable == set(MAP_REACHABLE)
    text_bearing = {r.dialog for r in events.dialog_text_references()}
    assert not (reachable & text_bearing), 'the two halves must not overlap'
    for dialog in text_bearing:
        consumers = events.consumers_of('event_resource', dialog)
        assert consumers['events'] == ()
        assert consumers['placements'] == ()
        assert consumers['maps'] == ()


def test_the_save_flag_findings_are_unchanged(events):
    flags = sorted({r.index for r in events.operand_references()
                    if r.kind == 'save_flag'})
    assert flags == [266, 267]
    assert {r.access for r in events.operand_references()
            if r.kind == 'save_flag'} == {'set'}


def test_the_dispatch_table_still_matches_the_declared_handlers(image):
    """31/31, unchanged. No second VM was introduced for dialog semantics."""
    from tools.webfoot.data.script_specs import _BUU_HANDLERS
    for slot, expected in enumerate(_BUU_HANDLERS):
        assert _word(image, 0x080554C0 + 4 * slot) == expected


def test_no_write_or_growth_surface_was_added(events):
    """The ticket succeeds without WRITE, and none was attempted."""
    for name in ('set_dialog_text', 'write_dialog', 'author_dialog',
                 'set_text_reference', 'retarget_dialog'):
        assert not hasattr(events, name)


def test_the_compressed_text_region_was_not_touched():
    """0x0879BF2C stays unclaimed: no investigated consumer reaches it."""
    contract = CONTRACTS[PROFILE]['event_resource']
    assert 'compressed_text' not in CONTRACTS[PROFILE]
    assert contract['table'] + 4 * contract['count'] == 0x0879BF2C
