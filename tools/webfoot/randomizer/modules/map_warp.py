"""``map-warp`` - the warp randomizer as a module of the shared foundation.

This module is an *adapter*, not an implementation. Every destination, arrival,
facing, permutation and refusal is decided by
:mod:`tools.webfoot.warp_randomizer`, which is unmodified and still the only
place that policy exists. What is added here is exactly the three things the
module contract asks for and nothing else:

* the stable id, display name and progress caption a product needs;
* the seed answer (see below - it is the one interesting decision in this file);
* the translation of a :class:`~tools.webfoot.warp_randomizer.WarpRandomization`
  into a :class:`~tools.webfoot.randomizer.module.ModulePlan`.

The seed namespace is a legacy passthrough, and it is load-bearing
=================================================================

Every other module derives its own seed as ``sha256(domain | master | module_id)``.
This one **must not**. The warp core draws from
``sha256(SEED_DOMAIN | seed | group | step)`` where ``seed`` is the string the
user typed, and ``SEED_DOMAIN`` is frozen in
:mod:`tools.webfoot.warp_randomizer` precisely because changing it changes every
warp mapping ever produced. Feeding the core a *derived* seed instead of the
master seed would silently break every warp seed that already exists - a user's
saved seed would no longer reproduce their run.

So ``map-warp`` consumes the master seed itself, and says so: its
:attr:`~tools.webfoot.randomizer.module.RandomizerModule.seed_namespace` is
``master-legacy`` and its algorithm version is 1. This is still a stable
namespace in the sense the architecture requires - the module's result is a
function of the master seed and this module's algorithm version alone, and adding
or disabling any other module cannot move it - and it is the *only* namespace
that may be spelled this way, because it is the only one with history behind it.
The architecture test pins both halves of that: ``map-warp``'s derived seed
equals the master seed, and every other registered module's seed differs from it
and from its siblings'.
"""

from __future__ import annotations

import json
from typing import Mapping

from ...warp_randomizer import POLICY_ID, plan_warp_randomization
from ..module import ModulePlan, RandomizerModule

#: The namespace label recorded in the manifest. See the module docstring: this
#: is the frozen legacy contract, not an oversight.
SEED_NAMESPACE = "master-legacy"


class MapWarpModule(RandomizerModule):
    """The proven ``reciprocal-door-pairs/3`` warp randomizer."""

    id = "map-warp"
    display_name = "Map warps"
    description = (
        "Shuffles where the doors of Buu's Fury lead. Doors move in reciprocal "
        "pairs, so the door you arrive on is the one that takes you back."
    )
    default_enabled = True
    algorithm_version = 1
    seed_namespace = SEED_NAMESPACE
    progress_label = "Randomizing warp destinations"

    @classmethod
    def derive_seed(cls, master_seed: str) -> str:
        """The master seed, verbatim. See the module docstring for why."""
        return master_seed

    @classmethod
    def plan(
        cls,
        context,
        settings: Mapping[str, object],
        *,
        seed: str,
    ) -> ModulePlan:
        randomization = plan_warp_randomization(context.image(), context.profile, seed)
        summary = randomization.manifest.summary()
        # The core renders its record as deterministic JSON text (it is written to
        # disk verbatim by `webfoot warp-randomizer`); the shared manifest is a
        # document, so the text is parsed back into a mapping rather than embedded
        # as a quoted string. Same bytes, same information, one JSON document.
        core = json.loads(
            randomization.manifest.to_json(
                output_sha256="", output_size=len(context.image())
            )
        )
        return ModulePlan(
            module_id=cls.id,
            changes=tuple(randomization.write_plan.changes),
            manifest={
                # The policy stays on the module that owns it, so a combined
                # manifest says which warp algorithm produced its map-warps half
                # rather than implying there is one global policy.
                "algorithm": POLICY_ID,
                "counts": {
                    "supported": summary["supported_transitions"],
                    "randomized": summary["randomized"],
                    "destinations_moved": summary["destinations_changed"],
                    "destinations_unchanged": summary["destinations_unchanged"],
                    "skipped": summary["skipped"],
                },
                "skipped_reasons": summary["skipped_by_reason"],
                "class_counts": summary["class_counts"],
                "forced_dead_end_links": summary["forced_dead_end_links"],
                # The randomizer's own full record, verbatim: every transition
                # row, its retail and randomized bundle, its pair and its skip
                # reason. Carried whole so the product manifest stays a superset
                # of the core's rather than a second, thinner document. The
                # output digest is deliberately absent here - it is stated once,
                # by the application, at the top level of the manifest, because a
                # plan has not produced an image yet.
                "randomizer": core,
            },
            spoiler=None,
            summary_lines=(
                f"Supported: {summary['supported_transitions']}",
                f"Randomized: {summary['randomized']}",
                f"Destinations moved: {summary['destinations_changed']}",
                f"Skipped: {summary['skipped']}",
            ),
        )
