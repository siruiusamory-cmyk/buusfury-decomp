"""Portable tests for the warp randomizer's policy. ROMHACK-WARP-RANDOMIZER-001.

Two layers are covered without a ROM:

* the seeded permutation and the dead-end guard - :func:`shuffled_indices`,
  :func:`guarded_matching` and :func:`normalize_seed`, which are pure functions of
  a seed, a group index and a pair shape and reach no image;
* the manifest's shape and its byte determinism, built here from hand-made
  decisions rather than from a corpus.

The structural test in the last section is the one that keeps this tool honest:
the offsets it declares randomizable must be real bytes of the 24-byte record the
codec owns, and the bytes it declares preserved must be the rest of them. That is
asserted against :data:`TRANSITION_LAYOUT` rather than restated, so a change to
the record's layout cannot leave this policy silently pointing at the wrong byte.

Everything that needs the canonical image - the counts, the byte safety, the
skipped reasons - lives in ``tests/integration/test_warp_randomizer_rom.py``.
"""

from __future__ import annotations

import json

import pytest

from tools.webfoot.formats.map_transitions import (
    TRANSITION_CLASS_A_RAW,
    TRANSITION_CLASS_B_RAW,
    TRANSITION_LAYOUT,
    TRANSITION_SIZE,
)
from tools.webfoot.warp_randomizer import (
    PAIR_GROUP_INDEX,
    POLICY_ID,
    PRESERVED_RECORD_OFFSETS,
    RANDOMIZED,
    RANDOMIZED_RECORD_OFFSETS,
    SKIPPED,
    TICKET,
    WarpGroupDecision,
    WarpRandomizerError,
    WarpRandomizerManifest,
    WarpRandomizerSeedError,
    WarpRecordDecision,
    guarded_matching,
    normalize_seed,
    shuffled_indices,
)

# --- the seed ----------------------------------------------------------------


def test_a_seed_is_identified_by_its_exact_text() -> None:
    """An integer seed is spelled, and a leading zero is not normalized away."""
    assert normalize_seed(1) == "1"
    assert normalize_seed("1") == "1"
    assert normalize_seed("01") == "01"
    assert normalize_seed(0) == "0"
    assert normalize_seed("cale-1") == "cale-1"


def test_a_leading_zero_seed_is_a_different_mapping() -> None:
    """The claim above, shown on the permutation rather than on the string."""
    assert shuffled_indices(3, seed="1", group=0) == (2, 0, 1)
    assert shuffled_indices(3, seed="01", group=0) == (1, 0, 2)


@pytest.mark.parametrize("seed", ["", None, 1.5, b"bytes", ["a"]])
def test_a_seed_that_is_not_a_non_empty_string_or_integer_is_refused(seed) -> None:
    with pytest.raises(WarpRandomizerSeedError):
        normalize_seed(seed)


def test_a_boolean_is_not_an_integer_seed() -> None:
    """``True`` is an ``int`` in Python and is refused as a typo, not spelled "True"."""
    with pytest.raises(WarpRandomizerSeedError):
        normalize_seed(True)


# --- the permutation ---------------------------------------------------------


def test_zero_and_one_element_shuffles_are_the_only_permutation_there_is() -> None:
    assert shuffled_indices(0, seed="any", group=0) == ()
    assert shuffled_indices(1, seed="any", group=0) == (0,)
    assert shuffled_indices(1, seed="other", group=99) == (0,)


@pytest.mark.parametrize("count", [2, 3, 5, 16, 64])
@pytest.mark.parametrize("seed", ["a", "b", "cale-1"])
def test_the_shuffle_is_always_a_permutation(count: int, seed: str) -> None:
    """Every draw keeps one of each index, whatever the seed is."""
    order = shuffled_indices(count, seed=seed, group=3)
    assert sorted(order) == list(range(count))
    assert len(order) == count


def test_the_shuffle_refuses_an_empty_seed_rather_than_seeding_on_it() -> None:
    with pytest.raises(WarpRandomizerSeedError):
        shuffled_indices(4, seed="", group=0)


def test_the_shuffle_is_deterministic_and_group_separated() -> None:
    """Same seed and group, same order; a different group is a different stream."""
    first = shuffled_indices(7, seed="cale-1", group=11)
    second = shuffled_indices(7, seed="cale-1", group=11)
    assert first == second
    other_group = shuffled_indices(7, seed="cale-1", group=12)
    assert other_group != first


