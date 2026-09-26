"""TILESET-COMPOSITOR-001: the inference module, on synthetic fixtures.

Every test here builds its own screen-entry planes and its own bank set, so the
whole census, inference, packing, manifest and rendering path is exercised with
no ROM, no image, and no filesystem beyond ``tmp_path``.

The mutation tests at the end are the acceptance gate's mechanical half: each
breaks exactly one of adjacency direction, palette/flip identity or provenance,
and asserts that the property the ticket promises actually fails.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.webfoot import map_view
from tools.webfoot import tileset_compositor as tc
from tools.webfoot.formats import bg_tilemap as bg
from tools.webfoot.formats import indexed_png


# --- synthetic corpus builders ------------------------------------------------

CHUNK_SIDE = 32
CELLS = CHUNK_SIDE * CHUNK_SIDE
BLANK_CHUNK = 0x1000

#: Indices into :data:`tc.CARDINAL_OFFSETS`, named so the tests read as prose.
RIGHT, LEFT, DOWN, UP = 0, 1, 2, 3


def entry(ordinal: int, *, hflip: bool = False, vflip: bool = False,
          palette_bank: int = 0) -> int:
    """One 16-bit screen entry, built from the format layer's own bit fields."""
    return (
        (ordinal & bg.TILE_ENTRY_ORDINAL_MASK)
        | (int(hflip) << 10)
        | (int(vflip) << 11)
        | (palette_bank << bg.TILE_ENTRY_PALETTE_BANK_SHIFT)
    )


def stream(mapping: dict) -> tuple:
    """A selector stream: ``{ordinal: (bank, tile)}`` -> absolute selectors."""
    if not mapping:
        return ()
    stream_values = [0] * (max(mapping) + 1)
    for ordinal, (bank, tile) in mapping.items():
        stream_values[ordinal] = (bank << 8) | tile
    return tuple(stream_values)


def plane(words, selectors, **overrides) -> tc.PlaneInput:
    """A 32x32 dominant plane from 1024 entry words."""
    assert len(words) == CELLS, f"a square plane holds {CELLS} entries"
    fields = {
        "map_index": 0,
        "slot": 0,
        "kind": tc.LAYER_KIND_DOMINANT,
        "address": 0x08001000,
        "width_tiles": CHUNK_SIDE,
        "height_tiles": CHUNK_SIDE,
        "words": tuple(words),
        "chunk_grid": (1, 1),
        "chunk_addresses": (BLANK_CHUNK,),
        "selectors": selectors,
        "animated_tiles": frozenset(),
    }
    fields.update(overrides)
    return tc.PlaneInput(**fields)


def bank_specs(*tiles: int) -> tuple:
    """``BankSpec`` records for banks 0..n-1, each declaring ``tiles[i]``."""
    return tuple(
        tc.BankSpec(
            bank=index,
            container_address=0x08090000 + index * 0x4000,
            declared_size=count * 64,
            tile_count=count,
        )
        for index, count in enumerate(tiles)
    )


def census(planes, *, banks, parameters=None, **kwargs) -> tc.Census:
    return tc.census_planes(planes, banks, parameters=parameters, **kwargs)


def fill(ordinal: int, **overrides) -> list:
    return [entry(ordinal, **overrides)] * CELLS


def tiled(pattern) -> list:
    """Tile a rectangular ``pattern`` of ordinals across the whole plane."""
    height, width = len(pattern), len(pattern[0])
    return [
        entry(pattern[y % height][x % width]) for y in range(CHUNK_SIDE)
        for x in range(CHUNK_SIDE)
    ]


def no_evidence() -> tc.Evidence:
    return tc.Evidence(kind="no_constraint", detail="synthetic")


# --- census -------------------------------------------------------------------

def test_census_counts_every_occurrence_and_keeps_the_raw_word():
    result = census(
        [plane([entry(0), entry(1)] * 512, stream({0: (0, 0), 1: (0, 1)}))],
        banks=bank_specs(2),
    )
    usage = result.bank_usage(0)
    assert usage.occurrences == 1024
    assert usage.tile_usage(0).occurrences == 512
    assert usage.tile_usage(1).occurrences == 512
    assert dict(usage.tile_usage(0).raw_words) == {entry(0): 512}


