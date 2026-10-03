"""The enemy randomizer pack: one master seed, three modules, no new architecture.

The pack extends the randomizer the project already ships rather than standing
up a second one. It reuses:

* the seeded-draw discipline of :mod:`tools.webfoot.warp_randomizer` (SHA-256
  domain separation, Fisher-Yates over the hash stream, no ``random`` module and
  no process-global RNG state), under this pack's own frozen domain;
* :class:`tools.webfoot.write.WritePlan` and
  :func:`tools.webfoot.write.emit_image` as the only writer;
* :class:`tools.webfoot.entities.PlacementTypes` for the placement/enemy
  relationship and :mod:`tools.webfoot.formats.stat_tables` for the stat record
  codec, both unmodified.

Modules
-------

* :mod:`~tools.webfoot.enemy_randomizer.stats` - bounded multiplicative
  randomization of the already-decoded enemy stat fields;
* :mod:`~tools.webfoot.enemy_randomizer.placement` - same-map shuffle of proven
  placement slots;
* :mod:`~tools.webfoot.enemy_randomizer.enemy_type` - same-map shuffle of
  canonical ``(stat selector, sprite id)`` identity pairs.

The privacy of one module seed from another is owned by
:mod:`~tools.webfoot.enemy_randomizer.seeds`, not by the order these modules run
in.
"""

from __future__ import annotations

from .config import PRESETS, EnemyRandomizerConfig, Preset
from .eligibility import Classification, EnemySlot, SlotModel
from .manifest import RunManifest
from .planner import EnemyRandomization, plan_enemy_randomization
from .seeds import (
    MASTER_DOMAIN,
    MODULE_DOMAIN,
    MODULE_ENEMY_PLACEMENT,
    MODULE_ENEMY_STAT,
    MODULE_ENEMY_TYPE,
    MODULE_IDS,
    MODULE_WARP,
    SeedError,
    Stream,
    derive_all_module_seeds,
    derive_module_seed,
    normalize_seed,
)

__all__ = [
    "Classification",
    "EnemyRandomization",
    "EnemyRandomizerConfig",
    "EnemySlot",
    "MASTER_DOMAIN",
    "MODULE_DOMAIN",
    "MODULE_ENEMY_PLACEMENT",
    "MODULE_ENEMY_STAT",
    "MODULE_ENEMY_TYPE",
    "MODULE_IDS",
    "MODULE_WARP",
    "PRESETS",
    "Preset",
    "RunManifest",
    "SeedError",
    "SlotModel",
    "Stream",
    "derive_all_module_seeds",
    "derive_module_seed",
    "normalize_seed",
    "plan_enemy_randomization",
]
