"""Deterministic master-seed derivation for the enemy randomizer pack.

One master seed controls every module, and the derivation is a pure function of
that seed so a run can be reproduced from the manifest alone.

Why this is not the warp randomizer's stream
============================================

:mod:`tools.webfoot.warp_randomizer` draws from
``sha256(SEED_DOMAIN | seed | group | step)`` where ``SEED_DOMAIN`` is a constant
that is **load-bearing**: changing it changes every warp mapping ever produced.
This pack therefore never touches that constant and never draws from that
stream. It derives its own module seeds from a separate, equally frozen domain::

    MASTER DOMAIN | master seed | module id
        -> module seed (hex)

and each module then draws ``sha256(MODULE DOMAIN | module seed | step)``.

That indirection is what makes the ticket's seed-separation requirement
structural rather than a hope about call ordering. A module seed is a function of
the master seed and the module's own name, and of nothing else - not of which
other modules are enabled, not of how many draws a sibling module made, and not
of the order the modules run in. Enabling stat randomization cannot move the
enemy-type result, because the enemy-type seed never depends on it.

Determinism
===========

Every function here is pure. There is no ``random`` module use, no
``hash()`` (which is salted per process), and no process-global RNG state of any
kind. The same master seed and module id produce the same bytes on any machine
and in any process, which is what lets the manifest reproduce an output ROM
hash.
"""

from __future__ import annotations

import hashlib

#: The frozen derivation domain for this pack. Never edit this string: it is the
#: single reason two different randomizer packs sharing a master seed cannot
#: produce each other's mapping. Recorded in every manifest beside the warp
#: randomizer's own domain so the two are visibly distinct.
MASTER_DOMAIN = b"log1-remake/RANDOMIZER-ENEMY-PACK-001/master"

#: Per-module draw domain. The module seed already names the module, so this is
#: the second half of the separation: a seed's stream is identified by both.
MODULE_DOMAIN = b"log1-remake/RANDOMIZER-ENEMY-PACK-001/module"

#: The module ids. Stable strings rather than integers, because these appear in
#: the manifest and a reader has to be able to tell which seed belongs to which
#: module without a lookup table that could drift.
MODULE_WARP = "warp"
MODULE_ENEMY_TYPE = "enemy-type"
MODULE_ENEMY_PLACEMENT = "enemy-placement"
MODULE_ENEMY_STAT = "enemy-stat"

#: Every module this pack can derive a seed for, in the order the manifest lists
#: them. The order is presentation only: derivation does not depend on it, which
#: is exactly why reordering this tuple cannot change any output.
MODULE_IDS: tuple[str, ...] = (
    MODULE_WARP,
    MODULE_ENEMY_TYPE,
    MODULE_ENEMY_PLACEMENT,
    MODULE_ENEMY_STAT,
)


class SeedError(ValueError):
    """A seed or module id this pack cannot use."""


def normalize_seed(seed: str | int) -> str:
    """The exact string a master seed is identified by.

    Deliberately the same contract the warp randomizer states, because a user
    who types ``"Goku"`` into either tool should get the same notion of what a
    seed is. ``"01"`` and ``"1"`` are different seeds, since a caller who writes
    a leading zero means it; the empty string is refused rather than silently
    seeded, because ``""`` and a typo are indistinguishable in a manifest.

    Kept local rather than imported so this pack does not acquire a dependency
    on the warp core's private surface. The two must agree, and the focused tests
    assert that they do.
    """
    if isinstance(seed, bool) or not isinstance(seed, (str, int)):
        raise SeedError(f"a seed is a string or an integer, got {seed!r}")
    text = str(seed)
    if not text:
        raise SeedError("a seed must not be empty")
    return text


def derive_module_seed(master_seed: str | int, module_id: str) -> str:
    """The module seed for one module, as a hex digest.

    A hex digest rather than raw bytes so it is JSON-representable and appears in
    the manifest exactly as it is used. It is a *derived* value, never an input:
    the master seed stays the only thing a user supplies.
    """
    text = normalize_seed(master_seed)
    if not isinstance(module_id, str) or not module_id:
        raise SeedError("a module id must be a non-empty string")
    material = (
        MASTER_DOMAIN + b"|seed|" + text.encode("utf-8")
        + b"|module|" + module_id.encode("utf-8")
    )
    return hashlib.sha256(material).hexdigest()


def derive_all_module_seeds(master_seed: str | int) -> dict[str, str]:
    """Every module seed, keyed by module id.

    The manifest's ``module_seeds`` block. Built by iterating :data:`MODULE_IDS`,
    and each entry is computed independently, so the result is identical no
    matter which modules a given run actually enables.
    """
    return {module_id: derive_module_seed(master_seed, module_id)
            for module_id in MODULE_IDS}


def _draw(module_seed: str, step: int) -> int:
    """One deterministic draw from a module's stream."""
    material = (
        MODULE_DOMAIN + b"|module_seed|" + module_seed.encode("ascii")
        + b"|step|" + str(step).encode("ascii")
    )
    return int.from_bytes(hashlib.sha256(material).digest(), "big")


class Stream:
    """A module's draw stream: ``.permutation(n)`` and ``.integer(lo, hi)``.

    An object rather than free functions so nothing has to thread a step counter
    through call sites, and so two callers cannot accidentally share one counter
    and thereby couple their draws.

    The counter is per-instance and never global. A ``Stream`` for enemy types
    and a ``Stream`` for stats are two independent sequences even when they were
    derived from the same master seed, because their module seeds differ.
    """

    __slots__ = ("_seed", "_step")

    def __init__(self, module_seed: str) -> None:
        if not isinstance(module_seed, str) or not module_seed:
            raise SeedError("a module seed must be a non-empty string")
        self._seed = module_seed
        self._step = 0

    @property
    def draws(self) -> int:
        """How many values this stream has produced. For manifest provenance."""
        return self._step

    def raw(self) -> int:
        """The next 256-bit draw, as an integer."""
        value = _draw(self._seed, self._step)
        self._step += 1
        return value

    def integer(self, low: int, high: int) -> int:
        """A uniform-enough integer in ``[low, high]`` inclusive.

        Modulo bias is avoided by rejecting the top partial bucket rather than
        accepting it, so the distribution does not quietly favour the low end of
        a range whose width does not divide the draw space. The rejection is a
        deterministic function of the stream, so a run stays reproducible.
        """
        if type(low) is not int or type(high) is not int:
            raise SeedError("an integer range takes two integers")
        if high < low:
            raise SeedError(f"empty integer range [{low}, {high}]")
        span = high - low + 1
        if span == 1:
            return low
        # The largest multiple of `span` the 256-bit draw space contains.
        limit = (1 << 256) - ((1 << 256) % span)
        while True:
            value = self.raw()
            if value < limit:
                return low + (value % span)

    def permutation(self, count: int) -> tuple[int, ...]:
        """A seeded Fisher-Yates permutation of ``range(count)``.

        Pure and total: ``count <= 1`` returns the only permutation there is, so
        a single-element group consumes no seed material and is identical under
        every seed. That is what makes "different seeds differ" a claim about the
        groups that actually had a choice.
        """
        if type(count) is not int or count < 0:
            raise SeedError(f"a permutation size is a non-negative int, got {count!r}")
        order = list(range(count))
        for index in range(count - 1, 0, -1):
            swap = self.raw() % (index + 1)
            order[index], order[swap] = order[swap], order[index]
        return tuple(order)
