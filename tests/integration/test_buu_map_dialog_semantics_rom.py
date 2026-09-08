"""TOOLKIT-021: what the four map-reachable dialogs actually do.

TOOLKIT-020 proved `dialog -> text` for a slot-178 subset and stated plainly
that `map -> placement -> event -> dialog -> text` did NOT close, because the
four dialogs the verified map corpus reaches are a disjoint set. This ticket
resolves those four instead of assuming their behavior is text.

The result is a measured negative plus a positive. The negative: no slot any of
the four calls reaches the text table OR the dialog table, at any depth to 10 -
so there is no direct text chain and no multi-hop `dialog A -> dialog B` route
either. The positive: they are save-state and scene-control logic, and the save
bitfield's TEST/SET/CLEAR primitives are now all three resolved.

A negative is only worth the instrument that produced it, so the same walker is
pointed at the three known positives (slots 178, 182, 216) in this file. If it
ever stops finding those, the negative below stops being evidence.

Evidence: docs/research/BUU_MAP_DIALOG_SEMANTICS.md
"""
from pathlib import Path

import pytest

from tools.webfoot.analysis.thumb import (is_pop_with_pc, ldr_literal_address,
                                          scan_bl)
from tools.webfoot.data.placement_contracts import CONTRACTS
from tools.webfoot.data.script_specs import OPCODE_SETS
from tools.webfoot.formats import placement_links as links
from tools.webfoot.formats.script_vm import assemble
from tools.webfoot.maps import load_maps
from tools.webfoot.placement_events import PlacementEvents
from tools.webfoot.profile import RomProfileCatalog

ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
PROFILE = 'buus_fury_usa_rev0_01c1707f'

#: TOOLKIT-018/019: the only dialogs the verified map corpus reaches.
MAP_REACHABLE = (393, 506, 508, 509)

#: Exact structure of each, so a codec regression fails here too.
#: index -> (dialog_type, code_size, instructions, record_size)
CORPUS = {393: (0, 12, 6, 48), 506: (0, 38, 17, 56),
          508: (0, 56, 20, 824), 509: (0, 54, 20, 88)}

#: Consumer counts, preserved from TOOLKIT-018/019.
CONSUMERS = {393: (3, 7, 1), 506: (2, 30, 2), 508: (5, 5, 1), 509: (5, 5, 1)}
TOTAL_DIALOG_REFERENCES = 15
TOTAL_CONSUMING_PLACEMENTS = 47
TOTAL_CONSUMING_MAPS = 4
EVENT_SAVE_FLAGS = (266, 267)

#: Every native slot the four dialogs call, and how many calls each receives.
SLOT_CENSUS = {0: 3, 4: 10, 5: 1, 26: 2, 29: 2, 55: 1, 100: 1,
               107: 2, 119: 2, 120: 2, 138: 1, 186: 1, 187: 3}

#: Handler addresses, native_table + 4 * slot with the Thumb bit cleared.
SLOT_HANDLERS = {0: 0x08000206, 4: 0x0800026E, 5: 0x0800028A, 26: 0x08000738,
                 29: 0x080007E6, 55: 0x08000C4E, 100: 0x08001C1C,
                 107: 0x08001E6E, 119: 0x08002390, 120: 0x08002404,
                 138: 0x080026EA, 186: 0x080032C2, 187: 0x08003310}

#: The tables the negative is about.
TEXT_TABLE = 0x0806BCE8
DIALOG_TABLE = 0x0879B704

#: The controls. If the walker stops finding these, it proves nothing below.
TEXT_SLOT = 178
DIALOG_SLOTS = (182, 216)

#: One bit-addressing shape, three bitwise operations. That is the whole
#: classification: byte = saveobj + 0x50 + 5 + (bit >> 3), mask = 1 << (bit&7).
FLAG_TEST = 0x08004364
FLAG_SET = 0x08004380
FLAG_CLEAR = 0x08004396
SAVE_OBJECT_LITERAL = 0x08054FBC

