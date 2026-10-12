"""The exact-search helpers: bitmasks, Gosper subsets, and the enumeration-versus-search guard.

The load-bearing test is `test_infeasibility_cannot_be_read_from_a_partial_walk`: the whole reason the
helper exists is that a greedy or union-find verdict was reported as a proof, and the property has to
refuse that reading rather than return a falsy value a caller can quote.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.research import exact_search as search  # noqa: E402


def test_masks_and_values_round_trip() -> None:
    assert search.values_of(search.mask_of([0, 3, 7])) == [0, 3, 7]
    assert search.mask_of([]) == 0
    assert search.values_of(0) == []
    with pytest.raises(ValueError):
        search.mask_of([-1])
    with pytest.raises(ValueError):
        search.values_of(-1)


def test_submasks_match_brute_force_and_are_descending() -> None:
    mask = 0b1011
    got = list(search.submasks(mask))
    brute = [value for value in range(1 << 4) if value & ~mask == 0 and value]
    assert sorted(got, reverse=True) == sorted(brute, reverse=True)
    assert got == sorted(got, reverse=True), "Gosper walks downward"
    assert list(search.submasks(mask, include_empty=True)) == [0] + got
    assert len(got) == 2 ** bin(mask).count("1") - 1, "every submask but the empty one"


def test_chunks_cut_a_palette_mask_into_banks_without_stopping_early() -> None:
    mask = 1 | (0x8000 << 240)
    banks = search.chunks_of(mask, 16, count=16)
    assert len(banks) == 16
    assert banks[0] == 0x0001 and banks[15] == 0x8000


def test_byte_and_halfword_masks_report_what_is_present() -> None:
    assert search.values_of(search.byte_values(b"\x00\x02\x02\xff")) == [0, 2, 255]
    assert search.values_of(search.halfword_values(b"\x01\x00\x00\x01\x07")) == [1, 256]


def test_an_exhaustive_walk_counts_every_state_and_keeps_the_first_witness() -> None:
    states = list(itertools.combinations(range(6), 3))
    result = search.enumerate_exact(states, lambda combo: sum(combo) == 7, size=len(states),
                                    label="triples summing to 7")
    assert result.states == 20 and result.matches == 3 and result.witness == (0, 2, 5)
    assert result.solved and not result.impossible
    assert "3 match(es) in 20 state(s), a witness exists" in result.report()


def test_a_walk_with_no_match_says_so_only_because_it_checked_everything() -> None:
    states = list(itertools.combinations(range(6), 3))
    result = search.enumerate_exact(states, lambda combo: sum(combo) == 100, size=len(states))
    assert result.impossible
    assert "no witness exists (exhaustive)" in result.report()


def test_infeasibility_cannot_be_read_from_a_partial_walk() -> None:
    partial = search.Enumeration(label="greedy", states=3, matches=0, witness=None, exhaustive=False)
    with pytest.raises(search.NotExhaustive, match="says nothing about infeasibility"):
        _ = partial.impossible
    assert "NOT exhaustive" in partial.report()


def test_a_space_over_the_limit_is_refused_before_any_work() -> None:
    with pytest.raises(search.EnumerationTooLarge, match="over the 10 enumeration limit"):
        search.enumerate_exact(iter(range(100)), lambda value: value == 1, size=100, limit=10,
                               label="a big space")
    with pytest.raises(search.EnumerationTooLarge, match="passed 10 states"):
        search.enumerate_exact(iter(range(100)), lambda value: value == 1, limit=10)


def test_a_declared_size_that_disagrees_with_the_walk_is_a_defect_not_a_result() -> None:
    with pytest.raises(AssertionError, match="declared 5 states and produced 3"):
        search.enumerate_exact(iter(range(3)), lambda value: False, size=5)
