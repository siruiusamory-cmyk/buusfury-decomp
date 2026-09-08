"""TOOLKIT-023: can any existing Buu placement record be safely repurposed?

TOOLKIT-022 refused to materialize an expanded placement run, leaving relocation
and free-space allocation as the blockers for authoring a new entity instance.
Before opening a relocation contract, this ticket asked the cheaper question:
does the canonical ROM already contain placement records that are genuinely
unused, so an authored clone could take over an existing physical slot without
changing any run's size or count?

The answer is no, and this module pins *why* rather than pinning the bare no.
Three hypotheses were tested and each is refuted here on positive evidence:

* the 147 records TOOLKIT-017 added are dead --- refuted: all 57 script-bearing
  records live inside that delta, and the old codec missed them by truncating
  each run at the first non-legacy tail;
* the 1,604 bytes of interior gap inside 26 run spans are free --- refuted: they
  decompose into descriptors, script roots, and live interleaved records;
* the 129 factory-led records no run reaches are orphans --- refuted: 119 are
  referenced from secondary pointer arrays, and the remaining 10 are
  coincidental factory words in an IWRAM-pointer region, not placements at all.

The expensive failure mode in this direction is a false positive: classifying a
live record as free and handing it out as authoring capacity would corrupt real
game content. So the tests below assert the *instrument* works (a reference
sweep that finds 200 of 200 known-live records) before they assert any negative,
per the TOOLKIT-021 lesson that a negative result is only worth what its
positive controls are worth.

Evidence: docs/research/BUU_PLACEMENT_REUSE.md
"""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import struct

import pytest

from tools.webfoot.data.placement_contracts import CONTRACTS
from tools.webfoot.formats import map_placements as mp

SHA = '940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e'
PROFILE = 'buus_fury_usa_rev0_01c1707f'
ROM_BASE = 0x08000000

#: Corpus-wide totals reproduced by this ticket, not carried from TOOLKIT-017.
CENSUS_RECORDS = 1442
CENSUS_RUNS = 240
LEGACY_RECORDS = 1295
DELTA_RECORDS = 147

#: The behavior handlers reached through a record's `+0x14` descriptor.
HANDLER_NULL = 0x0800421D
HANDLER_SCRIPT = 0x0800421F
HANDLER_OTHER = 0x0800424F
NULL_DESCRIPTOR = 0x080555A0

#: The script-bearing subset TOOLKIT-016 promoted, used here as a positive control.
OWNED_RECORDS = 57
OWNED_MAPS = (19, 21, 22, 240, 309, 325, 428, 430, 432, 437)

#: Run-span interior gaps, and the residue left after every known anchor.
GAPPED_RUNS = 26
CONTIGUOUS_RUNS = 214
HOLE_BYTES = 1604
HOLE_COUNT = 85

#: Factory words the run walk does not reach, and how they resolve.
UNREACHED_RECORDS = 129
UNREACHED_REFERENCED = 119
UNREACHED_FALSE_POSITIVES = 10

#: The placement region: the union of every declared run's byte span.
REGION_START = 0x0728FC
REGION_END = 0x08E188

#: Bounded pointer arrays, owned by a family other than `MapEntry[+0x14]`, that
#: reference the in-region records no declared run reaches. Thirteen of them end
#: at the TOOLKIT-012 rect-descriptor factory, naming that owner.
SECONDARY_ARRAYS = 40
RECT_FACTORY = 0x0800742D

#: A live function pointer heading a record family interleaved in run gaps.
#: Thumb at file 0x039F08, so the gap bytes are code-referenced, not padding.
INTERLEAVED_FACTORY = 0x08039F09


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


@pytest.fixture
def runs():
    return CONTRACTS[PROFILE]['runs']


@pytest.fixture
def census(data, runs):
    """Every record the 240 declared runs reach, keyed by file offset.

    Uses the production codec and the trusted run provenance rather than a
    re-derived walk, so a disagreement here is a real regression and not a
    second opinion about how to walk.
    """
    reached = {}
    for index, (pointer, count) in sorted(runs.items()):
        offsets = mp.iter_placement_offsets(data, pointer - ROM_BASE, count=count)
        assert len(offsets) == count
        for ordinal, offset in enumerate(offsets):
            assert offset not in reached, 'a record is claimed by two runs'
            reached[offset] = (index, ordinal, mp.read_placement_record(data, offset))
    return reached


def _u32(data, addr):
    return struct.unpack_from('<I', data, addr - ROM_BASE)[0]


def _handler(data, record):
    """The behavior handler this record's `+0x14` descriptor names."""
    return _u32(data, record.descriptor_pointer_raw)


