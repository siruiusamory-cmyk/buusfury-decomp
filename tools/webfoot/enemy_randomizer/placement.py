"""MODULE B - same-map enemy placement shuffle over proven slots.

No coordinate is ever invented
==============================

The module does not generate positions. It permutes the **existing**
``position_raw`` values among the eligible slots *of one map*, so every
coordinate that ends up in the image was already in the image, on that same map.
That is the ticket's central placement rule and it is the reason this module is
safe at all: map membership, coordinate encoding, and the signed halfword
representation are all preserved by construction rather than re-derived.

Same map, not global
====================

The permutation is computed independently per map. A global permutation would let
an enemy move to a map it was never placed on, which changes which encounters
exist rather than only where they stand. Same-map was measured to be a real
scope, not a token one: 236 of the 268 placement-bearing maps hold two or more
eligible slots, covering 1,465 of the 1,487 eligible placements.

What this module does NOT change
================================

It writes ``position_raw`` only. Identity, the type selector, the sprite id, the
flags word, the behavior-descriptor pointer and the child-pointer array are all
left exactly as they were, so a placement move cannot silently change what an
enemy *is*, only where it stands. That separation is what makes the three modules
compose predictably: this module never depends on the type module's choices, and
the type module never depends on this one's.

Door triggers
=============

Slots refused for sitting inside a transition rectangle are excluded from the
permutation pool, so an enemy is never moved onto or off such a coordinate. The
census found exactly two such slots in the whole corpus, so this costs almost
nothing and removes the one placement shape that could park an enemy in a doorway.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..maps import PlacementEntry
from .eligibility import EnemySlot, Refusal, SlotModel
from .records import RecordEdits
from .seeds import Stream


class PlacementRandomizationError(ValueError):
    """A placement shuffle this module refused to perform."""


#: How many times a group may re-draw to avoid leaving every slot where it
#: started. Bounded, because an unbounded retry loop is a hang waiting for a
#: pathological seed; the bound is deterministic and seed-independent.
MAX_REDRAWS = 8


@dataclass(frozen=True, slots=True)
class PlacementDecision:
    """One slot, where it started and where it ended up.

    Positions are signed map/world pixels, the authority the renderer consumes.
    The raw halfwords are carried alongside because they are the actual storage
    and a reader comparing two records wants the value the ROM holds.
    """

    placement: str
    map_index: int
    original: tuple[int, int]
    randomized: tuple[int, int]

    @property
    def moved(self) -> bool:
        return self.original != self.randomized

    def to_json(self) -> dict:
        return {
            "placement": self.placement,
            "map": f"map:{self.map_index:04d}",
            "original": {"x": self.original[0], "y": self.original[1]},
            "randomized": {"x": self.randomized[0], "y": self.randomized[1]},
            "moved": self.moved,
        }


@dataclass(frozen=True, slots=True)
class PlacementOutcome:
    decisions: tuple[PlacementDecision, ...]
    groups_shuffled: int
    groups_refused: tuple[tuple[int, str], ...]

    @property
    def moved_count(self) -> int:
        return sum(1 for d in self.decisions if d.moved)

    def summary(self) -> dict:
        return {
            "maps_shuffled": self.groups_shuffled,
            "slots_moved": self.moved_count,
            "slots_considered": len(self.decisions),
            "groups_refused": [
                {"map": f"map:{index:04d}", "reason": reason}
                for index, reason in self.groups_refused
            ],
        }


def _shuffle_group(
    group: list[EnemySlot], stream: Stream
) -> list[tuple[int, int]]:
    """New positions for one map's slots: a permutation of their own positions.

    The permutation is drawn from the stream, and if it happens to be the identity
    (every enemy standing exactly where it started) the draw is repeated a bounded
    number of times. Without that, a map occasionally does nothing under a seed
    and a player reasonably reads it as a bug. The retry consumes further draws
    from the *same* stream in a fixed order, so it stays deterministic and does not
    touch any other module's stream.
    """
    positions = [slot.original_position for slot in group]
    count = len(positions)
    if count < 2:
        return positions
    for _ in range(MAX_REDRAWS):
        order = stream.permutation(count)
        candidate = [positions[index] for index in order]
        if candidate != positions:
            return candidate
    # Every draw landed on the identity within the bound. Returning the last
    # candidate is correct - a shuffle that changes nothing is a legal outcome -
    # and is better than raising, because the map is still internally consistent.
    return [positions[index] for index in order]


def shuffle_placements(
    model: SlotModel,
    stream: Stream,
    *,
    entries: dict,
    edits: RecordEdits,
) -> PlacementOutcome:
    """Shuffle each map's eligible slots among their own proven positions.

    Writes its intent into ``edits`` rather than encoding bytes, so the placement
    shuffle and the type shuffle can touch one record and still produce a single
    attributed change. Returns the decisions for the manifest and the spoiler log.
    """
    decisions: list[PlacementDecision] = []
    groups_shuffled = 0
    groups_refused: list[tuple[int, str]] = []

    by_map = model.by_map()
    for map_index in sorted(by_map):
        group = [
            slot for slot in by_map[map_index]
            if model.refusal_reason(slot) != Refusal.IN_DOOR_TRIGGER
        ]
        if len(group) < 2:
            groups_refused.append(
                (map_index, "fewer than two eligible slots in this map")
            )
            continue

        # Stable order: the map's own placement order, which is the order the
        # engine's array uses. Sorting by identity would also be stable, but this
        # keeps the group in the order the map actually stores its objects.
        group = sorted(group, key=lambda s: s.placement.identity.placement_index)
        new_positions = _shuffle_group(group, stream)
        groups_shuffled += 1

        for slot, position in zip(group, new_positions):
            entry: PlacementEntry = entries[slot.identity]
            original = slot.original_position
            if position != original:
                record = entry.record.with_map_position(position[0], position[1])
                edits.set(slot.identity, "placement", position_raw=record.position_raw)
            decisions.append(
                PlacementDecision(
                    placement=slot.key, map_index=map_index,
                    original=original, randomized=position,
                )
            )

    return PlacementOutcome(
        decisions=tuple(decisions),
        groups_shuffled=groups_shuffled,
        groups_refused=tuple(groups_refused),
    )


def placements_by_identity(entries) -> dict:
    """Index placements by identity, refusing a duplicate rather than hiding one."""
    indexed = {}
    for entry in entries:
        if entry.identity in indexed:
            raise PlacementRandomizationError(
                f"two placement records claim {entry.identity}"
            )
        indexed[entry.identity] = entry
    return indexed
