"""One spoiler architecture for every randomizer product.

A spoiler is the *readable* half of a run: which enemy now stands where and what
its stats became. It is optional by design - a blind stream needs the manifest
(provenance) without the answers - so the architecture has to make "no spoiler
file" a first-class outcome rather than an empty file.

Two rules, and both exist because a module that broke them would be a second
application:

* **modules never open a spoiler file.** A module returns a bounded mapping for
  its own section; the application decides whether any of it is written, what the
  file is called, and where it goes.
* **one document, one section per module.** The standalone Enemy Randomizer's
  spoiler contains the sections of the modules it enabled and nothing else, and a
  future combined tool's spoiler contains all of them - without either module
  knowing which product it is running inside.

What a spoiler is not
=====================

Turning the spoiler off is **not** a general promise that nothing revealing is
written. The manifest is always written, and some of its content is a mapping
rather than a provenance line: ``map-warp`` has carried its full per-transition
record - every retail destination and every randomized one - in its manifest since
v0.1.0, because that record is what lets a third party audit a warp seed without
the tool. It stays there.

So the precise contract is: the spoiler holds the answers a module chooses to keep
*out of* the manifest, and the manifest remains provenance. An independent review
raised this as a product-promise question, and it is answered by stating the
contract rather than by moving the warp record, which would delete audit evidence
that a published manifest has always contained.

The document deliberately does not carry an absolute path, for the same reason the
manifest does not: a spoiler should be comparable between two machines.
"""

from __future__ import annotations

from typing import Mapping, Sequence

from .manifest import FORMAT_VERSION, canonical_json, document_digest
from .module import ModulePlan, RandomizerModule

__all__ = [
    "FORMAT_VERSION",
    "build_spoiler",
    "canonical_json",
    "document_digest",
]


def build_spoiler(
    *,
    tool_name: str,
    tool_version: str,
    modules: Sequence[type[RandomizerModule]],
    plans: Sequence[ModulePlan],
    master_seed: str,
    profile_id: str,
    output_filename: str,
    output_sha256: str,
) -> dict | None:
    """The combined spoiler for a run, or ``None`` when nothing has to be hidden.

    ``None`` rather than an empty document, so the application can refuse to
    create a file at all. A module with nothing secret contributes no section; a
    run in which no module has anything secret produces no spoiler, and the
    manifest's ``spoiler`` key stays null.
    """
    sections: dict[str, Mapping[str, object]] = {}
    for plan in plans:
        if plan.spoiler is None:
            continue
        if not any(plan.spoiler.values()):
            continue
        sections[plan.module_id] = plan.spoiler
    if not sections:
        return None

    return {
        "format_version": FORMAT_VERSION,
        "tool": {"name": tool_name, "version": tool_version},
        "profile": profile_id,
        "master_seed": master_seed,
        "output": {"filename": output_filename, "sha256": output_sha256},
        "modules": dict(sections),
        "module_order": [
            module.id for module in modules if module.id in sections
        ],
    }
