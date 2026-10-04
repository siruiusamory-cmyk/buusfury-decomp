"""SPRITE-NEW-ATTACHMENT-CORE-001: the map-actor attachment planner, portably.

Everything here runs over synthetic bytes: a fabricated image holding a
four-record MapEntry table, one engine-counted object array of the supported
sibling family, a second map whose array must stay untouched, a declared
canonical free region and a declared generated expansion. That split is
deliberate. The canonical image is ROM-derived and cannot be exercised portably,
so the proof against the measured map-102 case lives in
`tests/integration/test_sprite_attachment_rom.py`; what is decided HERE is what
this ticket adds - how an appended object record is encoded, where the allocator
puts it and its re-emitted array, which canonical bytes move, and what is
refused.

Every expectation is a byte read back out of the emitted image through the same
codec the planner wrote it with, so a test that passes cannot be reading the
planner's own assumptions back to itself.
"""

from __future__ import annotations

import hashlib
import struct

import pytest

from tests.helpers import make_synthetic_rom, profile_for

from tools.webfoot import sprite_attachment as spa
from tools.webfoot.binary import FileOffset
from tools.webfoot.formats import map_entry as me
from tools.webfoot.formats import map_placements as mp
from tools.webfoot.layout import OwnedRegion, RomRange
from tools.webfoot.write import apply_plan, plan_changes

ROM_BASE = 0x08000000

ROM_SIZE = 0x8000
MAP_TABLE_OFFSET = 0x1000
MAP_TABLE_COUNT = 4
TARGET_MAP = 2
UNRELATED_MAP = 0

#: The target map's object array: records of the supported family, packed
#: contiguously from a fixed base so a 255-slot array still fits the image.
TARGET_ARRAY_OFFSET = 0x2000
TARGET_RECORD_BASE = 0x2800
#: A second map with its own array and its own single record, which no plan
#: below may touch.
UNRELATED_ARRAY_OFFSET = 0x2404
UNRELATED_RECORD = 0x2450
#: A word-aligned word that holds nothing, used to plant a second reference.
SPARE_WORD_OFFSET = 0x2500

FREE_OFFSET = 0x1800
FREE_SIZE = 0x0400
EXPANSION_SIZE = 0x20000
PADDING = 0xFF
EVIDENCE = "synthetic fixture for map-actor attachment"

FAMILY = spa.supported_family(spa.FAMILY_MAP_SIBLING)
RECORD_COUNT = 3
NEW_SPRITE_ID = 307
NEW_POSITION = (209, 580)
NEW_RETAINED_04 = 0
#: A retained pointer the records carry. Chosen outside every array layout the
#: fixtures build, so the interior-reference census cannot collide with it.
NEW_DATA_POINTER = ROM_BASE + 0x2700
NEW_BOX = spa.WanderBox(0x00C0, 0x0220, 0x0110, 0x0270)
RETAIL_BOX = (0x0148, 0x0238, 0x01A0, 0x0298)


def _address(file_offset: int) -> bytes:
    return (ROM_BASE + file_offset).to_bytes(4, "little")


def _field(name: str) -> int:
    return next(field.offset for field in me.MAP_ENTRY_LAYOUT if field.name == name)


def _write_map_entry(image: bytearray, index: int, count: int,
                     array_offset: int) -> int:
    at = MAP_TABLE_OFFSET + index * me.MAP_ENTRY_SIZE
    image[at + 0x01:at + 0x04] = bytes((1, 1, index & 0xFF))
    image[at + _field("trigger_count_raw")] = count
    image[at + _field("scripts_pointer_raw"):at + _field("scripts_pointer_raw") + 4] = \
        _address(array_offset)
    return at