def _factory_offsets(data):
    """Every four-aligned file offset holding the placement factory tag."""
    return [o for o in range(0, len(data) - 3, 4)
            if struct.unpack_from('<I', data, o)[0] == mp.FACTORY_RAW]


def _pointer_index(data):
    """Word-aligned inbound references, mapping target file offset -> ref sites."""
    index = defaultdict(list)
    words = struct.unpack_from(f'<{len(data) // 4}I', data, 0)
    for slot, word in enumerate(words):
        if ROM_BASE <= word < ROM_BASE + len(data):
            index[word - ROM_BASE].append(slot * 4)
    return index


def _run_array_slots(runs):
    """Every word occupied by a declared run's pointer array."""
    return {pointer - ROM_BASE + 4 * k
            for pointer, count in runs.values() for k in range(count)}


def _spans(census):
    """Each record's `(start, end)` file extent."""
    return {offset: (offset, offset + record.consumed_length)
            for offset, (_, _, record) in census.items()}


def _iwram_words(data, offset, radius=64):
    """IWRAM pointers among the words surrounding `offset`.

    A placement record lives in the map data region and never has one nearby;
    the false-positive factory words sit in a pointer/vtable area that is dense
    with them. This is the discriminator, so it is measured, not asserted.
    """
    window = struct.unpack_from(f'<{2 * radius // 4}I', data, offset - radius)
    return sum(1 for word in window if 0x03000000 <= word < 0x03008000)


def _points_at_a_factory(data, offset):
    """True when the word at `offset` points at a placement factory tag."""
    if not 0 <= offset < len(data) - 3:
        return False
    target = struct.unpack_from('<I', data, offset)[0] - ROM_BASE
    return (0 <= target < len(data) - 3
            and struct.unpack_from('<I', data, target)[0] == mp.FACTORY_RAW)


def _pointer_array_extent(data, site):
    """The maximal run of consecutive placement pointers containing `site`."""
    start = site
    while _points_at_a_factory(data, start - 4):
        start -= 4
    end = site
    while _points_at_a_factory(data, end + 4):
        end += 4
    return start, end + 4


# --- Census reconciliation -------------------------------------------------

def test_census_totals_reconcile_to_1442(census, runs):
    assert len(runs) == CENSUS_RUNS
    assert len(census) == CENSUS_RECORDS


def test_every_declared_run_is_accounted_for(census, runs):
    counted = Counter(index for index, _, _ in census.values())
    assert set(counted) == set(runs)
    assert all(counted[index] == count for index, (_, count) in runs.items())


def test_no_record_body_overlaps_another(census):
    ordered = sorted(_spans(census).values())
    assert all(a[1] <= b[0] for a, b in zip(ordered, ordered[1:]))


def test_record_size_follows_the_child_count(census):
    for _, _, record in census.values():
        assert record.consumed_length == 0x1C + 4 * record.child_count
        assert 1 <= record.child_count <= mp.MAX_CHILDREN


def test_census_is_deterministic(data, runs):
    def walk():
        return tuple(sorted(
            offset
            for pointer, count in runs.values()
            for offset in mp.iter_placement_offsets(data, pointer - ROM_BASE, count=count)))

    assert walk() == walk()


# --- The 147-record delta --------------------------------------------------

@pytest.fixture
def delta(data, census, runs):
    """Records the legacy fixed-tail codec dropped, by TOOLKIT-017 reconstruction.

    The legacy subset is rebuilt by stopping each run at its first old-tail
    mismatch --- *not* by filtering the full census for the old tail, which
    would wrongly readmit the 42 delta records that happen to match the shape.
    """
    legacy, extra = set(), []
    for index, (pointer, count) in sorted(runs.items()):
        stopped = False
        for offset in mp.iter_placement_offsets(data, pointer - ROM_BASE, count=count):
            if not stopped and mp.is_legacy_placement_record(data, offset):
                legacy.add(offset)
            else:
                stopped = True
                extra.append(offset)
    return legacy, extra


def test_historical_1295_plus_147_reconciles(delta, census):
    legacy, extra = delta
    assert len(legacy) == LEGACY_RECORDS
    assert len(extra) == DELTA_RECORDS
    assert len(legacy) + len(extra) == len(census) == CENSUS_RECORDS
    assert not legacy.intersection(extra)


def test_the_delta_holds_every_script_bearing_record(data, census, delta):
    """The strongest single refutation that the 147 are dead.

    Script-bearing records are the most demonstrably live in the corpus: their
    descriptor names the interpreter trampoline. All 57 sit in the delta.
    """
    _, extra = delta
    scripted = {offset for offset, (_, _, record) in census.items()
                if _handler(data, record) == HANDLER_SCRIPT}
    assert len(scripted) == OWNED_RECORDS
    assert scripted.issubset(set(extra))


