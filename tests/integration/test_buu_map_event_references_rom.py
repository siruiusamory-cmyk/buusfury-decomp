"""TOOLKIT-018: map-scene event operand references, measured against the ROM.

Two reference classes are proven here and one hypothesis is refuted. The
refutation carries tests of its own on purpose: the operands that reach the
event-resource table look exactly like text ids, and without a pinned negative
a later reader could revive that reading from the numbers alone.

Evidence: docs/research/BUU_MAP_EVENT_REFERENCES.md
"""
from pathlib import Path
import struct

import pytest

from tools.webfoot.data.placement_contracts import CONTRACTS
from tools.webfoot.formats.placement_links import operand_references
from tools.webfoot.formats.script_vm import _operand
from tools.webfoot.maps import load_maps
from tools.webfoot.placement_events import PlacementEvents
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.scripts import load_scripts

ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
PROFILE = 'buus_fury_usa_rev0_01c1707f'

#: The verified TOOLKIT-004 text infrastructure, used only to prove absence.
TEXT_TABLE = 0x0806BCE8
TEXT_ENTRIES = 1534
TEXT_POOL = (0x0805792C, 0x0806BCE6)

#: Measured corpus, pinned by TOOLKIT-016 and unchanged by this ticket.
ROOTS, BLOCKS, INSTRUCTIONS, EXTENT = 25, 42, 202, 514

pytestmark = pytest.mark.skipif(not ROM.exists(), reason='canonical ROM not present')


def contract_table(image):
    """File offset of the event-resource pointer table."""
    return CONTRACTS[PROFILE]['event_resource']['table'] - 0x08000000


@pytest.fixture(scope='module')
def catalog():
    return RomProfileCatalog.load('config/roms.yaml')


@pytest.fixture(scope='module')
def events(catalog):
    return PlacementEvents(load_maps(ROM, catalog))


@pytest.fixture(scope='module')
def image():
    return ROM.read_bytes()


@pytest.fixture(scope='module')
def contract():
    return CONTRACTS[PROFILE]


@pytest.fixture(scope='module')
def references(events):
    return events.operand_references()


# --- census -----------------------------------------------------------------

def test_corpus_census_is_unchanged(catalog):
    """The reference work must not perturb the corpus it reads."""
    corpus = load_scripts(ROM, catalog, 'placement_descriptor_event')
    assert len(corpus.ir.entries) == ROOTS
    assert len(corpus.ir.blocks) == BLOCKS
    assert corpus.instruction_count == INSTRUCTIONS
    assert sum(s.size for s in corpus.segments) == EXTENT
    assert len(corpus.attachments) == 57


def test_opcode_census_is_exact(catalog):
    corpus = load_scripts(ROM, catalog, 'placement_descriptor_event')
    census = {}
    for block in corpus.ir.blocks:
        for ins in block.instructions:
            census[ins.opcode] = census.get(ins.opcode, 0) + 1
    assert census == {0x00: 41, 0x01: 2, 0x02: 74, 0x03: 2, 0x04: 1, 0x07: 5,
                      0x08: 6, 0x0F: 1, 0x11: 25, 0x12: 1, 0x13: 5, 0x1B: 3,
                      0x1C: 3, 0x1D: 33}
    assert sum(census.values()) == INSTRUCTIONS
    assert census[0x1C] == 3, 'the three canonical backward branches must survive'


def test_instruction_enumeration_is_deterministic(catalog):
    def enumerate_once():
        corpus = load_scripts(ROM, catalog, 'placement_descriptor_event')
        return [(b.identity, i.source_offset, i.opcode)
                for b in corpus.ir.blocks for i in b.instructions]
    assert enumerate_once() == enumerate_once()


# --- event resource ---------------------------------------------------------

def test_event_resource_table_is_bounded(image, contract):
    """522 ascending pointers whose records tile the pool exhaustively."""
    resource = contract['event_resource']
    base = resource['table'] - 0x08000000
    pointers = [struct.unpack_from('<I', image, base + 4 * i)[0]
                for i in range(resource['count'])]
    assert all(a < b for a, b in zip(pointers, pointers[1:]))
    assert all(p % 4 == 0 for p in pointers)
    assert pointers[0] == resource['pool_start']
    # The pool ends exactly where its own table begins, with no gap and no
    # overlap; that is what makes the 522 bound a measurement, not a guess.
    sizes = [b - a for a, b in zip(pointers, pointers[1:] + [resource['table']])]
    assert sum(sizes) == resource['table'] - resource['pool_start'] == 127328
    assert min(sizes) > 0