#: Flag ranges the dialogs act on, resolved with the handlers' own pop order.
FLAG_RANGES = {506: (284, 3), 508: (287, 3), 509: (287, 3)}

#: Family 2, construct-and-queue: same shape as TOOLKIT-019/020, different
#: destination. No identity is claimed between them.
ALLOCATOR = 0x0803D5B8
QUEUE_APPEND = 0x0801936A

#: Family 3, slot 119.
TRANSITION_WORKER = 0x08008D44
CALL_VIA_VENEER = 0x08046AA4
TRANSITION_STATE_WORD = 0x03002A58
TRANSITION_POPS = 5

#: Generous headroom. The negative is re-checked at every one of these.
SEARCH_DEPTHS = (4, 6, 8, 10)
WALK_LIMIT = 512

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


def _body_end(image, address):
    """First `pop {..,pc}` or `bx lr` at or after `address`, bounded."""
    for step in range(0, WALK_LIMIT * 2, 2):
        offset = address - 0x08000000 + step
        if not 0 <= offset < len(image) - 2:
            break
        halfword = int.from_bytes(image[offset:offset + 2], 'little')
        if is_pop_with_pc(halfword) or halfword == 0x4770:
            return address + step + 2
    return address + WALK_LIMIT * 2


def _reaches(image, entry, target, maxdepth):
    """Whole-call-graph search for a PC-relative literal equal to `target`.

    Every BL is followed and every literal inspected - not one path. The repo's
    own Thumb helpers own BL decoding and literal addressing; re-deriving
    either here would be a second implementation free to drift from the real
    one, which is the defect TOOLKIT-019 hit with its walker.
    """
    seen, stack = set(), [(entry & ~1, 0)]
    while stack:
        address, depth = stack.pop()
        if address in seen or depth > maxdepth:
            continue
        if not 0x08000000 <= address < 0x08000000 + len(image):
            continue
        seen.add(address)
        end = _body_end(image, address)
        for step in range(0, end - address, 2):
            offset = address - 0x08000000 + step
            halfword = int.from_bytes(image[offset:offset + 2], 'little')
            pool = ldr_literal_address(halfword, address + step)
            if pool is not None and _word(image, pool) == target:
                return True
        for bl in scan_bl(image, address - 0x08000000, end - 0x08000000):
            stack.append((bl.target & ~1, depth + 1))
    return False


def _slot_handler(image, slot):
    return _word(image, CONTRACTS[PROFILE]['native_table'] + 4 * slot)


def _slots_of(image, record, spec):
    """Native slots one dialog calls.

    Only opcodes 2 and 3 dispatch natively. Opcode 0 is `push_byte`; counting
    it as a call would invent slots out of pushed constants.
    """
    _, _, ir = links.dialog_code_block(image, record, spec)
    return [ins.operands[0].value
            for block in ir.blocks for ins in block.instructions
            if ins.opcode in (0x02, 0x03) and ins.operands]


# --- the frozen corpus -------------------------------------------------------

def test_the_map_reachable_corpus_is_exactly_four_type_zero_dialogs(events):
    """Ticket section 2. The centre of this ticket, pinned by identity."""
    reached = sorted({r.index for r in events.operand_references()
                      if r.kind == 'event_resource'})
    assert tuple(reached) == MAP_REACHABLE


def test_each_map_reachable_dialog_has_its_exact_structure(records, image, spec):
    """Type, code size, instruction count and record size, all four."""
    for index, (dtype, code, instrs, size) in CORPUS.items():
        record = records[index]
        assert record.supported, f'dialog {index} must stay supported'
        assert record.dialog_type == dtype
        assert record.size == size
        _, raw, ir = links.dialog_code_block(image, record, spec)
        assert len(raw) == code
        assert sum(len(b.instructions) for b in ir.blocks) == instrs


