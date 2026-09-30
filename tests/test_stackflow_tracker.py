"""DECOMP-OBJECT-STACKFLOW-TEST-001: synthetic cases for the pure tracker.

These drive `buusfury.object_track.track_normalized` with hand-built plain
dictionaries, so the tracking policy is proved directly rather than inferred from
the census. Nothing here needs the ROM, capstone, or a toolchain.
"""

from __future__ import annotations

import pytest

from buusfury import object_track
from buusfury.object_track import item, track_normalized


# ---------------------------------------------------------------------------
# 1. spill -> reload -> field read
# ---------------------------------------------------------------------------
def test_spill_reload_then_field_read():
    """The case this whole tracker exists for."""
    run = [
        item(0x1000, "str", dst="r0", base="sp", disp=0x10),
        item(0x1002, "ldr", dst="r2", base="sp", disp=0x10),
        item(0x1004, "ldrb", dst="r1", base="r2", disp=0x20),
    ]
    result = track_normalized(run, "r0")
    assert len(result["spills"]) == 1
    assert len(result["reloads"]) == 1
    assert len(result["records"]) == 1
    record = result["records"][0]
    assert record["offset"] == 0x20
    assert record["width"] == 1
    assert record["access"] == "read"
    assert record["via_reload"] is True


# ---------------------------------------------------------------------------
# 2. spill -> reload -> field write
# ---------------------------------------------------------------------------
def test_spill_reload_then_field_write():
    run = [
        item(0x1000, "str", dst="r0", base="sp", disp=8),
        item(0x1002, "ldr", dst="r3", base="sp", disp=8),
        item(0x1004, "strh", dst="r1", base="r3", disp=0x30),
    ]
    result = track_normalized(run, "r0")
    assert len(result["records"]) == 1
    record = result["records"][0]
    assert record["offset"] == 0x30
    assert record["width"] == 2
    assert record["access"] == "write"
    assert record["via_reload"] is True


# ---------------------------------------------------------------------------
# 3. multiple independent stack slots
# ---------------------------------------------------------------------------
def test_multiple_stack_slots_are_kept_apart():
    run = [
        item(0x1000, "str", dst="r0", base="sp", disp=4),
        item(0x1002, "str", dst="r0", base="sp", disp=8),
        item(0x1004, "ldr", dst="r5", base="sp", disp=8),
        item(0x1006, "ldr", dst="r6", base="sp", disp=4),
        item(0x1008, "ldrb", dst="r1", base="r5", disp=0x11),
        item(0x100A, "ldrb", dst="r1", base="r6", disp=0x22),
    ]
    result = track_normalized(run, "r0")
    assert len(result["spills"]) == 2
    assert len(result["reloads"]) == 2
    assert [r["offset"] for r in result["records"]] == [0x11, 0x22]


# ---------------------------------------------------------------------------
# 4. a stack-slot overwrite kills provenance
# ---------------------------------------------------------------------------
def test_stack_slot_overwrite_kills_provenance():
    """A store of unknown provenance into the same slot must invalidate it, so the
    later reload proves nothing and no access is reported."""
    run = [
        item(0x1000, "str", dst="r0", base="sp", disp=0x10),
        item(0x1002, "str", dst="r9", base="sp", disp=0x10),   # r9 is not tracked
        item(0x1004, "ldr", dst="r2", base="sp", disp=0x10),
        item(0x1006, "ldrb", dst="r1", base="r2", disp=0x20),
    ]
    result = track_normalized(run, "r0")
    assert result["reloads"] == []
    assert result["records"] == []


# ---------------------------------------------------------------------------
# 5. an ambiguous / control-flow merge kills provenance
# ---------------------------------------------------------------------------
def test_control_flow_discontinuity_kills_provenance():
    """A gap between consecutive addresses means a merge this pass cannot prove."""
    run = [
        item(0x1000, "ldrb", dst="r1", base="r0", disp=1),
        item(0x2000, "ldrb", dst="r1", base="r0", disp=2),     # jumped here
    ]
    result = track_normalized(run, "r0")
    assert [r["offset"] for r in result["records"]] == [1]
    assert result["stopped"] == object_track.STOP_DISCONTINUITY
    assert result["stopped_at"] == 0x2000


