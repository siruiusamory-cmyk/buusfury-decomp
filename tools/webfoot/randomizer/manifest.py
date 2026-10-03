"""One manifest format for every randomizer product.

Before this package there were two: the warp product's ``warprand`` document and
the enemy pack's ``RunManifest``, each with its own shape, each the only place its
own facts lived. Once one shell can run several modules in one pass, two formats
stop being a style question - a combined run has ONE output and therefore needs
ONE document describing it, and a reader must not have to know which product
produced a file before they can read it.

The format is versioned twice on purpose:

* ``format_version`` - the shape of this document. It changes only when a reader
  could no longer find a fact where it used to be.
* each module's ``module_version`` - that module's seed-affecting algorithm
  version. A seed is only reproducible alongside the algorithm version that
  consumed it, so a change that alters output for an unchanged seed must bump it.

Every module contributes a *bounded* section under ``modules``. Adding a module
adds a key; it never moves an existing one. Nothing in this document is an
absolute path: the output contributes its basename alone, so two runs of the same
image, seed and output name in two different folders produce identical bytes and a
published manifest can be compared with a locally produced one.
"""

from __future__ import annotations

import hashlib
import json
from typing import Mapping, Sequence

from .module import ModulePlan, RandomizerModule

#: The document shape. See the module docstring.
FORMAT_VERSION = 1

#: How every registered seed is reached. Stated rather than implied, because a
#: reader re-deriving a module seed has to know whether the master seed was hashed
#: or consumed verbatim - and for ``map-warp`` it is consumed verbatim, for the
#: legacy reason its own module docstring gives.
SEED_DERIVATION_NOTE = (
    "each module's seed is a pure function of the master seed and that module's "
    "own id or namespace, so enabling or disabling a module cannot move a sibling's "
    "result. 'master-legacy' means the module consumes the master seed itself, "
    "because its seed semantics predate this framework and are frozen."
)


def canonical_json(document: Mapping) -> str:
    """Deterministic JSON text: sorted keys, fixed indent, LF-terminated.

    One serializer for the manifest and the spoiler, so two runs that agree
    produce byte-identical files and a digest of the text is a digest of the run.
    """
    return json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def document_digest(document: Mapping) -> str:
    """SHA-256 of the canonical text. The manifest's own identity."""
    return hashlib.sha256(canonical_json(document).encode("utf-8")).hexdigest()


def _module_section(
    module: type[RandomizerModule],
    plan: ModulePlan | None,
    derived_seed: str,
) -> dict:
    """One module's bounded block, whether or not it ran.

    A module that did not run still gets a section, carrying ``enabled: false``.
    Recording what a run *could* have done is what makes two manifests
    comparable: a reader can tell "this module was off" from "this module did
    nothing".
    """
    section: dict = {
        "display_name": module.display_name,
        "enabled": plan is not None,
        "module_version": module.algorithm_version,
        "seed_namespace": module.seed_namespace,
        "derived_seed": derived_seed,
    }
    if plan is not None:
        section.update(plan.manifest)
        if plan.summary_lines:
            section["summary_lines"] = list(plan.summary_lines)
    return section


def build_manifest(
    *,
    tool_name: str,
    tool_version: str,
    modules: Sequence[type[RandomizerModule]],
    enabled: frozenset[str],
    plans: Sequence[ModulePlan],
    module_seeds: Mapping[str, str],
    profile_id: str,
    source_sha256: str,
    source_size: int,
    master_seed: str,
    output_filename: str,
    output_size: int,
    output_sha256: str,
    changed_byte_count: int,
    progression: str = "",
    spoiler_filename: str | None = None,
    module_order: Sequence[str] = (),
    tool_commit: str | None = None,
    tool_dirty: bool | None = None,
) -> dict:
    """The shared manifest for one finished run.

    Every number here is either read from the verified profile or reported by the
    writer; none is a constant restated in the application, so a format change
    cannot leave a stale value in a published document.
    """
    plans_by_id = {plan.module_id: plan for plan in plans}
    sections = {
        module.id: _module_section(
            module, plans_by_id.get(module.id), module_seeds[module.id]
        )
        for module in modules
    }

    limitations: list[str] = []
    for module in modules:
        plan = plans_by_id.get(module.id)
        if plan is None:
            continue
        for statement in plan.limitations:
            if statement not in limitations:
                limitations.append(statement)

    document: dict = {
        "format_version": FORMAT_VERSION,
        "tool": {"name": tool_name, "version": tool_version},
        # The commit is stated under its own key rather than inside ``tool``, so
        # adding provenance never changes the shape of the two facts every reader
        # already looks for. A packaged build has no repository to ask, so this is
        # legitimately null there - a provenance gap, recorded rather than hidden -
        # and ``dirty`` says whether the recorded commit is the bytes that produced
        # the build or only the tree they were based on.
        "build": {"commit": tool_commit, "dirty": tool_dirty},
        "source": {
            "profile": profile_id,
            "size": source_size,
            "sha256": source_sha256,
        },
        "master_seed": master_seed,
        "seed_derivation": {
            "note": SEED_DERIVATION_NOTE,
            "module_seeds": dict(sorted(module_seeds.items())),
        },
        "module_order": list(module_order),
        "modules": sections,
        "output": {
            "filename": output_filename,
            "size": output_size,
            "sha256": output_sha256,
            "changed_byte_count": changed_byte_count,
        },
    }
    if progression:
        document["progression"] = progression
    if limitations:
        document["limitations"] = limitations
    document["spoiler"] = (
        {"filename": spoiler_filename} if spoiler_filename else None
    )
    return document