def _write_sibling(image: bytearray, at: int, *, sprite_id: int,
                   position: tuple[int, int], data_pointer: int,
                   box: tuple[int, int, int, int],
                   flags: int = 0) -> None:
    """One record of the supported family, its +0x18 naming its own entry."""
    low, high = mp.encode_position(*position)
    struct.pack_into("<I", image, at + 0x00, FAMILY.factory_raw)
    struct.pack_into("<I", image, at + 0x04, flags)
    struct.pack_into("<I", image, at + 0x08, (high << 16) | low)
    struct.pack_into("<I", image, at + 0x0C, data_pointer)
    struct.pack_into("<I", image, at + 0x10, sprite_id)
    struct.pack_into("<I", image, at + 0x14, spa.SINGLE_ENTRY_TABLE_COUNT)
    struct.pack_into("<I", image, at + 0x18, ROM_BASE + at + FAMILY.entry_inline_offset)
    entry = at + FAMILY.entry_inline_offset
    struct.pack_into("<I", image, entry + 0x00, FAMILY.entry_class_raw)
    struct.pack_into("<I", image, entry + 0x04, 0x00000080)
    struct.pack_into("<4H", image, entry + 0x08, *box)


def _records(count: int = RECORD_COUNT) -> tuple[int, ...]:
    return tuple(TARGET_RECORD_BASE + index * FAMILY.record_size
                 for index in range(count))


def _world(count: int = RECORD_COUNT):
    """The synthetic image, its profile, and the entry template a caller passes."""
    records = _records(count)
    image = bytearray(make_synthetic_rom(size=ROM_SIZE))
    _write_map_entry(image, TARGET_MAP, len(records), TARGET_ARRAY_OFFSET)
    _write_map_entry(image, UNRELATED_MAP, 1, UNRELATED_ARRAY_OFFSET)
    for index, record in enumerate(records):
        image[TARGET_ARRAY_OFFSET + 4 * index:
              TARGET_ARRAY_OFFSET + 4 * index + 4] = _address(record)
        _write_sibling(image, record, sprite_id=10 + index,
                       position=(100 + index, 200),
                       data_pointer=NEW_DATA_POINTER, box=RETAIL_BOX)
    image[UNRELATED_ARRAY_OFFSET:UNRELATED_ARRAY_OFFSET + 4] = _address(UNRELATED_RECORD)
    _write_sibling(image, UNRELATED_RECORD, sprite_id=12, position=(40, 50),
                   data_pointer=NEW_DATA_POINTER, box=(1, 2, 3, 4))
    image = bytes(image)
    profile = profile_for(
        image,
        tables={"map_entries": {"address": ROM_BASE + MAP_TABLE_OFFSET,
                                "count": MAP_TABLE_COUNT,
                                "record_size": me.MAP_ENTRY_SIZE}},
        free_regions=[{"file_offset": FREE_OFFSET, "size": FREE_SIZE,
                       "status": "CONFIRMED", "evidence": EVIDENCE}],
        generated_expansion={"output_size": EXPANSION_SIZE, "padding_byte": PADDING,
                             "evidence": EVIDENCE},
    )
    template = image[records[0] + FAMILY.entry_inline_offset:
                     records[0] + FAMILY.entry_inline_offset + FAMILY.entry_size]
    return image, profile, template


def _request(image, *, template=None, position=NEW_POSITION, sprite_id=NEW_SPRITE_ID,
             box=NEW_BOX, data_pointer=NEW_DATA_POINTER, retained=NEW_RETAINED_04,
             family=spa.FAMILY_MAP_SIBLING, map_index=TARGET_MAP, count=RECORD_COUNT):
    if template is None:
        record = _records(count)[0]
        template = image[record + FAMILY.entry_inline_offset:
                         record + FAMILY.entry_inline_offset + FAMILY.entry_size]
    return spa.NewMapActor(
        map_index=map_index, family=family, sprite_id=sprite_id, position=position,
        retained_04_raw=retained, data_pointer_raw=data_pointer,
        behaviour_entry=template, wander_box=box)


def _plan(image, profile, request=None):
    return spa.plan_new_map_actor(image, None, request or _request(image),
                                  profile=profile)


