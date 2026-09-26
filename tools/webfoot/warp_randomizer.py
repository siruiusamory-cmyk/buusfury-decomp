"""ROMHACK-WARP-RANDOMIZER-001 - a seeded warp randomizer over the proven family.

**This is a side-hack tool, not a capability.** It adds no Workbench surface,
changes no DragonByte Z capability count and performs no new reverse engineering:
every fact it uses is already measured and carried by
:mod:`tools.webfoot.map_transitions` and
:mod:`tools.webfoot.formats.map_transitions`. It randomizes *nothing* on its own
authority - it stages edits through the one transition authority and lets that
authority's own refusals decide what is safe.

What it randomizes
==================

The supported family is the one the authority loads: the 24-byte selector-1-root
connection records. On the canonical Buu's Fury image that is **735** records.

A randomizable object is a **destination bundle**, not a destination map. This
ticket forbids shuffling the destination alone, and the reason is measured: the
record also carries the point the player is placed at in the destination and the
arrival-facing override, and a destination edit that leaves those behind places
the player using the *previous* destination's geometry. So one bundle is the
triple

* the destination ``MapEntry`` key at ``+0x11``/``+0x12``;
* the arrival point at ``+0x14``/``+0x16``;
* the arrival-facing override in ``+0x10``'s high nibble.

Everything else in the record is the **source trigger** and is preserved
byte-for-byte: ``+0x00`` and ``+0x04``, the two ordered intervals at
``+0x08``..``+0x0F``, ``+0x13``, and - importantly - the low two bits of
``+0x10``, which are the door gate rather than the arrival facing. The authority's
own ``set_facing`` writes only the high nibble for exactly that reason.

Classes
=======

The record corpus contains two class words and the authority proves they are not
interchangeable: the **566 class** passes its ``+0x14``/``+0x16`` pair to the warp
routine as the arrival itself, while the **169 class** reads the same pair as a
scene-relative delta and adds the scene origin to it. An arrival can therefore be
authored only on the 566 class, and ``set_arrival`` refuses the other class
outright. A 169-class record is left unchanged and reported, because randomizing
its destination alone is the half-edit this ticket forbids.

The policy: reciprocal door pairs
================================

The permutation unit is a **clean mutual door pair**: two records, ``f: X -> Y``
and ``r: Y -> X``, where each is the other's only door back and both can carry an
arrival. The canonical corpus holds 248 of them, covering 496 of the 735 records.
A seeded Fisher-Yates draw over the pair set chooses which pair's maps each pair
moves to, and the two halves of a pair always move together: ``f`` arrives on
``r``'s own trigger rectangle and ``r`` on ``f``'s. So the door a player arrives on
is always the door that leads back - retail's own shape, and the rule the external
practice states outright (the OoT Entrance Randomizer keeps "all entrances
bidirectional").

An earlier revision permuted one record's destination at a time. That let an
arrival land inside a door the permutation had pointed somewhere else, and a player
who arrives inside a trigger never crosses its edge, so it never fires: 168 of 559
arrivals did that and a human playthrough was trapped in a loop. Reciprocity is
what removes that class.

A **dead-end guard** then refuses to link two maps that each hold exactly one door
record: such a link is an isolated 2-cycle with no way on, which a player entering
from a scripted transition cannot leave, and the second playthrough hit exactly
that. The guard is a rule about the door graph's topology, not progression logic -
it does not guarantee a route, a hub can still lead into a pocket, and
:attr:`WarpRandomizerManifest.forced_leaf_links` reports how often it had to be
relaxed so a bypassed rule cannot pass as a satisfied one.

A record that is not half of a clean pair is left byte-identical with its own
stated reason: 169 are the 169-class, and 70 have no clean mutual pair.

Determinism
===========

The permutation is drawn from SHA-256, not from a library PRNG, so the mapping
does not depend on an implementation detail of ``random``: group ``g``'s shuffle
draws ``sha256(domain | seed | g | i)`` for each Fisher-Yates step ``i``, and the
guard consumes that order rather than a second source. The same seed and the same
image therefore produce the same mapping, the same manifest bytes and the same
output bytes, on any machine.

Three views of one image
========================

They are deliberate, and each exists for a reason the other two cannot serve.
``canonical`` is read-only and supplies the retail graph, the door pairs and the
arrival points. ``staged`` receives the edits and produces the byte plan. And
``validator`` carries each planned pair through the authority's own ``set_arrival``
before a byte is staged, because deriving from the edited object would make an
arrival depend on which other records had already moved, while validating on
``staged`` would leave a half-written record behind when the authority refuses.

Safety
======

:func:`plan_warp_randomization` is pure over an in-memory image and returns a
:class:`~tools.webfoot.write.WritePlan`; nothing here writes a file. The driver
:func:`emit_randomized_rom` applies that plan through ``webfoot.write.emit_image``,
which is the only writer: it opens the canonical image read-only, refuses to
overwrite an output, and re-checks the base identity. This tool never guarantees
that the result is playable; progression logic is out of scope by the ticket.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

from . import capability
from .binary import BinaryAddressError
from .formats.map_transitions import (
    FACING_MASK,
    TRANSITION_CLASS_A_RAW,
    TRANSITION_CLASS_B_RAW,
    TransitionArrival,
)
from .map_transitions import (
    MapIdentity,
    MapTransitions,
    MapTransitionsError,
    TransitionEntry,
    TransitionIdentity,
    read_map_transitions,
)
from .profile import RomProfile, RomProfileCatalog
from .write import WritePlan, emit_image

#: The manifest schema this module writes.
SCHEMA_VERSION = 1

#: The ticket this tool exists for.
TICKET = "ROMHACK-WARP-RANDOMIZER-001"

#: The policy id, recorded in every manifest so a mapping names the rule that
#: produced it. Bump it when the rule changes: a seed alone does not identify a
#: mapping if the algorithm behind it moved.
#:
#: ``/1`` permuted a source map's destination *maps* one record at a time. That
#: broke reciprocity: a record could arrive on a door the permutation had pointed
#: somewhere else, and a player who arrives inside a trigger never crosses its
#: edge, so that door never fires. A human playthrough was trapped in exactly that
#: loop on 2026-09-26, and a census found 168 of 559 arrivals sitting on a door
#: that now led elsewhere.
#:
#: ``/2`` permutes whole **reciprocal door pairs** instead, so the door a player
#: arrives on is always the door that leads back. That is retail's own shape and
#: the rule the external practice states outright - the OoT Entrance Randomizer
#: keeps "all entrances bidirectional", and the ALttP Door Randomizer ships the
#: same discipline for 2D doors.
#: ``/3`` adds the **leaf-link guard**. A map with exactly one door record is a
#: dead end on its own: if the permutation links two of them, the pair becomes an
#: isolated 2-cycle and a player who entered from a scripted transition has no way
#: on - which is what happened on the first `/2` playthrough, where a door out of
#: map 33 landed on map 390 and map 390's only door came straight back. Retail never
#: does this: of its canonical single-door pairs, 67 lead to a hub and only 2 are
#: dead-end-to-dead-end. The guard refuses that one shape.
#:
#: It is a rule about the door graph's topology, NOT progression logic: it knows
#: nothing about items, flags or story order, and it does **not** guarantee a route
#: - a hub can still lead into a pocket. Reachability logic stays out of scope.
POLICY_ID = "reciprocal-door-pairs/3"

#: Domain separation for the SHA-256 permutation stream. Two tools may share a
#: seed string without sharing a mapping.
SEED_DOMAIN = b"log1-remake/ROMHACK-WARP-RANDOMIZER-001/permutation"

#: The one permutation group this policy draws from. Fixed, because the group is
#: the whole compatibility class; see :class:`WarpGroupDecision`.
PAIR_GROUP_INDEX = 0

#: The record bytes a randomized bundle is allowed to rewrite, by offset within
#: the 24-byte record. ``+0x10`` appears because its HIGH nibble carries the
#: arrival-facing override; its low two bits are the door gate and are copied
#: through unchanged. ``+0x14`` and ``+0x15`` are the two bytes of the arrival's
#: ``x`` halfword, which is why both are listed.
RANDOMIZED_RECORD_OFFSETS = (0x10, 0x11, 0x12, 0x14, 0x15, 0x16, 0x17)

#: The record bytes no randomized bundle may touch: the class word, the invariant
#: word, both ordered intervals - which are the source trigger region the ticket
#: requires to stay in place - and the unresolved byte at ``+0x13``. ``+0x10`` is
#: deliberately absent because only half of it is preserved, and that half is
#: asserted separately by masking.
PRESERVED_RECORD_OFFSETS = (0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                            0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x13)

#: ``+0x10``'s preserved half: the door gate, as opposed to the arrival facing.
#: The mask is the codec's own ``FACING_MASK``; this module never restates it.
GATE_MASK = FACING_MASK

#: The two dispositions a record can carry.
RANDOMIZED = "randomized"
SKIPPED = "skipped"

#: The positional class labels. Which class word means what is UNRESOLVED; what
#: is proved is the *difference* between them, so the labels stay positional.
CLASS_LABELS: Mapping[int, str] = {
    TRANSITION_CLASS_A_RAW: "A",
    TRANSITION_CLASS_B_RAW: "B",
}

#: A 169-class record whose arrival is a scene-relative delta.
REASON_SCENE_RELATIVE_ARRIVAL = (
    "169-class record: +0x14/+0x16 is a scene-relative delta, so an arrival "
    "cannot be authored and randomizing the destination alone is forbidden"
)

#: A source map nothing in the corpus canonically routes back to, or any other
#: record that is not half of a clean mutual door pair.
#:
#: A pair is clean when the record has exactly one door back, that door's own door
#: back is the record, and both halves can carry an arrival. Only then can the two
#: destinations be moved together while keeping every arrival on a door that leads
#: back; anything else would be a retarget whose arrival the engine cannot be
#: shown to honour, which is the defect this policy exists to remove.
REASON_NO_RECIPROCAL_PAIR = (
    "the record is not half of a clean mutual door pair (exactly one door back, "
    "reciprocal, both halves arrival-authorable), so a retarget could not keep its "
    "arrival on a door that leads back"
)

#: A retail destination key that names no map in this profile's table.
REASON_UNRESOLVED_RETAIL_DESTINATION = (
    "the record's retail destination key resolves to no map in this profile's "
    "table, so the retail side of the bundle cannot be reported"
)


class WarpRandomizerError(ValueError):
    """Base error for the warp randomizer."""


class WarpRandomizerSeedError(WarpRandomizerError):
    """Raised for a seed this tool cannot use."""


#: What a bundle derivation or an arrival check can raise. ``BinaryAddressError``
#: is included deliberately: ``destination_bounds`` resolves the destination's
#: walkable extent through the engine's own word, and an image the profile's map
#: table cannot describe makes that unreachable. That is a record this tool cannot
#: randomize, so it is reported and skipped rather than aborting the run.
BUNDLE_REFUSALS = (MapTransitionsError, BinaryAddressError)


# --- the permutation: pure, hash-drawn, ROM-free -----------------------------


def normalize_seed(seed: str | int) -> str:
    """The exact string a seed is identified by.

    No normalization beyond ``str()`` for an integer: ``"01"`` and ``"1"`` are
    different seeds, because a caller who writes a leading zero means it. The
    empty string is refused rather than silently seeded, since "" and a typo are
    indistinguishable in a manifest.
    """
    if isinstance(seed, bool) or not isinstance(seed, (str, int)):
        raise WarpRandomizerSeedError(
            f"a seed is a string or an integer, got {seed!r}"
        )
    text = str(seed)
    if not text:
        raise WarpRandomizerSeedError("a seed must not be empty")
    return text


def _draw(seed: str, group: int, step: int) -> int:
    """One deterministic draw from the seed's stream. See the module docstring."""
    material = (
        SEED_DOMAIN
        + b"|seed|"
        + seed.encode("utf-8")
        + b"|group|"
        + str(group).encode("ascii")
        + b"|step|"
        + str(step).encode("ascii")
    )
    return int.from_bytes(hashlib.sha256(material).digest(), "big")