def test_event_resource_table_has_exactly_two_inbound_references(image, contract):
    """Both are the consumer literal pools; nothing else names the table."""
    needle = struct.pack('<I', contract['event_resource']['table'])
    hits = [i for i in range(0, len(image) - 3, 4) if image[i:i + 4] == needle]
    assert hits == [0x31C0, 0x3444]


def test_event_resource_references_are_exact(references):
    resource = [r for r in references if r.kind == 'event_resource']
    assert len(resource) == 15
    assert sorted({r.index for r in resource}) == [393, 506, 508, 509]
    assert {r.access for r in resource} == {''}


def test_every_resource_index_resolves_inside_the_pool(image, contract, references):
    resource = contract['event_resource']
    base = resource['table'] - 0x08000000
    for ref in references:
        if ref.kind != 'event_resource':
            continue
        assert 0 <= ref.index < resource['count']
        target = struct.unpack_from('<I', image, base + 4 * ref.index)[0]
        assert resource['pool_start'] <= target < resource['table']


def test_operand_provenance_round_trips_through_the_image(image, references):
    """Reading the recorded physical bytes must reproduce the operand value.

    This is what makes ``source`` provenance rather than decoration: the offset
    survives IR virtualisation and still names the real encoded field.
    """
    for ref in references:
        operand, end = _operand(image, ref.source, 'sm7')
        assert operand.value == ref.index
        assert end - ref.source == ref.encoded_length
        assert len(operand.encoding) == ref.encoded_length


# --- save flag --------------------------------------------------------------

def test_save_flag_references_are_exact(references):
    flags = [r for r in references if r.kind == 'save_flag']
    assert len(flags) == 2
    assert sorted(r.index for r in flags) == [266, 267]


def test_save_flag_access_is_set_only(references, contract):
    """0x08004396 clears bits but the corpus never reaches it, so only SET."""
    assert contract['save_flag']['consumers'] == {29: 'set'}
    assert {r.access for r in references if r.kind == 'save_flag'} == {'set'}


def test_save_flag_consumer_is_a_bitfield_set(image):
    """Pin the exact arithmetic: byte = operand >> 3, bit = operand & 7."""
    setter = image[0x4380:0x4394]
    clearer = image[0x4396:0x43AA]
    # asrs r2,r1,#3 selects the byte; lsls r3,r1,#0x1d then lsrs r3,r3,#0x1d
    # isolates the low three bits as the bit number.
    assert struct.unpack_from('<H', setter, 0)[0] == 0x10CA   # asrs r2, r1, #3
    assert struct.unpack_from('<H', setter, 4)[0] == 0x074B   # lsls r3, r1, #29
    # The two routines are byte-identical apart from the combining instruction,
    # which is exactly what makes one a set and the other a clear.
    assert setter[:0x10] == clearer[:0x10]
    assert struct.unpack_from('<H', setter, 0x10)[0] == 0x4311   # orrs r1, r2
    assert struct.unpack_from('<H', clearer, 0x10)[0] == 0x438A  # bics r2, r1


# --- refutation of the text hypothesis --------------------------------------

def test_no_map_scene_event_emits_a_text_reference(references):
    """The whole point of the ticket, pinned negative."""
    assert {r.kind for r in references} == {'event_resource', 'save_flag'}
    assert not [r for r in references if r.kind == 'text']


def test_resource_indices_are_not_promoted_despite_text_range(references):
    """Every index sits inside 0..1533 and none of them is a text reference.

    If this test ever fails because something started classifying these as
    text, the classifier has regressed to numeric-range reasoning.
    """
    values = [r.index for r in references]
    assert values, 'guard against a vacuous pass'
    assert all(0 <= v < TEXT_ENTRIES for v in values)
    assert all(r.kind != 'text' for r in references)


def test_consumers_never_reach_the_verified_text_table(image):
    """None of the three consumer functions carries the text table literal."""
    needle = struct.pack('<I', TEXT_TABLE)
    for start, size in ((0x0030F8, 0x120), (0x00327E, 0x1D0), (0x012588, 0x60)):
        assert needle not in image[start:start + size]


def test_no_resource_record_references_text_infrastructure(image, contract):
    """The records themselves hold no text pointer and no real string start."""
    resource = contract['event_resource']
    base = resource['table'] - 0x08000000
    starts = {struct.unpack_from('<I', image, TEXT_TABLE - 0x08000000 + 4 * i)[0]
              for i in range(TEXT_ENTRIES)}
    low, high = TEXT_POOL
    table_hits, string_hits, coincidences = 0, 0, 0
    for word in range(resource['pool_start'] - 0x08000000, base, 4):
        value = struct.unpack_from('<I', image, word)[0]
        if value == TEXT_TABLE:
            table_hits += 1
        elif low <= value <= high:
            coincidences += 1
            if value in starts:
                string_hits += 1
    assert table_hits == 0
    assert string_hits == 0
    # Three words land in the pool's numeric range by coincidence. Two are odd
    # aligned, which no UTF-16LE string start can be.
    assert coincidences == 3


