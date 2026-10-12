"""Exact enumeration and bitmask helpers, so a search failure is never a proof.

WHY THIS EXISTS. Three sessions in a row answered a small feasibility question with a model, a greedy or a
union-find argument, and each answer was wrong: a greedy said "no two-bank assignment" on two frames where a
restart search found one immediately, a parameterised search asked about colours instead of cells, and a
union-find that assumed colours cannot repeat "proved" impossibility for six of eight frames. The constraint
was then solved exactly in one run each. The measured spaces were tiny - 54,264 A-subsets and 96 assignments
per subset - and enumeration settled them.

THE RULE, and it is the point of this module: if the space has fewer than about 10^6 candidate states,
enumerate it and report a certificate, and never report a heuristic verdict as a proof. A search that
stopped early, timed out, or could not fit its own guard has produced NO evidence about infeasibility.
:func:`enumerate_exact` therefore counts every state, and :attr:`Enumeration.impossible` refuses to be read
as a proof unless the enumeration was exhaustive.

WHAT IS HERE, and nothing else: bitmask construction and decomposition, Gosper's submask iteration (the
subset walk the joint-palette work needed), and the exact enumeration wrapper. It is pure: no I/O, no
filesystem, no ROM, so it can be used from a scratch probe and from a tracked tool alike.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Any, TypeVar

#: The state count above which enumeration needs a decision rather than a loop. Stated as a constant so a
#: caller can raise it deliberately and say so, instead of discovering the ceiling as a timeout.
DEFAULT_ENUMERATION_LIMIT = 1_000_000


class EnumerationTooLarge(ValueError):
    """Raised when a space over the enumeration limit was handed to the exact walker."""


class NotExhaustive(AssertionError):
    """Raised when a result that did not enumerate every state is read as an impossibility proof."""


def mask_of(values: Iterable[int]) -> int:
    """A bitmask with one bit per distinct value. Negative values are refused."""
    mask = 0
    for value in values:
        if value < 0:
            raise ValueError(f"a bitmask cannot hold the negative value {value}")
        mask |= 1 << value
    return mask


def values_of(mask: int) -> list[int]:
    """The set bits of ``mask``, lowest first."""
    if mask < 0:
        raise ValueError(f"a bitmask cannot be negative, got {mask}")
    return [index for index in range(mask.bit_length()) if mask >> index & 1]


def chunks_of(mask: int, width: int, *, count: int | None = None) -> list[int]:
    """``mask`` cut into ``width``-bit slices, low slice first.

    This is what turns a 256-entry palette-index mask into sixteen bank masks, which is the question the
    free-bank work asks; the slicing is stated once here rather than at each call site. With ``count`` the
    result always holds that many slices, zero-padded, so a bank walk cannot silently stop early because
    the top bank was unused.
    """
    if width <= 0:
        raise ValueError(f"a chunk width must be positive, got {width}")
    width_count = count if count is not None else -(-mask.bit_length() // width) or 1
    return [(mask >> (start * width)) & ((1 << width) - 1) for start in range(width_count)]


def byte_values(data: bytes) -> int:
    """The mask of byte values present in ``data``, one bit per value 0..255."""
    return mask_of(data)


def halfword_values(data: bytes) -> int:
    """The mask of 16-bit little-endian values present in ``data``.

    Truncates a trailing odd byte rather than inventing a halfword for it.
    """
    return mask_of(int.from_bytes(data[at:at + 2], "little") for at in range(0, len(data) - 1, 2))


def submasks(mask: int, *, include_empty: bool = False) -> Iterator[int]:
    """Every submask of ``mask``, by Gosper's hack, without materialising the list.

    A mask with ``n`` bits has ``2**n`` submasks, so a 16-bit bank mask is 65,536 states and a 20-bit one is
    over the enumeration limit - :func:`enumerate_exact` reports that, it does not silently stop. The order
    is descending, which is the order Gosper's hack produces; a caller that needs another order sorts.
    """
    if mask < 0:
        raise ValueError(f"a bitmask cannot be negative, got {mask}")
    if include_empty:
        yield 0
    current = mask
    while current:
        yield current
        current = (current - 1) & mask


Item = TypeVar("Item")


@dataclass(frozen=True)
class Enumeration:
    """The result of an exhaustive walk: how many states were checked and how many matched.

    ``witness`` is the first match, kept so a feasibility claim can cite a concrete assignment rather than
    an assertion that one exists.
    """

    label: str
    states: int
    matches: int
    witness: Any | None
    exhaustive: bool

    @property
    def solved(self) -> bool:
        return self.matches > 0

    @property
    def impossible(self) -> bool:
        """True only for an exhaustive walk with no match.

        Reading this on a partial walk is a defect rather than a result, so it raises instead of returning
        False: a caller that wants "not found yet" writes that, and does not borrow the word proof.
        """
        if not self.exhaustive:
            raise NotExhaustive(
                f"{self.label or 'this walk'} checked {self.states} state(s) and stopped before exhausting "
                "the space, so it says nothing about infeasibility"
            )
        return self.matches == 0

    def report(self) -> str:
        """One line safe to paste into a report or a review request."""
        if not self.exhaustive:
            return (f"{self.label or 'enumeration'}: {self.matches} match(es) in {self.states} state(s) "
                    "checked, NOT exhaustive")
        verdict = "a witness exists" if self.matches else "no witness exists (exhaustive)"
        return (f"{self.label or 'enumeration'}: {self.matches} match(es) in {self.states} state(s), "
                f"{verdict}")


def enumerate_exact(
    states: Iterable[Item],
    predicate: Callable[[Item], bool],
    *,
    size: int | None = None,
    limit: int = DEFAULT_ENUMERATION_LIMIT,
    label: str = "",
) -> Enumeration:
    """Every state, tested; the exact match count and the first witness.

    ``size`` is the caller's own count of the space when it knows one - a state count, not a byte count and
    not a guess. A known ``size`` over ``limit`` raises :class:`EnumerationTooLarge` before any work, which
    is the decision point: a space that large needs a counting argument or a different formulation, not a
    longer loop. An unknown size is walked to the end and reported with its real count.

    No early exit: the loop always runs the whole iterable. A witness does not stop it, because "one exists"
    and "how many exist" are different claims and the second is what makes the first useful.
    """
    if size is not None and size > limit:
        raise EnumerationTooLarge(
            f"{label or 'the space'} holds {size} states, over the {limit} enumeration limit; count it or "
            "reformulate it, and do not report a partial search as a proof"
        )
    checked = 0
    matches = 0
    witness: Any | None = None
    for state in states:
        checked += 1
        if checked > limit:
            raise EnumerationTooLarge(
                f"{label or 'the space'} passed {limit} states while being walked; the space is larger than "
                "this helper is for, so stop and count it instead"
            )
        if predicate(state):
            matches += 1
            if witness is None:
                witness = state
    if size is not None and checked != size:
        raise AssertionError(
            f"{label or 'the space'} declared {size} states and produced {checked}; one of the two is wrong"
        )
    return Enumeration(label=label, states=checked, matches=matches, witness=witness, exhaustive=True)