def test_each_map_reachable_dialog_round_trips_exactly(records, image, spec):
    """Semantics are layered above the codec, so the codec must stay exact."""
    for index in MAP_REACHABLE:
        _, raw, ir = links.dialog_code_block(image, records[index], spec)
        assert assemble(ir) == raw, f'dialog {index} stopped round-tripping'


def test_dialog_393_branches_over_its_own_terminate(records, image, spec):
    """The case that disproved a first-terminate extent rule in TOOLKIT-019.

    Its branch_if_zero at +4 targets +9, past a terminate at +7. Cutting the
    block at the first terminate would lose 4 of its 12 bytes.
    """
    _, raw, ir = links.dialog_code_block(image, records[393], spec)
    branches = [ins for b in ir.blocks for ins in b.instructions
                if ins.target is not None]
    assert len(branches) == 1
    assert branches[0].source_offset == 4 and branches[0].target == 9
    terminates = sorted(ins.source_offset for b in ir.blocks
                        for ins in b.instructions if ins.opcode == 0x11)
    assert terminates == [7, 11], 'a terminate is branched over'
    assert len(raw) == 12


def test_dialogs_508_and_509_are_the_same_program_with_different_operands(
        records, image, spec):
    """They share map:0019 and split its placements; only operands differ."""
    shapes = []
    for index in (508, 509):
        _, _, ir = links.dialog_code_block(image, records[index], spec)
        shapes.append([ins.opcode for b in ir.blocks for ins in b.instructions])
    assert shapes[0] == shapes[1]


# --- consumers ---------------------------------------------------------------

def test_consumer_counts_are_preserved(events):
    """Ticket sections 29 and 30: TOOLKIT-018/019 ownership must not move."""
    placements, maps = set(), set()
    for index, (n_events, n_places, n_maps) in CONSUMERS.items():
        found = events.consumers_of('event_resource', index)
        assert len(found['events']) == n_events, f'dialog {index} events'
        assert len(found['placements']) == n_places, f'dialog {index} placements'
        assert len(found['maps']) == n_maps, f'dialog {index} maps'
        placements |= set(found['placements'])
        maps |= set(found['maps'])
    assert len(placements) == TOTAL_CONSUMING_PLACEMENTS
    assert len(maps) == TOTAL_CONSUMING_MAPS


def test_the_event_reference_corpus_is_unchanged(events):
    """15 dialog references plus the two event-level save flags."""
    refs = events.operand_references()
    dialogs = [r for r in refs if r.kind == 'event_resource']
    flags = sorted({r.index for r in refs if r.kind == 'save_flag'})
    assert len(dialogs) == TOTAL_DIALOG_REFERENCES
    assert tuple(flags) == EVENT_SAVE_FLAGS


# --- the native-slot census --------------------------------------------------

def test_the_four_dialogs_native_slot_census_is_exact(records, image, spec):
    """Ticket section 4. Thirteen slots, with exact call counts."""
    census = {}
    for index in MAP_REACHABLE:
        for slot in _slots_of(image, records[index], spec):
            census[slot] = census.get(slot, 0) + 1
    assert census == SLOT_CENSUS


def test_each_slot_resolves_to_its_recorded_handler(image):
    """Handler identity, so a table shift cannot silently repoint a family."""
    for slot, handler in SLOT_HANDLERS.items():
        assert _slot_handler(image, slot) & ~1 == handler


def test_opcode_zero_is_push_byte_and_never_dispatches_natively(spec):
    """The census above is only correct because of this.

    Reading opcode 0 as a native call would invent slots out of pushed
    constants - 30, 75 and 5 in dialogs 508/509 among them.
    """
    by_value = {op.value: op for op in spec.instructions}
    assert by_value[0].name == 'push_byte'
    assert by_value[2].name == 'native_stack'
    assert by_value[3].name == 'native_pop'
    assert tuple(CONTRACTS[PROFILE]['native_opcodes']) == (2, 3)


# --- the central negative, and its control -----------------------------------

