"""Portable tests for CREATED map transitions. MAP-WARP-CREATE-PROJECT-001.

Three layers are covered over a synthetic image and no ROM:

* ``project.model.TransitionCreations`` - what a created transition *is* on disk:
  the durable ``map:NNNN/transition:<name>`` identity, the template it is composed
  over, the pinned template bytes, and the refusals that keep a malformed document
  from being silently dropped from a build;
* ``map_transitions.materialize_transition_creations`` - the authority that turns
  that document into a byte plan: it allocates the record and the expanded pointer
  array, composes the record over the template, and rewrites ``root + 0x40`` and
  ``root + 0x44``;
* ``map_transitions.set_transition_creations`` / ``read_project_transition_creations``
  - the save/reopen round trip, which is where the authored identity has to survive.

The synthetic image is deliberately *not* a canonical ROM and asserts no canonical
count. The real 8 MiB image, its real map 40 and the build are exercised in
``tests/integration/test_map_transition_create_rom.py``.

Several assertions below are the named regressions the ticket's mutations M1-M6 are
aimed at; each is marked with the mutation it kills.
"""

from __future__ import annotations

from dataclasses import replace as dataclasses_replace
import hashlib
from pathlib import Path

import pytest

from tests.unit.test_map_transitions import (
    GBA_BASE,
    IMAGE_SIZE,
    TABLE_OFFSET,
    key_for,
    record_bytes,
    synthetic_image,
)

from tools.webfoot.allocation import InsufficientSpaceError
from tools.webfoot.binary import GbaRomAddress
from tools.webfoot.formats.map_transitions import (
    CREATED_CLASS_RAW,
    FACING_EAST,
    FACING_NORTH,
    FACING_PRESERVED_MASK,
    SUPPORTED_CLASS_RAW,
    TRANSITION_CLASS_B_RAW,
    TRANSITION_LAYOUT,
    TRANSITION_SIZE,
    MapTransitionRegionError,
    TransitionArrival,
    TransitionRegion,
)
from tools.webfoot.map_transitions import (
    CREATION_ARRAY_PREFIX,
    CREATION_RECORD_PREFIX,
    AuthoredTransitionCreation,
    CreatedTransitionIdentity,
    MapIdentity,
    MapTransitionsError,
    TransitionCreation,
    TransitionFieldError,
    TransitionIdentity,
    created_record_fields,
    materialize_transition_creations,
    read_map_transitions,
    read_project_transition_creations,
    read_transition_creations,
    remove_transition_creation,
    set_transition_creations,
)
from tools.webfoot.packaged import packaged_profile
from tools.webfoot.profile import MapEntryTableProfile, RomProfile
from tools.webfoot.project import (
    PROJECT_FORMAT_VERSION,
    TRANSITION_CREATION_FILE,
    TRANSITION_FILE,
    ProjectLoadError,
    ProjectMeta,
    ProjectValidationError,
    TransitionCreations,
    read_project,
    transition_creation_identity,
    write_project,
    write_transition_creations,
    write_transition_edits,
)
from tools.webfoot.write import apply_plan, plan_changes

META = ProjectMeta(
    format_version=PROJECT_FORMAT_VERSION,
    profile_id="synthetic_transition_creation",
    game="synthetic",
    base_rom_sha256="0" * 64,
    base_rom_size=IMAGE_SIZE,
    name="synthetic",
)

#: The destination map's own lookup key, for the synthetic table.
DESTINATION = MapIdentity(1)

#: A record whose ``+0x10`` carries a gate of 2 and no arrival-facing override, and
#: whose ``+0x13`` is 0 - the two unresolved bytes a creation preserves. The gate
#: value is deliberately NOT 0 so that a composition which silently zeroes the low
#: nibble is caught, and the override is deliberately absent so that "the created
#: record states no override" and "it inherited the template's" differ.
TEMPLATE_FACING_RAW = 0x02
TEMPLATE_BYTE_0X13 = 0
TEMPLATE_REGION = TransitionRegion(first=(0, 9), second=(112, 169))
#: The template's own arrival. Small, because the synthetic destination map's
#: declared extent is 241x161 px, and the aliasing test below has to reach the
#: composition check rather than the bounds check.
TEMPLATE_ARRIVAL = TransitionArrival(8, 8)

AUTHORED_REGION = TransitionRegion(first=(232, 273), second=(0, 17))
AUTHORED_ARRIVAL = TransitionArrival(16, 24)

#: Three maps: map 0 holds one 566-class record, map 1 one record, map 2 none.
PER_MAP = [
    [
        record_bytes(
            destination_key=tuple(key_for(1)),
            first=TEMPLATE_REGION.first,
            second=TEMPLATE_REGION.second,
            byte_0x10=TEMPLATE_FACING_RAW,
            byte_0x13=TEMPLATE_BYTE_0X13,
            word_0x14=TEMPLATE_ARRIVAL.x,
            byte_0x16=TEMPLATE_ARRIVAL.y & 0xFF,
            byte_0x17=TEMPLATE_ARRIVAL.y >> 8,
        )
    ],
    [record_bytes(destination_key=tuple(key_for(0)))],
    [],
]

