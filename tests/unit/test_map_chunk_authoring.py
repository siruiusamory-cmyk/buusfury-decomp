"""Portable tests for the chunk-authoring rules that need no image.

MAP-CHUNK-AUTHORING-001. Synthetic only: the plane composer, the container
encoder, the identity and template grammars, and the placement-key refusal are
pure functions over values, so they are pinned here where CI (which has no
canonical ROM) can run them. Everything that has to read a real layer - resolving
a template, materializing a body, writing a cell reference - lives in
``tests/integration/test_map_chunk_authoring_rom.py``.
"""

from __future__ import annotations

import pytest

from tools.webfoot import map_chunk as mc
from tools.webfoot.formats import map_graphics as mg
from tools.webfoot.formats import webfoot_lz as lz

#: A tiny permitted vocabulary. The composer only asks whether a value is in it,
#: so three entries are enough to exercise every refusal.
VOCABULARY = (0x0000, 0x0015, 0x0821)


def _plane(fill: int = 0x0000) -> tuple[int, ...]:
    return (fill,) * mg.CHUNK_ENTRY_COUNT


# --- the container -----------------------------------------------------------


def test_a_chunk_body_round_trips_through_its_container():
    plane = tuple(range(mg.CHUNK_ENTRY_COUNT))
    blob = mg.pack_dominant_chunk(plane)
    kind, declared = lz.read_header(blob, 0)
    assert kind == mg.CHUNK_CONTAINER_KIND == 1
    assert declared == mg.CHUNK_DECODED_BYTES
    container = lz.unpack(blob, 0)
    assert container.data == mg.chunk_body_bytes(plane)


def test_an_authored_container_satisfies_the_retail_termination_contract():
    """The engine's own escape must fall at the declared boundary.

    This is the postcondition CQA-02 resolved from the disassembly and the one a
    written payload has to meet, so an authored chunk is not merely decodable by
    this project's reader - it terminates the way the retail decoder requires.
    """
    blob = mg.pack_dominant_chunk(_plane(0x0015))
    container = lz.validate_retail_termination(blob, 0)
    assert container.kind == 1
    assert len(container.data) == mg.CHUNK_DECODED_BYTES


@pytest.mark.parametrize(
    "plane,message",
    [
        ((0,) * 10, "1024 screen entries"),
        ((0,) * (mg.CHUNK_ENTRY_COUNT + 1), "1024 screen entries"),
        (("x",) * mg.CHUNK_ENTRY_COUNT, "16-bit entry"),
        ((0x10000,) * mg.CHUNK_ENTRY_COUNT, "16-bit entry"),
        (b"\x00" * 4, "sequence of screen entries"),
    ],
)
def test_a_malformed_plane_is_refused(plane, message):
    with pytest.raises(mg.MapGraphicsError, match=message):
        mg.chunk_body_bytes(plane)


def test_pack_refuses_a_kind_the_format_does_not_have():
    """`pack` emits a packed container; a stored kind is a different object."""
    with pytest.raises(lz.ContainerError, match="not one of"):
        lz.pack(b"payload", kind=0)


def test_either_packed_kind_decodes_to_the_same_payload():
    """The two packed kinds share one token stream; only the header differs.

    This is the fact that lets an authored chunk be emitted in the kind every
    canonical chunk uses rather than only in the encoder's own kind.
    """
    payload = mg.chunk_body_bytes(_plane(0x0015))
    two = lz.pack(payload, kind=2)
    one = lz.pack(payload, kind=1)
    assert one[8:] == two[8:]
    assert one[:8] != two[:8]
    assert lz.unpack(one, 0).data == lz.unpack(two, 0).data == payload


# --- identity and template ---------------------------------------------------


@pytest.mark.parametrize("name", ["grass-sign", "chunk:grass-sign", "a", "a" * 64])
def test_a_valid_chunk_name_is_accepted(name):
    identity = mc.chunk_identity(name)
    assert identity.startswith("chunk:")
    assert mc.chunk_identity(identity) == identity


@pytest.mark.parametrize("name", ["", "Grass", "1grass", "has space", "a" * 65, None, 7])
def test_an_invalid_chunk_name_is_refused(name):
    with pytest.raises(mc.ChunkAuthoringError):
        mc.chunk_identity(name)


def test_a_template_round_trips_through_its_text():
    template = mc.ChunkTemplate(map_index=40, layer_slot=1, ordinal=2)
    assert template.text == "map:0040/layer:1/chunk:2"
    assert mc.ChunkTemplate.parse(template.text) == template