def test_two_seeds_produce_different_orders() -> None:
    """Not merely "a stream exists": two named seeds disagree, order by order."""
    table = {
        "a": (2, 0, 1),
        "b": (0, 1, 2),
        "cale-1": (1, 0, 2),
        "cale-2": (0, 2, 1),
    }
    for seed, expected in table.items():
        assert shuffled_indices(3, seed=seed, group=7) == expected
    assert len(set(table.values())) == len(table)


def test_the_dead_end_guard_never_links_two_single_door_maps() -> None:
    """Policy /3's rule, proved without a ROM.

    Pairs 0 and 1 leave maps with exactly one door; pairs 2 and 3 leave hubs. A
    link between two single-door maps closes an isolated 2-cycle with no way on, so
    the guard must give the single-door pairs the hub targets.
    """
    order = (0, 1, 2, 3)
    forward = (True, True, False, False)
    returning = (True, True, False, False)
    targets, forced = guarded_matching(order, forward, returning)

    assert forced == 0
    assert sorted(targets) == [0, 1, 2, 3], "the matching must stay complete"
    assert targets[0] == 2 and targets[1] == 3
    for index, target in enumerate(targets):
        assert not (forward[index] and returning[target]), (index, target)


def test_the_guard_finds_a_matching_the_greedy_pass_would_miss() -> None:
    """The count is exact, not a greedy accident.

    Pair 0 may take only target 1 and pair 1 only target 0, while the greedy pass
    in seeded order hands pair 0 the only target it can see and leaves pair 1
    stuck. The augmenting search must move the earlier pair rather than relax the
    rule, so the reported count stays 0.
    """
    targets, forced = guarded_matching(
        (0, 1), (False, True), (False, True)
    )
    assert forced == 0
    assert sorted(targets) == [0, 1]
    assert targets[0] == 1 and targets[1] == 0


def test_an_unsatisfiable_guard_is_reported_rather_than_hidden() -> None:
    """Two single-door pairs and no hub target: the rule is relaxed and COUNTED.

    Every pair in the set then takes a link the guard would have refused, so the
    count is two - one per relaxed pair - and the matching is still complete.
    """
    order = (0, 1)
    forward = (True, True)
    returning = (True, True)
    targets, forced = guarded_matching(order, forward, returning)
    assert sorted(targets) == [0, 1]
    assert forced == 2, "each relaxed link must be visible in the manifest"


def test_a_pair_permutation_is_a_bijection_over_the_pairs() -> None:
    """The draw the guard consumes is still a permutation, not a sample.

    A permutation that repeated or dropped a pair would leave a door without a
    partner, which is the defect the reciprocal policy exists to remove; the guard
    only reorders WHICH pair takes which, and the matching test above proves it
    stays complete.
    """
    for count in (1, 2, 3, 16, 64):
        order = shuffled_indices(count, seed="cale-1", group=PAIR_GROUP_INDEX)
        assert sorted(order) == list(range(count))
        assert len(order) == count


# --- the manifest ------------------------------------------------------------


def decision(
    *,
    identity: str = "map:0040/transition:0000",
    disposition: str = RANDOMIZED,
    reason: str = "",
    randomized_destination: str | None = "map:0378",
    retail_arrival: tuple[int, int] | None = (8, 152),
    arrival: tuple[int, int] | None = (120, 96),
) -> WarpRecordDecision:
    return WarpRecordDecision(
        identity=identity,
        source_map_index=40,
        index=0,
        class_raw=TRANSITION_CLASS_A_RAW,
        class_label="A",
        retail_destination="map:0039",
        randomized_destination=randomized_destination,
        retail_arrival=retail_arrival,
        arrival=arrival,
        retail_facing_raw=0x02,
        randomized_facing_raw=0x32,
        arrival_facing=2,
        gate_direction=2,
        disposition=disposition,
        skip_reason=reason,
        changed=disposition == RANDOMIZED,
    )


def manifest(decisions: tuple[WarpRecordDecision, ...]) -> WarpRandomizerManifest:
    return WarpRandomizerManifest(
        seed="cale-1",
        profile_id="test_profile",
        base_sha256="0" * 64,
        base_size=0x100,
        decisions=decisions,
        groups=(
            WarpGroupDecision(
                label="clean-mutual-door-pairs",
                members=2 * max(1, len(decisions)),
                pairs=max(1, len(decisions)),
            ),
        ),
    )