def _emit(image, profile, attachment):
    generated = profile.generated_expansion.generated_image(
        len(image), tuple(a.allocated_range for a in attachment.generated_allocations))
    plan = plan_changes(image, attachment.changes, profile_id=profile.id,
                        base_sha256=profile.sha256, generated_image=generated,
                        generated_allocations=attachment.generated_allocations,
                        relocations=attachment.relocations)
    return plan, apply_plan(image, plan)


def _word(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset + 4], "little")


def _halfwords(data: bytes, offset: int, count: int) -> tuple[int, ...]:
    return struct.unpack_from(f"<{count}H", data, offset)


# --- the shape this ticket moved out of research -----------------------------


def test_the_supported_family_is_the_measured_map_sibling_shape():
    assert FAMILY.factory_raw == 0x08017DA3
    assert FAMILY.header_size == 0x1C
    assert FAMILY.entry_size == 0x10
    assert FAMILY.record_size == 0x2C
    assert FAMILY.entry_class_raw == 0x0800A7A1
    assert FAMILY.box_offset == 0x08
    assert spa.SINGLE_ENTRY_TABLE_COUNT == 1


def test_an_unsupported_family_name_is_refused():
    with pytest.raises(spa.SpriteAttachmentError, match="not a supported"):
        spa.supported_family("placement-0800fd55")


def test_only_the_one_measured_family_is_supported():
    assert sorted(spa.SUPPORTED_FAMILIES) == [spa.FAMILY_MAP_SIBLING]


# --- what the emitted image must show ----------------------------------------


def test_the_object_bound_increases_by_exactly_one():
    image, profile, _ = _world()
    attachment = _plan(image, profile)
    _, out = _emit(image, profile, attachment)
    field = MAP_TABLE_OFFSET + TARGET_MAP * me.MAP_ENTRY_SIZE + _field("trigger_count_raw")
    assert image[field] == RECORD_COUNT
    assert out[field] == RECORD_COUNT + 1
    assert attachment.actor.array_slots == RECORD_COUNT + 1


def test_the_map_entry_repoints_to_the_new_array():
    image, profile, _ = _world()
    attachment = _plan(image, profile)
    _, out = _emit(image, profile, attachment)
    field = MAP_TABLE_OFFSET + TARGET_MAP * me.MAP_ENTRY_SIZE + _field("scripts_pointer_raw")
    assert _word(out, field) == attachment.actor.array_rom_address
    assert attachment.actor.array_rom_address >= ROM_BASE + ROM_SIZE


def test_the_new_array_carries_every_existing_slot_verbatim():
    image, profile, _ = _world()
    attachment = _plan(image, profile)
    _, out = _emit(image, profile, attachment)
    new_at = attachment.actor.array_range.start.value
    old = image[TARGET_ARRAY_OFFSET:TARGET_ARRAY_OFFSET + 4 * RECORD_COUNT]
    assert out[new_at:new_at + 4 * RECORD_COUNT] == old
    assert _word(out, new_at + 4 * RECORD_COUNT) == \
        attachment.actor.record_rom_address


def test_the_new_record_carries_the_requested_sprite_id_and_position():
    image, profile, _ = _world()
    attachment = _plan(image, profile)
    _, out = _emit(image, profile, attachment)
    at = attachment.actor.record_range.start.value
    assert _word(out, at + FAMILY.sprite_id_offset) == NEW_SPRITE_ID
    low, high = mp.encode_position(*NEW_POSITION)
    assert _word(out, at + FAMILY.position_offset) == (high << 16) | low
    assert _word(out, at + FAMILY.retained_04_offset) == NEW_RETAINED_04
    assert _word(out, at + FAMILY.table_count_offset) == spa.SINGLE_ENTRY_TABLE_COUNT


