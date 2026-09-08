"""TOOLKIT-024 proofs for the map-owned placement-run traversal contract.

Every number here was measured against the canonical Buu's Fury image, not
carried from a prior ticket's summary. The ROM is opened read-only on every
path. See docs/research/BUU_PLACEMENT_RUN_RELOCATION.md.

The central claim under test is that the engine's OUTER traversal - how many
records a map's run contains - is a counted loop over `MapEntry+0x04` indexing
the pointer array at `MapEntry+0x14`, with no sentinel and no suffix. That is a
statement about the code at 0x08008C9E, so these tests assert the actual
instruction halfwords, not merely a numeric correlation over the corpus.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import struct

import pytest

from tools.webfoot.allocation import AllocationRequest, InsufficientSpaceError, allocate
from tools.webfoot.analysis.thumb import RomReader, find_aligned_words, scan_bl
from tools.webfoot.binary import FileOffset
from tools.webfoot.data.placement_contracts import CONTRACTS
from tools.webfoot.entities import load_placement_types
from tools.webfoot.formats.map_placements import (
    FACTORY_RAW,
    PlacementRecord,
    read_placement_record,
)
from tools.webfoot.layout import AnchorId, FreeRegion, LayoutError, ReferenceClass, RomRange
from tools.webfoot.maps import MAP_FIELDS, MapIdentity, load_maps
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.relocation import RelocationRequest, plan_relocation


LOCAL_ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
CATALOG = "config/roms.yaml"
PROFILE_ID = "buus_fury_usa_rev0_01c1707f"

#: Measured, TOOLKIT-007. MapEntry table at file 0x0008E2E0, stride 0x38.
MAP_TABLE_OFFSET = 0x0008E2E0
MAP_ENTRY_STRIDE = 0x38

#: The selected run. Map 10 is the TOOLKIT-022 canonical example, and is
#: re-verified against this ticket's selection criteria by
#: `test_the_selected_run_satisfies_its_selection_criteria`.
SELECTED_MAP = 10
RUN_ARRAY_ADDRESS = 0x0807293C
RUN_ARRAY_OFFSET = 0x07293C
RUN_ARRAY_BYTES = 8
RUN_BODIES_START = 0x0728FC
RUN_BODIES_END = 0x07293C
RUN_RECORD_COUNT = 2
RUN_RECORD_OFFSETS = (0x0728FC, 0x07291C)
RUN_PLACEMENT_IDS = (0x0000002B, 0x0000001C)
RUN_ENCODED_BYTES = 72  # 64 body + 8 pointer

#: The owner reference: MapEntry 10 base + 0x14.
MAP_ENTRY_OFFSET = MAP_TABLE_OFFSET + SELECTED_MAP * MAP_ENTRY_STRIDE  # 0x08E510
OWNER_SOURCE_OFFSET = MAP_ENTRY_OFFSET + 0x14  # 0x08E524
COUNT_FIELD_OFFSET = MAP_ENTRY_OFFSET + 0x04  # 0x08E514

#: The proven outer traversal loop, TOOLKIT-024. Address -> raw halfword.
#: These are the instructions the contract rests on; if any changes, the ROM is
#: not the image this evidence was measured against.
OUTER_LOOP = {
    0x08008C9E: 0x6860,  # ldr  r0,[r4,#0x04]   current MapEntry pointer
    0x08008CA0: 0x2500,  # mov  r5,#0           index = 0
    0x08008CA2: 0x7900,  # ldrb r0,[r0,#0x04]   MapEntry+0x04 = COUNT
    0x08008CA4: 0x2800,  # cmp  r0,#0
    0x08008CA6: 0xDD17,  # ble  0x08008CD8      count <= 0 consumes nothing
    0x08008CA8: 0x6860,  # ldr  r0,[r4,#0x04]   loop head
    0x08008CAA: 0x00A9,  # lsl  r1,r5,#2        index * 4
    0x08008CAC: 0x6940,  # ldr  r0,[r0,#0x14]   MapEntry+0x14 = array base
    0x08008CAE: 0x5846,  # ldr  r6,[r0,r1]      array[index]
    0x08008CB0: 0x6870,  # ldr  r0,[r6,#0x04]   body+0x04 flags predicate
    0x08008CCE: 0x6860,  # ldr  r0,[r4,#0x04]   loop tail
    0x08008CD0: 0x3501,  # add  r5,#1
    0x08008CD2: 0x7900,  # ldrb r0,[r0,#0x04]   re-read the SAME count byte
    0x08008CD4: 0x42A8,  # cmp  r0,r5
    0x08008CD6: 0xDCE7,  # bgt  0x08008CA8      index < count: continue
}

#: The by-(zone,area) MapEntry lookup; the only literal consumer of the table.
MAP_ENTRY_LOOKUP = 0x080089FC
MAP_TABLE_LITERAL_OFFSET = 0x8A58

#: Census runs whose declared count is short of the engine's `+0x04`, because
#: `iter_placement_offsets` stops at a sibling-family pointer. Measured.
CENSUS_SHORT_RUNS = {17: (1, 4), 96: (3, 4), 151: (14, 16), 258: (3, 4), 450: (1, 2)}

#: Sibling factories found in those extra slots. Both are Thumb entries.
SIBLING_FACTORIES = {0x080111A9: 0xB5F3, 0x08017DA3: 0xB530}


def catalog():
    return RomProfileCatalog.load(CATALOG)


def require_rom():
    if not LOCAL_ROM.is_file():
        pytest.skip("user-supplied Buu's Fury ROM is not present")


@pytest.fixture
def image() -> bytes:
    require_rom()
    return LOCAL_ROM.read_bytes()


@pytest.fixture
def maps():
    require_rom()
    return load_maps(LOCAL_ROM, catalog())


@pytest.fixture
def types():
    require_rom()
    return load_placement_types(LOCAL_ROM, catalog())


def runs_table():
    return CONTRACTS[PROFILE_ID]["runs"]


# --- SC1: the selected run ----------------------------------------------


def test_the_selected_run_satisfies_its_selection_criteria(image):
    """Map 10 is not assumed to be a good example; the criteria are checked."""
    pointer, declared = runs_table()[SELECTED_MAP]
    assert pointer == RUN_ARRAY_ADDRESS and declared == RUN_RECORD_COUNT
    # The engine count agrees with the census count, so this run carries no
    # census ambiguity of its own.
    assert image[COUNT_FIELD_OFFSET] == RUN_RECORD_COUNT
    records = [read_placement_record(image, o) for o in RUN_RECORD_OFFSETS]
    # Every child_count is 1, so no record exercises an unusual size.
    assert [r.child_count for r in records] == [1, 1]
    # Bodies are physically contiguous with no interior hole.
    assert RUN_RECORD_OFFSETS[0] == RUN_BODIES_START
    assert RUN_RECORD_OFFSETS[0] + records[0].consumed_length == RUN_RECORD_OFFSETS[1]
    assert RUN_RECORD_OFFSETS[1] + records[1].consumed_length == RUN_BODIES_END


def test_the_selected_run_identity_is_exact(image, maps):
    placements = maps.map_placements(MapIdentity(SELECTED_MAP))
    assert len(placements) == RUN_RECORD_COUNT
    assert tuple(p.file_offset for p in placements) == RUN_RECORD_OFFSETS
    assert tuple(p.record.id_raw for p in placements) == RUN_PLACEMENT_IDS
    assert tuple(p.record.child_count for p in placements) == (1, 1)
    body_bytes = sum(len(p.original_bytes) for p in placements)
    assert body_bytes == RUN_BODIES_END - RUN_BODIES_START == 64
    assert body_bytes + RUN_ARRAY_BYTES == RUN_ENCODED_BYTES
    # The array begins exactly where the last body ends.
    assert RUN_ARRAY_OFFSET == RUN_BODIES_END


# --- SC2: canonical record sequence via the production codec -------------


def test_the_canonical_record_sequence_reads_through_the_production_codec(image):
    """PC1: the enumeration reproduces the known start, records and end."""
    sequence = []
    cursor = RUN_ARRAY_OFFSET
    for index in range(image[COUNT_FIELD_OFFSET]):
        word = struct.unpack_from("<I", image, cursor + 4 * index)[0]
        offset = word - 0x08000000
        record = read_placement_record(image, offset)
        sequence.append((offset, record.consumed_length, record.child_count))
    assert sequence == [(0x0728FC, 32, 1), (0x07291C, 32, 1)]
    assert sequence[0][0] == RUN_BODIES_START
    assert sequence[-1][0] + sequence[-1][1] == RUN_BODIES_END


def test_body_adjacency_is_layout_not_traversal(image):
    """The arithmetic identity holds, and is explicitly NOT the run's bound.

    The run is an array of pointers; the engine computes `base + index*4` and
    dereferences. Contiguity says how the canonical image was laid out. This
    test pins that distinction so no later reader mistakes it for termination.
    """
    first = read_placement_record(image, RUN_RECORD_OFFSETS[0])
    assert RUN_RECORD_OFFSETS[0] + first.consumed_length == RUN_RECORD_OFFSETS[1]
    # The traversal reaches record 1 through the array slot, not by addition.
    slot1 = struct.unpack_from("<I", image, RUN_ARRAY_OFFSET + 4)[0]
    assert slot1 - 0x08000000 == RUN_RECORD_OFFSETS[1]
    # Adjacency is not universal across the corpus, so it cannot be the rule.
    holed = [
        index
        for index, (pointer, count) in runs_table().items()
        if _has_interior_hole(image, pointer, count)
    ]
    assert holed, "if no run had a hole, adjacency could not be ruled out this way"


def _has_interior_hole(image: bytes, pointer: int, count: int) -> bool:
    offsets = []
    for index in range(count):
        word = struct.unpack_from("<I", image, pointer - 0x08000000 + 4 * index)[0]
        target = word - 0x08000000
        if not 0 <= target < len(image) - 4:
            return False
        if struct.unpack_from("<I", image, target)[0] != FACTORY_RAW:
            return False
        offsets.append(target)
    spans = sorted((o, o + read_placement_record(image, o).consumed_length) for o in offsets)
    return any(a[1] != b[0] for a, b in zip(spans, spans[1:]))


# --- SC4/SC5: the traversal contract -------------------------------------


def test_the_outer_traversal_loop_is_present_verbatim(image):
    """SC4: instruction-level proof, asserted as raw halfwords."""
    reader = RomReader(image)
    for address, halfword in OUTER_LOOP.items():
        assert reader.u16(address) == halfword, f"0x{address:08X} changed"


def test_the_outer_traversal_bound_is_the_map_entry_count_byte(image):
    """The bound is `ldrb rX,[MapEntry,#0x04]`, at BOTH the guard and the tail.

    0x7900 decodes as the byte-load form `ldrb r0,[r0,#0x04]`:
    (h & 0xF000) == 0x7000 is the immediate-offset load/store group, bit 12 set
    selects the byte width, bit 11 set selects load, and the 5-bit immediate at
    bits 6..10 is 1 -> offset 0x04 for a byte access.
    """
    reader = RomReader(image)
    for site in (0x08008CA2, 0x08008CD2):
        halfword = reader.u16(site)
        assert (halfword & 0xF000) == 0x7000, "immediate load/store group"
        assert (halfword >> 12) & 1 == 1, "byte width"
        assert (halfword >> 11) & 1 == 1, "load"
        assert ((halfword >> 6) & 0x1F) == 0x04, "offset +0x04"


def test_the_outer_traversal_indexes_the_map_entry_array_pointer(image):
    """The array base is `ldr rX,[MapEntry,#0x14]`, indexed by index*4."""
    reader = RomReader(image)
    base = reader.u16(0x08008CAC)  # ldr r0,[r0,#0x14]
    assert (base & 0xF000) == 0x6000, "immediate load/store group"
    assert (base >> 12) & 1 == 0, "word width"
    assert (base >> 11) & 1 == 1, "load"
    assert ((base >> 6) & 0x1F) * 4 == 0x14, "offset +0x14"
    scale = reader.u16(0x08008CAA)  # lsl r1,r5,#2
    assert (scale & 0xF800) == 0x0000 and ((scale >> 6) & 0x1F) == 2, "index * 4"
    assert reader.u16(0x08008CAE) == 0x5846, "ldr r6,[r0,r1] register-offset load"


def test_the_outer_traversal_reads_no_sentinel_and_owns_no_suffix(image):
    """No instruction in the loop compares a loaded word to a terminator.

    Corroborated by the corpus: the word immediately after each array end is
    heterogeneous live data, which is what "there is nothing to terminate"
    predicts. A sentinel contract would require it to be uniform.
    """
    reader = RomReader(image)
    # The loop body's only comparisons are against the count and against zero
    # (the flags predicate result). Neither is a word loaded from the array.
    assert reader.u16(0x08008CA4) == 0x2800  # cmp r0,#0   (count vs 0)
    assert reader.u16(0x08008CD4) == 0x42A8  # cmp r0,r5   (count vs index)
    following = {}
    for pointer, count in runs_table().values():
        end = pointer - 0x08000000 + 4 * count
        word = struct.unpack_from("<I", image, end)[0]
        following[word] = following.get(word, 0) + 1
    assert len(following) > 1, "a uniform value would suggest a sentinel"
    assert max(following.values()) < len(runs_table()) // 2


def test_outer_traversal_is_proven_independently_of_child_count(image):
    """SC5: the outer loop never reads body +0x18.

    The per-placement `child_count` at body +0x18 is consumed by 0x0800A93C,
    reached only from the constructor chain behind the factory call. The outer
    loop's only body accesses are +0x00 (factory) and +0x04 (flags). The two
    loops were traced separately; neither is evidence for the other.
    """
    reader = RomReader(image)
    body_accesses = []
    for address in range(0x08008CA8, 0x08008CCE, 2):
        halfword = reader.u16(address)
        if (halfword & 0xF000) in (0x6000, 0x7000) and ((halfword >> 3) & 7) == 6:
            width = 1 if (halfword >> 12) & 1 else 4
            body_accesses.append(((halfword >> 6) & 0x1F) * width)
    assert body_accesses == [0x04, 0x00], "outer loop touches only flags and factory"
    assert 0x18 not in body_accesses


def test_the_map_entry_table_has_exactly_one_literal_consumer(image):
    """The loader is reached through a single lookup, so the loop is the path."""
    literals = find_aligned_words(image, 0x08000000 + MAP_TABLE_OFFSET, 0, len(image))
    assert literals == [MAP_TABLE_LITERAL_OFFSET]
    callers = [b.site_address for b in scan_bl(image, 0, 0x400000) if b.target == MAP_ENTRY_LOOKUP]
    assert len(callers) == 5


# --- the +0x04 correlation and its five exceptions -----------------------


def test_the_engine_count_matches_the_declared_count_for_all_but_five_runs(image):
    mismatched = {
        index: (count, image[MAP_TABLE_OFFSET + index * MAP_ENTRY_STRIDE + 4])
        for index, (_, count) in runs_table().items()
        if image[MAP_TABLE_OFFSET + index * MAP_ENTRY_STRIDE + 4] != count
    }
    assert len(runs_table()) == 240
    assert mismatched == CENSUS_SHORT_RUNS


def test_every_census_shortfall_is_a_sibling_family_pointer(image):
    """The census truncates at a non-0x0800FD55 pointer; the engine does not.

    This is what makes `+0x04` the true count and the declared count the
    artifact - the same prefix-truncation failure TOOLKIT-023 recorded for the
    legacy tail codec, recurring one level up at the pointer array.
    """
    reader = RomReader(image)
    for index, (declared, engine) in CENSUS_SHORT_RUNS.items():
        pointer, _ = runs_table()[index]
        first_extra = struct.unpack_from("<I", image, pointer - 0x08000000 + 4 * declared)[0]
        factory = struct.unpack_from("<I", image, first_extra - 0x08000000)[0]
        assert factory != FACTORY_RAW, f"map {index} would not have truncated"
        assert factory in SIBLING_FACTORIES, f"map {index} extra slot 0x{factory:08X}"
        # The sibling factory is a real Thumb function entry, not stray data.
        assert reader.u16(factory - 1) == SIBLING_FACTORIES[factory]
        assert engine > declared


def test_map_17_proves_the_census_lost_live_placements(image):
    """Decisive case: slots 2 and 3 are ordinary placements the census dropped."""
    pointer, declared = runs_table()[17]
    assert declared == 1 and image[MAP_TABLE_OFFSET + 17 * MAP_ENTRY_STRIDE + 4] == 4
    kinds = []
    for index in range(4):
        word = struct.unpack_from("<I", image, pointer - 0x08000000 + 4 * index)[0]
        kinds.append(struct.unpack_from("<I", image, word - 0x08000000)[0] == FACTORY_RAW)
    assert kinds == [True, False, True, True]


# --- SC3/SC6: owner and reverse references -------------------------------


def test_the_owner_reference_is_confirmed_and_non_relocatable(types):
    """SC3: classification read off the implemented rule, not asserted."""
    document = types.reference_document()
    array = AnchorId(f"map:{SELECTED_MAP:04d}/placement_references")
    anchor = next(a for a in document.anchors if a.identity == array)
    assert anchor.range.start.value == RUN_ARRAY_OFFSET
    assert anchor.range.size == RUN_ARRAY_BYTES == RUN_RECORD_COUNT * 4
    assert anchor.kind == "placement_reference_array"
    assert anchor.relocatable is False
    owner = [r for r in document.references if r.target == array]
    assert len(owner) == 1
    assert owner[0].source.value == OWNER_SOURCE_OFFSET
    assert owner[0].classification is ReferenceClass.CONFIRMED_REFERENCE


def test_the_run_has_exactly_one_external_inbound_reference(image, types):
    """SC6 + PC2: the instrument finds the known owner, so zero means zero."""
    targets = {
        0x08000000 + RUN_ARRAY_OFFSET: "array",
        0x08000000 + RUN_RECORD_OFFSETS[0]: "record0",
        0x08000000 + RUN_RECORD_OFFSETS[1]: "record1",
    }
    found: dict[str, list[int]] = {name: [] for name in targets.values()}
    interior = set(range(RUN_BODIES_START, RUN_ARRAY_OFFSET + RUN_ARRAY_BYTES, 4))
    interior_hits = []
    for offset in range(0, len(image) - 3, 4):
        word = struct.unpack_from("<I", image, offset)[0]
        if word in targets:
            found[targets[word]].append(offset)
        elif 0x08000000 <= word and (word - 0x08000000) in interior:
            interior_hits.append(offset)
    # PC2 positive control: the known owner reference IS found by this scan.
    assert found["array"] == [OWNER_SOURCE_OFFSET]
    assert found["record0"] == [RUN_ARRAY_OFFSET]
    assert found["record1"] == [RUN_ARRAY_OFFSET + 4]
    # Negative result, credible only because the controls above passed.
    assert interior_hits == []


def test_pointers_inside_the_run_all_point_outward(image):
    """Outward pointers survive a move; only the array slots point inward."""
    inward, outward = [], []
    for offset in range(RUN_BODIES_START, RUN_ARRAY_OFFSET + RUN_ARRAY_BYTES, 4):
        word = struct.unpack_from("<I", image, offset)[0]
        if not 0x08000000 <= word < 0x08800000:
            continue
        target = word - 0x08000000
        (inward if RUN_BODIES_START <= target < RUN_ARRAY_OFFSET + RUN_ARRAY_BYTES
         else outward).append(offset)
    assert inward == [RUN_ARRAY_OFFSET, RUN_ARRAY_OFFSET + 4], "only the array slots"
    assert outward, "the bodies do carry outward pointers"
    for offset in outward:
        assert offset < RUN_ARRAY_OFFSET, "outward pointers live in the bodies"


# --- SC7: the +1 hypothetical --------------------------------------------


def test_the_plus_one_hypothetical_is_exact(image):
    records = [read_placement_record(image, o) for o in RUN_RECORD_OFFSETS]
    canonical_bodies = sum(r.consumed_length for r in records)
    clone = records[0].with_position(123, 456)
    new_bodies = canonical_bodies + clone.consumed_length
    assert (canonical_bodies, RUN_RECORD_COUNT * 4) == (64, 8)
    assert (new_bodies, 3 * 4) == (96, 12)
    assert new_bodies + 12 == 108
    assert (new_bodies + 12) - (canonical_bodies + 8) == 36
    # Only the position halfwords differ from the template.
    assert clone.to_bytes()[:0x0C] == records[0].to_bytes()[:0x0C]
    assert clone.to_bytes()[0x10:] == records[0].to_bytes()[0x10:]
    assert (clone.position_low, clone.position_high) == (123, 456)


def test_the_required_owner_metadata_changes_are_closed(image):
    """The rewrite set is closed BECAUSE the contract is proven, not assumed."""
    assert image[COUNT_FIELD_OFFSET] == RUN_RECORD_COUNT  # 1: must become 3
    assert struct.unpack_from("<I", image, OWNER_SOURCE_OFFSET)[0] == RUN_ARRAY_ADDRESS  # 2
    # 6: nothing else. No terminator word is owned, so none must be written.
    assert RUN_ARRAY_OFFSET + RUN_RECORD_COUNT * 4 == RUN_ARRAY_OFFSET + RUN_ARRAY_BYTES


# --- SC8: synthetic relocation, and the exact blocker --------------------


def test_capacity_is_necessary_but_the_published_graph_refuses_relocation(types):
    request = AllocationRequest(
        AnchorId(f"map:{SELECTED_MAP:04d}/placement_references"),
        f"map:{SELECTED_MAP:04d}", 108, 4)
    with pytest.raises(InsufficientSpaceError):
        allocate(types.profile, [request])
    profile = replace(types.profile, free_regions=(
        FreeRegion(RomRange(FileOffset(0x10000), 4096), "synthetic verified capacity"),))
    first = allocate(profile, [request])
    assert first[0].range.start.value == 0x10000
    assert first == allocate(profile, [request]), "deterministic"
    # Capacity does not override the fixed-anchor authority guard.
    document = replace(types.reference_document(), profile=profile)
    with pytest.raises(LayoutError, match="non-relocatable anchor"):
        plan_relocation(document, [RelocationRequest(request.anchor, b"\x00" * 12)])
    assert document.image == types.maps.base_bytes


def test_the_relocator_cannot_express_the_count_rewrite(types):
    """SC8: the blocker, measured rather than argued.

    This probe relaxes exactly one published boolean IN MEMORY to locate the
    NEXT gate. It writes nothing and grants nothing: the published graph keeps
    `relocatable=False`, which the test above pins. What it establishes is that
    even past the flag, `plan_relocation` rewrites the owner pointer correctly
    and still leaves `MapEntry+0x04` untouched, because a count field is
    neither a reference source nor a relocated payload.
    """
    document = types.reference_document()
    array = AnchorId(f"map:{SELECTED_MAP:04d}/placement_references")
    profile = replace(types.profile, free_regions=(
        FreeRegion(RomRange(FileOffset(0x10000), 4096), "synthetic verified capacity"),))
    probe = replace(
        document, profile=profile,
        anchors=tuple(replace(a, relocatable=True) if a.identity == array else a
                      for a in document.anchors))
    result = plan_relocation(probe, [RelocationRequest(array, b"\x00" * 12)])
    output = result.document.image
    # The owner pointer rewrite DOES work.
    assert struct.unpack_from("<I", output, OWNER_SOURCE_OFFSET)[0] == 0x08010000
    # Canonical slots follow their records.
    assert struct.unpack_from("<I", output, 0x10000)[0] == 0x08000000 + RUN_RECORD_OFFSETS[0]
    assert struct.unpack_from("<I", output, 0x10004)[0] == 0x08000000 + RUN_RECORD_OFFSETS[1]
    # The third slot is empty: no clone anchor exists, and the relocator's
    # contract does not create anchors or append new reference sources.
    assert struct.unpack_from("<I", output, 0x10008)[0] == 0
    # THE BLOCKER: the count is unchanged, so the engine would still read 2.
    assert output[COUNT_FIELD_OFFSET] == RUN_RECORD_COUNT
    # No emitted change targets the count byte, by construction.
    assert all(c.offset != COUNT_FIELD_OFFSET for c in result.plan.effective_changes)


def test_count_fields_are_refused_as_editable_independently():
    """The second, independent refusal of a count write."""
    assert set(MAP_FIELDS) == {"zone", "area", "variation", "flags", "music_id"}
    assert not any(name.endswith("count") for name in MAP_FIELDS)


# --- SC12: regressions this ticket must not break ------------------------


def test_the_census_totals_are_preserved(maps):
    """TOOLKIT-023's numbers are unchanged; this ticket corrected no census."""
    placements = tuple(maps.placements())
    assert len(placements) == 1442
    assert len({p.file_offset for p in placements}) == 1442
    assert sum(len(p.original_bytes) for p in placements) == 46244
    assert len(runs_table()) == 240
    counts = [p.record.child_count for p in placements]
    assert [counts.count(n) for n in (1, 2, 3, 4)] == [1427, 7, 6, 2]


def test_the_selected_run_round_trips_byte_identically(image, maps):
    for placement in maps.map_placements(MapIdentity(SELECTED_MAP)):
        record = PlacementRecord.from_bytes(placement.original_bytes)
        assert record.to_bytes() == placement.original_bytes
        assert placement.original_bytes == image[
            placement.file_offset:placement.file_offset + len(placement.original_bytes)]


def test_the_canonical_image_is_never_modified(image):
    import hashlib
    assert len(image) == 8388608
    assert hashlib.sha256(image).hexdigest() == (
        "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e")
