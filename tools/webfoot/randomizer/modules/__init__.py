"""The registered randomizer modules.

Each module is an adapter over a proven algorithm; none of them implements one.
See :mod:`tools.webfoot.randomizer.registry` for the canonical order and the
structural checks that run at import.
"""

from __future__ import annotations

from .enemy import (  # noqa: F401 - re-exported for the registry and for tests
    ENEMY_MODULE_IDS,
    EnemyPlacementModule,
    EnemyStatModule,
    plan_enemy_group,
)
from .map_warp import MapWarpModule  # noqa: F401

__all__ = [
    "ENEMY_MODULE_IDS",
    "EnemyPlacementModule",
    "EnemyStatModule",
    "MapWarpModule",
    "plan_enemy_group",
]
