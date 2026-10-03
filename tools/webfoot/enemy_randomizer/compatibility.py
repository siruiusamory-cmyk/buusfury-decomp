"""Enemy compatibility classes, derived from evidence rather than invented.

The ticket asks for conservative compatibility pools and explicitly prefers a
simple safe result over a speculative elaborate taxonomy. This module is that
simple result, and it states why it is simple.

What was investigated, and what the evidence refused
====================================================

The ticket lists candidate dimensions. Each was checked against the canonical
corpus before being discarded, and the discards are recorded here so a later
ticket does not repeat the search:

======================  ==========================================================
dimension               finding
======================  ==========================================================
ground / flying         **No field distinguishes them.** The enemy stat record
                        decodes to exactly ``exp``/``hp``/``type_id``/``level``/
                        ``strength``/``power``/``endurance`` plus an undecoded
                        12-byte block; a 12-byte block that has never been
                        decoded cannot license a movement class, and guessing
                        one from it would be exactly the speculation the ticket
                        forbids.
melee / ranged          Same: no decoded field carries it.
movement behavior       The placement's behavior-descriptor pointer is the
                        **same shared null-handler descriptor** (``0x080555A0``)
                        across the corpus. It cannot separate two enemies,
                        because it is identical for all of them.
collision footprint     No per-placement collision data exists in this project; a
                        search finds none. ``COLLISION_FORMAT.md`` covers map
                        collision, not actor footprints.
sprite / resource       ``+0x10`` is a confirmed sprite id, but a sprite id says
                        what an actor *looks like*, not how it moves or fights.
                        Using it as a movement class would be inference from
                        appearance.
map / area restriction  Already enforced structurally: the shuffle is same-map, so
                        every identity is placed only on a coordinate its own map
                        already had.
required init fields    The identity templates are whole canonical placements, so
                        whatever initialization an enemy needs, the record that
                        carries it is the one being installed.
engine object class     One factory (``0x0800FD55``) and one constructor
                        (``0x0800F68C``) serve the whole corpus, so the engine
                        object class is constant and cannot partition it.
======================  ==========================================================

So there is exactly one compatibility class this evidence supports, and it is
defined by what makes an identity a *coherent* thing rather than by a guessed
movement type.

The class
=========

``PROVEN_CANONICAL`` - an identity is an ordered pair
``(stat selector, sprite id)`` that some canonical placement in this profile
actually builds. Not a composed pair, not a selector alone, and not an identity
from another profile.

The safety argument is about **internal coherence**, not about movement: when a
whole canonical pair is installed, the stat record and the sprite travel together
to the same object, which is the combination the retail engine itself constructs
in that very profile. The forbidden hybrid - one enemy's graphics with another's
behaviour and a third's stats - is not representable, because the module never
writes a selector and a sprite independently.

A finer taxonomy would be *desirable* and is not *available*, and inventing one
would be worse than admitting that: it would look like a safety property while
resting on nothing.

What the class does not claim
=============================

It does not claim that any canonical enemy is safe in any canonical slot. It
claims the identity is internally coherent, which is what the evidence supports.
The residual risk - an actor that is visually or mechanically out of place, or a
boss that no available field identifies - is stated in the audit and bounded by
runtime smoke, not papered over with a class name.
"""

from __future__ import annotations

from dataclasses import dataclass

from .eligibility import EnemySlot, SlotModel


class CompatibilityError(ValueError):
    """A compatibility question this model refuses to answer."""


#: The one class this evidence supports. Named rather than left implicit so a
#: manifest records which pool a run shuffled within, and so a future ticket that
#: can actually measure a split has an obvious place to add a second one.
PROVEN_CANONICAL = "PROVEN_CANONICAL"

#: Every class this version knows. The tuple exists so a report can print the
#: full set, and so adding a class is a visible change rather than a silent one.
COMPATIBILITY_CLASSES: tuple[str, ...] = (PROVEN_CANONICAL,)


@dataclass(frozen=True, slots=True)
class IdentityPair:
    """One proven-coherent enemy identity: a stat selector plus a sprite id."""

    selector: int
    sprite: int

    @property
    def key(self) -> str:
        return f"enemy_type:{self.selector:03d}:{self.sprite:03d}"

    @property
    def display(self) -> str:
        """The pair as a reader sees it, never a ROM address."""
        return f"type {self.selector} / sprite {self.sprite}"

    def to_json(self) -> dict:
        return {"selector": self.selector, "sprite": self.sprite, "id": self.key}


def canonical_pairs(model: SlotModel) -> dict[IdentityPair, tuple[EnemySlot, ...]]:
    """Every ``(selector, sprite)`` pair the corpus actually builds, and its slots.

    Built from **all** placements, not only the eligible ones, because a pair is
    proven coherent by the retail engine constructing it - and a scripted actor is
    still evidence that the engine builds that pair. Restricting the evidence base
    to eligible placements would discard real proof for no gain.
    """
    pairs: dict[IdentityPair, list[EnemySlot]] = {}
    for slot in model.slots:
        pair = IdentityPair(slot.original_selector, slot.original_sprite)
        pairs.setdefault(pair, []).append(slot)
    return {pair: tuple(slots) for pair, slots in pairs.items()}


def canonical_pair_set(model: SlotModel) -> frozenset[IdentityPair]:
    """Every pair the corpus builds, as a set, for O(1) membership tests.

    ``is_canonical`` scanning the slot tuple is fine for a one-off question and
    ruinous in the type shuffle, which asks once per installed identity: the scan
    ran 315,947 generator steps in a profile of a single plan. Building the set
    once turns that question into a lookup.
    """
    return frozenset(
        IdentityPair(slot.original_selector, slot.original_sprite)
        for slot in model.slots
    )


def is_canonical(pair: IdentityPair, model: SlotModel) -> bool:
    """Whether some canonical placement builds this exact pair.

    The set is attached to the model, which is frozen and built once per run, so
    the cost is paid once and every later question is a hash lookup.
    """
    cached = model.canonical_pair_set
    if cached is None:
        cached = canonical_pair_set(model)
        object.__setattr__(model, "canonical_pair_set", cached)
    return pair in cached


def compatibility_class(pair: IdentityPair, model: SlotModel) -> str:
    """The class a pair belongs to, or a refusal.

    A pair no canonical placement builds is not "an unknown class" that could be
    defaulted - it is an identity with no evidence behind it, and the only safe
    answer is to refuse it. Callers treat the refusal as a veto.
    """
    if not is_canonical(pair, model):
        raise CompatibilityError(
            f"{pair.display} is not built by any canonical placement in this "
            "profile, so installing it would compose an identity the retail "
            "engine was never shown to construct"
        )
    return PROVEN_CANONICAL
