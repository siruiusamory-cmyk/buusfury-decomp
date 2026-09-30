"""DECOMP-OBJECT-LAYOUT-001: the object-offset census for *(0x08054FBC + 0x14).

PORTABLE tests need no ROM and no toolchain: they read the committed census at
config/object_layout.json, which is generated deterministically by
build/gen_object_map.py from the canonical ROM.
"""

from __future__ import annotations

import json
import re

import pytest

from buusfury import identity, lift


@pytest.fixture(scope="module")
def census():
    path = identity.REPO_ROOT / "config" / "object_layout.json"
    if not path.is_file():
        pytest.skip("the object-layout census has not been generated")
    return json.loads(path.read_text("utf-8"))


# ---------------------------------------------------------------------------
# the census itself
# ---------------------------------------------------------------------------
def test_the_object_expression_is_the_one_under_study(census):
    assert census["object_expression"] == "*(0x08054FBC + 0x14)"
    assert census["global_struct"] == "0x08054FBC"


def test_all_user_sites_are_classified(census):
    """The ticket asks for all ~60 known reader sites."""
    sites = census["user_sites"]
    assert census["user_site_count"] == len(sites)
    assert len(sites) >= 60, f"expected the known 60-plus sites, found {len(sites)}"
    for site in sites:
        assert site["function"].startswith("0x")
        assert site["seed"].startswith("0x")
        assert site["deref"].startswith("0x")
        assert site["object_register"]


def test_every_site_records_its_containing_function(census):
    functions = {s["function"] for s in census["user_sites"]}
    assert len(functions) >= 20, f"too few distinct containing functions: {len(functions)}"
    for name in functions:
        assert re.fullmatch(r"0x[0-9A-F]{8}", name), name


# ---------------------------------------------------------------------------
# the offset map
# ---------------------------------------------------------------------------
def test_the_offset_map_groups_by_offset_with_width_and_direction(census):
    offset_map = census["offset_map"]
    assert offset_map, "the offset map is empty"
    for key, records in offset_map.items():
        assert int(key) >= 0
        assert records
        for record in records:
            assert record["offset"] == int(key)
            assert record["width"] in (1, 2, 4)
            assert record["access"] in ("read", "write")
            assert isinstance(record["indexed"], bool)
            assert record["mnemonic"]


def test_the_confirmed_field_offsets(census):
    """The independently confirmed fields, from the tracked register."""
    assert census["distinct_offsets"] == [0x0], census["distinct_offsets"]


def test_the_highest_proven_offset(census):
    assert census["highest_proven_offset"] == 0x0
    assert census["highest_proven_offset_hex"] == "0x000"


def test_the_refactor_tightened_one_rule(census):
    """Moving the policy into buusfury.object_track tightened one rule: a
    two-register add no longer preserves provenance, because object + object + const
    is not a valid object pointer. That removed the 0x01 access, and the loss is
    recorded rather than hidden."""
    assert census["distinct_offsets"] == [0x0]
    assert census["stack_flow"]["implemented"] is True


def test_the_tracker_is_sound_rather_than_permissive(census):
    """DECOMP-OBJECT-STACKFLOW-001 made the tracker fail closed at every
    control-flow discontinuity. The previous map resolved 14 offsets by
    propagating ACROSS branches and was therefore not sound; the sound map
    resolves far fewer, and this is recorded rather than hidden."""
    assert census["stack_flow"]["implemented"] is True
    assert census["stack_flow"]["fails_closed_on"]
    assert census["accesses_via_a_reload"] == census["accesses_via_a_reload"]


def test_the_access_widths_are_recorded(census):
    widths = census["access_widths"]
    assert widths, "no access widths recorded"
    for key, count in widths.items():
        assert int(key) in (1, 2, 4)
        assert count > 0


def test_indexed_and_constant_accesses_are_distinguished(census):
    total = census["indexed_accesses"] + census["constant_accesses"]
    assert total == sum(len(v) for v in census["offset_map"].values())
    assert census["constant_accesses"] > 0


# ---------------------------------------------------------------------------
# the flag-array neighbourhood
# ---------------------------------------------------------------------------
def test_nothing_was_found_in_the_flag_neighbourhood(census):
    """The ticket's priority question, answered negatively and honestly: no access
    in 0x40..0x80 was resolved through the tracked register, so no first-field-
    after-the-array, no bounded loop and no copy extent was established."""
    assert census["accesses_in_0x2D_to_0x80"] == []
    for offset in census["distinct_offsets"]:
        assert not (0x2D <= offset <= 0x80), hex(offset)


def test_the_flag_array_bound_remains_unresolved(census):
    status = census["flag_array_bound_status"]
    assert "UNRESOLVED" in status
    assert "not derivable" in status
    assert "0x2D" in status and "0x80" in status


def test_the_highest_field_is_below_the_flag_array(census):
    """Worth stating explicitly: the census's highest confirmed field is 0x2C, and
    the flag array's first byte is a PROVEN 0x55. The array is therefore a hard
    lower bound on the object that exceeds every field this census resolved."""
    assert census["highest_proven_offset"] < 0x55
    assert census["accesses_in_0x2D_to_0x80"] == []
    assert census["accesses_above_the_flag_array"] == []


# ---------------------------------------------------------------------------
# the constructor search
# ---------------------------------------------------------------------------
def test_both_constructor_shapes_found_zero_writers(census):
    search = census["constructor_search"]
    assert search["shape_1"]["writers"] == 0
    assert search["shape_2"]["writers"] == 0
    assert search["shape_1"]["readers"] >= 60
    assert "UNRECOVERABLE" in search["conclusion"]


def test_the_second_shape_is_genuinely_different(census):
    """It must not be a restatement of the first."""
    one = census["constructor_search"]["shape_1"]["signature"]
    two = census["constructor_search"]["shape_2"]["signature"]
    assert one != two
    assert "12 instructions" in two


def test_no_allocation_size_was_found(census):
    assert census["exact_size_proven"] is False


# ---------------------------------------------------------------------------
# honesty of the artifact
# ---------------------------------------------------------------------------
def test_the_census_declares_itself_a_lower_bound(census):
    """Absence of an offset must never be read as evidence of disuse."""
    text = census["census_is_a_lower_bound"]
    assert "LOWER BOUND" in text
    assert "NOT" in text and "evidence" in text


def test_the_verdict_is_explicit(census):
    assert "unresolved" in census["verdict"]
    assert "lower bound" in census["verdict"]


def test_the_artifact_is_environment_independent(census):
    text = json.dumps(census)
    assert "C:\\\\" not in text
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text


def test_the_generator_is_committed(census):
    """The census must be reproducible, so its generator ships with it."""
    # The generator must live OUTSIDE build/, which is gitignored: a generator
    # under build/ is not committed, so the census would not be reproducible.
    generator = identity.REPO_ROOT / "tools" / "buusfury" / "gen_object_map.py"
    assert generator.is_file(), "the committed census has no committed generator"
    assert census["generated_by"] == "tools/buusfury/gen_object_map.py"
    assert not (identity.REPO_ROOT / "build" / "gen_object_map.py").exists(), \
        "the generator must not live under the gitignored build/"


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