@pytest.mark.parametrize(
    "text", ["map:40/layer:1/chunk:1", "map:0040/BG1/chunk:1", "map:0040/layer:4/chunk:1",
             "map:0040/layer:1/chunk:0", "", None]
)
def test_an_invalid_template_is_refused(text):
    with pytest.raises(mc.ChunkAuthoringError):
        mc.ChunkTemplate.parse(text)


def test_a_template_ordinal_is_one_based():
    with pytest.raises(mc.ChunkAuthoringError, match="1-based"):
        mc.ChunkTemplate(map_index=0, layer_slot=0, ordinal=0)


# --- composing a body --------------------------------------------------------


def test_composing_applies_every_edit_and_leaves_the_rest_alone():
    template = _plane(0x0000)
    edits = (
        mc.ChunkEntryEdit(row=1, column=2, prior=0x0000, entry=0x0015),
        mc.ChunkEntryEdit(row=3, column=4, prior=0x0000, entry=0x0821),
    )
    composed = mc.compose_body(template, edits, VOCABULARY)
    assert composed[1 * 32 + 2] == 0x0015
    assert composed[3 * 32 + 4] == 0x0821
    changed = [i for i, (a, b) in enumerate(zip(template, composed)) if a != b]
    assert changed == [1 * 32 + 2, 3 * 32 + 4]


@pytest.mark.parametrize(
    "edits,match",
    [
        # A stored prior that disagrees means the chunk is not from this template.
        ((mc.ChunkEntryEdit(0, 0, prior=0x0015, entry=0x0821),),
         "not composed from this template"),
        # Authoring rearranges existing graphics; it does not add new ones.
        ((mc.ChunkEntryEdit(0, 0, prior=0x0000, entry=0x0FFF),),
         "no chunk of the template's layer"),
        ((mc.ChunkEntryEdit(32, 0, prior=0x0000, entry=0x0015),), "outside the 32x32 plane"),
        (
            (
                mc.ChunkEntryEdit(0, 0, prior=0x0000, entry=0x0015),
                mc.ChunkEntryEdit(0, 0, prior=0x0015, entry=0x0821),
            ),
            "edited twice",
        ),
    ],
    ids=[
        "a prior the template does not hold",
        "an entry outside the permitted vocabulary",
        "a cell outside the plane",
        "editing one cell twice",
    ],
)
def test_composing_refuses_an_edit_the_template_cannot_hold(edits, match):
    with pytest.raises(mc.ChunkAuthoringError, match=match):
        mc.compose_body(_plane(0x0000), edits, VOCABULARY)


@pytest.mark.parametrize("prior,entry", [(0x10000, 1), (1, -1), ("a", 1), (1, None)])
def test_composing_refuses_a_value_that_is_not_a_screen_entry(prior, entry):
    edits = (mc.ChunkEntryEdit(0, 0, prior=prior, entry=entry),)
    with pytest.raises(mc.ChunkAuthoringError, match="16-bit screen entry"):
        mc.compose_body(_plane(0x0000), edits, VOCABULARY)


def test_composing_twice_with_the_same_edits_is_deterministic():
    template = _plane(0x0000)
    edits = (mc.ChunkEntryEdit(row=5, column=6, prior=0x0000, entry=0x0015),)
    assert mc.compose_body(template, edits, VOCABULARY) == mc.compose_body(
        template, edits, VOCABULARY
    )


# --- placement legality ------------------------------------------------------


def test_a_chunk_may_only_be_placed_in_the_map_it_was_composed_against():
    """A plane holds tile ordinals, which only resolve through one map's block."""
    mc.validate_authored_placement(40, 40, 1)
    with pytest.raises(mc.ChunkAuthoringError, match="character block"):
        mc.validate_authored_placement(40, 39, 1)


def test_a_placement_layer_must_be_a_regular_background():
    with pytest.raises(mc.ChunkAuthoringError, match="BG0..BG3"):
        mc.validate_authored_placement(40, 40, 4)


@pytest.mark.parametrize(
    "key",
    [("map", 1, 0), (40, 1), (40, 1, 0, 0), (40.0, 1, 0), (40, 1, "0"), "40,1,0"],
)
def test_a_malformed_placement_key_is_the_surfaces_own_error(key):
    """A GUI boundary catches one family; unpacking must not raise outside it."""
    with pytest.raises(mc.ChunkAuthoringError):
        mc._placement_key(key)