def test_the_manifest_is_byte_deterministic() -> None:
    rows = (
        decision(),
        decision(
            identity="map:0041/transition:0000",
            disposition=SKIPPED,
            reason="the transition authority refused the bundle: no door",
            randomized_destination=None,
            arrival=None,
        ),
    )
    first = manifest(rows).to_json(output_sha256="a" * 64, output_size=0x100)
    second = manifest(rows).to_json(output_sha256="a" * 64, output_size=0x100)
    assert first == second
    assert first.endswith("\n")


def test_the_manifest_counts_dispositions_and_reasons() -> None:
    refused = "169-class record: a scene-relative delta"
    other = "no map leads back to this source map"
    rows = (
        decision(),
        decision(identity="map:0041/transition:0000", disposition=SKIPPED,
                 reason=refused, randomized_destination=None, arrival=None),
        decision(identity="map:0042/transition:0000", disposition=SKIPPED,
                 reason=refused, randomized_destination=None, arrival=None),
        decision(identity="map:0043/transition:0000", disposition=SKIPPED,
                 reason=other, randomized_destination=None, arrival=None),
    )
    counts = manifest(rows).summary(output_sha256="b" * 64)
    assert counts["supported_transitions"] == 4
    assert counts["randomized"] == 1
    assert counts["skipped"] == 3
    assert counts["skipped_by_reason"] == {refused: 2, other: 1}
    assert counts["groups_with_a_choice"] == 1
    assert counts["pairs"] == 4


def test_the_manifest_carries_no_filesystem_path() -> None:
    """A path would make the same seed's manifest differ between checkouts."""
    text = manifest((decision(),)).to_json(output_sha256="c" * 64, output_size=0x100)
    payload = json.loads(text)
    assert payload["ticket"] == TICKET
    assert payload["policy"]["id"] == POLICY_ID
    assert "path" not in json.dumps(payload["base_rom"])
    assert "path" not in json.dumps(payload["output_rom"])
    assert payload["base_rom"]["sha256"] == "0" * 64
    assert payload["output_rom"]["sha256"] == "c" * 64
    assert len(payload["records"]) == 1


def test_a_decision_renders_its_bytes_as_fixed_width_hex() -> None:
    row = decision().to_json()
    assert row["class_raw"] == "0x08007675"
    assert row["retail_facing_raw"] == "0x02"
    assert row["randomized_facing_raw"] == "0x32"
    assert row["retail_arrival"] == [8, 152]
    assert row["arrival"] == [120, 96]
    assert row["gate_direction"] == 2
    assert row["disposition"] == RANDOMIZED
    assert row["skip_reason"] == ""
    # A record that states no arrival reports both sides as null rather than
    # reporting the sentinel as a point; the 169 class is exactly this case.
    sentinel = decision(retail_arrival=None).to_json()
    assert sentinel["retail_arrival"] is None
    # A skipped row carries no randomized bundle at all, which is what makes
    # "left unchanged" checkable from the manifest alone.
    skipped = decision(
        disposition=SKIPPED, reason="why", randomized_destination=None, arrival=None
    ).to_json()
    assert skipped["randomized_destination"] is None
    assert skipped["arrival"] is None
    assert skipped["skip_reason"] == "why"


# --- the policy against the codec --------------------------------------------


def test_the_declared_offsets_partition_the_record() -> None:
    """Every byte of the 24-byte record is either randomized or preserved."""
    randomized = set(RANDOMIZED_RECORD_OFFSETS)
    preserved = set(PRESERVED_RECORD_OFFSETS)
    assert randomized & preserved == set()
    assert randomized | preserved == set(range(TRANSITION_SIZE))
    assert (0x10 in randomized) and (0x13 in preserved)
    # The arrival's x is a halfword, so both of its bytes are randomizable.
    assert {0x14, 0x15} <= randomized


def test_every_declared_offset_lies_inside_a_real_field() -> None:
    for offset in RANDOMIZED_RECORD_OFFSETS + PRESERVED_RECORD_OFFSETS:
        owners = [
            item.name
            for item in TRANSITION_LAYOUT
            if item.offset <= offset < item.offset + item.width
        ]
        assert len(owners) == 1, (offset, owners)


def test_the_class_labels_cover_exactly_the_two_measured_class_words() -> None:
    """A class word the codec does not measure has no policy here."""
    from tools.webfoot.warp_randomizer import CLASS_LABELS, _class_label

    assert set(CLASS_LABELS) == {TRANSITION_CLASS_A_RAW, TRANSITION_CLASS_B_RAW}
    assert _class_label(TRANSITION_CLASS_A_RAW) == "A"
    assert _class_label(TRANSITION_CLASS_B_RAW) == "B"
    with pytest.raises(WarpRandomizerError):
        _class_label(0x08001234)
