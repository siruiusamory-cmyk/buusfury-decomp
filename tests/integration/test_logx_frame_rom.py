"""Read-only ROM-gated evidence for LOGX-FRAME-001.

Only findings independently established in
``docs/research/LOGX_FRAME_PROVENANCE.md`` are asserted here: the animation
reference census and its sharing, the animation object's header and 4-byte-stride
frame-cell table, the engine's own ``16*frame + 4*direction + 4`` arithmetic, the
frame record's 8-byte header and 12-byte pieces, the graphics-word relationship,
the direction index's four compile-time values, and the full-census arithmetic.

The suite skips cleanly when the private canonical ROM is not configured and it
never writes to it.  **No ROM-derived fixtures are committed**: every expectation
here is a count, an address, an index, a field value, or a short instruction
encoding.  Nothing decoded from a container is stored.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.research import logx_frame_probe as probe

# --- independently measured constants of the canonical image -----------------

#: Section A: the animation references and their sharing.  Reference counts and
#: unique-target counts are different populations and are asserted separately.
EXPECTED_DEFINITIONS = 297
EXPECTED_ARRAY_SLOTS = 4070
EXPECTED_NON_NULL_REFERENCES = 1721
EXPECTED_NULL_SLOTS = 2349
EXPECTED_UNIQUE_ANIMATIONS = 1017
EXPECTED_SHARED_ANIMATIONS = 410
EXPECTED_MAX_ANIMATION_REUSE = 16
EXPECTED_ANIMATION_MIN = 0x083C3AC4
EXPECTED_ANIMATION_MAX = 0x086A899C
EXPECTED_ANIMATION_REUSE_HISTOGRAM = {
    1: 607, 2: 252, 3: 88, 4: 45, 5: 12, 6: 4, 8: 7, 10: 1, 16: 1,
}

#: Section E/F/H: the frame-cell table and its population.
EXPECTED_FRAME_COUNT_DISTRIBUTION = {
    1: 80, 2: 275, 3: 180, 4: 407, 5: 16, 6: 13, 7: 11, 8: 3, 9: 2,
    10: 2, 11: 24, 12: 2, 16: 2,
}
EXPECTED_FRAME_UNITS = 3415
EXPECTED_CELLS = 13660
EXPECTED_CELLS_PER_DIRECTION_INDEX = 3415
EXPECTED_NULL_CELLS = 0
EXPECTED_UNIQUE_FRAME_TARGETS = 10980
EXPECTED_SHARED_FRAME_TARGETS = 989
EXPECTED_MAX_FRAME_REUSE = 4
EXPECTED_FRAME_REUSE_HISTOGRAM = {1: 9991, 3: 287, 4: 702}
EXPECTED_DISTINCT_CELLS_PER_FRAME_UNIT = {1: 702, 2: 287, 4: 2426}

#: Section I/J: the frame records and their pieces.
EXPECTED_PIECE_COUNT_DISTRIBUTION = {1: 10959, 2: 19, 4: 2}
EXPECTED_PIECE_REFERENCES = 11005
EXPECTED_MULTI_PIECE_FRAMES = 21
EXPECTED_MAXIMUM_PIECE_COUNT = 4

#: Section N: the graphics-container relationship.  Every piece resolves.  This
#: ticket's population is *distinct container offsets reached by a piece*, which is
#: **7,390**; the figure the ROM bible used to publish, **7,355**, is exactly the
#: single-piece-frame subset of it.  EVIDENCE-RISK-DEBT-001 corrected the bible and
#: the shipping reader, so the two now state the same population; this constant was
#: already the accepted one and did not move.
EXPECTED_RESOLVED_PIECES = 11005
EXPECTED_UNRESOLVED_PIECES = 0
EXPECTED_UNIQUE_GRAPHICS_TARGETS = 7390
EXPECTED_GRAPHICS_REGION_MIN = 0x003C34D0
EXPECTED_GRAPHICS_REGION_MAX = 0x006A87A8
EXPECTED_GRAPHICS_REUSE_HISTOGRAM = {
    1: 4396, 2: 2757, 3: 69, 4: 135, 5: 6, 6: 5, 8: 10, 10: 2, 16: 6, 20: 1, 24: 3,
}

#: Section M: the packed OBJ attribute pair at piece ``+0x04``.
EXPECTED_ATTRIBUTE_SHAPES = {0: 6656, 1: 73, 2: 4276}
EXPECTED_ATTRIBUTE_SIZES = {0: 12, 1: 47, 2: 9233, 3: 1713}
EXPECTED_FLIP_HISTOGRAM = {"H=0 V=0": 8157, "H=1 V=0": 2848}
EXPECTED_DISTINCT_ATTRIBUTE_WORDS = 16
EXPECTED_CONTAINER_DECLARED_SIZES = {
    64: 8, 128: 4, 256: 47, 512: 3957, 1024: 5276, 2048: 388, 4096: 1325,
}

#: Section B/E: the exact accepted arithmetic, on one representative animation.
REPRESENTATIVE_ANIMATION = 0x0850C1DC
REPRESENTATIVE_FRAME_COUNT = 2
REPRESENTATIVE_CELLS = (
    0x0850C13C, 0x0850C164, 0x0850C18C, 0x0850C1B4,
    0x0850C150, 0x0850C178, 0x0850C1A0, 0x0850C1C8,
)
REPRESENTATIVE_TRAILERS = (0x00000001, 0x00000400)
REPRESENTATIVE_FRAME_0 = 0x0850C13C
#: The frame header is the frame's own bounding box: min_x, min_y, width, height.
REPRESENTATIVE_FRAME_0_BOUNDS = (-8, -24, 32, 32)
REPRESENTATIVE_PIECE_0 = 0x0850C144
REPRESENTATIVE_PIECE_0_FIELDS = {
    "x": -8,
    "y": -24,
    "dim_0": 32,
    "dim_1": 32,
    "attributes_raw": 0x80002000,
    "shape": 0,
    "size": 2,
    "horizontal_flip": False,
    "vertical_flip": False,
    "graphics_raw": 0x0850BBB8,
    "graphics_offset": 0x0050BBB8,
    "container_size": 1024,
}

#: A four-frame animation, so the row stride is exercised, not just the first row.
FOUR_FRAME_ANIMATION = 0x083C51C4
FOUR_FRAME_CELLS = (
    0x083C5124, 0x083C5174, 0x083C5124, 0x083C5124,
    0x083C5138, 0x083C5188, 0x083C5138, 0x083C5138,
    0x083C514C, 0x083C519C, 0x083C514C, 0x083C514C,
    0x083C5160, 0x083C51B0, 0x083C5160, 0x083C5160,
)

#: A two-piece frame and a four-piece frame, the only multi-piece shapes present.
#: Each header carries the frame's bounding box over its pieces.
TWO_PIECE_FRAME = 0x08423128
TWO_PIECE_FRAME_BOUNDS = (-8, -40, 32, 48)
TWO_PIECE_PIECES = (
    {"address": 0x08423130, "x": -8, "y": -40, "dim_0": 32, "dim_1": 32,
     "attributes_raw": 0x80002000, "graphics_raw": 0x084224E0, "container_size": 1024},
    {"address": 0x0842313C, "x": -8, "y": -8, "dim_0": 32, "dim_1": 16,
     "attributes_raw": 0x80006000, "graphics_raw": 0x0842259C, "container_size": 512},
)
FOUR_PIECE_FRAME = 0x08579890
FOUR_PIECE_FRAME_BOUNDS = (0, -80, 96, 96)
FOUR_PIECE_PIECE_BOUNDS = ((64, 64), (32, 64), (64, 32), (32, 32))

#: Section Q: the direction index is written as one of exactly four constants.
EXPECTED_DIRECTION_CONSTANTS = (
    (0x0800A8C2, 3),
    (0x0800A8C8, 2),
    (0x0800A8D2, 0),
    (0x0800A8D8, 1),
    (0x080159D4, 3),
    (0x080159DC, 2),
    (0x080159E6, 0),
    (0x080159EC, 1),
)


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    """The canonical image, read once for the whole module.

    Module scope is deliberate: the census walks thousands of packed containers,
    and the probe's per-image container table is keyed on the image object, so one
    shared ``bytes`` object keeps the whole suite to a single decode pass.  The
    determinism test below makes its own copies explicitly.
    """
    path = Path(
        os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
    )
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest().upper() == probe.CANONICAL_SHA256
    return data


# --- section A: the animation reference census --------------------------------


def test_animation_reference_census(canonical_bytes: bytes) -> None:
    census = probe.animation_reference_census(canonical_bytes)
    assert census["definitions"] == EXPECTED_DEFINITIONS
    assert census["array_slots"] == EXPECTED_ARRAY_SLOTS
    assert census["non_null_references"] == EXPECTED_NON_NULL_REFERENCES
    assert census["null_slots"] == EXPECTED_NULL_SLOTS
    assert census["unique_animation_targets"] == EXPECTED_UNIQUE_ANIMATIONS
    assert census["shared_targets"] == EXPECTED_SHARED_ANIMATIONS
    assert census["max_reuse"] == EXPECTED_MAX_ANIMATION_REUSE
    assert census["reuse_histogram"] == EXPECTED_ANIMATION_REUSE_HISTOGRAM
    assert census["malformed_targets"] == []
    assert census["all_word_aligned"] is True
    assert census["minimum_target"] == f"{EXPECTED_ANIMATION_MIN:#010x}"
    assert census["maximum_target"] == f"{EXPECTED_ANIMATION_MAX:#010x}"
    # Reference count and unique-target count are different populations.
    assert census["non_null_references"] > census["unique_animation_targets"]


def test_every_animation_target_is_a_unique_distinct_object(canonical_bytes: bytes) -> None:
    """The 1,017 targets are distinct ROM pointers, and the walk reaches each once.

    ``animation_addresses`` is itself a sorted set, so asserting sortedness of its
    output would be a tautology.  The independent check is that the *references*
    it aggregates over collapse to that many distinct targets, and that a raw
    walk of the definition run finds no target the set misses.
    """
    addresses = probe.animation_addresses(canonical_bytes)
    assert len(addresses) == EXPECTED_UNIQUE_ANIMATIONS

    raw: list[int] = []
    for definition in probe.sprite.iter_definitions(canonical_bytes):
        raw.extend(value for value in definition.array if value)
    assert len(raw) == EXPECTED_NON_NULL_REFERENCES
    assert len(set(raw)) == EXPECTED_UNIQUE_ANIMATIONS
    assert sorted(set(raw)) == addresses
    assert all(probe.in_rom(canonical_bytes, address) for address in addresses)
    assert all(address % 4 == 0 for address in addresses)


# --- sections C/E/F: the animation object ------------------------------------


def test_animation_object_layout(canonical_bytes: bytes) -> None:
    animation = probe.read_animation(canonical_bytes, REPRESENTATIVE_ANIMATION)
    assert animation.frame_count == REPRESENTATIVE_FRAME_COUNT
    assert animation.cells == REPRESENTATIVE_CELLS
    assert (animation.trailer_0_raw, animation.trailer_1_raw) == REPRESENTATIVE_TRAILERS
    assert animation.table_address == REPRESENTATIVE_ANIMATION + 4
    assert animation.table_end_address == REPRESENTATIVE_ANIMATION + 4 + 4 * len(
        REPRESENTATIVE_CELLS
    )
    assert animation.end_address == animation.table_end_address + 8
    assert animation.cell_count == 4 * animation.frame_count


def test_animation_frame_count_is_a_word_and_its_high_halfword_is_zero(
    canonical_bytes: bytes,
) -> None:
    for address in probe.animation_addresses(canonical_bytes):
        animation = probe.read_animation(canonical_bytes, address)
        assert probe.FRAME_COUNT_MIN <= animation.frame_count <= probe.FRAME_COUNT_MAX
        assert probe._u16(canonical_bytes, address + 2) == 0


def test_the_cell_arithmetic_indexes_the_record_two_dimensionally(
    canonical_bytes: bytes,
) -> None:
    """``base + 4 + 16*frame + 4*direction`` selects the cell the record holds.

    The engine expression is computed here from the raw bytes, independently of the
    ``Animation`` accessor under test, so a drift in either fails the comparison.
    """
    for address in (REPRESENTATIVE_ANIMATION, FOUR_FRAME_ANIMATION):
        animation = probe.read_animation(canonical_bytes, address)
        for frame in range(animation.frame_count):
            for direction in range(probe.ANIMATION_DIRECTIONS):
                independent = probe._u32(
                    canonical_bytes, address + 4 + 16 * frame + 4 * direction
                )
                trace = probe.cell_arithmetic_trace(
                    canonical_bytes, address, frame, direction
                )
                assert trace["flat_index"] == 4 * frame + direction
                assert int(trace["target"], 16) == independent
                assert int(trace["cell_address"], 16) == (
                    address + 4 + 16 * frame + 4 * direction
                )
                assert animation.cells[4 * frame + direction] == independent


def test_four_frame_animation_repeats_cells_across_directions(
    canonical_bytes: bytes,
) -> None:
    """A shared frame target is reached from several direction positions."""
    animation = probe.read_animation(canonical_bytes, FOUR_FRAME_ANIMATION)
    assert animation.frame_count == 4
    assert animation.cells == FOUR_FRAME_CELLS
    # Direction 0 of frames 0..3 are four distinct records; the other three
    # directions share two of them.  A *direction*-major reading of the table
    # would instead find the repeats four rows apart.
    row_starts = animation.cells[0::4]
    assert len(set(row_starts)) == 4
    for frame in range(4):
        row = animation.cells[4 * frame : 4 * frame + 4]
        assert row[0] == row[2] == row[3]
        assert len(set(row)) == 2


def test_cell_census(canonical_bytes: bytes) -> None:
    census = probe.cell_census(canonical_bytes)
    assert census["unique_animations"] == EXPECTED_UNIQUE_ANIMATIONS
    assert census["frame_units"] == EXPECTED_FRAME_UNITS
    assert census["cells"] == EXPECTED_CELLS
    assert census["non_null_cells"] == EXPECTED_CELLS
    assert census["null_cells"] == EXPECTED_NULL_CELLS
    assert census["unique_frame_targets"] == EXPECTED_UNIQUE_FRAME_TARGETS
    assert census["shared_frame_targets"] == EXPECTED_SHARED_FRAME_TARGETS
    assert census["max_frame_reuse"] == EXPECTED_MAX_FRAME_REUSE
    assert census["frame_reuse_histogram"] == EXPECTED_FRAME_REUSE_HISTOGRAM
    assert census["frame_count_distribution"] == EXPECTED_FRAME_COUNT_DISTRIBUTION
    assert census["distinct_cells_per_frame_unit"] == EXPECTED_DISTINCT_CELLS_PER_FRAME_UNIT
    # Every direction position carries the same number of cells, because the
    # engine's arithmetic multiplies the frame index by four.
    for index, bucket in census["cells_by_direction_index"].items():
        assert bucket["present"] == EXPECTED_CELLS_PER_DIRECTION_INDEX, index
        assert bucket["non_null"] == EXPECTED_CELLS_PER_DIRECTION_INDEX, index
        assert bucket["null"] == 0, index


def test_matrix_model_check(canonical_bytes: bytes) -> None:
    """Three structural facts the alternative readings would falsify."""
    check = probe.matrix_model_check(canonical_bytes)
    assert check["cell_targets"] == EXPECTED_CELLS
    assert check["cell_targets_that_are_not_rom_pointers"] == 0
    assert check["overlapping_animation_objects"] == 0
    assert check["shared_frame_targets"] == EXPECTED_SHARED_FRAME_TARGETS
    # Every shared target is reached at ONE frame index from several direction
    # indices.  Under a direction-major table a shared target would be reached at
    # one direction from several frames instead, and this would be non-zero.
    assert check["shared_targets_confined_to_one_frame_index"] == EXPECTED_SHARED_FRAME_TARGETS
    assert check["shared_targets_spanning_frame_indices"] == 0


def test_trailer_words_are_recorded_raw(canonical_bytes: bytes) -> None:
    census = probe.trailer_census(canonical_bytes)
    assert census["animations"] == EXPECTED_UNIQUE_ANIMATIONS
    assert census["trailer_0_histogram"][1] == 1006
    assert census["trailer_1_distinct"] == 21
    assert census["trailer_1_histogram"][512] == 430
    assert census["trailer_1_histogram"][1024] == 379


# --- sections I/J/K/L/M/N: frame records and pieces ----------------------------


def test_frame_record_layout(canonical_bytes: bytes) -> None:
    record = probe.read_frame(canonical_bytes, REPRESENTATIVE_FRAME_0)
    assert record.piece_count == 1
    assert record.header_bounds == REPRESENTATIVE_FRAME_0_BOUNDS
    assert record.header_bounds == record.piece_bounds
    assert record.end_address == (
        REPRESENTATIVE_FRAME_0 + probe.FRAME_HEADER_SIZE + probe.PIECE_RECORD_SIZE
    )
    piece = record.pieces[0]
    assert piece.address == REPRESENTATIVE_PIECE_0
    for field, expected in REPRESENTATIVE_PIECE_0_FIELDS.items():
        if field == "container_size":
            assert probe.container_size(canonical_bytes, piece.graphics_offset) == expected
            continue
        assert getattr(piece, field) == expected, field
    # The attribute pair decodes to the piece's own stored extents.
    assert piece.dimensions == (piece.dim_0, piece.dim_1)


def test_the_frame_header_is_the_frames_own_bounding_box(canonical_bytes: bytes) -> None:
    """Over the whole corpus, header == piece bounding box, with no exceptions."""
    census = probe.frame_bbox_census(canonical_bytes)
    assert census["frames"] == EXPECTED_UNIQUE_FRAME_TARGETS
    assert census["header_minima_match_piece_minima"] == EXPECTED_UNIQUE_FRAME_TARGETS
    assert census["header_extents_match_piece_union"] == EXPECTED_UNIQUE_FRAME_TARGETS
    assert census["header_is_the_piece_bounding_box"] == EXPECTED_UNIQUE_FRAME_TARGETS
    assert census["mismatches"] == []
    # And the two multi-piece examples really are bounding boxes, not coincidences.
    for address, bounds in (
        (TWO_PIECE_FRAME, TWO_PIECE_FRAME_BOUNDS),
        (FOUR_PIECE_FRAME, FOUR_PIECE_FRAME_BOUNDS),
    ):
        record = probe.read_frame(canonical_bytes, address)
        assert record.header_bounds == bounds, hex(address)
        assert record.piece_bounds == bounds, hex(address)
        assert record.header_bounds != record.pieces[0].dimensions


def test_frame_census(canonical_bytes: bytes) -> None:
    census = probe.frame_census(canonical_bytes)
    assert census["unique_frame_records"] == EXPECTED_UNIQUE_FRAME_TARGETS
    assert census["piece_references"] == EXPECTED_PIECE_REFERENCES
    assert census["piece_count_distribution"] == EXPECTED_PIECE_COUNT_DISTRIBUTION
    assert census["multi_piece_frames"] == EXPECTED_MULTI_PIECE_FRAMES
    assert census["maximum_piece_count"] == EXPECTED_MAXIMUM_PIECE_COUNT
    assert census["minimum_piece_count"] == 1


def test_two_piece_frame(canonical_bytes: bytes) -> None:
    record = probe.read_frame(canonical_bytes, TWO_PIECE_FRAME)
    assert record.piece_count == 2
    assert record.header_bounds == TWO_PIECE_FRAME_BOUNDS
    assert record.piece_bounds == TWO_PIECE_FRAME_BOUNDS
    assert record.end_address == TWO_PIECE_FRAME + 8 + 24
    for piece, expected in zip(record.pieces, TWO_PIECE_PIECES):
        assert piece.address == expected["address"]
        assert piece.x == expected["x"]
        assert piece.y == expected["y"]
        assert (piece.dim_0, piece.dim_1) == (expected["dim_0"], expected["dim_1"])
        assert piece.attributes_raw == expected["attributes_raw"]
        assert piece.dimensions == (piece.dim_0, piece.dim_1)
        assert piece.graphics_raw == expected["graphics_raw"]
        assert probe.container_size(canonical_bytes, piece.graphics_offset) == (
            expected["container_size"]
        )
    # The pieces are 12 bytes apart, so the second piece starts inside the first
    # piece's would-be 16-byte footprint.  The stride is measured, not assumed.
    assert record.pieces[1].address - record.pieces[0].address == probe.PIECE_RECORD_SIZE == 12


def test_four_piece_frame(canonical_bytes: bytes) -> None:
    record = probe.read_frame(canonical_bytes, FOUR_PIECE_FRAME)
    assert record.piece_count == 4
    assert record.header_bounds == FOUR_PIECE_FRAME_BOUNDS
    assert record.end_address == FOUR_PIECE_FRAME + 8 + 48
    for index, piece in enumerate(record.pieces):
        assert piece.address == FOUR_PIECE_FRAME + 8 + 12 * index
        assert piece.graphics_offset is not None
        assert probe.container_size(canonical_bytes, piece.graphics_offset) == (
            piece.dim_0 * piece.dim_1
        )
        # The header is the union, so it is larger than any single piece here.
        assert piece.dimensions == (piece.dim_0, piece.dim_1)
    assert tuple(piece.dimensions for piece in record.pieces) == FOUR_PIECE_PIECE_BOUNDS


def test_piece_census(canonical_bytes: bytes) -> None:
    census = probe.piece_census(canonical_bytes)
    assert census["piece_references"] == EXPECTED_PIECE_REFERENCES
    assert census["container_dimension_matches"] == EXPECTED_PIECE_REFERENCES
    assert census["attribute_dimension_matches"] == EXPECTED_PIECE_REFERENCES
    assert census["attribute_dimension_mismatches"] == 0
    assert census["unique_graphics_targets"] == EXPECTED_UNIQUE_GRAPHICS_TARGETS
    assert census["graphics_pointer_forms"] == {"absolute": EXPECTED_PIECE_REFERENCES}
    assert census["graphics_max_reuse"] == 24
    assert census["graphics_reuse_histogram"] == EXPECTED_GRAPHICS_REUSE_HISTOGRAM
    assert census["dimension_0_distribution"] == {8: 12, 16: 3977, 32: 5645, 64: 1371}
    assert census["dimension_1_distribution"] == {8: 8, 16: 78, 32: 9252, 64: 1667}
    assert census["container_declared_sizes"] == EXPECTED_CONTAINER_DECLARED_SIZES
    # Every piece states whole 8x8 tiles, so a stated dimension is a pixel count.
    assert all(value % 8 == 0 for value in census["dimension_0_distribution"])
    assert all(value % 8 == 0 for value in census["dimension_1_distribution"])


def test_piece_attribute_pair(canonical_bytes: bytes) -> None:
    """The packed OBJ attribute pair is stored, decodes, and is never shape 3."""
    census = probe.piece_census(canonical_bytes)
    assert census["attribute_shape_distribution"] == EXPECTED_ATTRIBUTE_SHAPES
    assert census["attribute_size_distribution"] == EXPECTED_ATTRIBUTE_SIZES
    assert census["flip_histogram"] == EXPECTED_FLIP_HISTOGRAM
    assert census["distinct_attribute_words"] == EXPECTED_DISTINCT_ATTRIBUTE_WORDS
    # Shape 3 is reserved on this hardware and no canonical piece uses it.
    assert 3 not in census["attribute_shape_distribution"]
    # Vertical flip never occurs; colour-256 always does.
    assert "V=1" not in " ".join(census["flip_histogram"])
    total = sum(EXPECTED_FLIP_HISTOGRAM.values())
    assert total == EXPECTED_PIECE_REFERENCES
    # And per piece, the decode reproduces the stored extents and a valid shape.
    for address in (REPRESENTATIVE_FRAME_0, TWO_PIECE_FRAME, FOUR_PIECE_FRAME):
        for piece in probe.read_frame(canonical_bytes, address).pieces:
            assert piece.shape < 3
            assert piece.colour_256 is True
            assert piece.dimensions == (piece.dim_0, piece.dim_1)


def test_every_piece_resolves_to_a_container_of_its_own_declared_size(
    canonical_bytes: bytes,
) -> None:
    """The joint test that makes the graphics word evidence, over the corpus."""
    checked = 0
    for address in probe.frame_addresses(canonical_bytes):
        for piece in probe.read_frame(canonical_bytes, address).pieces:
            assert piece.graphics_offset is not None
            assert probe.is_graphics_target(piece.graphics_offset)
            size = probe.container_size(canonical_bytes, piece.graphics_offset)
            assert size == piece.dim_0 * piece.dim_1
            checked += 1
    assert checked == EXPECTED_PIECE_REFERENCES


def test_graphics_pointer_census(canonical_bytes: bytes) -> None:
    census = probe.graphics_pointer_census(canonical_bytes)
    assert census["piece_references"] == EXPECTED_PIECE_REFERENCES
    assert census["resolvable"] == EXPECTED_RESOLVED_PIECES
    assert census["resolved_offset_whose_container_disagrees"] == 0
    assert census["words_that_are_not_pointers"] == 0
    assert census["unique_targets"] == EXPECTED_UNIQUE_GRAPHICS_TARGETS
    assert census["unique_targets_that_fail"] == []
    assert census["region_min"] == f"{EXPECTED_GRAPHICS_REGION_MIN:#08x}"
    assert census["region_max"] == f"{EXPECTED_GRAPHICS_REGION_MAX:#08x}"
    # The region bounds are re-derived here from the resolved offsets, so the
    # probe's constants cannot make a moved region invisible.
    resolved = sorted(
        piece.graphics_offset
        for address in probe.frame_addresses(canonical_bytes)
        for piece in probe.read_frame(canonical_bytes, address).pieces
        if piece.graphics_offset is not None
    )
    assert resolved[0] == EXPECTED_GRAPHICS_REGION_MIN
    assert resolved[-1] == EXPECTED_GRAPHICS_REGION_MAX
    assert all(offset % 4 == 0 for offset in resolved)
    assert len(set(resolved)) == EXPECTED_UNIQUE_GRAPHICS_TARGETS


def test_animation_walk_is_healthy(canonical_bytes: bytes) -> None:
    """Every animation reference resolves end to end, with no malformed record."""
    census = probe.animation_walk_census(canonical_bytes)
    assert census["animation_references"] == EXPECTED_NON_NULL_REFERENCES
    assert census["healthy_animations"] == EXPECTED_NON_NULL_REFERENCES
    assert census["malformed_animations"] == []
    assert census["malformed_cell_references"] == 0
    assert census["malformed_piece_references"] == 0
    assert census["malformed_graphics_references"] == 0
    assert census["cell_references"] == 23068
    assert census["piece_references"] == 23180
    # The two cell populations are different numbers on purpose.
    assert census["cell_references"] != EXPECTED_CELLS
    assert census["unique_frame_targets"] == EXPECTED_UNIQUE_FRAME_TARGETS


# --- section S: object extents ------------------------------------------------


def test_extent_census(canonical_bytes: bytes) -> None:
    census = probe.extent_census(canonical_bytes)
    assert census["animations"] == EXPECTED_UNIQUE_ANIMATIONS
    assert census["consecutive_animation_pairs"] == EXPECTED_UNIQUE_ANIMATIONS - 1
    assert census["animation_pairs_where_the_count_overruns_the_next_record"] == 0
    assert census["frame_records"] == EXPECTED_UNIQUE_FRAME_TARGETS
    assert census["frame_pairs_ending_exactly_where_the_next_begins"] == 9963
    assert census["frame_gap_minimum"] >= 0
    # A frame record begins exactly where 30 animations' cell tables end, so the
    # two words after those tables are that record's header, not a trailer.
    assert census["animations_whose_table_end_is_a_frame_record_start"] == 30


# --- section B/E/Q: the engine -------------------------------------------------


def test_every_quoted_instruction_matches_the_image(canonical_bytes: bytes) -> None:
    report = probe.engine_census(canonical_bytes)
    assert report["all_match"] is True
    for name, entry in report["instructions"].items():
        assert entry["matches"] is True, name
        assert entry["address"].startswith("0x")


def test_every_evidence_site_is_even_and_unique() -> None:
    addresses = [address for address, _ in probe.EVIDENCE_INSTRUCTIONS.values()]
    assert len(addresses) == len(set(addresses))
    assert all(address % 2 == 0 for address in addresses)


def test_the_engine_arithmetic_is_16_frame_plus_4_direction_plus_4(
    canonical_bytes: bytes,
) -> None:
    """Read the shifts straight out of the image, then re-apply them."""
    for name, expected_shift in (
        ("cell_row_scale", "#4"),
        ("cell_column_scale", "#2"),
        ("constructor_row", "#4"),
        ("constructor_column", "#2"),
        ("cell_method2_row", "#4"),
        ("cell_method2_column", "#2"),
    ):
        address, _ = probe.EVIDENCE_INSTRUCTIONS[name]
        mnemonic, operands, _ = probe.instruction_at(canonical_bytes, address)
        assert mnemonic == "lsls", name
        assert expected_shift in operands, name
    mnemonic, operands, _ = probe.instruction_at(canonical_bytes, 0x0800EF46)
    assert mnemonic == "ldr"
    assert operands.endswith("#4]")
    # And the base is the selected animation, not the definition: 0x0800EF3A loads
    # obj+0x50, which the selector wrote from definition[0x54 + 4*index].
    mnemonic, operands, _ = probe.instruction_at(canonical_bytes, 0x0800EF3A)
    assert mnemonic == "ldr"
    assert "#0x50" in operands
    mnemonic, operands, _ = probe.instruction_at(canonical_bytes, 0x0800ECE0)
    assert mnemonic == "ldr"
    assert "#0x54" in operands


def test_frame_count_bounds_the_animation(canonical_bytes: bytes) -> None:
    """The advice routine compares the frame index with animation + 0x00."""
    mnemonic, operands, _ = probe.instruction_at(canonical_bytes, 0x0800DE7E)
    assert mnemonic == "ldr"
    assert operands == "r3, [r3]"
    mnemonic, operands, _ = probe.instruction_at(canonical_bytes, 0x0800DE80)
    assert mnemonic == "cmp"
    mnemonic, operands, _ = probe.instruction_at(canonical_bytes, 0x0800DE82)
    assert mnemonic == "bgt"
    mnemonic, operands, _ = probe.instruction_at(canonical_bytes, 0x0800DE90)
    assert mnemonic == "strb"
    assert "#0x11" in operands


def test_direction_index_has_exactly_four_values(canonical_bytes: bytes) -> None:
    report = probe.state_table_direction_evidence(canonical_bytes)
    assert tuple(
        (int(entry["site"], 16), entry["value"]) for entry in report["constant_sites"]
    ) == EXPECTED_DIRECTION_CONSTANTS
    assert report["distinct_values"] == [0, 1, 2, 3]
    assert report["writes_exactly_four_positions"] is True
    for site in report["store_sites"]:
        mnemonic, operands, _ = probe.instruction_at(canonical_bytes, int(site, 16))
        assert mnemonic == "strb"
        assert "#0x10" in operands


def test_the_direction_index_is_a_runtime_byte_not_a_frame_counter(
    canonical_bytes: bytes,
) -> None:
    """The two indices the renderer combines come from different object bytes."""
    mnemonic, operands, _ = probe.instruction_at(canonical_bytes, 0x0800EF38)
    assert (mnemonic, operands) == ("ldrb", "r2, [r0, #0x11]")
    mnemonic, operands, _ = probe.instruction_at(canonical_bytes, 0x0800EF40)
    assert (mnemonic, operands) == ("ldrb", "r2, [r0, #0x10]")
    # The facing computers write the direction to obj+0x10; the animation
    # advance writes the frame index to obj+0x11.
    for site, _value in EXPECTED_DIRECTION_CONSTANTS:
        mnemonic, operands, _ = probe.instruction_at(canonical_bytes, site + 2)
        assert mnemonic == "strb"
        assert "#0x10" in operands
    mnemonic, operands, _ = probe.instruction_at(canonical_bytes, 0x0800DE90)
    assert (mnemonic, operands) == ("strb", "r2, [r1, #0x11]")


# --- determinism --------------------------------------------------------------


def test_reports_are_deterministic(canonical_bytes: bytes) -> None:
    """Recomputed from scratch, the reports agree; the memo is not the evidence.

    ``_memoised_census`` caches by image content, so comparing two calls that hit
    the cache would compare an object with itself.  The cache is cleared between
    the two computations here, so each report is genuinely produced twice.
    """
    first = probe.cell_census(canonical_bytes)
    probe._memoised_census.cache_clear()
    second = probe.cell_census(canonical_bytes)
    assert first == second
    assert first is not second

    first = probe.animation_reference_census(canonical_bytes)
    probe._memoised_census.cache_clear()
    second = probe.animation_reference_census(canonical_bytes)
    assert first == second
    assert first is not second

    probe._memoised_census.cache_clear()
    assert probe.piece_census(canonical_bytes) == probe.piece_census(canonical_bytes)


def test_reports_track_the_bytes(canonical_bytes: bytes) -> None:
    """A one-byte change moves the report, so the equalities above are not vacuous.

    Each mutation is applied to a *copy*; the canonical image is never written to.
    """
    reference = probe.piece_census(canonical_bytes)

    # A byte inside an animation's frame count changes the cell population.
    mutation = bytearray(canonical_bytes)
    mutation[REPRESENTATIVE_ANIMATION - probe.ROM_BASE + probe.ANIMATION_FRAME_COUNT] = 3
    assert probe.cell_census(bytes(mutation)) != probe.cell_census(canonical_bytes)

    # A byte inside one piece's graphics word changes the piece census.
    mutation = bytearray(canonical_bytes)
    mutation[REPRESENTATIVE_PIECE_0 - probe.ROM_BASE + probe.PIECE_GRAPHICS] ^= 0x01
    assert probe.piece_census(bytes(mutation)) != reference

    # A byte inside one piece's dimensions changes it too.
    mutation = bytearray(canonical_bytes)
    mutation[REPRESENTATIVE_PIECE_0 - probe.ROM_BASE + probe.PIECE_DIM_0] = 8
    assert probe.piece_census(bytes(mutation)) != reference

    # And the canonical image itself is untouched: the report repeats.
    assert probe.piece_census(canonical_bytes) == reference
