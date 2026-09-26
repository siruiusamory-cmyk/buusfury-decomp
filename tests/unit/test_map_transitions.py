"""Portable tests for the selector-1-root transition record. MAP-WARP-FORMAT-001.

Two layers are covered without any ROM:

* ``formats.map_transitions`` - the pure 24-byte codec, its positional region
  fields and its fail-closed refusals;
* ``map_transitions`` - the SDK authority, exercised over a synthetic image
  assembled here from the measured format (a 0x38-stride map table whose
  `+0x2C` word leads to a selector-1 root, the root's `+0x40`/`+0x44` pair, and
  4-byte array elements pointing at 24-byte records).

The synthetic image is deliberately *not* a canonical ROM and asserts no
canonical count; the corpus arithmetic lives in
``tests/integration/test_map_transitions_rom.py``.
"""

from __future__ import annotations

from dataclasses import fields
from dataclasses import replace as dataclasses_replace
import hashlib

import pytest

from tools.webfoot.formats.map_transitions import (
    SUPPORTED_CLASS_RAW,
    TRANSITION_CLASS_A_RAW,
    TRANSITION_CLASS_B_RAW,
    TRANSITION_LAYOUT,
    TRANSITION_SIZE,
    MapTransitionFamilyError,
    MapTransitionLengthError,
    MapTransitionRegionError,
    MapTransitionValueError,
    TransitionRecord,
    TransitionRegion,
)
from tools.webfoot.map_transitions import (
    ARRAY_ELEMENT_WIDTH,
    MAP_ENTRY_SOURCE_OFFSET,
    ROOT_ARRAY_OFFSET,
    ROOT_COUNT_OFFSET,
    MapIdentity,
    MapTransitions,
    MapTransitionsError,
    TransitionFieldError,
    TransitionIdentity,
    UnknownTransitionError,
    _read_corpus,
)
from tools.webfoot.write import apply_plan

# --- a synthetic image laid out from the measured format ---------------------

GBA_BASE = 0x08000000
IMAGE_SIZE = 0x8000
TABLE_OFFSET = 0x0100
TABLE_STRIDE = 0x38
SOURCE_BASE = 0x1000
ROOT_BASE = 0x2000
ROOT_STRIDE = 0x48
ARRAY_BASE = 0x3000
ARRAY_STRIDE = 0x20
RECORD_BASE = 0x4000

#: One invariant word in the canonical corpus. Carried, never trusted.
CONSTANT_RAW = 0x0800776D

#: The measured format, stated here independently of the implementation.
#:
#: The synthetic layout below is written with these literals rather than with
#: the module's constants, so a mutation to either constant is *detected* by
#: these tests instead of being silently followed by the fixture.
MEASURED_RECORD_SIZE = 24
MEASURED_ELEMENT_WIDTH = 4


def key_for(index: int) -> bytes:
    """A distinct two-byte map key per index, differing in *both* bytes.

    Two differing bytes matter: a controlled destination edit is only proved to
    touch both key fields when both of them actually change.
    """
    return bytes((0x10 + index, 0x20 + index))


def put_u32(data: bytearray, offset: int, value: int) -> None:
    data[offset : offset + 4] = value.to_bytes(4, "little")


def record_bytes(
    *,
    class_raw: int = TRANSITION_CLASS_A_RAW,
    constant_raw: int = CONSTANT_RAW,
    first: tuple[int, int] = (0, 8),
    second: tuple[int, int] = (0, 8),
    byte_0x10: int = 0,
    destination_key: tuple[int, int] = (0x11, 0x21),
    byte_0x13: int = 0,
    word_0x14: int = 0,
    byte_0x16: int = 0,
    byte_0x17: int = 0,
) -> bytes:
    """One 24-byte record with every field controllable."""
    return TransitionRecord(
        class_raw=class_raw,
        constant_raw=constant_raw,
        bound_a_raw=first[0],
        bound_b_raw=second[0],
        bound_c_raw=first[1],
        bound_d_raw=second[1],
        byte_0x10_raw=byte_0x10,
        destination_key_high=destination_key[0],
        destination_key_low=destination_key[1],
        byte_0x13_raw=byte_0x13,
        word_0x14_raw=word_0x14,
        byte_0x16_raw=byte_0x16,
        byte_0x17_raw=byte_0x17,
    ).to_bytes()