def test_item_use_text_references_still_confirmed(catalog):
    """TOOLKIT-014 must not regress; its proof is a different mechanism."""
    corpus = load_scripts(ROM, catalog, 'item_use')
    assert len(corpus.ir.blocks) == 86
    assert corpus.instruction_count == 351
    assert len(corpus.attachments) == 23
    assert any(a.label_text_ids for a in corpus.attachments)


def test_static40_text_values_remain_candidates(catalog):
    """Still CANDIDATE, still not promoted, still not demoted to refuted."""
    corpus = load_scripts(ROM, catalog, 'static40')
    assert corpus.instruction_count == 328
    assert not any(a.label_text_ids for a in corpus.attachments)


# --- traversal --------------------------------------------------------------

def test_forward_traversal_map_to_resource(events, references):
    """map -> placement -> descriptor -> event -> resource, by pointer only."""
    for ref in references:
        owners = [d for d in events.descriptors if d.event == ref.event]
        assert owners, f'{ref.event} must have a descriptor owner'
        assert all(d.placements for d in owners)


def test_reverse_consumers_of_a_shared_resource(events):
    """Sharing is real and must be visible; five placements reach index 508."""
    found = events.consumers_of('event_resource', 508)
    assert found['maps'] == ('map:0019',)
    assert len(found['events']) == 5
    assert len(found['placements']) == 5


def test_reverse_consumers_of_a_save_flag(events):
    found = events.consumers_of('save_flag', 266)
    assert found['maps'] == ('map:0240',)
    assert found['placements'] == ('map:0240/placement:0000',)


def test_reverse_consumers_of_an_unreferenced_index(events):
    assert events.consumers_of('event_resource', 0) == {
        'events': (), 'placements': (), 'maps': ()}


# --- project representation -------------------------------------------------

def test_project_document_preserves_every_reference(events, references):
    document = events.project_document()
    assert len(document['operand_references']) == len(references)
    # Multiple references from one event are preserved individually rather than
    # collapsed into a single field.
    keys = [(r['event'], r['ir_offset']) for r in document['operand_references']]
    assert len(keys) == len(set(keys))


def test_project_document_is_deterministic(catalog):
    first = PlacementEvents(load_maps(ROM, catalog)).project_document()
    second = PlacementEvents(load_maps(ROM, catalog)).project_document()
    assert first == second


def test_low_level_script_bytes_remain_authoritative(events):
    """References are supplemental; the raw event bytes still round-trip."""
    document = events.project_document()
    for event in events.events:
        assert document['events'][event.identity]['raw'] == event.original_bytes.hex()


# --- graph ------------------------------------------------------------------

def test_graph_anchors_each_referenced_resource_slot(events, catalog, image):
    from tools.webfoot.document import RomDocument
    maps = load_maps(ROM, catalog)
    base = RomDocument.from_bytes(maps.base_bytes, maps.profile)
    extended = PlacementEvents(maps).extend_references(base)
    slots = sorted(a.identity.value for a in extended.anchors
                   if a.kind == 'event_resource_slot')
    assert slots == ['event_resource:0393', 'event_resource:0506',
                     'event_resource:0508', 'event_resource:0509']
    # One anchor per distinct referenced slot, shared by all its consumers,
    # so 15 references collapse to 4 anchors.
    assert len(slots) == 4
    # Each anchor covers the real 4-byte table slot for its index.
    table = contract_table(image)
    for anchor in extended.anchors:
        if anchor.kind != 'event_resource_slot':
            continue
        index = int(anchor.identity.value.rsplit(':', 1)[1])
        assert anchor.range.start.value == table + 4 * index
        assert anchor.range.size == 4


def test_graph_counts_are_deterministic(catalog):
    from tools.webfoot.document import RomDocument

    def build():
        maps = load_maps(ROM, catalog)
        document = RomDocument.from_bytes(maps.base_bytes, maps.profile)
        extended = PlacementEvents(maps).extend_references(document)
        return len(extended.anchors), len(extended.references)

    #: TOOLKIT-025: the graph is larger because the placement census is larger, not
    #: because anything here changed shape. Bounding each map's object array by the
    #: engine's `MapEntry+0x04` count recovered 117 placement records the frozen
    #: contract could not express, and each one contributes its anchors and references
    #: like every other placement. The equality either side of the literal is the real
    #: invariant - two independent builds of the same bytes agree exactly - and it is
    #: asserted first so a determinism break is never mistaken for a stale total.
    assert build() == build() == (217, 1850)


