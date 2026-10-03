"""The shared enemy eligibility and compatibility model.

Both the placement shuffle and the type shuffle read this one model. Neither
rediscovers enemies on its own, which is what stops the two modules disagreeing
about what an enemy is.

What is actually known, and what is not
=======================================

The honest state of the evidence, measured against the canonical image:

* A placement record's ``+0x08`` selector is **CONFIRMED** to resolve an enemy
  stat record (``TOOLKIT-009``: ``table + 28 * selector``, base ``08711274``).
  That proves a *stat link*.
* A placement's ``+0x10`` is **CONFIRMED** to be a sprite id (``HUMAN-4``:
  ``0800F6AE`` loads it into resolver ``08000158``, which indexes the character
  pointer table at ``argument - 10``). That proves a *graphics link*.
* The project has **no** boss, arena, NPC, friendly, quest-critical or
  kill-count label. ``ENTITY_FORMAT.md``'s own capability matrix records
  "NPC / enemy / item classification | NOT ESTABLISHED". A search for
  ``\\bboss\\b`` or ``\\barena\\b`` across ``tools/``, ``docs/`` and ``src/``
  returns only English prose.

So this model does **not** claim to classify a boss. It classifies by evidence a
consumer actually established, and it fails closed on everything else. Two
consequences are stated rather than hidden:

1. A selector outside the verified stat extent is ``UNKNOWN`` and is never
   touched. Those are exactly the seven the census found
   (``141, 142, 145, 146, 147, 148, 149``): the constructor computes them, but
   nothing proves they are 28-byte enemy records - and ``TOOLKIT-009`` notes
   selector 141 fails the stat shape predicate, so extending the table to cover
   them would be actively unjustified.
2. A *boss* with no script descriptor, sitting in a map that has another
   eligible placement, is **indistinguishable from an ordinary enemy** on
   current evidence. This model does not pretend otherwise. What it does
   provide is that the common shapes are removed structurally: a script-attached
   actor is refused, and an enemy alone in its own map is never shuffled because
   a shuffle of one element is not a shuffle. The residual is bounded by runtime
   smoke. Its measurement and the exact scope of the claim are in section 11 of
   ``docs/research/ENEMY_RANDOMIZER_VERIFICATION.md``.

Eligibility is never inferred from HP
=====================================

The ticket forbids treating a hit-point value as a classification, and this
model does not: no rule below reads ``hp``, ``level``, ``strength``, ``power``
or ``exp``. ``hp`` appears only as a *field to randomize*, never as a reason to
believe something is an enemy.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum

from ..entities import PlacementTypeIdentity, PlacementTypes
from ..formats import stat_tables as st
from ..formats.map_placements import SCRIPT_DISPATCH_HANDLER
from ..maps import MapIdentity, PlacementEntry, PlacementIdentity, Maps

#: The seven selectors the constructor computes but which fall outside the
#: independently verified enemy-stat extent. Recorded by name so a report can
#: print them without re-deriving the set, and so a future ticket that verifies
#: one of them has an obvious place to delete it from.
OUT_OF_STAT_EXTENT_SELECTORS: tuple[int, ...] = (141, 142, 145, 146, 147, 148, 149)


class Classification(str, Enum):
    """What a placement is, by evidence, and whether it may be randomized.

    ``ORDINARY_COMBAT_ENEMY`` is the only value eligible by default. Every other
    value is excluded, and UNKNOWN fails closed rather than being treated as a
    weak yes.
    """

    ORDINARY_COMBAT_ENEMY = "ORDINARY_COMBAT_ENEMY"
    SCRIPTED_ACTOR = "SCRIPTED_ACTOR"
    UNKNOWN = "UNKNOWN"

    @property
    def eligible(self) -> bool:
        return self is Classification.ORDINARY_COMBAT_ENEMY


class Refusal(str, Enum):
    """Why one slot is not randomized. Each value is a stable manifest key."""

    SCRIPT_EVENT = "script_event"
    #: A placement that dispatches a script this project has not decoded, or whose
    #: descriptor could not be read. Refused because "not decoded" is not
    #: "not scripted".
    SCRIPT_UNRESOLVED = "script_unresolved"
    OUTSIDE_STAT_EXTENT = "outside_stat_extent"
    IN_DOOR_TRIGGER = "in_door_trigger"
    ALONE_IN_MAP = "alone_in_map"
    MODULE_DISABLED = "module_disabled"


#: The refusal reasons that describe the *actor*, not the run. A slot refused for
#: one of these is excluded from both shuffles and from stat randomization, and
#: is reported under its own reason rather than as an unexplained omission.
ACTOR_REFUSALS: tuple[Refusal, ...] = (
    Refusal.SCRIPT_EVENT,
    Refusal.SCRIPT_UNRESOLVED,
    Refusal.OUTSIDE_STAT_EXTENT,
)


@dataclass(frozen=True, slots=True)
class EnemySlot:
    """One normalized enemy slot: the unit both shuffles operate on.

    This is the shared model the ticket asks for. It carries the placement's
    original identity pair and its original coordinates, and the planner fills
    in the randomized pair and the coordinates it moved to. Nothing here is a
    ROM address: identity is the placement's own ``(map, index)``.
    """

    placement: PlacementEntry
    classification: Classification
    #: The engine's type selector, i.e. which stat record this placement builds.
    original_selector: int
    #: The sprite id at ``+0x10``. Half of the identity pair, never a cosmetic
    #: afterthought: seven selectors in the canonical corpus pair with more than
    #: one sprite, so a selector-only swap can leave the sprite behind.
    original_sprite: int
    #: The enemy stat record this selector resolves to, or ``None`` when the
    #: selector falls outside the verified stat extent. Carried on the slot so
    #: the stat module never re-derives the selector-to-record hop: exactly one
    #: component performs it, and it is this model.
    stat_identity: st.StatIdentity | None

    @property
    def identity(self) -> PlacementIdentity:
        return self.placement.identity

    @property
    def map_index(self) -> int:
        return self.placement.identity.map_index

    @property
    def key(self) -> str:
        return self.placement.identity.key

    @property
    def record(self):
        return self.placement.record

    @property
    def original_pair(self) -> tuple[int, int]:
        """The proven-coherent identity the retail engine actually builds."""
        return (self.original_selector, self.original_sprite)

    @property
    def original_position(self) -> tuple[int, int]:
        """Signed map/world pixels.

        The axis and unit are established, not assumed: ``PLACEMENT-POS-001``
        Phases 1-3 prove ``raw_0`` is horizontal and ``raw_1`` vertical, both in
        map-space pixels, by tracing the value into the OAM writer. Three older
        docs still call the axis UNKNOWN; they are stale on this point.
        """
        return (self.record.position_x, self.record.position_y)

    def __str__(self) -> str:
        return self.key


@dataclass(frozen=True, slots=True)
class SlotModel:
    """Every placement, classified, plus the refusals that produced the verdict.

    Built once per run and read by every module, so the three modules cannot
    disagree about eligibility.
    """

    slots: tuple[EnemySlot, ...]
    refusals: tuple[tuple[EnemySlot, Refusal], ...]
    out_of_extent_selectors: tuple[int, ...]
    #: Why the script exclusion could not be evaluated, or ``None`` when it could.
    #: Carried on the model so the manifest can state that the run fell back to
    #: refusing every actor, instead of silently looking like a normal run.
    script_evidence_error: str | None = None
    #: Identity -> reason, built on first use. A cache, not part of the model's
    #: meaning: `refusals` stays the authority and this only answers the same
    #: question in constant time. A field rather than an attribute because this
    #: dataclass is slotted.
    refusal_index: dict | None = None
    #: Identity pairs the corpus builds, built on first use. Same rationale; it
    #: lives here so `compatibility.is_canonical` can populate it on the model.
    canonical_pair_set: frozenset | None = None

    @property
    def eligible(self) -> tuple[EnemySlot, ...]:
        return tuple(s for s in self.slots if s.classification.eligible)

    def by_map(self) -> dict[int, tuple[EnemySlot, ...]]:
        """Eligible slots grouped by map, each group in placement order.

        Placement order rather than sorted output: it is the map's own array
        order, so a group's indexing is stable and reproducible without relying
        on a sort that a later change could perturb.
        """
        grouped: dict[int, list[EnemySlot]] = {}
        for slot in self.eligible:
            grouped.setdefault(slot.map_index, []).append(slot)
        return {index: tuple(group) for index, group in grouped.items()}

    def refusal_reason(self, slot: EnemySlot) -> Refusal | None:
        """Why ``slot`` was refused, or ``None`` if it was not.

        Indexed rather than scanned. The obvious loop over ``self.refusals`` is
        O(refusals) per call, and the placement and type modules ask once per slot
        while grouping, so the scan dominated a profile of the whole plan (2,942
        calls over a 1,559-refusal tuple, 0.775 s of a 3.3 s run). The index is
        built once, lazily, and ``refusals`` keeps its tuple shape so a manifest
        can still iterate it in a deterministic order.
        """
        index = self.refusal_index
        if index is None:
            index = {refused.identity: reason for refused, reason in self.refusals}
            object.__setattr__(self, "refusal_index", index)
        return index.get(slot.identity)

    def counts(self) -> dict[str, int]:
        """Classification counts, keyed by the enum value, for the manifest."""
        tally = Counter(slot.classification.value for slot in self.slots)
        return dict(sorted(tally.items()))

    def refusal_counts(self) -> dict[str, int]:
        tally = Counter(reason.value for _, reason in self.refusals)
        return dict(sorted(tally.items()))

    def summary(self) -> dict:
        document = {
            "placements": len(self.slots),
            "eligible": len(self.eligible),
            "maps_with_eligible": len(self.by_map()),
            "maps_with_two_or_more_eligible": sum(
                1 for group in self.by_map().values() if len(group) >= 2
            ),
            "classification_counts": self.counts(),
            "refusal_counts": self.refusal_counts(),
            "out_of_extent_selectors": list(self.out_of_extent_selectors),
        }
        # A run that could not evaluate the script exclusion refuses every actor
        # instead. That fallback must be VISIBLE in the manifest, or such a run
        # looks exactly like a normal one whose seed simply changed nothing.
        if self.script_evidence_error is not None:
            document["script_evidence_error"] = self.script_evidence_error
            document["script_evidence_fallback"] = (
                "the script exclusion could not be evaluated, so every placement "
                "was refused as unresolved rather than assumed script-free"
            )
        return document


def _classify(
    placement: PlacementEntry,
    type_identity: PlacementTypeIdentity,
    types: PlacementTypes,
    has_script_event: bool,
    has_unresolved_script: bool,
) -> Classification:
    """Classify one placement from evidence its consumers actually established.

    Order matters and is deliberate: a script attachment is checked first,
    because it is positive evidence of a scripted actor and it outranks the stat
    link. A scripted placement that also resolves a stat record is still a
    scripted actor - the stat record says what it *is*, the script says what it
    *does*, and it is the doing that makes it unsafe to move.

    A placement that dispatches a script this project never decoded is refused on
    the same footing: the absence of a decoded script is not evidence that there
    is no script.
    """
    if has_script_event or has_unresolved_script:
        return Classification.SCRIPTED_ACTOR
    if types.type(type_identity).enemy_identity is None:
        # Inside the supported selector bound, but outside the verified stat
        # extent. The constructor computes a target; nothing proves it is an
        # enemy record. UNKNOWN, therefore untouched.
        return Classification.UNKNOWN
    return Classification.ORDINARY_COMBAT_ENEMY


def build_slot_model(
    maps: Maps,
    types: PlacementTypes,
    *,
    scripted: frozenset[PlacementIdentity] | tuple[PlacementIdentity, ...] = (),
    unresolved_script: frozenset[PlacementIdentity] | tuple[PlacementIdentity, ...] | None = None,
    door_slots: frozenset[PlacementIdentity] | tuple[PlacementIdentity, ...] = (),
    script_evidence_error: str | None = None,
) -> SlotModel:
    """Classify every placement once, and record why the refused ones were refused.

    ``scripted`` and ``unresolved_script`` are supplied by the caller because
    reading the event corpus is expensive and profile-conditional;
    :func:`scripted_placements` produces both. ``door_slots`` is the set of slots
    whose coordinates fall inside one of their own map's transition rectangles,
    produced by :func:`placements_in_door_triggers`.

    All three are passed in rather than computed here so this function stays a
    pure classification over data the caller already had to load, and so the
    tests can drive it without a ROM.

    ``unresolved_script`` has no default, and that is deliberate. Defaulting it to
    empty would make the fail-closed rule optional and would reproduce the exact
    defect this parameter exists to fix: a caller who forgot it would silently
    treat an undecoded script as no script. Passing ``frozenset()`` is a statement
    that the script evidence was checked and found nothing; omitting the argument
    is now a TypeError rather than a quiet widening of eligibility.
    """
    if unresolved_script is None:
        raise TypeError(
            "build_slot_model requires unresolved_script: pass the set from "
            "scripted_placements (or an explicit frozenset() if the script "
            "evidence was genuinely checked and empty). It is not defaulted so "
            "that forgetting it cannot silently admit a scripted actor."
        )
    scripted_ids = frozenset(scripted)
    unresolved_ids = frozenset(unresolved_script)
    door_ids = frozenset(door_slots)
    slots: list[EnemySlot] = []
    refusals: list[tuple[EnemySlot, Refusal]] = []
    seen_out_of_extent: set[int] = set()

    for placement in maps.placements():
        resolved = types.type_of(placement.identity)
        has_event = placement.identity in scripted_ids
        unresolved = placement.identity in unresolved_ids
        classification = _classify(
            placement, resolved.identity, types, has_event, unresolved
        )
        slot = EnemySlot(
            placement=placement,
            classification=classification,
            original_selector=placement.record.type_raw,
            original_sprite=placement.record.id_raw,
            stat_identity=resolved.enemy_identity,
        )
        slots.append(slot)
        if has_event:
            refusals.append((slot, Refusal.SCRIPT_EVENT))
        elif unresolved:
            refusals.append((slot, Refusal.SCRIPT_UNRESOLVED))
        elif classification is Classification.UNKNOWN:
            refusals.append((slot, Refusal.OUTSIDE_STAT_EXTENT))
            seen_out_of_extent.add(placement.record.type_raw)
        elif placement.identity in door_ids:
            # Eligible as an actor, but its coordinates sit inside a warp
            # trigger. Moving an identity onto it, or it onto another slot, is
            # the shape that can park an enemy in a doorway.
            refusals.append((slot, Refusal.IN_DOOR_TRIGGER))

    # A map with a single eligible slot has nothing to shuffle against. Recorded
    # as a refusal rather than left as a silent no-op, so a reader can see the
    # maps whose only eligible slot was left alone and why. Measured on the
    # canonical corpus: 18 lone-in-map placements across 18 maps.
    eligible_by_map = Counter(
        slot.map_index for slot in slots
        if slot.classification.eligible
        and slot.identity not in door_ids
    )
    for slot in slots:
        if slot.classification is not Classification.ORDINARY_COMBAT_ENEMY:
            continue
        if slot.identity in door_ids:
            continue
        if eligible_by_map[slot.map_index] < 2:
            refusals.append((slot, Refusal.ALONE_IN_MAP))

    return SlotModel(
        slots=tuple(slots),
        refusals=tuple(refusals),
        out_of_extent_selectors=tuple(sorted(seen_out_of_extent)),
        script_evidence_error=script_evidence_error,
    )


def scripted_placements(
    maps: Maps, events
) -> tuple[frozenset[PlacementIdentity], frozenset[PlacementIdentity]]:
    """Placements the verified event corpus ties to a script.

    Returns ``(scripted, unresolved)``; both sets are excluded from randomization.
    The second is the part that makes this fail closed, and an earlier revision of
    this pack did not have it.

    ``scripted`` is straightforward: the descriptor's handler dispatches a script
    and the corpus decoded that script's root, so the placement is an actor the
    game drives from a script - a cutscene participant, an event gate or a
    scripted encounter.

    ``unresolved`` is the subtle case. Seven placements in the canonical corpus
    dispatch through the verified script handler ``0x0800421F`` but point at a
    script root whose extent was never established under the VM evidence
    contract, so
    :class:`~tools.webfoot.placement_events.PlacementEvents` returns them with
    ``event is None`` - it states that admitting them "would promote undecoded
    roots into the event corpus on reachability alone, which is not evidence". A
    placement that dispatches a script is a scripted actor **whether or not this
    project has decoded the script**, so reading a ``None`` event as "not scripted"
    is the inference from absence the ticket forbids. They
    are excluded, and kept in their own set so the reason stays visible instead of
    being folded into the count of decoded ones.

    A placement whose descriptor cannot be read at all is likewise unresolved: an
    unreadable descriptor is not evidence that the placement has no script.
    """
    scripted: set[PlacementIdentity] = set()
    unresolved: set[PlacementIdentity] = set()
    for placement in maps.placements():
        try:
            descriptor = events.descriptor_of(placement.identity)
        except Exception:  # noqa: BLE001 - unreadable is refused, not assumed safe
            unresolved.add(placement.identity)
            continue
        if descriptor.event is not None:
            scripted.add(placement.identity)
        elif descriptor.record.handler_pointer_raw == SCRIPT_DISPATCH_HANDLER:
            unresolved.add(placement.identity)
    return frozenset(scripted), frozenset(unresolved)


def placements_in_door_triggers(
    maps: Maps, transitions
) -> frozenset[PlacementIdentity]:
    """Eligible placements whose coordinate sits inside one of its map's doors.

    Legitimate to compute because both quantities are map-space pixels:
    ``PLACEMENT-POS-001`` Phase 3 proves the placement's two raw halfwords are
    signed map X and Y, and a transition's region endpoints are the same plane -
    ``MAP-WARP-CANVAS-001`` independently landed a known region on map 39's
    doorway band.

    Each region's two intervals are treated as ordered bounds, because "two
    ordered pairs" is all the format proves: which interval is horizontal is
    UNRESOLVED in the transition record itself. The placement's axes ARE
    established (``PLACEMENT-POS-001`` Phase 3: low halfword = map X, high = map
    Y), so this function makes one assignment - placement X against the region's
    ``first`` interval and Y against ``second`` - and does NOT treat the test as
    axis-symmetric. It is not, and neither is the underlying uncertainty.

    THE UNSAFE DIRECTION IS UNDER-REPORTING, not over-reporting. A slot this
    function fails to identify is a slot that gets shuffled, which is the outcome
    the exclusion exists to prevent; a false positive merely withholds a slot from
    the shuffle, which is harmless. If the region's axis order is the opposite of
    the assignment made here, every hit is spurious and every real overlap is
    missed, so the check degrades to "no slots excluded" rather than to something
    conservative.

    The size of that exposure is NOT established, and an earlier revision of this
    docstring wrongly called it bounded by "the 2 slots the census found inside a
    trigger" - circular, because the census used this same one-orientation test.
    What is true: the transition format does not resolve the axis, the placement
    format does, and nobody has yet established which pairing is correct. Section
    7.1 of ``docs/research/ENEMY_RANDOMIZER_VERIFICATION.md`` records this as an
    open question rather than a bound.
    """
    regions: dict[int, list[tuple[tuple[int, int], tuple[int, int]]]] = {}
    for entry in transitions.entries():
        record = entry.record
        regions.setdefault(entry.identity.source.index, []).append(
            (record.region.first, record.region.second)
        )

    def inside(x: int, y: int, candidates) -> bool:
        for (a_lo, a_hi), (b_lo, b_hi) in candidates:
            lo_a, hi_a = min(a_lo, a_hi), max(a_lo, a_hi)
            lo_b, hi_b = min(b_lo, b_hi), max(b_lo, b_hi)
            if lo_a <= x <= hi_a and lo_b <= y <= hi_b:
                return True
        return False

    found: set[PlacementIdentity] = set()
    for placement in maps.placements():
        candidates = regions.get(placement.identity.map_index)
        if not candidates:
            continue
        if inside(placement.record.position_x, placement.record.position_y, candidates):
            found.add(placement.identity)
    return frozenset(found)


def map_identity(index: int) -> MapIdentity:
    """Kept so callers do not import :mod:`maps` just to name a map."""
    return MapIdentity(index)