def synthetic_image(per_map: list[list[bytes]]) -> bytes:
    """A minimal image carrying exactly the structures the format defines."""
    data = bytearray(IMAGE_SIZE)
    running = 0
    for index, records in enumerate(per_map):
        source = SOURCE_BASE + index * 8
        root = ROOT_BASE + index * ROOT_STRIDE
        array = ARRAY_BASE + index * ARRAY_STRIDE
        put_u32(data, source, GBA_BASE + root)
        put_u32(data, root + ROOT_COUNT_OFFSET, len(records))
        put_u32(data, root + ROOT_ARRAY_OFFSET, GBA_BASE + array if records else 0)
        for element, raw in enumerate(records):
            offset = RECORD_BASE + (running + element) * MEASURED_RECORD_SIZE
            data[offset : offset + MEASURED_RECORD_SIZE] = raw
            put_u32(data, array + element * MEASURED_ELEMENT_WIDTH, GBA_BASE + offset)
        running += len(records)
        table = TABLE_OFFSET + index * TABLE_STRIDE
        data[table : table + 2] = key_for(index)
        put_u32(data, table + MAP_ENTRY_SOURCE_OFFSET, GBA_BASE + source)
    return bytes(data)


def loaded(per_map: list[list[bytes]]) -> tuple[bytes, MapTransitions]:
    image = synthetic_image(per_map)
    corpus = _read_corpus(
        image,
        table_offset=TABLE_OFFSET,
        table_count=len(per_map),
        profile_id="synthetic",
        base_sha256=hashlib.sha256(image).hexdigest(),
    )
    return image, corpus


def offset_of(corpus: MapTransitions, identity: TransitionIdentity) -> int:
    return corpus.entry(identity).file_offset


# --- the codec ---------------------------------------------------------------


def test_the_record_is_twenty_four_bytes_of_engine_read_fields() -> None:
    assert TRANSITION_SIZE == MEASURED_RECORD_SIZE == 24
    assert ARRAY_ELEMENT_WIDTH == MEASURED_ELEMENT_WIDTH == 4
    assert sum(item.width for item in TRANSITION_LAYOUT) == TRANSITION_SIZE
    assert [item.offset for item in TRANSITION_LAYOUT] == [
        0x00, 0x04, 0x08, 0x0A, 0x0C, 0x0E, 0x10, 0x11, 0x12, 0x13, 0x14, 0x16, 0x17
    ]


def test_a_decoded_record_re_encodes_byte_identically() -> None:
    raw = record_bytes(
        class_raw=TRANSITION_CLASS_B_RAW,
        constant_raw=CONSTANT_RAW,
        first=(96, 257),
        second=(0, 17),
        byte_0x10=0x03,
        destination_key=(0x11, 0x21),
        byte_0x13=0x01,
        word_0x14=0x00C0,
        byte_0x16=0x8B,
        byte_0x17=0x02,
    )
    record = TransitionRecord.from_bytes(raw)
    assert record.to_bytes() == raw
    assert len(raw) == 24


@pytest.mark.parametrize("size", [0, 23, 25, 48])
def test_a_record_of_the_wrong_length_is_refused(size: int) -> None:
    with pytest.raises(MapTransitionLengthError):
        TransitionRecord.from_bytes(bytes(size))


def test_the_region_decodes_positionally_and_an_axis_swap_is_load_bearing() -> None:
    """A non-square, asymmetric case: every one of the four values is distinct.

    The record stores `first` low at `+0x08`, `second` low at `+0x0A`, `first`
    high at `+0x0C` and `second` high at `+0x0E`. Transposing the two intervals,
    or their endpoints, changes bytes here - a square or symmetric region could
    not tell those mistakes apart.
    """
    raw = record_bytes(first=(592, 601), second=(136, 241))
    record = TransitionRecord.from_bytes(raw)
    assert record.region == TransitionRegion(first=(592, 601), second=(136, 241))
    assert raw[0x08:0x10] == (592).to_bytes(2, "little") + (136).to_bytes(2, "little") \
        + (601).to_bytes(2, "little") + (241).to_bytes(2, "little")
    assert record.region.to_bytes() == raw[0x08:0x10]

    swapped = TransitionRegion(first=(136, 241), second=(592, 601))
    assert swapped != record.region
    assert swapped.to_bytes() != raw[0x08:0x10]
    # The intervals are deliberately not axis-named, so the only honest
    # statement is positional: 592 is not 136, and 601 is not 241.
    assert record.region.first[0] != record.region.second[0]
    assert record.region.first[1] != record.region.second[1]


