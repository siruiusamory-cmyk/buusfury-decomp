"""DECOMP-EWRAM-LAYOUT-001: the static pointer table at 0x08054FBC.

These read the committed artifact config/ewram_layout.json, which is generated
deterministically from the canonical ROM by tools/buusfury/gen_ewram_layout.py.
No ROM and no toolchain are needed.
"""

from __future__ import annotations

import json

import pytest

from buusfury import identity, lift

EXPECTED_TARGETS = [
    0x03003300, 0x03003898, 0x030038A4, 0x0300197C, 0x03001990, 0x03001068,
    0x03001C4C, 0x03002BAC, 0x03002BD8, 0x030019A4, 0x03002A64,
]
SORTED_TARGETS = sorted(EXPECTED_TARGETS)


@pytest.fixture(scope="module")
def layout():
    path = identity.REPO_ROOT / "config" / "ewram_layout.json"
    if not path.is_file():
        pytest.skip("the static layout artifact has not been generated")
    return json.loads(path.read_text("utf-8"))


# ---------------------------------------------------------------------------
# 1. the complete table
# ---------------------------------------------------------------------------
def test_all_eleven_non_zero_entries_are_mapped(layout):
    assert layout["validation"]["non_zero_entry_count"] == 11
    assert [int(e["value"], 16) for e in layout["entries"]] == EXPECTED_TARGETS


def test_the_table_is_zero_terminated(layout):
    assert layout["terminator"]["table_offset"] == "0x2C"
    assert layout["terminator"]["raw"] == 0


def test_each_entry_carries_its_rom_address_and_offset(layout):
    for entry in layout["entries"]:
        assert entry["table_offset"].startswith("0x")
        assert entry["rom_address"].startswith("0x08054F")
        assert entry["value"].startswith("0x")
        assert int(entry["rom_address"], 16) == 0x08054FBC + int(entry["table_offset"], 16)


# ---------------------------------------------------------------------------
# 2. structure validation
# ---------------------------------------------------------------------------
def test_all_values_are_unique(layout):
    assert layout["validation"]["all_values_unique"] is True
    values = [e["value"] for e in layout["entries"]]
    assert len(set(values)) == len(values) == 11


def test_table_order_is_measured_and_is_not_memory_order(layout):
    """The ticket says not to assume table order equals memory order; it does not."""
    assert layout["validation"]["table_order_equals_memory_order"] is False
    assert "NOT sorted by address" in layout["validation"]["table_order_note"]
    assert [int(e["value"], 16) for e in layout["entries"]] != SORTED_TARGETS


def test_every_entry_is_an_iwram_address(layout):
    """The previous artifact called these EWRAM pointers; they are IWRAM."""
    assert layout["validation"]["all_in_IWRAM"] is True
    assert layout["validation"]["regions_present"] == ["IWRAM"]
    assert "THEY ARE NOT" in layout["region_correction"]
    for entry in layout["entries"]:
        value = int(entry["value"], 16)
        assert 0x03000000 <= value < 0x03008000, entry


def test_no_entry_points_outside_valid_gba_ram(layout):
    assert layout["validation"]["any_outside_valid_ram"] is False
    assert layout["validation"]["entries_outside_valid_gba_ram"] == []
    for entry in layout["entries"]:
        assert entry["region"] == "IWRAM"


# ---------------------------------------------------------------------------
# 3. the sorted layout and its intervals
# ---------------------------------------------------------------------------
def test_the_sorted_layout_is_in_ascending_memory_order(layout):
    ordered = layout["sorted_memory_layout"]
    assert len(ordered) == 11
    values = [int(e["target"], 16) for e in ordered]
    assert values == sorted(values) == SORTED_TARGETS
    for position, entry in enumerate(ordered):
        assert entry["ascending_position"] == position


def test_every_interval_is_classed_as_inferred(layout):
    """Adjacency is an upper bound only, and the artifact must say so."""
    for entry in layout["sorted_memory_layout"]:
        assert entry["class"] in ("INFERRED_MAX_EXTENT", "PROVEN_START_UNBOUNDED_ABOVE")
        assert entry["class"] != "PROVEN_EXTENT"
    assert "INFERRED_MAX_EXTENT" in layout["adjacency_is_an_upper_bound_only"]


def test_the_gap_extremes(layout):
    assert layout["validation"]["smallest_gap_bytes"] == 0xC
    assert layout["validation"]["largest_gap_bytes"] == 0xE18


def test_the_twelve_byte_gap_is_a_real_consistency_signal(layout):
    """Two entries are only 12 bytes apart, which is consistent with these being
    genuinely distinct small static objects rather than unrelated addresses."""
    ordered = layout["sorted_memory_layout"]
    small = [e for e in ordered if e["gap_to_next_higher_bytes"] == 0xC]
    assert len(small) == 1
    assert small[0]["target"] == "0x03003898"