TEMPLATE = TransitionIdentity(MapIdentity(0), 0)
NEW_DOOR = CreatedTransitionIdentity(MapIdentity(0), "new-door")


def image_bytes(per_map=None) -> bytes:
    return synthetic_image(PER_MAP if per_map is None else per_map)


def profile_for(image: bytes, *, count: int = len(PER_MAP)) -> RomProfile:
    """The packaged profile with this synthetic image's identity and free space.

    ``free_regions`` is emptied because the packaged profile's single declared
    VERIFIED_FREE region lies past this 32 KiB image, which the storage model would
    refuse - and because a creation is ``EXPANDED_ONLY``, so canonical free space is
    not something these tests should accidentally depend on.
    """
    base = packaged_profile()
    assert base.map_entries is not None
    return dataclasses_replace(
        base,
        id="synthetic_transition_creation",
        sha256=hashlib.sha256(image).hexdigest(),
        size=len(image),
        free_regions=(),
        map_entries=MapEntryTableProfile(
            address=GbaRomAddress(GBA_BASE + TABLE_OFFSET),
            count=count,
            record_size=base.map_entries.record_size,
        ),
    )


def project_at(tmp_path: Path, creations: TransitionCreations | None = None) -> Path:
    write_project(
        tmp_path, META, enemies=[], characters=[], transition_creations=creations
    )
    return tmp_path


def request(
    *, name: str = "new-door", template: TransitionIdentity = TEMPLATE,
    destination: MapIdentity = DESTINATION, region: TransitionRegion = AUTHORED_REGION,
    arrival: TransitionArrival = AUTHORED_ARRIVAL, facing: int | None = FACING_EAST,
    source: MapIdentity = MapIdentity(0),
) -> TransitionCreation:
    identity = CreatedTransitionIdentity(source, name)
    return TransitionCreation(
        identity=identity,
        template=template,
        destination=destination,
        region=region,
        arrival=arrival,
        facing=facing,
    )


def authored_for(
    image: bytes, creation: TransitionCreation, *, priors: tuple[int, int] | None = None
) -> AuthoredTransitionCreation:
    """A stored creation whose priors are measured from the image, as the SDK does.

    ``priors`` overrides them, for the tests that need a creation naming a template
    the image does not contain - so the authority, and not this fixture, is what
    refuses it.
    """
    if priors is None:
        profile = profile_for(image)
        template = read_map_transitions(image, profile).entry(creation.template).record
        priors = (template.byte_0x10_raw, template.byte_0x13_raw)
    return AuthoredTransitionCreation(
        creation=creation,
        prior_facing_raw=priors[0],
        prior_unresolved_raw=priors[1],
    )


def materialize(image: bytes, *creations: TransitionCreation, reserved=()):
    profile = profile_for(image)
    mapping = {
        creation.identity: authored_for(image, creation) for creation in creations
    }
    return materialize_transition_creations(
        image, mapping, profile=profile, reserved=reserved
    )


def build(image: bytes, result) -> bytes:
    profile = profile_for(image)
    plan = plan_changes(
        image,
        result.changes,
        profile_id=profile.id,
        base_sha256=profile.identity.sha256,
        generated_image=result.generated_image,
        generated_allocations=result.generated_allocations,
        transition_creations=result.provenance,
    )
    return apply_plan(image, plan)


def u32(image: bytes, offset: int) -> int:
    return int.from_bytes(image[offset : offset + 4], "little")


#: The generated image's size, taken from the profile declaration rather than
#: restated, so an above-EOF address can be decoded the way a consumer would.
def offset_of(gba_address: int, image_size: int | None = None) -> int:
    if image_size is None:
        profile = packaged_profile()
        assert profile.generated_expansion is not None
        image_size = profile.generated_expansion.output_size
    return GbaRomAddress(gba_address).to_file_offset(image_size)


# --- the identity -------------------------------------------------------------


def test_the_identity_is_a_map_key_and_an_authored_name():
    identity = CreatedTransitionIdentity(MapIdentity(40), "kai-shop")
    assert identity.key == "map:0040/transition:kai-shop"
    assert str(identity) == identity.key
    # The authority and the document producer must spell the identity the same way;
    # the project package cannot import the authority (it must not reach a module
    # that opens ROMs), so the two spellings are pinned together here.
    assert transition_creation_identity(40, "kai-shop") == identity.key


def test_the_identity_carries_no_address_and_no_array_index():
    """The ticket's identity rule: nothing positional may appear in the key."""
    key = CreatedTransitionIdentity(MapIdentity(7), "a-door").key
    assert key == "map:0007/transition:a-door"
    assert "0x" not in key
    assert key.count(":") == 2  # map:, transition: - and no index


