"""SPRITE-NEW-ATTACHMENT-RUNTIME-PARITY-001: what the composition driver reads.

The runtime ticket composes its image from two production planners and takes the
attachment's parameters from the proven image's own bytes. This file pins that
last part portably: the proven image is self-describing - map 102's re-emitted
object array is one slot longer and that last slot names the authored record - so
the sprite id, position, the retained ``+0x04`` and ``+0x0C`` words, the class-A
behaviour entry and the wander box are read rather than restated, and an image
that does not carry that shape is refused instead of yielding a guess.

The world here is synthetic. The canonical composition and the emulator session
are the ticket's own evidence; what is decided HERE is that the driver's reader
recovers exactly those fields and refuses the shapes it does not model.
"""

from __future__ import annotations

import importlib.util
import struct
import sys
from pathlib import Path

import pytest

from tests.helpers import make_synthetic_rom, profile_for

from tools.webfoot.formats import map_entry as me
from tools.webfoot.formats import map_placements as mp
from tools.webfoot.sprite_attachment import WanderBox, supported_family

_ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "sprite_new_attachment_parity",
    _ROOT / "tools/research/sprite_new_attachment_parity.py")
assert _SPEC is not None and _SPEC.loader is not None
parity = importlib.util.module_from_spec(_SPEC)
# `dataclass(slots=True)` resolves annotations through `sys.modules[cls.__module__]`,
# so the module must be registered before it is executed.
sys.modules[_SPEC.name] = parity
_SPEC.loader.exec_module(parity)

ROM_BASE = 0x08000000
ROM_SIZE = 0x8000
MAP_TABLE_OFFSET = 0x1000
MAP_COUNT = 103
ARRAY_OFFSET = 0x3000
ARRAY_SLOTS = 11
RECORD_OFFSET = 0x3100

FAMILY = supported_family(parity.FAMILY)
SPRITE_ID = 307
POSITION = (209, 580)
RETAINED_04 = 0
DATA_POINTER = ROM_BASE + 0x2000
BOX = WanderBox(0x00C0, 0x0220, 0x0110, 0x0270)
EVIDENCE = "synthetic fixture for the attachment runtime driver"


def _write_record(image: bytearray, at: int) -> None:
    low, high = mp.encode_position(*POSITION)
    struct.pack_into("<I", image, at + 0x00, FAMILY.factory_raw)
    struct.pack_into("<I", image, at + 0x04, RETAINED_04)
    struct.pack_into("<I", image, at + 0x08, (high << 16) | low)
    struct.pack_into("<I", image, at + 0x0C, DATA_POINTER)
    struct.pack_into("<I", image, at + 0x10, SPRITE_ID)
    struct.pack_into("<I", image, at + 0x14, 1)
    struct.pack_into("<I", image, at + 0x18,
                     ROM_BASE + at + FAMILY.entry_inline_offset)
    entry = at + FAMILY.entry_inline_offset
    struct.pack_into("<I", image, entry, FAMILY.entry_class_raw)
    struct.pack_into("<I", image, entry + 0x04, 0x00000080)
    struct.pack_into("<4H", image, entry + 0x08, *BOX.as_halfwords())


def _world():
    """A proven-shaped image: map 102 declares 11 slots, the last is the record."""
    image = bytearray(make_synthetic_rom(size=ROM_SIZE))
    entry_at = MAP_TABLE_OFFSET + parity.MAP_INDEX * me.MAP_ENTRY_SIZE
    image[entry_at + 0x04] = ARRAY_SLOTS
    image[entry_at + 0x14:entry_at + 0x18] = (ROM_BASE + ARRAY_OFFSET).to_bytes(4, "little")
    for slot in range(ARRAY_SLOTS - 1):
        struct.pack_into("<I", image, ARRAY_OFFSET + 4 * slot,
                         ROM_BASE + 0x2000 + 0x2C * slot)
    struct.pack_into("<I", image, ARRAY_OFFSET + 4 * (ARRAY_SLOTS - 1),
                     ROM_BASE + RECORD_OFFSET)
    _write_record(image, RECORD_OFFSET)
    image = bytes(image)
    profile = profile_for(image, tables={"map_entries": {
        "address": ROM_BASE + MAP_TABLE_OFFSET, "count": MAP_COUNT,
        "record_size": me.MAP_ENTRY_SIZE}})
    return image, profile


