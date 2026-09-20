"""Property tests for the write path's binary invariants.

Example-based coverage of these rules already exists (`test_relocation.py`,
`test_authored_image.py`, `test_stat_write.py`); what is added here is the
general statement, over generated bases and generated change sets, of the
invariants those examples sample:

* an edit plan does not depend on the order its changes are reported in;
* identical physical writes collapse to one change, deterministically;
* two writes that disagree about one span always fail closed;
* overlapping (not merely duplicated) spans always fail closed;
* applying a plan changes exactly the declared bytes;
* a no-op plan reproduces the base byte for byte;
* reverting an applied plan restores the base byte for byte;
* a plan is refused against any base other than the one it was computed from;
* a self-consistent provenance document still cannot excuse a byte changed
  outside its declared fields.

Everything here is pure: bytes in, bytes out, no ROM, no Qt, no filesystem.
The generated cases are deliberately tiny (at most 48 bytes) so the whole
module stays a fraction of a second inside the portable gate.
"""

from __future__ import annotations

import hashlib
import os

from hypothesis import given, settings
from hypothesis import strategies as st
import pytest

from tools.webfoot.authored_image import (
    AuthoredImageError,
    normalize_changes,
    verify_emitted_image,
)
from tools.webfoot.write import (
    ByteChange,
    ChangeValidationError,
    OverlappingChangeError,
    WriteManifest,
    apply_plan,
    plan_changes,
)

def _search_depth() -> int:
    """Examples per property; ``WEBFOOT_PROPERTY_EXAMPLES`` deepens the sweep."""
    try:
        return max(1, int(os.environ.get("WEBFOOT_PROPERTY_EXAMPLES", "50")))
    except ValueError:  # pragma: no cover - a malformed override
        return 50


#: Derandomized on purpose: `fast` is documented as the deterministic portable
#: gate, and a gate that explores a different sample each run can go red on
#: unchanged code. A falsifying example is still printed with its seed, and the
#: depth is a documented knob rather than a per-run accident.
SETTINGS = settings(
    max_examples=_search_depth(), deadline=None, derandomize=True
)

_MAX_BASE = 48


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _change(offset: int, old: bytes, new: bytes, owner: str = "owner:0") -> ByteChange:
    return ByteChange(offset=offset, old=old, new=new, owner=owner, reason="property")


@st.composite
def base_with_disjoint_changes(draw: st.DrawFn) -> tuple[bytes, list[ByteChange]]:
    """A base image plus changes on pairwise-disjoint, non-empty spans.

    The spans are cut from the image itself so every ``old`` is genuinely what
    the base holds, which is what makes the plan applicable rather than a
    validation failure.
    """
    base = draw(st.binary(min_size=1, max_size=_MAX_BASE))
    cuts = sorted(
        {0, len(base)}
        | set(draw(st.lists(st.integers(0, len(base)), max_size=4, unique=True)))
    )
    changes: list[ByteChange] = []
    for index, (start, stop) in enumerate(zip(cuts, cuts[1:])):
        if start == stop:
            continue
        old = base[start:stop]
        new = draw(st.binary(min_size=len(old), max_size=len(old)))
        changes.append(_change(start, old, new, owner=f"owner:{index}"))
    return base, changes


@SETTINGS
@given(case=base_with_disjoint_changes(), data=st.data())
def test_normalized_changes_do_not_depend_on_input_order(
    case: tuple[bytes, list[ByteChange]], data: st.DataObject
) -> None:
    """The normalized edit set is a function of the edits, not of their order.

    ``authored_image.normalize_changes`` promises the emitted image and its
    manifest are identical whatever order the caller reported edits in.
    """
    _, changes = case
    shuffled = data.draw(st.permutations(changes))

    assert normalize_changes(shuffled) == normalize_changes(changes)


@SETTINGS
@given(case=base_with_disjoint_changes(), data=st.data())
def test_identical_physical_writes_collapse_deterministically(
    case: tuple[bytes, list[ByteChange]], data: st.DataObject
) -> None:
    """Repeating the same physical write any number of times is one change."""
    _, changes = case
    repeats = data.draw(st.lists(st.integers(1, 3), min_size=1, max_size=3))
    repeated = changes * sum(repeats)
    shuffled = data.draw(st.permutations(repeated))

    assert normalize_changes(shuffled) == normalize_changes(changes)


@SETTINGS
@given(base=st.binary(min_size=1, max_size=_MAX_BASE), data=st.data())
def test_writes_that_disagree_about_one_span_fail_closed(
    base: bytes, data: st.DataObject
) -> None:
    """Two owners cannot write different bytes to the same field."""
    offset = data.draw(st.integers(min_value=0, max_value=len(base) - 1))
    size = data.draw(st.integers(min_value=1, max_value=len(base) - offset))
    old = base[offset : offset + size]
    first = data.draw(st.binary(min_size=size, max_size=size))
    delta = data.draw(st.integers(min_value=1, max_value=255))
    second = bytes([(first[0] + delta) % 256]) + first[1:]

    with pytest.raises(AuthoredImageError):
        normalize_changes([_change(offset, old, first, "a:1"),
                           _change(offset, old, second, "b:1")])


@SETTINGS
@given(base=st.binary(min_size=2, max_size=_MAX_BASE), data=st.data())
def test_overlapping_spans_fail_closed_in_the_planner(
    base: bytes, data: st.DataObject
) -> None:
    """Distinct spans that share a byte are refused, not resolved by order."""
    start = data.draw(st.integers(min_value=0, max_value=len(base) - 2))
    first_size = data.draw(st.integers(min_value=1, max_value=len(base) - start - 1))
    second_start = data.draw(
        st.integers(min_value=start, max_value=start + first_size - 1)
    )
    second_size = data.draw(
        st.integers(min_value=1, max_value=len(base) - second_start)
    )
    first = _change(start, base[start : start + first_size],
                    base[start : start + first_size], "a:1")
    second = _change(second_start, base[second_start : second_start + second_size],
                     base[second_start : second_start + second_size], "b:1")

    with pytest.raises(OverlappingChangeError):
        plan_changes(base, [first, second], profile_id="p", base_sha256=_sha256(base))