@pytest.mark.parametrize(
    "name",
    ["", "Door", "1door", "-door", "door name", "door.name", "a" * 65, "døor"],
)
def test_a_name_outside_the_measured_shape_is_refused(name):
    with pytest.raises(MapTransitionsError):
        CreatedTransitionIdentity(MapIdentity(0), name)


def test_a_non_map_source_is_refused():
    with pytest.raises(MapTransitionsError):
        CreatedTransitionIdentity("map:0000", "door")  # type: ignore[arg-type]


# --- the document -------------------------------------------------------------


def stored(creation: TransitionCreation | None = None) -> TransitionCreations:
    creation = creation or request()
    return TransitionCreations.from_edits({(0, creation.identity.name): _stored(creation)})


def _stored(creation: TransitionCreation):
    from tools.webfoot.project import AuthoredTransitionCreation as Stored

    return Stored(
        source=creation.identity.source.key,
        name=creation.identity.name,
        template=str(creation.template),
        destination=str(creation.destination),
        region=creation.region,
        arrival=(creation.arrival.x, creation.arrival.y),
        prior_facing_raw=TEMPLATE_FACING_RAW,
        prior_unresolved_raw=TEMPLATE_BYTE_0X13,
        facing=creation.facing,
    )


def test_the_document_round_trips_through_disk(tmp_path):
    project_at(tmp_path, stored())
    reopened = read_transition_creations(tmp_path)
    assert reopened == stored()
    assert reopened.edits()[(0, "new-door")].identity == NEW_DOOR.key


def test_the_stored_document_carries_no_address_offset_or_index(tmp_path):
    project_at(tmp_path, stored())
    text = (tmp_path / TRANSITION_CREATION_FILE).read_text(encoding="utf-8")
    assert "0x" not in text
    for banned in ("offset", "address", "index", "record"):
        assert banned not in text
    assert "template = \"map:0000/transition:0000\"" in text


def test_the_document_is_keyed_for_deterministic_order(tmp_path):
    first = request(name="b-door")
    second = request(name="a-door")
    document = TransitionCreations.from_edits(
        {(0, first.identity.name): _stored(first), (0, second.identity.name): _stored(second)}
    ).to_document()
    assert list(document["creation"]["map:0000"]) == ["a-door", "b-door"]
    assert TransitionCreations.from_edits({}).is_empty()


def test_names_for_map_is_the_order_a_build_appends_in():
    first = request(name="zulu")
    second = request(name="alpha")
    creations = TransitionCreations.from_edits(
        {(0, "zulu"): _stored(first), (0, "alpha"): _stored(second)}
    )
    assert creations.names_for_map(0) == ("alpha", "zulu")
    assert creations.names_for_map(9) == ()


def test_a_template_outside_the_same_source_map_is_refused():
    """The text-level half of the same-map template rule."""
    with pytest.raises(ProjectValidationError):
        TransitionCreations.from_edits({(0, "door"): _stored(
            request(template=TransitionIdentity(MapIdentity(1), 0))
        )})


@pytest.mark.parametrize(
    "missing",
    ["template", "destination", "region", "arrival", "prior_facing_raw",
     "prior_unresolved_raw"],
)
def test_a_creation_missing_a_required_field_is_refused(missing, tmp_path):
    entry = _stored(request()).to_document()
    del entry[missing]
    with pytest.raises(ProjectLoadError):
        TransitionCreations.from_document(
            {"creation": {"map:0000": {"door": entry}}}, "x"
        )


def test_an_unknown_key_in_a_creation_is_refused():
    entry = _stored(request()).to_document()
    entry["address"] = 0x1234
    with pytest.raises(ProjectLoadError):
        TransitionCreations.from_document(
            {"creation": {"map:0000": {"door": entry}}}, "x"
        )


def test_a_project_without_the_creation_document_stays_loadable(tmp_path):
    project_at(tmp_path)
    assert read_project(tmp_path).transition_creations.is_empty()
    assert not (tmp_path / TRANSITION_CREATION_FILE).exists()


def test_an_empty_creation_set_writes_no_document(tmp_path):
    write_transition_creations(tmp_path, TransitionCreations())
    assert not (tmp_path / TRANSITION_CREATION_FILE).exists()


def test_a_malformed_document_on_disk_is_an_error_not_an_empty_set(tmp_path):
    write_project(tmp_path, META, enemies=[], characters=[])
    (tmp_path / TRANSITION_CREATION_FILE).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / TRANSITION_CREATION_FILE).write_text(
        "[creation]\n", encoding="utf-8"
    )
    with pytest.raises(ProjectLoadError):
        read_project(tmp_path)