def test_the_entry_word_names_the_records_own_inline_behaviour_entry():
    image, profile, _ = _world()
    attachment = _plan(image, profile)
    _, out = _emit(image, profile, attachment)
    at = attachment.actor.record_range.start.value
    entry_word = _word(out, at + FAMILY.table_entry_offset)
    assert entry_word == attachment.actor.behaviour_entry_address
    assert entry_word == attachment.actor.record_rom_address + FAMILY.entry_inline_offset
    assert entry_word == ROM_BASE + at + FAMILY.entry_inline_offset
    assert _word(out, entry_word - ROM_BASE) == FAMILY.entry_class_raw


def test_the_data_pointer_is_carried_verbatim():
    image, profile, _ = _world()
    attachment = _plan(image, profile)
    _, out = _emit(image, profile, attachment)
    at = attachment.actor.record_range.start.value
    assert _word(out, at + FAMILY.data_pointer_offset) == NEW_DATA_POINTER
    assert attachment.actor.data_pointer_raw == NEW_DATA_POINTER


def test_the_wander_box_bytes_are_the_requested_bounds():
    image, profile, _ = _world()
    attachment = _plan(image, profile)
    _, out = _emit(image, profile, attachment)
    entry = attachment.actor.behaviour_entry_address - ROM_BASE
    assert _halfwords(out, entry + FAMILY.box_offset, 4) == NEW_BOX.as_halfwords()
    template = _request(image).behaviour_entry
    assert _halfwords(template, FAMILY.box_offset, 4) == RETAIL_BOX


def test_every_existing_object_record_is_byte_identical():
    image, profile, _ = _world()
    attachment = _plan(image, profile)
    _, out = _emit(image, profile, attachment)
    for record in _records() + (UNRELATED_RECORD,):
        assert out[record:record + FAMILY.record_size] == \
            image[record:record + FAMILY.record_size]
    assert out[TARGET_ARRAY_OFFSET:TARGET_ARRAY_OFFSET + 4 * RECORD_COUNT] == \
        image[TARGET_ARRAY_OFFSET:TARGET_ARRAY_OFFSET + 4 * RECORD_COUNT]


def test_only_the_object_bound_and_the_array_field_move_canonically():
    image, profile, _ = _world()
    attachment = _plan(image, profile)
    _, out = _emit(image, profile, attachment)
    changed = {offset for offset in range(len(image)) if out[offset] != image[offset]}
    entry_at = MAP_TABLE_OFFSET + TARGET_MAP * me.MAP_ENTRY_SIZE
    bound = entry_at + _field("trigger_count_raw")
    pointer = set(range(entry_at + _field("scripts_pointer_raw"),
                        entry_at + _field("scripts_pointer_raw") + 4))
    assert changed <= ({bound} | pointer)
    assert bound in changed
    assert changed & pointer


def test_unrelated_maps_are_unchanged():
    image, profile, _ = _world()
    attachment = _plan(image, profile)
    _, out = _emit(image, profile, attachment)
    unrelated_entry = MAP_TABLE_OFFSET + UNRELATED_MAP * me.MAP_ENTRY_SIZE
    assert out[unrelated_entry:unrelated_entry + me.MAP_ENTRY_SIZE] == \
        image[unrelated_entry:unrelated_entry + me.MAP_ENTRY_SIZE]
    assert _word(out, unrelated_entry + _field("scripts_pointer_raw")) == \
        ROM_BASE + UNRELATED_ARRAY_OFFSET
    assert out[UNRELATED_ARRAY_OFFSET:UNRELATED_ARRAY_OFFSET + 4] == \
        image[UNRELATED_ARRAY_OFFSET:UNRELATED_ARRAY_OFFSET + 4]


def test_both_new_spans_are_above_canonical_eof_and_outside_the_free_region():
    image, profile, _ = _world()
    attachment = _plan(image, profile)
    assert len(attachment.reserved) == 2
    for region in attachment.reserved:
        assert region.range.start.value >= len(image)
        assert region.range.end <= EXPANSION_SIZE
        assert not region.range.overlaps(RomRange(FileOffset(FREE_OFFSET), FREE_SIZE))
    spans = {a.allocated_range for a in attachment.generated_allocations}
    assert spans == {region.range for region in attachment.reserved}