@pytest.mark.parametrize(
    "first, second, reason",
    [
        ((20, 10), (0, 5), "unordered first"),
        ((0, 5), (20, 10), "unordered second"),
        ((7, 7), (0, 5), "degenerate first"),
        ((0, 5), (7, 7), "degenerate second"),
    ],
)
def test_an_unordered_or_degenerate_region_is_refused(
    first: tuple[int, int], second: tuple[int, int], reason: str
) -> None:
    with pytest.raises(MapTransitionRegionError):
        TransitionRegion(first=first, second=second)
    raw = record_bytes(first=first, second=second)
    with pytest.raises(MapTransitionRegionError):
        TransitionRecord.from_bytes(raw).validate()


def test_a_region_endpoint_outside_its_u16_field_is_refused() -> None:
    with pytest.raises(MapTransitionValueError):
        TransitionRegion(first=(0, 0x10000), second=(0, 5))


@pytest.mark.parametrize(
    "class_raw",
    [0x00000000, 0x08000000, 0x08007674, 0x08007676, 0x080072CC, 0xFFFFFFFF],
)
def test_an_unmeasured_class_word_is_refused(class_raw: int) -> None:
    """The fail-closed regression for an unsupported transition family."""
    raw = record_bytes(class_raw=class_raw)
    record = TransitionRecord.from_bytes(raw)
    assert record.to_bytes() == raw, "an unknown class must still round-trip"
    with pytest.raises(MapTransitionFamilyError):
        record.validate()
    assert record.class_raw not in SUPPORTED_CLASS_RAW


@pytest.mark.parametrize(
    "class_raw", sorted(SUPPORTED_CLASS_RAW)
)
def test_both_measured_class_words_are_supported(class_raw: int) -> None:
    record = TransitionRecord.from_bytes(record_bytes(class_raw=class_raw))
    assert record.validate() is record
    assert record.is_supported_class


def test_a_field_outside_its_physical_width_is_refused() -> None:
    record = TransitionRecord.from_bytes(record_bytes())
    for bad in (
        {"byte_0x10_raw": 0x100},
        {"destination_key_high": -1},
        {"class_raw": 0x1_0000_0000},
        {"bound_a_raw": 0x10000},
    ):
        with pytest.raises(MapTransitionValueError):
            dataclasses_replace(record, **bad).to_bytes()


def test_a_controlled_destination_edit_moves_only_the_key_bytes() -> None:
    raw = record_bytes(destination_key=(0x11, 0x21))
    edited = TransitionRecord.from_bytes(raw).with_destination_key(key_for(2))
    out = edited.to_bytes()
    assert [i for i in range(TRANSITION_SIZE) if out[i] != raw[i]] == [0x11, 0x12]
    assert edited.destination_key == key_for(2)


def test_a_destination_key_must_be_two_bytes() -> None:
    record = TransitionRecord.from_bytes(record_bytes())
    for bad in (b"", b"\x01", b"\x01\x02\x03"):
        with pytest.raises(MapTransitionValueError):
            record.with_destination_key(bad)


def test_a_controlled_region_edit_writes_the_positional_slots() -> None:
    """Every one of the eight region bytes moves, and to a distinguishable value.

    A mistake that swapped the two intervals, or either interval's endpoints,
    would land a different value in at least one of these offsets.
    """
    raw = record_bytes(first=(0, 1), second=(0, 2))
    region = TransitionRegion(
        first=(0x0102, 0x0304), second=(0x0506, 0x0708)
    )
    edited = TransitionRecord.from_bytes(raw).with_region(region)
    out = edited.to_bytes()
    assert [i for i in range(TRANSITION_SIZE) if out[i] != raw[i]] == list(range(0x08, 0x10))
    assert out[0x08:0x10] == bytes((0x02, 0x01, 0x06, 0x05, 0x04, 0x03, 0x08, 0x07))
    assert TransitionRecord.from_bytes(out).region == region