def test_removing_the_last_edit_does_not_delete_a_creation(tmp_path):
    """The reason the two documents are separate: one writer must not eat the other."""
    from tools.webfoot.project import TransitionEdits

    project_at(tmp_path, stored())
    write_transition_edits(tmp_path, TransitionEdits())
    assert not (tmp_path / TRANSITION_FILE).exists()
    assert (tmp_path / TRANSITION_CREATION_FILE).exists()
    assert read_project(tmp_path).transition_creations == stored()


# --- materialization ----------------------------------------------------------


def test_a_creation_appends_one_record_and_increments_the_root_count():
    """M1 - a build that does not increment root+0x40 fails here."""
    image = image_bytes()
    result = materialize(image, request())
    output = build(image, result)
    root = read_map_transitions(image, profile_for(image)).root_for(MapIdentity(0))
    assert u32(image, offset_of(root.count_offset)) == 1
    assert u32(output, offset_of(root.count_offset)) == 2
    enumerated = tuple(read_map_transitions(output, profile_for(image)).for_map(MapIdentity(0)))
    assert [entry.identity.index for entry in enumerated] == [0, 1]


def test_the_expanded_array_carries_the_canonical_elements_then_the_new_one():
    """M2 and M3 - a build that leaves the old array, or appends with the wrong
    stride or order, fails on these bytes."""
    image = image_bytes()
    result = materialize(image, request())
    output = build(image, result)
    root = read_map_transitions(image, profile_for(image)).root_for(MapIdentity(0))
    canonical_element = image[offset_of(root.array_address) : offset_of(root.array_address) + 4]
    new_array = u32(output, offset_of(root.array_pointer_offset))
    assert new_array != root.array_address
    assert offset_of(new_array) >= IMAGE_SIZE, "the expanded array must live above EOF"
    body = output[offset_of(new_array) : offset_of(new_array) + 8]
    record_address = u32(output, offset_of(new_array) + 4)
    assert body[:4] == canonical_element
    assert body[4:] == record_address.to_bytes(4, "little")
    # The canonical array is still there, byte-identical, and no longer pointed at.
    assert image[offset_of(root.array_address) : offset_of(root.array_address) + 4] == body[:4]
    assert output[offset_of(root.array_address) : offset_of(root.array_address) + 4] == body[:4]


def test_the_root_array_pointer_is_rewritten_to_the_new_array():
    image = image_bytes()
    root = read_map_transitions(image, profile_for(image)).root_for(MapIdentity(0))
    result = materialize(image, request())
    output = build(image, result)
    new_array = u32(output, offset_of(root.array_pointer_offset))
    assert new_array != root.array_address
    assert new_array == result.provenance[0].array_address
    # The canonical array's own bytes are still in the image, untouched.
    assert output[offset_of(root.array_address):
                  offset_of(root.array_address) + 4] == \
        image[offset_of(root.array_address):offset_of(root.array_address) + 4]


def test_the_created_record_is_authored_by_the_project_and_preserved_by_the_template():
    image = image_bytes()
    result = materialize(image, request())
    output = build(image, result)
    corpus = read_map_transitions(output, profile_for(image))
    created = corpus.entry(TransitionIdentity(MapIdentity(0), 1)).record
    template = corpus.entry(TEMPLATE).record
    assert created.class_raw == CREATED_CLASS_RAW
    assert created.constant_raw == template.constant_raw
    assert created.byte_0x13_raw == TEMPLATE_BYTE_0X13
    assert created.region == AUTHORED_REGION
    assert created.destination_key == bytes(key_for(1))
    assert created.arrival == AUTHORED_ARRIVAL
    assert created.facing.arrival_direction == FACING_EAST
    assert created.facing.gate_direction == TEMPLATE_FACING_RAW & 0x03
    assert corpus.destination(TransitionIdentity(MapIdentity(0), 1)) == DESTINATION


def test_an_absent_facing_states_no_override_and_keeps_the_template_gate():
    image = image_bytes()
    result = materialize(image, request(facing=None))
    output = build(image, result)
    created = read_map_transitions(output, profile_for(image)).entry(
        TransitionIdentity(MapIdentity(0), 1)
    ).record
    assert created.byte_0x10_raw & ~FACING_PRESERVED_MASK == 0
    assert created.facing.arrival_direction is None
    assert created.facing.gate_direction == TEMPLATE_FACING_RAW & 0x03


def test_the_created_record_does_not_alias_the_template():
    """M4 - an array element pointing at the template record fails here."""
    image = image_bytes()
    result = materialize(image, request())
    output = build(image, result)
    corpus = read_map_transitions(output, profile_for(image))
    created_entry = corpus.entry(TransitionIdentity(MapIdentity(0), 1))
    template_entry = corpus.entry(TEMPLATE)
    assert created_entry.record_address != template_entry.record_address
    assert created_entry.record.to_bytes() != template_entry.record.to_bytes()
    # The template itself is untouched, byte for byte.
    assert output[offset_of(template_entry.record_address):
                  offset_of(template_entry.record_address) + TRANSITION_SIZE] == \
        image[offset_of(template_entry.record_address):
              offset_of(template_entry.record_address) + TRANSITION_SIZE]