def shuffled_indices(count: int, *, seed: str, group: int) -> tuple[int, ...]:
    """A seeded Fisher-Yates permutation of ``range(count)``.

    Pure and total: ``count <= 1`` returns the only permutation there is, so a
    single-candidate group consumes no seed material and is identical under every
    seed - which is what makes "different seeds differ" a claim about the groups
    that actually have a choice. The seed is put through :func:`normalize_seed`
    here too, so the pure helper refuses an empty seed exactly as the planner
    does rather than silently seeding on "".
    """
    if type(count) is not int or count < 0:
        raise WarpRandomizerError(f"a permutation size is a non-negative int, got {count!r}")
    seed = normalize_seed(seed)
    order = list(range(count))
    for index in range(count - 1, 0, -1):
        swap = _draw(seed, group, index) % (index + 1)
        order[index], order[swap] = order[swap], order[index]
    return tuple(order)


def guarded_matching(
    order: Sequence[int],
    forward_single_door: Sequence[bool],
    return_single_door: Sequence[bool],
) -> tuple[tuple[int, ...], int]:
    """Give every pair a distinct target pair, refusing dead-end-to-dead-end links.

    ``order`` is the seeded permutation of pair indices and is the preference order
    every pair draws from; ``forward_single_door[i]`` says pair ``i``'s forward map
    has exactly one door record, and ``return_single_door[j]`` the same for pair
    ``j``'s return map. Linking pair ``i`` to pair ``j`` joins those two maps, so
    the guard refuses the case where BOTH are single-door: the link would close a
    2-cycle between two dead ends.

    Returns the chosen target per pair and how many pairs had to take a target the
    guard would have refused. That count is exact rather than a greedy accident: the
    greedy pass is followed by an augmenting-path search over the allowed links, so
    a non-zero count means no guard-honouring matching of this pair set exists, not
    merely that the first pass failed to find one. The search is complete for this
    bipartite graph and every pass is over a list in a fixed order, so the result
    depends on ``order`` alone.

    Pure, so the rule is proved without a ROM.
    """
    count = len(order)
    forward_single_door = tuple(forward_single_door)
    return_single_door = tuple(return_single_door)

    def allowed(index: int, candidate: int) -> bool:
        return not (forward_single_door[index] and return_single_door[candidate])

    # Pass 1 - the greedy choice, allowed links only, in the seeded order.
    holder: dict[int, int] = {}
    unmatched: list[int] = []
    for index in range(count):
        choice = next(
            (c for c in order if c not in holder and allowed(index, c)), -1
        )
        if choice < 0:
            unmatched.append(index)
        else:
            holder[choice] = index

    # Pass 2 - augmenting paths. A pair the greedy pass could not place may still
    # be placeable by moving an earlier pair, and this finds it if it exists.
    def augment(index: int, seen: set[int]) -> bool:
        for candidate in order:
            if candidate in seen or not allowed(index, candidate):
                continue
            seen.add(candidate)
            displaced = holder.get(candidate)
            if displaced is None or augment(displaced, seen):
                holder[candidate] = index
                return True
        return False

    still_unmatched = [index for index in unmatched if not augment(index, set())]

    # Pass 3 - whatever is left has no allowed target, so the rule is relaxed for
    # it and counted. The matching stays complete: every pair still gets a target.
    for index in still_unmatched:
        free = next(candidate for candidate in order if candidate not in holder)
        holder[free] = index

    targets = [-1] * count
    for candidate in sorted(holder):
        targets[holder[candidate]] = candidate
    return tuple(targets), len(still_unmatched)