def test_an_edit_never_touches_the_unresolved_fields() -> None:
    raw = record_bytes(byte_0x10=0x41, byte_0x13=0x01, word_0x14=0x1234,
                       byte_0x16=0x8B, byte_0x17=0x02)
    record = TransitionRecord.from_bytes(raw)
    for edited in (
        record.with_destination_key(key_for(3)),
        record.with_region(TransitionRegion(first=(5, 6), second=(7, 8))),
    ):
        out = edited.to_bytes()
        for offset in (0x00, 0x04, 0x10, 0x13, 0x14, 0x16, 0x17):
            assert out[offset] == raw[offset], hex(offset)


# --- the authority -----------------------------------------------------------


def test_the_identity_names_a_source_map_and_an_index_only() -> None:
    """No address, no offset: the identity model is the whole addressability."""
    assert {field.name for field in fields(TransitionIdentity)} == {"source", "index"}
    identity = TransitionIdentity(MapIdentity(39), 1)
    assert identity.key == "map:0039/transition:0001"
    assert str(identity) == identity.key


def test_the_identity_rejects_a_negative_index_and_a_non_map_source() -> None:
    with pytest.raises(MapTransitionsError):
        TransitionIdentity(MapIdentity(0), -1)
    with pytest.raises(MapTransitionsError):
        TransitionIdentity(39, 0)  # type: ignore[arg-type]


def test_the_corpus_enumerates_in_map_then_index_order() -> None:
    _, corpus = loaded([
        [record_bytes(destination_key=tuple(key_for(1)))],
        [],
        [record_bytes(destination_key=tuple(key_for(0))),
         record_bytes(destination_key=tuple(key_for(1)))],
    ])
    assert corpus.map_count == 3
    assert corpus.record_count == 3
    assert [entry.identity.key for entry in corpus.entries()] == [
        "map:0000/transition:0000",
        "map:0002/transition:0000",
        "map:0002/transition:0001",
    ]
    assert [entry.identity.key for entry in corpus.for_map(MapIdentity(2))] == [
        "map:0002/transition:0000",
        "map:0002/transition:0001",
    ]
    assert corpus.for_map(MapIdentity(1)) == ()


def test_every_record_round_trips_byte_identically() -> None:
    _, corpus = loaded([
        [record_bytes(first=(96, 257), second=(0, 17))],
        [record_bytes(class_raw=TRANSITION_CLASS_B_RAW, first=(1, 2), second=(3, 4))],
    ])
    for entry in corpus.entries():
        assert entry.record.to_bytes() == entry.original_bytes, entry.identity
        assert len(entry.original_bytes) == TRANSITION_SIZE
    assert len(corpus.validate()) == 2


def test_a_destination_decodes_to_a_map_identity() -> None:
    _, corpus = loaded([[record_bytes(destination_key=tuple(key_for(2)))], [], []])
    identity = TransitionIdentity(MapIdentity(0), 0)
    assert corpus.destination(identity) == MapIdentity(2)
    assert corpus.map_for_key(key_for(2)) == MapIdentity(2)
    assert corpus.key_for(MapIdentity(2)) == key_for(2)


def test_a_controlled_destination_edit_changes_only_the_two_key_bytes() -> None:
    image, corpus = loaded([
        [record_bytes(destination_key=tuple(key_for(0)))],
        [],
        [],
    ])
    identity = TransitionIdentity(MapIdentity(0), 0)
    offset = offset_of(corpus, identity)
    before = corpus.key_for(corpus.destination(identity))
    corpus.set_destination(identity, MapIdentity(2))
    assert corpus.destination(identity) == MapIdentity(2)

    plan = corpus.plan()
    edited = apply_plan(image, plan)
    assert [i for i in range(len(image)) if image[i] != edited[i]] == [
        offset + 0x11,
        offset + 0x12,
    ]
    assert corpus.key_for(MapIdentity(2)) == key_for(2)
    assert any(c != d for c, d in zip(corpus.key_for(MapIdentity(2)), before))
    effective = [c for c in plan.changes if c.is_effective]
    assert [c.owner for c in effective] == ["map:0000/transition:0000"]
    assert effective[0].reason == "transition edit: destination_key_high, destination_key_low"