def test_the_created_record_lives_above_canonical_eof_and_its_pointer_decodes():
    """M5 - a mis-encoded above-EOF pointer fails to decode back here."""
    image = image_bytes()
    result = materialize(image, request())
    for allocation in result.generated_allocations:
        assert allocation.allocated_range.start.value >= IMAGE_SIZE
        assert allocation.allocated_rom_address >= GBA_BASE + IMAGE_SIZE
        assert offset_of(allocation.allocated_rom_address) == (
            allocation.allocated_range.start.value
        )
    provenance = result.provenance[0]
    assert result.generated_allocations, "a creation must be expanded storage"
    assert provenance.record_pointer_bytes == (
        provenance.record_address.to_bytes(4, "little").hex()
    )
    assert provenance.array_pointer_bytes == (
        provenance.array_address.to_bytes(4, "little").hex()
    )
    assert provenance.count_bytes == provenance.count.to_bytes(4, "little").hex()


def test_only_the_root_pair_and_the_new_spans_differ():
    image = image_bytes()
    result = materialize(image, request())
    output = build(image, result)
    changed = {
        offset for offset in range(IMAGE_SIZE) if image[offset] != output[offset]
    }
    root = read_map_transitions(image, profile_for(image)).root_for(MapIdentity(0))
    allowed = set(
        range(offset_of(root.count_offset), offset_of(root.count_offset) + 4)
    ) | set(
        range(offset_of(root.array_pointer_offset),
              offset_of(root.array_pointer_offset) + 4)
    )
    assert changed <= allowed
    assert changed, "a creation must change at least the count and the array pointer"


def test_every_existing_record_stays_byte_identical():
    image = image_bytes()
    result = materialize(image, request())
    output = build(image, result)
    before = read_map_transitions(image, profile_for(image))
    after = read_map_transitions(output, profile_for(image))
    for entry in before.entries():
        assert after.entry(entry.identity).record == entry.record
        assert after.entry(entry.identity).record_address == entry.record_address


def test_the_field_accounting_covers_the_record_exactly_once():
    fields = created_record_fields()
    assert [(field.offset, field.width) for field in fields] == [
        (item.offset, item.width) for item in TRANSITION_LAYOUT
    ]
    assert sum(field.width for field in fields) == TRANSITION_SIZE
    sources = {field.field: (field.source, field.authored_mask) for field in fields}
    for name in ("class_raw", "constant_raw", "byte_0x13_raw"):
        assert sources[name] == ("template", 0)
    for name in ("bound_a_raw", "destination_key_high", "byte_0x17_raw"):
        assert sources[name][0] == "authored"
    assert sources["byte_0x10_raw"] == ("authored+template", 0xF0)
    # Eight region bytes, two destination-key bytes and four arrival bytes are
    # authored whole, plus the four authored bits of +0x10's high nibble.
    assert sum(field.authored_bits for field in fields) == 8 * 14 + 4


def test_the_provenance_records_the_identity_the_template_and_the_growth():
    image = image_bytes()
    result = materialize(image, request())
    assert len(result.provenance) == 1
    entry = result.provenance[0]
    assert entry.identity == NEW_DOOR.key
    assert entry.index == 1
    assert entry.template == str(TEMPLATE)
    assert entry.prior_count == 1 and entry.count == 2
    assert entry.destination == str(DESTINATION)
    assert entry.region == (AUTHORED_REGION.first, AUTHORED_REGION.second)
    assert entry.arrival == (AUTHORED_ARRIVAL.x, AUTHORED_ARRIVAL.y)
    assert entry.facing == FACING_EAST
    assert entry.prior_facing_raw == TEMPLATE_FACING_RAW
    assert entry.prior_unresolved_raw == TEMPLATE_BYTE_0X13
    assert entry.record_size == TRANSITION_SIZE
    assert entry.array_size == 2 * 4
    assert entry.record_file_offset == offset_of(entry.record_address)
    assert entry.array_file_offset == offset_of(entry.array_address)
    assert entry.prior_array_address != entry.array_address
    document = entry.to_json()
    assert document["record_fields"]


def test_two_creations_on_one_map_grow_the_array_once_and_keep_name_order():
    image = image_bytes()
    first = request(name="a-door")
    second = request(name="b-door")
    result = materialize(image, second, first)
    output = build(image, result)
    corpus = read_map_transitions(output, profile_for(image))
    enumerated = corpus.for_map(MapIdentity(0))
    assert [entry.identity.index for entry in enumerated] == [0, 1, 2]
    assert corpus.destination(TransitionIdentity(MapIdentity(0), 1)) == DESTINATION
    assert [entry.identity for entry in result.provenance] == [
        "map:0000/transition:a-door",
        "map:0000/transition:b-door",
    ]
    root = read_map_transitions(image, profile_for(image)).root_for(MapIdentity(0))
    assert u32(output, offset_of(root.count_offset)) == 3
    assert result.provenance[0].array_size == 3 * 4


