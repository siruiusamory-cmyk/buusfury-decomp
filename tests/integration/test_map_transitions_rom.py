"""ROM-gated proofs for the transition family. MAP-WARP-FORMAT-001.

The canonical Buu's Fury image is opened read-only on every path. Nothing here
writes to it, and the one mutated image is produced in memory by
`webfoot.write.apply_plan`, never emitted.

Every canonical count asserted below was measured from that image by
``tools/research/logx_connector_probe.py`` and recorded in
``docs/research/LOGX_CONNECTOR_PROVENANCE.md``; this file pins the SDK authority
to the same numbers rather than restating the research.

The suite skips cleanly when the private canonical ROM is not configured.
`LOGX_CANONICAL_ROM` overrides the default `roms/` path, so a review worktree -
which never carries the ignored image - can point at the main checkout's copy and
run the whole file read-only.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot.formats.map_transitions import (
    SUPPORTED_CLASS_RAW,
    TRANSITION_CLASS_A_RAW,
    TRANSITION_CLASS_B_RAW,
    TRANSITION_SIZE,
    MapTransitionRegionError,
    TransitionRegion,
)
from tools.webfoot.map_transitions import (
    MapIdentity,
    MapTransitionsError,
    TransitionFieldError,
    TransitionIdentity,
    load_map_transitions,
)
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.write import OutputPathError, apply_plan, emit_image

LOCAL_ROM = Path(
    os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
)
CATALOG = "config/roms.yaml"

#: Measured from the canonical image, LOGX-CONNECTOR-001.
MAP_RECORD_COUNT = 452
TRANSITION_COUNT = 735
MAPS_WITH_TRANSITIONS = 348
MAX_TRANSITIONS_PER_MAP = 14
DESTINATION_RESOLVED = 735
CLASS_A_COUNT = 566
CLASS_B_COUNT = 169
SELF_LINK_MAPS = (125, 126, 127)
#: Self-link *records*: the census counts three distinct (source, destination)
#: pairs, and map 125 alone carries three of these records.
SELF_LINK_RECORDS = 9

#: A known reciprocal pair and a known one-way link, both cited in the
#: provenance document's representative-record table.
MAP_38 = MapIdentity(38)
MAP_39 = MapIdentity(39)
MAP_40 = MapIdentity(40)
MAP_33 = MapIdentity(33)
MAP_34 = MapIdentity(34)

#: Map 39's second record: destination key `010C`, a deliberately non-square and
#: asymmetric region (9 wide by 105 tall, all four endpoints distinct).
MAP_39_SECOND = TransitionIdentity(MAP_39, 1)
MAP_39_SECOND_KEY = bytes((0x01, 0x0C))
MAP_39_SECOND_REGION = TransitionRegion(first=(592, 601), second=(136, 241))


def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load(CATALOG)


def require_rom() -> None:
    if not LOCAL_ROM.is_file():
        pytest.skip("user-supplied Buu's Fury ROM is not present")


@pytest.fixture(scope="module")
def transitions():
    require_rom()
    return load_map_transitions(LOCAL_ROM, catalog())


def edit_once(mutate):
    """A freshly loaded corpus with one staged edit, plus its applied image."""
    require_rom()
    corpus = load_map_transitions(LOCAL_ROM, catalog())
    mutate(corpus)
    plan = corpus.plan()
    return corpus, plan, apply_plan(corpus.base_bytes, plan)


# --- canonical enumeration ---------------------------------------------------


def test_the_canonical_transition_corpus_is_enumerated_canonically(transitions):
    assert transitions.map_count == MAP_RECORD_COUNT
    assert transitions.record_count == TRANSITION_COUNT

    per_map = {
        MapIdentity(index): len(transitions.for_map(MapIdentity(index)))
        for index in range(transitions.map_count)
    }
    assert sum(per_map.values()) == TRANSITION_COUNT
    assert sum(1 for count in per_map.values() if count) == MAPS_WITH_TRANSITIONS
    assert max(per_map.values()) == MAX_TRANSITIONS_PER_MAP

    keys = [entry.identity.key for entry in transitions.entries()]
    assert len(set(keys)) == TRANSITION_COUNT, "identities must be unique"
    assert keys == sorted(keys), "enumeration order is (source map, index)"
    # `for_map` is the per-map enumeration, in array index order.
    assert [entry.identity.index for entry in transitions.for_map(MAP_39)] == [0, 1]


def test_enumeration_is_deterministic_across_loads():
    require_rom()
    first = load_map_transitions(LOCAL_ROM, catalog())
    second = load_map_transitions(LOCAL_ROM, catalog())
    assert [e.identity.key for e in first.entries()] == [
        e.identity.key for e in second.entries()
    ]
    assert first.plan().changes == second.plan().changes


def test_the_identity_carries_no_address(transitions):
    """Addressability is semantic: no record or file offset reaches a caller."""
    for entry in list(transitions.entries())[:8]:
        assert not hasattr(entry.identity, "address")
        assert not hasattr(entry.identity, "file_offset")
        assert entry.identity.source.index >= 0
        assert entry.identity.index >= 0


# --- exact round trip --------------------------------------------------------


def test_every_canonical_record_round_trips_byte_identically(transitions):
    checked = 0
    for entry in transitions.entries():
        assert len(entry.original_bytes) == TRANSITION_SIZE
        assert entry.record.to_bytes() == entry.original_bytes, entry.identity
        checked += 1
    assert checked == TRANSITION_COUNT
    assert len(transitions.validate()) == TRANSITION_COUNT


def test_the_two_measured_class_words_cover_the_corpus(transitions):
    census: dict[int, int] = {}
    for entry in transitions.entries():
        assert entry.record.class_raw in SUPPORTED_CLASS_RAW, entry.identity
        census[entry.record.class_raw] = census.get(entry.record.class_raw, 0) + 1
    assert census == {TRANSITION_CLASS_A_RAW: CLASS_A_COUNT,
                      TRANSITION_CLASS_B_RAW: CLASS_B_COUNT}


def test_the_unresolved_fields_are_carried_not_defaulted(transitions):
    """A record's unknown bytes survive the round trip, so nothing invents them."""
    sample = transitions.entry(MAP_39_SECOND)
    raw = sample.original_bytes
    assert sample.record.byte_0x10_raw == raw[0x10]
    assert sample.record.byte_0x13_raw == raw[0x13]
    assert sample.record.word_0x14_raw == int.from_bytes(raw[0x14:0x16], "little")
    assert sample.record.byte_0x16_raw == raw[0x16]
    assert sample.record.byte_0x17_raw == raw[0x17]
    assert sample.record.constant_raw == int.from_bytes(raw[0x04:0x08], "little")