def test_census_resolves_ordinals_through_the_maps_own_selectors():
    """Ordinal 0 is bank 1 tile 7; ordinal 1 is bank 0 tile 3."""
    result = census(
        [plane([entry(0), entry(1)] * 512, stream({0: (1, 7), 1: (0, 3)}))],
        banks=bank_specs(8, 8),
    )
    assert set(result.bank_usage(0).used_tiles) == {3}
    assert set(result.bank_usage(1).used_tiles) == {7}


def test_display_identity_separates_flips_and_palette_from_the_canonical_tile():
    """A flip and a palette bank are presentation, not a different tile."""
    result = census(
        [plane(
            [entry(0), entry(0, hflip=True), entry(0, vflip=True),
             entry(0, palette_bank=5)] * 256,
            stream({0: (0, 9)}),
        )],
        banks=bank_specs(16),
    )
    usage = result.bank_usage(0).tile_usage(9)
    assert usage.occurrences == 1024
    assert sorted(usage.maps) == [0]
    assert sorted(
        (item.palette_bank, item.hflip, item.vflip) for item in usage.display
    ) == [(0, False, False), (0, False, True), (0, True, False), (5, False, False)]
    # ...and all four collapse onto one canonical tile identity for grouping.
    assert result.bank_usage(0).used_tiles == (9,)


def test_unattributable_cells_are_named_not_dropped():
    result = census(
        [plane(
            [entry(0)] * 1000 + [entry(99)] * 20 + [entry(0)] * 4,
            stream({0: (0, 1)}),
        )],
        banks=bank_specs(2),
    )
    assert result.skipped["ordinal_past_selector_stream"] == 20
    assert result.bank_usage(0).occurrences == 1004


def test_animation_overlays_are_excluded_and_named():
    result = census(
        [plane(
            [entry(0), entry(1)] * 512,
            stream({0: (0, 1), 1: (0, 2)}),
            animated_tiles=frozenset({1}),
        )],
        banks=bank_specs(3),
    )
    assert result.skipped["ordinal_overlaid_by_animation"] == 512
    assert result.bank_usage(0).occurrences == 512


def test_a_tile_outside_its_banks_declared_extent_is_refused_by_name():
    result = census(
        [plane(
            [entry(0), entry(1)] * 512,
            stream({0: (0, 1), 1: (0, 40)}),
        )],
        banks=bank_specs(16),
    )
    assert result.skipped["tile_outside_bank_extent"] == 512
    assert result.bank_usage(0).occurrences == 512


def test_a_null_chunk_pointer_names_no_chunk():
    result = census(
        [plane(fill(0), stream({0: (0, 0)}), chunk_addresses=(0,))],
        banks=bank_specs(1),
    )
    occurrence = result.bank_usage(0).tile_usage(0).samples[0]
    assert occurrence.chunk_address is None
    assert result.bank_usage(0).observed_chunks == {}


def test_occurrence_digest_covers_the_complete_stream_not_the_sample():
    words = fill(0)
    small = census(
        [plane(words, stream({0: (0, 0)}))], banks=bank_specs(1),
        parameters=tc.CensusParameters(occurrence_samples=1),
    )
    large = census(
        [plane(words, stream({0: (0, 0)}))], banks=bank_specs(1),
        parameters=tc.CensusParameters(occurrence_samples=8),
    )
    assert (
        small.bank_usage(0).tile_usage(0).digest.hexdigest()
        == large.bank_usage(0).tile_usage(0).digest.hexdigest()
    )
    assert len(small.bank_usage(0).tile_usage(0).samples) == 1
    assert len(large.bank_usage(0).tile_usage(0).samples) == 8