def test_creations_on_two_maps_get_their_own_arrays():
    image = image_bytes()
    on_zero = request()
    on_one = request(
        name="back-door",
        source=MapIdentity(1),
        template=TransitionIdentity(MapIdentity(1), 0),
        destination=MapIdentity(0),
    )
    result = materialize(image, on_zero, on_one)
    arrays = {
        allocation.owner: allocation
        for allocation in result.generated_allocations
        if allocation.owner.startswith(CREATION_ARRAY_PREFIX)
    }
    assert set(arrays) == {
        f"{CREATION_ARRAY_PREFIX}map:0000",
        f"{CREATION_ARRAY_PREFIX}map:0001",
    }
    assert arrays[f"{CREATION_ARRAY_PREFIX}map:0000"].allocated_range != arrays[
        f"{CREATION_ARRAY_PREFIX}map:0001"
    ].allocated_range


def test_the_allocation_avoids_the_callers_reservation_set():
    image = image_bytes()
    from tools.webfoot.layout import FileOffset, RomRange

    reserved = (RomRange(FileOffset(IMAGE_SIZE), 0x2000),)
    result = materialize(image, request(), reserved=reserved)
    for allocation in result.generated_allocations:
        assert not allocation.allocated_range.overlaps(reserved[0])
    assert all(span.start.value >= IMAGE_SIZE + 0x2000 for span in result.reserved)


def test_materialization_is_deterministic_and_independent_of_request_order():
    image = image_bytes()
    first = materialize(image, request(name="a-door"), request(name="b-door"))
    second = materialize(image, request(name="b-door"), request(name="a-door"))
    assert [c.to_json() for c in first.changes] == [c.to_json() for c in second.changes]
    assert [p.to_json() for p in first.provenance] == [
        p.to_json() for p in second.provenance
    ]
    again = materialize(image, request(name="a-door"), request(name="b-door"))
    assert [c.to_json() for c in again.changes] == [
        c.to_json() for c in first.changes
    ]


def test_the_build_is_byte_identical_twice():
    image = image_bytes()
    assert build(image, materialize(image, request())) == build(
        image, materialize(image, request())
    )


def test_an_empty_creation_set_contributes_nothing():
    image = image_bytes()
    result = materialize_transition_creations(
        image, {}, profile=profile_for(image)
    )
    assert result.changes == ()
    assert result.provenance == ()
    assert result.generated_allocations == ()
    assert result.reserved == ()
    assert result.generated_image is None


# --- refusals -----------------------------------------------------------------


def test_a_creation_identical_to_its_template_is_refused():
    """The capability is creation, not aliasing.

    Every authored value is the template's own, so the composed record would come
    out byte-identical and the "creation" would be a second pointer at a record the
    image already has.
    """
    image = image_bytes()
    with pytest.raises(TransitionFieldError, match="byte-identical"):
        materialize(
            image,
            request(
                destination=MapIdentity(1),
                region=TEMPLATE_REGION,
                arrival=TEMPLATE_ARRIVAL,
                facing=None,
            ),
        )


def test_a_template_outside_the_source_map_is_refused():
    image = image_bytes()
    with pytest.raises(TransitionFieldError, match="same source map"):
        materialize(image, request(template=TransitionIdentity(MapIdentity(1), 0)))


def test_an_unknown_template_identity_is_refused():
    image = image_bytes()
    missing = request(template=TransitionIdentity(MapIdentity(0), 7))
    with pytest.raises(TransitionFieldError, match="does not contain"):
        materialize_transition_creations(
            image,
            {missing.identity: authored_for(image, missing, priors=(0, 0))},
            profile=profile_for(image),
        )


def test_a_169_class_template_is_refused():
    """Only the 566 class is supported: the other class's pair is a delta."""
    image = image_bytes(
        [
            [
                record_bytes(
                    class_raw=TRANSITION_CLASS_B_RAW,
                    destination_key=tuple(key_for(1)),
                    byte_0x10=TEMPLATE_FACING_RAW,
                )
            ],
            [record_bytes(destination_key=tuple(key_for(0)))],
            [],
        ]
    )
    with pytest.raises(TransitionFieldError, match="scene-relative delta"):
        materialize(image, request())