def test_a_branch_ends_the_run():
    run = [
        item(0x1000, "ldrb", dst="r1", base="r0", disp=1),
        item(0x1002, "b", imm=0x3000),
        item(0x1004, "ldrb", dst="r1", base="r0", disp=9),
    ]
    result = track_normalized(run, "r0")
    assert [r["offset"] for r in result["records"]] == [1]
    assert result["stopped"] == object_track.STOP_BRANCH


def test_a_conditional_branch_ends_the_run():
    run = [
        item(0x1000, "ldrb", dst="r1", base="r0", disp=1),
        item(0x1002, "beq", imm=0x3000),
        item(0x1004, "ldrb", dst="r1", base="r0", disp=9),
    ]
    result = track_normalized(run, "r0")
    assert [r["offset"] for r in result["records"]] == [1]
    assert result["stopped"] == object_track.STOP_BRANCH


# ---------------------------------------------------------------------------
# 6. unrelated stack traffic creates no false object accesses
# ---------------------------------------------------------------------------
def test_unrelated_stack_traffic_creates_no_false_accesses():
    run = [
        item(0x1000, "str", dst="r7", base="sp", disp=0x20),
        item(0x1002, "str", dst="r6", base="sp", disp=0x24),
        item(0x1004, "ldr", dst="r5", base="sp", disp=0x20),
        item(0x1006, "ldrb", dst="r1", base="r5", disp=0x55),
        item(0x1008, "ldrb", dst="r1", base="r0", disp=0x10),
    ]
    result = track_normalized(run, "r0")
    assert result["spills"] == []
    assert result["reloads"] == []
    assert [r["offset"] for r in result["records"]] == [0x10]


def test_a_frame_store_of_a_tracked_register_is_a_spill_not_an_access():
    run = [item(0x1000, "str", dst="r0", base="sp", disp=0)]
    result = track_normalized(run, "r0")
    assert result["records"] == []
    assert len(result["spills"]) == 1


# ---------------------------------------------------------------------------
# regression: the previously UNSOUND branch propagation
# ---------------------------------------------------------------------------
def test_regression_a_register_may_not_survive_a_branch():
    """This is the defect DECOMP-OBJECT-STACKFLOW-001 corrected.

    The previous census propagated a register ACROSS a branch and reported offsets
    on the far side that a merge could have invalidated. The tracker must refuse:
    no access may be reported after a branch, even when the object register is
    never rewritten and the addresses happen to look contiguous.
    """
    run = [
        item(0x1000, "ldrb", dst="r1", base="r0", disp=0x2C),
        item(0x1002, "bne", imm=0x1008),
        item(0x1004, "ldrb", dst="r1", base="r0", disp=0x40),
        item(0x1006, "ldrb", dst="r1", base="r0", disp=0x55),
    ]
    result = track_normalized(run, "r0")
    offsets = [r["offset"] for r in result["records"]]
    assert offsets == [0x2C], (
        "an offset beyond a branch must NOT be reported; the previous 14-offset "
        f"map did exactly this. Got {offsets}"
    )
    assert 0x40 not in offsets and 0x55 not in offsets


def test_regression_an_unknown_reload_does_not_restore_provenance():
    run = [
        item(0x1000, "ldr", dst="r2", base="sp", disp=0x10),
        item(0x1002, "ldrb", dst="r1", base="r2", disp=0x20),
    ]
    result = track_normalized(run, "r0")
    assert result["reloads"] == [] and result["records"] == []


# ---------------------------------------------------------------------------
# the remaining fail-closed rules
# ---------------------------------------------------------------------------
def test_an_unrecognised_clobber_of_the_object_register_loses_it():
    run = [
        item(0x1000, "muls", dst="r0", src="r1"),
        item(0x1002, "ldrb", dst="r1", base="r0", disp=0x55),
    ]
    result = track_normalized(run, "r0")
    assert result["records"] == []


def test_unknown_pointer_arithmetic_loses_provenance():
    run = [
        item(0x1000, "adds", dst="r2", src="r0", imm=None),
        item(0x1002, "ldrb", dst="r1", base="r2", disp=5),
    ]
    result = track_normalized(run, "r0")
    assert result["records"] == []


def test_provenance_conflict_loses_the_register():
    """A register re-loaded from a base that is not tracked must not keep the
    provenance it had before."""
    run = [
        item(0x1000, "adds", dst="r4", src="r0", imm=0),
        item(0x1002, "ldr", dst="r4", base="r7", disp=0),
        item(0x1004, "ldrb", dst="r1", base="r4", disp=5),
    ]
    result = track_normalized(run, "r0")
    assert result["records"] == []