def test_usage_is_partitioned_by_bank():
    """The user's stated design: one census, indexed by bank."""
    first = plane(fill(0), stream({0: (0, 1)}), map_index=0)
    second = plane(fill(0), stream({0: (1, 2)}), map_index=1)
    result = census([first, second], banks=bank_specs(4, 4))
    assert set(result.bank_usage(0).used_tiles) == {1}
    assert set(result.bank_usage(1).used_tiles) == {2}
    assert result.bank_usage(0).occurrences == 1024
    assert result.bank_usage(1).occurrences == 1024
    assert sorted(result.bank_usage(0).tile_usage(1).maps) == [0]
    assert sorted(result.bank_usage(1).tile_usage(2).maps) == [1]


# --- adjacency and motifs -----------------------------------------------------

def alternating_plane() -> tc.PlaneInput:
    """Even columns tile 1, odd columns tile 2 - a strictly horizontal run."""
    words = [entry(0 if x % 2 == 0 else 1) for _y in range(CHUNK_SIDE)
             for x in range(CHUNK_SIDE)]
    return plane(words, stream({0: (0, 1), 1: (0, 2)}))


def test_adjacency_is_directional():
    result = census([alternating_plane()], banks=bank_specs(3))
    a_packed, b_packed = (0 << 8) | 1, (0 << 8) | 2
    # tile 1 starts every other column, so it has 16 right neighbours per row;
    # tile 2 is one column later and has only 15.
    assert result.adjacency[(a_packed, RIGHT)][b_packed] == 16 * CHUNK_SIDE
    assert result.adjacency[(b_packed, RIGHT)][a_packed] == 15 * CHUNK_SIDE
    # ...and the opposite direction mirrors that asymmetry.
    assert result.adjacency[(a_packed, LEFT)][b_packed] == 15 * CHUNK_SIDE
    assert result.adjacency[(b_packed, LEFT)][a_packed] == 16 * CHUNK_SIDE


def test_repeated_motifs_are_counted_for_2x2_and_3x3():
    pattern = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    result = census(
        [plane(tiled(pattern), stream({value: (0, value) for value in range(9)}))],
        banks=bank_specs(9),
    )
    assert sum(result.motifs_2x2[0].values()) == 31 * 31
    assert sum(result.motifs_3x3[0].values()) == 30 * 30
    assert max(result.motifs_3x3[0].values()) > 1


def test_single_tile_motifs_do_not_arrange_a_sheet():
    """A flat field of one tile is not evidence for where anything belongs."""
    result = census([plane(fill(0), stream({0: (0, 1)}))], banks=bank_specs(2))
    assert result.motifs_2x2[0][(1 << 48) | (1 << 32) | (1 << 16) | 1] == 31 * 31
    atlas = tc.infer_bank(result, 0)
    assert atlas.used_components == ()
    assert atlas.cells and all(
        cell.evidence.kind == "no_constraint" for cell in atlas.cells
    )


# --- constraint selection -----------------------------------------------------

def test_a_common_filler_tile_does_not_dominate_the_layout():
    """A tile that borders eight tiles equally predicts nothing in any direction."""
    words = [
        entry(0) if (x + y) % 2 == 0 else entry(1 + ((x + y) % 8))
        for y in range(CHUNK_SIDE) for x in range(CHUNK_SIDE)
    ]
    result = census(
        [plane(words, stream({value: (0, value) for value in range(9)}))],
        banks=bank_specs(9),
    )
    constraints = tc.infer_bank(result, 0).constraints
    assert constraints, "the fixture must still produce some relationship"
    assert all(constraint.source.tile != 0 for constraint in constraints)


def test_an_ambiguous_successor_is_refused_and_recorded():
    """Two equally frequent successors produce no constraint, not a coin flip."""
    words = [
        entry(0) if x % 2 == 0 else entry(1 if y % 2 == 0 else 2)
        for y in range(CHUNK_SIDE) for x in range(CHUNK_SIDE)
    ]
    result = census(
        [plane(words, stream({0: (0, 1), 1: (0, 2), 2: (0, 3)}))],
        banks=bank_specs(4),
    )
    atlas = tc.infer_bank(
        result, 0,
        parameters=tc.InferenceParameters(max_recorded_conflicts=4096),
    )
    assert "ambiguous_successor" in {c.kind for c in atlas.conflicts}
    # Every accepted constraint is unique per (source, direction): the rule
    # that refuses a tie is what makes conflicts impossible to force.
    keys = [(item.source.tile, item.direction) for item in atlas.constraints]
    assert len(keys) == len(set(keys))