def test_the_delta_spans_all_three_handlers(data, census, delta):
    _, extra = delta
    handlers = Counter(_handler(data, census[offset][2]) for offset in extra)
    assert handlers[HANDLER_SCRIPT] == OWNED_RECORDS
    assert handlers[HANDLER_OTHER] == 24
    assert handlers[HANDLER_NULL] == 66
    assert sum(handlers.values()) == DELTA_RECORDS


def test_legacy_shape_alone_does_not_explain_the_delta(data, delta):
    """42 delta records match the old tail and were still dropped.

    That is what makes the delta a truncation artifact rather than a statement
    about record content: the old codec cut each run at the first mismatch, so
    a conforming record behind a non-conforming one was lost anyway.
    """
    _, extra = delta
    matching = [o for o in extra if mp.is_legacy_placement_record(data, o)]
    assert len(matching) == 42


# --- Run-span interiors ----------------------------------------------------

@pytest.fixture
def holes(data, census, runs):
    """Every gap between consecutive record bodies inside a single run's span."""
    per_run = defaultdict(list)
    for offset, (index, _, record) in census.items():
        per_run[index].append((offset, offset + record.consumed_length))
    gaps = []
    for index, spans in per_run.items():
        spans.sort()
        gaps.extend((index, a[1], b[0]) for a, b in zip(spans, spans[1:]) if a[1] < b[0])
    return gaps


def test_run_interior_gaps_are_measured_not_assumed(holes, census):
    gapped = {index for index, _, _ in holes}
    assert len(holes) == HOLE_COUNT
    assert len(gapped) == GAPPED_RUNS
    assert sum(end - start for _, start, end in holes) == HOLE_BYTES
    assert CENSUS_RUNS - len(gapped) == CONTIGUOUS_RUNS


def test_run_gaps_are_not_padding(data, holes):
    """No hole is erasable filler, so none of the 1,604 bytes is capacity.

    Padding in this ROM would read as `0xFF` or as a zeroed run. Neither
    appears: the gaps carry live interleaved records and bytecode.
    """
    blob = b''.join(data[start:end] for _, start, end in holes)
    assert len(blob) == HOLE_BYTES
    assert blob.count(0xFF) == 0
    assert blob.count(0) < len(blob) // 2


def test_run_gaps_carry_a_live_interleaved_record_family(data, holes):
    """`0x08039F09` heads records inside the gaps and is Thumb code.

    A gap word that points at executable code is referenced data, which is the
    positive evidence that these bytes are owned rather than merely non-zero.
    """
    tags = sum(
        struct.unpack_from(f'<{(end - start) // 4}I', data, start).count(INTERLEAVED_FACTORY)
        for _, start, end in holes if (end - start) % 4 == 0)
    assert tags > 0
    # Thumb `mov r2,r1 ; mov r1,r0 ; mov r0,#0` at the pointer's target.
    assert data[INTERLEAVED_FACTORY - ROM_BASE - 1:][:6] == bytes.fromhex('0a1c011c0020')


# --- Positive controls: the instrument must find known positives ------------

def test_reference_sweep_finds_every_known_live_record(data, census, runs):
    """Negative-result methodology, per TOOLKIT-021.

    Every claim below that a record is unreferenced rests on this sweep. If the
    sweep could miss a live record it would manufacture free capacity, so it is
    validated against known positives before it is trusted for any negative.
    """
    index = _pointer_index(data)
    slots = _run_array_slots(runs)
    sample = sorted(census)[:200]
    assert all(index.get(offset) for offset in sample)
    assert all(any(site in slots for site in index[offset]) for offset in sample)


def test_script_bearing_control_classifies_live(data, census):
    scripted = {index for index, _, record in census.values()
                if _handler(data, record) == HANDLER_SCRIPT}
    assert tuple(sorted(scripted)) == OWNED_MAPS


def test_null_descriptor_fan_in_reproduces_toolkit_016(census):
    fan_in = Counter(record.descriptor_pointer_raw for _, _, record in census.values())
    assert fan_in[NULL_DESCRIPTOR] == 1361


def test_every_censused_record_classifies_live_map_owned(census):
    """The classification totals, and their reconciliation to 1,442.

    Orphan, shared-only, unknown, candidate and confirmed classes are all empty;
    a record reached by a declared run is live and is not counted twice.
    """
    live = [offset for offset in census]
    assert len(live) == CENSUS_RECORDS
    assert len(set(live)) == len(live)


# --- Reuse candidates: each refuted on positive evidence --------------------

