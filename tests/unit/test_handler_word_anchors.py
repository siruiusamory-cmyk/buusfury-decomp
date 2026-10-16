"""PINMAP-07b: each module's handler word equals its profile code anchor.

Every integer is spelled here rather than read from the constant under test.
"""

from __future__ import annotations

import pytest

from tools.webfoot import map_render, placement_events, sprite_attachment
from tools.webfoot.formats import map_graphics, map_placements
from tools.webfoot.packaged import packaged_profile

HANDLER_WORDS = (
    ("factory_raw", 0x0800FD55, lambda: map_placements.FACTORY_RAW),
    ("script_dispatch_handler", 0x0800421F, lambda: map_placements.SCRIPT_DISPATCH_HANDLER),
    ("handler_0800421d", 0x0800421D,
     lambda: sorted(map_placements.HANDLERS)[0]),
    ("handler_0800424f", 0x0800424F,
     lambda: sorted(map_placements.HANDLERS)[2]),
    ("sibling_factory_08017da3", 0x08017DA3, lambda: map_placements.SIBLING_FACTORIES[0]),
    ("sibling_factory_080111a9", 0x080111A9, lambda: map_placements.SIBLING_FACTORIES[1]),
    ("dominant_layer_handler", 0x08008087, lambda: map_graphics.DOMINANT_LAYER_HANDLER),
    ("dominant_layer_handler", 0x08008087, lambda: map_render.SUPPORTED_LAYER_HANDLER),
    ("absent_layer_handler", 0x08007A41, lambda: map_graphics.ABSENT_LAYER_HANDLER),
    ("terrain_field_layer_handler", 0x080088BD,
     lambda: map_graphics.TERRAIN_FIELD_LAYER_HANDLER),
    ("sibling_factory_08017da3", 0x08017DA3, lambda: sprite_attachment.SIBLING_FACTORY_RAW),
    ("entry_class_0800a7a1", 0x0800A7A1, lambda: sprite_attachment.ENTRY_CLASS_RAW),
)


@pytest.mark.parametrize(
    "name,literal,read", HANDLER_WORDS,
    ids=[f"{index}-{row[0]}" for index, row in enumerate(HANDLER_WORDS)],
)
def test_a_handler_word_reads_the_literal_integer_it_exposed_before(name, literal, read):
    assert read() == literal
    assert packaged_profile().require_code_anchor(name).address.raw == literal


def test_the_handler_names_are_unchanged_and_keyed_by_their_addresses():
    assert sorted(map_placements.HANDLERS.values()) == [
        "handler_0800421d", "handler_0800421f", "handler_0800424f"
    ]
    assert map_placements.HANDLERS[map_placements.SCRIPT_DISPATCH_HANDLER] == (
        "handler_0800421f"
    )


def test_factory_raw_reads_the_placement_type_key():
    assert map_placements.FACTORY_RAW == 0x0800FD55
    assert packaged_profile().placement_types.factory_raw == map_placements.FACTORY_RAW


def test_the_one_dominant_handler_anchor_serves_both_consumers():
    assert map_graphics.DOMINANT_LAYER_HANDLER == 0x08008087
    assert map_render.SUPPORTED_LAYER_HANDLER == 0x08008087


def test_the_placement_event_descriptor_words_read_through_the_moved_constants():
    assert placement_events.HANDLERS is map_placements.HANDLERS
    assert placement_events.SCRIPT_DISPATCH_HANDLER is map_placements.SCRIPT_DISPATCH_HANDLER


def test_the_sprite_attachment_family_word_is_the_moved_sibling_factory():
    family = sprite_attachment.supported_family(sprite_attachment.FAMILY_MAP_SIBLING)
    assert family.factory_raw == map_placements.SIBLING_FACTORIES[0] == 0x08017DA3