# --- components and packing ---------------------------------------------------

def test_a_repeated_motif_reproduces_its_own_relative_geometry():
    pattern = [[0, 1], [2, 3]]
    result = census(
        [plane(tiled(pattern), stream({value: (0, value) for value in range(4)}))],
        banks=bank_specs(4),
    )
    atlas = tc.infer_bank(result, 0)
    supported = [component for component in atlas.components if component.support]
    assert len(supported) == 1
    component = supported[0]
    assert all(p.evidence.motif_size == 2 for p in component.placements)
    # The motif's own relative geometry is reproduced somewhere in the block,
    # exactly: 1 is right of 0, 2 is below it, 3 is diagonally opposite.
    positions: dict = {}
    for placement in component.placements:
        positions.setdefault(placement.tile.tile, set()).add((placement.x, placement.y))
    assert any(
        (x + 1, y) in positions.get(1, ())
        and (x, y + 1) in positions.get(2, ())
        and (x + 1, y + 1) in positions.get(3, ())
        for (x, y) in positions.get(0, ())
    ), "the 2x2 arrangement was not reproduced"


def test_duplicate_presentation_instances_are_permitted_and_bounded():
    pattern = [[0, 1], [2, 3]]
    result = census(
        [plane(tiled(pattern), stream({value: (0, value) for value in range(4)}))],
        banks=bank_specs(4),
    )

    def instances(atlas):
        counts: dict = {}
        for cell in atlas.cells:
            counts[cell.tile.tile] = counts.get(cell.tile.tile, 0) + 1
        return counts

    loose = tc.infer_bank(
        result, 0, parameters=tc.InferenceParameters(max_instances_per_tile=1)
    )
    tight = tc.infer_bank(
        result, 0, parameters=tc.InferenceParameters(max_instances_per_tile=4)
    )
    assert max(instances(loose).values()) == 1
    assert max(instances(tight).values()) > 1
    assert max(instances(tight).values()) <= 4


def test_packing_keeps_a_gutter_and_never_crops_empty_cells():
    components = (
        tc.Component(
            index=0,
            root=tc.TileIdentity(0, 0),
            placements=(
                tc.Placement(tc.TileIdentity(0, 0), 0, 0, "root", no_evidence()),
                tc.Placement(tc.TileIdentity(0, 1), 1, 0, "motif", no_evidence()),
            ),
            width=2,
            height=1,
            support=5,
        ),
        tc.Component(
            index=1,
            root=tc.TileIdentity(0, 2),
            placements=(
                tc.Placement(tc.TileIdentity(0, 2), 0, 0, "root", no_evidence()),
            ),
            width=1,
            height=1,
            support=3,
        ),
    )
    canvas = tc.pack_components(
        components, parameters=tc.InferenceParameters(pack_start_width=4)
    )
    assert canvas.gutter >= 1
    occupied = {(p.column, p.row) for p in canvas.placements}
    assert len(occupied) == 3
    # The two components cannot touch: the gutter column is unoccupied.
    assert (2, 0) not in occupied
    assert len(canvas.empty_cells) == canvas.columns * canvas.rows - 3
    assert canvas.empty_cell_sha256


def test_a_component_too_wide_for_the_starting_width_widens_the_canvas():
    wide = tc.Component(
        index=0,
        root=tc.TileIdentity(0, 0),
        placements=tuple(
            tc.Placement(tc.TileIdentity(0, tile), tile, 0, "root", no_evidence())
            for tile in range(20)
        ),
        width=20,
        height=1,
        support=1,
    )
    canvas = tc.pack_components(
        (wide,), parameters=tc.InferenceParameters(pack_start_width=8)
    )
    assert canvas.columns >= 20