# ---------------------------------------------------------------------------
# the policy is followed positively too
# ---------------------------------------------------------------------------
def test_an_immediate_add_carries_provenance():
    run = [
        item(0x1000, "adds", dst="r4", src="r0", imm=0x40),
        item(0x1002, "ldrb", dst="r1", base="r4", disp=1),
    ]
    result = track_normalized(run, "r0")
    assert result["records"][0]["offset"] == 0x41


def test_an_immediate_copy_carries_provenance():
    run = [
        item(0x1000, "adds", dst="r4", src="r0", imm=0),
        item(0x1002, "ldrb", dst="r1", base="r4", disp=7),
    ]
    result = track_normalized(run, "r0")
    assert result["records"][0]["offset"] == 7


def test_a_simple_move_carries_provenance():
    run = [
        item(0x1000, "mov", dst="r5", src="r0"),
        item(0x1002, "ldrb", dst="r1", base="r5", disp=9),
    ]
    result = track_normalized(run, "r0")
    assert result["records"][0]["offset"] == 9


def test_an_indexed_access_is_flagged():
    run = [item(0x1000, "ldrb", dst="r1", base="r0", disp=0, index=True)]
    result = track_normalized(run, "r0")
    assert result["records"][0]["indexed"] is True


def test_a_direct_access_with_no_spill_is_reported():
    run = [item(0x1000, "ldrb", dst="r1", base="r0", disp=5)]
    result = track_normalized(run, "r0")
    assert result["records"][0]["offset"] == 5
    assert result["records"][0]["via_reload"] is False


def test_the_run_ends_cleanly_at_the_end_of_input():
    run = [item(0x1000, "ldrb", dst="r1", base="r0", disp=5)]
    assert track_normalized(run, "r0")["stopped"] == object_track.STOP_END


# ---------------------------------------------------------------------------
# the module is pure and cheap to import
# ---------------------------------------------------------------------------
def test_the_module_needs_no_rom_and_exposes_the_policy():
    assert callable(object_track.track_normalized)
    assert callable(object_track.normalize)
    assert callable(object_track.item)
    assert object_track.WIDTH["ldrb"] == 1
    assert object_track.WIDTH["ldrh"] == 2
    assert object_track.WIDTH["ldr"] == 4


def test_the_tracker_never_mutates_its_input():
    run = [item(0x1000, "ldrb", dst="r1", base="r0", disp=5)]
    before = [dict(x) for x in run]
    track_normalized(run, "r0")
    assert run == before


@pytest.mark.parametrize("mnemonic,width", [
    ("ldrb", 1), ("strb", 1), ("ldrh", 2), ("strh", 2), ("ldr", 4), ("str", 4),
])
def test_every_width_is_reported(mnemonic, width):
    run = [item(0x1000, mnemonic, dst="r1", base="r0", disp=0)]
    assert track_normalized(run, "r0")["records"][0]["width"] == width


# ---------------------------------------------------------------------------
# the one rule the refactor TIGHTENED, pinned so it cannot drift back
# ---------------------------------------------------------------------------
def test_a_two_register_add_does_not_preserve_provenance():
    """`adds r1, r1, r0` computes object + object + const, which is NOT a valid
    object pointer, so provenance must be dropped.

    The pre-refactor inline tracker accepted ANY operand being the object register
    here and kept the register. That was unsound, and removing it is why the census
    lost the 0x01 access when the policy moved into this module.
    """
    run = [
        item(0x1000, "adds", dst="r1", src="r1", imm=None),   # a two-register add
        item(0x1002, "ldrb", dst="r2", base="r1", disp=0x01),
    ]
    result = track_normalized(run, "r0")
    assert result["records"] == [], "an unknown two-register add must lose the register"


def test_an_add_of_a_tracked_register_to_an_unknown_value_loses_it():
    run = [
        item(0x1000, "adds", dst="r4", src="r0", imm=0),
        item(0x1002, "adds", dst="r4", src="r7", imm=None),
        item(0x1004, "ldrb", dst="r1", base="r4", disp=1),
    ]
    result = track_normalized(run, "r0")
    assert result["records"] == []