def test_a_shared_root_is_refused_because_it_would_move_another_map():
    """Maps 0 and 2 resolve to one root, and that root is refused for both.

    The fixture gives the shared root a count of 0 - the shape every one of the
    canonical image's 11 shared roots has - so the corpus still loads and the refusal
    is about the sharing rather than about a malformed image.
    """
    from tests.unit.test_map_transitions import ROOT_BASE, SOURCE_BASE

    image = bytearray(image_bytes([[], [], []]))
    image[SOURCE_BASE + 2 * 8 : SOURCE_BASE + 2 * 8 + 4] = (
        GBA_BASE + ROOT_BASE
    ).to_bytes(4, "little")
    shared = bytes(image)
    profile = profile_for(shared)
    corpus = read_map_transitions(shared, profile)
    assert corpus.root_for(MapIdentity(0)).root_address == corpus.root_for(
        MapIdentity(2)
    ).root_address
    assert corpus.shared_root_maps(MapIdentity(0)) == (MapIdentity(2),)
    assert corpus.shared_root_maps(MapIdentity(2)) == (MapIdentity(0),)
    with pytest.raises(TransitionFieldError, match="shared with map:0002"):
        materialize_transition_creations(
            shared,
            {NEW_DOOR: authored_for(shared, request(), priors=(0, 0))},
            profile=profile,
        )
    # A control: an unshared map with no record of its own is refused for the
    # template rather than for sharing, so the sharing refusal above is the sharing.
    orphan = request(
        name="orphan", source=MapIdentity(2),
        template=TransitionIdentity(MapIdentity(2), 0),
    )
    with pytest.raises(TransitionFieldError, match="does not contain"):
        materialize_transition_creations(
            image_bytes(),
            {orphan.identity: authored_for(image_bytes(), orphan, priors=(0, 0))},
            profile=profile_for(image_bytes()),
        )


def test_a_template_whose_facing_byte_drifted_is_refused():
    image = image_bytes()
    authored = authored_for(image, request())
    drifted = AuthoredTransitionCreation(
        creation=authored.creation,
        prior_facing_raw=TEMPLATE_FACING_RAW ^ 0x01,
        prior_unresolved_raw=TEMPLATE_BYTE_0X13,
    )
    with pytest.raises(TransitionFieldError, match=r"\+0x10"):
        materialize_transition_creations(
            image, {NEW_DOOR: drifted}, profile=profile_for(image)
        )


def test_a_template_whose_tail_byte_drifted_is_refused():
    image = image_bytes()
    authored = authored_for(image, request())
    drifted = AuthoredTransitionCreation(
        creation=authored.creation,
        prior_facing_raw=TEMPLATE_FACING_RAW,
        prior_unresolved_raw=1,
    )
    with pytest.raises(TransitionFieldError, match=r"\+0x13"):
        materialize_transition_creations(
            image, {NEW_DOOR: drifted}, profile=profile_for(image)
        )


def test_an_unknown_destination_is_refused():
    image = image_bytes()
    with pytest.raises(TransitionFieldError):
        materialize(image, request(destination=MapIdentity(9)))


def test_an_arrival_off_the_destination_map_is_refused():
    image = image_bytes()
    # The synthetic root's extent word is zero, so the destination is 241x161 px.
    with pytest.raises(TransitionFieldError, match="off the map"):
        materialize(image, request(arrival=TransitionArrival(5000, 8)))


def test_an_unordered_or_degenerate_region_never_reaches_a_plan():
    with pytest.raises(MapTransitionRegionError):
        TransitionRegion(first=(10, 10), second=(0, 4))
    with pytest.raises(MapTransitionRegionError):
        TransitionRegion(first=(10, 4), second=(0, 4))


def test_a_count_that_cannot_grow_is_refused(monkeypatch):
    """The 4-byte count at root+0x40 is checked, not truncated.

    The ceiling is lowered rather than the image's count raised, because a count
    above the array's real length would be refused as a malformed corpus before the
    creation ever ran - so this is the only way to reach the overflow branch at all.
    """
    import tools.webfoot.map_transitions as authority

    monkeypatch.setattr(authority, "MAX_TRANSITION_COUNT", 1)
    image = image_bytes()
    with pytest.raises(TransitionFieldError, match="overflow"):
        materialize(image, request())


def test_an_allocator_refusal_is_reported_rather_than_worked_around():
    """No generated expansion, no canonical space: the request must fail closed."""
    image = image_bytes()
    base = profile_for(image)
    assert base.generated_expansion is not None
    profile = dataclasses_replace(
        base,
        id="synthetic_transition_creation_no_expansion",
        generated_expansion=None,
    )
    with pytest.raises(InsufficientSpaceError):
        materialize_transition_creations(
            image, {NEW_DOOR: authored_for(image, request())}, profile=profile
        )


def test_canonical_free_space_is_not_used_even_when_it_would_fit():
    """`EXPANDED_ONLY` is a policy, not a preference: first fit is never consulted.

    The profile here declares 1 KiB of canonical VERIFIED_FREE space - far more than
    the 24-byte record plus a 12-byte array need - and the domain must still place
    both above canonical EOF, leaving those canonical bytes untouched.
    """
    from tools.webfoot.layout import FileOffset, FreeRegion, RomRange

    image = image_bytes()
    free = FreeRegion(
        RomRange(FileOffset(0x6000), 0x400), "synthetic canonical free space"
    )
    profile = dataclasses_replace(profile_for(image), free_regions=(free,))
    result = materialize_transition_creations(
        image, {NEW_DOOR: authored_for(image, request())}, profile=profile
    )
    for allocation in result.generated_allocations:
        assert not allocation.allocated_range.overlaps(free.range)
        assert allocation.allocated_range.start.value >= IMAGE_SIZE
    output = build(image, result)
    assert output[0x6000:0x6400] == image[0x6000:0x6400]