def test_the_walker_finds_the_three_known_positive_links(image):
    """The control. Without this the negative below is not evidence.

    These three links were proven by TOOLKIT-019 and TOOLKIT-020 through
    separate investigations. The walker used for the negative must reproduce
    all three, or it is simply an instrument that finds nothing.
    """
    assert _reaches(image, _slot_handler(image, TEXT_SLOT), TEXT_TABLE, 10), \
        'slot 178 must still reach the text table'
    for slot in DIALOG_SLOTS:
        assert _reaches(image, _slot_handler(image, slot), DIALOG_TABLE, 10), \
            f'slot {slot} must still reach the dialog table'


def test_no_map_reachable_slot_reaches_the_text_table(image):
    """Ticket section 34: the non-overlap rule, strengthened not weakened.

    TOOLKIT-019/020 pinned that the four dialogs do not *contain* the text
    base. This is the stronger statement: their entire reachable call graph
    does not reach it either, so no indirect route exists.
    """
    for depth in SEARCH_DEPTHS:
        hits = [slot for slot in SLOT_CENSUS
                if _reaches(image, _slot_handler(image, slot), TEXT_TABLE, depth)]
        assert hits == [], f'no map-reachable slot reaches text at depth {depth}'


def test_no_map_reachable_slot_reaches_the_dialog_table(image):
    """Ticket sections 7 and 8: dialog A -> dialog B does not exist.

    This was the most direct way the separate map->dialog and dialog->text
    halves could have met. They do not.
    """
    for depth in SEARCH_DEPTHS:
        hits = [slot for slot in SLOT_CENSUS
                if _reaches(image, _slot_handler(image, slot), DIALOG_TABLE, depth)]
        assert hits == [], f'no map-reachable slot reaches a dialog at depth {depth}'


def test_the_text_slot_is_absent_from_all_four_dialogs(records, image, spec):
    """The simple statement of the same fact, kept alongside the deep one."""
    for index in MAP_REACHABLE:
        assert TEXT_SLOT not in _slots_of(image, records[index], spec)


# --- family 1: the save-flag primitives --------------------------------------

def test_the_three_flag_primitives_share_one_address_shape(image):
    """What classifies TEST/SET/CLEAR is the bitwise op, not a name.

    All three compute the same byte and mask from the bit index. They differ in
    exactly one instruction: ands, orrs, bics.
    """
    def halfwords(address, count):
        offset = address - 0x08000000
        return [int.from_bytes(image[offset + 2 * i:offset + 2 * i + 2], 'little')
                for i in range(count)]

    # asrs r2,r1,#3 (0x10CA) then adds r0,r2,r0 (0x1810): the byte holding the
    # bit is base + (bit >> 3). Identical opening in all three primitives.
    for address in (FLAG_TEST, FLAG_SET, FLAG_CLEAR):
        assert halfwords(address, 2) == [0x10CA, 0x1810], \
            f'0x{address:08X} does not start with the shared bit-address shape'

    # movs r1,#1 (0x2101), later shifted by the low three bits of the index:
    # mask = 1 << (bit & 7). Also shared by all three.
    for address in (FLAG_TEST, FLAG_SET, FLAG_CLEAR):
        assert 0x2101 in halfwords(address, 10), \
            f'0x{address:08X} does not build a single-bit mask'

    # The strongest form of the claim: SET and CLEAR are byte-identical for
    # their first eight halfwords and diverge at exactly one instruction.
    # Nothing about the addressing differs - only the operation.
    ands, orrs, bics = 0x4008, 0x4311, 0x438A
    assert halfwords(FLAG_SET, 8) == halfwords(FLAG_CLEAR, 8)
    assert halfwords(FLAG_SET, 9)[8] == orrs, 'SET must use orrs'
    assert halfwords(FLAG_CLEAR, 9)[8] == bics, 'CLEAR must use bics'
    assert halfwords(FLAG_TEST, 9)[8] == ands, 'TEST must use ands'

    # And the three operations are mutually exclusive, so no primitive can be
    # silently reclassified as another.
    assert len({orrs, bics, ands}) == 3
    for address, own in ((FLAG_TEST, ands), (FLAG_SET, orrs), (FLAG_CLEAR, bics)):
        others = {ands, orrs, bics} - {own}
        assert not others & set(halfwords(address, 10)), \
            f'0x{address:08X} must use only its own operation'