# --- known decode ------------------------------------------------------------


def test_the_known_source_and_destination_decode(transitions):
    assert transitions.destination(TransitionIdentity(MAP_38, 0)) == MAP_39
    assert [transitions.destination(e.identity) for e in transitions.for_map(MAP_39)] == [
        MAP_38,
        MAP_40,
    ]
    assert transitions.destination(TransitionIdentity(MAP_33, 0)) == MAP_34

    second = transitions.entry(MAP_39_SECOND)
    assert second.record.destination_key == MAP_39_SECOND_KEY
    assert transitions.key_for(MAP_40) == MAP_39_SECOND_KEY
    assert second.original_bytes[0x11:0x13] == MAP_39_SECOND_KEY


def test_every_canonical_destination_resolves_and_the_graph_is_stable(transitions):
    resolved = 0
    self_links = 0
    self_link_sources = set()
    for entry in transitions.entries():
        resolved += 1
        if transitions.destination(entry.identity) == entry.identity.source:
            self_links += 1
            self_link_sources.add(entry.identity.source.index)
    assert resolved == DESTINATION_RESOLVED
    # The census counts three self-links as three (source, destination) pairs;
    # one map happens to carry several such records, so the *sources* are the
    # three maps and the *records* are nine.
    assert sorted(self_link_sources) == sorted(SELF_LINK_MAPS)
    assert self_links == SELF_LINK_RECORDS


# --- coordinates -------------------------------------------------------------


def test_the_region_is_asymmetric_so_a_transposition_is_load_bearing(transitions):
    """All four endpoints differ: a swap of either interval, or of either
    interval's ends, changes the bytes and the decoded values."""
    entry = transitions.entry(MAP_39_SECOND)
    record = entry.record
    assert record.region == MAP_39_SECOND_REGION
    a, b = MAP_39_SECOND_REGION.first
    c, d = MAP_39_SECOND_REGION.second
    assert len({a, b, c, d}) == 4
    assert (b - a) != (d - c), "a square region could not tell the axes apart"
    transposed = TransitionRegion(first=(c, d), second=(a, b))
    assert transposed != record.region
    assert entry.original_bytes[0x08:0x10] == bytes((0x50, 0x02, 0x88, 0x00,
                                                     0x59, 0x02, 0xF1, 0x00))
    assert transposed.to_bytes() != entry.original_bytes[0x08:0x10]


# --- controlled serialization ------------------------------------------------


