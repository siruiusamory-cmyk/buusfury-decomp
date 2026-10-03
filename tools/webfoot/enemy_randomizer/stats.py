"""MODULE A - bounded multiplicative randomization of enemy combat stats.

The policy, stated exactly
==========================

For each selected field of each eligible enemy record::

    factor     = seeded rational in [range.low, range.high]
    candidate  = original * factor, floored (integer arithmetic only)
    randomized = clamp(candidate, field floor, field ceiling)

This is **relative to the record's own original value**, never a draw from a
global range. That is the ticket's progression safeguard: it keeps the game's
broad power curve intact, so a weak enemy scaled by the preset's ceiling stays
weak, and a level-1 area cannot receive an endgame number just because the
generator was asked for one. A global ``random(min, max)`` would flatten the
curve into noise while looking superficially random.

Provenance for every field
==========================

Nothing here is assumed. Each field's storage, width, legal domain and
zero-semantics come from the codec (:mod:`tools.webfoot.formats.stat_tables`,
``DATA-001`` verified against the canonical ROM) or from a runtime measurement:

=============  =========  ============  ==================================
field          storage    domain        notes
=============  =========  ============  ==================================
``exp``        u24 @0x00  0..16777215   0 is legal (13 records hold 0)
``hp``         u24 @0x04  0..16777215   displayed hit points; floor 1
``level``      u8  @0x0C  0..255        measured 1..175, floor 1, cap 200
``strength``   u8  @0x0D  0..255        0 legal (25 records)
``power``      u8  @0x0E  0..255        0 legal (47 records)
``endurance``  u8  @0x0F  0..255        0 legal (4 records)
=============  =========  ============  ==================================

The two 24-bit fields are **unsigned**, as are the four u8 fields. ``hp`` here is
the **displayed** hit-point value, not a fixed-point quantity, and the evidence is
the repository's own identification oracle: the wolf is found by
``find_enemies_by_hp(175)``, so the record holds 175 - the number the player sees.
P-010's 1024-raw-units-per-displayed-point figure describes the RUNTIME ACTOR's
HP, a different quantity in a different place; applying it to this record once put
a floor of 1024 under values that run as low as 1 and clamped every record below
it upward whatever the seed. The floor is therefore 1.

Zero has no "unset" meaning in this data model. A zero ``strength`` is a real
authored zero, so a multiplicative policy leaves it at zero - ``0 * k == 0`` -
rather than inventing a minimum.

The record's own ``type_id`` is deliberately never randomized: it is the
record's identity and the key the placement selector relationship resolves
through. Randomizing it would rewrite identity, which is the type module's job
and is done as an atomic pair swap there, not as a stat edit.

Per type, not per instance
==========================

Stats live in one record per selector, shared by every placement that uses it, so
randomizing a selector once is the whole effect and a per-instance draw would be
a fiction the data model cannot express. A selector is randomized only when
**every** placement using it is an eligible ordinary combat enemy; one unsafe
consumer vetoes the shared record, which is the fail-closed direction.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from ..formats import stat_tables as st
from ..stats import StatTables
from .config import STAT_FIELDS, EnemyRandomizerConfig
from .eligibility import Classification, EnemySlot, Refusal, SlotModel
from .seeds import Stream


class StatRandomizationError(ValueError):
    """A stat this module refused to emit."""


@dataclass(frozen=True, slots=True)
class StatDecision:
    """One enemy stat record: its original values, its randomized values, and why.

    Both sides are carried so the manifest is self-describing - a reader can see
    what changed without the ROM - and so a spoiler log can present the change
    using enemy identities rather than a single ROM address.
    """

    selector: int
    enemy_identity: str
    factor: str
    original: dict[str, int]
    randomized: dict[str, int]

    @property
    def fields(self) -> tuple[str, ...]:
        return tuple(sorted(self.original))

    @property
    def changed_fields(self) -> tuple[str, ...]:
        return tuple(f for f in self.fields if self.original[f] != self.randomized[f])

    @property
    def changed(self) -> bool:
        return bool(self.changed_fields)

    def to_json(self) -> dict:
        return {
            "selector": self.selector,
            "enemy": self.enemy_identity,
            "factor": self.factor,
            "original": dict(sorted(self.original.items())),
            "randomized": dict(sorted(self.randomized.items())),
            "changed_fields": list(self.changed_fields),
        }


@dataclass(frozen=True, slots=True)
class StatOutcome:
    decisions: tuple[StatDecision, ...]
    refused_selectors: tuple[tuple[int, str], ...]
    fields: tuple[str, ...]

    @property
    def randomized_records(self) -> int:
        return sum(1 for d in self.decisions if d.changed)

    def summary(self) -> dict:
        return {
            "records_considered": len(self.decisions),
            "records_changed": self.randomized_records,
            "refused_selectors": [
                {"selector": selector, "reason": reason}
                for selector, reason in self.refused_selectors
            ],
            "fields": list(self.fields),
        }


def pick_factor(stream: Stream, band) -> Fraction:
    """A seeded factor inside the band, drawn on a fixed rational grid.

    Drawn as an exact fraction rather than a float, so the result is identical on
    every machine and ``0.75`` means three quarters rather than the nearest
    double. 1024 grid steps cover a narrow band densely enough that two seeds
    rarely agree by accident, while keeping the set of reachable factors finite
    and therefore reproducible.
    """
    steps = 1024
    span = band.high - band.low
    if span == 0:
        return band.low
    index = stream.integer(0, steps)
    return band.low + span * Fraction(index, steps)


def scale_field(original: int, factor: Fraction, name: str) -> int:
    """``original * factor``, floored, then clamped to the field's legal domain.

    An original zero stays zero: it is an authored value, not an unset marker,
    and no evidence in this project establishes a nonzero minimum for ``exp``,
    ``strength``, ``power`` or ``endurance``.

    The clamp is a bound rather than a repair: a field's domain is a fact about
    the bytes the ROM gave it, so no seed may produce a value that does not fit.
    Because the policy is multiplicative and the band is bounded, the clamp is
    reachable only near a field's ceiling.
    """
    low, high = STAT_FIELDS[name]
    if original == 0:
        return 0
    candidate = (original * factor.numerator) // factor.denominator
    return max(low, min(high, candidate))


def eligible_stat_selectors(
    model: SlotModel,
) -> tuple[list[EnemySlot], list[tuple[int, str]]]:
    """Which selectors may be randomized, and which were refused and why.

    Returns one representative slot per eligible selector - every slot sharing a
    selector carries the same stat identity, so any of them names the record.

    A stat record is SCALED only when every placement that selects it is an ordinary
    combat enemy that the run actually randomized. That is stricter than "the
    placement is classified ordinary", and deliberately so, because the manifest and
    the owner's waiver both describe EXCLUSIONS, and a record whose other consumer is
    an excluded actor is not excluded from the effect.

    A review found the consequence of getting this wrong: ``alone_in_map`` slots stay
    classified ``ORDINARY_COMBAT_ENEMY`` (they are ordinary enemies; the refusal is
    about *moving* them, not about what they are), so they were passing the
    classification test and their records were being scaled - 11 of 18 such slots had
    their stats changed, while ``exclusions.policy`` told the reader that a placement
    "is refused when it is the only eligible slot in its map", and Waiver 1 leaned on
    that exclusion as the boss protection.

    Two refusals are therefore treated the same way here, and the distinction is
    worth stating because they are not the same kind of thing:

    * an actor-level refusal (a scripted actor or an unresolved script) vetoes the
      record outright - the actor must stay untouched, so every record it reads must;
    * a slot-level refusal (in a door trigger, or alone in its map) vetoes the record
      only if NO placement using it may justify scaling. A door slot MAY justify it on
      its own, because its refusal is about movement rather than about the actor; a
      lone-in-map slot may not, because it means the map had no other eligible
      placement. If a shared record still has a consumer the run randomizes, the
      record is scaled; if every consumer is excluded, the record is left alone.
      Measured on the canonical corpus, the lone-in-map rule costs exactly the two
      selectors used solely by lone slots (80 and 136); vetoing every selector that a
      lone slot happens to touch would have cost 11 records and silently stripped stat
      randomization from ordinary enemies elsewhere, which is the over-veto this
      docstring already warns about for door slots.
    """
    by_selector: dict[int, list[EnemySlot]] = {}
    for slot in model.slots:
        by_selector.setdefault(slot.original_selector, []).append(slot)

    #: Reasons about the ACTOR: a scripted actor, an actor whose script was never
    #: decoded, or a selector outside the verified stat extent. ANY consumer with one
    #: of these vetoes the record outright, no matter how many other consumers look
    #: ordinary. That is the original rule and it is not negotiable: the actor is one
    #: the run promised not to touch, so every record it reads must be left alone.
    actor_refusals = {
        Refusal.SCRIPT_EVENT, Refusal.SCRIPT_UNRESOLVED, Refusal.OUTSIDE_STAT_EXTENT,
    }

    def may_justify_scaling(slot) -> bool:
        """Whether this placement, on its own, justifies scaling the record.

        Deliberately NOT the whole rule - it answers only "is this a placement the
        run randomizes as a placement". Two conditions:

        * not ``alone_in_map``. A lone slot is never randomized as a slot, so it
          cannot justify scaling its record either; otherwise a record used solely by
          one lone enemy gets scaled while the manifest tells the reader that
          placement is refused. Selectors 80 and 136 are exactly this case, one lone
          consumer each;
        * classified ordinary combat enemy.

        A placement refused only for sitting IN A DOOR TRIGGER does count here, and it
        counts EVEN AS THE ONLY CONSUMER. That is deliberate and asymmetric with
        alone-in-map: a door refusal is about not moving an actor into a doorway, and a
        record is shared by every placement selecting it, so letting one door-adjacent
        placement veto a selector would strip a stat edit from every other enemy using
        that type for a reason unrelated to stats. A lone-in-map slot is different in
        kind: it means the map had no other eligible placement at all.

        Consequence, stated rather than left to be discovered: a record whose only
        consumer is a door-trigger slot IS scaled. That case does not arise on the
        canonical corpus - both in-door slots use selector 115, which an ordinary
        placement also selects - so it is latent, not live.

        An earlier revision folded the actor reasons into this predicate instead of
        vetoing the selector, which silently dropped the scripted-actor protection and
        let 21 records shared with scripted actors be scaled - a regression a review
        caught. Actor reasons are checked at the selector level below, where they
        cannot be diluted by an ordinary sibling.
        """
        if model.refusal_reason(slot) is Refusal.ALONE_IN_MAP:
            return False
        return slot.classification is Classification.ORDINARY_COMBAT_ENEMY

    eligible: list[EnemySlot] = []
    refused: list[tuple[int, str]] = []
    for selector in sorted(by_selector):
        slots = by_selector[selector]

        # Rule 1, and it dominates: if ANY consumer is an actor the run must leave
        # alone, the record is refused. Checked over every slot, not over a filtered
        # subset, so an ordinary sibling can never outvote a scripted actor.
        actor_blocked = [s for s in slots if model.refusal_reason(s) in actor_refusals]
        if actor_blocked:
            kinds = sorted({model.refusal_reason(s).value for s in actor_blocked})
            refused.append((selector, f"shared with {'/'.join(kinds)} placement(s)"))
            continue

        # Rule 2: the record must have at least one consumer that the run actually
        # randomizes. Otherwise it is only read by excluded placements (alone in its
        # map, or in a door trigger with no randomized sibling).
        consumers = [s for s in slots if may_justify_scaling(s)]
        if not consumers:
            kinds = sorted({
                (model.refusal_reason(s) or s.classification).value
                if hasattr(model.refusal_reason(s) or s.classification, "value")
                else str(model.refusal_reason(s) or s.classification)
                for s in slots
            })
            refused.append((selector, f"every consumer is excluded ({'/'.join(kinds)})"))
            continue
        eligible.append(consumers[0])
    return eligible, refused


def randomize_stats(
    model: SlotModel,
    stat_tables: StatTables,
    config: EnemyRandomizerConfig,
    stream: Stream,
) -> StatOutcome:
    """Randomize eligible enemy stat records on ``stat_tables``, in place.

    Edits go through the stat authority's own
    :meth:`~tools.webfoot.stats.StatTables.set_enemy_field`, so validation stays
    in the one component that owns it. This function never touches a file and
    never builds a plan; the caller plans and the writer writes.
    """
    if config.stat_range is None:
        raise StatRandomizationError(
            "stat randomization is requested but the configuration carries no range"
        )
    fields = tuple(config.stat_fields)
    for name in fields:
        if name not in STAT_FIELDS:
            raise StatRandomizationError(f"unknown stat field {name!r}")

    eligible, refused = eligible_stat_selectors(model)
    band = config.stat_range
    decisions: list[StatDecision] = []

    for slot in eligible:
        identity = slot.stat_identity
        if identity is None:
            # The veto rules above already exclude these, but a None identity is
            # a programming error rather than a data one, so refuse loudly.
            raise StatRandomizationError(
                f"selector {slot.original_selector} has no stat identity to randomize"
            )
        entry = stat_tables.enemy(identity)
        original = {name: getattr(entry.record, name) for name in fields}

        factor = pick_factor(stream, band)
        randomized = {name: scale_field(original[name], factor, name) for name in fields}

        for name in fields:
            if randomized[name] != original[name]:
                stat_tables.set_enemy_field(identity, name, randomized[name])

        decisions.append(
            StatDecision(
                selector=slot.original_selector,
                enemy_identity=str(identity),
                factor=f"{factor.numerator}/{factor.denominator}",
                original=original,
                randomized=randomized,
            )
        )

    return StatOutcome(decisions=tuple(decisions), refused_selectors=tuple(refused), fields=fields)


def enemy_field_names() -> tuple[str, ...]:
    """The codec's own decoded field names, for tests and reports."""
    return tuple(name for _, _, name in st.ENEMY_DECODED_SPANS)