def test_save_flag_gets_no_rom_anchor(catalog):
    """A flag is a runtime bit; it owns no ROM bytes to protect."""
    from tools.webfoot.document import RomDocument
    maps = load_maps(ROM, catalog)
    extended = PlacementEvents(maps).extend_references(
        RomDocument.from_bytes(maps.base_bytes, maps.profile))
    assert not [a for a in extended.anchors if 'save_flag' in a.identity.value]


# --- fail closed ------------------------------------------------------------

def test_index_outside_the_declared_table_is_rejected(events, contract):
    corpus = events.corpus()
    narrowed = dict(contract['event_resource'])
    narrowed['count'] = 400  # 506/508/509 now fall outside
    with pytest.raises(ValueError):
        operand_references(corpus.ir, corpus.segments, narrowed,
                           contract['save_flag'])


def test_repeated_operand_values_resolve_by_position(events, contract, image):
    """An operand is identified by position, never by matching its value.

    On the canonical corpus every selected index happens to be the first
    occurrence of its value, so a by-value lookup would agree by luck. This
    test therefore drives the real classifier at a pop depth that lands on a
    duplicated operand, where the two rules disagree: `block:0010` pushes
    (3, 506, 0, 0) and depth 1 selects the LAST zero at position 3, while a
    by-value lookup would return the first zero at position 2 and report the
    wrong physical offset.
    """
    corpus = events.corpus()
    duplicated = [ins for block in corpus.ir.blocks for ins in block.instructions
                  if ins.opcode == 0x1D
                  and len({o.value for o in ins.operands[1:]}) < len(ins.operands) - 1]
    assert duplicated, 'guard against a vacuous pass'

    # Depth 1 makes the classifier select each consumer's top-of-stack operand,
    # which for the (3, 506, 0, 0) push is the duplicated trailing zero.
    shallow = dict(contract['event_resource'])
    shallow['consumers'] = {slot: 1 for slot in contract['event_resource']['consumers']}
    found = operand_references(corpus.ir, corpus.segments, shallow,
                               contract['save_flag'])
    resource = [r for r in found if r.kind == 'event_resource']
    assert resource, 'depth-1 reclassification must still produce references'

    # Value alone cannot distinguish the two zeros, so assert the exact offset.
    # map:0021 encodes (3, 506, 0, 0) with both zeros one byte wide, so the
    # selected trailing zero sits at 0x73B01; a by-value lookup would return
    # the first zero at 0x73B00.
    zeros = [r for r in resource if r.event.startswith('map:0021')]
    assert [(r.index, r.source) for r in zeros] == [(0, 0x73B01)]

    for ref in resource:
        operand, _ = _operand(image, ref.source, 'sm7')
        assert operand.value == ref.index

    # And the real contract depths still round-trip.
    for ref in events.operand_references():
        operand, _ = _operand(image, ref.source, 'sm7')
        assert operand.value == ref.index


def test_unknown_consumer_slot_yields_no_references(events, contract):
    """An operand is classified only through a declared consumer."""
    corpus = events.corpus()
    silent = dict(contract['event_resource'])
    silent['consumers'] = {}
    found = operand_references(corpus.ir, corpus.segments, silent,
                               {'consumers': {}})
    assert found == ()


def test_canonical_rom_is_unchanged(image):
    import hashlib
    digest = hashlib.sha256(image).hexdigest()
    assert digest == ('940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808'
                      'bc36f059e')


# --- CLI --------------------------------------------------------------------

def _run(capsys, *argv):
    from tools.webfoot.cli import main
    assert main(list(argv)) == 0
    import json
    return json.loads(capsys.readouterr().out)


def test_cli_reports_every_reference(capsys, references):
    found = _run(capsys, 'event', 'references', str(ROM))
    assert len(found) == len(references)
    assert {r['kind'] for r in found} == {'event_resource', 'save_flag'}


def test_cli_answers_where_a_resource_is_used(capsys):
    found = _run(capsys, 'event', 'consumers-of', str(ROM), 'event_resource:0508')
    assert found['maps'] == ['map:0019']
    assert len(found['placements']) == 5


def test_cli_answers_where_a_save_flag_is_set(capsys):
    found = _run(capsys, 'event', 'consumers-of', str(ROM), 'save_flag:0266')
    assert found['maps'] == ['map:0240']


def test_cli_rejects_an_unknown_resource_kind(capsys):
    from tools.webfoot.cli import main
    assert main(['event', 'consumers-of', str(ROM), 'text:0266']) == 2


def test_no_reference_authoring_command_exists():
    """READ only. Semantic WRITE is absent, so argparse rejects the verb."""
    from tools.webfoot.cli import main
    for verb in ('set-reference', 'retarget', 'edit-reference'):
        with pytest.raises(SystemExit):
            main(['event', verb, str(ROM)])
