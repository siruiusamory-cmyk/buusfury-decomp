"""MODULE C - same-map enemy-type shuffle over proven-coherent identity pairs.

What an "enemy type" is, and why it is a pair
=============================================

Changing one numeric id is not sufficient, and the corpus proves it. A placement
carries two independent identity fields:

* ``+0x08``, the stat selector: Thumb ``0800FD56`` loads it, the wrapper computes
  ``(sel*8-sel)*4 + 08711274`` = ``28 * sel``, and passes the selected 28-byte
  record to constructor ``0800F68C`` (``TOOLKIT-009``, CONFIRMED). This chooses
  the **stats**.
* ``+0x10``, the sprite id: ``0800F6AE`` loads it into resolver ``08000158``,
  which indexes the actor character pointer table ``0x086B6BDC`` at
  ``argument - 10`` (``HUMAN-4``, CONFIRMED). This chooses the **graphics**.

They are not redundant. Measured over the canonical corpus, **seven selectors
pair with more than one sprite**: selector 15 with ``[70, 235]``, 20 with
``[78, 79]``, 37 with ``[123, 124]``, 47 with ``[70, 141, 235]``, 59 with
``[36, 261]``, 86 with ``[209, 211, 213, 215]``, and 141 with
``[10, 11, 227, 253]``. Writing the selector alone would therefore leave the old
sprite behind on those seven and produce a graphics/stat mismatch. Identity is
the ordered pair, and this module writes both halves as one semantic mutation.

Atomicity
=========

The pair installed is always a pair some canonical placement in this profile
already builds, so the resulting object is one the retail engine itself
constructs: its stats and its sprite belong together. The mode the ticket forbids
- enemy B's graphics with enemy A's behaviour and enemy C's stats - cannot be
produced, because the module never sources the two halves from different enemies
and never composes a pair the corpus does not contain.

Same map
========

Like the placement shuffle, the permutation is per map. An identity that a map
builds may be installed on another slot in that same map, which keeps the map's
identity vocabulary exactly as it was - the same enemies appear, in different
hands - and cannot introduce an enemy into a map that never had it.

Information the modules must not cross
======================================

This module reads only the identity pair. It never reads a randomized position,
and the placement module never reads a randomized identity, so the two shuffles
are independent streams over independent fields of the same record. The planner
merges their intents and encodes each record once (see
:mod:`~tools.webfoot.enemy_randomizer.records`).
"""

from __future__ import annotations

from dataclasses import dataclass

from .compatibility import IdentityPair, canonical_pairs, compatibility_class
from .eligibility import EnemySlot, Refusal, SlotModel
from .records import RecordEdits
from .seeds import Stream


class TypeRandomizationError(ValueError):
    """A type shuffle this module refused to perform."""


#: How many times a group may re-draw to avoid leaving every identity where it
#: started. Mirrors the placement module's bound and for the same reason.
MAX_REDRAWS = 8


@dataclass(frozen=True, slots=True)
class TypeDecision:
    """One slot, the identity it had and the identity it was given."""

    placement: str
    map_index: int
    original: IdentityPair
    randomized: IdentityPair

    @property
    def changed(self) -> bool:
        return self.original != self.randomized

    def to_json(self) -> dict:
        return {
            "placement": self.placement,
            "map": f"map:{self.map_index:04d}",
            "original": self.original.display,
            "randomized": self.randomized.display,
            "original_id": self.original.key,
            "randomized_id": self.randomized.key,
            "changed": self.changed,
        }


@dataclass(frozen=True, slots=True)
class TypeOutcome:
    decisions: tuple[TypeDecision, ...]
    groups_shuffled: int
    groups_refused: tuple[tuple[int, str], ...]
    pool_size: int
    compatibility_class: str

    @property
    def changed_count(self) -> int:
        return sum(1 for d in self.decisions if d.changed)

    @property
    def distinct_identities_used(self) -> int:
        return len({d.randomized for d in self.decisions})

    def summary(self) -> dict:
        return {
            "compatibility_class": self.compatibility_class,
            "pool_size": self.pool_size,
            "maps_shuffled": self.groups_shuffled,
            "slots_changed": self.changed_count,
            "slots_considered": len(self.decisions),
            "distinct_identities_used": self.distinct_identities_used,
            "groups_refused": [
                {"map": f"map:{index:04d}", "reason": reason}
                for index, reason in self.groups_refused
            ],
        }


def _shuffle_pairs(
    group: list[EnemySlot], stream: Stream
) -> list[IdentityPair]:
    """New identities for one map's slots: a permutation of their own identities.

    The pool is the map's own identity multiset, so the map's enemy vocabulary is
    preserved exactly - the same identities are present before and after, in
    different hands. A permutation that leaves every identity where it started is
    re-drawn within a fixed bound so a map does not silently do nothing; the
    retry draws from the same stream in a fixed order.
    """
    pairs = [IdentityPair(slot.original_selector, slot.original_sprite) for slot in group]
    count = len(pairs)
    if count < 2:
        return pairs
    for _ in range(MAX_REDRAWS):
        order = stream.permutation(count)
        candidate = [pairs[index] for index in order]
        if candidate != pairs:
            return candidate
    return [pairs[index] for index in order]


def shuffle_enemy_types(
    model: SlotModel,
    stream: Stream,
    *,
    edits: RecordEdits,
) -> TypeOutcome:
    """Shuffle canonical identity pairs within each map.

    Writes ``type_raw`` and ``id_raw`` together into ``edits``, which is what
    makes the change atomic: the two fields are set in one call for one placement
    and become one ``ByteChange``.
    """
    pool = canonical_pairs(model)
    decisions: list[TypeDecision] = []
    groups_shuffled = 0
    groups_refused: list[tuple[int, str]] = []

    by_map = model.by_map()
    for map_index in sorted(by_map):
        group = list(by_map[map_index])
        if len(group) < 2:
            groups_refused.append(
                (map_index, "fewer than two eligible slots in this map")
            )
            continue
        # A door-trigger slot is excluded from the permutation rather than left
        # out of the group entirely: excluding it keeps its own coordinates and
        # its own identity, so it cannot be handed a different enemy.
        shuffleable = [
            slot for slot in group
            if model.refusal_reason(slot) != Refusal.IN_DOOR_TRIGGER
        ]
        if len(shuffleable) < 2:
            groups_refused.append(
                (map_index, "fewer than two shuffleable slots in this map")
            )
            continue

        shuffleable.sort(key=lambda s: s.placement.identity.placement_index)
        new_pairs = _shuffle_pairs(shuffleable, stream)
        groups_shuffled += 1

        for slot, pair in zip(shuffleable, new_pairs):
            # Every pair here came from this map's own slots, so it is canonical
            # by construction; the check is kept as an assertion of that
            # invariant rather than as a filter that could silently drop one.
            compatibility_class(pair, model)
            if pair != slot.original_pair:
                edits.set(
                    slot.identity, "enemy-type",
                    type_raw=pair.selector, id_raw=pair.sprite,
                )
            decisions.append(
                TypeDecision(
                    placement=slot.key, map_index=map_index,
                    original=IdentityPair(*slot.original_pair),
                    randomized=pair,
                )
            )

    return TypeOutcome(
        decisions=tuple(decisions),
        groups_shuffled=groups_shuffled,
        groups_refused=tuple(groups_refused),
        pool_size=len(pool),
        compatibility_class="PROVEN_CANONICAL",
    )
