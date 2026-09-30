"""DECOMP-FLAGSTATE-LAYOUT-001: the flag array's extent, as far as it is provable.

PORTABLE tests need no ROM and no toolchain. ROM-gated tests skip cleanly when the
baserom is absent. The ROM is opened READ-ONLY.

This ticket lifts NO new routine: the evidence needed for the layout comes from the
five routines already lifted and from an image-wide search for the object's
constructor, which found no writer of the object pointer. No lift report is added
or changed.
"""

from __future__ import annotations

import pytest

from buusfury import identity, lift


@pytest.fixture(scope="module")
def layout():
    try:
        rom = identity.resolve_baserom()
        identity.verify(rom)
    except Exception as exc:  # noqa: BLE001 - the fixture's whole job is to skip
        pytest.skip(f"no canonical baserom available: {exc}")
    return lift.derive_flag_array_layout(rom.read_bytes())


# ---------------------------------------------------------------------------
# the array's start: PROVEN
# ---------------------------------------------------------------------------
def test_the_array_starts_at_base_plus_0x55(layout):
    assert layout["array_start"] == "base + 0x55"
    assert layout["array_start_is_proven"] is True


def test_the_three_accessors_independently_agree_on_the_start(layout):
    """The gather and the apply-mask routine reach the array through the accessors,
    so only the accessors compute the index arithmetic themselves."""
    assert layout["routines_computing_the_index_arithmetic"] == 3
    assert layout["users_agreeing_on_the_start"] is True
    computes = [u for u in layout["users"] if u["computes_the_index_arithmetic"]]
    assert {u["role"] for u in computes} == {"test", "set", "clear"}
    for user in computes:
        assert user["object_offset"] == 0x50
        assert user["field_offset"] == 5
        assert user["storage_base"] == "base + 0x55"


def test_the_two_delegates_are_marked_as_reaching_the_array_through_the_accessors(layout):
    delegates = [u for u in layout["users"] if not u["computes_the_index_arithmetic"]]
    assert {u["role"] for u in delegates} == {"gather", "apply-mask"}
    for user in delegates:
        assert user["storage_base"] is None
        assert user["reaches_the_array_through"]


def test_the_entry_size_and_the_index_split(layout):
    assert layout["entry_size_bytes"] == 1
    assert layout["index_split"]["bits_per_byte"] == 8
    assert ">> 3" in layout["index_split"]["byte_index"]
    assert "& 7" in layout["index_split"]["bit_index"]


def test_the_array_is_not_word_aligned(layout):
    """+0x55 is an odd offset, which is worth recording."""
    assert "ODD offset" in layout["alignment"]
    assert "NOT word-aligned" in layout["alignment"]


# ---------------------------------------------------------------------------
# the bounds
# ---------------------------------------------------------------------------
def test_the_lower_bound_is_proven(layout):
    assert layout["lower_bound_bytes"] == 1
    assert layout["lower_bound_bits"] == 8
    assert "bits 0 and 1 are demonstrably both used" in layout["lower_bound_evidence"]


def test_no_upper_bound_is_derivable(layout):
    """The honest answer: nothing in the code fixes the array's end."""
    assert layout["upper_bound_bytes"] is None
    assert layout["upper_bound_bits"] is None
    assert "compares an index, an offset or a width against a size" in layout["upper_bound_reason"]


def test_the_verdict_is_honest_bounds(layout):
    assert layout["verdict"].startswith("HONEST BOUNDS")
    assert layout["missing_evidence"]


def test_the_object_has_a_proven_minimum_size(layout):
    assert layout["object_minimum_size_bytes"] == 0x56
    assert "0x56" in layout["object_minimum_size_evidence"]


def test_the_neighbours_are_stated(layout):
    assert layout["neighbour_below"]["offset"] == "base + 0x54"
    assert layout["neighbour_above"]["offset"] is None
    assert "nothing" in layout["neighbour_above"]["description"]


# ---------------------------------------------------------------------------
# the index-range question
# ---------------------------------------------------------------------------
def test_no_index_constraint_is_proven_and_none_is_inferred(layout):
    """The ticket's key question. The answer is NO, and the report must say so
    rather than implying the routines are safe."""
    constraints = layout["index_constraints"]
    assert constraints["any_proven"] is False
    detail = constraints["detail"]
    assert "NO constraint" in detail
    assert "does NOT" in detail
    assert "none should be inferred" in detail


def test_the_clamp_that_does_exist_is_not_an_array_bound(layout):
    """The apply-mask routine clamps the MASK to the width; that is not a bound on
    the offset plus the width."""
    assert "clamps the MASK to the width" in layout["index_constraints"]["detail"]
    assert "never clamps offset + width" in layout["index_constraints"]["detail"]


# ---------------------------------------------------------------------------
# the constructor search
# ---------------------------------------------------------------------------
def test_the_constructor_search_found_no_writer(layout):
    search = layout["constructor_search"]
    assert search["writers_found"] == 0
    assert search["readers_found"] > 0
    assert "NOT RECOVERABLE" in search["conclusion"] or "not" in search["conclusion"].lower()


def test_no_initialisation_copy_or_serialisation_was_found(layout):
    assert layout["initialisation_or_copy_found"] is False
    assert layout["serialisation_found"] is False


def test_the_derivation_is_mechanical(layout):
    assert layout["derived_from_rom"] is True
    assert layout["not_hand_written"] is True


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