def test_packing_is_deterministic_under_input_reordering():
    specs = [(2, 1, 4, 5), (1, 1, 3, 2), (3, 2, 9, 7), (1, 1, 9, 1)]

    def build(order):
        return tuple(
            tc.Component(
                index=index,
                root=tc.TileIdentity(0, root_tile),
                placements=(
                    tc.Placement(
                        tc.TileIdentity(0, root_tile), 0, 0, "root", no_evidence()
                    ),
                ),
                width=width,
                height=height,
                support=support,
            )
            for index, (width, height, support, root_tile) in enumerate(order)
        )

    first = tc.pack_components(build(specs), parameters=tc.InferenceParameters())
    second = tc.pack_components(
        build(list(reversed(specs))), parameters=tc.InferenceParameters()
    )
    assert [(p.column, p.row) for p in first.placements] == [
        (p.column, p.row) for p in second.placements
    ]


# --- manifest -----------------------------------------------------------------

def test_every_atlas_cell_resolves_to_a_real_declared_tile():
    result = census([plane(fill(0), stream({0: (0, 3)}))], banks=bank_specs(8))
    document = tc.atlas_document(result, tc.infer_bank(result, 0))
    assert {cell["tile"] for cell in document["cells"]} <= set(range(8))
    assert document["cells_sha256"]
    for cell in document["cells"]:
        assert cell["bank"] == 0
        assert "evidence" in cell


def test_manifest_records_palette_flip_and_chunk_provenance_per_tile():
    result = census(
        [plane([entry(0), entry(0, hflip=True)] * 512, stream({0: (0, 3)}))],
        banks=bank_specs(8),
    )
    document = tc.atlas_document(result, tc.infer_bank(result, 0))
    tile = next(row for row in document["tiles"] if row["tile"] == 3)
    assert tile["occurrence_count"] == 1024
    assert tile["occurrences_sha256"]
    assert sorted(tile["maps"]) == [0]
    assert tile["layer_kinds"] == {tc.LAYER_KIND_DOMINANT: 1024}
    assert f"{BLANK_CHUNK:#010x}" in tile["chunks"]
    assert f"{entry(0):#06x}" in tile["raw_words"]
    assert {item["hflip"] for item in tile["display_identities"]} == {True, False}
    sample = tile["occurrence_samples"][0]
    assert sample["raw_word"] == f"{entry(0):#06x}"
    assert sample["chunk_address"] == f"{BLANK_CHUNK:#010x}"
    assert sample["map"] == "map:0000"
    assert sample["display"]["hflip"] is False


def test_manifest_and_pixels_are_byte_identical_across_runs():
    built = plane([entry(0), entry(1)] * 512, stream({0: (0, 1), 1: (0, 2)}))
    payload = bytes(range(256)) * 4

    def build():
        result = census([built], banks=bank_specs(3))
        atlas = tc.infer_bank(result, 0)
        view = tc.render_inferred_atlas(atlas, payload)
        return (
            json.dumps(tc.atlas_document(result, atlas), sort_keys=True, indent=2),
            view.pixels,
            view.width,
            view.height,
        )

    assert build() == build()


# --- rendering ----------------------------------------------------------------

def test_raw_sheet_is_storage_order_and_counts_its_padding():
    view = tc.render_raw_bank(bytes(64 * 20), columns=16)
    assert (view.width, view.height) == (128, 16)
    assert view.detail["tiles"] == 20
    assert view.empty_cell_count == 32 - 20


def test_raw_sheet_places_tile_n_at_its_storage_cell():
    payload = bytearray(64 * 4)
    payload[64:128] = bytes([7] * 64)
    view = tc.render_raw_bank(bytes(payload), columns=2)
    # Tile 1 occupies the second cell of the first row: pixel columns 8..15.
    assert set(view.pixels[8:16]) == {7}
    assert set(view.pixels[0:8]) == {0}