def test_an_edit_leaves_every_other_record_untouched() -> None:
    image, corpus = loaded([
        [record_bytes(destination_key=tuple(key_for(0))),
         record_bytes(destination_key=tuple(key_for(1)))],
        [record_bytes(destination_key=tuple(key_for(0)))],
        [],
    ])
    target = TransitionIdentity(MapIdentity(0), 1)
    corpus.set_destination(target, MapIdentity(2))
    edited = apply_plan(image, corpus.plan())
    for entry in corpus.entries():
        if entry.identity == target:
            continue
        span = slice(entry.file_offset, entry.file_offset + TRANSITION_SIZE)
        assert edited[span] == entry.original_bytes, entry.identity
    assert [c.owner for c in corpus.plan().changes if c.is_effective] == [str(target)]


def test_a_controlled_region_edit_changes_only_the_region_bytes() -> None:
    image, corpus = loaded([[record_bytes(first=(0, 1), second=(0, 2))]])
    identity = TransitionIdentity(MapIdentity(0), 0)
    offset = offset_of(corpus, identity)
    corpus.set_region(
        identity, TransitionRegion(first=(0x0102, 0x0304), second=(0x0506, 0x0708))
    )
    edited = apply_plan(image, corpus.plan())
    assert [i for i in range(len(image)) if image[i] != edited[i]] == list(
        range(offset + 0x08, offset + 0x10)
    )


def test_a_no_op_plan_emits_no_differing_bytes() -> None:
    image, corpus = loaded([[record_bytes()]])
    edited = apply_plan(image, corpus.plan())
    assert edited == image
    assert not any(change.is_effective for change in corpus.plan().changes)


def test_an_unknown_transition_identity_is_refused() -> None:
    _, corpus = loaded([[record_bytes()]])
    for identity in (
        TransitionIdentity(MapIdentity(0), 1),
        TransitionIdentity(MapIdentity(3), 0),
    ):
        with pytest.raises(UnknownTransitionError):
            corpus.entry(identity)


def test_an_unknown_destination_map_is_refused() -> None:
    _, corpus = loaded([[record_bytes()]])
    identity = TransitionIdentity(MapIdentity(0), 0)
    with pytest.raises(TransitionFieldError):
        corpus.set_destination(identity, MapIdentity(9))
    with pytest.raises(TransitionFieldError):
        corpus.set_destination(identity, MapIdentity(1))
    with pytest.raises(TransitionFieldError):
        corpus.set_destination(identity, 2)  # type: ignore[arg-type]


def test_a_destination_key_that_names_no_map_is_refused() -> None:
    _, corpus = loaded([[record_bytes(destination_key=(0xFF, 0xFE))]])
    with pytest.raises(MapTransitionsError):
        corpus.destination(TransitionIdentity(MapIdentity(0), 0))


def test_an_invalid_region_never_reaches_a_plan() -> None:
    image, corpus = loaded([[record_bytes()]])
    identity = TransitionIdentity(MapIdentity(0), 0)
    with pytest.raises(MapTransitionRegionError):
        TransitionRegion(first=(20, 10), second=(0, 5))
    with pytest.raises(TransitionFieldError):
        corpus.set_region(identity, ((0, 5), (0, 5)))  # type: ignore[arg-type]
    assert apply_plan(image, corpus.plan()) == image


def test_an_unsupported_record_fails_the_whole_load() -> None:
    """The corpus-level half of the fail-closed regression."""
    with pytest.raises(MapTransitionFamilyError):
        loaded([[record_bytes(), record_bytes(class_raw=0x08001234)]])
    with pytest.raises(MapTransitionRegionError):
        loaded([[record_bytes(first=(20, 10), second=(0, 5))]])


def test_a_shared_record_is_refused() -> None:
    data = bytearray(synthetic_image([[record_bytes()], [record_bytes()]]))
    put_u32(data, ARRAY_BASE + ARRAY_STRIDE, GBA_BASE + RECORD_BASE)
    with pytest.raises(MapTransitionsError, match="reached by both"):
        _read_corpus(bytes(data), table_offset=TABLE_OFFSET, table_count=2,
                     profile_id="synthetic", base_sha256="0" * 64)


