"""CQA-04-DECODE-STACK-AUTHORITY-001 - ROM-gated cross-stack equivalence.

The audit finding was that the two production map/graphics decode stacks were
never compared. This file is the comparison, over the canonical corpus:

* every map the SDK's narrow renderer accepts is rendered by **both** surfaces and
  the composites must be byte-identical, which is the level their contracts agree
  at (one draws only dominant chunk grids, the other classifies all five handler
  forms; identical pixels over the shared domain is what "one reader of record"
  has to mean in practice);
* a decisive disagreement between the shared reader and an independent
  raw-bytes oracle fails, so the equality above cannot be satisfied by two copies
  of the same mistake;
* the production writer's plans are re-derived from the shared reader and must
  match field-for-field, which is the writer-parity requirement;
* the intentional capability difference - the SDK renderer understanding only the
  dominant handler - is pinned as a deliberate refusal rather than left as "the
  other parser just doesn't understand it".

Run this file by name. It is ROM-gated and skips without the canonical image; it
is not part of the portable suite.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import struct

import pytest

from tools.webfoot import map_render as mr
from tools.webfoot import map_view as mv
from tools.webfoot.formats import map_entry as _ME
from tools.webfoot.formats import map_graphics as mg
from tools.webfoot.map_layout_write import MapLayoutWriter
from tools.webfoot.packaged import packaged_profile

ROM_PATH = Path(
    os.environ.get(
        "LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"
    )
)
CANONICAL_SHA256 = packaged_profile().sha256

#: Which maps to compare. Every map is the useful corpus, and the two surfaces
#: only agree on the dominant form, so the enumeration is filtered by the SDK
#: renderer's own acceptance rather than by a hand-picked list.
pytestmark = pytest.mark.skipif(
    not ROM_PATH.is_file(), reason="canonical ROM not configured locally"
)


@pytest.fixture(scope="module")
def rom() -> bytes:
    data = ROM_PATH.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA256, (
        "the configured image is not the packaged canonical profile's"
    )
    return data


@pytest.fixture(scope="module")
def reader(rom: bytes) -> mg.MapGraphicsReader:
    return mg.MapGraphicsReader(rom, packaged_profile())


# --- the raw-bytes oracle ----------------------------------------------------
#
# Deliberately independent of the shared reader: this is `test_asset_export_*`'s
# technique applied to the map side, reading the record's bytes at the offsets
# `formats.map_entry`'s layout declares, in the file the ROM actually is. It
# exists to make the equivalence assertion below discriminating rather than
# tautological.

def _raw_map_entry(rom: bytes, index: int) -> dict[str, int]:
    table = packaged_profile().map_entries
    record = table.address.raw + index * table.record_size
    offset = record - 0x08000000
    raw = rom[offset : offset + table.record_size]
    assert len(raw) == table.record_size
    return {
        "address": record,
        "key_high": raw[0x00],
        "key_low": raw[0x01],
        "text_index": struct.unpack_from("<H", raw, 0x0C)[0],
        "source_address": struct.unpack_from("<I", raw, 0x2C)[0],
        "root_address": struct.unpack_from(
            "<I", rom, struct.unpack_from("<I", raw, 0x2C)[0] - 0x08000000
        )[0],
        "chunk_x": None,
        "chunk_y": None,
        "chunk_addresses": None,
    }


def _raw_layer(rom: bytes, root_address: int, slot: int) -> dict[str, int]:
    record = struct.unpack_from(
        "<I", rom, root_address - 0x08000000 + mg.ROOT_LAYER_SLOTS[slot]
    )[0]
    handler = struct.unpack_from("<I", rom, record - 0x08000000)[0]
    chunk_x = rom[record - 0x08000000 + mg.LAYER_CHUNK_X_OFFSET]
    chunk_y = rom[record - 0x08000000 + mg.LAYER_CHUNK_Y_OFFSET]
    addresses = tuple(
        struct.unpack_from(
            "<I",
            rom,
            record - 0x08000000 + mg.LAYER_CHUNK_WINDOW_OFFSET + cell * 4,
        )[0]
        for cell in range(chunk_x * chunk_y)
    )
    return {
        "address": record,
        "handler": handler,
        "chunk_x": chunk_x,
        "chunk_y": chunk_y,
        "chunk_addresses": addresses,
    }


def test_map_entry_interpretation_matches_a_raw_bytes_oracle(rom, reader):
    """Every map row the shared reader publishes equals the record's own bytes.

    If a field's offset or width were reinterpreted in the shared reader, the two
    readings would part company on at least one of the 452 rows.
    """
    entries = mg.read_map_entries(reader)
    assert len(entries) == reader.map_entry_count()
    assert len(entries) == 452

    for index, entry in enumerate(entries):
        raw = _raw_map_entry(rom, index)
        assert entry.address == raw["address"]
        assert (entry.key_high, entry.key_low) == (
            raw["key_high"],
            raw["key_low"],
        )
        assert entry.source_address == raw["source_address"]
        assert entry.root_address == raw["root_address"]
        assert (entry.text_index or 0) == raw["text_index"]


def test_layer_interpretation_matches_a_raw_bytes_oracle(rom, reader):
    """Every layer record the shared reader publishes equals its own bytes."""
    entries = mg.read_map_entries(reader)
    compared = 0
    for entry in entries:
        for slot in range(4):
            layer = mg.read_layer(reader, entry.root_address, slot)
            raw = _raw_layer(rom, entry.root_address, slot)
            assert layer.address == raw["address"]
            assert layer.handler == raw["handler"]
            assert (layer.chunk_x, layer.chunk_y) == (
                raw["chunk_x"],
                raw["chunk_y"],
            )
            if layer.handler == mg.DOMINANT_LAYER_HANDLER:
                assert layer.chunk_addresses == raw["chunk_addresses"]
            compared += 1
    assert compared == 452 * 4


# --- cross-surface parity over the common corpus -----------------------------

@pytest.fixture(scope="module")
def corpus(rom: bytes, reader: mg.MapGraphicsReader) -> dict[str, object]:
    """One pass over every map, recording what each surface does with it.

    Built once because the renderer's full assembly is expensive and both the
    parity test and the classification test need the same answers; a shared pass
    keeps this file's cost proportional to the corpus rather than to the number of
    assertions over it.

    A map the narrow renderer turns down costs only its record reads here. The
    refusal itself is asserted once, by
    ``test_the_two_surfaces_disagree_only_about_deliberately_unrendered_forms``,
    rather than re-proved per map: rendering every refused map a second time would
    multiply this file's runtime for no additional distinct evidence.
    """
    from tools.export import map_browser as mb

    accepted: dict[int, tuple] = {}
    refused: dict[int, tuple[str, ...]] = {}
    for index in range(reader.map_entry_count()):
        entry = mg.read_map_entries(reader)[index]
        classifications = tuple(
            mg.read_layer(reader, entry.root_address, slot).classification
            for slot in range(4)
        )
        try:
            sdk = mr.render_map(rom, f"map:{index:04d}")
        except mr.MapRenderError:
            refused[index] = classifications
            continue
        export = mb.render_map(rom, index)
        accepted[index] = (
            sdk.width,
            sdk.height,
            sdk.composite,
            sdk.palette,
            {layer.bg: layer.pixels for layer in sdk.layers},
            {
                layer.slot: layer.pixels
                for layer in export.layers
                if layer.classification == "dominant"
            },
            export.width,
            export.height,
            export.composite,
            export.palette,
        )
    return {"accepted": accepted, "refused": refused}


def test_every_commonly_renderable_map_is_byte_identical_across_the_stacks(corpus):
    """Both surfaces render the shared domain to identical pixels.

    The comparison is per-layer index bytes and the composite, which is the level
    the two contracts agree at. Chrome, overlays and the palette's presentation are
    each surface's own business; the pixels a reader produces are not.
    """
    accepted = corpus["accepted"]
    for index, recorded in accepted.items():
        (
            sdk_width,
            sdk_height,
            sdk_composite,
            sdk_palette,
            sdk_layers,
            export_layers,
            export_width,
            export_height,
            export_composite,
            export_palette,
        ) = recorded
        assert sdk_width == export_width, f"map:{index:04d} width"
        assert sdk_height == export_height, f"map:{index:04d} height"
        assert sdk_composite == export_composite, f"map:{index:04d} composite"
        assert sdk_palette == export_palette, f"map:{index:04d} palette"
        assert sdk_layers == export_layers, f"map:{index:04d} layers"

    # A guard against the corpus silently becoming empty and the test passing
    # without comparing anything.
    assert len(accepted) > 300, f"only {len(accepted)} maps were comparable"


def test_the_two_surfaces_disagree_only_about_deliberately_unrendered_forms(
    rom, reader, corpus
):
    """Where the surfaces differ, the difference is this renderer's own refusal.

    The SDK renderer is proven against the dominant chunk grid and refuses any
    other handler form; the map view classifies all five and renders three. The
    audit recorded that as an unexplained parser divergence. It is classified
    here: for every map the narrow renderer turns down, both surfaces name the
    *same handler from the same reader* - so the difference is a rendering
    contract, not a second reading of the record.
    """
    from tools.export import map_browser as mb

    refused = corpus["refused"]
    assert refused, "the corpus should contain forms this renderer refuses"
    seen: dict[str, int] = {}
    for index, classifications in refused.items():
        view = mb.render_map(rom, index)
        assert tuple(item.classification for item in view.layers) == classifications
        for name in classifications:
            seen[name] = seen.get(name, 0) + 1

    # At least one refusal is the renderer's own policy rather than an
    # unclassifiable record, so the difference is shown to be deliberate.
    assert any(
        name in seen
        for name in ("static_graphical_terrain_field", "static_graphical_screenblock")
    ), seen
    assert set(seen) <= {
        "dominant",
        "static_graphical_screenblock",
        "static_graphical_terrain_field",
        "absent_placeholder",
        "unclassified_handler",
        "dominant_zero_grid",
        "dominant_partial_zero_grid",
    }
    # And proven on one map, since the refusal is a raise.
    first = next(iter(refused))
    with pytest.raises(mr.MapRenderError):
        mr.render_map(rom, f"map:{first:04d}")


def test_map_19s_terrain_field_is_understood_and_deliberately_not_authored(rom, reader):
    """The audit's named example, classified rather than left unexplained.

    The terrain-field layer form is decoded by the shared reader - its handler,
    its cell grid, its container run - and rendered by the map view. What it is
    *not* is editable: the layout writer's one write operation is a four-byte
    dominant-layer chunk-pointer cell, and a terrain field has no such window. So
    the layout/Objects surface refusing such a map is the renderer's and the
    editor's declared contract, not a parser that does not understand the record.
    """
    target = None
    for index in range(reader.map_entry_count()):
        entry = mg.read_map_entries(reader)[index]
        for slot in range(4):
            layer = mg.read_layer(reader, entry.root_address, slot)
            if layer.classification == "static_graphical_terrain_field":
                target = (index, slot, layer)
                break
        if target is not None:
            break

    assert target is not None, "the canonical corpus is expected to use this form"
    index, slot, layer = target
    assert layer.handler == mg.TERRAIN_FIELD_LAYER_HANDLER
    assert layer.terrain_x > 0 and layer.terrain_y > 0
    assert layer.terrain_cells == layer.terrain_x * layer.terrain_y

    # The reader supplies the containers, and the view renders them.
    containers = mg.read_terrain_field_cells(reader, layer.address)
    assert len(containers) == layer.terrain_cells
    view = mv.render_map(reader.data, index, profile=reader.profile)
    rendered = [item for item in view.layers if item.slot == slot]
    assert rendered and rendered[0].pixels
    assert any("terrain-field" in warning for warning in view.warnings)

    # The writer refuses the same slot by name, which is the deliberate limit.
    from tools.webfoot.map_layout_write import MapLayoutWriteError

    writer = MapLayoutWriter(reader.data)
    with pytest.raises(MapLayoutWriteError, match="not the dominant chunk form"):
        writer.chunk_pointer(index, slot, 0)


# --- the production writer's plans ------------------------------------------

def test_writer_plans_are_re_derived_from_the_shared_reader(rom, reader):
    """Every writer plan field equals the shared reader's own answer.

    The ticket requires that moving the writer off the export reader changed no
    plan. Each plan is generated by the writer and then re-derived independently
    from the shared reader's `MapEntry`/`LayerRecord`, so the plan and the
    interpretation are shown to be the same thing.
    """
    writer = MapLayoutWriter(rom)
    entries = mg.read_map_entries(reader)
    checked = 0

    for index in range(0, reader.map_entry_count(), 7):
        for slot in range(4):
            layer = mg.read_layer(reader, entries[index].root_address, slot)
            if layer.classification != "dominant" or not layer.chunk_addresses:
                continue
            for cell, pointer in enumerate(layer.chunk_addresses):
                assert writer.chunk_pointer(index, slot, cell) == pointer
                expected_offset = (
                    layer.address + mg.LAYER_CHUNK_WINDOW_OFFSET + 4 * cell
                ) - 0x08000000
                assert writer.chunk_pointer_offset(index, slot, cell) == expected_offset
                # The old bytes the plan would replace are the image's own, at the
                # offset the writer reports.
                assert (
                    rom[expected_offset : expected_offset + 4]
                    == pointer.to_bytes(4, "little")
                )
                checked += 1
    assert checked > 100, f"only {checked} cells were compared"


def test_a_supported_writer_edit_is_byte_for_byte_what_it_planned(rom, reader):
    """A planned edit writes exactly the field it named, and nothing else.

    This is the writer-parity claim in its sharpest form: build the edited image
    and every differing byte must be inside a planned span, holding the planned
    value, with the plan's offsets taken from the shared reader.
    """
    writer = MapLayoutWriter(rom)
    entries = mg.read_map_entries(reader)

    planned = 0
    for index in range(reader.map_entry_count()):
        for slot in range(4):
            layer = mg.read_layer(reader, entries[index].root_address, slot)
            if layer.classification != "dominant":
                continue
            non_null = [p for p in layer.chunk_addresses if p]
            if len(set(non_null)) < 2:
                continue
            for cell, pointer in enumerate(layer.chunk_addresses):
                replacement = next(p for p in non_null if p != pointer)
                offset = writer.chunk_pointer_offset(index, slot, cell)
                writer.set_chunk_pointer(index, slot, cell, replacement)
                edited = writer.build()
                changed = {
                    at
                    for at in range(len(rom))
                    if rom[at] != edited[at]
                }
                assert changed, "a planned change must change bytes"
                assert changed <= set(range(offset, offset + 4)), (
                    f"map:{index:04d} BG{slot} cell {cell} changed bytes outside "
                    f"the planned field"
                )
                assert edited[offset : offset + 4] == replacement.to_bytes(4, "little")
                assert writer.pending_offsets == (offset,)
                # Revert and the image is the canonical image again.
                writer.set_chunk_pointer(index, slot, cell, pointer)
                assert writer.build() == rom
                planned += 1
                break
            break
        if planned:
            break
    assert planned == 1


def test_the_canonical_rom_is_not_modified_by_this_module(rom):
    """Reading through both stacks leaves the configured image untouched."""
    before = ROM_PATH.stat()
    # A map both surfaces accept, so the read really exercises both.
    index = 40
    mr.render_map(rom, f"map:{index:04d}")
    mv.render_map(rom, index)
    after = ROM_PATH.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
    assert hashlib.sha256(ROM_PATH.read_bytes()).hexdigest() == CANONICAL_SHA256
    # The map-entry table's own width, so this file also fails if the record
    # format moved under it.
    assert _ME.MAP_ENTRY_SIZE == 0x38