def test_the_reader_takes_every_authored_field_from_the_image():
    image, profile = _world()
    actor = parity.reference_actor(image, profile=profile)
    assert actor["sprite_id"] == SPRITE_ID
    assert actor["position"] == list(POSITION)
    assert actor["retained_04_raw"] == RETAINED_04
    assert actor["data_pointer_raw"] == DATA_POINTER
    assert actor["wander_box"] == list(BOX.as_halfwords())
    assert actor["record_rom_address"] == f"0x{ROM_BASE + RECORD_OFFSET:08X}"
    assert actor["array_rom_address"] == f"0x{ROM_BASE + ARRAY_OFFSET:08X}"
    assert actor["entry_word"] == ROM_BASE + RECORD_OFFSET + FAMILY.entry_inline_offset
    assert actor["_behaviour_entry"] == \
        image[RECORD_OFFSET + FAMILY.entry_inline_offset:
              RECORD_OFFSET + FAMILY.entry_size + FAMILY.entry_inline_offset]


def test_the_derived_request_is_a_production_planner_request():
    """The reader's own fields are exactly what ``NewMapActor`` needs."""
    from tools.webfoot.sprite_attachment import NewMapActor

    image, profile = _world()
    actor = parity.reference_actor(image, profile=profile)
    built = NewMapActor(
        map_index=parity.MAP_INDEX, family=parity.FAMILY,
        sprite_id=actor["sprite_id"], position=tuple(actor["position"]),
        retained_04_raw=actor["retained_04_raw"],
        data_pointer_raw=actor["data_pointer_raw"],
        behaviour_entry=actor["_behaviour_entry"], wander_box=actor["_wander_box"])
    assert built.behaviour_entry[:4] == FAMILY.entry_class_raw.to_bytes(4, "little")
    # The driver imports `webfoot.*` and this test imports `tools.webfoot.*`, so the
    # two `WanderBox` classes are different objects for the same file; compare values.
    assert built.wander_box.as_halfwords() == BOX.as_halfwords()
    assert built.sprite_id == SPRITE_ID


def test_a_last_slot_of_another_family_is_refused():
    image, profile = _world()
    other = bytearray(image)
    struct.pack_into("<I", other, RECORD_OFFSET, 0x0800FD55)
    with pytest.raises(parity.AttachmentParityError, match="not the supported family"):
        parity.reference_actor(bytes(other), profile=profile)


def test_a_reference_that_is_not_eleven_slots_is_refused():
    image, profile = _world()
    other = bytearray(image)
    other[MAP_TABLE_OFFSET + parity.MAP_INDEX * me.MAP_ENTRY_SIZE + 0x04] = 10
    with pytest.raises(parity.AttachmentParityError, match="not the 11"):
        parity.reference_actor(bytes(other), profile=profile)


def test_a_reference_entry_of_another_class_is_refused():
    image, profile = _world()
    other = bytearray(image)
    struct.pack_into("<I", other, RECORD_OFFSET + FAMILY.entry_inline_offset,
                     0x0800A223)
    with pytest.raises(parity.AttachmentParityError, match="class word"):
        parity.reference_actor(bytes(other), profile=profile)


class _Start:
    def __init__(self, value):
        self.value = value


class _Range:
    def __init__(self, start):
        self.start = _Start(start)


class _PlacedActor:
    """Only the two ranges the comparability decision reads."""

    def __init__(self, record, array):
        self.record_range = _Range(record)
        self.array_range = _Range(array)


def test_the_reference_comparison_holds_only_at_the_reference_s_own_offsets():
    report = {"record_file_offset": 0x801F38, "array_file_offset": 0x801F0C}
    assert parity.actor_regions_comparable(_PlacedActor(0x801F38, 0x801F0C), report)
    assert not parity.actor_regions_comparable(_PlacedActor(0x801F40, 0x801F14), report)
    assert not parity.actor_regions_comparable(_PlacedActor(0x801F38, 0x801F14), report)