def test_records_with_overlapping_extents_are_refused() -> None:
    data = bytearray(synthetic_image([[record_bytes(), record_bytes()]]))
    put_u32(data, ARRAY_BASE + ARRAY_ELEMENT_WIDTH, GBA_BASE + RECORD_BASE + 0x08)
    with pytest.raises(MapTransitionsError, match="overlap"):
        _read_corpus(bytes(data), table_offset=TABLE_OFFSET, table_count=1,
                     profile_id="synthetic", base_sha256="0" * 64)


def test_a_duplicated_map_lookup_key_is_refused() -> None:
    data = bytearray(synthetic_image([[record_bytes()], [record_bytes()]]))
    second = TABLE_OFFSET + TABLE_STRIDE
    data[second : second + 2] = key_for(0)
    with pytest.raises(MapTransitionsError, match="share the two-byte"):
        _read_corpus(bytes(data), table_offset=TABLE_OFFSET, table_count=2,
                     profile_id="synthetic", base_sha256="0" * 64)


@pytest.mark.parametrize(
    "patch, message",
    [
        (("source", 0), "declares no selector-1 source"),
        (("source", 0xDEADBEEF), "selector-1 source"),
        (("root", 0), "empty selector-1 word run"),
        (("root", 0xDEADBEEF), "selector-1 root"),
        (("count_null_array", 2), "null together"),
        (("array_null_count", 1), "null together"),
        (("array", 0xDEADBEEF), "array 0xDEADBEEF is not an aligned"),
        (("element", 0xDEADBEEF), "not an aligned transition"),
        (("element", GBA_BASE + RECORD_BASE + 2), "not an aligned transition"),
        (("element", GBA_BASE + IMAGE_SIZE - 8), "extends past the image"),
    ],
)
def test_an_unmeasured_root_or_element_form_is_refused(
    patch: tuple[str, int], message: str
) -> None:
    data = bytearray(synthetic_image([[record_bytes(), record_bytes()]]))
    table = TABLE_OFFSET
    source = SOURCE_BASE
    root = ROOT_BASE
    kind, value = patch
    if kind == "source":
        put_u32(data, table + MAP_ENTRY_SOURCE_OFFSET, value)
    elif kind == "root":
        put_u32(data, source, value)
    elif kind == "count_null_array":
        put_u32(data, root + ROOT_COUNT_OFFSET, value)
        put_u32(data, root + ROOT_ARRAY_OFFSET, 0)
    elif kind == "array_null_count":
        put_u32(data, root + ROOT_COUNT_OFFSET, 0)
        put_u32(data, root + ROOT_ARRAY_OFFSET, GBA_BASE + ARRAY_BASE)
    elif kind == "array":
        put_u32(data, root + ROOT_ARRAY_OFFSET, value)
    else:
        put_u32(data, ARRAY_BASE, value)
    with pytest.raises(MapTransitionsError, match=message):
        _read_corpus(bytes(data), table_offset=TABLE_OFFSET, table_count=1,
                     profile_id="synthetic", base_sha256="0" * 64)


def test_a_map_whose_root_declares_no_records_is_enumerable_and_empty() -> None:
    _, corpus = loaded([[], [record_bytes()]])
    assert corpus.for_map(MapIdentity(0)) == ()
    assert corpus.record_count == 1
    assert corpus.entry(TransitionIdentity(MapIdentity(1), 0)).original_bytes


def test_an_array_reaching_past_the_declared_count_is_not_read() -> None:
    """The count is the engine's bound; the elements after it are not records."""
    data = bytearray(synthetic_image([[record_bytes(), record_bytes()]]))
    put_u32(data, ROOT_BASE + ROOT_COUNT_OFFSET, 1)
    corpus = _read_corpus(
        bytes(data), table_offset=TABLE_OFFSET, table_count=1,
        profile_id="synthetic", base_sha256="0" * 64,
    )
    assert corpus.record_count == 1
    assert next(corpus.entries()).identity.index == 0