def test_the_relocation_record_names_the_field_it_rewrote():
    image, profile, _ = _world()
    attachment = _plan(image, profile)
    (relocation,) = attachment.relocations
    assert relocation.old_range == RomRange(
        FileOffset(TARGET_ARRAY_OFFSET), 4 * RECORD_COUNT)
    assert relocation.new_range == attachment.actor.array_range
    (rewrite,) = relocation.references
    assert rewrite.new_source_file_offset == (
        MAP_TABLE_OFFSET + TARGET_MAP * me.MAP_ENTRY_SIZE
        + _field("scripts_pointer_raw"))
    assert rewrite.new_target_file_offset == attachment.actor.array_range.start.value


def test_write_owners_name_the_map_they_edit():
    image, profile, _ = _world()
    attachment = _plan(image, profile)
    owners = {change.owner for change in attachment.changes}
    assert owners == {f"{spa.ARRAY_OWNER}:map-{TARGET_MAP:04d}",
                      f"{spa.RECORD_OWNER}:map-{TARGET_MAP:04d}"}
    assert all(f"map-{TARGET_MAP:04d}" in region.owner
               for region in attachment.reserved)
    assert all(f"map-{TARGET_MAP:04d}" in entry.owner
               for entry in attachment.generated_allocations)


def test_identical_input_plans_deterministically():
    image, profile, _ = _world()
    first = _plan(image, profile)
    second = _plan(image, profile)
    assert first.changes == second.changes
    assert first.actor == second.actor
    assert first.reserved == second.reserved
    _, left = _emit(image, profile, first)
    _, right = _emit(image, profile, second)
    assert left == right
    assert hashlib.sha256(left).hexdigest() == hashlib.sha256(right).hexdigest()


def test_the_plan_travels_through_the_shared_reservation_set():
    image, profile, _ = _world()
    first = _plan(image, profile)
    second = spa.plan_new_map_actor(
        image, None, _request(image, sprite_id=308), profile=profile,
        reserved=first.reserved)
    assert second.actor.record_range != first.actor.record_range
    assert not second.actor.record_range.overlaps(first.actor.record_range)
    assert not second.actor.array_range.overlaps(first.actor.array_range)


# --- refusals ----------------------------------------------------------------


def test_a_map_whose_array_holds_another_family_is_refused():
    image, profile, _ = _world()
    other = bytearray(image)
    struct.pack_into("<I", other, _records()[1], 0x080111A9)
    with pytest.raises(spa.SpriteAttachmentError, match="not the supported family"):
        _plan(bytes(other), profile)


def test_a_map_whose_array_holds_a_placement_is_refused():
    image, profile, _ = _world()
    other = bytearray(image)
    struct.pack_into("<I", other, _records()[2], mp.FACTORY_RAW)
    with pytest.raises(spa.SpriteAttachmentError, match="not the supported family"):
        _plan(bytes(other), profile)


def test_an_array_named_by_a_second_word_is_refused():
    image, profile, _ = _world()
    other = bytearray(image)
    other[SPARE_WORD_OFFSET:SPARE_WORD_OFFSET + 4] = _address(TARGET_ARRAY_OFFSET)
    with pytest.raises(spa.SpriteAttachmentError, match="is named at"):
        _plan(bytes(other), profile)


def test_a_reference_into_the_middle_of_the_array_is_refused():
    image, profile, _ = _world()
    other = bytearray(image)
    other[SPARE_WORD_OFFSET:SPARE_WORD_OFFSET + 4] = _address(TARGET_ARRAY_OFFSET + 4)
    with pytest.raises(spa.SpriteAttachmentError, match="middle of the array"):
        _plan(bytes(other), profile)