def test_a_controlled_destination_edit_serializes_correctly(transitions):
    current = transitions.destination(MAP_39_SECOND)
    current_key = transitions.key_for(current)
    # A destination whose key differs in *both* bytes, so a plan that wrote only
    # one of the two key fields could not pass.
    target = next(
        MapIdentity(index)
        for index in range(transitions.map_count)
        if all(
            written != original
            for written, original in zip(
                transitions.key_for(MapIdentity(index)), current_key
            )
        )
    )
    assert target != MAP_40

    corpus, plan, edited = edit_once(
        lambda c: c.set_destination(MAP_39_SECOND, target),
    )
    offset = corpus.entry(MAP_39_SECOND).file_offset
    assert [i for i in range(len(edited)) if edited[i] != corpus.base_bytes[i]] == [
        offset + 0x11,
        offset + 0x12,
    ]
    assert corpus.destination(MAP_39_SECOND) == target
    assert transitions.destination(MAP_39_SECOND) == MAP_40, "the source is untouched"

    effective = [change for change in plan.changes if change.is_effective]
    assert [change.owner for change in effective] == [str(MAP_39_SECOND)]
    assert effective[0].offset == offset
    assert effective[0].new[0x11:0x13] == transitions.key_for(target)


def test_a_controlled_region_edit_serializes_correctly(transitions):
    region = TransitionRegion(first=(0x0102, 0x0304), second=(0x0506, 0x0708))
    corpus, plan, edited = edit_once(
        lambda c: c.set_region(MAP_39_SECOND, region)
    )
    offset = corpus.entry(MAP_39_SECOND).file_offset
    assert [i for i in range(len(edited)) if edited[i] != corpus.base_bytes[i]] == list(
        range(offset + 0x08, offset + 0x10)
    )
    assert corpus.entry(MAP_39_SECOND).record.region == region
    assert corpus.entry(MAP_39_SECOND).record.to_bytes()[0x08:0x10] == region.to_bytes()
    effective = [change for change in plan.changes if change.is_effective]
    assert [change.owner for change in effective] == [str(MAP_39_SECOND)]


def test_an_edit_leaves_every_unrelated_record_untouched(transitions):
    corpus, _, edited = edit_once(
        lambda c: c.set_destination(MAP_39_SECOND, MAP_33)
    )
    for entry in corpus.entries():
        if entry.identity == MAP_39_SECOND:
            continue
        span = slice(entry.file_offset, entry.file_offset + TRANSITION_SIZE)
        assert edited[span] == entry.original_bytes, entry.identity
    # And the whole image, outside that one record, is byte-identical.
    offset = corpus.entry(MAP_39_SECOND).file_offset
    assert edited[:offset] == corpus.base_bytes[:offset]
    assert edited[offset + TRANSITION_SIZE :] == corpus.base_bytes[offset + TRANSITION_SIZE :]


# --- fail closed -------------------------------------------------------------


def test_an_invalid_map_coordinate_or_type_is_refused(transitions):
    with pytest.raises(TransitionFieldError):
        transitions.set_destination(MAP_39_SECOND, MapIdentity(MAP_RECORD_COUNT))
    with pytest.raises(TransitionFieldError):
        transitions.set_destination(MAP_39_SECOND, 40)  # type: ignore[arg-type]
    with pytest.raises(MapTransitionRegionError):
        TransitionRegion(first=(20, 10), second=(0, 5))
    with pytest.raises(MapTransitionRegionError):
        TransitionRegion(first=(7, 7), second=(0, 5))
    with pytest.raises(TransitionFieldError):
        transitions.set_region(MAP_39_SECOND, ((0, 5), (0, 5)))  # type: ignore[arg-type]
    with pytest.raises(MapTransitionsError):
        transitions.entry(TransitionIdentity(MAP_39, 2))
    # The staged failures left nothing behind: the corpus still plans to a no-op.
    assert not any(change.is_effective for change in transitions.plan().changes)


def test_a_key_that_names_no_map_is_refused(transitions):
    with pytest.raises(MapTransitionsError):
        transitions.map_for_key(b"\xff\xff")
    with pytest.raises(TransitionFieldError):
        transitions.key_for(MapIdentity(MAP_RECORD_COUNT))


# --- input safety ------------------------------------------------------------


def test_the_canonical_rom_is_unchanged_and_refused_as_a_write_target():
    require_rom()
    before = hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest()

    corpus = load_map_transitions(LOCAL_ROM, catalog())
    corpus.set_destination(MAP_39_SECOND, MAP_33)
    plan = corpus.plan()
    applied = apply_plan(corpus.base_bytes, plan)

    after = hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest()
    assert after == before
    assert after == "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
    assert applied != corpus.base_bytes

    # The canonical input is refused as a destination, by the shared write
    # policy, before any byte is read.
    with pytest.raises(OutputPathError):
        emit_image(LOCAL_ROM, LOCAL_ROM, plan)