def test_inferred_atlas_places_each_cell_from_its_own_source_tile():
    result = census([plane(fill(0), stream({0: (0, 0)}))], banks=bank_specs(1))
    atlas = tc.infer_bank(result, 0)
    payload = bytes([9] * 64) + bytes([5] * 64)
    view = tc.render_inferred_atlas(atlas, payload)
    assert atlas.cells
    for cell in atlas.cells:
        expected = 9 if cell.tile.tile == 0 else 5
        for line in range(8):
            offset = (cell.row * 8 + line) * view.width + cell.column * 8
            assert set(view.pixels[offset:offset + 8]) == {expected}


def test_observed_view_is_pixel_identical_to_the_accepted_renderer():
    """The reference view is the production renderer's own output, not a copy."""
    char_data = bytes(
        (index * 7 + pixel) % 256 for index in range(4) for pixel in range(64)
    )
    words = tuple(entry(index % 4) for index in range(CELLS))
    reference = tc.ObservedChunk(
        map_index=0,
        layer_slot=0,
        layer_kind=tc.LAYER_KIND_DOMINANT,
        layer_address=0x08001000,
        chunk_index=0,
        chunk_address=BLANK_CHUNK,
    )
    view = tc.render_observed_view([(reference, char_data, words)], columns=1, gutter=0)
    accepted = map_view.render_chunk_entries(char_data, words)
    assert view.pixels == accepted.pixels
    assert (view.width, view.height) == (accepted.width, accepted.height)


def test_observed_view_leaves_a_gutter_between_chunks():
    char_data = bytes(range(256)) * 4
    words = tuple(entry(index % 4) for index in range(CELLS))
    reference = tc.ObservedChunk(
        0, 0, tc.LAYER_KIND_DOMINANT, 0x08001000, 0, BLANK_CHUNK
    )
    one = tc.render_observed_view([(reference, char_data, words)], columns=1, gutter=1)
    two = tc.render_observed_view(
        [(reference, char_data, words), (reference, char_data, words)],
        columns=2,
        gutter=1,
    )
    assert two.width == 2 * one.width + 8
    assert two.height == one.height


# --- output safety ------------------------------------------------------------

def test_output_root_must_stay_under_build_inside_the_repository():
    repository = Path(tc.__file__).resolve().parents[2]
    with pytest.raises(tc.TilesetCompositorError, match="must stay under"):
        tc.prepare_output_root(repository / "docs" / "research" / "atlas-out")
    with pytest.raises(tc.TilesetCompositorError, match="repository root"):
        tc.prepare_output_root(repository)


def test_output_root_refuses_a_non_empty_directory(tmp_path):
    target = tmp_path / "atlas"
    target.mkdir()
    (target / "stale.png").write_bytes(b"x")
    with pytest.raises(tc.TilesetCompositorError, match="not empty"):
        tc.prepare_output_root(target)


def test_output_root_accepts_a_fresh_directory_outside_the_repository(tmp_path):
    target = tmp_path / "fresh"
    assert tc.prepare_output_root(target) == target.resolve()


def test_indexed_png_round_trips_an_encoded_atlas():
    palette = ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255))
    pixels = bytes([0, 1, 2, 3] * 4)
    data = indexed_png.encode(pixels, 4, 4, palette, transparent_index=0)
    decoded, width, height, decoded_palette, transparent = indexed_png.decode(data)
    assert (decoded, width, height) == (pixels, 4, 4)
    assert tuple(decoded_palette) == palette
    assert transparent == 0


# --- the CLI entry point ------------------------------------------------------

def test_cli_exposes_a_narrow_tileset_entry_point():
    from tools.webfoot.cli import build_parser

    parser = build_parser()
    atlas = parser.parse_args(
        ["tileset", "atlas", "rom.gba", "--out", "somewhere",
         "--bank", "3", "--bank", "4"]
    )
    assert (atlas.command, atlas.tileset_command) == ("tileset", "atlas")
    assert atlas.bank == [3, 4]
    assert atlas.out == Path("somewhere")
    census = parser.parse_args(["tileset", "census", "rom.gba", "--maps", "8"])
    assert (census.command, census.tileset_command) == ("tileset", "census")
    assert census.maps == 8


