"""DECOMP-OBJECT-CONSTRUCTOR-001: the owner struct and the object's location.

These read the committed census at config/object_layout.json, which is generated
deterministically from the canonical ROM by tools/buusfury/gen_object_map.py.
No ROM and no toolchain are needed.
"""

from __future__ import annotations

import json

import pytest

from buusfury import identity, lift


@pytest.fixture(scope="module")
def census():
    path = identity.REPO_ROOT / "config" / "object_layout.json"
    if not path.is_file():
        pytest.skip("the object-layout census has not been generated")
    return json.loads(path.read_text("utf-8"))


@pytest.fixture(scope="module")
def owner(census):
    if "owner_table" not in census:
        pytest.skip("the owner-table derivation is not present")
    return census["owner_table"]


# ---------------------------------------------------------------------------
# the decisive finding: the field is ROM data, not a code assignment
# ---------------------------------------------------------------------------
def test_the_object_slot_is_read_straight_out_of_the_rom(owner):
    """This is why every writer search failed: there is no writer in code."""
    assert owner["object_slot_offset"] == "0x14"
    assert owner["object_slot_value"] == "0x03001068"
    assert owner["planted_by_code"] is False
    assert "present in the ROM image" in owner["planted_by_code_evidence"]


def test_every_table_value_is_an_ewram_pointer(owner):
    """The struct at 0x08054FBC is a table of absolute EWRAM addresses."""
    assert owner["all_values_are_ewram_pointers"] is True
    assert owner["ewram_pointer_count"] == 11
    for word in owner["words"]:
        if word["raw"] == 0:
            continue
        assert 0x02000000 <= word["raw"] < 0x03008000, word


def test_the_object_lives_at_a_static_address_not_on_the_heap(owner):
    assert owner["address_is_static_not_heap"] is True
    assert owner["object_address"] == "0x03001068"


def test_the_table_is_zero_terminated(owner):
    assert owner["zero_terminated_at"] == "0x2C"


# ---------------------------------------------------------------------------
# the constructor lead, and why it is NOT the owner's constructor
# ---------------------------------------------------------------------------
def test_the_allocator_lead_is_recorded_and_rejected(owner):
    """sub_0805082C is constructor-shaped and stores to [r0+0x14], but its store is
    inside the 0x28 bytes it just allocated - a different object."""
    note = owner["allocator_note"]
    assert "sub_0805082C" in note
    assert "0x28 bytes" in note
    assert "NOT this object's constructor" in note
    assert "[r0+0x14]" in note


# ---------------------------------------------------------------------------
# the static extent: an INFERRED upper bound, labelled as one
# ---------------------------------------------------------------------------
def test_the_static_extent_is_inferred_not_proven(owner):
    assert owner["static_extent_upper_bound_is_proven"] is False
    assert "INFERRED, NOT PROVEN" in owner["static_extent_upper_bound_evidence"]
    assert "do not overlap" in owner["static_extent_upper_bound_evidence"]


def test_the_inferred_extent_comes_from_the_next_table_pointer(owner):
    assert owner["next_ewram_address_above_the_object"] == "0x0300197C"
    assert owner["static_extent_upper_bound_bytes"] == 0x914
    assert 0x0300197C - 0x03001068 == 0x914


def test_the_object_minimum_size_is_still_the_proven_one():
    """The static address does not change the proven lower bound, which lives in
    the layout derivation rather than in this artifact."""
    from buusfury import identity as ident, lift as lift_mod
    try:
        rom = ident.resolve_baserom()
        ident.verify(rom)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"no canonical baserom available: {exc}")
    layout = lift_mod.derive_flag_array_layout(rom.read_bytes())
    assert layout["object_minimum_size_bytes"] == 0x56
    assert layout["lower_bound_bytes"] == 1
    assert layout["array_start"] == "base + 0x55"


# ---------------------------------------------------------------------------
# the flag array: still not proven, and now for a stated reason
# ---------------------------------------------------------------------------
def test_the_flag_array_bound_is_still_not_proven(census):
    bound = census["flag_array_upper_bound_from_static_layout"]
    assert bound["upper_bound_bytes"] is None
    assert bound["upper_bound_bits"] is None
    assert "STILL NOT PROVEN" in bound["status"]
    assert "INFERRED" in bound["status"]


def test_the_flag_array_start_address_is_derived_from_the_static_object(census):
    bound = census["flag_array_upper_bound_from_static_layout"]
    assert bound["object_address"] == "0x03001068"
    assert bound["flag_array_start"] == "object + 0x55"
    assert bound["flag_array_start_address"] == f"0x{0x03001068 + 0x55:08X}"


def test_the_inferred_extent_is_NOT_used_as_a_proven_flag_bound(census):
    """The ticket's evidence discipline: an inferred static extent must not be
    promoted into a proven flag-array bound."""
    bound = census["flag_array_upper_bound_from_static_layout"]
    assert bound["upper_bound_bytes"] is None, (
        "the inferred 0x914 extent must not be presented as a proven flag bound"
    )


# ---------------------------------------------------------------------------
# nothing else moved
# ---------------------------------------------------------------------------
def test_the_census_still_reports_the_same_user_sites(census):
    assert census["user_site_count"] == 61


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

def test_the_artifact_is_environment_independent(census):
    text = json.dumps(census)
    assert "C:\\" not in text
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