def test_slot_29_still_proves_set_and_anchors_the_family(image):
    """TOOLKIT-018's proven result, re-derived here as this family's control.

    A classification method that could not reproduce the one already-proven
    member would not be trusted on slots 186 and 187.
    """
    handler = _slot_handler(image, 29) & ~1
    assert handler == SLOT_HANDLERS[29]
    targets = [bl.target & ~1 for bl in
               scan_bl(image, handler - 0x08000000,
                       _body_end(image, handler) - 0x08000000)]
    assert targets == [FLAG_SET], 'slot 29 calls SET and nothing else'
    assert CONTRACTS[PROFILE]['save_flag']['consumers'] == {29: 'set'}


def test_slot_186_tests_a_flag_range_and_slot_187_writes_one(image):
    """Ticket section 11: TEST / SET / CLEAR classified by consumer code."""
    test_handler = _slot_handler(image, 186) & ~1
    test_calls = {bl.target & ~1 for bl in
                  scan_bl(image, test_handler - 0x08000000,
                          _body_end(image, test_handler) - 0x08000000)}
    assert test_calls == {FLAG_TEST}, 'slot 186 only tests'

    write_handler = _slot_handler(image, 187) & ~1
    write_calls = {bl.target & ~1 for bl in
                   scan_bl(image, write_handler - 0x08000000,
                           _body_end(image, write_handler) - 0x08000000)}
    assert write_calls == {FLAG_SET, FLAG_CLEAR}, 'slot 187 sets and clears'


def test_the_clear_primitive_is_now_reached_and_recorded(image):
    """OLD CLAIM: clear is "unreached by this corpus, so only SET is claimed."

    NEW EVIDENCE: slot 187, called by dialogs 506, 508 and 509, calls it.
    RESOLUTION: recorded under `dialog_save_flag`, kept separate from the
    event-level `save_flag` because a different consumer proved it.
    """
    contract = CONTRACTS[PROFILE]['dialog_save_flag']
    assert contract['consumers'] == {186: 'test_range', 187: 'write_range'}
    assert contract['primitives'] == {'test': FLAG_TEST, 'set': FLAG_SET,
                                      'clear': FLAG_CLEAR}
    # The two contracts stay distinct: only one of them reaches CLEAR.
    assert 'clear' not in CONTRACTS[PROFILE]['save_flag']['consumers'].values()


def test_the_flag_consumers_share_the_save_object(image):
    """Every caller reaches the bitfield through [0x08054FBC + 0x14]."""
    for slot in (29, 186, 187):
        handler = _slot_handler(image, slot) & ~1
        end = _body_end(image, handler)
        literals = []
        for step in range(0, end - handler, 2):
            offset = handler - 0x08000000 + step
            halfword = int.from_bytes(image[offset:offset + 2], 'little')
            pool = ldr_literal_address(halfword, handler + step)
            if pool is not None:
                literals.append(_word(image, pool))
        assert SAVE_OBJECT_LITERAL in literals, f'slot {slot} save object'


def test_the_flag_ranges_the_dialogs_act_on_are_exact(records, image, spec):
    """Base and count come from push_many, read with the handlers' pop order.

    The operation is proven; what flags 284-289 MEAN in the game is not, and
    nothing here names them.
    """
    for index, (base, count) in FLAG_RANGES.items():
        _, _, ir = links.dialog_code_block(image, records[index], spec)
        pushes = [tuple(o.value for o in ins.operands)
                  for b in ir.blocks for ins in b.instructions
                  if ins.opcode == 0x1D and len(ins.operands) == 3]
        assert (2, base, count) in pushes, f'dialog {index} flag range'


# --- family 2: construct and queue -------------------------------------------