# --- persistence --------------------------------------------------------------


def test_a_creation_survives_save_reopen_and_build(tmp_path):
    """M6 - dropping the authored identity on reopen fails here."""
    image = image_bytes()
    project = project_at(tmp_path)
    changed = set_transition_creations(
        project, profile_for(image), image, {NEW_DOOR: request()}
    )
    assert changed is True
    reopened = read_project_transition_creations(project)
    assert set(reopened) == {NEW_DOOR}
    assert reopened[NEW_DOOR].creation.region == AUTHORED_REGION
    assert reopened[NEW_DOOR].creation.facing == FACING_EAST
    assert reopened[NEW_DOOR].prior_facing_raw == TEMPLATE_FACING_RAW
    assert reopened[NEW_DOOR].prior_unresolved_raw == TEMPLATE_BYTE_0X13
    assert reopened[NEW_DOOR].creation.identity.key == "map:0000/transition:new-door"


def test_the_stored_priors_are_measured_from_the_image_not_the_caller(tmp_path):
    image = image_bytes()
    project = project_at(tmp_path)
    set_transition_creations(project, profile_for(image), image, {NEW_DOOR: request()})
    entry = read_project(project).transition_creations.edits()[(0, "new-door")]
    assert entry.prior_facing_raw == TEMPLATE_FACING_RAW
    assert entry.prior_unresolved_raw == TEMPLATE_BYTE_0X13


def test_reissuing_the_same_creation_is_a_no_op(tmp_path):
    image = image_bytes()
    project = project_at(tmp_path)
    assert set_transition_creations(
        project, profile_for(image), image, {NEW_DOOR: request()}
    )
    assert not set_transition_creations(
        project, profile_for(image), image, {NEW_DOOR: request()}
    )


def test_removing_a_creation_un_authors_it(tmp_path):
    image = image_bytes()
    project = project_at(tmp_path)
    set_transition_creations(project, profile_for(image), image, {NEW_DOOR: request()})
    assert remove_transition_creation(project, NEW_DOOR) is True
    assert remove_transition_creation(project, NEW_DOOR) is False
    assert not (project / TRANSITION_CREATION_FILE).exists()
    assert read_project_transition_creations(project) == {}


def test_none_removes_a_creation_in_one_batch(tmp_path):
    image = image_bytes()
    project = project_at(tmp_path)
    set_transition_creations(project, profile_for(image), image, {NEW_DOOR: request()})
    assert set_transition_creations(
        project, profile_for(image), image, {NEW_DOOR: None}
    )
    assert read_project_transition_creations(project) == {}


def test_a_batch_with_one_illegal_entry_writes_nothing(tmp_path):
    image = image_bytes()
    project = project_at(tmp_path)
    good = request(name="good-door")
    bad = request(name="bad-door", destination=MapIdentity(9))
    with pytest.raises(TransitionFieldError):
        set_transition_creations(
            project, profile_for(image), image, {good.identity: good, bad.identity: bad}
        )
    assert not (project / TRANSITION_CREATION_FILE).exists()


def test_a_request_whose_identity_disagrees_with_its_key_is_refused(tmp_path):
    image = image_bytes()
    project = project_at(tmp_path)
    other = request(name="other")
    with pytest.raises(TransitionFieldError, match="must agree"):
        set_transition_creations(
            project, profile_for(image), image, {NEW_DOOR: other}
        )


def test_a_project_build_of_creations_is_ordered_by_name(tmp_path):
    image = image_bytes()
    project = project_at(tmp_path)
    second = request(name="b-door")
    first = request(name="a-door")
    set_transition_creations(
        project,
        profile_for(image),
        image,
        {second.identity: second, first.identity: first},
    )
    requests = read_project_transition_creations(project)
    result = materialize_transition_creations(
        image, requests, profile=profile_for(image)
    )
    assert [entry.identity for entry in result.provenance] == [
        "map:0000/transition:a-door",
        "map:0000/transition:b-door",
    ]


def test_the_creation_record_pointer_is_not_the_template_pointer():
    """A second, provenance-level statement of M4."""
    image = image_bytes()
    result = materialize(image, request())
    entry = result.provenance[0]
    assert int.from_bytes(
        bytes.fromhex(entry.record_pointer_bytes), "little"
    ) == entry.record_address
    assert entry.record_address != entry.template_address
    assert entry.record_address >= GBA_BASE + IMAGE_SIZE