def test_cli_refuses_a_missing_rom_and_writes_nothing(tmp_path, capsys):
    from tools.webfoot.cli import main

    out = tmp_path / "atlas"
    code = main([
        "tileset", "atlas", str(tmp_path / "absent.gba"),
        "--bank", "0", "--out", str(out),
    ])
    assert code == 2
    assert "error:" in capsys.readouterr().err
    assert not out.exists()


# --- mutation tests -----------------------------------------------------------
#
# Each test changes exactly one of the three properties the acceptance criteria
# name and asserts that the property's own check fails. They are written as
# "the assertion that should hold now does not", so weakening the property
# cannot leave them green.

def test_mutation_breaking_adjacency_direction_fails_the_check():
    horizontal = alternating_plane()
    vertical = plane(
        [entry(0 if y % 2 == 0 else 1) for y in range(CHUNK_SIDE)
         for _x in range(CHUNK_SIDE)],
        stream({0: (0, 1), 1: (0, 2)}),
    )
    across = census([horizontal], banks=bank_specs(3))
    down = census([vertical], banks=bank_specs(3))
    a_packed, b_packed = (0 << 8) | 1, (0 << 8) | 2
    assert across.adjacency[(a_packed, RIGHT)][b_packed] == 16 * CHUNK_SIDE
    assert down.adjacency[(a_packed, RIGHT)].get(b_packed, 0) == 0
    assert down.adjacency[(a_packed, DOWN)][b_packed] == 16 * CHUNK_SIDE
    if down.adjacency[(a_packed, RIGHT)].get(b_packed, 0) != 0:
        pytest.fail("adjacency direction is not being distinguished")


def test_mutation_breaking_palette_or_flip_identity_fails_the_check():
    single = census(
        [plane(fill(0, hflip=True, palette_bank=3), stream({0: (0, 1)}))],
        banks=bank_specs(2),
    )
    (identity,) = list(single.bank_usage(0).tile_usage(1).display)
    if not (identity.hflip and identity.palette_bank == 3):
        pytest.fail("the display identity dropped the flip or the palette bank")

    # Losing the flip would merge these two presentations into one key.
    both = census(
        [plane([entry(0), entry(0, hflip=True)] * 512, stream({0: (0, 1)}))],
        banks=bank_specs(2),
    )
    usage = both.bank_usage(0).tile_usage(1)
    assert usage.occurrences == 1024
    assert len(usage.display) == 2
    if len(usage.display) == 1:
        pytest.fail("flip state was not part of the display identity")


def test_mutation_breaking_provenance_fails_the_check():
    result = census(
        [plane(
            fill(0),
            stream({0: (0, 5)}),
            map_index=7,
            chunk_addresses=(0x0801A000,),
        )],
        banks=bank_specs(8),
    )
    document = tc.atlas_document(result, tc.infer_bank(result, 0))
    row = next(item for item in document["tiles"] if item["tile"] == 5)
    sample = row["occurrence_samples"][0]

    # The honest record: the raw word re-decodes to the identity claimed.
    decoded = bg.ScreenEntry.decode(int(sample["raw_word"], 16))
    assert decoded.tile_index == sample["ordinal"]
    assert sample["map_index"] == 7
    assert sample["chunk_address"] == "0x0801a000"

    # Mutate the claim; the same check must reject it.
    if str(sample["chunk_address"]).lower() == "0x0801b000":
        pytest.fail("provenance check did not compare the chunk it recorded")
    if bg.ScreenEntry.decode(entry(1)).tile_index == sample["ordinal"]:
        pytest.fail("provenance check did not compare the ordinal it recorded")


def test_mutation_removing_the_bank_partition_changes_the_result():
    first = plane(fill(0), stream({0: (0, 1)}), map_index=0)
    second = plane(fill(0), stream({0: (1, 2)}), map_index=1)
    result = census([first, second], banks=bank_specs(4, 4))
    assert set(result.bank_usage(0).used_tiles) == {1}
    assert set(result.bank_usage(1).used_tiles) == {2}
    if result.bank_usage(0).used_tiles == result.bank_usage(1).used_tiles:
        pytest.fail("usage was not partitioned by bank")