# --- the manifest: pure data -------------------------------------------------


@dataclass(frozen=True, slots=True)
class WarpRecordDecision:
    """One supported record and what the randomizer did with it.

    Everything a reviewer needs is here: the identity, the **whole retail bundle**
    (destination, arrival and facing byte), the randomized bundle, the class, and -
    for a record left alone - the reason. The two destination fields are the
    two-byte keys' *map* identities, because that is the only thing the engine
    resolves from the record; the raw key bytes are derivable from the map and are
    not restated.

    ``retail_arrival`` is the canonical ``+0x14``/``+0x16`` point, or ``None``
    when the record states no arrival: the sentinel for the 566 class, and always
    for the 169 class, whose stored pair is a scene-relative delta rather than a
    point and must not be reported as one. It is here so that "did the arrival
    move?" is answerable from the manifest alone instead of only from the build
    provenance.
    """

    identity: str
    source_map_index: int
    index: int
    class_raw: int
    class_label: str
    retail_destination: str | None
    randomized_destination: str | None
    retail_arrival: tuple[int, int] | None
    arrival: tuple[int, int] | None
    retail_facing_raw: int
    randomized_facing_raw: int
    arrival_facing: int | None
    gate_direction: int
    disposition: str
    skip_reason: str
    changed: bool
    #: The reciprocal pair this record was permuted as, and its other half. Both
    #: are ``None`` for a record the policy left alone. ``counterpart`` is what
    #: makes the manifest checkable on its own: the two rows name each other.
    pair: str | None = None
    counterpart: str | None = None

    def to_json(self) -> dict:
        return {
            "transition": self.identity,
            "source_map": self.source_map_index,
            "index": self.index,
            "class_raw": f"0x{self.class_raw:08X}",
            "class": self.class_label,
            "retail_destination": self.retail_destination,
            "randomized_destination": self.randomized_destination,
            "retail_arrival": (
                list(self.retail_arrival) if self.retail_arrival is not None else None
            ),
            "arrival": list(self.arrival) if self.arrival is not None else None,
            "retail_facing_raw": f"0x{self.retail_facing_raw:02X}",
            "randomized_facing_raw": f"0x{self.randomized_facing_raw:02X}",
            "arrival_facing": self.arrival_facing,
            "gate_direction": self.gate_direction,
            "disposition": self.disposition,
            "skip_reason": self.skip_reason,
            "changed": self.changed,
            "pair": self.pair,
            "counterpart": self.counterpart,
        }


