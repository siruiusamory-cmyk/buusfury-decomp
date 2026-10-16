"""The module registry: one explicit list, one deterministic order, no magic.

Registration is a static tuple, not a decorator that appends to a global as a side
effect of import order. That is a deliberate constraint, because the combined tool
this foundation exists for will run several modules in one pass and its output
must not depend on which module happened to be imported first:

* :data:`MODULE_ORDER` states the canonical order by hand;
* :func:`validate_registry` proves at import time that every registered module
  appears in it exactly once, that ids are unique, and that seed namespaces are
  unique;
* the seed of one module is a pure function of the master seed and that module's
  id, so enabling or disabling a sibling cannot move it.

Nothing here consults the filesystem, dictionary iteration order, or a checkbox.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from .errors import ModuleRefusedError
from .module import (
    GroupPlanRequest,
    ModuleContractError,
    ModulePlan,
    RandomizerModule,
)
from .modules.enemy import (
    ENEMY_MODULE_IDS,
    EnemyPlacementModule,
    EnemyStatModule,
    plan_enemy_group,
)
from .modules.map_warp import MapWarpModule

#: The canonical execution and presentation order. Adding a module means adding
#: its id here, and a future module gets an explicit position rather than an
#: accidental one.
MODULE_ORDER: tuple[str, ...] = (
    "map-warp",
    "enemy-placement",
    "enemy-stat",
)

#: Every registered module class, in canonical order.
MODULE_CLASSES: tuple[type[RandomizerModule], ...] = (
    MapWarpModule,
    EnemyPlacementModule,
    EnemyStatModule,
)


def _plan_single(request: GroupPlanRequest) -> tuple[ModulePlan, ...]:
    """The planner for a group that holds exactly one module."""
    plans: list[ModulePlan] = []
    for module_id in request.enabled:
        module = module_for(module_id)
        settings = request.settings.get(module_id, {})
        module.validate(request.context, settings)
        plans.append(
            module.plan(
                request.context,
                settings,
                seed=request.module_seeds[module_id],
            )
        )
    return tuple(plans)


@dataclass(frozen=True, slots=True)
class ModuleGroup:
    """Modules that must be planned in ONE pass over the image.

    A single-module group is the ordinary case. The enemy pair is the exception,
    and for a measured reason rather than convenience: the pack builds one slot
    model per load and returns one merged change set, so planning the two in
    separate passes would load the image twice and would put two overlapping
    :class:`~tools.webfoot.write.WritePlan` objects over one image - the exact
    shape that lets a collision hide from the writer's per-plan overlap check.
    """

    ids: tuple[str, ...]
    planner: Callable[[GroupPlanRequest], tuple[ModulePlan, ...]]


#: Groups in canonical order. Every registered module belongs to exactly one.
MODULE_GROUPS: tuple[ModuleGroup, ...] = (
    ModuleGroup(ids=("map-warp",), planner=_plan_single),
    ModuleGroup(ids=ENEMY_MODULE_IDS, planner=plan_enemy_group),
)


def validate_registry() -> None:
    """Prove the registry's structural invariants, or raise.

    Called at import. These are development defects rather than user errors, so
    failing loudly at import is the right behaviour: a registry that lists a
    module twice, or gives two modules the same seed namespace, cannot produce a
    reproducible combined run and must never reach a release.
    """
    declared = tuple(cls.id for cls in MODULE_CLASSES)
    if len(set(declared)) != len(declared):
        raise ModuleContractError(f"duplicate module id in the registry: {declared}")
    if set(MODULE_ORDER) != set(declared):
        raise ModuleContractError(
            "MODULE_ORDER must name every registered module exactly once; "
            f"order={MODULE_ORDER} registered={declared}"
        )
    namespaces = [cls.seed_namespace for cls in MODULE_CLASSES]
    if len(set(namespaces)) != len(namespaces):
        raise ModuleContractError(
            f"two modules share a seed namespace: {namespaces}"
        )
    for cls in MODULE_CLASSES:
        if not cls.id or not cls.seed_namespace or not cls.progress_label:
            raise ModuleContractError(f"{cls.__name__} has an empty declaration")
        if cls.algorithm_version < 1:
            raise ModuleContractError(
                f"{cls.id}: algorithm_version starts at 1, got {cls.algorithm_version}"
            )
    grouped = [module_id for group in MODULE_GROUPS for module_id in group.ids]
    if sorted(grouped) != sorted(declared):
        raise ModuleContractError(
            "every registered module must belong to exactly one group; "
            f"groups={grouped} registered={declared}"
        )
    for group in MODULE_GROUPS:
        if group.ids != tuple(sorted(group.ids, key=MODULE_ORDER.index)):
            raise ModuleContractError(
                f"group {group.ids} is not in canonical order"
            )


validate_registry()


def modules() -> tuple[type[RandomizerModule], ...]:
    """Every registered module class, in canonical order."""
    by_id = {cls.id: cls for cls in MODULE_CLASSES}
    return tuple(by_id[module_id] for module_id in MODULE_ORDER)


def module_for(module_id: str) -> type[RandomizerModule]:
    """The module class registered under ``module_id``, or a refusal."""
    for cls in MODULE_CLASSES:
        if cls.id == module_id:
            return cls
    raise ModuleRefusedError(
        f"unknown randomizer module {module_id!r}; "
        f"registered: {', '.join(MODULE_ORDER)}"
    )


def known_module_ids() -> tuple[str, ...]:
    return MODULE_ORDER


def default_enabled_ids() -> frozenset[str]:
    """Every module that starts enabled, in registry terms."""
    return frozenset(cls.id for cls in MODULE_CLASSES if cls.default_enabled)


def resolve_enabled(
    allowed: Sequence[str] | None, requested: Sequence[str] | frozenset[str] | None
) -> frozenset[str]:
    """The enabled module set for one run, or a refusal.

    ``allowed`` is the product's own list - the enemy executable allows the two
    enemy modules and not the map-warp one, and the map-warp executable allows
    map-warp and nothing else. A request for a module outside it is refused
    rather than ignored, because a dropped module would produce a ROM under a
    label that promised it.
    """
    permitted = frozenset(allowed) if allowed is not None else frozenset(MODULE_ORDER)
    unknown = permitted - frozenset(MODULE_ORDER)
    if unknown:
        raise ModuleRefusedError(
            f"unknown module(s) allowed: {', '.join(sorted(unknown))}; "
            f"registered: {', '.join(MODULE_ORDER)}"
        )
    if requested is None:
        return frozenset(default_enabled_ids() & permitted)
    wanted = frozenset(requested)
    refused = wanted - permitted
    if refused:
        raise ModuleRefusedError(
            f"this product does not offer {', '.join(sorted(refused))}; "
            f"it offers {', '.join(sorted(permitted)) or 'no module'}"
        )
    unknown = wanted - frozenset(MODULE_ORDER)
    if unknown:
        raise ModuleRefusedError(
            f"unknown module(s): {', '.join(sorted(unknown))}; "
            f"registered: {', '.join(MODULE_ORDER)}"
        )
    return wanted


def derive_module_seeds(master_seed: str) -> dict[str, str]:
    """Every registered module's seed, keyed by module id.

    Every entry is computed independently of the others and of which modules a
    run enables, so a manifest always states what the run *could* have done and
    reordering, adding or disabling a module cannot move an existing one's seed.
    """
    return {cls.id: cls.derive_seed(master_seed) for cls in modules()}


def progress_steps(enabled: Sequence[str] | frozenset[str]) -> tuple[str, ...]:
    """The real phases of one run, in order, for a progress display.

    Built from the modules the run actually enables, so the warp product's phase
    list is the one it always had - verify, randomize warps, write, verify and
    record - and an enemy run names the enemy work instead of inheriting a warp's
    wording. Each entry is reported immediately *before* the work it names begins,
    so a bar fed from these can only ever understate progress, never claim work
    that has not started.
    """
    enabled_set = frozenset(enabled)
    phases = ["Verifying the ROM"]
    for module_id in MODULE_ORDER:
        if module_id in enabled_set:
            phases.append(module_for(module_id).progress_label)
    phases.append("Writing the randomized ROM")
    phases.append("Verifying the source ROM and writing the manifest")
    return tuple(phases)


def plan_modules(
    *,
    enabled: frozenset[str],
    context,
    master_seed: str,
    settings: Mapping[str, Mapping[str, object]] | None = None,
    sdk_commit: str | None = None,
) -> tuple[ModulePlan, ...]:
    """Plan every enabled module, one group at a time, in canonical order.

    Returns the plans sorted into :data:`MODULE_ORDER`, so a caller never sees a
    group's internal order leak into the manifest.
    """
    unknown = frozenset(enabled) - frozenset(MODULE_ORDER)
    if unknown:
        raise ModuleRefusedError(
            f"unknown module(s): {', '.join(sorted(unknown))}"
        )
    seeds = derive_module_seeds(master_seed)
    resolved_settings = {
        module_id: module_for(module_id).resolve_settings(
            (settings or {}).get(module_id)
        )
        for module_id in enabled
    }

    contributions: list[ModulePlan] = []
    for group in MODULE_GROUPS:
        members = enabled & frozenset(group.ids)
        if not members:
            continue
        request = GroupPlanRequest(
            context=context,
            master_seed=master_seed,
            enabled=frozenset(members),
            module_seeds=seeds,
            settings=resolved_settings,
            sdk_commit=sdk_commit,
        )
        produced = tuple(group.planner(request))
        produced_ids = {plan.module_id for plan in produced}
        if produced_ids != set(members):
            raise ModuleContractError(
                f"group {group.ids} was asked for {sorted(members)} but produced "
                f"{sorted(produced_ids)}"
            )
        contributions.extend(produced)

    order = {module_id: index for index, module_id in enumerate(MODULE_ORDER)}
    contributions.sort(key=lambda plan: order[plan.module_id])
    return tuple(contributions)