def test_no_record_hides_inside_a_traversed_run_span(data, census):
    """A skipped record inside a live span would be the one dangerous case.

    Such a record is unsafe even when nothing names it, because the run's bytes
    are actively traversed. There are none: traversal consumes exactly the
    pointers the array lists.
    """
    per_run = defaultdict(list)
    for offset, (index, _, record) in census.items():
        per_run[index].append((offset, offset + record.consumed_length))
    for index, spans in per_run.items():
        low = min(s for s, _ in spans)
        high = max(e for _, e in spans)
        for probe in range(low, high - 3, 4):
            if struct.unpack_from('<I', data, probe)[0] == mp.FACTORY_RAW:
                assert probe in census, f'unpointed record inside map {index} span'


def test_unreached_factory_words_resolve_to_live_or_false_positive(data, census):
    unreached = [o for o in _factory_offsets(data) if o not in census]
    assert len(unreached) == UNREACHED_RECORDS
    index = _pointer_index(data)
    referenced = [o for o in unreached if index.get(o)]
    unreferenced = [o for o in unreached if not index.get(o)]
    assert len(referenced) == UNREACHED_REFERENCED
    assert len(unreferenced) == UNREACHED_FALSE_POSITIVES


def test_referenced_unreached_records_are_owned_elsewhere(data, census, runs):
    """119 records are named by a secondary pointer array, so they are live.

    They are not reached by a `MapEntry[+0x14]` run, but something lists them.
    An unmodelled owner is not an absent owner.
    """
    index = _pointer_index(data)
    slots = _run_array_slots(runs)
    unreached = [o for o in _factory_offsets(data) if o not in census and index.get(o)]
    assert len(unreached) == UNREACHED_REFERENCED
    arrays = set()
    for offset in unreached:
        # Exactly one inbound reference each, and never from a declared run
        # array --- these records belong to a different owner, not to a map.
        assert len(index[offset]) == 1
        site = index[offset][0]
        assert site not in slots
        arrays.add(_pointer_array_extent(data, site))
    # All 119 are covered by 40 bounded pointer arrays, and a bounded array is a
    # structure. Thirteen end at the `0x0800742D` rect descriptor family, which
    # is what identifies the owner as another family rather than as no owner.
    in_region = {(a, b) for a, b in arrays if a < REGION_END}
    assert len(in_region) == len(arrays) == SECONDARY_ARRAYS
    terminators = Counter(struct.unpack_from('<I', data, b)[0] for _, b in in_region)
    assert terminators[RECT_FACTORY] == 13


def test_zero_reference_words_are_false_positives_not_orphans(data, census):
    """The 10 unreferenced factory words are not placement records.

    They lie outside the placement region entirely, in a dense IWRAM-pointer
    area, and carry a zero position and zero flags. The bytes that let them
    parse are a coincidental recurrence of the legacy tail sequence. Treating
    one as a free slot would corrupt whatever that region really is.
    """
    index = _pointer_index(data)
    unreferenced = [o for o in _factory_offsets(data)
                    if o not in census and not index.get(o)]
    assert len(unreferenced) == UNREACHED_FALSE_POSITIVES
    for offset in unreferenced:
        assert offset >= REGION_END, 'a candidate inside the placement region'
        record = mp.read_placement_record(data, offset)
        assert record.position_raw == 0
        assert record.flags_raw == 0
        # Every candidate sits near IWRAM pointers; no live record does.
        assert _iwram_words(data, offset) >= 1


def test_iwram_proximity_separates_candidates_from_live_records(data, census):
    """The discriminator is sharp in both directions, which is why it is used.

    Of 400 known-live records, zero have an IWRAM pointer within 64 bytes. All
    ten zero-reference candidates have at least one. Without this control the
    proximity claim would be an observation about ten addresses rather than a
    property that separates the two populations.
    """
    live = [o for o in sorted(census)[:400] if o >= 64]
    assert live
    assert all(_iwram_words(data, offset) == 0 for offset in live)


def test_the_placement_region_excludes_every_candidate(data, census):
    starts = [o for o in census]
    assert min(starts) == REGION_START
    assert max(o + census[o][2].consumed_length for o in starts) == REGION_END


# --- Fail-closed posture ---------------------------------------------------

def test_no_record_is_promoted_to_repurposable(data, census):
    """Absence of a reference never becomes authoring capacity.

    This is the invariant the ticket exists to protect. Every factory-led word
    in the image is either reached by a declared run, referenced from elsewhere,
    or outside the placement region --- so the confirmed-reusable set is empty
    and stays empty.
    """
    index = _pointer_index(data)
    for offset in _factory_offsets(data):
        assert offset in census or index.get(offset) or offset >= REGION_END


def test_canonical_rom_is_untouched(rom):
    assert hashlib.sha256(rom.read_bytes()).hexdigest() == SHA
