"""SPRITE-NEW-ATTACHMENT-CORE-001: the planner against the canonical image.

ROM-gated and read-only. The suite skips cleanly when the private canonical Buu's
Fury image is not configured locally, and it never writes to it: every test plans
an in-memory derivative, and one test re-hashes the file afterwards to prove that.

What only this file can establish is that the production planner reproduces the
measured map-102 case: the ten retail object records byte-identical, the object
bound 10 -> 11, the array re-emitted with all ten pointers verbatim plus the new
one, the new record carrying sprite id 307, the retained data pointer, the inline
class-0x0800A7A1 behaviour entry with the authored wander box, and the entry word
naming that entry. What the retail ENGINE does with that image is a separate,
runtime claim owned by ``docs/research/SPRITE_NEW_RUNTIME.md`` and the mGBA runs
behind it; nothing here is evidence for it.

**No ROM-derived fixture is committed.** Every number here is either read out of
the image at run time or a measured offset this repository already publishes.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot import capability
from tools.webfoot import sprite_attachment as spa
from tools.webfoot.binary import FileOffset
from tools.webfoot.formats import map_entry as me
from tools.webfoot.formats import map_placements as mp
from tools.webfoot.layout import RomRange
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.rom import identify_rom
from tools.webfoot.write import apply_plan, plan_changes

ROM_BASE = 0x08000000
CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

FAMILY = spa.supported_family(spa.FAMILY_MAP_SIBLING)

#: The map the runtime work proved, its measured object array, and the sibling
#: record the controlled actor was cloned from.
MAP_INDEX = 102
MAP_ARRAY_ADDRESS = 0x080784B4
MAP_ARRAY_COUNT = 10
DONOR_SLOT = 7
UNRELATED_MAP = 103

#: What the runtime experiment authored on that record.
NEW_SPRITE_ID = 307
NEW_POSITION = (209, 580)
NEW_BOX = spa.WanderBox(0x00C0, 0x0220, 0x0110, 0x0270)
PROVEN_ENTRY_CLASS = 0x0800A7A1


def _rom_path() -> Path:
    return Path(os.environ.get(
        "SPRITE_NEW_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    path = _rom_path()
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA256
    return data


@pytest.fixture(scope="module")
def identification(canonical_bytes):
    return identify_rom(_rom_path(), RomProfileCatalog.load("config/roms.yaml"))


@pytest.fixture(scope="module")
def profile(identification):
    return capability.require(
        identification, capability.Capability.MAP_ENTRIES,
        subsystem="map actor attachment test", check_header=True)


def _field(name: str) -> int:
    return next(field.offset for field in me.MAP_ENTRY_LAYOUT if field.name == name)


def _entry_offset(profile, index: int) -> int:
    return (profile.map_entries.address.to_file_offset(profile.size)
            + index * profile.map_entries.record_size)


def _word(image: bytes, offset: int) -> int:
    return int.from_bytes(image[offset:offset + 4], "little")


def _donor(image: bytes, profile, slot: int = DONOR_SLOT) -> int:
    """The file offset of the retail sibling record the controlled actor cloned."""
    entry = _entry_offset(profile, MAP_INDEX)
    array = _word(image, entry + _field("scripts_pointer_raw")) - ROM_BASE
    return _word(image, array + 4 * slot) - ROM_BASE


def _request(image: bytes, profile) -> spa.NewMapActor:
    donor = _donor(image, profile)
    return spa.NewMapActor(
        map_index=MAP_INDEX, family=spa.FAMILY_MAP_SIBLING,
        sprite_id=NEW_SPRITE_ID, position=NEW_POSITION,
        retained_04_raw=_word(image, donor + 0x04),
        data_pointer_raw=_word(image, donor + 0x0C),
        behaviour_entry=image[donor + 0x1C:donor + 0x2C],
        wander_box=NEW_BOX)


@pytest.fixture(scope="module")
def planned(canonical_bytes, profile):
    """One plan and one emitted image, made once for the module."""
    attachment = spa.plan_new_map_actor(canonical_bytes, None,
                                        _request(canonical_bytes, profile),
                                        profile=profile)
    generated = profile.generated_expansion.generated_image(
        len(canonical_bytes),
        tuple(a.allocated_range for a in attachment.generated_allocations))
    plan = plan_changes(
        canonical_bytes, attachment.changes, profile_id=profile.id,
        base_sha256=profile.sha256, generated_image=generated,
        generated_allocations=attachment.generated_allocations,
        relocations=attachment.relocations)
    return attachment, apply_plan(canonical_bytes, plan)


def _differing(image: bytes, output: bytes, window: int = 0x10000) -> set[int]:
    """Every canonical offset the derivative changed, in windowed comparisons."""
    differing: set[int] = set()
    for start in range(0, len(image), window):
        left = image[start:start + window]
        right = output[start:start + window]
        if left != right:
            differing.update(start + index for index in range(len(left))
                             if left[index] != right[index])
    return differing


def test_the_fixture_is_the_measured_map_102_array(canonical_bytes, profile):
    entry = _entry_offset(profile, MAP_INDEX)
    assert canonical_bytes[entry + _field("trigger_count_raw")] == MAP_ARRAY_COUNT
    assert _word(canonical_bytes, entry + _field("scripts_pointer_raw")) == \
        MAP_ARRAY_ADDRESS
    array = MAP_ARRAY_ADDRESS - ROM_BASE
    for slot in range(MAP_ARRAY_COUNT):
        target = _word(canonical_bytes, array + 4 * slot) - ROM_BASE
        assert _word(canonical_bytes, target) == FAMILY.factory_raw


def test_the_planner_appends_one_object_and_moves_no_other_canonical_byte(
        canonical_bytes, profile, planned):
    attachment, output = planned
    entry = _entry_offset(profile, MAP_INDEX)
    changed = _differing(canonical_bytes, output)
    bound = entry + _field("trigger_count_raw")
    pointer = set(range(entry + _field("scripts_pointer_raw"),
                        entry + _field("scripts_pointer_raw") + 4))
    assert changed <= ({bound} | pointer)
    assert output[bound] == MAP_ARRAY_COUNT + 1
    assert attachment.actor.array_slots == MAP_ARRAY_COUNT + 1


def test_the_ten_retail_object_records_are_byte_identical(canonical_bytes, profile,
                                                          planned):
    _, output = planned
    array = MAP_ARRAY_ADDRESS - ROM_BASE
    record_size = spa.supported_family(spa.FAMILY_MAP_SIBLING).record_size
    for slot in range(MAP_ARRAY_COUNT):
        target = _word(canonical_bytes, array + 4 * slot) - ROM_BASE
        assert output[target:target + record_size] == \
            canonical_bytes[target:target + record_size]
    assert output[array:array + 4 * MAP_ARRAY_COUNT] == \
        canonical_bytes[array:array + 4 * MAP_ARRAY_COUNT]


def test_the_new_array_pointer_is_the_reencoded_array(canonical_bytes, profile,
                                                      planned):
    attachment, output = planned
    entry = _entry_offset(profile, MAP_INDEX)
    assert _word(output, entry + _field("scripts_pointer_raw")) == \
        attachment.actor.array_rom_address
    array_at = attachment.actor.array_range.start.value
    old = canonical_bytes[MAP_ARRAY_ADDRESS - ROM_BASE:
                          MAP_ARRAY_ADDRESS - ROM_BASE + 4 * MAP_ARRAY_COUNT]
    assert output[array_at:array_at + 4 * MAP_ARRAY_COUNT] == old
    assert _word(output, array_at + 4 * MAP_ARRAY_COUNT) == \
        attachment.actor.record_rom_address


def test_the_new_record_is_the_controlled_actor_the_runtime_ran(canonical_bytes,
                                                                profile, planned):
    attachment, output = planned
    at = attachment.actor.record_range.start.value
    donor = _donor(canonical_bytes, profile)
    assert _word(output, at + 0x00) == _word(canonical_bytes, donor + 0x00)
    assert _word(output, at + 0x04) == _word(canonical_bytes, donor + 0x04)
    assert _word(output, at + 0x10) == NEW_SPRITE_ID
    assert _word(output, at + 0x14) == spa.SINGLE_ENTRY_TABLE_COUNT
    low, high = mp.encode_position(*NEW_POSITION)
    assert _word(output, at + 0x08) == (high << 16) | low
    assert _word(output, at + 0x0C) == _word(canonical_bytes, donor + 0x0C)


def test_the_entry_word_names_the_inline_behaviour_entry_with_the_authored_box(
        canonical_bytes, profile, planned):
    attachment, output = planned
    at = attachment.actor.record_range.start.value
    entry_word = _word(output, at + 0x18)
    assert entry_word == attachment.actor.behaviour_entry_address
    assert entry_word == attachment.actor.record_rom_address + 0x1C
    entry = at + 0x1C
    assert _word(output, entry) == PROVEN_ENTRY_CLASS
    assert _word(output, entry + 0x04) == _word(canonical_bytes,
                                                _donor(canonical_bytes, profile) + 0x20)
    assert tuple(int.from_bytes(output[entry + 0x08 + 2 * index:
                                        entry + 0x0A + 2 * index], "little")
                 for index in range(4)) == NEW_BOX.as_halfwords()


def test_the_relocated_array_is_a_recorded_relocation(canonical_bytes, profile,
                                                      planned):
    attachment, _ = planned
    (relocation,) = attachment.relocations
    assert relocation.old_range == RomRange(
        FileOffset(MAP_ARRAY_ADDRESS - ROM_BASE), 4 * MAP_ARRAY_COUNT)
    assert relocation.new_range == attachment.actor.array_range
    (rewrite,) = relocation.references
    assert rewrite.old_target_file_offset == MAP_ARRAY_ADDRESS - ROM_BASE
    assert rewrite.new_target_file_offset == attachment.actor.array_range.start.value


def test_unrelated_maps_are_unchanged(canonical_bytes, profile, planned):
    _, output = planned
    for index in (UNRELATED_MAP, 0, 1):
        entry = _entry_offset(profile, index)
        assert output[entry:entry + me.MAP_ENTRY_SIZE] == \
            canonical_bytes[entry:entry + me.MAP_ENTRY_SIZE]


def test_identical_input_plans_deterministically(canonical_bytes, profile):
    request = _request(canonical_bytes, profile)
    first = spa.plan_new_map_actor(canonical_bytes, None, request, profile=profile)
    second = spa.plan_new_map_actor(canonical_bytes, None, request, profile=profile)
    assert first.changes == second.changes
    assert first.actor == second.actor
    assert first.relocations == second.relocations


def test_the_verified_identification_resolves_the_same_profile(canonical_bytes,
                                                               identification,
                                                               profile, planned):
    attachment, _ = planned
    gated = spa.plan_new_map_actor(canonical_bytes, identification,
                                   _request(canonical_bytes, profile))
    assert gated.changes == attachment.changes
    assert gated.actor == attachment.actor


def test_planning_never_writes_the_canonical_image(canonical_bytes, planned):
    assert hashlib.sha256(_rom_path().read_bytes()).hexdigest() == CANONICAL_SHA256
    assert hashlib.sha256(canonical_bytes).hexdigest() == CANONICAL_SHA256
