"""The enemy modules: ``enemy-placement`` and ``enemy-stat``.

Two modules, one plan pass
==========================

The addendum requires Enemy Placement and Enemy Stats to be independently
toggleable, and they are: each can be enabled alone and each produces a different
ROM. What they are *not* is independently plannable, and that is a measured
property of the pack rather than a preference.

The pack loads an 8 MiB image once and builds one slot model from it, and both
enemy modules read that model; planning them in two passes would build the model
twice and, worse, would plan two :class:`~tools.webfoot.write.WritePlan` objects
over one image, which is exactly the shape that hides a collision (the writer's
overlap check is per plan). So the registry declares them a *group*: the
foundation calls the group once, and the group returns one
:class:`~tools.webfoot.randomizer.module.ModulePlan` per enabled member. Where
the two modules meet is the group's business; what each one does is still
entirely the pack's, called through its own
:class:`~tools.webfoot.enemy_randomizer.planner.EnemyRandomizerContext`.

Byte attribution
================

The pack returns one merged change set. Each byte is attributed to the module
that caused it by looking the change's ``owner`` up in that module's own recorded
decisions - the placement module's :class:`~tools.webfoot.enemy_randomizer.placement.PlacementDecision`
carries the placement identity, and the stat module's
:class:`~tools.webfoot.enemy_randomizer.stats.StatDecision` carries the enemy
identity, and those identity strings are exactly what
:class:`~tools.webfoot.write.ByteChange` records as its owner. A change nobody
claims is a defect in the attribution, so it fails closed rather than being
silently dropped or double-counted.

Module C is absent by construction
==================================

``enemy-type`` is deliberately **not registered**. The pack ships the module and
the CLI can still reach it explicitly, but this foundation - and therefore every
product built on it - does not offer it, so there is no toggle to disable, no
half-implemented feature to explain, and no wording anywhere in the shell that
could imply an enemy's species is changed. Every enemy section of every manifest
still records ``delivers_ticket_module_c: false`` and carries the pack's own
statement of what the two shipping modules do and do not do.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Mapping

from ...enemy_randomizer.config import (
    PRESETS,
    ConfigError,
    EnemyRandomizerConfig,
    preset as lookup_preset,
)
from ...enemy_randomizer.planner import EnemyRandomizerError, EnemyRandomization
from ...enemy_randomizer.seeds import (
    MODULE_ENEMY_PLACEMENT,
    MODULE_ENEMY_STAT,
    derive_module_seed,
)
from ...write import ByteChange
from ..errors import ModuleRefusedError
from ..module import (
    SETTING_CHOICE,
    GroupPlanRequest,
    ModulePlan,
    RandomizerModule,
    SettingDescriptor,
)

#: The enemy module ids this foundation registers, in canonical order.
ENEMY_MODULE_IDS: tuple[str, ...] = (MODULE_ENEMY_PLACEMENT, MODULE_ENEMY_STAT)

#: The default band. Named rather than repeated: the conservative stream preset
#: is the product's default and the ticket's STREAM SAFE requirement.
DEFAULT_BAND = "stream-safe"

#: The setting that selects a band, shared by both modules.
BAND_SETTING = SettingDescriptor(
    key="stat_band",
    kind=SETTING_CHOICE,
    label="Enemy stat range",
    help=(
        "How far an enemy's stats may move from their own original values. "
        "Stream safe is the conservative choice; chaos is wider, and an enemy's "
        "stats are still scaled from its own values rather than drawn from one "
        "big shared range."
    ),
    default=DEFAULT_BAND,
    choices=tuple(sorted(PRESETS)),
)

#: The standing disclosure every enemy manifest section carries. The pack defines
#: the same fact inside its own configuration block, and this module repeats it at
#: the section's top level so a reader scanning a combined manifest sees it without
#: knowing the pack's schema. A test pins the two to agree, because two statements
#: of one fact are two things that can drift.
MODULE_C_DELIVERED = False


def _band(config_settings: Mapping[str, object]) -> str:
    band = str(config_settings.get("stat_band", DEFAULT_BAND))
    if band not in PRESETS:
        raise ModuleRefusedError(
            f"unknown enemy stat band {band!r}; available: {', '.join(sorted(PRESETS))}"
        )
    return band


class _EnemyModule(RandomizerModule):
    """Shared behaviour for the two enemy modules."""

    settings: tuple[SettingDescriptor, ...] = ()

    @classmethod
    def derive_seed(cls, master_seed: str) -> str:
        """The pack's own domain-separated derivation, unchanged.

        Reused rather than reimplemented so a seed derived here is the same seed
        ``webfoot randomize`` derives for the same module - which is what makes
        the application route and the CLI route produce the same ROM.
        """
        return derive_module_seed(master_seed, cls.id)


class EnemyPlacementModule(_EnemyModule):
    """``enemy-placement``: a same-map shuffle over proven slots."""

    id = MODULE_ENEMY_PLACEMENT
    display_name = "Shuffle enemy placements"
    description = (
        "Shuffles enemy placements within each map, using only positions the map "
        "already had. No new spawn is created and no coordinate is invented."
    )
    default_enabled = True
    algorithm_version = 1
    seed_namespace = MODULE_ENEMY_PLACEMENT
    progress_label = "Shuffling enemy placements"


class EnemyStatModule(_EnemyModule):
    """``enemy-stat``: bounded, multiplicative, per-record stat randomization."""

    id = MODULE_ENEMY_STAT
    display_name = "Randomize enemy stats"
    description = (
        "Randomizes enemy stats within safe bounds, scaling each enemy from its "
        "own original values so the game's general progression is preserved."
    )
    default_enabled = True
    algorithm_version = 1
    seed_namespace = MODULE_ENEMY_STAT
    progress_label = "Randomizing enemy stats"
    #: The band belongs to the stat module, which is the module it configures.
    #: Declaring it on both would draw the same control twice and imply the two
    #: modules could disagree - which the group refuses.
    settings = (BAND_SETTING,)


def _config_for(request: GroupPlanRequest, band: str) -> EnemyRandomizerConfig:
    """The pack configuration this group's enabled set and settings describe.

    The band's own preset supplies everything except the enabled set, so the
    presets stay the single definition of STREAM SAFE - the frontend composes a
    preset, it never restates one. The enabled set is narrowed to the modules the
    request actually asked for, which is what makes stats-only and
    placement-only runs real rather than a manifest claim.
    """
    base = lookup_preset(band).config
    enabled = frozenset(request.enabled) & frozenset(ENEMY_MODULE_IDS)
    if not enabled:
        raise ModuleRefusedError("no enemy module was enabled")
    return replace(base, enabled=enabled)


def _partition_changes(
    changes: tuple[ByteChange, ...], result: EnemyRandomization
) -> dict[str, tuple[ByteChange, ...]]:
    """Attribute every change to the module whose decisions name it.

    Only *effective* changes are attributed. The pack encodes every stat record -
    including the base-stat records of playable characters it never scales - so
    that a record which re-encodes to different bytes cannot pass unnoticed; a
    record that re-encodes identically is a round-trip proof, not an edit, and
    carrying it into the plan would add a validated row that changes nothing.
    """
    placement_owners = (
        {decision.placement for decision in result.placements.decisions}
        if result.placements is not None
        else set()
    )
    stat_owners = (
        {decision.enemy_identity for decision in result.stats.decisions}
        if result.stats is not None
        else set()
    )
    buckets: dict[str, list[ByteChange]] = {module_id: [] for module_id in ENEMY_MODULE_IDS}
    unclaimed: list[ByteChange] = []
    for change in changes:
        if change.owner in placement_owners:
            buckets[MODULE_ENEMY_PLACEMENT].append(change)
        elif change.owner in stat_owners:
            buckets[MODULE_ENEMY_STAT].append(change)
        else:
            unclaimed.append(change)
    if unclaimed:
        # Fail closed. An unattributed change would either vanish from the record
        # or be counted twice, and both of those make the manifest describe an
        # image no module planned.
        raise ModuleRefusedError(
            "the enemy pack produced "
            f"{len(unclaimed)} change(s) that no module's decisions account for "
            f"(first: {unclaimed[0].owner!r}); refusing to attribute them"
        )
    return {module_id: tuple(items) for module_id, items in buckets.items()}


def plan_enemy_group(request: GroupPlanRequest) -> tuple[ModulePlan, ...]:
    """One plan pass for every enabled enemy module.

    Registered as the enemy group's planner. Called once per run regardless of how
    many enemy modules are enabled, which is what keeps a two-module run at one
    image load and one slot model.
    """
    # The shell calls `validate` for a single-module group; a group planner has to
    # do it for its own members, so the contract holds for both shapes. Imported
    # here rather than at module scope because the registry imports this module.
    from ..registry import module_for

    for module_id in sorted(request.enabled):
        module_for(module_id).validate(
            request.context, request.settings.get(module_id, {})
        )

    settings_by_module = {
        module_id: request.settings.get(module_id, {}) for module_id in request.enabled
    }
    # Only the modules that declare a band contribute one; a placement-only run
    # has no stat configuration to disagree about.
    bands = {
        _band(settings)
        for settings in settings_by_module.values()
        if "stat_band" in settings
    }
    if len(bands) > 1:
        # One pack configuration plans the enabled set, so two different bands in
        # one run has no meaning. Refused rather than silently picking one.
        raise ModuleRefusedError(
            "the enemy modules must agree on a stat band; got "
            f"{', '.join(sorted(bands))}"
        )
    band = bands.pop() if bands else DEFAULT_BAND

    config = _config_for(request, band)
    enemy_context = request.context.enemy_context()
    try:
        result = enemy_context.plan(
            request.master_seed,
            config,
            preset_name=band,
            sdk_commit=request.sdk_commit,
        )
    except (EnemyRandomizerError, ConfigError) as exc:
        raise ModuleRefusedError(f"The enemy randomizer refused this run: {exc}") from exc

    # The registry's derived seed and the seed the pack actually consumed are two
    # independently computed values, and the manifest publishes the first while the
    # bytes come from the second. They agree today because both call the pack's own
    # `derive_module_seed`; this refuses a run where an override ever makes them
    # disagree, rather than letting a manifest state a seed that was not used.
    for module_id, recorded in result.module_seeds.items():
        if module_id not in request.enabled:
            continue
        expected = request.module_seeds.get(module_id)
        if expected is not None and expected != recorded:
            raise ModuleRefusedError(
                f"{module_id}: the seed this run derived ({expected}) is not the "
                f"seed the core consumed ({recorded}); refusing to record a run "
                "whose manifest would misstate its own seed"
            )

    changes = _partition_changes(tuple(result.plan.effective_changes), result)

    summaries = result.manifest.module_summaries
    spoiler = result.spoiler
    limitations = tuple(
        value
        for key, value in (
            ("scope_note", result.manifest.exclusions.get("scope_note")),
            ("enemy_type_module", result.manifest.exclusions.get("enemy_type_module")),
        )
        if value
    )

    plans: list[ModulePlan] = []
    for module_id in ENEMY_MODULE_IDS:
        if module_id not in request.enabled:
            continue
        spoiler_section: Mapping[str, object] | None = None
        if module_id == MODULE_ENEMY_PLACEMENT:
            section: dict[str, object] = {
                "algorithm": "same-map-placement-shuffle/1",
                "scope": config.placement_scope,
                "summary": summaries.get(module_id, {}),
                # Placement classification is what eligibility IS, so the model's
                # summary and its exclusions belong to this module rather than
                # being restated at the top of a shared document as if every
                # module had an eligibility question.
                "eligibility": result.manifest.slot_summary,
                "exclusions": result.manifest.exclusions,
            }
            spoiler_section = {"slots": list(spoiler.slots)} if spoiler.slots else None
        else:
            section = {
                "algorithm": "bounded-multiplicative-stats/1",
                "summary": summaries.get(module_id, {}),
                # The pack's own configuration block travels whole: it is what
                # carries the band, the field list and the Module C disclosure.
                "configuration": result.manifest.configuration,
            }
            spoiler_section = {"stats": list(spoiler.stats)} if spoiler.stats else None
        section["delivers_ticket_module_c"] = MODULE_C_DELIVERED
        section["change_count"] = len(changes.get(module_id, ()))
        plans.append(
            ModulePlan(
                module_id=module_id,
                changes=changes.get(module_id, ()),
                manifest=section,
                spoiler=spoiler_section,
                summary_lines=_summary_lines(module_id, result),
                limitations=limitations,
            )
        )
    return tuple(plans)


def _summary_lines(module_id: str, result: EnemyRandomization) -> tuple[str, ...]:
    """What this module did, in the pack's own numbers."""
    if module_id == MODULE_ENEMY_PLACEMENT and result.placements is not None:
        return (
            f"Placements moved: {result.placements.moved_count}",
            f"Maps shuffled: {result.placements.groups_shuffled}",
        )
    if module_id == MODULE_ENEMY_STAT and result.stats is not None:
        return (f"Enemy records changed: {result.stats.randomized_records}",)
    return ()
