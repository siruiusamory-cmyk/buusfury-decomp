"""The standalone *Enemy Randomizer* - a product composed over the foundation.

This package is what ENEMY-RANDOMIZER-EXE-001 ships, and it is deliberately
small, because almost nothing in it is new:

* :mod:`tools.webfoot.randomizer` owns the ROM check, the path safety, the seed,
  the output naming, the manifest, the spoiler, the refusal vocabulary, the
  module registry and the window;
* :mod:`tools.webfoot.enemy_randomizer` owns the placement shuffle and the stat
  policy - the already-proven core, called through its own context and unchanged;
* :mod:`tools.webfoot.randomizer.modules.enemy` is the adapter that presents those
  two as the modules ``enemy-placement`` and ``enemy-stat``;
* this package is the *composition*: a name, a version, a launch seed, an output
  template, two toggles, a band selector and a README.

What it randomizes, stated the way the manifest states it
=========================================================

* **enemy placement** - eligible ordinary enemies are shuffled among proven
  existing placements *within one map*. No spawn is created and no coordinate is
  invented.
* **enemy stats** - supported enemy stat fields are scaled around each record's
  own original values within a bounded band, which is what preserves the game's
  general progression.

What it does not
================

* **enemy species or type.** Enemy identity is the ordered pair ``(stat selector,
  sprite id)``, and within one coupled-field group every member already agrees on
  its flags, descriptor and children - so exchanging identity between two members
  is exactly exchanging their positions. No identity can cross a coupled-field
  boundary without producing an actor whose behaviour belongs to a different
  enemy than its sprite and stats, which nothing establishes is coherent. That
  research result is why the module is not registered here at all, and why every
  manifest this tool writes records ``delivers_ticket_module_c: false``.
* **actors it can positively identify as something other than an ordinary enemy**,
  plus anything the eligibility model cannot classify. Excluded: actors carrying a
  script event, actors whose script root was never decoded, actors whose stat
  selector falls outside the verified enemy-stat extent, placements inside a door
  trigger, and an enemy that is the only eligible one in its map. There is no
  "randomize everything" switch, because one would be a way to turn those off.

  One of those exclusions is weaker than the word "bosses" would suggest, and the
  honest version is in every manifest this package writes: the project has **no
  boss, NPC or quest-critical classification**, so none is claimed. A boss that is
  neither script-attached nor alone in its map is indistinguishable from an
  ordinary enemy and may be randomized. The shipped README says so in the same
  words, because a user reading only the download should not have to open a
  manifest to learn it.
* items, map generation, or anything else.

No ROM is bundled, and none can be: the only data file in the packaged build is
the ROM profile catalog, a table of addresses and hashes.
"""

from __future__ import annotations

from .service import (
    DEFAULT_SEED,
    MANIFEST_SUFFIX,
    MODULE_IDS,
    OUTPUT_TEMPLATE,
    PROGRESSION_DISCLAIMER,
    PROGRESS_STEPS,
    SPOILER_SUFFIX,
    TOOL_NAME,
    TOOL_VERSION,
    EnemyRandomizerService,
    default_service,
    default_output_path,
)

__all__ = [
    "DEFAULT_SEED",
    "MANIFEST_SUFFIX",
    "MODULE_IDS",
    "OUTPUT_TEMPLATE",
    "PROGRESSION_DISCLAIMER",
    "PROGRESS_STEPS",
    "SPOILER_SUFFIX",
    "TOOL_NAME",
    "TOOL_VERSION",
    "EnemyRandomizerService",
    "default_output_path",
    "default_service",
]