@SETTINGS
@given(case=base_with_disjoint_changes(), data=st.data())
def test_a_plan_orders_its_changes_and_ignores_input_order(
    case: tuple[bytes, list[ByteChange]], data: st.DataObject
) -> None:
    """Planning normalizes to one canonical, offset-ordered change tuple."""
    base, changes = case
    shuffled = data.draw(st.permutations(changes))

    first = plan_changes(base, changes, profile_id="p", base_sha256=_sha256(base))
    second = plan_changes(base, shuffled, profile_id="p", base_sha256=_sha256(base))

    assert first.changes == second.changes
    assert [change.offset for change in first.changes] == sorted(
        change.offset for change in first.changes
    )


@SETTINGS
@given(case=base_with_disjoint_changes())
def test_applying_a_plan_changes_exactly_the_declared_bytes(
    case: tuple[bytes, list[ByteChange]],
) -> None:
    """The emitted image is the base with exactly the declared fields replaced."""
    base, changes = case
    plan = plan_changes(base, changes, profile_id="p", base_sha256=_sha256(base))

    expected = bytearray(base)
    for change in plan.effective_changes:
        expected[change.offset : change.end] = change.new
    emitted = apply_plan(base, plan)

    assert emitted == bytes(expected)
    allowed = {
        index
        for change in plan.effective_changes
        for index in range(change.offset, change.end)
    }
    assert {
        index
        for index, (before, after) in enumerate(zip(base, emitted))
        if before != after
    } <= allowed


@SETTINGS
@given(base=st.binary(min_size=1, max_size=_MAX_BASE), data=st.data())
def test_a_no_op_plan_reproduces_the_base(
    base: bytes, data: st.DataObject
) -> None:
    """Emitting nothing is byte-identical, whether empty or merely neutral."""
    empty = plan_changes(base, [], profile_id="p", base_sha256=_sha256(base))
    assert empty.is_noop
    assert apply_plan(base, empty) == base

    offset = data.draw(st.integers(min_value=0, max_value=len(base) - 1))
    size = data.draw(st.integers(min_value=1, max_value=len(base) - offset))
    neutral = _change(offset, base[offset : offset + size], base[offset : offset + size])
    neutral_plan = plan_changes(
        base, [neutral], profile_id="p", base_sha256=_sha256(base)
    )

    assert neutral_plan.is_noop
    assert apply_plan(base, neutral_plan) == base


@SETTINGS
@given(case=base_with_disjoint_changes())
def test_reverting_an_applied_plan_restores_the_base(
    case: tuple[bytes, list[ByteChange]],
) -> None:
    """Every change carries its own inverse, so a revert is exact."""
    base, changes = case
    plan = plan_changes(base, changes, profile_id="p", base_sha256=_sha256(base))
    emitted = apply_plan(base, plan)

    revert = [
        _change(change.offset, change.new, change.old, change.owner)
        for change in plan.effective_changes
    ]
    restored = apply_plan(
        emitted,
        plan_changes(emitted, revert, profile_id="p", base_sha256=_sha256(emitted)),
    )

    assert restored == base


@SETTINGS
@given(case=base_with_disjoint_changes())
def test_a_plan_is_refused_against_any_other_base(
    case: tuple[bytes, list[ByteChange]],
) -> None:
    """A plan cannot be applied to an image it was not computed from."""
    base, changes = case
    plan = plan_changes(base, changes, profile_id="p", base_sha256=_sha256(base))

    mutated = bytes([base[0] ^ 0xFF]) + base[1:]
    with pytest.raises(ChangeValidationError):
        apply_plan(mutated, plan)
    with pytest.raises(ChangeValidationError):
        apply_plan(base + b"\x00", plan)


@SETTINGS
@given(base=st.binary(min_size=2, max_size=_MAX_BASE), data=st.data())
def test_provenance_cannot_excuse_a_byte_outside_its_declared_fields(
    base: bytes, data: st.DataObject
) -> None:
    """A self-consistent manifest cannot widen what the image is allowed to say.

    The forged document below hashes the tampered image correctly and declares
    the same changes; only the byte-level reconstruction check catches it.
    """
    size = data.draw(st.integers(min_value=1, max_value=len(base) - 1))
    new = data.draw(st.binary(min_size=size, max_size=size))
    change = _change(0, base[:size], new)
    plan = plan_changes(base, [change], profile_id="p", base_sha256=_sha256(base))
    emitted = apply_plan(base, plan)

    manifest = WriteManifest(
        base_profile_id="p",
        base_sha256=_sha256(base),
        output_sha256=_sha256(emitted),
        output_size=len(emitted),
        changes=plan.effective_changes,
    )
    # Control: the image the plan produced is accepted.
    verify_emitted_image(base, emitted, plan.effective_changes, manifest)

    outside = data.draw(st.integers(min_value=size, max_value=len(base) - 1))
    tampered = bytearray(emitted)
    tampered[outside] ^= 0xFF
    forged = WriteManifest(
        base_profile_id="p",
        base_sha256=_sha256(base),
        output_sha256=_sha256(bytes(tampered)),
        output_size=len(tampered),
        changes=plan.effective_changes,
    )

    with pytest.raises(AuthoredImageError, match="outside the requested fields"):
        verify_emitted_image(base, bytes(tampered), plan.effective_changes, forged)