@dataclass(frozen=True, slots=True)
class WarpGroupDecision:
    """One compatibility class and the pairs permuted inside it.

    The class is the whole set of clean mutual door pairs, and that is deliberate
    rather than lazy. A pair is compatible with every other pair by construction -
    both halves can carry an arrival, and each is the other's single door back - so
    the structure itself is the compatibility, and it says nothing about which maps
    a pair may be exchanged with. The alternative, grouping by the forward record's
    source map, was measured first: it leaves 175 of 207 groups holding a single
    pair, so the permutation can only be the identity, and just 46 of 496
    destinations moved. ``members`` is the record count (two per pair); ``pairs``
    is the number of permuted units.
    """

    label: str
    members: int
    pairs: int

    def to_json(self) -> dict:
        return {
            "group": self.label,
            "members": self.members,
            "pairs": self.pairs,
        }


@dataclass(frozen=True, slots=True)
class WarpRandomizerManifest:
    """The whole deterministic record of one seeded mapping."""

    seed: str
    profile_id: str
    base_sha256: str
    base_size: int
    decisions: tuple[WarpRecordDecision, ...]
    groups: tuple[WarpGroupDecision, ...]
    #: How many pairs had to accept a dead-end-to-dead-end link because the guard
    #: could not be honoured without leaving another pair unassigned. Zero is the
    #: satisfying answer; anything else says the rule was relaxed and by how much.
    forced_leaf_links: int = 0

    # --- counts ---------------------------------------------------------

    @property
    def supported(self) -> int:
        return len(self.decisions)

    @property
    def randomized(self) -> tuple[WarpRecordDecision, ...]:
        return tuple(item for item in self.decisions if item.disposition == RANDOMIZED)

    @property
    def skipped(self) -> tuple[WarpRecordDecision, ...]:
        return tuple(item for item in self.decisions if item.disposition == SKIPPED)

    def skipped_by_reason(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.skipped:
            counts[item.skip_reason] = counts.get(item.skip_reason, 0) + 1
        return counts

    @property
    def class_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.decisions:
            counts[item.class_label] = counts.get(item.class_label, 0) + 1
        return counts

    def summary(self, *, output_sha256: str | None = None) -> dict:
        """The counting half of the manifest, without the 735 rows."""
        randomized = self.randomized
        changed = sum(1 for item in randomized if item.changed)
        destinations_changed = sum(
            1 for item in randomized
            if item.randomized_destination != item.retail_destination
        )
        stated_by_retail = sum(
            1 for item in self.decisions if (item.retail_facing_raw >> 4) != 0
        )
        forced = sum(
            1 for item in randomized if (item.randomized_facing_raw >> 4) != 0
        )
        return {
            "ticket": TICKET,
            "policy_id": POLICY_ID,
            "seed": self.seed,
            "profile": self.profile_id,
            "base_sha256": self.base_sha256,
            "output_sha256": output_sha256,
            "supported_transitions": self.supported,
            "class_counts": self.class_counts,
            "randomized": len(randomized),
            "destinations_changed": destinations_changed,
            "destinations_unchanged": len(randomized) - destinations_changed,
            "records_with_changed_bytes": changed,
            "records_with_unchanged_bytes": len(randomized) - changed,
            "arrival_facing_stated_by_retail": stated_by_retail,
            "arrival_facing_forced_by_randomizer": forced,
            "skipped": len(self.skipped),
            "skipped_by_reason": self.skipped_by_reason(),
            "groups": len(self.groups),
            "pairs": sum(group.pairs for group in self.groups),
            "groups_with_a_choice": sum(1 for g in self.groups if g.pairs > 1),
            "forced_dead_end_links": self.forced_leaf_links,
        }

    def to_json(self, *, output_sha256: str, output_size: int) -> str:
        """The manifest as deterministic JSON text, LF-terminated.

        Only hashes and counts travel here - no filesystem path - so the same
        seed over the same image produces the same bytes wherever it is run.
        """
        payload = {
            "schema_version": SCHEMA_VERSION,
            "ticket": TICKET,
            "policy": {
                "id": POLICY_ID,
                "randomized_fields": [
                    "destination_key_high",
                    "destination_key_low",
                    "byte_0x10_raw (high nibble: arrival facing)",
                    "word_0x14_raw",
                    "byte_0x16_raw",
                    "byte_0x17_raw",
                ],
                "preserved_fields": [
                    "class_raw",
                    "constant_raw",
                    "bound_a_raw",
                    "bound_b_raw",
                    "bound_c_raw",
                    "bound_d_raw",
                    "byte_0x10_raw (low two bits: door gate)",
                    "byte_0x13_raw",
                ],
                "randomized_offsets": [f"0x{v:02X}" for v in RANDOMIZED_RECORD_OFFSETS],
                "preserved_offsets": [f"0x{v:02X}" for v in PRESERVED_RECORD_OFFSETS],
                "grouping": (
                    "one compatibility class - the clean mutual door pairs - "
                    "permuted as a single seeded bijection. Grouping the pairs by "
                    "the forward record's source map was measured and rejected: "
                    "175 of 207 such groups hold a single pair, so the draw could "
                    "only be the identity and just 46 of 496 destinations moved. "
                    "A pair is only moved when both halves are arrival-authorable "
                    "and each is the other's single door back"
                ),
                "eligibility": (
                    "a record whose +0x14/+0x16 pair is an absolute arrival AND "
                    "that is half of a clean mutual door pair; the 169 class stores "
                    "a scene-relative delta and a record with no reciprocal partner "
                    "is left unchanged, each with its own reported reason"
                ),
                "assignment": (
                    "seeded Fisher-Yates over the group's pairs; the two halves of "
                    "a pair always move together, which is what keeps the mapping "
                    "bidirectional"
                ),
                "arrival": (
                    "the destination's own door back - the paired record's region "
                    "centre, a point inside the door the player will use to return, "
                    "checked against the destination's walkable extent. This is "
                    "retail's own arrival shape: the player stands where they "
                    "stepped through rather than on an unrelated trigger"
                ),
                "reciprocity": (
                    "preserved by construction and proved in the tests: for every "
                    "randomized record the destination holds a record leading back "
                    "to its source. The OoT Entrance Randomizer states the same "
                    "rule - all entrances are kept bidirectional"
                ),
                "dead_end_guard": (
                    "a map with exactly one door record is a dead end, so the "
                    "permutation refuses to link two of them: that shape closes an "
                    "isolated 2-cycle with no way on, which a scripted entrance "
                    "cannot escape. It is a rule about the door graph's topology, "
                    "not progression logic, and it does not guarantee a route"
                ),
                "facing": (
                    "the authority's default arrival facing (away from the nearest "
                    "edge), an authoring default rather than engine law; the door "
                    "gate bits are preserved from the record"
                ),
                "progression": (
                    "no beatability, reachability or progression guarantee; this "
                    "tool randomizes structure only"
                ),
            },
            "seed": {"given": self.seed, "domain": SEED_DOMAIN.decode("ascii")},
            "base_rom": {
                "profile": self.profile_id,
                "sha256": self.base_sha256,
                "size": self.base_size,
            },
            "output_rom": {"sha256": output_sha256, "size": output_size},
            "counts": self.summary(output_sha256=output_sha256),
            "groups": [group.to_json() for group in self.groups],
            "records": [item.to_json() for item in self.decisions],
        }
        return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class WarpRandomization:
    """One seeded randomization: the record of it and the plan that applies it."""

    manifest: WarpRandomizerManifest
    write_plan: WritePlan


# --- the plan ----------------------------------------------------------------


def _class_label(class_raw: int) -> str:
    try:
        return CLASS_LABELS[class_raw]
    except KeyError:
        raise WarpRandomizerError(
            f"class word {class_raw:#010x} is not one of the two the authority "
            "loads; this tool has no policy for it"
        ) from None


def _retail_destination(
    canonical: MapTransitions, identity: TransitionIdentity
) -> MapIdentity | None:
    """The map this record leads to, or None when its key resolves to nothing."""
    try:
        return canonical.destination(identity)
    except MapTransitionsError:
        return None


def _doors_back(
    canonical: MapTransitions,
    retail: Mapping[str, MapIdentity | None],
    identity: TransitionIdentity,
) -> tuple[TransitionIdentity, ...]:
    """The destination's own records that lead back to this record's source map."""
    target = retail[identity.key]
    if target is None:
        return ()
    return tuple(
        entry.identity
        for entry in canonical.for_map(target)
        if retail[entry.identity.key] == identity.source
    )


def _mutual_pairs(
    canonical: MapTransitions,
    eligible: tuple[TransitionIdentity, ...],
    retail: Mapping[str, MapIdentity | None],
) -> tuple[tuple[TransitionIdentity, TransitionIdentity], ...]:
    """Every clean reciprocal door pair, in deterministic order.

    Clean means: the record has exactly one door back, that door's own door back is
    the record, both halves are arrival-authorable, and neither is a self-link (a
    record cannot be its own counterpart). A pair is returned as
    ``(forward, return)`` ordered by (source map, index), so "forward" is a
    deterministic label rather than a semantic claim.

    Only these pairs can be permuted while keeping every arrival on a door that
    leads back, which is the property the external practice states and the reason
    this policy exists.
    """
    doors = {entry.key: _doors_back(canonical, retail, entry) for entry in eligible}
    eligible_keys = {entry.key for entry in eligible}
    pairs: list[tuple[TransitionIdentity, TransitionIdentity]] = []
    used: set[str] = set()
    for identity in sorted(eligible, key=lambda item: (item.source.index, item.index)):
        if identity.key in used:
            continue
        back = doors[identity.key]
        if len(back) != 1:
            continue
        other = back[0]
        if other.key == identity.key or other.key not in eligible_keys or other.key in used:
            continue
        if doors[other.key] != (identity,):
            continue
        forward, returning = sorted(
            (identity, other), key=lambda item: (item.source.index, item.index)
        )
        pairs.append((forward, returning))
        used.update((identity.key, other.key))
    return tuple(pairs)


def plan_warp_randomization(
    image: bytes, profile: RomProfile, seed: str | int
) -> WarpRandomization:
    """Randomize every safely randomizable transition in ``image``.

    Pure over ``image``: it reads bytes and returns a plan. Nothing is written and
    ``image`` is never mutated. See the module docstring for the policy.

    A record the policy cannot randomize is left byte-identical and carries its
    reason in the manifest. Every accepted pair is validated on a *third* view of
    the same image before a byte is staged on the output view, so a refusal the
    authority raises leaves nothing half-written: a record can never end up with a
    new destination and the previous destination's arrival.
    """
    text = normalize_seed(seed)
    canonical = read_map_transitions(image, profile)
    staged = read_map_transitions(image, profile)
    validator = read_map_transitions(image, profile)

    entries = list(canonical.entries())
    by_key = {entry.identity.key: entry for entry in entries}
    # Resolved once, read everywhere: the retail side of every row, the pair
    # search, and the point a pair's arrival is taken from.
    retail: dict[str, MapIdentity | None] = {
        entry.identity.key: _retail_destination(canonical, entry.identity)
        for entry in entries
    }
    eligible = tuple(
        entry.identity
        for entry in entries
        if entry.record.has_raw_arrival_pair and retail[entry.identity.key] is not None
    )

    pairs = _mutual_pairs(canonical, eligible, retail)

    # The assignment: one seeded bijection over the pair set. A pair's two halves
    # always move together, so every arrival lands on the door that leads back.
    accepted: list[tuple[TransitionIdentity, TransitionIdentity, int]] = []
    refusal: dict[str, str] = {}
    groups: list[WarpGroupDecision] = []
    if pairs:
        groups.append(
            WarpGroupDecision(
                label="clean-mutual-door-pairs",
                members=2 * len(pairs),
                pairs=len(pairs),
            )
        )
    order = shuffled_indices(len(pairs), seed=text, group=PAIR_GROUP_INDEX)
    forward_single = tuple(
        len(canonical.for_map(pair[0].source)) == 1 for pair in pairs
    )
    return_single = tuple(
        len(canonical.for_map(pair[1].source)) == 1 for pair in pairs
    )
    targets, forced_leaf_links = guarded_matching(order, forward_single, return_single)
    for index, target_index in enumerate(targets):
        forward, returning = pairs[index]
        host, host_return = pairs[target_index]
        # forward -> the map the OTHER pair's return door sits in, arriving on
        # that door; that pair's return door -> forward's map, arriving on
        # forward's door. Both arrivals are region centres of a real door, so
        # every arrival is on the door that leads back.
        moves = (
            (forward, host_return.source, by_key[host_return.key]),
            (host_return, forward.source, by_key[forward.key]),
        )
        ok = True
        for identity, destination, arrival_entry in moves:
            point = _region_centre(arrival_entry.record.region)
            try:
                validator.set_destination(identity, destination)
                validator.set_arrival(identity, point)
            except BUNDLE_REFUSALS as exc:
                refusal[forward.key] = refusal[host_return.key] = (
                    f"the transition authority refused the bundle: {exc}"
                )
                ok = False
                break
        if ok:
            accepted.append((forward, host_return, target_index))

    # What each accepted record will carry, keyed by identity: the map the pair
    # moved it to, the point on that map's return door, the facing, and the pair
    # label the manifest reports.
    planned: dict[str, tuple[MapIdentity, TransitionArrival, int, str, str]] = {}
    for number, (forward, returning, _target) in enumerate(accepted, start=1):
        label = f"pair:{number:04d}"
        for identity, partner in ((forward, returning), (returning, forward)):
            # The record moves to the map its partner's door sits in, and arrives
            # ON that door: the partner's own region is a rectangle in the
            # partner's source map, which is exactly the destination.
            destination = partner.source
            point = _region_centre(by_key[partner.key].record.region)
            planned[identity.key] = (
                destination,
                point,
                canonical.default_facing(destination, point),
                label,
                partner.key,
            )

    for identity_key, (destination, point, facing, _label, _partner) in planned.items():
        identity = by_key[identity_key].identity
        staged.set_destination(identity, destination)
        staged.set_arrival(identity, point)
        staged.set_facing(identity, facing)

    rows: list[WarpRecordDecision] = []
    for entry in entries:
        identity = entry.identity
        retail_destination = retail[identity.key]
        if identity.key not in planned:
            if not entry.record.has_raw_arrival_pair:
                reason = REASON_SCENE_RELATIVE_ARRIVAL
            elif retail_destination is None:
                reason = REASON_UNRESOLVED_RETAIL_DESTINATION
            else:
                reason = refusal.get(identity.key) or REASON_NO_RECIPROCAL_PAIR
            rows.append(_skip(entry, retail_destination, reason))
            continue
        destination, point, facing, label, partner_key = planned[identity.key]
        staged_record = staged.entry(identity).record
        rows.append(
            WarpRecordDecision(
                identity=identity.key,
                source_map_index=identity.source.index,
                index=identity.index,
                class_raw=entry.record.class_raw,
                class_label=_class_label(entry.record.class_raw),
                retail_destination=(
                    retail_destination.key if retail_destination is not None else None
                ),
                randomized_destination=destination.key,
                retail_arrival=_retail_arrival(entry.record),
                arrival=(point.x, point.y),
                retail_facing_raw=entry.record.byte_0x10_raw,
                randomized_facing_raw=staged_record.byte_0x10_raw,
                arrival_facing=facing,
                gate_direction=entry.record.facing.gate_direction,
                disposition=RANDOMIZED,
                skip_reason="",
                changed=staged_record != entry.record,
                pair=label,
                counterpart=partner_key,
            )
        )

    # Re-validate the whole randomized corpus before its bytes are planned: an
    # edit that broke another record's form would otherwise surface as a write.
    staged.validate()
    manifest = WarpRandomizerManifest(
        seed=text,
        profile_id=profile.id,
        base_sha256=canonical.base_sha256,
        base_size=len(image),
        decisions=tuple(rows),
        groups=tuple(groups),
        forced_leaf_links=forced_leaf_links,
    )
    return WarpRandomization(manifest=manifest, write_plan=staged.plan())


def _region_centre(region) -> TransitionArrival:
    """The centre of one door's trigger rectangle, as the arrival point.

    The two intervals are positional; a point inside both is inside the rectangle
    the engine compares, which is the only containment reading the evidence
    supports. This is where the player stands on the door that leads back.
    """
    (low_x, high_x), (low_y, high_y) = region.first, region.second
    return TransitionArrival(x=(low_x + high_x) // 2, y=(low_y + high_y) // 2)


def _retail_arrival(record) -> tuple[int, int] | None:
    """The record's canonical arrival as a point, or None when it states none.

    ``None`` covers both cases the codec distinguishes: the 566 class's measured
    sentinel, and the 169 class, whose pair is a scene-relative delta and whose
    ``arrival`` accessor refuses rather than returning a delta as a position.
    """
    if not record.has_raw_arrival_pair:
        return None
    point = record.arrival
    if point is None:
        return None
    return (point.x, point.y)


def _skip(
    entry: TransitionEntry, retail: MapIdentity | None, reason: str
) -> WarpRecordDecision:
    record = entry.record
    return WarpRecordDecision(
        identity=entry.identity.key,
        source_map_index=entry.identity.source.index,
        index=entry.identity.index,
        class_raw=record.class_raw,
        class_label=_class_label(record.class_raw),
        retail_destination=retail.key if retail is not None else None,
        randomized_destination=None,
        retail_arrival=_retail_arrival(record),
        arrival=None,
        retail_facing_raw=record.byte_0x10_raw,
        randomized_facing_raw=record.byte_0x10_raw,
        arrival_facing=record.facing.arrival_direction,
        gate_direction=record.facing.gate_direction,
        disposition=SKIPPED,
        skip_reason=reason,
        changed=False,
    )


# --- the driver --------------------------------------------------------------


def emit_randomized_rom(
    rom_path: str | Path,
    output_path: str | Path,
    seed: str | int,
    *,
    catalog: RomProfileCatalog,
    manifest_path: str | Path,
    provenance_path: str | Path | None = None,
) -> tuple[WarpRandomization, str]:
    """Build a randomized derivative ROM and write its manifest.

    The flow is the repository's one flow: the canonical image is identified and
    read, ``emit_image`` writes a NEW output and never the input, and the base
    identity is re-checked after the read. Returns the randomization and the
    output image's SHA-256.

    Every path this call writes is checked against the others BEFORE anything is
    emitted. ``emit_image`` guards its own provenance manifest against aliasing the
    image or the base, but this module's manifest is written here, so without the
    same guard ``manifest_path`` could name the output and the freshly emitted ROM
    would be replaced by JSON while the call still returned success.
    """
    from .rom import identify_rom
    from .write import paths_are_the_same_file

    source = Path(rom_path)
    destination = Path(manifest_path)
    for other, label in (
        (Path(output_path), "the output image"),
        (source, "the canonical image"),
        (Path(provenance_path) if provenance_path is not None else None,
         "the build provenance manifest"),
    ):
        if other is not None and paths_are_the_same_file(destination, other):
            raise WarpRandomizerError(
                f"the randomizer manifest must not alias {label}: {destination}"
            )
    if destination.exists():
        raise WarpRandomizerError(
            f"refusing to overwrite the existing manifest {destination}"
        )

    identification = identify_rom(source, catalog)
    profile = capability.require(
        identification,
        capability.Capability.MAP_ENTRIES,
        subsystem="warp randomization",
        error_type=WarpRandomizerError,
        check_header=True,
    )
    image = source.read_bytes()
    randomization = plan_warp_randomization(image, profile, seed)

    write_manifest = emit_image(
        source,
        output_path,
        randomization.write_plan,
        manifest_path=provenance_path,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(
        randomization.manifest.to_json(
            output_sha256=write_manifest.output_sha256,
            output_size=write_manifest.output_size,
        ).encode("utf-8")
    )
    return randomization, write_manifest.output_sha256


def main(argv: Sequence[str] | None = None) -> int:
    """``python -m tools.webfoot.warp_randomizer`` - build one randomized ROM."""
    from .cli import load_catalog

    parser = argparse.ArgumentParser(
        prog="python -m tools.webfoot.warp_randomizer",
        description=(
            "ROMHACK-WARP-RANDOMIZER-001: build a seeded, randomized derivative "
            "of a verified Buu's Fury image. The canonical image is never written."
        ),
    )
    parser.add_argument("--rom", type=Path, required=True, help="canonical ROM")
    parser.add_argument("--output", type=Path, required=True, help="new ROM to write")
    parser.add_argument("--seed", required=True, help="the seed; same seed, same mapping")
    parser.add_argument("--manifest", type=Path, required=True, help="randomizer manifest to write")
    parser.add_argument("--provenance", type=Path, default=None,
                        help="build provenance manifest (default: <output>.provenance.json)")
    parser.add_argument("--profiles", type=Path, default=None, help="ROM profile YAML")
    parser.add_argument("--summary", action="store_true", help="print the counts as JSON")
    args = parser.parse_args(argv)

    # CQA-12: a normal build publishes its provenance manifest beside the image.
    # The API keeps ``None`` meaning "no provenance"; the CLI supplies the default
    # its own help text promises, so a run cannot lose provenance by omission.
    provenance = args.provenance
    if provenance is None:
        provenance = args.output.with_name(args.output.name + ".provenance.json")

    try:
        catalog = load_catalog(args.profiles)
        randomization, output_sha256 = emit_randomized_rom(
            args.rom,
            args.output,
            args.seed,
            catalog=catalog,
            manifest_path=args.manifest,
            provenance_path=provenance,
        )
    except (ValueError, OSError) as exc:
        print(f"error: {exc}")
        return 2

    if args.summary:
        print(json.dumps(
            randomization.manifest.summary(output_sha256=output_sha256),
            indent=2, ensure_ascii=False, sort_keys=True,
        ))
    else:
        counts = randomization.manifest.summary(output_sha256=output_sha256)
        print(f"seed: {counts['seed']}")
        print(f"randomized: {counts['randomized']} of {counts['supported_transitions']} "
              f"supported ({counts['skipped']} skipped)")
        print(f"output: {args.output}")
        print(f"output sha256: {output_sha256}")
        print(f"manifest: {args.manifest}")
        print(f"provenance: {provenance}")
    return 0


if __name__ == "__main__":  # pragma: no cover - the module entry point
    raise SystemExit(main())