def test_slots_100_and_107_construct_and_queue(image):
    """Same shape as TOOLKIT-019/020, different destination, no identity."""
    for slot in (100, 107):
        handler = _slot_handler(image, slot) & ~1
        targets = {bl.target & ~1 for bl in
                   scan_bl(image, handler - 0x08000000,
                           _body_end(image, handler) - 0x08000000)}
        assert QUEUE_APPEND in targets, f'slot {slot} appends to a list'
    handler = _slot_handler(image, 100) & ~1
    targets = {bl.target & ~1 for bl in
               scan_bl(image, handler - 0x08000000,
                       _body_end(image, handler) - 0x08000000)}
    assert ALLOCATOR in targets, 'slot 100 allocates before queueing'


# --- family 3: slot 119 ------------------------------------------------------

def test_slot_119_pops_five_and_matches_its_callers_push(records, image, spec):
    """Its arity is read from the handler, then checked against the dialogs.

    Both callers push exactly five values, which is what makes the coordinate
    pair claim structural rather than positional guesswork.
    """
    handler = _slot_handler(image, 119) & ~1
    # Five `str r1,[r0]` stack-depth writebacks, one per popped value.
    offset = handler - 0x08000000
    body = image[offset:_body_end(image, handler) - 0x08000000]
    assert body.count((0x6001).to_bytes(2, 'little')) == TRANSITION_POPS

    for index in (508, 509):
        _, _, ir = links.dialog_code_block(image, records[index], spec)
        pushes = [ins.operands[0].value for b in ir.blocks
                  for ins in b.instructions if ins.opcode == 0x1D]
        assert TRANSITION_POPS in pushes, f'dialog {index} pushes five for 119'


def test_slot_119_releases_an_object_then_calls_the_transition_worker(image):
    """Structural only. No gameplay verb is promoted from this."""
    handler = _slot_handler(image, 119) & ~1
    end = _body_end(image, handler)
    targets = [bl.target & ~1 for bl in
               scan_bl(image, handler - 0x08000000, end - 0x08000000)]
    assert CALL_VIA_VENEER in targets, 'virtual release through the veneer'
    assert TRANSITION_WORKER in targets, 'then the worker'
    literals = []
    for step in range(0, end - handler, 2):
        offset = handler - 0x08000000 + step
        halfword = int.from_bytes(image[offset:offset + 2], 'little')
        pool = ldr_literal_address(halfword, handler + step)
        if pool is not None:
            literals.append(_word(image, pool))
    assert TRANSITION_STATE_WORD in literals


def test_slot_119_reaches_no_presentation_target(image):
    """Rejects "slot 119 is the dialog close / wait primitive".

    Its call graph is the largest in this corpus at 70 nodes, and none of it
    reaches text. Naming it a presentation primitive would be exactly the
    context-guessing TOOLKIT-020 refused for slot 139.
    """
    handler = _slot_handler(image, 119)
    assert not _reaches(image, handler, TEXT_TABLE, 10)
    assert not _reaches(image, handler, DIALOG_TABLE, 10)


# --- preserved refutations ---------------------------------------------------

def test_toolkit_018_event_to_text_refutation_still_stands(events):
    """Event operands become dialogs and save flags, never text."""
    kinds = {r.kind for r in events.operand_references()}
    assert kinds == {'event_resource', 'save_flag'}, 'no event operand is text'


def test_the_slot_139_wait_hypothesis_is_not_revived_by_context(records, image, spec):
    """TOOLKIT-020 refuted it. It is not in this corpus, so nothing revives it."""
    for index in MAP_REACHABLE:
        assert 139 not in _slots_of(image, records[index], spec)


def test_the_non_type_zero_corpus_stays_closed(records):
    """Ticket sections 10 and 26: the escalation condition was never met.

    No map-reachable dialog invokes another dialog record, so no subtype was
    opened and the 286 refused records are untouched.
    """
    assert len([r for r in records if not r.supported]) == 286
    assert len([r for r in records if r.supported]) == 236