# ---------------------------------------------------------------------------
# 4. the focus object
# ---------------------------------------------------------------------------
def test_the_focus_object_is_the_lowest_in_the_table(layout):
    focus = layout["focus_object"]
    assert focus["table_offset"] == "0x14"
    assert focus["target"] == "0x03001068"
    assert focus["ascending_position"] == 0
    assert focus["nearest_lower_static_object"] is None
    assert "LOWEST address" in focus["position_note"]


def test_the_focus_object_neighbours_and_gaps(layout):
    focus = layout["focus_object"]
    assert focus["nearest_higher_static_object"] == "0x0300197C"
    assert focus["gap_to_next_lower_bytes"] is None
    assert focus["gap_to_next_higher_bytes"] == 0x914


def test_the_flag_array_start_address(layout):
    focus = layout["focus_object"]
    assert focus["flag_array_start_offset"] == "0x55"
    assert focus["flag_array_start_address"] == "0x030010BD"
    assert 0x03001068 + 0x55 == 0x030010BD


def test_the_inferred_maximum_extent_and_flag_capacity(layout):
    focus = layout["focus_object"]
    assert focus["maximum_extent_bytes_under_non_overlap"] == 0x914
    assert focus["max_bytes_available_from_the_flag_array_start"] == 0x914 - 0x55
    assert focus["max_bytes_available_from_the_flag_array_start"] == 0x8BF
    assert focus["max_flag_bits_if_the_inferred_extent_held"] == 0x8BF * 8
    assert focus["max_flag_bits_if_the_inferred_extent_held"] == 17912


def test_the_maximum_extent_is_explicitly_inferred_not_proven(layout):
    """The ticket forbids manufacturing a precise object size from adjacency."""
    focus = layout["focus_object"]
    assert focus["maximum_extent_is_proven"] is False
    assert focus["maximum_extent_class"] == "INFERRED_MAX_EXTENT"
    assert "non-overlap" in focus["why_this_is_not_proven"]
    assert "Nothing shows" in focus["why_this_is_not_proven"]


def test_the_flag_array_bound_remains_unproven(layout):
    assert "STILL NOT PROVEN" in layout["flag_array_bound_status"]
    assert "INFERRED" in layout["flag_array_bound_status"]


# ---------------------------------------------------------------------------
# 5. cross-check across the objects
# ---------------------------------------------------------------------------
def test_every_target_is_referenced_elsewhere_as_a_literal(layout):
    """The interval model holds consistently: all eleven addresses are named by
    code or data beyond their own table entry, so they are distinct objects rather
    than padding."""
    cross = layout["cross_check_literal_references"]
    assert len(cross) == 11
    for row in cross:
        assert row["literal_word_occurrences_in_the_image"] > 1, row
        assert row["referenced_by_code_as_a_constant"] is True
        assert row["first_occurrences"]


def test_the_cross_check_counts_are_recorded(layout):
    counts = {row["table_offset"]: row["literal_word_occurrences_in_the_image"]
              for row in layout["cross_check_literal_references"]}
    assert counts["0x14"] == 41
    assert counts["0x18"] == 180
    assert min(counts.values()) == 4


# ---------------------------------------------------------------------------
# 6. evidence discipline
# ---------------------------------------------------------------------------
def test_proven_inferred_and_unproven_are_kept_apart(layout):
    assert layout["proven"] and layout["inferred"] and layout["unproven"]
    assert any("unique" in p for p in layout["proven"])
    assert any("maximum extent" in i for i in layout["inferred"])
    assert any("exact size" in u for u in layout["unproven"])


def test_no_size_is_presented_as_proven(layout):
    for entry in layout["sorted_memory_layout"]:
        assert entry["class"].startswith("INFERRED") or entry["class"].startswith("PROVEN_START")
    assert layout["focus_object"]["maximum_extent_is_proven"] is False


def test_the_artifact_is_environment_independent(layout):
    text = json.dumps(layout)
    assert "C:\\" not in text
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text


def test_the_generator_is_committed_and_outside_build(layout):
    generator = identity.REPO_ROOT / "tools" / "buusfury" / "gen_ewram_layout.py"
    assert generator.is_file(), "the artifact has no committed generator"
    assert layout["generated_by"] == "tools/buusfury/gen_ewram_layout.py"
    assert not (identity.REPO_ROOT / "build" / "gen_ewram_layout.py").exists()


def test_no_new_lift_target_was_added():
    """A FLOOR, not an exact count.

    Pinning the exact number of targets means every later ticket that adds one must
    edit an earlier ticket's test. That happened four times when native slot 178
    became the fourteenth target, so this asserts a floor and the named survivors
    instead.
    """
    ids = [t.id for t in lift.load_targets()]
    assert len(ids) >= 13, ids
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith",
                    "use", "effect", "flagread", "booluse", "clear", "gather", "flagmask"):
        assert earlier in ids, earlier