def test_a_behaviour_entry_of_the_wrong_class_is_refused():
    image, profile, template = _world()
    wrong = bytearray(template)
    struct.pack_into("<I", wrong, 0, 0x0800A223)
    with pytest.raises(spa.SpriteAttachmentError, match="class word"):
        _plan(image, profile, _request(image, template=bytes(wrong)))


def test_a_behaviour_entry_of_the_wrong_size_is_refused():
    image, profile, template = _world()
    with pytest.raises(spa.SpriteAttachmentError, match="behaviour entry"):
        _plan(image, profile, _request(image, template=template[:8]))


def test_an_inverted_wander_box_is_refused():
    with pytest.raises(spa.SpriteAttachmentError, match="inverted"):
        spa.WanderBox(0x0200, 0x0220, 0x0100, 0x0270)


def test_a_wander_box_pixel_outside_the_halfword_is_refused():
    with pytest.raises(spa.SpriteAttachmentError, match="unsigned 16-bit"):
        spa.WanderBox(0, 0, 0x10000, 0x10)


def test_a_map_without_an_object_array_is_refused():
    image, profile, _ = _world()
    other = bytearray(image)
    other[MAP_TABLE_OFFSET + TARGET_MAP * me.MAP_ENTRY_SIZE
          + _field("trigger_count_raw")] = 0
    with pytest.raises(spa.SpriteAttachmentError, match="declares no object array"):
        _plan(bytes(other), profile)


def test_a_full_object_array_is_refused():
    image, profile, _ = _world(count=spa.MAX_OBJECT_COUNT)
    with pytest.raises(spa.SpriteAttachmentError, match="cannot count"):
        _plan(image, profile, _request(image, count=spa.MAX_OBJECT_COUNT))


def test_a_retained_data_pointer_outside_the_image_window_is_refused():
    image, profile, _ = _world()
    with pytest.raises(spa.SpriteAttachmentError, match="retained data pointer"):
        _plan(image, profile, _request(image, data_pointer=0x03000000))


def test_a_zero_sprite_id_is_refused():
    image, profile, _ = _world()
    with pytest.raises(spa.SpriteAttachmentError, match="sprite id"):
        _plan(image, profile, _request(image, sprite_id=0))


def test_a_map_index_outside_the_table_is_refused():
    image, profile, _ = _world()
    with pytest.raises(spa.SpriteAttachmentError, match="outside the"):
        _plan(image, profile, _request(image, map_index=MAP_TABLE_COUNT))


def test_an_image_its_profile_does_not_describe_is_refused():
    image, profile, _ = _world()
    with pytest.raises(spa.SpriteAttachmentError, match="refusing to plan"):
        _plan(image + b"\x00", profile)


def test_an_unmodelled_request_object_is_refused():
    image, profile, _ = _world()
    with pytest.raises(spa.SpriteAttachmentError, match="NewMapActor"):
        spa.plan_new_map_actor(image, None, object(), profile=profile)


def test_planning_without_a_profile_or_an_identification_is_refused():
    image, _, _ = _world()
    with pytest.raises(spa.SpriteAttachmentError, match="verified ROM identification"):
        spa.plan_new_map_actor(image, None, _request(image))


def test_a_profile_without_a_generated_expansion_is_refused():
    image, _, _ = _world()
    profile = profile_for(image, tables={
        "map_entries": {"address": ROM_BASE + MAP_TABLE_OFFSET,
                        "count": MAP_TABLE_COUNT, "record_size": me.MAP_ENTRY_SIZE}})
    with pytest.raises(spa.SpriteAttachmentError, match="generated expansion"):
        spa.plan_new_map_actor(image, None, _request(image), profile=profile)


def test_a_profile_without_a_map_table_is_refused():
    image, _, _ = _world()
    profile = profile_for(image, generated_expansion={
        "output_size": EXPANSION_SIZE, "padding_byte": PADDING, "evidence": EVIDENCE})
    with pytest.raises(spa.SpriteAttachmentError, match="no map-entry table"):
        spa.plan_new_map_actor(image, None, _request(image), profile=profile)
